"""RuntimeService: unified run lifecycle management."""

import asyncio
import logging
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from sqlalchemy.orm import Session

from app.graph.state import IncidentAgentState, RunStatus
from app.models.db_models import IncidentRun, IncidentRunEvent, RunStatusEnum
from app.repositories.runs_repo import RunsRepo
from app.repositories.events_repo import EventsRepo
from app.repositories.evidence_repo import EvidenceRepo
from app.repositories.actions_repo import ActionsRepo
from app.services.event_bus import event_bus
from app.services.graph_runner import GraphRunner

logger = logging.getLogger(__name__)


class RuntimeService:
    def __init__(self, db: Session):
        self.db = db
        self.runs_repo = RunsRepo(db)
        self.events_repo = EventsRepo(db)
        self.evidence_repo = EvidenceRepo(db)
        self.actions_repo = ActionsRepo(db)

    def create_run(
        self,
        initial_state: IncidentAgentState,
        started_by: Optional[str] = None,
        input_source: Optional[str] = None,
    ) -> IncidentRun:
        ticket = initial_state.get("ticket")
        kwargs = {}
        if ticket:
            kwargs["ticket_id"] = getattr(ticket, "ticket_id", None) or (ticket.get("ticket_id") if isinstance(ticket, dict) else None)
            kwargs["severity"] = getattr(ticket, "severity", None) or (ticket.get("severity") if isinstance(ticket, dict) else None)
            kwargs["service"] = getattr(ticket, "service", None) or (ticket.get("service") if isinstance(ticket, dict) else None)
            kwargs["env"] = getattr(ticket, "env", None) or (ticket.get("env") if isinstance(ticket, dict) else None)
            title = getattr(ticket, "title", None) or (ticket.get("title") if isinstance(ticket, dict) else None) or ""
            description = getattr(ticket, "description", None) or (ticket.get("description") if isinstance(ticket, dict) else None) or ""
            kwargs["summary_json"] = {"title": title, "description": description}
        if input_source:
            kwargs["input_source"] = input_source

        thread_id = initial_state.get("thread_id", f"thread-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
        run = self.runs_repo.create(thread_id=thread_id, started_by=started_by, **kwargs)

        # Set run_id + thread_id in state
        initial_state["run_id"] = run.run_id
        initial_state["thread_id"] = run.thread_id

        return run

    async def start_run(
        self,
        run: IncidentRun,
        initial_state: IncidentAgentState,
        is_resume: bool = False,
    ) -> IncidentAgentState:
        runner = GraphRunner(self.db)
        return await runner.run(run.run_id, initial_state, is_resume=is_resume)

    def start_run_background(
        self,
        run: IncidentRun,
        initial_state: IncidentAgentState,
        is_resume: bool = False,
    ) -> asyncio.Task:
        async def _run():
            try:
                await self.start_run(run, initial_state, is_resume=is_resume)
            except Exception:
                logger.exception(f"Background run {run.run_id} failed")

        return asyncio.ensure_future(_run())

    def get_run(self, run_id: str) -> Optional[IncidentRun]:
        return self.runs_repo.get(run_id)

    def list_runs(self, limit: int = 100, offset: int = 0) -> List[IncidentRun]:
        return self.runs_repo.list(limit=limit, offset=offset)

    def get_events(
        self,
        run_id: str,
        last_event_id: Optional[str] = None,
        last_event_ts: Optional[datetime] = None,
    ) -> List[IncidentRunEvent]:
        if last_event_id or last_event_ts:
            return self.events_repo.list_incremental(run_id, last_event_id=last_event_id, last_event_ts=last_event_ts)
        return self.events_repo.list_by_run(run_id)

    async def subscribe_events(self, run_id: str) -> AsyncIterator[Dict[str, Any]]:
        async for event in event_bus.iter_events(run_id):
            yield event

    def get_evidence(self, run_id: str):
        return self.evidence_repo.list_by_run(run_id)
