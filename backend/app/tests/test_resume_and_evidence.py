from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.graph.context import get_node_event_hook
from app.api import approvals as approvals_api
from app.api import incidents as incidents_api
from app.graph.nodes import risk_gate_node
from app.graph.state import RunStatus
from app.models.action import ActionSpec
from app.models.db_models import Base, IncidentCheckpoint, IncidentRun, RunStatusEnum
from app.models.remediation import RemediationPlan
from app.repositories.evidence_repo import EvidenceRepo
from app.repositories.runs_repo import RunsRepo
from app.repositories.rca_repo import RcaRepo
from app.services.approval_runtime import ApprovalRuntime
from app.services.event_bus import EventType
from app.services.graph_runner import GraphRunner


def create_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_risk_gate_requires_approval_for_prod_action_even_when_low_risk():
    state = {
        "ticket": {"env": "prod", "severity": "P2"},
        "remediation_plan": RemediationPlan(
            summary="restart service",
            actions=[
                ActionSpec(
                    action_type="restart",
                    service="mysql",
                    env="prod",
                    params={},
                    risk_level="LOW",
                    requires_approval=False,
                )
            ],
            expected_outcome="recover",
            rollback_plan="none",
        ),
        "user_context": {"requires_immediate_human": True},
        "root_cause_candidates": [{"confidence": 0.9}],
        "step_count": 0,
    }

    result = risk_gate_node(state)

    assert result["risk_decision"] == "NEEDS_APPROVAL"


def test_approval_runtime_emits_single_resume_event(monkeypatch):
    session_factory = create_session_factory()
    db = session_factory()
    try:
        run = IncidentRun(
            run_id="run-approval",
            thread_id="thread-approval",
            status=RunStatusEnum.WAITING_HUMAN,
            service="mysql",
            env="prod",
            severity="P2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        checkpoint = IncidentCheckpoint(
            checkpoint_id="cp-risk",
            run_id="run-approval",
            node_name="node_risk_gate",
            state_json={"risk_decision": "NEEDS_APPROVAL", "evidence_items": []},
            created_at=datetime.utcnow(),
        )
        db.add(run)
        db.add(checkpoint)
        db.commit()

        published = []

        def fake_publish(**kwargs):
            published.append(kwargs)

        monkeypatch.setattr("app.services.approval_runtime.event_bus.publish", fake_publish)

        runtime = ApprovalRuntime(db)
        state, node_name = runtime.prepare_resume_state(
            run_id="run-approval",
            approval_id="apr-1",
            decision="approved",
        )

        assert node_name == "node_risk_gate"
        assert state["_resume_from_node"] == "node_executor"
        assert len(published) == 1
        assert published[0]["event_type"] == EventType.RUN_RESUMED
    finally:
        db.close()


def test_incidents_run_graph_bg_marks_resume(monkeypatch):
    calls = []

    class DummyDb:
        def close(self):
            return None

    class FakeRuntimeService:
        def __init__(self, db):
            self.db = db

        def get_run(self, run_id):
            return {"run_id": run_id}

        async def start_run(self, run, initial_state, is_resume=False):
            calls.append(
                {"run": run, "initial_state": initial_state, "is_resume": is_resume}
            )

    monkeypatch.setattr(incidents_api, "SessionLocal", lambda: DummyDb())
    monkeypatch.setattr(incidents_api, "RuntimeService", FakeRuntimeService)

    incidents_api._run_graph_bg("run-1", {"foo": "bar"}, True)

    assert calls == [
        {"run": {"run_id": "run-1"}, "initial_state": {"foo": "bar"}, "is_resume": True}
    ]


def test_approvals_resume_bg_marks_resume(monkeypatch):
    calls = []

    class DummyDb:
        def close(self):
            return None

    class FakeRuntimeService:
        def __init__(self, db):
            self.db = db

        def get_run(self, run_id):
            return {"run_id": run_id}

        async def start_run(self, run, initial_state, is_resume=False):
            calls.append(
                {"run": run, "initial_state": initial_state, "is_resume": is_resume}
            )

    class FakeApprovalRuntime:
        def __init__(self, db):
            self.db = db

        def prepare_resume_state(self, **kwargs):
            return {"run_id": kwargs["run_id"]}, "node_risk_gate"

    monkeypatch.setattr(approvals_api, "SessionLocal", lambda: DummyDb())
    monkeypatch.setattr("app.services.runtime.RuntimeService", FakeRuntimeService)
    monkeypatch.setattr(approvals_api, "ApprovalRuntime", FakeApprovalRuntime)

    approvals_api._resume_run_bg("run-2", "apr-2", "approved")

    assert calls == [
        {"run": {"run_id": "run-2"}, "initial_state": {"run_id": "run-2"}, "is_resume": True}
    ]


