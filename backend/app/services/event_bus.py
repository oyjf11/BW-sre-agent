"""EventBus: publish events to DB + SSE subscribers."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Dict, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.db_models import IncidentRunEvent


class EventType(str, Enum):
    # Run lifecycle
    RUN_CREATED = "RUN_CREATED"
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"
    RUN_RESUMED = "RUN_RESUMED"

    # Node lifecycle
    NODE_STARTED = "NODE_STARTED"
    NODE_COMPLETED = "NODE_COMPLETED"
    NODE_FAILED = "NODE_FAILED"
    NODE_SKIPPED = "NODE_SKIPPED"

    # Checkpoint
    CHECKPOINT_SAVED = "CHECKPOINT_SAVED"
    CHECKPOINT_RESTORED = "CHECKPOINT_RESTORED"

    # Evidence
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    EVIDENCE_FAILED = "EVIDENCE_FAILED"
    EVIDENCE_AGGREGATED = "EVIDENCE_AGGREGATED"

    # Diagnosis
    DIAGNOSIS_COMPLETED = "DIAGNOSIS_COMPLETED"
    CRITIC_DECISION = "CRITIC_DECISION"

    # Risk & Approval
    RISK_ASSESSED = "RISK_ASSESSED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVAL_DECIDED = "APPROVAL_DECIDED"

    # Execution
    ACTION_STARTED = "ACTION_STARTED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    ACTION_FAILED = "ACTION_FAILED"
    VERIFY_COMPLETED = "VERIFY_COMPLETED"

    # RCA
    RCA_GENERATED = "RCA_GENERATED"
    RCA_CONFIRMED = "RCA_CONFIRMED"


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, list[asyncio.Queue]] = {}

    def publish(
        self,
        db: Session,
        run_id: str,
        event_type: EventType,
        node_name: Optional[str] = None,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
    ) -> IncidentRunEvent:
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        event = IncidentRunEvent(
            event_id=event_id,
            run_id=run_id,
            ts=datetime.utcnow(),
            level=level,
            type=event_type.value,
            node_name=node_name,
            message=message,
            data_json=data,
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # Notify SSE subscribers
        event_dict = {
            "event_id": event.event_id,
            "run_id": event.run_id,
            "ts": event.ts.isoformat(),
            "level": event.level,
            "type": event.type,
            "node_name": event.node_name,
            "message": event.message,
            "data": event.data_json,
        }
        for queue in self._subscribers.get(run_id, []):
            queue.put_nowait(event_dict)

        return event

    def subscribe(self, run_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(run_id, []).append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue) -> None:
        queues = self._subscribers.get(run_id, [])
        if queue in queues:
            queues.remove(queue)
        if not queues and run_id in self._subscribers:
            del self._subscribers[run_id]

    async def iter_events(self, run_id: str) -> AsyncIterator[Dict[str, Any]]:
        queue = self.subscribe(run_id)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self.unsubscribe(run_id, queue)


# Singleton
event_bus = EventBus()
