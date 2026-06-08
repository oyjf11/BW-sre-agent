from datetime import datetime

from app.graph.nodes import rca_node, remediation_node, risk_gate_node
from app.graph.state import RunStatus
from app.models.action import ActionSpec
from app.models.evidence import EvidenceItem
from app.models.incident import IncidentTicket
from app.models.incident_type import IncidentType
from app.models.rca import RcaReport
from app.models.remediation import RemediationPlan
from app.models.root_cause import RootCauseCandidate


def _ticket(env: str = "prod") -> IncidentTicket:
    return IncidentTicket(
        ticket_id="INC-001",
        title="支付服务5xx升高",
        description="发布后部分用户下单失败",
        service="payment-service",
        env=env,
        severity="P2",
        source="manual",
    )


def _deployment_evidence() -> EvidenceItem:
    return EvidenceItem(
        evidence_id="ev-deploy-1",
        tool_name="query_deployments",
        category="deployments",
        source_ref="deployments/payment-service",
        source_timestamp=datetime.utcnow(),
        summary="Recent deployment changed payment-service before the incident",
        raw_payload={"deployment_id": "dep-1"},
        confidence=0.9,
        freshness_score=0.9,
        completeness_score=0.9,
    )


def test_remediation_uses_incident_type_for_chinese_deployment_regression():
    state = {
        "ticket": _ticket(),
        "root_cause_candidates": [
            RootCauseCandidate(
                candidate_id="rc-1",
                hypothesis="本次发布的代码变更引入了支付处理逻辑异常",
                confidence=0.88,
                incident_type=IncidentType.deployment_regression,
                supporting_evidence_ids=["ev-deploy-1"],
            )
        ],
        "evidence_items": [_deployment_evidence()],
        "step_count": 0,
    }

    result = remediation_node(state)

    action = result["remediation_plan"].actions[0]
    assert action.action_type == "rollback"
    assert action.risk_level == "HIGH"
    assert action.requires_approval is True


def test_risk_gate_requires_approval_for_prod_restart_floor():
    state = {
        "ticket": {"env": "prod", "severity": "P2"},
        "remediation_plan": RemediationPlan(
            summary="restart service",
            actions=[
                ActionSpec(
                    action_type="restart",
                    service="payment-service",
                    env="prod",
                    params={},
                    risk_level="LOW",
                    requires_approval=False,
                )
            ],
            expected_outcome="recover",
            rollback_plan="none",
        ),
        "user_context": {},
        "root_cause_candidates": [{"confidence": 0.9}],
        "step_count": 0,
    }

    result = risk_gate_node(state)

    assert result["risk_decision"] == "NEEDS_APPROVAL"


def test_rca_execution_results_deduplicate_and_read_action_type_from_result(monkeypatch):
    captured_prompt = {}

    def fake_complete(prompt: str, system_prompt: str):
        captured_prompt["text"] = prompt
        return ""

    monkeypatch.setattr("app.graph.nodes.llm_client.complete_sync", fake_complete)

    state = {
        "run_id": "run-rca",
        "ticket": _ticket(env="staging"),
        "status": RunStatus.COMPLETED,
        "verify_decision": "SUCCESS",
        "root_cause_candidates": [
            RootCauseCandidate(
                candidate_id="rc-1",
                hypothesis="本次发布导致接口错误",
                confidence=0.9,
                incident_type=IncidentType.deployment_regression,
            )
        ],
        "remediation_plan": RemediationPlan(
            summary="restart service",
            actions=[
                ActionSpec(
                    action_id="act-1",
                    action_type="restart",
                    service="payment-service",
                    env="staging",
                    params={},
                    risk_level="LOW",
                    requires_approval=False,
                )
            ],
            expected_outcome="recover",
            rollback_plan="none",
        ),
        "execution_results": [
            {
                "action_id": "act-1",
                "success": True,
                "result": {"action_type": "restart"},
                "error": None,
                "skipped": False,
            }
        ],
        "action_results": [
            {
                "action_id": "act-1",
                "success": True,
                "result": {"action_type": "restart"},
                "error": None,
                "skipped": False,
            }
        ],
        "evidence_items": [_deployment_evidence()],
        "step_count": 12,
        "loop_count": 0,
    }

    result = rca_node(state)

    report: RcaReport = result["rca_report"]
    assert captured_prompt["text"].count("- restart: SUCCESS") == 1
    assert "- unknown: SUCCESS" not in captured_prompt["text"]
    assert report.report_markdown.count("- restart: SUCCESS") == 1
    assert "- unknown: SUCCESS" not in report.report_markdown
