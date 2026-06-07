"""Assemble offline eval results into JSON and Markdown reports."""
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.evals.scorer import CaseResult

_DISCLAIMER = (
    "> 本报告由**真实 LLM**生成，结果存在波动，属**非 CI 指标**。"
    "请结合 repeat 的均值和波动范围解读，勿作为单点门禁。"
)


def build_report(
    mode: str,
    rounds_results: List[List[CaseResult]],
    rounds_metrics: List[Dict[str, Any]],
    aggregate: Dict[str, Any],
    extra_meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    meta = {
        "generated_at": datetime.utcnow().isoformat(),
        "real_llm": True,
        "ci_metric": False,
        "repeat": len(rounds_results),
    }
    if extra_meta:
        meta.update(extra_meta)

    rounds = []
    for idx, (results, metrics) in enumerate(zip(rounds_results, rounds_metrics)):
        rounds.append(
            {
                "round": idx + 1,
                "metrics": metrics,
                "cases": [asdict(result) for result in results],
            }
        )

    return {
        "mode": mode,
        "meta": meta,
        "aggregate": aggregate,
        "rounds": rounds,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines: List[str] = []
    lines.append(f"# OpsPilot 离线评测报告 - mode={report['mode']}")
    lines.append("")
    lines.append(_DISCLAIMER)
    lines.append("")
    lines.append(f"- 生成时间: {report['meta']['generated_at']}")
    lines.append(f"- 轮数 (repeat): {report['meta']['repeat']}")
    lines.append("")
    lines.append("## 聚合指标（N 轮均值 + 波动）")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    lines.append(f"| Incident Type Top1 | {_fmt_band(aggregate.get('top1_accuracy'))} |")
    lines.append(f"| Incident Type Top3 | {_fmt_band(aggregate.get('top3_accuracy'))} |")
    lines.append(f"| Macro F1 | {_fmt_band(aggregate.get('macro_f1'))} |")
    lines.append(f"| Unknown Rate | {_fmt_band(aggregate.get('unknown_rate'))} |")
    lines.append(f"| 风险准确率 | {_fmt_band(aggregate.get('risk_accuracy'))} |")
    lines.append(f"| 终态准确率 | {_fmt_band(aggregate.get('status_accuracy'))} |")
    lines.append(f"| 平均 confidence | {_fmt_band(aggregate.get('avg_confidence'))} |")
    lines.append(f"| 平均 latency(ms) | {_fmt_band(aggregate.get('avg_latency_ms'))} |")
    lines.append("")

    per_class = aggregate.get("last_round_per_class", {})
    if per_class:
        lines.append("## Per-class Recall（末轮）")
        lines.append("")
        lines.append("| 类别 | recall | precision | f1 | support |")
        lines.append("|------|--------|-----------|----|---------|")
        for class_name, metrics in sorted(per_class.items()):
            lines.append(
                f"| {class_name} | {_fmt(metrics['recall'])} | "
                f"{_fmt(metrics['precision'])} | {_fmt(metrics['f1'])} | "
                f"{metrics['support']} |"
            )
        lines.append("")

    confusion = aggregate.get("last_round_confusion_matrix", {})
    if confusion:
        lines.append("## Confusion Matrix / 混淆矩阵（末轮，行=expected 列=actual）")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(confusion, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    lines.append("## Hypothesis 抽查（首期只采集不评分）")
    lines.append("")
    last_round = report["rounds"][-1] if report["rounds"] else {"cases": []}
    for case in last_round["cases"]:
        error = case.get("error")
        if error:
            lines.append(f"- **{case['case_id']}** [ERROR] {error}")
        else:
            lines.append(
                f"- **{case['case_id']}** expected=`{_fmt(case['expected_type'])}` "
                f"actual=`{_fmt(case['actual_type'])}` conf={_fmt(case['confidence'])}: "
                f"{case.get('hypothesis') or '—'}"
            )
    lines.append("")
    return "\n".join(lines)


def write_report(report: Dict[str, Any], output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    out.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _fmt_band(band: Optional[Dict[str, Any]]) -> str:
    if not band or band.get("mean") is None:
        return "—"
    return f"{_fmt(band['mean'])} (min {_fmt(band['min'])} / max {_fmt(band['max'])})"
