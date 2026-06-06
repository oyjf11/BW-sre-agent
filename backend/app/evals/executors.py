"""Graph execution strategies for offline eval."""
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from app.graph.builder import create_incident_graph


@runtime_checkable
class GraphExecutor(Protocol):
    mode: str

    async def execute(self, case_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        ...


class DirectGraphExecutor:
    """Run the compiled graph directly without DB persistence or event writes."""

    mode = "direct"

    def __init__(self, checkpointer: Optional[Any] = None):
        self._checkpointer = checkpointer

    async def execute(self, case_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        graph = create_incident_graph(checkpointer=self._checkpointer)
        config = {
            "recursion_limit": 50,
            "configurable": {"thread_id": f"eval-{case_id}"},
        }
        return await graph.ainvoke(initial_state, config=config)


class RunnerGraphExecutor:
    """Run through GraphRunner for production-chain smoke checks."""

    mode = "runner"

    async def execute(self, case_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        from app.repositories import SessionLocal
        from app.services.graph_runner import GraphRunner

        run_id = f"eval-{case_id}"
        db = SessionLocal()
        try:
            self._ensure_run_row(db, run_id)
            runner = GraphRunner(db)
            state = {**initial_state, "run_id": run_id, "thread_id": run_id}
            return await runner.run(run_id=run_id, initial_state=state)
        finally:
            db.close()

    @staticmethod
    def _ensure_run_row(db, run_id: str) -> None:
        from app.models.db_models import IncidentRun, RunStatusEnum

        existing = db.query(IncidentRun).filter(IncidentRun.run_id == run_id).first()
        if existing:
            return

        db.add(IncidentRun(run_id=run_id, thread_id=run_id, status=RunStatusEnum.NEW))
        db.commit()
