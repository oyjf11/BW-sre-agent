"""GraphRunner: wraps graph execution with event recording, checkpoint, and status tracking."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from sqlalchemy.orm import Session

from app.graph.builder import create_incident_graph
from app.graph.context import set_node_event_hook, reset_node_event_hook
from app.graph.serde import serialize_state
from app.graph.state import IncidentAgentState, RunStatus
from app.models.db_models import RunStatusEnum
from app.repositories.checkpoints_repo import CheckpointsRepo
from app.repositories.evidence_repo import EvidenceRepo
from app.repositories.runs_repo import RunsRepo
from app.repositories.rca_repo import RcaRepo
from app.services.event_bus import EventBus, EventType, event_bus

import uuid

logger = logging.getLogger(__name__)


class GraphRunner:
    def __init__(self, db: Session, bus: Optional[EventBus] = None):
        self.db = db
        self.bus = bus or event_bus
        self.runs_repo = RunsRepo(db)
        self.checkpoints_repo = CheckpointsRepo(db)
        self.evidence_repo = EvidenceRepo(db)
        self.rca_repo = RcaRepo(db)
        self._persisted_evidence_ids: set = set()

    def _initialize_persisted_evidence_ids(self, state: IncidentAgentState):
        """Seed in-memory dedupe set from already collected evidence in resumed state."""
        items = state.get("evidence_items", [])
        self._persisted_evidence_ids = {
            item.evidence_id if hasattr(item, "evidence_id") else item.get("evidence_id", "")
            for item in items
        }
        self._persisted_evidence_ids.discard("")

    def _emit(
        self,
        run_id: str,
        event_type: EventType,
        node_name: Optional[str] = None,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
    ):
        self.bus.publish(
            db=self.db,
            run_id=run_id,
            event_type=event_type,
            node_name=node_name,
            message=message,
            data=data,
            level=level,
        )

    def _update_run(self, run_id: str, **kwargs):
        self.runs_repo.update(run_id, **kwargs)

    def _coerce_run_status(self, status: Any) -> Optional[RunStatusEnum]:
        """Normalize graph state status to the DB enum without crashing on bad values."""
        if status is None:
            return None

        value = status.value if hasattr(status, "value") else status
        try:
            return RunStatusEnum(value)
        except ValueError:
            logger.warning("Ignoring invalid run status %r for run update", value)
            return None

    def _sync_run_progress(self, run_id: str, state: IncidentAgentState):
        """Persist the latest step/status snapshot for detail-page polling."""
        update_fields: Dict[str, Any] = {}

        step = state.get("step_count")
        if step is not None:
            update_fields["step_count"] = step

        status_enum = self._coerce_run_status(state.get("status"))
        if status_enum is not None:
            update_fields["status"] = status_enum

        if update_fields:
            self._update_run(run_id, **update_fields)

    def _save_checkpoint(self, run_id: str, node_name: str, state: IncidentAgentState):
        cp_id = f"cp_{uuid.uuid4().hex[:8]}"
        serialized = serialize_state(state)
        self.checkpoints_repo.save(cp_id, run_id, node_name, serialized)
        self._emit(
            run_id,
            EventType.CHECKPOINT_SAVED,
            node_name=node_name,
            message=f"Checkpoint saved at {node_name}",
        )

    def _persist_evidence(self, run_id: str, state: IncidentAgentState):
        """Persist any new evidence_items from state to the evidence DB table."""
        items = state.get("evidence_items", [])
        for item in items:
            eid = item.evidence_id if hasattr(item, "evidence_id") else item.get("evidence_id", "")
            if not eid or eid in self._persisted_evidence_ids:
                continue
            try:
                tool_name = (
                    item.tool_name if hasattr(item, "tool_name") else item.get("tool_name", "")
                )
                category = item.category if hasattr(item, "category") else item.get("category", "")
                source_ref = (
                    item.source_ref if hasattr(item, "source_ref") else item.get("source_ref", "")
                )
                summary = item.summary if hasattr(item, "summary") else item.get("summary", "")
                raw_payload = (
                    item.raw_payload if hasattr(item, "raw_payload") else item.get("raw_payload")
                )
                self.evidence_repo.insert(
                    run_id=run_id,
                    tool_name=tool_name,
                    category=category,
                    source_ref=source_ref,
                    summary=summary,
                    raw_payload=raw_payload,
                    evidence_id=eid,
                )
                self._persisted_evidence_ids.add(eid)
            except Exception:
                logger.warning(f"Failed to persist evidence {eid}", exc_info=True)

    def _persist_rca(self, run_id: str, state: IncidentAgentState):
        """Persist RCA report from state to the RCA DB table."""
        rca_report = state.get("rca_report")
        if not rca_report:
            return

        try:
            # Handle both Pydantic model and dict (from checkpoint deserialization)
            if hasattr(rca_report, "model_dump"):
                report_dict = rca_report.model_dump()
            elif isinstance(rca_report, dict):
                report_dict = rca_report
            else:
                report_dict = {
                    "run_id": getattr(rca_report, "run_id", run_id),
                    "report_markdown": getattr(rca_report, "report_markdown", ""),
                    "root_cause": getattr(rca_report, "root_cause", ""),
                    "resolution": getattr(rca_report, "resolution", ""),
                    "prevention_items": getattr(rca_report, "prevention_items", []),
                    "timeline_summary": getattr(rca_report, "timeline_summary", None),
                    "impact_assessment": getattr(rca_report, "impact_assessment", None),
                    "supporting_evidence_ids": getattr(rca_report, "supporting_evidence_ids", []),
                    "executed_action_ids": getattr(rca_report, "executed_action_ids", []),
                }

            self.rca_repo.upsert(
                run_id=run_id,
                report_markdown=report_dict.get("report_markdown", ""),
                root_cause=report_dict.get("root_cause", ""),
                resolution=report_dict.get("resolution", ""),
                prevention_items=report_dict.get("prevention_items"),
                timeline_summary=report_dict.get("timeline_summary"),
                impact_assessment=report_dict.get("impact_assessment"),
                supporting_evidence_ids=report_dict.get("supporting_evidence_ids"),
                executed_action_ids=report_dict.get("executed_action_ids"),
            )
            logger.info(f"RCA report persisted for run {run_id}")
        except Exception:
            logger.warning(f"Failed to persist RCA report for run {run_id}", exc_info=True)

    async def run(
        self, run_id: str, initial_state: IncidentAgentState, is_resume: bool = False
    ) -> IncidentAgentState:
        """Execute the full graph with event tracking and checkpoints.

        Args:
            run_id: The run identifier
            initial_state: The initial state for graph execution
            is_resume: If True, skip RUN_CREATED event and started_at update (for approval resume)
        """
        if not is_resume:
            self._update_run(run_id, started_at=datetime.utcnow())
            self._emit(run_id, EventType.RUN_CREATED, message="Run started")
        else:
            self._initialize_persisted_evidence_ids(initial_state)

        graph = create_incident_graph()

        # Inject event hook so node wrappers can emit NODE_STARTED / NODE_FAILED
        # before and after each node executes (true pre/post execution timing).
        def _node_hook(event_type, node_name, *, message="", level="INFO", data=None):
            if event_type == EventType.NODE_STARTED and node_name:
                self._update_run(run_id, current_node=node_name)
            self._emit(
                run_id, event_type, node_name=node_name, message=message, data=data, level=level
            )

        hook_token = set_node_event_hook(_node_hook)
        try:
            if is_resume:
                resume_update: Dict[str, Any] = {"completed_at": None}
                resume_status = self._coerce_run_status(initial_state.get("status"))
                if resume_status is not None:
                    resume_update["status"] = resume_status
                self._update_run(run_id, **resume_update)

            final_state = initial_state
            async for event in graph.astream(initial_state, config={"recursion_limit": 50}):
                for node_name, node_output in event.items():
                    if node_name == "__end__":
                        continue

                    if isinstance(node_output, dict):
                        final_state = {**final_state, **node_output}

                    self._sync_run_progress(run_id, final_state)
                    step = final_state.get("step_count", 0)
                    self._save_checkpoint(run_id, node_name, final_state)
                    self._persist_evidence(run_id, final_state)
                    self._persist_rca(run_id, final_state)

                    self._emit(
                        run_id,
                        EventType.NODE_COMPLETED,
                        node_name=node_name,
                        message=f"Node {node_name} completed",
                        data={"step_count": step},
                    )

            # Determine final status
            status = final_state.get("status", RunStatus.COMPLETED)
            status_enum = self._coerce_run_status(status) or RunStatusEnum.COMPLETED

            self._update_run(
                run_id,
                status=status_enum,
                completed_at=datetime.utcnow(),
                current_node=None,
            )

            status_value = status_enum.value
            if status_enum in (RunStatusEnum.COMPLETED, RunStatusEnum.WAITING_HUMAN):
                self._emit(
                    run_id,
                    EventType.RUN_COMPLETED,
                    message=f"Run finished with status {status_value}",
                )
            else:
                self._emit(
                    run_id, EventType.RUN_COMPLETED, message=f"Run ended with status {status_value}"
                )

            return final_state

        except Exception as exc:
            logger.exception(f"Graph execution failed for run {run_id}")
            error_msg = str(exc)

            # NODE_FAILED is emitted by the node wrapper (_wrap_with_events) before
            # the exception propagates here — no need to re-emit it for the last node.
            self._update_run(
                run_id,
                status=RunStatusEnum.FAILED,
                last_error_code="GRAPH_EXECUTION_ERROR",
                last_error_message=error_msg[:1000],
                completed_at=datetime.utcnow(),
            )
            self._emit(
                run_id,
                EventType.RUN_FAILED,
                message=f"Run failed: {error_msg[:200]}",
                level="ERROR",
            )
            raise
        finally:
            reset_node_event_hook(hook_token)
