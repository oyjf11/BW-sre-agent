from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from app.main import _bootstrap_legacy_alembic_state
from app.models.db_models import Base


class FakeAlembicCommand:
    def __init__(self):
        self.calls = []

    def stamp(self, cfg, revision):
        self.calls.append((cfg, revision))


def create_sqlite_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_bootstrap_stamps_when_schema_exists_but_revision_missing():
    engine = create_sqlite_engine()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))

    command = FakeAlembicCommand()
    cfg = object()

    _bootstrap_legacy_alembic_state(cfg, command, engine)

    assert command.calls == [(cfg, "head")]


def test_bootstrap_skips_when_revision_already_present():
    engine = create_sqlite_engine()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        connection.execute(text("INSERT INTO alembic_version(version_num) VALUES ('006')"))

    command = FakeAlembicCommand()
    cfg = object()

    _bootstrap_legacy_alembic_state(cfg, command, engine)

    assert command.calls == []


def test_bootstrap_skips_when_schema_is_incomplete():
    engine = create_sqlite_engine()
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE incident_runs (run_id VARCHAR PRIMARY KEY)"))

    command = FakeAlembicCommand()
    cfg = object()

    _bootstrap_legacy_alembic_state(cfg, command, engine)

    assert command.calls == []
