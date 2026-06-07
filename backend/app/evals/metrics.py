"""Aggregate CaseResult objects into offline eval metrics."""
from typing import Any, Dict, List, Optional

from app.evals.scorer import CaseResult


def compute_metrics(results: List[CaseResult]) -> Dict[str, Any]:
    scored = [result for result in results if result.error is None]
    errored = [result for result in results if result.error is not None]

    pairs = [
        (result.expected_type, result.actual_type)
        for result in scored
        if result.expected_type is not None
    ]
    confusion: Dict[str, Dict[str, int]] = {}
    for expected, actual in pairs:
        actual_key = actual if actual is not None else "<none>"
        confusion.setdefault(expected, {})
        confusion[expected][actual_key] = confusion[expected].get(actual_key, 0) + 1

    classes = sorted(
        {expected for expected, _ in pairs}
        | {actual for _, actual in pairs if actual is not None}
    )
    per_class: Dict[str, Dict[str, float]] = {}
    for class_name in classes:
        true_positive = sum(
            1 for expected, actual in pairs if expected == class_name and actual == class_name
        )
        false_positive = sum(
            1 for expected, actual in pairs if expected != class_name and actual == class_name
        )
        false_negative = sum(
            1 for expected, actual in pairs if expected == class_name and actual != class_name
        )
        precision = (
            true_positive / (true_positive + false_positive)
            if (true_positive + false_positive)
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if (true_positive + false_negative)
            else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )
        per_class[class_name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(1 for expected, _ in pairs if expected == class_name),
        }

    expected_classes = [
        class_name for class_name in classes if any(e == class_name for e, _ in pairs)
    ]
    macro_f1 = (
        round(
            sum(per_class[class_name]["f1"] for class_name in expected_classes)
            / len(expected_classes),
            4,
        )
        if expected_classes
        else None
    )

    actual_types = [result.actual_type for result in scored if result.actual_type is not None]
    unknown_rate = (
        round(
            sum(1 for actual_type in actual_types if actual_type == "unknown")
            / len(actual_types),
            4,
        )
        if actual_types
        else None
    )

    return {
        "case_count": len(results),
        "scored_count": len(scored),
        "error_count": len(errored),
        "error_cases": [result.case_id for result in errored],
        "top1_accuracy": _accuracy([result.hit_top1 for result in scored]),
        "top3_accuracy": _accuracy([result.hit_top3 for result in scored]),
        "risk_accuracy": _accuracy([result.risk_match for result in scored]),
        "status_accuracy": _accuracy([result.status_match for result in scored]),
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": confusion,
        "unknown_rate": unknown_rate,
        "avg_confidence": _safe_mean([result.confidence for result in scored]),
        "avg_latency_ms": _safe_mean(
            [
                float(result.latency_ms)
                for result in scored
                if result.latency_ms is not None
            ]
        ),
    }


_SCALAR_KEYS = (
    "top1_accuracy",
    "top3_accuracy",
    "risk_accuracy",
    "status_accuracy",
    "macro_f1",
    "unknown_rate",
    "avg_confidence",
    "avg_latency_ms",
)


def aggregate_rounds(round_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    agg: Dict[str, Any] = {"rounds": len(round_metrics)}
    for key in _SCALAR_KEYS:
        values = [metric[key] for metric in round_metrics if metric.get(key) is not None]
        if values:
            agg[key] = {
                "mean": round(sum(values) / len(values), 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
            }
        else:
            agg[key] = {"mean": None, "min": None, "max": None}

    if round_metrics:
        agg["last_round_confusion_matrix"] = round_metrics[-1]["confusion_matrix"]
        agg["last_round_per_class"] = round_metrics[-1]["per_class"]

    return agg


def _safe_mean(values: List[Optional[float]]) -> Optional[float]:
    vals = [value for value in values if value is not None]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 4)


def _accuracy(flags: List[Optional[bool]]) -> Optional[float]:
    graded = [flag for flag in flags if flag is not None]
    if not graded:
        return None
    return round(sum(1 for flag in graded if flag) / len(graded), 4)
