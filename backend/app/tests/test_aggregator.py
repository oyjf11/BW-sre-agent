"""Unit tests for aggregator pure functions — cross-agent correlation graph,
causal chains, contradiction detection, and weighted quality scoring.
"""

import pytest
from app.models.planning import (
    AgentRunStatus,
    SpecialistAnalysis,
    SpecialistEvidence,
    AnomalySignal,
    CorrelationHint,
)
from app.graph.nodes.aggregator import (
    _build_correlation_graph,
    _infer_causal_chains,
    _detect_cross_agent_contradictions,
    _compute_weighted_quality,
    _format_global_summary,
    _get_conclusion_prefix,
)


def _make_analysis(
    agent_id: str = "k8s_specialist",
    category: str = "k8s",
    conclusion: str = "正常: all healthy",
    anomalies: list = None,
    hints: list = None,
    confidence: float = 0.8,
    run_status: AgentRunStatus = AgentRunStatus.COMPLETED,
    partial: bool = False,
    truncated: bool = False,
) -> SpecialistAnalysis:
    evidence = SpecialistEvidence(
        evidence_id=f"ev_{agent_id}",
        category=category,
        conclusion=conclusion,
        severity="info",
        anomalies=anomalies or [],
        correlation_hints=hints or [],
    )
    return SpecialistAnalysis(
        agent_id=agent_id,
        agent_category=category,
        evidence_items=[evidence],
        collected_tool_names=[],
        raw_tool_results={},
        execution_summary="test",
        confidence=confidence,
        run_status=run_status,
        partial=partial,
        truncated=truncated,
    )


class TestBuildCorrelationGraph:
    def test_empty_analyses(self):
        graph = _build_correlation_graph([])
        assert graph == {}

    def test_no_hints(self):
        a1 = _make_analysis(category="k8s")
        a2 = _make_analysis(category="db")
        graph = _build_correlation_graph([a1, a2])
        assert graph["k8s"] == []
        assert graph["db"] == []

    def test_concrete_hints(self):
        a1 = _make_analysis(category="k8s", hints=[
            CorrelationHint(source_category="k8s", target_category="db", reason="link", confidence=0.8, source="llm"),
        ])
        a2 = _make_analysis(category="db")
        graph = _build_correlation_graph([a1, a2])
        assert "db" in graph["k8s"]

    def test_low_confidence_hints_ignored(self):
        a1 = _make_analysis(category="k8s", hints=[
            CorrelationHint(source_category="k8s", target_category="db", reason="link", confidence=0.3, source="llm"),
        ])
        a2 = _make_analysis(category="db")
        graph = _build_correlation_graph([a1, a2])
        assert graph["k8s"] == []

    def test_three_concrete_hints_correct_adjacency(self):
        a1 = _make_analysis(category="k8s", hints=[
            CorrelationHint(source_category="k8s", target_category="db", reason="", confidence=0.9, source="llm"),
            CorrelationHint(source_category="k8s", target_category="logs", reason="", confidence=0.7, source="llm"),
        ])
        a2 = _make_analysis(category="db", hints=[
            CorrelationHint(source_category="db", target_category="metrics", reason="", confidence=0.8, source="llm"),
        ])
        a3 = _make_analysis(category="logs")
        a4 = _make_analysis(category="metrics")
        a5 = _make_analysis(category="deployments")
        graph = _build_correlation_graph([a1, a2, a3, a4, a5])
        assert set(graph["k8s"]) == {"db", "logs"}
        assert graph["db"] == ["metrics"]
        assert graph["logs"] == []
        assert graph["metrics"] == []
        assert graph["deployments"] == []


