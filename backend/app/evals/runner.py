"""Orchestrate offline eval dataset runs."""
import time
from typing import Any, Dict, List, Tuple

from app.evals.case_loader import load_cases
from app.evals.fixture_context import fixture_scope
from app.evals.metrics import aggregate_rounds, compute_metrics
from app.evals.scorer import CaseResult, score_case
from app.models.incident import IncidentTicket


def build_initial_state(case: Dict[str, Any]) -> Dict[str, Any]:
    case_id = case["case_id"]
    return {
        "run_id": f"eval-{case_id}",
        "thread_id": f"eval-{case_id}",
        "ticket": IncidentTicket(**case["ticket"]),
        "evidence_items": [],
        "root_cause_candidates": [],
        "evidence_collection_results": [],
        "evidence_quality_score": 0.0,
        "step_count": 0,
    }


async def run_one_case(case: Dict[str, Any], executor) -> CaseResult:
    case_id = case["case_id"]
    fixtures = case.get("tool_fixtures", {}) or {}
    initial_state = build_initial_state(case)

    start = time.perf_counter()
    try:
        with fixture_scope(fixtures):
            final_state = await executor.execute(case_id, initial_state)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return score_case(case, final_state, latency_ms)
    except Exception as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return CaseResult.error_result(
            case_id,
            f"{type(exc).__name__}: {exc}",
            latency_ms,
        )


async def run_dataset(
    dataset_path: str,
    executor,
    repeat: int = 1,
) -> Tuple[List[List[CaseResult]], List[Dict[str, Any]], Dict[str, Any]]:
    cases = load_cases(dataset_path)
    rounds_results: List[List[CaseResult]] = []
    rounds_metrics: List[Dict[str, Any]] = []

    for _ in range(max(1, repeat)):
        case_results = [await run_one_case(case, executor) for case in cases]
        rounds_results.append(case_results)
        rounds_metrics.append(compute_metrics(case_results))

    aggregate = aggregate_rounds(rounds_metrics)
    return rounds_results, rounds_metrics, aggregate
