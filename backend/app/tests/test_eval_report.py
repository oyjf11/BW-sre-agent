"""Tests for report assembly + markdown rendering."""
import json

from app.evals.metrics import aggregate_rounds, compute_metrics
from app.evals.report import build_report, render_markdown, write_report
from app.evals.scorer import CaseResult


def _r(case_id, exp, act):
    return CaseResult(
        case_id=case_id,
        hit_top1=(exp == act),
        hit_top3=(exp == act),
        risk_match=None,
        status_match=None,
        actual_type=act,
        expected_type=exp,
        confidence=0.8,
        latency_ms=100,
        hypothesis="some hypothesis text",
    )


def _round():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", "resource_exhaustion", "unknown"),
    ]
    return results, compute_metrics(results)


def test_build_report_structure():
    r1, m1 = _round()
    report = build_report(
        mode="direct",
        rounds_results=[r1],
        rounds_metrics=[m1],
        aggregate=aggregate_rounds([m1]),
    )
    assert report["mode"] == "direct"
    assert report["meta"]["real_llm"] is True
    assert report["meta"]["ci_metric"] is False
    assert "aggregate" in report
    assert len(report["rounds"]) == 1
    assert report["rounds"][0]["cases"][0]["hypothesis"] == "some hypothesis text"


def test_render_markdown_contains_disclaimer_and_metrics():
    r1, m1 = _round()
    report = build_report(
        mode="direct",
        rounds_results=[r1],
        rounds_metrics=[m1],
        aggregate=aggregate_rounds([m1]),
    )
    md = render_markdown(report)
    assert "真实 LLM" in md
    assert "非 CI 指标" in md
    assert "Top1" in md
    assert "Confusion" in md or "混淆" in md


def test_write_report_emits_json(tmp_path):
    r1, m1 = _round()
    report = build_report(
        mode="direct",
        rounds_results=[r1],
        rounds_metrics=[m1],
        aggregate=aggregate_rounds([m1]),
    )
    out = tmp_path / "report.json"
    write_report(report, str(out))
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["mode"] == "direct"
    assert (tmp_path / "report.md").exists()
