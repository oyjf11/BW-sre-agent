"""Tests for dataset case loading + schema validation."""
import json

import pytest

from app.evals.case_loader import EvalDatasetError, load_cases


def _valid_case(case_id="c1", incident_type="deployment_regression"):
    return {
        "case_id": case_id,
        "description": "human-readable scenario",
        "ticket": {
            "ticket_id": "INC-1",
            "title": "5xx spike",
            "description": "errors",
            "service": "payment-service",
            "env": "staging",
            "severity": "P2",
            "source": "manual",
        },
        "tool_fixtures": {"query_logs": {"count": 3}},
        "expected": {"incident_type": incident_type},
    }


def _write(tmp_path, name, data):
    f = tmp_path / name
    f.write_text(json.dumps(data), encoding="utf-8")
    return f


def test_loads_valid_directory(tmp_path):
    _write(tmp_path, "a.json", _valid_case("c1"))
    _write(tmp_path, "b.json", _valid_case("c2", "resource_exhaustion"))
    cases = load_cases(str(tmp_path))
    assert {c["case_id"] for c in cases} == {"c1", "c2"}


def test_loads_single_file(tmp_path):
    f = _write(tmp_path, "a.json", _valid_case("solo"))
    cases = load_cases(str(f))
    assert len(cases) == 1
    assert cases[0]["case_id"] == "solo"


def test_missing_case_id_fails(tmp_path):
    bad = _valid_case()
    del bad["case_id"]
    _write(tmp_path, "bad.json", bad)
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "case_id" in str(exc.value)


def test_missing_ticket_field_fails(tmp_path):
    bad = _valid_case()
    del bad["ticket"]["service"]
    _write(tmp_path, "bad.json", bad)
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "service" in str(exc.value)


def test_illegal_expected_incident_type_fails(tmp_path):
    bad = _valid_case(incident_type="aliens")
    _write(tmp_path, "bad.json", bad)
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "incident_type" in str(exc.value)


def test_duplicate_case_id_fails(tmp_path):
    _write(tmp_path, "a.json", _valid_case("dup"))
    _write(tmp_path, "b.json", _valid_case("dup"))
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "dup" in str(exc.value)


def test_empty_directory_fails(tmp_path):
    with pytest.raises(EvalDatasetError):
        load_cases(str(tmp_path))
