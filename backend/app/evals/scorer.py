"""Deterministic per-case scoring for offline eval."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CaseResult:
    case_id: str
    hit_top1: Optional[bool]
    hit_top3: Optional[bool]
    risk_match: Optional[bool]
    status_match: Optional[bool]
    actual_type: Optional[str]
    expected_type: Optional[str]
    confidence: Optional[float]
    latency_ms: Optional[int]
    hypothesis: Optional[str]
    error: Optional[str] = None

    @classmethod
    def error_result(cls, case_id: str, error: str, latency_ms: int) -> "CaseResult":
        return cls(
            case_id=case_id,
            hit_top1=None,
            hit_top3=None,
            risk_match=None,
            status_match=None,
            actual_type=None,
            expected_type=None,
            confidence=None,
            latency_ms=latency_ms,
            hypothesis=None,
            error=error,
        )


def score_case(case: Dict[str, Any], final_state: Dict[str, Any], latency_ms: int) -> CaseResult:
    case_id = case["case_id"]
    expected = case.get("expected", {}) or {}

    candidates = final_state.get("root_cause_candidates") or []
    candidate_types = (
        _type_value(candidate) for candidate in candidates if candidate is not None
    )
    types: List[str] = [type_value for type_value in candidate_types if type_value]
    top_candidate = candidates[0] if candidates else None
    top_type = types[0] if types else None

    expected_type = expected.get("incident_type")
    hit_top1 = top_type == expected_type if expected_type is not None else None
    hit_top3 = expected_type in types[:3] if expected_type is not None else None

    expected_risk = expected.get("risk_decision")
    risk_match = (
        final_state.get("risk_decision") == expected_risk
        if expected_risk is not None
        else None
    )

    expected_status = expected.get("final_status")
    actual_status = _status_value(final_state.get("status"))
    status_match = actual_status == expected_status if expected_status is not None else None

    return CaseResult(
        case_id=case_id,
        hit_top1=hit_top1,
        hit_top3=hit_top3,
        risk_match=risk_match,
        status_match=status_match,
        actual_type=top_type,
        expected_type=expected_type,
        confidence=_attr(top_candidate, "confidence"),
        latency_ms=latency_ms,
        hypothesis=_attr(top_candidate, "hypothesis"),
        error=None,
    )


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, dict):
        return obj.get(name, default)
    return default


def _type_value(candidate: Any) -> Optional[str]:
    incident_type = _attr(candidate, "incident_type")
    if incident_type is None:
        return None
    return incident_type.value if hasattr(incident_type, "value") else str(incident_type)


def _status_value(status: Any) -> Optional[str]:
    if status is None:
        return None
    return status.value if hasattr(status, "value") else str(status)
