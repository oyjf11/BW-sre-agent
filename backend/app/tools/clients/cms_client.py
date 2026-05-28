import json
import logging
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    from alibabacloud_cms20190101.client import Client as CmsClient
    from alibabacloud_cms20190101 import models as cms_models
    from alibabacloud_tea_openapi import models as open_api_models
except ModuleNotFoundError:  # pragma: no cover
    CmsClient = None
    cms_models = None
    open_api_models = None


CMS_NAMESPACE = "acs_k8s"

METRIC_MAP = {
    "cpu_usage": "cluster.cpu.utilization",
    "memory_usage": "cluster.memory.utilization",
    "cpu_request": "cluster.cpu.request",
    "memory_request": "cluster.memory.request",
    "cpu_limit": "cluster.cpu.limit",
    "memory_limit": "cluster.memory.limit",
    "disk_usage": "cluster.filesystem.usage",
    "disk_available": "cluster.filesystem.available",
    "network_rx": "cluster.network.rx.rate",
    "network_tx": "cluster.network.tx.rate",
}


@lru_cache(maxsize=1)
def _create_cms_client(
    access_key_id: str,
    access_key_secret: str,
    region_id: str,
) -> Any:
    if CmsClient is None:
        raise RuntimeError("alibabacloud-cms20190101 package is not installed")

    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
    )
    config.endpoint = f"metrics.{region_id}.aliyuncs.com"
    return CmsClient(config)


class MetricsClient:
    def __init__(
        self,
        cluster_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        region_id: Optional[str] = None,
    ):
        settings = get_settings()
        self.cluster_id = cluster_id or settings.k8s_cluster_id
        self.access_key_id = access_key_id or settings.alibaba_access_key_id
        self.access_key_secret = access_key_secret or settings.alibaba_access_key_secret
        self.region_id = region_id or settings.alibaba_region_id

        if not self.cluster_id:
            raise RuntimeError(
                "K8S_CLUSTER_ID is required for real metrics adapter"
            )

    def _get_client(self) -> Any:
        return _create_cms_client(
            self.access_key_id,
            self.access_key_secret,
            self.region_id,
        )

    def query_metric(
        self,
        metric_name: str,
        dimension_key: str = "cluster",
        dimension_value: str = "",
        window_minutes: int = 30,
        period: int = 300,
    ) -> Optional[Dict[str, Any]]:
        cms_metric = METRIC_MAP.get(metric_name, metric_name)

        client = self._get_client()
        now = datetime.now(timezone.utc)
        start = (now - timedelta(minutes=max(1, window_minutes))).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        dimensions = json.dumps([{dimension_key: dimension_value or self.cluster_id}])

        request = cms_models.DescribeMetricDataRequest()
        request.namespace = CMS_NAMESPACE
        request.metric_name = cms_metric
        request.dimensions = dimensions
        request.start_time = start
        request.end_time = end
        request.period = str(max(60, period))

        try:
            response = client.describe_metric_data(request)
        except Exception as e:
            logger.warning(f"CMS metric query failed: metric={cms_metric}, error={e}")
            return None

        if getattr(response.body, "code", "") != "200":
            return None

        datapoints_str = getattr(response.body, "datapoints", None)
        values = self._parse_datapoints(datapoints_str)

        return {
            "values": values,
            "unit": "%" if "utilization" in metric_name or "usage" in metric_name else "bytes",
            "metric_name": metric_name,
            "window": f"{window_minutes}m",
        }

    @staticmethod
    def _parse_datapoints(datapoints_str: str) -> List[Dict[str, Any]]:
        if not datapoints_str or datapoints_str == "[]":
            return []
        try:
            points = json.loads(datapoints_str)
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(points, list):
            return []
        result = []
        for p in points:
            if not isinstance(p, dict):
                continue
            ts = p.get("timestamp")
            val = p.get("Average") or p.get("Value")
            if val is not None:
                try:
                    result.append({
                        "timestamp": ts,
                        "value": float(val),
                    })
                except (ValueError, TypeError):
                    pass
        return result
