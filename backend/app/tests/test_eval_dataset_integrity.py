"""The shipped dataset must load cleanly and cover every core IncidentType."""
from pathlib import Path

from app.evals.case_loader import load_cases
from app.models.incident_type import IncidentType
from app.tools.gateway import tool_handlers

_DATASET_DIR = Path(__file__).resolve().parents[1] / "evals" / "datasets"
_NOT_REQUIRED = {IncidentType.unknown.value, IncidentType.other.value}


def test_dataset_loads():
    cases = load_cases(str(_DATASET_DIR))
    assert len(cases) >= 10


def test_every_core_incident_type_has_a_case():
    cases = load_cases(str(_DATASET_DIR))
    covered = {case.get("expected", {}).get("incident_type") for case in cases}
    required = {incident_type.value for incident_type in IncidentType} - _NOT_REQUIRED
    missing = required - covered
    assert not missing, f"dataset missing cases for: {sorted(missing)}"


def test_has_approval_scenario():
    cases = load_cases(str(_DATASET_DIR))
    risks = {case.get("expected", {}).get("risk_decision") for case in cases}
    assert "NEEDS_APPROVAL" in risks


def test_fixture_tool_names_are_registered():
    cases = load_cases(str(_DATASET_DIR))
    unknown_tools = []
    for case in cases:
        for tool_name in case.get("tool_fixtures", {}):
            if tool_name not in tool_handlers:
                unknown_tools.append((case["case_id"], tool_name))

    assert not unknown_tools
