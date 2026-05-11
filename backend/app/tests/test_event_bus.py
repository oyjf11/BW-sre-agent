import asyncio
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db_models import Base, IncidentRun, IncidentRunEvent, RunStatusEnum
from app.services.event_bus import EventBus, EventType


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Create a run for FK
    session.add(IncidentRun(run_id="run-1", thread_id="t-1", status=RunStatusEnum.NEW))
    session.commit()
    yield session
    session.close()


class TestEventBus:
    def test_publish_persists_to_db(self, db_session):
        bus = EventBus()
        event = bus.publish(
            db=db_session,
            run_id="run-1",
            event_type=EventType.NODE_STARTED,
            node_name="intake",
            message="Starting intake",
            data={"key": "value"},
        )
        assert event.event_id.startswith("evt_")
        assert event.type == "NODE_STARTED"

        # Query back
        stored = db_session.query(IncidentRunEvent).filter_by(run_id="run-1").all()
        assert len(stored) == 1
        assert stored[0].node_name == "intake"

    def test_publish_notifies_subscriber(self, db_session):
        bus = EventBus()
        queue = bus.subscribe("run-1")

        bus.publish(db=db_session, run_id="run-1", event_type=EventType.RUN_CREATED, message="created")

        assert not queue.empty()
        event = queue.get_nowait()
        assert event["type"] == "RUN_CREATED"
        assert event["message"] == "created"

    def test_unsubscribe(self, db_session):
        bus = EventBus()
        queue = bus.subscribe("run-1")
        bus.unsubscribe("run-1", queue)

        bus.publish(db=db_session, run_id="run-1", event_type=EventType.RUN_CREATED)
        assert queue.empty()

    def test_multiple_events(self, db_session):
        bus = EventBus()
        bus.publish(db=db_session, run_id="run-1", event_type=EventType.NODE_STARTED, node_name="intake")
        bus.publish(db=db_session, run_id="run-1", event_type=EventType.NODE_COMPLETED, node_name="intake")

        stored = db_session.query(IncidentRunEvent).filter_by(run_id="run-1").all()
        assert len(stored) == 2
