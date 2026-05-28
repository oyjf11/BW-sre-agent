import asyncio
import logging
from typing import Any, Dict

from app.tools.clients.oss_client import OssClientWrapper

logger = logging.getLogger(__name__)

RESPONSE_SIZE_LIMIT_KB = 64

EXT_MAP = {
    "markdown": "md",
    "json": "json",
}


async def write_rca_to_oss(
    run_id: str,
    service: str = "",
    env: str = "",
    content: str = "",
    content_type: str = "markdown",
    **kwargs,
) -> Dict[str, Any]:
    """Real adapter: write RCA report to Alibaba Cloud OSS."""
    ext = EXT_MAP.get(content_type, "md")
    svc_part = service or "unknown"
    key = f"rca/{svc_part}/{run_id}.{ext}"

    client = OssClientWrapper()
    result = await asyncio.to_thread(client.put_object, key, content)

    return {
        "run_id": run_id,
        "service": service,
        "env": env,
        "oss_key": key,
        "oss_url": result.get("oss_url", ""),
        "bucket": result.get("bucket", client.bucket_name),
        "content_type": content_type,
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def write_evidence_to_oss(
    run_id: str,
    service: str = "",
    env: str = "",
    content: str = "",
    **kwargs,
) -> Dict[str, Any]:
    """Real adapter: write evidence bundle JSON to Alibaba Cloud OSS."""
    svc_part = service or "unknown"
    key = f"evidence/{svc_part}/{run_id}.json"

    client = OssClientWrapper()
    result = await asyncio.to_thread(client.put_object, key, content)

    return {
        "run_id": run_id,
        "service": service,
        "env": env,
        "oss_key": key,
        "oss_url": result.get("oss_url", ""),
        "bucket": result.get("bucket", client.bucket_name),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }
