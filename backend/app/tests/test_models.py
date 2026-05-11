"""Tests for Domain Models."""
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models import (
    IncidentTicket,
    TriageResult,
    EvidenceItem,
    RootCauseCandidate,
    ActionSpec,
    RemediationPlan,
    ApprovalRequest,
    ApprovalResult,
    RcaReport,
    RunEvent,
)


class TestIncidentTicket:
    def test_create_valid(self):
        ticket = IncidentTicket(
            ticket_id="INC-001",
            title="Test Incident",
            description="Test description",
            service="api-gateway",
            env="prod",
            severity="P1",
            source="pagerduty",
        )
        assert ticket.ticket_id == "INC-001"
        assert ticket.title == "Test Incident"

    def test_serialize(self):
        ticket = IncidentTicket(
            ticket_id="INC-001",
            title="Test Incident",
            description="Test description",
            service="api-gateway",
            env="prod",
            severity="P1",
            source="pagerduty",
        )
        data = ticket.model_dump()
        assert data["ticket_id"] == "INC-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            IncidentTicket()


class TestTriageResult:
    def test_create_valid(self):
        triage = TriageResult(
            incident_type="performance",
            severity="P2",
            suspected_services=["api-gateway"],
            suggested_time_window={"start": datetime.now()},
            requires_immediate_human=False,
            rationale="High latency detected",
        )
        assert triage.incident_type == "performance"

    def test_serialize(self):
        triage = TriageResult(
            incident_type="performance",
            severity="P2",
            suspected_services=["api-gateway"],
            suggested_time_window={"start": datetime.now()},
            requires_immediate_human=False,
            rationale="High latency detected",
        )
        data = triage.model_dump()
        assert data["incident_type"] == "performance"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            TriageResult()


class TestEvidenceItem:
    def test_create_valid(self):
        evidence = EvidenceItem(
            evidence_id="ev-001",
            tool_name="query_logs",
            category="logs",
            source_ref="/logs/api-gateway/error.log",
            source_timestamp=datetime.now(),
            summary="Found error pattern in logs",
            raw_payload={"error": "timeout"},
            confidence=0.9,
            freshness_score=0.8,
            completeness_score=0.7,
        )
        assert evidence.evidence_id == "ev-001"

    def test_serialize(self):
        evidence = EvidenceItem(
            evidence_id="ev-001",
            tool_name="query_logs",
            category="logs",
            source_ref="/logs/api-gateway/error.log",
            source_timestamp=datetime.now(),
            summary="Found error pattern in logs",
            raw_payload={"error": "timeout"},
            confidence=0.9,
            freshness_score=0.8,
            completeness_score=0.7,
        )
        data = evidence.model_dump()
        assert data["evidence_id"] == "ev-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            EvidenceItem()


class TestRootCauseCandidate:
    def test_create_valid(self):
        candidate = RootCauseCandidate(
            candidate_id="rc-001",
            hypothesis="Database connection pool exhausted",
            confidence=0.85,
            supporting_evidence_ids=["ev-001", "ev-002"],
            contradicting_evidence_ids=[],
            next_checks=["check_db_connections"],
        )
        assert candidate.candidate_id == "rc-001"

    def test_serialize(self):
        candidate = RootCauseCandidate(
            candidate_id="rc-001",
            hypothesis="Database connection pool exhausted",
            confidence=0.85,
            supporting_evidence_ids=["ev-001", "ev-002"],
            contradicting_evidence_ids=[],
            next_checks=["check_db_connections"],
        )
        data = candidate.model_dump()
        assert data["candidate_id"] == "rc-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RootCauseCandidate()


class TestActionSpec:
    def test_create_valid(self):
        action = ActionSpec(
            action_type="restart",
            service="api-gateway",
            env="prod",
            params={"pods": ["api-gateway-0"]},
            risk_level="MEDIUM",
            requires_approval=True,
            idempotency_key="restart-api-001",
        )
        assert action.action_type == "restart"

    def test_serialize(self):
        action = ActionSpec(
            action_type="restart",
            service="api-gateway",
            env="prod",
            params={"pods": ["api-gateway-0"]},
            risk_level="MEDIUM",
            requires_approval=True,
            idempotency_key="restart-api-001",
        )
        data = action.model_dump()
        assert data["action_type"] == "restart"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ActionSpec()


