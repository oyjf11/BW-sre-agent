"""Incidents API routes."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.models.incident import IncidentTicket
from app.repositories import (
    SessionLocal,
    RunsRepo,
    RcaRepo,
    EvidenceRepo,
    ActionsRepo,
    CheckpointsRepo,
)
from app.graph.state import IncidentAgentState
from app.core.config import get_settings
from app.services.runtime import RuntimeService
from app.tracing import tracer
from app.tracing_providers import LocalTraceProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/incidents", tags=["incidents"])


# ---------- Request / Response models ----------

class IncidentTicketCreate(BaseModel):
    ticket_id: str
    title: str
    description: str
    service: str
    env: str
    severity: str
    source: str = "manual"
    time_range: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertEventCreate(BaseModel):
    alert_name: str
    service: str
    env: str
    severity: str
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    started_at: Optional[str] = None


class IncidentRunCreate(BaseModel):
    """Three mutually exclusive input modes: ticket, ticket_id, alert_event."""
    ticket: Optional[IncidentTicketCreate] = None
    ticket_id: Optional[str] = None
    alert_event: Optional[AlertEventCreate] = None


class IncidentRunResponse(BaseModel):
    run_id: str
    thread_id: str
    status: str
    severity: Optional[str] = None
    service: Optional[str] = None
    env: Optional[str] = None
    current_node: Optional[str] = None
    halted_at_node: Optional[str] = None
    terminal_reason: Optional[Dict[str, Any]] = None
    step_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RunEventResponse(BaseModel):
    event_id: str
    run_id: str
    level: str
    type: str
    node_name: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


class TraceEventResponse(BaseModel):
    name: str
    timestamp: str
    data: Dict[str, Any]


class TraceSpanResponse(BaseModel):
    span_id: str
    name: str
    run_id: Optional[str] = None
    parent_id: Optional[str] = None
    start_time: float
    start_timestamp: str
    end_time: Optional[float] = None
    end_timestamp: Optional[str] = None
    duration_ms: Optional[int] = None
    status: Optional[str] = None
    error: Optional[str] = None
    events: List[TraceEventResponse] = Field(default_factory=list)


class RunTraceResponse(BaseModel):
    run_id: str
    provider: str
    trace_url: str
    external_trace_id: Optional[str] = None
    external_root_span_id: Optional[str] = None
    external_trace_url: Optional[str] = None
    spans: List[TraceSpanResponse]


# ---------- helpers ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _run_to_response(run) -> IncidentRunResponse:
    return IncidentRunResponse(
        run_id=run.run_id,
        thread_id=run.thread_id,
        status=run.status.value if hasattr(run.status, "value") else run.status,
        severity=run.severity,
        service=run.service,
        env=run.env,
        current_node=run.current_node,
        halted_at_node=getattr(run, "halted_at_node", None),
        terminal_reason=getattr(run, "terminal_reason_json", None),
        step_count=run.step_count or 0,
        created_at=run.created_at,
        updated_at=run.updated_at,
        started_at=getattr(run, "started_at", None),
        completed_at=run.completed_at,
    )


def _event_to_response(ev) -> RunEventResponse:
    return RunEventResponse(
        event_id=ev.event_id,
        run_id=ev.run_id,
        level=ev.level,
        type=ev.type,
        node_name=ev.node_name,
        message=ev.message,
        data=ev.data_json,
        timestamp=ev.ts,
    )


def _load_latest_checkpoint_state(run_id: str, db) -> Dict[str, Any]:
    cp_repo = CheckpointsRepo(db)
    checkpoint = cp_repo.load_latest(run_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="No checkpoint found")

    state = checkpoint.state_json
    if isinstance(state, str):
        state = json.loads(state)
    if not isinstance(state, dict):
        raise HTTPException(status_code=500, detail="Invalid checkpoint state")

    return state


def _build_trace_url(run_id: str, external_trace_url: Optional[str] = None) -> str:
    if external_trace_url:
        return external_trace_url

    settings = get_settings()
    base_url = settings.tracing_public_base_url or settings.tracing_base_url
    if base_url:
        return f"{base_url.rstrip('/')}/incidents/runs/{run_id}/trace"
    return f"/incidents/runs/{run_id}/trace"


# ---------- routes ----------

@router.post("/runs", response_model=IncidentRunResponse, status_code=201)
async def create_run(data: IncidentRunCreate, background_tasks: BackgroundTasks, db=Depends(get_db)):
    # Validate mutually exclusive input modes
    modes = [data.ticket is not None, data.ticket_id is not None, data.alert_event is not None]
    if sum(modes) != 1:
        raise HTTPException(status_code=422, detail="Exactly one of ticket, ticket_id, or alert_event must be provided")

    from app.services.intake import IntakeService
    intake = IntakeService(db)

    if data.ticket:
        ticket = intake.from_ticket_payload(data.ticket.model_dump())
        input_source = "ticket"
    elif data.ticket_id:
        ticket = intake.from_ticket_id(data.ticket_id)
        input_source = "ticket_id"
    else:
        ticket = intake.from_alert_event(data.alert_event.model_dump())
        input_source = "alert_event"

    initial_state: IncidentAgentState = {
        "ticket": ticket,
        "evidence_items": [],
        "root_cause_candidates": [],
        "step_count": 0,
        "action_results": [],
    }

    runtime = RuntimeService(db)
    run = runtime.create_run(initial_state, input_source=input_source)

    # Run graph in background
    background_tasks.add_task(_run_graph_bg, run.run_id, initial_state)

    return _run_to_response(run)


def _run_graph_bg(run_id: str, initial_state: IncidentAgentState, is_resume: bool = False):
    import asyncio
    db = SessionLocal()
    try:
        runtime = RuntimeService(db)
        run = runtime.get_run(run_id)
        asyncio.run(runtime.start_run(run, initial_state, is_resume=is_resume))
    except Exception:
        logger.exception(f"Background run {run_id} failed")
    finally:
        db.close()


@router.get("/runs/{run_id}", response_model=IncidentRunResponse)
async def get_run(run_id: str, db=Depends(get_db)):
    runs_repo = RunsRepo(db)
    run = runs_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_response(run)


@router.get("/runs", response_model=List[IncidentRunResponse])
async def list_runs(limit: int = 100, offset: int = 0, db=Depends(get_db)):
    runs_repo = RunsRepo(db)
    runs = runs_repo.list(limit=limit, offset=offset)
    return [_run_to_response(r) for r in runs]


@router.get("/runs/{run_id}/events", response_model=List[RunEventResponse])
async def get_run_events(
    run_id: str,
    last_event_id: Optional[str] = None,
    last_event_ts: Optional[str] = None,
    db=Depends(get_db),
):
    runtime = RuntimeService(db)
    ts = datetime.fromisoformat(last_event_ts) if last_event_ts else None
    events = runtime.get_events(run_id, last_event_id=last_event_id, last_event_ts=ts)
    return [_event_to_response(ev) for ev in events]


@router.get("/runs/{run_id}/trace", response_model=RunTraceResponse)
async def get_run_trace(run_id: str, db=Depends(get_db)):
    runs_repo = RunsRepo(db)
    run = runs_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    settings = get_settings()
    metadata = tracer.get_trace_metadata(run_id)
    provider = metadata.get("provider") or settings.tracing_provider
    external_trace_url = metadata.get("external_trace_url")
    return RunTraceResponse(
        run_id=run_id,
        provider=provider,
        trace_url=_build_trace_url(run_id, external_trace_url),
        external_trace_id=metadata.get("external_trace_id"),
        external_root_span_id=metadata.get("external_root_span_id"),
        external_trace_url=external_trace_url,
        spans=tracer.get_spans(run_id),
    )


def _format_sse_event(event: Dict[str, Any]) -> Dict[str, str]:
    return {"data": json.dumps(event, default=str)}


@router.get("/runs/{run_id}/stream")
async def stream_events(run_id: str, db=Depends(get_db)):
    runs_repo = RunsRepo(db)
    run = runs_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    from app.services.event_bus import event_bus

    async def generate():
        async for event in event_bus.iter_events(run_id):
            yield _format_sse_event(event)

    return EventSourceResponse(generate())


@router.get("/runs/{run_id}/evidence")
async def get_run_evidence(run_id: str, db=Depends(get_db)):
    evidence_repo = EvidenceRepo(db)
    items = evidence_repo.list_by_run(run_id)
    return [
        {
            "evidence_id": ev.evidence_id,
            "run_id": ev.run_id,
            "tool_name": ev.tool_name,
            "category": ev.category,
            "source_ref": ev.source_ref,
            "summary": ev.summary,
            "raw_payload": ev.raw_payload_json,
            "created_at": ev.created_at.isoformat() if ev.created_at else None,
        }
        for ev in items
    ]


@router.get("/runs/{run_id}/evidence/collection-results")
async def get_evidence_collection_results(run_id: str, db=Depends(get_db)):
    state = _load_latest_checkpoint_state(run_id, db)
    return {
        "run_id": run_id,
        "collection_results": state.get("evidence_collection_results", []),
        "evidence_quality_score": state.get("evidence_quality_score"),
        "missing_evidence_categories": state.get("missing_evidence_categories", []),
        "failed_evidence_tools": state.get("failed_evidence_tools", []),
    }


@router.get("/runs/{run_id}/actions")
async def get_run_actions(run_id: str, db=Depends(get_db)):
    actions_repo = ActionsRepo(db)
    # ActionsRepo doesn't have list_by_run yet, query directly
    from app.models.db_models import IncidentAction
    actions = db.query(IncidentAction).filter(IncidentAction.run_id == run_id).all()
    return [
        {
            "action_id": a.action_id,
            "run_id": a.run_id,
            "action_type": a.action_type,
            "execution_status": a.execution_status,
            "params": a.params_json,
            "result": a.result_json,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in actions
    ]


@router.get("/runs/{run_id}/diagnosis")
async def get_run_diagnosis(run_id: str, db=Depends(get_db)):
    state = _load_latest_checkpoint_state(run_id, db)
    candidates = state.get("root_cause_candidates", [])
    confidence = state.get("confidence")
    if confidence is None and candidates:
        first_candidate = candidates[0]
        if isinstance(first_candidate, dict):
            confidence = first_candidate.get("confidence")

    return {
        "run_id": run_id,
        "root_cause_candidates": candidates,
        "confidence": confidence,
    }


@router.get("/runs/{run_id}/remediation")
async def get_run_remediation(run_id: str, db=Depends(get_db)):
    state = _load_latest_checkpoint_state(run_id, db)
    return {
        "run_id": run_id,
        "remediation_plan": state.get("remediation_plan"),
    }


@router.get("/runs/{run_id}/rca")
async def get_rca(run_id: str, db=Depends(get_db)):
    runs_repo = RunsRepo(db)
    run = runs_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rca_repo = RcaRepo(db)
    rca = rca_repo.get(run_id)
    if not rca:
        return {"run_id": run_id, "rca": "Root cause analysis pending"}

    return {
        "run_id": rca.run_id,
        "report_markdown": rca.report_markdown,
        "root_cause": rca.root_cause,
        "root_cause_status": getattr(rca, "root_cause_status", None),
        "resolution": rca.resolution,
        "prevention_items": rca.prevention_items_json,
        "confirmed_by_human": bool(rca.confirmed_by_human),
        "timeline_summary": rca.timeline_summary,
        "impact_assessment": rca.impact_assessment,
        "supporting_evidence_ids": rca.supporting_evidence_ids_json,
        "executed_action_ids": rca.executed_action_ids_json,
        "candidate_hypotheses": getattr(rca, "candidate_hypotheses_json", None),
        "automation_outcome": getattr(rca, "automation_outcome_json", None),
        "manual_next_steps": getattr(rca, "manual_next_steps_json", None),
        "archive_ref": rca.archive_ref,
    }


@router.post("/runs/{run_id}/rca/confirm")
async def confirm_rca(run_id: str, background_tasks: BackgroundTasks, db=Depends(get_db)):
    """Confirm RCA report. Triggers knowledge writeback in background."""
    rca_repo = RcaRepo(db)
    rca = rca_repo.get(run_id)
    if not rca:
        raise HTTPException(status_code=404, detail="RCA not found for this run")

    rca_repo.confirm(run_id)

    # Trigger writeback in background
    background_tasks.add_task(_writeback_bg, run_id)

    return {"status": "confirmed", "run_id": run_id}


def _writeback_bg(run_id: str):
    """Trigger knowledge writeback + archive after RCA confirmation."""
    db = SessionLocal()
    try:
        from app.services.knowledge_writeback import KnowledgeWritebackService
        service = KnowledgeWritebackService(db)
        service.writeback(run_id, target="runbook")
        service.archive_rca(run_id)
    except Exception:
        logger.exception(f"Knowledge writeback/archive failed for run {run_id}")
    finally:
        db.close()


@router.post("/runs/{run_id}/resume")
async def resume_run(run_id: str, background_tasks: BackgroundTasks, db=Depends(get_db)):
    """Resume a run from its last checkpoint (e.g., after manual approval via this endpoint)."""
    from app.repositories import ApprovalsRepo
    from app.services.approval_runtime import ApprovalRuntime

    runs_repo = RunsRepo(db)
    run = runs_repo.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Find the latest pending/approved approval for this run to get approval_id
    approvals_repo = ApprovalsRepo(db)
    approvals = [a for a in approvals_repo.get_pending() if a.run_id == run_id]
    if not approvals:
        # Fallback: try to resume without an approval_id (e.g., after timeout recovery)
        approval_runtime = ApprovalRuntime(db)
        try:
            state, node_name = approval_runtime.get_resume_state(run_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        state["_resume_from_node"] = "node_executor"
        background_tasks.add_task(_run_graph_bg, run_id, state, True)
        return {"status": "resuming", "run_id": run_id, "from_node": "node_executor"}

    approval = approvals[0]
    approval_runtime = ApprovalRuntime(db)
    try:
        state, node_name = approval_runtime.prepare_resume_state(
            run_id=run_id,
            approval_id=approval.approval_id,
            decision="approved",
            approver="human",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    background_tasks.add_task(_run_graph_bg, run_id, state, True)
    return {"status": "resuming", "run_id": run_id, "from_node": "node_executor", "approval_id": approval.approval_id}
