"""Tests for metric aggregation (pure stdlib, deterministic)."""
import math

from app.evals.metrics import aggregate_rounds, compute_metrics
from app.evals.scorer import CaseResult


def _r(case_id, exp, act, conf=0.8, risk=None, status=None, error=None):
    hit1 = (exp == act) if (exp is not None and error is None) else (None if error else False)
    return CaseResult(
        case_id=case_id,
        hit_top1=hit1,
        hit_top3=hit1,
        risk_match=risk,
        status_match=status,
        actual_type=act,
        expected_type=exp,
        confidence=conf,
        latency_ms=100,
        hypothesis="h",
        error=error,
    )


def test_top1_accuracy():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", "resource_exhaustion", "deployment_regression"),
        _r("c3", "database_failure", "database_failure"),
    ]
    m = compute_metrics(results)
    assert m["top1_accuracy"] == round(2 / 3, 4)
    assert m["case_count"] == 3
    assert m["scored_count"] == 3
    assert m["error_count"] == 0


def test_macro_f1_and_confusion_and_recall():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", "deployment_regression", "resource_exhaustion"),
        _r("c3", "resource_exhaustion", "resource_exhaustion"),
    ]
    m = compute_metrics(results)

    cm = m["confusion_matrix"]
    assert cm["deployment_regression"]["deployment_regression"] == 1
    assert cm["deployment_regression"]["resource_exhaustion"] == 1
    assert cm["resource_exhaustion"]["resource_exhaustion"] == 1

    assert m["per_class"]["deployment_regression"]["recall"] == 0.5
    assert m["per_class"]["resource_exhaustion"]["recall"] == 1.0
    assert math.isclose(m["macro_f1"], round(2 / 3, 4), abs_tol=1e-4)


def test_unknown_rate():
    results = [
        _r("c1", "deployment_regression", "unknown"),
        _r("c2", "resource_exhaustion", "resource_exhaustion"),
    ]
    m = compute_metrics(results)
    assert m["unknown_rate"] == 0.5


def test_risk_and_status_accuracy_skip_none():
    results = [
        _r("c1", "deployment_regression", "deployment_regression", risk=True, status=True),
        _r("c2", "resource_exhaustion", "resource_exhaustion", risk=False, status=None),
    ]
    m = compute_metrics(results)
    assert m["risk_accuracy"] == 0.5
    assert m["status_accuracy"] == 1.0


def test_errors_excluded_from_accuracy():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", None, None, error="Boom"),
    ]
    m = compute_metrics(results)
    assert m["error_count"] == 1
    assert m["scored_count"] == 1
    assert m["top1_accuracy"] == 1.0


def test_aggregate_rounds_mean_min_max():
    m1 = compute_metrics([_r("c1", "deployment_regression", "deployment_regression")])
    m2 = compute_metrics([_r("c1", "deployment_regression", "resource_exhaustion")])
    agg = aggregate_rounds([m1, m2])
    assert agg["top1_accuracy"]["mean"] == 0.5
    assert agg["top1_accuracy"]["min"] == 0.0
    assert agg["top1_accuracy"]["max"] == 1.0
    assert agg["rounds"] == 2