class TestInferCausalChains:
    def test_two_node_chain_with_anomalies(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: pods failing", anomalies=[
            AnomalySignal(signal_type="CrashLoopBackOff", description="crash"),
        ])
        a2 = _make_analysis(category="db", conclusion="异常: slow queries", anomalies=[
            AnomalySignal(signal_type="slow_queries", description="slow"),
        ])
        graph = {"k8s": ["db"], "db": []}
        chains = _infer_causal_chains(graph, [a1, a2])
        assert len(chains) >= 1
        assert chains[0]["chain"] == ["k8s", "db"]

    def test_no_anomalies_no_chains(self):
        a1 = _make_analysis(category="k8s", conclusion="正常: ok")
        a2 = _make_analysis(category="db", conclusion="正常: ok")
        graph = {"k8s": ["db"], "db": []}
        chains = _infer_causal_chains(graph, [a1, a2])
        assert len(chains) == 0

    def test_empty_graph_empty_chains(self):
        chains = _infer_causal_chains({}, [])
        assert chains == []

    def test_max_5_chains(self):
        analyses = []
        for cat in ["k8s", "db", "logs", "metrics", "deployments"]:
            analyses.append(_make_analysis(
                category=cat,
                conclusion="异常: broken",
                anomalies=[AnomalySignal(signal_type="x", description="x")],
                hints=[
                    CorrelationHint(
                        source_category=cat,
                        target_category="k8s" if cat != "k8s" else "db",
                        confidence=0.9,
                        source="llm",
                    ),
                ],
            ))
        graph = _build_correlation_graph(analyses)
        chains = _infer_causal_chains(graph, analyses)
        assert len(chains) <= 5

    def test_k8s_to_db_chain_types(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: CrashLoopBackOff", anomalies=[
            AnomalySignal(signal_type="CrashLoopBackOff", description=""),
        ])
        a2 = _make_analysis(category="db", conclusion="异常: high connections", anomalies=[
            AnomalySignal(signal_type="high_connections", description=""),
        ])
        graph = {"k8s": ["db"], "db": []}
        chains = _infer_causal_chains(graph, [a1, a2])
        assert len(chains) >= 1
        chain = chains[0]
        assert "CrashLoopBackOff" in chain["anomalies_along_path"] or "high_connections" in chain["anomalies_along_path"]


