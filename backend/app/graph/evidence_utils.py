from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class EvidenceCollectionResult(BaseModel):
    status: str  # SUCCESS_USABLE | SUCCESS_EMPTY | FAILED_CONFIG | FAILED_RUNTIME
    tool_name: str
    category: str
    summary: str = ""
    error_summary: str = ""
    latency_ms: int = 0
    collected_at: str = ""


def classify_result(
    tool_name: str,
    category: str,
    success: bool,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    latency_ms: int = 0,
    collected_at: str = "",
) -> EvidenceCollectionResult:
    if not success:
        if error and any(
            kw in error.lower()
            for kw in (
                "not configured",
                "no real adapter",
                "not implemented",
                "adapter not",
                "real adapter",
                "not found",
            )
        ):
            status = "FAILED_CONFIG"
        else:
            status = "FAILED_RUNTIME"
        return EvidenceCollectionResult(
            status=status,
            tool_name=tool_name,
            category=category,
            error_summary=error or "unknown error",
            latency_ms=latency_ms,
            collected_at=collected_at,
        )

    if not is_payload_usable(tool_name, result):
        return EvidenceCollectionResult(
            status="SUCCESS_EMPTY",
            tool_name=tool_name,
            category=category,
            summary=_summarize_result(tool_name, result),
            latency_ms=latency_ms,
            collected_at=collected_at,
        )

    return EvidenceCollectionResult(
        status="SUCCESS_USABLE",
        tool_name=tool_name,
        category=category,
        summary=_summarize_result(tool_name, result),
        latency_ms=latency_ms,
        collected_at=collected_at,
    )


def is_payload_usable(tool_name: str, payload: Optional[Dict[str, Any]]) -> bool:
    if not payload or not isinstance(payload, dict):
        return False

    if tool_name == "query_logs":
        logs = payload.get("logs")
        count = payload.get("count", 0)
        if isinstance(logs, list) and len(logs) > 0:
            return True
        return isinstance(count, (int, float)) and count > 0

    if tool_name == "query_metrics":
        metrics = payload.get("metrics", {})
        if isinstance(metrics, dict):
            for name, metric in metrics.items():
                if isinstance(metric, dict) and metric.get("values"):
                    vals = metric["values"]
                    if isinstance(vals, list) and len(vals) > 0:
                        return True
        return False

    if tool_name in ("query_deployments",):
        deployments = payload.get("deployments")
        count = payload.get("count", 0)
        if isinstance(deployments, list) and len(deployments) > 0:
            return True
        return isinstance(count, (int, float)) and count > 0

    if tool_name == "query_runbook":
        runbooks = payload.get("runbooks")
        count = payload.get("count", 0)
        if isinstance(runbooks, list) and len(runbooks) > 0:
            return True
        return isinstance(count, (int, float)) and count > 0

    if tool_name.startswith("query_k8s_"):
        if any(payload.get(k) for k in ("status", "pods", "events", "logs")):
            return True
        return False

    if tool_name.startswith("query_db_"):
        if any(payload.get(k) is not None for k in ("rows", "processes", "queries", "variables")):
            return True
        return bool(payload)

    if tool_name.startswith("query_lb_"):
        if payload.get("status") or payload.get("error_rate") is not None:
            return True
        return False

    return bool(payload)


def _summarize_result(tool_name: str, payload: Optional[Dict[str, Any]]) -> str:
    if not payload or not isinstance(payload, dict):
        return "empty result"

    if tool_name == "query_logs":
        return f"{payload.get('count', 0)} log entries"
    if tool_name == "query_metrics":
        metrics = payload.get("metrics", {})
        names = list(metrics.keys()) if isinstance(metrics, dict) else []
        return f"metrics: {', '.join(names) if names else 'none'}"
    if tool_name in ("query_deployments",):
        return f"{payload.get('count', 0)} deployments"
    if tool_name == "query_runbook":
        return f"{payload.get('count', 0)} runbooks"
    if tool_name.startswith("query_k8s_"):
        return payload.get("summary", "k8s data retrieved")
    if tool_name.startswith("query_db_"):
        return payload.get("summary", "db data retrieved")
    if tool_name.startswith("query_lb_"):
        return payload.get("summary", "lb data retrieved")
    return "data retrieved"


def compute_quality_from_results(
    collection_results: List[EvidenceCollectionResult],
) -> tuple[float, List[str], List[str]]:
    usable_by_category: Dict[str, int] = {}
    failed_tools: List[str] = []

    for r in collection_results:
        if r.status == "SUCCESS_USABLE":
            usable_by_category[r.category] = usable_by_category.get(r.category, 0) + 1
        elif r.status in ("FAILED_CONFIG", "FAILED_RUNTIME"):
            if r.tool_name not in failed_tools:
                failed_tools.append(r.tool_name)

    expected_categories = {"logs", "metrics", "deployments", "runbook", "k8s", "db", "lb"}
    present = set(usable_by_category.keys())
    coverage = len(present & expected_categories) / len(expected_categories) if expected_categories else 0

    quality_score = round(coverage, 2)
    missing = sorted(expected_categories - present)

    return quality_score, missing, failed_tools
