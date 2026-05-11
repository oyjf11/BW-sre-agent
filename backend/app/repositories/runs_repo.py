from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.db_models import IncidentRun, RunStatusEnum


class RunsRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, thread_id: str, started_by: Optional[str] = None, **kwargs) -> IncidentRun:
        run_id = str(uuid.uuid4())
        run = IncidentRun(
            run_id=run_id,
            thread_id=thread_id,
            status=RunStatusEnum.NEW,
            started_by=started_by,
            **kwargs,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update(self, run_id: str, **kwargs) -> Optional[IncidentRun]:
        run = self.db.query(IncidentRun).filter(IncidentRun.run_id == run_id).first()
        if not run:
            return None
        for key, value in kwargs.items():
            if hasattr(run, key):
                setattr(run, key, value)
        run.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(run)
        return run

    def get(self, run_id: str) -> Optional[IncidentRun]:
        return self.db.query(IncidentRun).filter(IncidentRun.run_id == run_id).first()

    def list(self, limit: int = 100, offset: int = 0) -> List[IncidentRun]:
        return (
            self.db.query(IncidentRun)
            .order_by(IncidentRun.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
