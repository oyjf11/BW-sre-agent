"""EventBus: publish events to DB + SSE subscribers."""

import asyncio
from dataclasses import dataclass
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
    RUN_PAUSED = "RUN_PAUSED"
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


@dataclass
class Subscriber:
    queue: asyncio.Queue
    loop: asyncio.AbstractEventLoop


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, list[Subscriber]] = {}

    def _notify(self, run_id: str, event: Dict[str, Any]) -> None:
        for subscriber in list(self._subscribers.get(run_id, [])):
            subscriber.loop.call_soon_threadsafe(subscriber.queue.put_nowait, event)

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

        event_dict = {
            "event_id": event.event_id,
            "run_id": event.run_id,
            "timestamp": event.ts.isoformat(),
            "level": event.level,
            "type": event.type,
            "node_name": event.node_name,
            "message": event.message,
            "data": event.data_json,
        }
        self._notify(run_id, event_dict)

        return event

    def subscribe(self, run_id: str) -> Subscriber:
        subscriber = Subscriber(queue=asyncio.Queue(), loop=asyncio.get_running_loop())
        self._subscribers.setdefault(run_id, []).append(subscriber)
        return subscriber

    def unsubscribe(self, run_id: str, subscriber: Subscriber) -> None:
        subscribers = self._subscribers.get(run_id, [])
        if subscriber in subscribers:
            subscribers.remove(subscriber)
        if not subscribers and run_id in self._subscribers:
            del self._subscribers[run_id]

    async def iter_events(self, run_id: str) -> AsyncIterator[Dict[str, Any]]:
        subscriber = self.subscribe(run_id)
        try:
            while True:
                yield await subscriber.queue.get()
        finally:
            self.unsubscribe(run_id, subscriber)


# Singleton
event_bus = EventBus()
