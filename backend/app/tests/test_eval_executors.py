"""Tests for DirectGraphExecutor end-to-end with mock LLM + fixture injection."""
import pytest

from app.evals.executors import DirectGraphExecutor, GraphExecutor
from app.evals.fixture_context import fixture_scope
from app.graph.state import RunStatus
from app.llm_client import llm_client
from app.models.incident import IncidentTicket
from app.models.incident_type import IncidentType


def _initial_state(case_id="exec-1"):
    ticket = IncidentTicket(
        ticket_id="INC-X",
        title="5xx after release",
        description="errors spiked post deploy",
        service="payment-service",
        env="staging",
        severity="P2",
        source="manual",
    )
    return {
        "run_id": f"eval-{case_id}",
        "thread_id": f"eval-{case_id}",
        "ticket": ticket,
        "events": [],
        "evidence_items": [],
        "root_cause_candidates": [],
        "evidence_collection_results": [],
        "evidence_quality_score": 0.0,
        "step_count": 0,
        "status": RunStatus.NEW,
    }


def _install_mock_llm(monkeypatch):
    def fake_complete_sync(prompt, system_prompt=None, temperature=0.7):
        if "incident_type" in prompt and "root cause candidates" in prompt:
            return """[
              {"incident_type": "deployment_regression",
               "hypothesis": "release introduced regression",
               "confidence": 0.85, "next_checks": ["rollback"]}
            ]"""
        if "triage information" in prompt:
            return """{"incident_type": "deployment_regression", "severity": "P2",
                       "suspected_services": ["payment-service"],
                       "suggested_time_window": {"start": "2h ago", "end": "now"},
                       "requires_immediate_human": false, "rationale": "deploy"}"""
        return "fallback_response"

    monkeypatch.setattr(llm_client, "complete_sync", fake_complete_sync)


@pytest.mark.asyncio
async def test_direct_executor_runs_end_to_end(monkeypatch):
    _install_mock_llm(monkeypatch)

    executor = DirectGraphExecutor()
    fixtures = {
        "query_logs": {"logs": [{"msg": "500"}], "count": 12},
        "query_deployments": {"deployments": [{"version": "v2"}], "count": 1},
    }
    with fixture_scope(fixtures):
        final_state = await executor.execute("exec-1", _initial_state())

    assert final_state is not None
    candidates = final_state.get("root_cause_candidates") or []
    assert len(candidates) >= 1
    top = candidates[0]
    top_type = top.incident_type if hasattr(top, "incident_type") else top.get("incident_type")
    type_value = top_type.value if hasattr(top_type, "value") else top_type
    assert type_value == IncidentType.deployment_regression.value


@pytest.mark.asyncio
async def test_direct_executor_fixture_controls_evidence(monkeypatch):
    _install_mock_llm(monkeypatch)
    executor = DirectGraphExecutor()

    with fixture_scope({"query_logs": {"logs": [{"m": "x"}], "count": 99}}):
        final_state = await executor.execute("exec-2", _initial_state("exec-2"))

    log_items = [
        evidence
        for evidence in final_state.get("evidence_items", [])
        if (
            evidence.tool_name
            if hasattr(evidence, "tool_name")
            else evidence.get("tool_name")
        )
        == "query_logs"
    ]
    assert log_items, "expected query_logs evidence from fixture"
    raw = (
        log_items[0].raw_payload
        if hasattr(log_items[0], "raw_payload")
        else log_items[0].get("raw_payload")
    )
    assert raw.get("count") == 99


def test_direct_executor_satisfies_protocol():
    executor = DirectGraphExecutor()
    assert isinstance(executor, GraphExecutor)
    assert executor.mode == "direct"
