"""Cross-agent evidence aggregator: correlation graph, causal chains,
contradiction detection, and weighted quality scoring.

All functions are pure — they consume SpecialistAnalysis objects and produce
deterministic outputs. No external I/O.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import logging

from app.models.planning import SpecialistAnalysis, CorrelationHint, AnomalySignal

logger = logging.getLogger(__name__)

CONTRADICTION_RULES = [
    ("k8s", "metrics", "可能非资源级故障"),
    ("k8s", "deployments", "故障可能非发布导致"),
    ("db", "k8s", "DB 自身问题，非容器层"),
    ("db", "metrics", "可能是慢查询/锁争用等非资源瓶颈"),
    ("logs", "k8s", "应用层故障，非基础设施"),
    ("metrics", "k8s", "资源压力未导致 Pod 级故障"),
]


def _get_category(analysis: SpecialistAnalysis) -> str:
    return analysis.agent_category


def _has_anomalies(analysis: SpecialistAnalysis) -> bool:
    for ev in analysis.evidence_items:
        if ev.anomalies:
            return True
    return False


def _get_anomaly_types(analysis: SpecialistAnalysis) -> List[str]:
    types: List[str] = []
    for ev in analysis.evidence_items:
        for a in ev.anomalies:
            if a.signal_type:
                types.append(a.signal_type)
    return list(set(types))


def _build_correlation_graph(
    analyses: List[SpecialistAnalysis],
) -> Dict[str, List[str]]:
    graph: Dict[str, List[str]] = {}
    categories = {_get_category(a) for a in analyses}

    for src_cat in categories:
        graph[src_cat] = []

    for a in analyses:
        src_cat = _get_category(a)
        for ev in a.evidence_items:
            for hint in ev.correlation_hints:
                if hint.confidence >= 0.6 and hint.target_category in categories:
                    if hint.target_category not in graph[src_cat]:
                        graph[src_cat].append(hint.target_category)

    return graph


def _infer_causal_chains(
    graph: Dict[str, List[str]],
    analyses: List[SpecialistAnalysis],
) -> List[Dict[str, Any]]:
    cat_to_anomalies: Dict[str, bool] = {}
    for a in analyses:
        cat_to_anomalies[_get_category(a)] = _has_anomalies(a)

    in_degree: Dict[str, int] = {cat: 0 for cat in graph}
    for src, targets in graph.items():
        for tgt in targets:
            in_degree[tgt] = in_degree.get(tgt, 0) + 1

    roots = [cat for cat, deg in in_degree.items() if deg == 0]
    chains: List[List[str]] = []

    def dfs(current: str, path: List[str], visited: set):
        if current in visited:
            return
        visited.add(current)
        if not cat_to_anomalies.get(current, False):
            visited.discard(current)
            return
        if not graph.get(current):
            if len(path) >= 2:
                chains.append(list(path))
            visited.discard(current)
            return
        has_anomaly_child = False
        for neighbor in graph[current]:
            if neighbor not in visited and cat_to_anomalies.get(neighbor, False):
                has_anomaly_child = True
                dfs(neighbor, path + [neighbor], visited)
        if not has_anomaly_child and len(path) >= 2:
            chains.append(list(path))
        visited.discard(current)

    for root in roots:
        dfs(root, [root], set())

    chains.sort(key=lambda c: len(c), reverse=True)
    formatted: List[Dict[str, Any]] = []
    for chain in chains[:5]:
        anomalies = []
        for cat in chain:
            anomalies.extend(
                _get_anomaly_types(
                    next((a for a in analyses if _get_category(a) == cat), None)
                    or SpecialistAnalysis(agent_id="", agent_category=cat)
                )
            )
        formatted.append({
            "chain": chain,
            "anomalies_along_path": list(set(anomalies)),
            "length": len(chain),
        })

    return formatted


def _get_conclusion_prefix(analysis: SpecialistAnalysis) -> str:
    for ev in analysis.evidence_items:
        conclusion = ev.conclusion or ""
        for prefix in ["正常:", "异常:", "部分:", "失败:"]:
            if conclusion.startswith(prefix):
                return prefix.rstrip(":")
    if analysis.run_status and analysis.run_status.value in ("LLM_FAILED", "TIMEOUT"):
        return "失败"
    if analysis.partial:
        return "部分"
    return "正常"


def _detect_cross_agent_contradictions(
    analyses: List[SpecialistAnalysis],
) -> List[Dict[str, str]]:
    cat_prefix: Dict[str, str] = {}
    for a in analyses:
        cat_prefix[_get_category(a)] = _get_conclusion_prefix(a)

    contradictions: List[Dict[str, str]] = []
    for cat_a, cat_b, reason in CONTRADICTION_RULES:
        pa = cat_prefix.get(cat_a)
        pb = cat_prefix.get(cat_b)
        if pa in ("异常", "部分") and pb == "正常":
            contradictions.append({
                "anomaly_category": cat_a,
                "normal_category": cat_b,
                "reason": reason,
            })

    return contradictions


def _compute_weighted_quality(analyses: List[SpecialistAnalysis]) -> float:
    if not analyses:
        return 0.0

    total = 0.0
    truncated_count = 0
    active_count = 0

    for a in analyses:
        if a.run_status and a.run_status.value == "LLM_FAILED":
            continue
        active_count += 1
        conf = a.confidence or 0.0
        if a.partial:
            conf *= 0.5
        total += conf
        if a.truncated:
            truncated_count += 1

    if active_count == 0:
        return 0.0

    avg = total / active_count
    penalty = max(1.0 - 0.1 * truncated_count, 0.5)
    coverage = min(active_count / 5.0, 1.0)

    return max(avg * penalty * coverage, 0.0)


def _format_global_summary(
    analyses: List[SpecialistAnalysis],
    quality_score: float,
    contradictions: List[Dict[str, str]],
    causal_chains: List[Dict[str, Any]],
) -> str:
    parts: List[str] = []

    completed = sum(1 for a in analyses if a.run_status and a.run_status.value == "COMPLETED")
    total = len(analyses)
    parts.append(f"Agent 完成: {completed}/{total}")

    degraded = [a for a in analyses if a.partial]
    if degraded:
        names = ", ".join(f"[降级] {a.agent_category}" for a in degraded)
        parts.append(names)

    parts.append(f"质量评分: {quality_score:.2f}")

    if contradictions:
        parts.append(f"矛盾信号: {len(contradictions)} 条")
        for c in contradictions:
            parts.append(
                f"  {c['anomaly_category']}异常 + {c['normal_category']}正常 → {c['reason']}"
            )

    if causal_chains:
        parts.append(f"因果链: {len(causal_chains)} 条")
        for chain in causal_chains:
            parts.append(f"  {' → '.join(chain['chain'])}")

    return "\n".join(parts)
