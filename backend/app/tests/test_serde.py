from datetime import datetime
from app.graph.serde import serialize_state, deserialize_state
from app.graph.state import IncidentAgentState, RunStatus
from app.models.incident import IncidentTicket
from app.models.triage import TriageResult
from app.models.evidence import EvidenceItem
from app.models.root_cause import RootCauseCandidate


class TestSerde:
    def _make_state(self) -> IncidentAgentState:
        return IncidentAgentState(
            run_id="run-001",
            thread_id="thread-001",
            ticket=IncidentTicket(
                ticket_id="T-1",
                title="CPU spike",
                description="CPU > 90%",
                service="order-svc",
                env="prod",
                severity="P1",
                source="alertmanager",
                time_range={"start": datetime(2026, 3, 28, 10, 0), "end": datetime(2026, 3, 28, 11, 0)},
            ),
            triage=TriageResult(
                incident_type="resource_exhaustion",
                severity="P1",
                suspected_services=["order-svc"],
                requires_immediate_human=False,
                rationale="High CPU",
            ),
            evidence_items=[
                EvidenceItem(
                    evidence_id="ev-1",
                    tool_name="query_metrics",
                    category="metrics",
                    source_ref="prometheus:cpu",
                    summary="CPU at 95%",
                ),
            ],
            root_cause_candidates=[
                RootCauseCandidate(
                    candidate_id="rc-1",
                    hypothesis="Memory leak",
                    confidence=0.8,
                    supporting_evidence_ids=["ev-1"],
                ),
            ],
            status=RunStatus.DIAGNOSED,
            step_count=5,
            error=None,
            action_results=[{"action": "restart", "ok": True}],
        )

    def test_roundtrip(self):
        state = self._make_state()
        serialized = serialize_state(state)

        # Verify it's JSON-safe (no Pydantic models or Enums)
        assert isinstance(serialized["ticket"], dict)
        assert isinstance(serialized["status"], str)
        assert serialized["status"] == "DIAGNOSED"
        assert isinstance(serialized["evidence_items"][0], dict)

        deserialized = deserialize_state(serialized)

        assert deserialized["run_id"] == "run-001"
        assert deserialized["status"] == RunStatus.DIAGNOSED
        assert deserialized["ticket"].service == "order-svc"
        assert deserialized["ticket"].time_range["start"] == datetime(2026, 3, 28, 10, 0)
        assert len(deserialized["evidence_items"]) == 1
        assert deserialized["evidence_items"][0].category == "metrics"
        assert deserialized["root_cause_candidates"][0].confidence == 0.8
        assert deserialized["action_results"] == [{"action": "restart", "ok": True}]

    def test_empty_state_roundtrip(self):
        state = IncidentAgentState(run_id="run-empty", thread_id="t-1", status=RunStatus.NEW, step_count=0)
        deserialized = deserialize_state(serialize_state(state))
        assert deserialized["run_id"] == "run-empty"
        assert deserialized["status"] == RunStatus.NEW
