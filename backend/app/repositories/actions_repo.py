from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.models.db_models import IncidentAction


class ActionsRepo:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        run_id: str,
        action_type: str,
        params: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        approval_id: Optional[str] = None,
        executor_name: Optional[str] = None,
        request_json: Optional[Dict[str, Any]] = None,
    ) -> IncidentAction:
        action_id = f"act_{uuid.uuid4().hex[:8]}"
        action = IncidentAction(
            action_id=action_id,
            run_id=run_id,
            idempotency_key=idempotency_key,
            action_type=action_type,
            params_json=params,
            execution_status="PENDING",
            approval_id=approval_id,
            executor_name=executor_name,
            request_json=request_json,
        )
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def get(self, action_id: str) -> Optional[IncidentAction]:
        return (
            self.db.query(IncidentAction)
            .filter(IncidentAction.action_id == action_id)
            .first()
        )

    def get_by_idempotency(self, idempotency_key: str) -> Optional[IncidentAction]:
        return (
            self.db.query(IncidentAction)
            .filter(IncidentAction.idempotency_key == idempotency_key)
            .first()
        )

    def list_by_run(self, run_id: str) -> List[IncidentAction]:
        return (
            self.db.query(IncidentAction)
            .filter(IncidentAction.run_id == run_id)
            .order_by(IncidentAction.created_at)
            .all()
        )

    def update_status(
        self,
        action_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> Optional[IncidentAction]:
        action = self.get(action_id)
        if not action:
            return None
        action.execution_status = status
        if result:
            action.result_json = result
        self.db.commit()
        self.db.refresh(action)
        return action

    def mark_started(self, action_id: str, attempt_no: int = 1) -> Optional[IncidentAction]:
        action = self.get(action_id)
        if not action:
            return None
        action.execution_status = "EXECUTING"
        action.attempt_no = attempt_no
        action.started_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(action)
        return action

    def mark_completed(
        self,
        action_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        verification_status: Optional[str] = None,
        verification_details: Optional[Dict[str, Any]] = None,
    ) -> Optional[IncidentAction]:
        action = self.get(action_id)
        if not action:
            return None
        action.execution_status = status
        action.completed_at = datetime.utcnow()
        if result is not None:
            action.result_json = result
        if verification_status is not None:
            action.verification_status = verification_status
        if verification_details is not None:
            action.verification_details_json = verification_details
        self.db.commit()
        self.db.refresh(action)
        return action
