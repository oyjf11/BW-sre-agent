"""Knowledge Writeback Service: writes confirmed RCA to knowledge base."""

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.db_models import IncidentKnowledgeWriteback, IncidentRcaReport
from app.repositories.rca_repo import RcaRepo
from app.services.event_bus import EventType, event_bus

logger = logging.getLogger(__name__)


class KnowledgeWritebackService:
    def __init__(self, db: Session):
        self.db = db
        self.rca_repo = RcaRepo(db)

    def writeback(self, run_id: str, target: str = "runbook") -> Optional[IncidentKnowledgeWriteback]:
        """Write confirmed RCA knowledge to target store. Returns None if not confirmed."""
        rca = self.rca_repo.get(run_id)
        if not rca:
            logger.warning(f"No RCA found for run {run_id}")
            return None

        if not rca.confirmed_by_human:
            logger.info(f"RCA for run {run_id} not confirmed by human, skipping writeback")
            return None

        # Build writeback content
        content = {
            "run_id": run_id,
            "root_cause": rca.root_cause,
            "resolution": rca.resolution,
            "prevention_items": rca.prevention_items_json,
            "report_markdown": rca.report_markdown,
        }

        metadata = {
            "source_run_id": run_id,
            "validated": True,
        }
        # Extract service/env/severity from run if available
        from app.repositories.runs_repo import RunsRepo
        runs_repo = RunsRepo(self.db)
        run = runs_repo.get(run_id)
        if run:
            metadata["service"] = run.service
            metadata["env"] = run.env
            metadata["severity"] = run.severity

        writeback_id = f"wb_{uuid.uuid4().hex[:8]}"
        record = IncidentKnowledgeWriteback(
            writeback_id=writeback_id,
            run_id=run_id,
            target=target,
            content_json=content,
            metadata_json=metadata,
            status="PENDING",
        )
        self.db.add(record)
        self.db.commit()

        # Attempt actual writeback (via gateway for runbook target)
        try:
            self._do_writeback(record, content, metadata)
            record.status = "COMPLETED"
            self.db.commit()

            event_bus.publish(
                db=self.db, run_id=run_id,
                event_type=EventType.RCA_COMPLETED,
                message=f"Knowledge writeback completed to {target}",
                data={"writeback_id": writeback_id, "target": target},
            )
        except Exception as e:
            logger.exception(f"Knowledge writeback failed for run {run_id}")
            record.status = "FAILED"
            record.error_message = str(e)
            self.db.commit()

            event_bus.publish(
                db=self.db, run_id=run_id,
                event_type=EventType.RCA_COMPLETED,
                message=f"Knowledge writeback failed to {target}: {e}",
                data={"writeback_id": writeback_id, "target": target, "error": str(e)},
            )

        self.db.refresh(record)
        return record

    def archive_rca(self, run_id: str) -> Optional[str]:
        """Archive RCA report + evidence bundle to OSS. Returns archive_ref or None."""
        rca = self.rca_repo.get(run_id)
        if not rca:
            return None

        try:
            archive_ref = self._do_archive(run_id, rca)
            rca.archive_ref = archive_ref
            self.db.commit()

            event_bus.publish(
                db=self.db, run_id=run_id,
                event_type=EventType.RCA_COMPLETED,
                message=f"RCA archived to {archive_ref}",
                data={"archive_ref": archive_ref},
            )
            return archive_ref
        except Exception as e:
            # OSS failure is non-blocking
            logger.exception(f"Archive failed for run {run_id}, continuing without archive")
            event_bus.publish(
                db=self.db, run_id=run_id,
                event_type=EventType.RCA_COMPLETED,
                message=f"Archive failed (non-blocking): {e}",
                data={"error": str(e)},
            )
            return None

    def _do_archive(self, run_id: str, rca: IncidentRcaReport) -> str:
        """Archive to OSS. Currently a stub returning a synthetic path."""
        archive_path = f"rca/{run_id}/report.md"
        logger.info(f"Archiving RCA for run {run_id} to {archive_path}")
        # In production: gateway.call_tool("write_rca_report_to_oss", {...})
        return archive_path

    def _do_writeback(self, record: IncidentKnowledgeWriteback, content: Dict[str, Any], metadata: Dict[str, Any]):
        """Actual writeback implementation. Currently a stub that logs."""
        logger.info(
            f"Writing knowledge for run {record.run_id} to {record.target}: "
            f"root_cause={content.get('root_cause', 'unknown')}"
        )
        # In production, this would call the gateway to write to a knowledge store
        # e.g., gateway.call_tool("write_runbook_entry", {...})
