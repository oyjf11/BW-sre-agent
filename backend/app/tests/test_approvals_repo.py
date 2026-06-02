from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.db_models import Base, IncidentApproval, IncidentRun, RunStatusEnum
from app.repositories.approvals_repo import ApprovalsRepo


def test_get_pending_returns_newest_approvals_first():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = session_factory()
    try:
        db.add(IncidentRun(run_id="run-1", thread_id="thread-1", status=RunStatusEnum.NEW))
        db.add_all(
            [
                IncidentApproval(
                    approval_id="apr_oldest",
                    run_id="run-1",
                    action_json={},
                    risk_level="LOW",
                    status="PENDING",
                    created_at=datetime(2026, 6, 1, 10, 0, 0),
                ),
                IncidentApproval(
                    approval_id="apr_approved",
                    run_id="run-1",
                    action_json={},
                    risk_level="LOW",
                    status="APPROVED",
                    created_at=datetime(2026, 6, 1, 11, 0, 0),
                ),
                IncidentApproval(
                    approval_id="apr_newest",
                    run_id="run-1",
                    action_json={},
                    risk_level="LOW",
                    status="PENDING",
                    created_at=datetime(2026, 6, 1, 12, 0, 0),
                ),
            ]
        )
        db.commit()

        approvals = ApprovalsRepo(db).get_pending()

        assert [approval.approval_id for approval in approvals] == [
            "apr_newest",
            "apr_oldest",
        ]
    finally:
        db.close()