class TestRemediationPlan:
    def test_create_valid(self):
        plan = RemediationPlan(
            summary="Restart API Gateway pods",
            actions=[
                {
                    "action_type": "restart",
                    "service": "api-gateway",
                    "env": "prod",
                    "params": {"pods": ["api-gateway-0"]},
                    "risk_level": "MEDIUM",
                    "requires_approval": True,
                    "idempotency_key": "restart-api-001",
                }
            ],
            expected_outcome="API Gateway recovered",
            rollback_plan="Scale up to 3 replicas",
            risk_notes="Brief downtime expected",
        )
        assert plan.summary == "Restart API Gateway pods"

    def test_serialize(self):
        plan = RemediationPlan(
            summary="Restart API Gateway pods",
            actions=[
                {
                    "action_type": "restart",
                    "service": "api-gateway",
                    "env": "prod",
                    "params": {"pods": ["api-gateway-0"]},
                    "risk_level": "MEDIUM",
                    "requires_approval": True,
                    "idempotency_key": "restart-api-001",
                }
            ],
            expected_outcome="API Gateway recovered",
            rollback_plan="Scale up to 3 replicas",
            risk_notes="Brief downtime expected",
        )
        data = plan.model_dump()
        assert data["summary"] == "Restart API Gateway pods"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RemediationPlan()


class TestApprovalRequest:
    def test_create_valid(self):
        approval = ApprovalRequest(
            approval_id="apr-001",
            run_id="run-001",
            action={
                "action_type": "restart",
                "service": "api-gateway",
                "env": "prod",
                "params": {"pods": ["api-gateway-0"]},
                "risk_level": "MEDIUM",
                "requires_approval": True,
                "idempotency_key": "restart-api-001",
            },
            reason="High latency in API Gateway",
            risk_level="MEDIUM",
            evidence_refs=["ev-001"],
            expected_impact="API Gateway recovered",
            rollback_plan="Scale up to 3 replicas",
        )
        assert approval.approval_id == "apr-001"

    def test_serialize(self):
        approval = ApprovalRequest(
            approval_id="apr-001",
            run_id="run-001",
            action={
                "action_type": "restart",
                "service": "api-gateway",
                "env": "prod",
                "params": {"pods": ["api-gateway-0"]},
                "risk_level": "MEDIUM",
                "requires_approval": True,
                "idempotency_key": "restart-api-001",
            },
            reason="High latency in API Gateway",
            risk_level="MEDIUM",
            evidence_refs=["ev-001"],
            expected_impact="API Gateway recovered",
            rollback_plan="Scale up to 3 replicas",
        )
        data = approval.model_dump()
        assert data["approval_id"] == "apr-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ApprovalRequest()


class TestApprovalResult:
    def test_create_valid(self):
        result = ApprovalResult(
            approval_id="apr-001",
            decision="approved",
            approver="admin@example.com",
            comment="Approved for execution",
            created_at="2024-01-01T00:00:00Z",
        )
        assert result.approval_id == "apr-001"

    def test_serialize(self):
        result = ApprovalResult(
            approval_id="apr-001",
            decision="approved",
            approver="admin@example.com",
            comment="Approved for execution",
            created_at="2024-01-01T00:00:00Z",
        )
        data = result.model_dump()
        assert data["approval_id"] == "apr-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ApprovalResult()


class TestRcaReport:
    def test_create_valid(self):
        report = RcaReport(
            run_id="run-001",
            report_markdown="# Root Cause Analysis\n\nDatabase connection pool exhausted",
            root_cause="Database connection pool size too small",
            resolution="Increased pool size from 10 to 50",
            prevention_items=["Monitor connection pool usage"],
            confirmed_by_human=True,
        )
        assert report.run_id == "run-001"

    def test_serialize(self):
        report = RcaReport(
            run_id="run-001",
            report_markdown="# Root Cause Analysis\n\nDatabase connection pool exhausted",
            root_cause="Database connection pool size too small",
            resolution="Increased pool size from 10 to 50",
            prevention_items=["Monitor connection pool usage"],
            confirmed_by_human=True,
        )
        data = report.model_dump()
        assert data["run_id"] == "run-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RcaReport()


class TestRunEvent:
    def test_create_valid(self):
        event = RunEvent(
            ts=datetime.now(),
            run_id="run-001",
            level="INFO",
            type="node_completed",
            node_name="triage_node",
            message="Triage completed successfully",
            data={"severity": "P2"},
        )
        assert event.run_id == "run-001"

    def test_serialize(self):
        event = RunEvent(
            ts=datetime.now(),
            run_id="run-001",
            level="INFO",
            type="node_completed",
            node_name="triage_node",
            message="Triage completed successfully",
            data={"severity": "P2"},
        )
        data = event.model_dump()
        assert data["run_id"] == "run-001"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            RunEvent()
