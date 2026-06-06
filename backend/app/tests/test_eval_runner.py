"""Tests for eval orchestration: state build, single-case isolation, repeat."""
import json

import pytest

from app.evals.runner import build_initial_state, run_dataset, run_one_case
from app.evals.scorer import CaseResult


class _StubExecutor:
    mode = "stub"

    def __init__(self, type_by_case):
        self._type_by_case = type_by_case
        self.seen_fixtures = []

    async def execute(self, case_id, initial_state):
        from app.evals.fixture_context import get_active_fixtures

        self.seen_fixtures.append((case_id, get_active_fixtures()))
        return {
            "root_cause_candidates": [
                {
                    "candidate_id": "x",
                    "hypothesis": "h",
                    "confidence": 0.8,
                    "incident_type": self._type_by_case[case_id],
                }
            ],
            "risk_decision": "LOW_ONLY",
            "status": "COMPLETED",
        }


def _case(case_id, expected_type, fixtures=None):
    return {
        "case_id": case_id,
        "ticket": {
            "ticket_id": "INC-1",
            "title": "t",
            "description": "d",
            "service": "svc",
            "env": "staging",
            "severity": "P2",
            "source": "manual",
        },
        "tool_fixtures": fixtures or {},
        "expected": {"incident_type": expected_type},
    }


def test_build_initial_state_from_case():
    state = build_initial_state(_case("c1", "deployment_regression"))
    assert state["run_id"] == "eval-c1"
    ticket = state["ticket"]
    assert ticket.service == "svc"
    assert state["evidence_items"] == []
    assert state["step_count"] == 0


@pytest.mark.asyncio
async def test_run_one_case_scores_hit():
    executor = _StubExecutor({"c1": "deployment_regression"})
    result = await run_one_case(_case("c1", "deployment_regression"), executor)
    assert isinstance(result, CaseResult)
    assert result.hit_top1 is True


@pytest.mark.asyncio
async def test_run_one_case_injects_fixture_scope():
    executor = _StubExecutor({"c1": "deployment_regression"})
    await run_one_case(
        _case("c1", "deployment_regression", {"query_logs": {"count": 5}}),
        executor,
    )
    case_id, fixtures = executor.seen_fixtures[0]
    assert case_id == "c1"
    assert fixtures == {"query_logs": {"count": 5}}


@pytest.mark.asyncio
async def test_run_one_case_captures_executor_error():
    class _Boom:
        mode = "boom"

        async def execute(self, case_id, initial_state):
            raise RuntimeError("kaboom")

    result = await run_one_case(_case("c1", "deployment_regression"), _Boom())
    assert result.error is not None
    assert "kaboom" in result.error


@pytest.mark.asyncio
async def test_run_dataset_repeats(tmp_path):
    for case_id, incident_type in [
        ("c1", "deployment_regression"),
        ("c2", "resource_exhaustion"),
    ]:
        (tmp_path / f"{case_id}.json").write_text(
            json.dumps(_case(case_id, incident_type)),
            encoding="utf-8",
        )

    executor = _StubExecutor(
        {"c1": "deployment_regression", "c2": "resource_exhaustion"}
    )
    rounds_results, rounds_metrics, aggregate = await run_dataset(
        str(tmp_path),
        executor,
        repeat=3,
    )
    assert len(rounds_results) == 3
    assert len(rounds_metrics) == 3
    assert aggregate["rounds"] == 3
    assert aggregate["top1_accuracy"]["mean"] == 1.0
