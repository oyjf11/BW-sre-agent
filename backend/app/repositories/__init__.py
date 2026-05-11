import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.db_models import Base
from app.core.config import get_settings

# Re-export all repos
from app.repositories.runs_repo import RunsRepo
from app.repositories.events_repo import EventsRepo
from app.repositories.checkpoints_repo import CheckpointsRepo
from app.repositories.evidence_repo import EvidenceRepo
from app.repositories.approvals_repo import ApprovalsRepo
from app.repositories.actions_repo import ActionsRepo
from app.repositories.rca_repo import RcaRepo

logger = logging.getLogger(__name__)


SQLITE_LEGACY_COLUMN_PATCHES = {
    "incident_approvals": [
        ("reason", "ALTER TABLE incident_approvals ADD COLUMN reason TEXT"),
        ("expected_impact", "ALTER TABLE incident_approvals ADD COLUMN expected_impact TEXT"),
        ("rollback_plan", "ALTER TABLE incident_approvals ADD COLUMN rollback_plan TEXT"),
    ],
    "incident_runs": [
        ("current_node", "ALTER TABLE incident_runs ADD COLUMN current_node VARCHAR"),
        ("input_source", "ALTER TABLE incident_runs ADD COLUMN input_source VARCHAR"),
        (
            "schema_version",
            "ALTER TABLE incident_runs ADD COLUMN schema_version INTEGER NOT NULL DEFAULT 1",
        ),
        ("step_count", "ALTER TABLE incident_runs ADD COLUMN step_count INTEGER NOT NULL DEFAULT 0"),
        ("last_error_code", "ALTER TABLE incident_runs ADD COLUMN last_error_code VARCHAR"),
        (
            "last_error_message",
            "ALTER TABLE incident_runs ADD COLUMN last_error_message TEXT",
        ),
        ("started_at", "ALTER TABLE incident_runs ADD COLUMN started_at DATETIME"),
        (
            "requires_human",
            "ALTER TABLE incident_runs ADD COLUMN requires_human INTEGER NOT NULL DEFAULT 0",
        ),
        ("summary_json", "ALTER TABLE incident_runs ADD COLUMN summary_json JSON"),
    ],
    "incident_actions": [
        ("approval_id", "ALTER TABLE incident_actions ADD COLUMN approval_id VARCHAR"),
        ("attempt_no", "ALTER TABLE incident_actions ADD COLUMN attempt_no INTEGER NOT NULL DEFAULT 1"),
        ("executor_name", "ALTER TABLE incident_actions ADD COLUMN executor_name VARCHAR"),
        ("request_json", "ALTER TABLE incident_actions ADD COLUMN request_json JSON"),
        (
            "verification_status",
            "ALTER TABLE incident_actions ADD COLUMN verification_status VARCHAR",
        ),
        (
            "verification_details_json",
            "ALTER TABLE incident_actions ADD COLUMN verification_details_json JSON",
        ),
        ("started_at", "ALTER TABLE incident_actions ADD COLUMN started_at DATETIME"),
        ("completed_at", "ALTER TABLE incident_actions ADD COLUMN completed_at DATETIME"),
    ],
    "incident_rca_reports": [
        (
            "timeline_summary",
            "ALTER TABLE incident_rca_reports ADD COLUMN timeline_summary TEXT",
        ),
        (
            "impact_assessment",
            "ALTER TABLE incident_rca_reports ADD COLUMN impact_assessment TEXT",
        ),
        (
            "supporting_evidence_ids_json",
            "ALTER TABLE incident_rca_reports ADD COLUMN supporting_evidence_ids_json JSON",
        ),
        (
            "executed_action_ids_json",
            "ALTER TABLE incident_rca_reports ADD COLUMN executed_action_ids_json JSON",
        ),
        ("archive_ref", "ALTER TABLE incident_rca_reports ADD COLUMN archive_ref VARCHAR"),
        ("created_at", "ALTER TABLE incident_rca_reports ADD COLUMN created_at DATETIME"),
    ],
}


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite:///"):
        return database_url.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
    return database_url


def ensure_sqlite_schema(engine) -> None:
    """Apply additive SQLite patches for legacy local databases.

    The app still boots via `create_all()`, which creates missing tables but does not
    migrate existing ones. Older local SQLite files can therefore miss columns that the
    current ORM selects, causing runtime 500s on simple reads like `GET /incidents/runs`.
    """
    if not engine.url.drivername.startswith("sqlite"):
        return

    with engine.begin() as connection:
        for table_name, column_patches in SQLITE_LEGACY_COLUMN_PATCHES.items():
            table_exists = connection.exec_driver_sql(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table_name,),
            ).fetchone()
            if not table_exists:
                continue

            existing_columns = {
                row[1] for row in connection.exec_driver_sql(f"PRAGMA table_info('{table_name}')")
            }
            for column_name, ddl in column_patches:
                if column_name in existing_columns:
                    continue
                connection.exec_driver_sql(ddl)
                logger.info("Patched legacy SQLite schema: added %s.%s", table_name, column_name)
                existing_columns.add(column_name)


DATABASE_URL = normalize_database_url(get_settings().database_url)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables via SQLAlchemy for isolated in-memory test databases ONLY.

    WARNING: This is NOT the application startup path.
    Production / staging schema migrations must be performed via `alembic upgrade head`.
    The FastAPI lifespan in main.py handles this automatically on server startup.

    Tests that use a real or file-based SQLite DB should also use Alembic instead.
    Only call this for ephemeral in-memory databases in test fixtures.
    """
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema(engine)


__all__ = [
    "RunsRepo",
    "EventsRepo",
    "CheckpointsRepo",
    "EvidenceRepo",
    "ApprovalsRepo",
    "ActionsRepo",
    "RcaRepo",
    "get_db",
    "init_db",
    "SessionLocal",
    "engine",
    "normalize_database_url",
]
