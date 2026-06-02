from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories import SessionLocal, ApprovalsRepo
from app.services.approval_runtime import ApprovalRuntime

router = APIRouter(prefix="/approvals", tags=["approvals"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ApprovalAction(BaseModel):
    action_type: str
    service: str
    env: str
    params: Dict[str, Any] = {}
    risk_level: str
    requires_approval: bool = False


class ApprovalCreate(BaseModel):
    run_id: str
    action: ApprovalAction
    reason: str
    risk_level: str
    evidence_refs: List[str] = []
    expected_impact: str
    rollback_plan: Optional[str] = None


class ApprovalResponse(BaseModel):
    approval_id: str
    run_id: str
    ticket_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    action: Dict[str, Any]
    risk_level: str
    status: str
    reason: Optional[str] = None
    expected_impact: Optional[str] = None
    rollback_plan: Optional[str] = None
    approver: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ApprovalDecision(BaseModel):
    decision: str  # approved / rejected / modify / more_evidence
    comment: Optional[str] = None
    # For 'modify': human-corrected remediation plan fields
    modified_plan: Optional[Dict[str, Any]] = None
    # For 'more_evidence': additional investigation scope
    additional_categories: Optional[List[str]] = None
    additional_context: Optional[str] = None


def _to_response(a) -> ApprovalResponse:
    ticket_id = None
    title = None
    description = None
    run = a.run
    if run:
        ticket_id = run.ticket_id
        summary = run.summary_json or {}
        if isinstance(summary, dict):
            title = summary.get("title")
            description = summary.get("description")

    return ApprovalResponse(
        approval_id=a.approval_id,
        run_id=a.run_id,
        ticket_id=ticket_id,
        title=title,
        description=description,
        action=a.action_json,
        risk_level=a.risk_level,
        status=a.status,
        reason=a.reason,
        expected_impact=a.expected_impact,
        rollback_plan=a.rollback_plan,
        approver=a.approver,
        comment=a.comment,
        created_at=a.created_at or datetime.utcnow(),
        updated_at=a.updated_at or a.created_at,
    )


@router.get("/pending", response_model=List[ApprovalResponse])
async def list_pending(db=Depends(get_db)):
    approvals_repo = ApprovalsRepo(db)
    return [_to_response(a) for a in approvals_repo.get_pending()]


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: str, db=Depends(get_db)):
    approvals_repo = ApprovalsRepo(db)
    approval = approvals_repo.get(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return _to_response(approval)


@router.post("/{approval_id}/decision")
async def submit_decision(
    approval_id: str,
    decision: ApprovalDecision,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
):
    approval_runtime = ApprovalRuntime(db)
    approvals_repo = ApprovalsRepo(db)

    approval = approvals_repo.get(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if decision.decision not in ("approved", "rejected", "modify", "more_evidence"):
        raise HTTPException(
            status_code=422,
            detail="Invalid decision. Must be: approved, rejected, modify, more_evidence",
        )

    approval_runtime.handle_decision(
        approval_id=approval_id,
        decision=decision.decision,
        comment=decision.comment,
    )

    # For approved / modify / more_evidence, trigger resume in background
    if decision.decision in ("approved", "modify", "more_evidence"):
        background_tasks.add_task(
            _resume_run_bg,
            approval.run_id,
            approval_id,
            decision.decision,
            decision.comment,
            decision.modified_plan,
            decision.additional_categories,
            decision.additional_context,
        )

    return {
        "status": "success",
        "message": f"Decision '{decision.decision}' recorded for approval {approval_id}",
    }


def _resume_run_bg(
    run_id: str,
    approval_id: str,
    decision: str,
    comment: Optional[str] = None,
    modified_plan: Optional[Dict[str, Any]] = None,
    additional_categories: Optional[List[str]] = None,
    additional_context: Optional[str] = None,
):
    """Resume a run after an approval decision in background."""
    import asyncio
    import logging

    logger = logging.getLogger(__name__)

    db = SessionLocal()
    try:
        from app.services.runtime import RuntimeService

        runtime = RuntimeService(db)
        run = runtime.get_run(run_id)
        if not run:
            logger.error(f"Cannot resume: run {run_id} not found")
            return

        approval_runtime = ApprovalRuntime(db)
        state, _node = approval_runtime.prepare_resume_state(
            run_id=run_id,
            approval_id=approval_id,
            decision=decision,
            approver="human",
            comment=comment,
            decision_data={
                "modified_plan": modified_plan,
                "additional_categories": additional_categories,
                "additional_context": additional_context,
            },
        )

        asyncio.run(runtime.start_run(run, state, is_resume=True))
    except Exception:
        logger.exception(f"Failed to resume run {run_id}")
    finally:
        db.close()