def test_graph_runner_resume_dedupes_existing_evidence_and_preserves_ids():
    session_factory = create_session_factory()
    db = session_factory()
    try:
        run = IncidentRun(
            run_id="run-evidence",
            thread_id="thread-evidence",
            status=RunStatusEnum.EXECUTING,
            service="mysql",
            env="prod",
            severity="P2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(run)
        db.commit()

        repo = EvidenceRepo(db)
        repo.insert(
            run_id="run-evidence",
            tool_name="query_logs",
            category="logs",
            source_ref="logs-run-evidence",
            summary="existing",
            raw_payload={"ok": True},
            evidence_id="ev-existing",
        )

        runner = GraphRunner(db)
        resumed_state = {
            "evidence_items": [
                {
                    "evidence_id": "ev-existing",
                    "tool_name": "query_logs",
                    "category": "logs",
                    "source_ref": "logs-run-evidence",
                    "summary": "existing",
                    "raw_payload": {"ok": True},
                }
            ]
        }
        runner._initialize_persisted_evidence_ids(resumed_state)
        runner._persist_evidence("run-evidence", resumed_state)

        items = repo.list_by_run("run-evidence")
        assert len(items) == 1
        assert items[0].evidence_id == "ev-existing"

        resumed_state["evidence_items"].append(
            {
                "evidence_id": "ev-new",
                "tool_name": "query_metrics",
                "category": "metrics",
                "source_ref": "metrics-run-evidence",
                "summary": "new",
                "raw_payload": {"value": 1},
            }
        )
        runner._persist_evidence("run-evidence", resumed_state)

        items = repo.list_by_run("run-evidence")
        evidence_ids = [item.evidence_id for item in items]
        assert evidence_ids == ["ev-existing", "ev-new"]

        runner._persist_rca(
            "run-evidence",
            {
                "rca_report": {
                    "report_markdown": "report",
                    "root_cause": "cause",
                    "resolution": "fix",
                    "prevention_items": ["p1"],
                    "supporting_evidence_ids": ["ev-existing", "ev-new"],
                    "executed_action_ids": ["act-1"],
                }
            },
        )

        rca = RcaRepo(db).get("run-evidence")
        assert rca.supporting_evidence_ids_json == ["ev-existing", "ev-new"]
    finally:
        db.close()


@pytest.mark.asyncio
async def test_graph_runner_persists_intermediate_status_and_current_node(monkeypatch):
    session_factory = create_session_factory()
    db = session_factory()
    try:
        run = IncidentRun(
            run_id="run-status-sync",
            thread_id="thread-status-sync",
            status=RunStatusEnum.NEW,
            service="payment-service",
            env="staging",
            severity="P2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(run)
        db.commit()

        observed = {}

        class FakeGraph:
            async def astream(self, initial_state, config=None):
                hook = get_node_event_hook()
                assert hook is not None

                hook(
                    EventType.NODE_STARTED,
                    "node_triage",
                    message="Node node_triage started",
                    level="INFO",
                )
                observed["current_node_after_start"] = RunsRepo(db).get("run-status-sync").current_node

                yield {
                    "node_triage": {
                        "status": RunStatus.TRIAGED,
                        "step_count": 1,
                        "evidence_items": [],
                    }
                }

                after_triage = RunsRepo(db).get("run-status-sync")
                observed["status_after_first_node"] = after_triage.status
                observed["step_after_first_node"] = after_triage.step_count

        monkeypatch.setattr("app.services.graph_runner.create_incident_graph", lambda: FakeGraph())

        runner = GraphRunner(db)
        final_state = await runner.run(
            "run-status-sync",
            {
                "run_id": "run-status-sync",
                "thread_id": "thread-status-sync",
                "evidence_items": [],
                "step_count": 0,
            },
        )

        run_after = RunsRepo(db).get("run-status-sync")
        assert observed["current_node_after_start"] == "node_triage"
        assert observed["status_after_first_node"] == RunStatusEnum.TRIAGED
        assert observed["step_after_first_node"] == 1
        assert final_state["status"] == RunStatus.TRIAGED
        assert run_after.status == RunStatusEnum.TRIAGED
        assert run_after.current_node is None
    finally:
        db.close()


@pytest.mark.asyncio
async def test_graph_runner_resume_syncs_status_before_next_node(monkeypatch):
    session_factory = create_session_factory()
    db = session_factory()
    try:
        run = IncidentRun(
            run_id="run-resume-status",
            thread_id="thread-resume-status",
            status=RunStatusEnum.WAITING_HUMAN,
            service="payment-service",
            env="prod",
            severity="P1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(run)
        db.commit()

        observed = {}

        class FakeGraph:
            async def astream(self, initial_state, config=None):
                current = RunsRepo(db).get("run-resume-status")
                observed["status_before_first_node"] = current.status
                observed["completed_at_before_first_node"] = current.completed_at
                yield {
                    "node_executor": {
                        "status": RunStatus.EXECUTING,
                        "step_count": 3,
                        "evidence_items": [],
                    }
                }

        monkeypatch.setattr("app.services.graph_runner.create_incident_graph", lambda: FakeGraph())

        runner = GraphRunner(db)
        await runner.run(
            "run-resume-status",
            {
                "run_id": "run-resume-status",
                "thread_id": "thread-resume-status",
                "status": RunStatus.EXECUTING,
                "evidence_items": [],
                "step_count": 2,
            },
            is_resume=True,
        )

        assert observed["status_before_first_node"] == RunStatusEnum.EXECUTING
        assert observed["completed_at_before_first_node"] is None
    finally:
        db.close()
