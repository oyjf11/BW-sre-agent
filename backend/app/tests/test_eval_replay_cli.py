"""Tests for CLI wiring: arg parsing, executor selection, compare diff."""
from app.evals.executors import DirectGraphExecutor, RunnerGraphExecutor
from app.evals.replay_runner import build_arg_parser, diff_compare, make_executor


def test_parser_defaults():
    parser = build_arg_parser()
    args = parser.parse_args([])
    assert args.mode == "direct"
    assert args.repeat == 1
    assert args.dataset.endswith("datasets/")


def test_parser_custom():
    parser = build_arg_parser()
    args = parser.parse_args(
        ["--mode", "runner", "--repeat", "3", "--dataset", "d/", "--output", "o.json"]
    )
    assert args.mode == "runner"
    assert args.repeat == 3
    assert args.dataset == "d/"
    assert args.output == "o.json"


def test_make_executor_direct():
    assert isinstance(make_executor("direct"), DirectGraphExecutor)


def test_make_executor_runner():
    assert isinstance(make_executor("runner"), RunnerGraphExecutor)


def test_diff_compare_flags_mismatch():
    direct_state = {
        "root_cause_candidates": [{"incident_type": "deployment_regression"}],
        "status": "COMPLETED",
    }
    runner_state = {
        "root_cause_candidates": [{"incident_type": "resource_exhaustion"}],
        "status": "WAITING_HUMAN",
    }
    diff = diff_compare("c1", direct_state, runner_state)
    assert diff["case_id"] == "c1"
    assert diff["incident_type_match"] is False
    assert diff["status_match"] is False
    assert diff["direct_incident_type"] == "deployment_regression"
    assert diff["runner_incident_type"] == "resource_exhaustion"


def test_diff_compare_agrees():
    state = {
        "root_cause_candidates": [{"incident_type": "deployment_regression"}],
        "status": "COMPLETED",
    }
    diff = diff_compare("c1", state, dict(state))
    assert diff["incident_type_match"] is True
    assert diff["status_match"] is True
