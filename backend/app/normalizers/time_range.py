"""Time range normalization: fill defaults when missing."""

from datetime import datetime, timedelta
from typing import Dict, Optional


DEFAULT_LOOKBACK_HOURS = 1


def normalize_time_range(time_range: Optional[Dict] = None) -> Dict[str, datetime]:
    now = datetime.utcnow()
    default_start = now - timedelta(hours=DEFAULT_LOOKBACK_HOURS)

    if not time_range:
        return {"start": default_start, "end": now}

    start = time_range.get("start")
    end = time_range.get("end")

    if isinstance(start, str):
        try:
            start = datetime.fromisoformat(start)
        except ValueError:
            start = default_start
    if isinstance(end, str):
        try:
            end = datetime.fromisoformat(end)
        except ValueError:
            end = now

    if start is None:
        start = default_start
    if end is None:
        end = now

    return {"start": start, "end": end}
