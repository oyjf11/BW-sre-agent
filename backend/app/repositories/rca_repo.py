from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.db_models import IncidentRcaReport


class RcaRepo:
    def __init__(self, db: Session):
        self.db = db

    def upsert(
        self,
        run_id: str,
        report_markdown: str,
        root_cause: str,
        resolution: str,
        prevention_items: Optional[List[str]] = None,
        confirmed_by_human: bool = False,
        timeline_summary: Optional[str] = None,
        impact_assessment: Optional[str] = None,
        supporting_evidence_ids: Optional[List[str]] = None,
        executed_action_ids: Optional[List[str]] = None,
        archive_ref: Optional[str] = None,
    ) -> IncidentRcaReport:
        existing = (
            self.db.query(IncidentRcaReport)
            .filter(IncidentRcaReport.run_id == run_id)
            .first()
        )
        if existing:
            existing.report_markdown = report_markdown
            existing.root_cause = root_cause
            existing.resolution = resolution
            existing.prevention_items_json = prevention_items
            existing.confirmed_by_human = 1 if confirmed_by_human else 0
            existing.timeline_summary = timeline_summary
            existing.impact_assessment = impact_assessment
            existing.supporting_evidence_ids_json = supporting_evidence_ids
            existing.executed_action_ids_json = executed_action_ids
            if archive_ref:
                existing.archive_ref = archive_ref
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            rca = IncidentRcaReport(
                run_id=run_id,
                report_markdown=report_markdown,
                root_cause=root_cause,
                resolution=resolution,
                prevention_items_json=prevention_items,
                confirmed_by_human=1 if confirmed_by_human else 0,
                timeline_summary=timeline_summary,
                impact_assessment=impact_assessment,
                supporting_evidence_ids_json=supporting_evidence_ids,
                executed_action_ids_json=executed_action_ids,
                archive_ref=archive_ref,
            )
            self.db.add(rca)
            self.db.commit()
            self.db.refresh(rca)
            return rca

    def get(self, run_id: str) -> Optional[IncidentRcaReport]:
        return (
            self.db.query(IncidentRcaReport)
            .filter(IncidentRcaReport.run_id == run_id)
            .first()
        )

    def confirm(self, run_id: str) -> Optional[IncidentRcaReport]:
        rca = self.get(run_id)
        if not rca:
            return None
        rca.confirmed_by_human = 1
        self.db.commit()
        self.db.refresh(rca)
        return rca
