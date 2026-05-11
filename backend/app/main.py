"""OpsPilot Backend - Main FastAPI Application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.api import incidents_router, approvals_router

logger = logging.getLogger(__name__)

_ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def _run_alembic_upgrade() -> None:
    """Run alembic upgrade head using the application database URL.

    This is the single authoritative schema migration path at startup.
    create_all() is NOT used here; Alembic is the sole schema authority.
    """
    try:
        from alembic.config import Config
        from alembic import command
        from app.repositories import DATABASE_URL, engine

        cfg = Config(str(_ALEMBIC_INI))
        cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

        _bootstrap_legacy_alembic_state(cfg, command, engine)
        command.upgrade(cfg, "head")
        logger.info("Alembic upgrade head completed successfully")
    except Exception:
        logger.exception(
            "Alembic migration failed at startup — database schema may be out of date"
        )
        raise


def _bootstrap_legacy_alembic_state(cfg, command, engine) -> None:
    """Stamp legacy local databases that already contain the full schema.

    Some local SQLite files were created outside Alembic, leaving all application
    tables present while `alembic_version` is missing or empty. Running the initial
    migration on that database causes `table already exists` failures on startup.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    from app.models.db_models import Base

    expected_tables = set(Base.metadata.tables.keys())
    if not expected_tables:
        return

    # Only auto-stamp when the full app schema already exists.
    if not expected_tables.issubset(existing_tables):
        return

    version_table_exists = "alembic_version" in existing_tables
    version_count = 0
    if version_table_exists:
        with engine.connect() as connection:
            version_count = connection.execute(
                text("SELECT COUNT(*) FROM alembic_version")
            ).scalar_one()

    if version_table_exists and version_count > 0:
        return

    logger.info(
        "Detected legacy database with existing schema but no Alembic revision; stamping head"
    )
    command.stamp(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_upgrade()
    yield


app = FastAPI(
    title="OpsPilot API",
    description="SRE Incident Management System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents_router)
app.include_router(approvals_router)


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
