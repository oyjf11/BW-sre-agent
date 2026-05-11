import json
import logging
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    from alibabacloud_slb20140515.client import Client as SlbClient
    from alibabacloud_slb20140515 import models as slb_models
    from alibabacloud_tea_openapi import models as open_api_models
except ModuleNotFoundError:  # pragma: no cover - exercised through adapter fallback
    SlbClient = None
    slb_models = None
    open_api_models = None

try:
    from alibabacloud_cms20190101.client import Client as CmsClient
    from alibabacloud_cms20190101 import models as cms_models
except ModuleNotFoundError:  # pragma: no cover
    CmsClient = None
    cms_models = None


SLB_CMS_NAMESPACE = "acs_slb_dashboard"


@lru_cache(maxsize=1)
def _create_slb_client(
    access_key_id: str,
    access_key_secret: str,
    region_id: str,
) -> Any:
    if SlbClient is None:
        raise RuntimeError("alibabacloud-slb20140515 package is not installed")

    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        region_id=region_id,
    )
    config.endpoint = f"slb.{region_id}.aliyuncs.com"
    return SlbClient(config)


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


class SlbClientWrapper:
    def __init__(
        self,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        region_id: Optional[str] = None,
    ):
        settings = get_settings()
        self.access_key_id = access_key_id or settings.alibaba_access_key_id
        self.access_key_secret = access_key_secret or settings.alibaba_access_key_secret
        self.region_id = region_id or settings.alibaba_region_id

        if not self.access_key_id or not self.access_key_secret:
            raise RuntimeError(
                "ALIBABA_ACCESS_KEY_ID and ALIBABA_ACCESS_KEY_SECRET are required "
                "for real SLB adapter"
            )

    def _get_client(self) -> Any:
        return _create_slb_client(
            self.access_key_id,
            self.access_key_secret,
            self.region_id,
        )

    def find_load_balancer_id(self, service: str, env: str = "") -> Optional[str]:
        """Find an SLB instance by service+env (via tag or loadBalancerName)."""
        client = self._get_client()

        # Strategy 1: tag filtering (Service + Env)
        tags = [slb_models.DescribeLoadBalancersRequestTag(key="Service", value=service)]
        if env:
            tags.append(slb_models.DescribeLoadBalancersRequestTag(key="Env", value=env))

        request = slb_models.DescribeLoadBalancersRequest()
        request.tag = tags
        request.region_id = self.region_id

        response = client.describe_load_balancers(request)
        lbs = response.body.load_balancers.load_balancer or []
        if lbs:
            return lbs[0].load_balancer_id

        # Strategy 2: fallback — search all LBs and match by name containing service+env
        request_all = slb_models.DescribeLoadBalancersRequest()
        request_all.region_id = self.region_id
        response_all = client.describe_load_balancers(request_all)
        all_lbs = response_all.body.load_balancers.load_balancer or []

        for lb in all_lbs:
            lb_name = (getattr(lb, "load_balancer_name", "") or "").lower()
            svc_lower = service.lower()
            env_lower = env.lower() if env else ""

            if svc_lower in lb_name:
                if not env_lower or env_lower in lb_name:
                    return lb.load_balancer_id

        # Strategy 3: match by service only (env not found) — only allowed when env is NOT set
        if not env:
            for lb in all_lbs:
                lb_name = (getattr(lb, "load_balancer_name", "") or "").lower()
                if service.lower() in lb_name:
                    return lb.load_balancer_id

        return None

    def get_health_status(self, load_balancer_id: str) -> Dict[str, Any]:
        """Query backend server health status for an SLB instance."""
        client = self._get_client()
        request = slb_models.DescribeHealthStatusRequest()
        request.load_balancer_id = load_balancer_id

        response = client.describe_health_status(request)
        backend_servers = response.body.backend_servers.backend_server or []

        healthy = 0
        unhealthy = 0
        health_check_path = ""
        server_details = []

        for server in backend_servers:
            server_health_status = getattr(server, "server_health_status", "unavailable")
            if server_health_status == "normal":
                healthy += 1
            else:
                unhealthy += 1

            listener_port = getattr(server, "listener_port", 0) or 0
            server_id = getattr(server, "server_id", "") or ""
            server_details.append({
                "server_id": server_id,
                "port": listener_port,
                "health_status": server_health_status,
            })

            if not health_check_path:
                hc_status = getattr(server, "health_check_status", None)
                if hc_status:
                    health_check_path = getattr(hc_status, "health_check", "") or "/healthz"

        status = (
            "healthy" if unhealthy == 0 and healthy > 0
            else "degraded" if healthy > 0
            else "unavailable"
        )

        return {
            "load_balancer_id": load_balancer_id,
            "status": status,
            "healthy_hosts": healthy,
            "unhealthy_hosts": unhealthy,
            "health_check_path": health_check_path or "/healthz",
            "backend_servers": server_details,
        }

    def get_load_balancer_attribute(self, load_balancer_id: str) -> Dict[str, Any]:
        """Query load balancer attribute for basic info."""
        client = self._get_client()
        request = slb_models.DescribeLoadBalancerAttributeRequest()
        request.load_balancer_id = load_balancer_id

        response = client.describe_load_balancer_attribute(request)
        body = response.body

        bandwidth = getattr(body, "bandwidth", 0) or 0
        address = getattr(body, "address", "") or ""
        lb_status = getattr(body, "load_balancer_status", "inactive") or "inactive"

        listener_ports = getattr(body, "listener_ports", None)
        port_list = getattr(listener_ports, "listener_port", []) if listener_ports else []

        return {
            "load_balancer_id": load_balancer_id,
            "address": address,
            "bandwidth_mbps": bandwidth,
            "status": lb_status,
            "listener_ports": port_list,
        }

    def _query_cms_metric(
        self, lb_id: str, metric_name: str, window_minutes: int
    ) -> Optional[float]:
        """Query a single CloudMonitor metric for the given SLB instance.

        Returns the average value over the window, or None if unavailable.
        """
        if CmsClient is None or cms_models is None:
            logger.debug("CMS SDK not installed, skipping metric query")
            return None

        cms_client = _create_cms_client(
            self.access_key_id, self.access_key_secret, self.region_id
        )
        now = datetime.now(timezone.utc)
        start = (now - timedelta(minutes=max(1, window_minutes))).strftime("%Y-%m-%dT%H:%M:%SZ")
        end = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        request = cms_models.DescribeMetricDataRequest()
        request.namespace = SLB_CMS_NAMESPACE
        request.metric_name = metric_name
        request.dimensions = f'[{{"instanceId":"{lb_id}"}}]'
        request.start_time = start
        request.end_time = end
        request.period = str(max(60, window_minutes * 60))

        try:
            response = cms_client.describe_metric_data(request)
        except Exception as e:
            logger.warning(f"CMS API call failed for metric={metric_name} lb={lb_id}: {e}")
            return None

        if getattr(response.body, "code", "") != "200":
            logger.warning(
                f"CMS returned non-200 for metric={metric_name} lb={lb_id}: "
                f"code={getattr(response.body, 'code', 'unknown')}"
            )
            return None

        datapoints_str = getattr(response.body, "datapoints", None)
        return self._parse_and_avg(datapoints_str)

    @staticmethod
    def _parse_and_avg(datapoints_str: str) -> Optional[float]:
        """Parse CMS datapoints JSON string and compute the average value."""
        if not datapoints_str or datapoints_str == "[]":
            return None
        try:
            points = json.loads(datapoints_str)
        except (json.JSONDecodeError, TypeError):
            return None
        if not isinstance(points, list) or len(points) == 0:
            return None
        values = []
        for p in points:
            if not isinstance(p, dict):
                continue
            val = p.get("Average") or p.get("Value")
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    continue
        return sum(values) / len(values) if values else None

    def get_traffic_metrics(
        self, load_balancer_id: str, window_minutes: int = 5
    ) -> Dict[str, Any]:
        """Get traffic metrics for an SLB instance via CloudMonitor (CMS) API.

        Queries acs_slb_dashboard namespace for QPS, latency, and HTTP status codes.
        Sets metrics_available=false when CMS is unreachable or returns no data.
        """
        attr = self.get_load_balancer_attribute(load_balancer_id)

        qps = self._query_cms_metric(load_balancer_id, "InstanceQps", window_minutes)
        rt = self._query_cms_metric(load_balancer_id, "InstanceRt", window_minutes)
        code_2xx = self._query_cms_metric(load_balancer_id, "InstanceStatusCode2xx", window_minutes)
        code_3xx = self._query_cms_metric(load_balancer_id, "InstanceStatusCode3xx", window_minutes)
        code_4xx = self._query_cms_metric(load_balancer_id, "InstanceStatusCode4xx", window_minutes)
        code_5xx = self._query_cms_metric(load_balancer_id, "InstanceStatusCode5xx", window_minutes)

        all_metrics = [qps, rt, code_2xx, code_3xx, code_4xx, code_5xx]
        any_available = any(v is not None for v in all_metrics)

        # Status code metrics are required for meaningful traffic health verification.
        # Having QPS/Rt without code metrics cannot determine error_rate.
        code_metrics = [code_2xx, code_3xx, code_4xx, code_5xx]
        code_metrics_available = any(v is not None for v in code_metrics)

        # Calculate error_rate = 5xx / (2xx+3xx+4xx+5xx)
        total_codes = sum(v for v in code_metrics if v is not None)
        error_rate = None
        if total_codes and total_codes > 0 and code_5xx is not None:
            error_rate = round(code_5xx / total_codes, 6)

        return {
            "load_balancer_id": load_balancer_id,
            "address": attr["address"],
            "bandwidth_mbps": attr["bandwidth_mbps"],
            "status": "active" if any_available else "unavailable",
            "qps": round(qps, 2) if qps is not None else 0.0,
            "error_rate": error_rate if error_rate is not None else 0.0,
            "p50_latency_ms": round(rt, 2) if rt is not None else 0.0,
            "p99_latency_ms": round(rt, 2) if rt is not None else 0.0,
            "window": f"{window_minutes}m",
            "metrics_available": any_available and code_metrics_available,
        }
