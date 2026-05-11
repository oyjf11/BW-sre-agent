from sqlalchemy import create_engine

from app.repositories import ensure_sqlite_schema, normalize_database_url


class TestRepositories:
    def test_normalize_database_url_for_sync_engine(self):
        assert (
            normalize_database_url("sqlite+aiosqlite:///./opspilot.db")
            == "sqlite:///./opspilot.db"
        )

    def test_normalize_database_url_keeps_non_async_urls(self):
        assert (
            normalize_database_url("postgresql://user:pass@localhost/db")
            == "postgresql://user:pass@localhost/db"
        )

    def test_ensure_sqlite_schema_upgrades_legacy_tables(self, tmp_path):
        engine = create_engine(
            f"sqlite:///{tmp_path / 'legacy.db'}",
            connect_args={"check_same_thread": False},
        )

        with engine.begin() as connection:
            connection.exec_driver_sql(
                """
                CREATE TABLE incident_runs (
                    run_id VARCHAR NOT NULL PRIMARY KEY,
                    thread_id VARCHAR NOT NULL,
                    ticket_id VARCHAR,
                    status VARCHAR(18) NOT NULL,
                    severity VARCHAR,
                    service VARCHAR,
                    env VARCHAR,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    completed_at DATETIME,
                    started_by VARCHAR
                )
                """
            )
            connection.exec_driver_sql(
                """
                INSERT INTO incident_runs (
                    run_id, thread_id, ticket_id, status, created_at, updated_at
                ) VALUES (
                    'run-1', 'thread-1', 'ticket-1', 'NEW',
                    '2026-03-29 00:00:00', '2026-03-29 00:00:00'
                )
                """
            )
            connection.exec_driver_sql(
                """
                CREATE TABLE incident_actions (
                    action_id VARCHAR NOT NULL PRIMARY KEY,
                    run_id VARCHAR NOT NULL,
                    idempotency_key VARCHAR,
                    action_type VARCHAR NOT NULL,
                    params_json JSON NOT NULL,
                    execution_status VARCHAR NOT NULL,
                    result_json JSON,
                    created_at DATETIME NOT NULL
                )
                """
            )
            connection.exec_driver_sql(
                """
                CREATE TABLE incident_rca_reports (
                    run_id VARCHAR NOT NULL PRIMARY KEY,
                    report_markdown TEXT NOT NULL,
                    root_cause TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    prevention_items_json JSON,
                    confirmed_by_human INTEGER
                )
                """
            )

        ensure_sqlite_schema(engine)
        ensure_sqlite_schema(engine)

        with engine.connect() as connection:
            run_columns = {
                row[1] for row in connection.exec_driver_sql("PRAGMA table_info('incident_runs')")
            }
            action_columns = {
                row[1] for row in connection.exec_driver_sql("PRAGMA table_info('incident_actions')")
            }
            rca_columns = {
                row[1] for row in connection.exec_driver_sql("PRAGMA table_info('incident_rca_reports')")
            }
            run_defaults = connection.exec_driver_sql(
                """
                SELECT schema_version, step_count, requires_human
                FROM incident_runs
                WHERE run_id = 'run-1'
                """
            ).fetchone()

        assert {
            "current_node",
            "input_source",
            "schema_version",
            "step_count",
            "last_error_code",
            "last_error_message",
            "started_at",
            "requires_human",
            "summary_json",
        }.issubset(run_columns)
        assert {
            "approval_id",
            "attempt_no",
            "executor_name",
            "request_json",
            "verification_status",
            "verification_details_json",
            "started_at",
            "completed_at",
        }.issubset(action_columns)
        assert {
            "timeline_summary",
            "impact_assessment",
            "supporting_evidence_ids_json",
            "executed_action_ids_json",
            "archive_ref",
            "created_at",
        }.issubset(rca_columns)
        assert run_defaults == (1, 0, 0)
