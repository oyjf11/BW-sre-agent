from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.incidents import router, get_db
from app.models.db_models import Base, IncidentCheckpoint, IncidentRun, RunStatusEnum
from app.tracing import tracer
from app.tracing_providers import LocalTraceProvider, ProviderSpanResult


def create_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return app, TestingSessionLocal


def seed_run_with_checkpoint(session_factory):
    db = session_factory()
    try:
        run = IncidentRun(
            run_id="run-123",
            thread_id="thread-123",
            status=RunStatusEnum.DIAGNOSED,
            service="payment-service",
            env="staging",
            severity="P2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        checkpoint = IncidentCheckpoint(
            checkpoint_id="cp-123",
            run_id="run-123",
            node_name="node_remediation",
            state_json={
                "root_cause_candidates": [
                    {
                        "candidate_id": "cand-1",
                        "hypothesis": "Recent deployment caused 5xx increase",
                        "confidence": 0.82,
                        "supporting_evidence_ids": ["ev-1"],
                        "contradicting_evidence_ids": [],
                        "next_checks": ["compare error rate before and after rollout"],
                    }
                ],
                "remediation_plan": {
                    "summary": "Rollback the latest deployment",
                    "actions": [
                        {
                            "action_type": "rollback",
                            "service": "payment-service",
                            "env": "staging",
                            "params": {"version": "previous"},
                            "risk_level": "HIGH",
                            "requires_approval": True,
                        }
                    ],
                    "expected_outcome": "Error rate should return to baseline",
                    "rollback_plan": "Redeploy current version if rollback fails",
                },
            },
            created_at=datetime.utcnow(),
        )
        db.add(run)
        db.add(checkpoint)
        db.commit()
    finally:
        db.close()


def test_get_run_diagnosis_returns_checkpoint_state():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/diagnosis")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == "run-123"
    assert payload["confidence"] == 0.82
    assert payload["root_cause_candidates"][0]["hypothesis"] == "Recent deployment caused 5xx increase"


def test_get_run_remediation_returns_checkpoint_state():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/remediation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == "run-123"
    assert payload["remediation_plan"]["summary"] == "Rollback the latest deployment"
    assert payload["remediation_plan"]["actions"][0]["action_type"] == "rollback"


def test_get_run_diagnosis_returns_404_without_checkpoint():
    app, _session_factory = create_test_client()

    with TestClient(app) as client:
        response = client.get("/incidents/runs/missing-run/diagnosis")

    assert response.status_code == 404
    assert response.json()["detail"] == "No checkpoint found"


def test_get_run_trace_returns_spans_and_local_url():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)
    tracer.clear()
    span_id = tracer.start_span("graph.run", run_id="run-123")
    tracer.add_event(span_id, "node_started", {"node_name": "node_intake"})
    tracer.end_span(span_id)

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/trace")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == "run-123"
    assert payload["provider"] == "local"
    assert payload["trace_url"].endswith("/incidents/runs/run-123/trace")
    assert payload["spans"][0]["name"] == "graph.run"
    tracer.configure_provider(LocalTraceProvider())


class ApiTraceProvider:
    name = "recording"

    def start_span(self, span):
        return ProviderSpanResult(
            external_trace_id="external-trace-run-123",
            external_span_id="external-root-span",
            external_trace_url="https://trace.example/run-123",
        )

    def add_event(self, span_id, event_name, data):
        return None

    def end_span(self, span):
        return None

    def get_trace_url(self, run_id):
        return f"https://trace.example/{run_id}"

    def flush(self):
        return None


def test_get_run_trace_returns_external_trace_metadata():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)
    tracer.clear()
    tracer.configure_provider(ApiTraceProvider())
    span_id = tracer.start_span("graph.run", run_id="run-123")
    tracer.end_span(span_id)

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/trace")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "recording"
    assert payload["trace_url"] == "https://trace.example/run-123"
    assert payload["external_trace_id"] == "external-trace-run-123"
    assert payload["external_root_span_id"] == "external-root-span"
    assert payload["external_trace_url"] == "https://trace.example/run-123"
    tracer.configure_provider(LocalTraceProvider())