class TestDetectCrossAgentContradictions:
    def test_k8s_anomaly_metrics_normal(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: pods failing")
        a2 = _make_analysis(category="metrics", conclusion="正常: all ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert any(c["anomaly_category"] == "k8s" and c["normal_category"] == "metrics" for c in contradictions)

    def test_all_normal_no_contradictions(self):
        a1 = _make_analysis(category="k8s", conclusion="正常: ok")
        a2 = _make_analysis(category="metrics", conclusion="正常: ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert len(contradictions) == 0

    def test_both_anomaly_no_contradictions(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: broken")
        a2 = _make_analysis(category="metrics", conclusion="异常: spikes")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert len(contradictions) == 0

    def test_db_anomaly_k8s_normal(self):
        a1 = _make_analysis(category="db", conclusion="异常: slow queries")
        a2 = _make_analysis(category="k8s", conclusion="正常: ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert any(c["anomaly_category"] == "db" and c["normal_category"] == "k8s" for c in contradictions)

    def test_logs_anomaly_k8s_normal(self):
        a1 = _make_analysis(category="logs", conclusion="异常: many errors")
        a2 = _make_analysis(category="k8s", conclusion="正常: ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert any(c["anomaly_category"] == "logs" and c["normal_category"] == "k8s" for c in contradictions)

    def test_metrics_anomaly_k8s_normal(self):
        a1 = _make_analysis(category="metrics", conclusion="异常: cpu spike")
        a2 = _make_analysis(category="k8s", conclusion="正常: ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert any(c["anomaly_category"] == "metrics" and c["normal_category"] == "k8s" for c in contradictions)

    def test_k8s_anomaly_deployment_normal(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: pods failing")
        a2 = _make_analysis(category="deployments", conclusion="正常: no recent deploy")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert any(c["anomaly_category"] == "k8s" and c["normal_category"] == "deployments" for c in contradictions)

    def test_db_anomaly_metrics_normal(self):
        a1 = _make_analysis(category="db", conclusion="异常: lock wait")
        a2 = _make_analysis(category="metrics", conclusion="正常: ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        assert any(c["anomaly_category"] == "db" and c["normal_category"] == "metrics" for c in contradictions)


class TestComputeWeightedQuality:
    def test_all_completed_high_quality(self):
        analyses = [
            _make_analysis(cat, confidence=0.85) for cat in ["k8s", "db", "logs", "metrics", "deployments"]
        ]
        score = _compute_weighted_quality(analyses)
        assert score >= 0.5

    def test_two_partial_three_normal(self):
        analyses = [
            _make_analysis("k8s", confidence=0.8),
            _make_analysis("db", confidence=0.25, partial=True),
            _make_analysis("logs", confidence=0.8),
            _make_analysis("metrics", confidence=0.25, partial=True),
            _make_analysis("deployments", confidence=0.8),
        ]
        score = _compute_weighted_quality(analyses)
        assert 0.0 < score < 0.8

    def test_all_llm_failed_zero_quality(self):
        analyses = [
            _make_analysis(cat, confidence=0.0, run_status=AgentRunStatus.LLM_FAILED)
            for cat in ["k8s", "db", "logs", "metrics", "deployments"]
        ]
        score = _compute_weighted_quality(analyses)
        assert score == 0.0

    def test_empty_analyses_zero(self):
        assert _compute_weighted_quality([]) == 0.0

    def test_singe_completed(self):
        analyses = [_make_analysis("k8s", confidence=0.9)]
        score = _compute_weighted_quality(analyses)
        coverage = 1.0 / 5.0
        assert score == pytest.approx(0.9 * coverage, abs=0.01)


class TestGetConclusionPrefix:
    def test_normal(self):
        a = _make_analysis(conclusion="正常: all healthy")
        assert _get_conclusion_prefix(a) == "正常"

    def test_anomaly(self):
        a = _make_analysis(conclusion="异常: pods failing")
        assert _get_conclusion_prefix(a) == "异常"

    def test_partial(self):
        a = _make_analysis(conclusion="部分: partial data")
        assert _get_conclusion_prefix(a) == "部分"

    def test_failed(self):
        a = _make_analysis(conclusion="失败: cannot analyze")
        assert _get_conclusion_prefix(a) == "失败"

    def test_llm_failed_status(self):
        a = _make_analysis(conclusion="", run_status=AgentRunStatus.LLM_FAILED)
        assert _get_conclusion_prefix(a) == "失败"

    def test_partial_status_no_conclusion(self):
        a = _make_analysis(conclusion="", partial=True, run_status=AgentRunStatus.PARTIAL)
        assert _get_conclusion_prefix(a) == "部分"


class TestFormatGlobalSummary:
    def test_basic_summary(self):
        analyses = [_make_analysis(category=cat) for cat in ["k8s", "db"]]
        summary = _format_global_summary(analyses, 0.8, [], [])
        assert "Agent 完成: 2/2" in summary
        assert "质量评分: 0.80" in summary

    def test_with_contradictions(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: pods failing")
        a2 = _make_analysis(category="metrics", conclusion="正常: ok")
        contradictions = _detect_cross_agent_contradictions([a1, a2])
        summary = _format_global_summary([a1, a2], 0.5, contradictions, [])
        assert "矛盾信号" in summary

    def test_with_causal_chains(self):
        a1 = _make_analysis(category="k8s", conclusion="异常: crash", anomalies=[
            AnomalySignal(signal_type="CrashLoopBackOff", description=""),
        ], hints=[
            CorrelationHint(source_category="k8s", target_category="db", reason="linked", confidence=0.8, source="llm"),
        ])
        a2 = _make_analysis(category="db", conclusion="异常: slow", anomalies=[
            AnomalySignal(signal_type="slow_queries", description=""),
        ])
        graph = _build_correlation_graph([a1, a2])
        chains = _infer_causal_chains(graph, [a1, a2])
        assert len(chains) > 0
        summary = _format_global_summary([a1, a2], 0.6, [], chains)
        assert "因果链" in summary

    def test_with_degraded(self):
        a1 = _make_analysis(category="k8s", partial=True)
        a2 = _make_analysis(category="db")
        summary = _format_global_summary([a1, a2], 0.7, [], [])
        assert "[降级]" in summary
