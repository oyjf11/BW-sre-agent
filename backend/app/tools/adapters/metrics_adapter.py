import asyncio
import logging
from typing import Any, Dict, List

from app.tools.clients.cms_client import MetricsClient, METRIC_MAP

logger = logging.getLogger(__name__)

RESPONSE_SIZE_LIMIT_KB = 64

SUPPORTED_METRICS = list(METRIC_MAP.keys())


async def query_metrics(
    service: str,
    env: str,
    time_range: Dict[str, str] = None,
    metric_names: List[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    client = MetricsClient()

    if metric_names is None:
        metric_names = ["cpu_usage", "memory_usage"]

    valid_names = [n for n in metric_names if n in METRIC_MAP]
    if not valid_names:
        valid_names = ["cpu_usage", "memory_usage"]

    metrics = {}
    for name in valid_names:
        result = await asyncio.to_thread(
            client.query_metric,
            metric_name=name,
            window_minutes=30,
            period=300,
        )
        metrics[name] = result if result else {
            "values": [],
            "unit": "unknown",
            "metric_name": name,
            "window": "30m",
        }

    return {
        "metrics": metrics,
        "service": service,
        "env": env,
        "supported_metrics": SUPPORTED_METRICS,
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }
