import asyncio
import logging
from typing import Any, Dict

from app.tools.clients.slb_client import SlbClientWrapper

logger = logging.getLogger(__name__)

RESPONSE_SIZE_LIMIT_KB = 64


async def query_lb_health_status(service: str, env: str, **kwargs) -> Dict[str, Any]:
    """Real adapter: query SLB backend server health status via Alibaba Cloud API."""
    client = SlbClientWrapper()
    lb_id = await asyncio.to_thread(client.find_load_balancer_id, service, env)

    if not lb_id:
        return {
            "service": service,
            "env": env,
            "status": "unknown",
            "healthy_hosts": 0,
            "unhealthy_hosts": 0,
            "health_check_path": "/healthz",
            "error": (
                f"No SLB instance found for service='{service}' env='{env}' "
                f"in region '{client.region_id}'"
            ),
        }

    result = await asyncio.to_thread(client.get_health_status, lb_id)
    result["service"] = service
    result["env"] = env
    result["response_size_limit_kb"] = RESPONSE_SIZE_LIMIT_KB
    return result


async def query_lb_traffic_metrics(
    service: str, env: str, window_minutes: int = 5, **kwargs
) -> Dict[str, Any]:
    """Real adapter: query SLB traffic metrics via Alibaba Cloud CMS API."""
    client = SlbClientWrapper()
    lb_id = await asyncio.to_thread(client.find_load_balancer_id, service, env)

    if not lb_id:
        return {
            "service": service,
            "env": env,
            "qps": 0.0,
            "error_rate": 0.0,
            "p50_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "window": f"{window_minutes}m",
            "metrics_available": False,
            "status": "unavailable",
            "error": (
                f"No SLB instance found for service='{service}' env='{env}' "
                f"in region '{client.region_id}'"
            ),
        }

    result = await asyncio.to_thread(client.get_traffic_metrics, lb_id, window_minutes)
    result["service"] = service
    result["env"] = env
    result["response_size_limit_kb"] = RESPONSE_SIZE_LIMIT_KB
    return result
