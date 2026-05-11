from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
import json

from app.models.db_models import IncidentCheckpoint


class CheckpointService:
    def __init__(self, db: Session):
        self.db = db

    def save_checkpoint(
        self,
        run_id: str,
        node_name: str,
        state: Dict[str, Any],
    ) -> IncidentCheckpoint:
        checkpoint_id = f"cp_{uuid.uuid4().hex[:8]}"
        checkpoint = IncidentCheckpoint(
            checkpoint_id=checkpoint_id,
            run_id=run_id,
            node_name=node_name,
            state_json=state,
        )
        self.db.add(checkpoint)
        self.db.commit()
        self.db.refresh(checkpoint)
        return checkpoint

    def load_latest_checkpoint(
        self, run_id: str, node_name: Optional[str] = None
    ) -> Optional[IncidentCheckpoint]:
        query = self.db.query(IncidentCheckpoint).filter(
            IncidentCheckpoint.run_id == run_id
        )
        if node_name:
            query = query.filter(IncidentCheckpoint.node_name == node_name)
        return query.order_by(IncidentCheckpoint.created_at.desc()).first()

    def load_all_for_run(self, run_id: str) -> list[IncidentCheckpoint]:
        return (
            self.db.query(IncidentCheckpoint)
            .filter(IncidentCheckpoint.run_id == run_id)
            .order_by(IncidentCheckpoint.created_at)
            .all()
        )
