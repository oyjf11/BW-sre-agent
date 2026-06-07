"""Tests for structured incident_type output from diagnose_node (mock LLM)."""

from app.graph.nodes import _coerce_incident_type, diagnose_node
from app.graph.state import RunStatus
from app.models.incident import IncidentTicket
from app.models.incident_type import IncidentType
from app.llm_client import llm_client


def _state():
    ticket = IncidentTicket(
        ticket_id="t1",
        title="5xx after release",
        description="errors spiked post deploy",
        service="payment-service",
        env="staging",
        severity="P2",
        source="manual",
    )
    return {
        "run_id": "diag-1",
        "ticket": ticket,
        "triage": {"incident_type": "deployment_regression"},
        "evidence_items": [],
        "root_cause_candidates": [],
    }


def test_incident_type_always_in_enum(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          {"incident_type": "deployment_regression", "hypothesis": "bad deploy",
           "confidence": 0.8, "next_checks": ["rollback"]}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    cands = out["root_cause_candidates"]
    assert len(cands) >= 1
    for c in cands:
        assert isinstance(c.incident_type, IncidentType)
    assert cands[0].incident_type == IncidentType.deployment_regression


def test_illegal_type_downgrades_to_other(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          {"incident_type": "aliens_did_it", "hypothesis": "ufo",
           "confidence": 0.9, "next_checks": []}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    assert out["root_cause_candidates"][0].incident_type == IncidentType.other


def test_candidates_sorted_by_confidence_desc(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          {"incident_type": "resource_exhaustion", "hypothesis": "low", "confidence": 0.3, "next_checks": []},
          {"incident_type": "deployment_regression", "hypothesis": "high", "confidence": 0.9, "next_checks": []},
          {"incident_type": "dependency_failure", "hypothesis": "mid", "confidence": 0.6, "next_checks": []}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    confs = [c.confidence for c in out["root_cause_candidates"]]
    assert confs == sorted(confs, reverse=True)
    assert out["root_cause_candidates"][0].incident_type == IncidentType.deployment_regression


def test_llm_failure_falls_back_to_unknown(monkeypatch):
    def boom(prompt, system_prompt=None, temperature=0.7):
        raise RuntimeError("LLM down")

    monkeypatch.setattr(llm_client, "complete_sync", boom)
    out = diagnose_node(_state())
    cands = out["root_cause_candidates"]
    assert len(cands) >= 1
    assert all(c.incident_type == IncidentType.unknown for c in cands)
    assert out["status"] == RunStatus.DIAGNOSED


def test_missing_type_defaults_to_unknown(monkeypatch):
    # LLM returns candidate WITHOUT incident_type key
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[{"hypothesis": "no type given", "confidence": 0.5, "next_checks": []}]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    assert out["root_cause_candidates"][0].incident_type == IncidentType.unknown


def test_coerce_incident_type_accepts_enum_instance():
    assert (
        _coerce_incident_type(IncidentType.deployment_regression)
        == IncidentType.deployment_regression
    )


def test_coerce_incident_type_blank_string_defaults_to_unknown():
    assert _coerce_incident_type("   ") == IncidentType.unknown


def test_bad_candidates_do_not_drop_valid_candidates(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          "not a candidate object",
          {"incident_type": "deployment_regression", "hypothesis": "bad confidence",
           "confidence": "not-a-number", "next_checks": []},
          {"incident_type": "dependency_failure", "hypothesis": "valid candidate",
           "confidence": 0.66, "next_checks": ["check dependency"]}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    cands = out["root_cause_candidates"]
    assert len(cands) == 1
    assert cands[0].hypothesis == "valid candidate"
    assert cands[0].incident_type == IncidentType.dependency_failure


class TestTriageReferenceAlignment:
    """triage still emits the same string values, now sourced from the enum."""

    def test_deploy_rule_emits_enum_value(self):
        from app.graph.nodes import _triage_by_rules

        r = _triage_by_rules("Release rollback failed", "", "P1", "svc", "prod")
        assert r is not None
        assert r.incident_type == IncidentType.deployment_regression.value

    def test_resource_rule_emits_enum_value(self):
        from app.graph.nodes import _triage_by_rules

        r = _triage_by_rules("OOM killed pod", "memory leak", "P2", "svc", "staging")
        assert r is not None
        assert r.incident_type == IncidentType.resource_exhaustion.value

    def test_dependency_rule_emits_enum_value(self):
        from app.graph.nodes import _triage_by_rules

        r = _triage_by_rules("downstream timeout 503", "", "P2", "svc", "staging")
        assert r is not None
        assert r.incident_type == IncidentType.dependency_failure.value

    def test_fallback_emits_enum_value(self):
        from app.graph.nodes import _triage_fallback

        r = _triage_fallback("weird thing", "P3", "svc")
        assert r.incident_type == IncidentType.service_degradation.value
