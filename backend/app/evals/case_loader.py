"""Load and validate eval dataset case JSON files."""
import json
from pathlib import Path
from typing import Dict, List

from app.models.incident_type import IncidentType

REQUIRED_TOP = ("case_id", "ticket")
REQUIRED_TICKET = (
    "ticket_id",
    "title",
    "description",
    "service",
    "env",
    "severity",
    "source",
)
_VALID_TYPES = {t.value for t in IncidentType}


class EvalDatasetError(Exception):
    """Raised when a dataset case fails schema validation."""


def load_cases(path: str) -> List[Dict]:
    """Load case dicts from a directory of *.json files or from one JSON file."""
    p = Path(path)
    if p.is_dir():
        files = sorted(p.glob("*.json"))
    elif p.is_file():
        files = [p]
    else:
        raise EvalDatasetError(f"Dataset path not found: {path}")

    cases: List[Dict] = []
    seen = set()
    for file_path in files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise EvalDatasetError(f"{file_path.name}: invalid JSON ({exc})") from exc

        _validate_case(data, file_path.name)
        case_id = data["case_id"]
        if case_id in seen:
            raise EvalDatasetError(f"Duplicate case_id '{case_id}' in {file_path.name}")
        seen.add(case_id)
        cases.append(data)

    if not cases:
        raise EvalDatasetError(f"No case JSON files found under {path}")

    return cases


def _validate_case(data: Dict, fname: str) -> None:
    if not isinstance(data, dict):
        raise EvalDatasetError(f"{fname}: top-level JSON must be an object")

    for key in REQUIRED_TOP:
        if key not in data:
            raise EvalDatasetError(f"{fname}: missing required field '{key}'")

    ticket = data["ticket"]
    if not isinstance(ticket, dict):
        raise EvalDatasetError(f"{fname}: 'ticket' must be an object")
    for key in REQUIRED_TICKET:
        if key not in ticket:
            raise EvalDatasetError(f"{fname}: ticket missing required field '{key}'")

    fixtures = data.get("tool_fixtures", {})
    if not isinstance(fixtures, dict):
        raise EvalDatasetError(f"{fname}: 'tool_fixtures' must be an object")

    expected = data.get("expected", {})
    if not isinstance(expected, dict):
        raise EvalDatasetError(f"{fname}: 'expected' must be an object")

    expected_type = expected.get("incident_type")
    if expected_type is not None and expected_type not in _VALID_TYPES:
        raise EvalDatasetError(
            f"{fname}: expected.incident_type '{expected_type}' is not a valid IncidentType"
        )
