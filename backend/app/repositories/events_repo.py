from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.db_models import IncidentRunEvent


class EventsRepo:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        run_id: str,
        event_type: str,
        node_name: Optional[str] = None,
        message: Optional[str] = None,
        data: Optional[dict] = None,
        level: str = "INFO",
    ) -> IncidentRunEvent:
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        event = IncidentRunEvent(
            event_id=event_id,
            run_id=run_id,
            ts=datetime.utcnow(),
            level=level,
            type=event_type,
            node_name=node_name,
            message=message,
            data_json=data,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_by_run(self, run_id: str) -> List[IncidentRunEvent]:
        return (
            self.db.query(IncidentRunEvent)
            .filter(IncidentRunEvent.run_id == run_id)
            .order_by(IncidentRunEvent.ts)
            .all()
        )

    def list_incremental(
        self,
        run_id: str,
        last_event_id: Optional[str] = None,
        last_event_ts: Optional[datetime] = None,
    ) -> List[IncidentRunEvent]:
        query = self.db.query(IncidentRunEvent).filter(IncidentRunEvent.run_id == run_id)

        if last_event_id:
            ref = self.db.query(IncidentRunEvent).filter(IncidentRunEvent.event_id == last_event_id).first()
            if ref:
                query = query.filter(IncidentRunEvent.ts > ref.ts)
        elif last_event_ts:
            query = query.filter(IncidentRunEvent.ts > last_event_ts)

        return query.order_by(IncidentRunEvent.ts).all()
