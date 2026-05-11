from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.db_models import IncidentApproval


class ApprovalsRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        run_id: str,
        action: Dict[str, Any],
        risk_level: str,
        approval_id: Optional[str] = None,
        reason: Optional[str] = None,
        expected_impact: Optional[str] = None,
        rollback_plan: Optional[str] = None,
    ) -> IncidentApproval:
        if not approval_id:
            approval_id = f"apr_{uuid.uuid4().hex[:8]}"
        approval = IncidentApproval(
            approval_id=approval_id,
            run_id=run_id,
            action_json=action,
            risk_level=risk_level,
            status="PENDING",
            reason=reason,
            expected_impact=expected_impact,
            rollback_plan=rollback_plan,
        )
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def update(
        self,
        approval_id: str,
        status: Optional[str] = None,
        approver: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Optional[IncidentApproval]:
        approval = (
            self.db.query(IncidentApproval)
            .filter(IncidentApproval.approval_id == approval_id)
            .first()
        )
        if not approval:
            return None
        if status:
            approval.status = status
        if approver:
            approval.approver = approver
        if comment:
            approval.comment = comment
        approval.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(approval)
        return approval

    def get_pending(self) -> List[IncidentApproval]:
        return (
            self.db.query(IncidentApproval)
            .filter(IncidentApproval.status == "PENDING")
            .order_by(IncidentApproval.created_at)
            .all()
        )

    def get(self, approval_id: str) -> Optional[IncidentApproval]:
        return (
            self.db.query(IncidentApproval)
            .filter(IncidentApproval.approval_id == approval_id)
            .first()
        )
