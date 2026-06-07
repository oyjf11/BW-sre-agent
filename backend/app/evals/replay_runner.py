"""CLI entry point for replaying offline eval datasets."""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from app.evals.case_loader import load_cases
from app.evals.executors import DirectGraphExecutor, RunnerGraphExecutor
from app.evals.fixture_context import fixture_scope
from app.evals.report import build_report, render_markdown, write_report
from app.evals.runner import build_initial_state, run_dataset

_DEFAULT_DATASET = "app/evals/datasets/"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="replay_runner",
        description="OpsPilot offline eval",
    )
    parser.add_argument("--mode", choices=["direct", "runner", "compare"], default="direct")
    parser.add_argument("--dataset", default=_DEFAULT_DATASET)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--output", default=None, help="JSON report path")
    return parser


def make_executor(mode: str):
    if mode == "runner":
        return RunnerGraphExecutor()
    return DirectGraphExecutor()


def diff_compare(
    case_id: str,
    direct_state: Dict[str, Any],
    runner_state: Dict[str, Any],
) -> Dict[str, Any]:
    direct_type = _incident_type_of(direct_state)
    runner_type = _incident_type_of(runner_state)
    direct_status = _status_of(direct_state)
    runner_status = _status_of(runner_state)
    return {
        "case_id": case_id,
        "direct_incident_type": direct_type,
        "runner_incident_type": runner_type,
        "incident_type_match": direct_type == runner_type,
        "direct_status": direct_status,
        "runner_status": runner_status,
        "status_match": direct_status == runner_status,
    }


async def _run_async(args) -> int:
    _preflight_api_key()
    if args.mode == "compare":
        report = await _run_compare(args.dataset)
        print(
            f"[compare] {report['mismatch_count']} mismatched case(s) "
            f"of {len(report['diffs'])}"
        )
        if args.output:
            _write_compare_report(report, args.output)
        return 0

    executor = make_executor(args.mode)
    rounds_results, rounds_metrics, aggregate = await run_dataset(
        args.dataset,
        executor,
        repeat=args.repeat,
    )
    report = build_report(
        mode=args.mode,
        rounds_results=rounds_results,
        rounds_metrics=rounds_metrics,
        aggregate=aggregate,
    )
    print(render_markdown(report))
    if args.output:
        write_report(report, args.output)
        print(f"\n[replay_runner] report written to {args.output} (+ .md)")
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    return asyncio.run(_run_async(args))


async def _run_compare(dataset_path: str) -> Dict[str, Any]:
    cases = load_cases(dataset_path)
    direct = DirectGraphExecutor()
    runner = RunnerGraphExecutor()
    diffs = []

    for case in cases:
        fixtures = case.get("tool_fixtures", {}) or {}
        with fixture_scope(fixtures):
            direct_state = await direct.execute(case["case_id"], build_initial_state(case))
        with fixture_scope(fixtures):
            runner_state = await runner.execute(case["case_id"], build_initial_state(case))
        diffs.append(diff_compare(case["case_id"], direct_state, runner_state))

    return {
        "mode": "compare",
        "meta": {"real_llm": True, "ci_metric": False},
        "diffs": diffs,
        "mismatch_count": sum(
            1
            for diff in diffs
            if not (diff["incident_type_match"] and diff["status_match"])
        ),
    }


def _incident_type_of(state: Dict[str, Any]) -> Optional[str]:
    candidates = state.get("root_cause_candidates") or []
    if not candidates:
        return None
    top = candidates[0]
    incident_type = top.incident_type if hasattr(top, "incident_type") else top.get("incident_type")
    if incident_type is None:
        return None
    return incident_type.value if hasattr(incident_type, "value") else str(incident_type)


def _status_of(state: Dict[str, Any]) -> Optional[str]:
    status = state.get("status")
    if status is None:
        return None
    return status.value if hasattr(status, "value") else str(status)


def _preflight_api_key() -> None:
    provider = os.getenv("LLM_PROVIDER", "minimax").lower()
    key_env = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "minimax": "MINIMAX_API_KEY",
    }.get(provider)
    if key_env and not os.getenv(key_env):
        print(
            f"[replay_runner] ERROR: LLM_PROVIDER={provider} requires {key_env}.",
            file=sys.stderr,
        )
        sys.exit(2)


def _write_compare_report(report: Dict[str, Any], output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# OpsPilot 离线评测 Compare 报告",
        "",
        "> 本报告由**真实 LLM**生成，属**非 CI 指标**。",
        "",
        f"- mismatch_count: {report['mismatch_count']}",
        "",
        "```json",
        json.dumps(report["diffs"], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    out.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
