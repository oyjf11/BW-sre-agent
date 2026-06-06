"""Tests for structured incident_type output from diagnose_node (mock LLM)."""
import pytest

from app.graph.nodes import diagnose_node
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
