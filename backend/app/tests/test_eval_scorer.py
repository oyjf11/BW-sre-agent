"""Tests for deterministic per-case scoring."""
from app.evals.scorer import CaseResult, score_case
from app.graph.state import RunStatus
from app.models.incident_type import IncidentType
from app.models.root_cause import RootCauseCandidate


def _case(expected):
    return {"case_id": "c1", "ticket": {}, "expected": expected}


def _cand(incident_type, conf):
    return RootCauseCandidate(
        candidate_id="x",
        hypothesis="h",
        confidence=conf,
        incident_type=incident_type,
    )


def test_top1_hit_and_miss():
    state = {
        "root_cause_candidates": [
            _cand(IncidentType.deployment_regression, 0.9),
            _cand(IncidentType.resource_exhaustion, 0.4),
        ],
        "risk_decision": "NEEDS_APPROVAL",
        "status": RunStatus.WAITING_HUMAN,
    }
    r = score_case(_case({"incident_type": "deployment_regression"}), state, 120)
    assert r.hit_top1 is True
    assert r.actual_type == "deployment_regression"
    assert r.confidence == 0.9
    assert r.latency_ms == 120

    r2 = score_case(_case({"incident_type": "resource_exhaustion"}), state, 120)
    assert r2.hit_top1 is False
    assert r2.hit_top3 is True


def test_top3_miss():
    state = {"root_cause_candidates": [_cand(IncidentType.deployment_regression, 0.9)]}
    r = score_case(_case({"incident_type": "database_failure"}), state, 50)
    assert r.hit_top1 is False
    assert r.hit_top3 is False


def test_risk_and_status_match():
    state = {
        "root_cause_candidates": [_cand(IncidentType.deployment_regression, 0.8)],
        "risk_decision": "NEEDS_APPROVAL",
        "status": RunStatus.WAITING_HUMAN,
    }
    r = score_case(
        _case(
            {
                "incident_type": "deployment_regression",
                "risk_decision": "NEEDS_APPROVAL",
                "final_status": "WAITING_HUMAN",
            }
        ),
        state,
        10,
    )
    assert r.risk_match is True
    assert r.status_match is True


def test_unset_expected_fields_are_skipped_as_none():
    state = {
        "root_cause_candidates": [_cand(IncidentType.deployment_regression, 0.8)],
        "risk_decision": "LOW_ONLY",
        "status": RunStatus.COMPLETED,
    }
    r = score_case(_case({"incident_type": "deployment_regression"}), state, 10)
    assert r.risk_match is None
    assert r.status_match is None


def test_handles_dict_candidates_from_checkpoint():
    state = {
        "root_cause_candidates": [
            {
                "candidate_id": "x",
                "hypothesis": "h",
                "confidence": 0.7,
                "incident_type": "network_failure",
            }
        ],
    }
    r = score_case(_case({"incident_type": "network_failure"}), state, 5)
    assert r.hit_top1 is True
    assert r.actual_type == "network_failure"


def test_no_candidates_gives_none_actual():
    state = {"root_cause_candidates": []}
    r = score_case(_case({"incident_type": "deployment_regression"}), state, 5)
    assert r.actual_type is None
    assert r.hit_top1 is False


def test_error_result_factory():
    r = CaseResult.error_result("c9", "BoomError: x", 33)
    assert r.case_id == "c9"
    assert r.error == "BoomError: x"
    assert r.hit_top1 is None
    assert r.latency_ms == 33
