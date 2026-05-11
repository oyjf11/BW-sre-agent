from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import uuid

from app.models.db_models import IncidentEvidence


class EvidenceRepo:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        run_id: str,
        tool_name: str,
        category: str,
        source_ref: str,
        summary: str,
        raw_payload: Optional[Dict[str, Any]] = None,
        evidence_id: Optional[str] = None,
    ) -> IncidentEvidence:
        evidence_id = evidence_id or f"ev_{uuid.uuid4().hex[:8]}"
        evidence = IncidentEvidence(
            evidence_id=evidence_id,
            run_id=run_id,
            tool_name=tool_name,
            category=category,
            source_ref=source_ref,
            summary=summary,
            raw_payload_json=raw_payload,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def list_by_run(self, run_id: str) -> List[IncidentEvidence]:
        return (
            self.db.query(IncidentEvidence)
            .filter(IncidentEvidence.run_id == run_id)
            .order_by(IncidentEvidence.created_at)
            .all()
        )
