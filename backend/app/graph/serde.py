"""State serialization / deserialization for checkpoint persistence."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.graph.state import IncidentAgentState, RunStatus
from app.models.incident import IncidentTicket
from app.models.triage import TriageResult
from app.models.evidence import EvidenceItem
from app.models.root_cause import RootCauseCandidate
from app.models.remediation import RemediationPlan
from app.models.approval import ApprovalRequest, ApprovalResult
from app.models.rca import RcaReport
from app.models.planning import MemoryHit, InvestigationPlan


def _serialize_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, BaseModel):
        return v.model_dump(mode="json")
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, list):
        return [_serialize_value(item) for item in v]
    if isinstance(v, dict):
        return {k: _serialize_value(val) for k, val in v.items()}
    return v


def serialize_state(state: IncidentAgentState) -> Dict[str, Any]:
    return {k: _serialize_value(v) for k, v in state.items()}


# Mapping from state key -> model class for deserialization
_SINGLE_MODEL_FIELDS = {
    "ticket": IncidentTicket,
    "triage": TriageResult,
    "remediation_plan": RemediationPlan,
    "pending_approval": ApprovalRequest,
    "approval_result": ApprovalResult,
    "rca_report": RcaReport,
    "investigation_plan": InvestigationPlan,
}

_LIST_MODEL_FIELDS = {
    "evidence_items": EvidenceItem,
    "root_cause_candidates": RootCauseCandidate,
    "memory_hits": MemoryHit,
}


def deserialize_state(data: Dict[str, Any]) -> IncidentAgentState:
    result: Dict[str, Any] = {}
    for key, value in data.items():
        if value is None:
            result[key] = None
        elif key in _SINGLE_MODEL_FIELDS:
            result[key] = _SINGLE_MODEL_FIELDS[key].model_validate(value)
        elif key in _LIST_MODEL_FIELDS:
            cls = _LIST_MODEL_FIELDS[key]
            result[key] = [cls.model_validate(item) for item in value]
        elif key == "status" and isinstance(value, str):
            result[key] = RunStatus(value)
        elif key == "error" and isinstance(value, dict):
            result[key] = value
        else:
            result[key] = value
    return IncidentAgentState(**result)
