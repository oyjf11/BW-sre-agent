import asyncio
import tempfile
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db_models import Base, IncidentRun, IncidentRunEvent, RunStatusEnum
from app.services.event_bus import EventBus, EventType


@pytest.fixture
def db_session():
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        # Create a run for FK
        session.add(IncidentRun(run_id="run-1", thread_id="t-1", status=RunStatusEnum.NEW))
        session.commit()
        yield session
        session.close()
    finally:
        os.unlink(db_path)


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

    @pytest.mark.asyncio
    async def test_publish_notifies_subscriber(self, db_session):
        bus = EventBus()
        iterator = bus.iter_events("run-1")
        pending = asyncio.create_task(anext(iterator))
        await asyncio.sleep(0)

        bus.publish(
            db=db_session,
            run_id="run-1",
            event_type=EventType.RUN_CREATED,
            message="created",
        )

        event = await asyncio.wait_for(pending, timeout=1)
        assert event["type"] == "RUN_CREATED"
        assert event["message"] == "created"
        assert "timestamp" in event
        await iterator.aclose()

    @pytest.mark.asyncio
    async def test_publish_notifies_subscriber_from_worker_thread(self, db_session):
        bus = EventBus()
        iterator = bus.iter_events("run-1")
        pending = asyncio.create_task(anext(iterator))
        await asyncio.sleep(0)

        await asyncio.to_thread(
            bus.publish,
            db_session,
            "run-1",
            EventType.NODE_STARTED,
            "node_intake",
            "started",
        )

        event = await asyncio.wait_for(pending, timeout=1)
        assert event["node_name"] == "node_intake"
        assert event["message"] == "started"
        await iterator.aclose()

    @pytest.mark.asyncio
    async def test_unsubscribe(self, db_session):
        bus = EventBus()
        subscriber = bus.subscribe("run-1")
        bus.unsubscribe("run-1", subscriber)

        bus.publish(db=db_session, run_id="run-1", event_type=EventType.RUN_CREATED)

        assert subscriber.queue.empty()

    def test_multiple_events(self, db_session):
        bus = EventBus()
        bus.publish(db=db_session, run_id="run-1", event_type=EventType.NODE_STARTED, node_name="intake")
        bus.publish(db=db_session, run_id="run-1", event_type=EventType.NODE_COMPLETED, node_name="intake")

        stored = db_session.query(IncidentRunEvent).filter_by(run_id="run-1").all()
        assert len(stored) == 2
