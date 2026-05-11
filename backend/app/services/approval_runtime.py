"""ApprovalRuntime: handles approval interrupt/resume lifecycle."""

import logging
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.graph.serde import deserialize_state, serialize_state
from app.graph.state import IncidentAgentState, RunStatus
from app.models.db_models import RunStatusEnum
from app.repositories.approvals_repo import ApprovalsRepo
from app.repositories.checkpoints_repo import CheckpointsRepo
from app.repositories.runs_repo import RunsRepo
from app.services.event_bus import EventType, event_bus

logger = logging.getLogger(__name__)


class ApprovalRuntime:
    def __init__(self, db: Session):
        self.db = db
        self.approvals_repo = ApprovalsRepo(db)
        self.runs_repo = RunsRepo(db)
        self.checkpoints_repo = CheckpointsRepo(db)

    def handle_decision(
        self,
        approval_id: str,
        decision: str,
        approver: str = "human",
        comment: Optional[str] = None,
    ):
        """Process an approval decision: approved/rejected/modify/more_evidence."""
        approval = self.approvals_repo.get(approval_id)
        if not approval:
            raise ValueError(f"Approval {approval_id} not found")

        run_id = approval.run_id
        status_map = {
            "approved": "APPROVED",
            "rejected": "REJECTED",
            "modify": "MODIFIED",
            "more_evidence": "NEED_MORE_EVIDENCE",
        }
        new_status = status_map.get(decision)
        if not new_status:
            raise ValueError(f"Invalid decision: {decision}")

        self.approvals_repo.update(
            approval_id, status=new_status, approver=approver, comment=comment
        )
        event_bus.publish(
            db=self.db,
            run_id=run_id,
            event_type=EventType.APPROVAL_DECIDED,
            message=f"Approval {decision} by {approver}",
            data={"approval_id": approval_id, "decision": decision, "comment": comment},
        )

        if decision == "rejected":
            self.runs_repo.update(
                run_id,
                status=RunStatusEnum.FAILED,
                last_error_code="APPROVAL_REJECTED",
                last_error_message=comment or "Approval rejected by human",
            )

        return approval

    def get_resume_state(self, run_id: str) -> Tuple[IncidentAgentState, str]:
        """Load the last checkpoint state for a run to resume from."""
        checkpoint = self.checkpoints_repo.load_latest(run_id)
        if not checkpoint:
            raise ValueError(f"No checkpoint found for run {run_id}")
        return deserialize_state(checkpoint.state_json), checkpoint.node_name

    def prepare_resume_state(
        self,
        run_id: str,
        approval_id: str,
        decision: str,
        approver: str = "human",
        comment: Optional[str] = None,
        decision_data: Optional[dict] = None,
    ) -> Tuple[IncidentAgentState, str]:
        """Prepare state for resuming after an approval decision.

        Sets _resume_from_node so the graph dispatcher routes to the right node
        instead of restarting from node_intake.

        IMPORTANT: We load the checkpoint from node_risk_gate (the node before
        approval_interrupt) because node_approval_interrupt is NOT in the allowed
        resume nodes list. Loading from it would cause the dispatcher to fall back
        to node_intake and re-run the entire flow.
        """
        # Try to load from node_risk_gate checkpoint first (the node before approval_interrupt)
        checkpoint = self.checkpoints_repo.load_latest(run_id, node_name="node_risk_gate")
        if not checkpoint:
            # Fallback to latest checkpoint
            checkpoint = self.checkpoints_repo.load_latest(run_id)
        if not checkpoint:
            raise ValueError(f"No checkpoint found for run {run_id}")

        state = deserialize_state(checkpoint.state_json)

        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"prepare_resume_state: loaded checkpoint from node={checkpoint.node_name}")
        logger.info(f"prepare_resume_state: state keys={list(state.keys())}")
        logger.info(f"prepare_resume_state: risk_decision={state.get('risk_decision')}")

        if decision == "approved":
            state["_resume_from_node"] = "node_executor"
            state["status"] = RunStatus.EXECUTING
            state["approval_result"] = {
                "approval_id": approval_id,
                "decision": "approved",
                "approver": approver,
                "comment": comment,
                "created_at": datetime.utcnow().isoformat(),
            }
            # Override risk_decision to LOW_ONLY so risk_gate routes to executor if re-executed
            state["risk_decision"] = "LOW_ONLY"
            logger.info(
                f"prepare_resume_state: setting _resume_from_node=node_executor, risk_decision=LOW_ONLY"
            )
            logger.info(f"prepare_resume_state: state keys={list(state.keys())}")
            logger.info(f"prepare_resume_state: _resume_from_node={state.get('_resume_from_node')}")
            event_bus.publish(
                db=self.db,
                run_id=run_id,
                event_type=EventType.RUN_RESUMED,
                message=f"Run resuming from node_executor after approval {approval_id}",
                data={"approval_id": approval_id, "resume_node": "node_executor"},
            )
        elif decision == "modify":
            self._apply_modify(state, decision_data or {})
            state["_resume_from_node"] = "node_risk_gate"
            state["status"] = RunStatus.EXECUTING
            state["approval_result"] = {
                "approval_id": approval_id,
                "decision": "modify",
                "approver": approver,
                "comment": comment,
                "created_at": datetime.utcnow().isoformat(),
            }
            event_bus.publish(
                db=self.db,
                run_id=run_id,
                event_type=EventType.RUN_RESUMED,
                message=f"Run resuming from node_risk_gate after modify {approval_id}",
                data={"approval_id": approval_id, "resume_node": "node_risk_gate"},
            )
        elif decision == "more_evidence":
            self._apply_more_evidence(state, decision_data or {})
            state["_resume_from_node"] = "node_evidence_fanout"
            state["status"] = RunStatus.GATHERING_EVIDENCE
            state["approval_result"] = {
                "approval_id": approval_id,
                "decision": "more_evidence",
                "approver": approver,
                "comment": comment,
                "created_at": datetime.utcnow().isoformat(),
            }
            event_bus.publish(
                db=self.db,
                run_id=run_id,
                event_type=EventType.RUN_RESUMED,
                message=f"Run resuming from node_evidence_fanout after more_evidence {approval_id}",
                data={"approval_id": approval_id, "resume_node": "node_evidence_fanout"},
            )

        return state, checkpoint.node_name

    def _apply_modify(self, state: IncidentAgentState, decision_data: dict) -> None:
        """Write back a human-modified remediation plan into state.

        The modified plan is accepted as a plain dict matching RemediationPlan fields.
        If no modified_plan is provided, state is unchanged (existing plan is used as-is).
        """
        modified_plan = decision_data.get("modified_plan")
        if not modified_plan:
            return

        from app.models.remediation import RemediationPlan

        try:
            plan = RemediationPlan(**modified_plan)
            state["remediation_plan"] = plan
        except Exception as e:
            logger.warning(f"Could not parse modified_plan, keeping original: {e}")

    def _apply_more_evidence(self, state: IncidentAgentState, decision_data: dict) -> None:
        """Update investigation plan and user context so evidence_fanout collects new evidence.

        Appends new InvestigationTask objects based on additional_categories.
        Also stores additional_context in user_context for nodes to reference.
        """
        from app.models.planning import InvestigationPlan, InvestigationTask

        additional_categories: list = decision_data.get("additional_categories") or []
        additional_context: str = decision_data.get("additional_context") or ""

        # Update user_context so downstream nodes can reference the request
        user_ctx = dict(state.get("user_context") or {})
        user_ctx["more_evidence_requested"] = {
            "categories": additional_categories,
            "context": additional_context,
            "requested_at": datetime.utcnow().isoformat(),
        }
        state["user_context"] = user_ctx

        # Append new tasks to the existing investigation plan
        if additional_categories:
            existing_plan = state.get("investigation_plan")
            if existing_plan and hasattr(existing_plan, "tasks"):
                existing_tasks = list(existing_plan.tasks)
            elif isinstance(existing_plan, dict):
                existing_tasks = [InvestigationTask(**t) for t in existing_plan.get("tasks", [])]
            else:
                existing_tasks = []

            # Determine next task_id index
            next_idx = len(existing_tasks) + 1
            new_tasks = []
            for cat in additional_categories:
                tool_map = {
                    "logs": "query_logs",
                    "metrics": "query_metrics",
                    "deployments": "query_recent_deployments",
                    "k8s": "query_k8s_events",
                    "lb": "query_lb_health_status",
                    "runbook": "search_runbooks",
                }
                tool_name = tool_map.get(cat, f"query_{cat}")
                new_tasks.append(
                    InvestigationTask(
                        task_id=f"extra_{next_idx}_{cat}",
                        category=cat,
                        tool_name=tool_name,
                        priority=3,
                        params={},
                    )
                )
                next_idx += 1

            if existing_plan and hasattr(existing_plan, "tasks"):
                state["investigation_plan"] = existing_plan.model_copy(
                    update={"tasks": existing_tasks + new_tasks}
                )
            else:
                rationale = (
                    (existing_plan or {}).get("rationale", "")
                    if isinstance(existing_plan, dict)
                    else ""
                )
                state["investigation_plan"] = InvestigationPlan(
                    tasks=existing_tasks + new_tasks,
                    rationale=rationale or "Supplemental investigation requested by human",
                )
