from typing import Dict, Any, List
from datetime import datetime
import time
import logging
import os
import inspect
from numbers import Integral
from tenacity import retry, stop_after_attempt, wait_exponential
from app.tracing import tracer

from app.tools.schemas import ToolRequest, ToolResponse, ToolMetadata, register_tool, TOOL_REGISTRY
from app.tools.adapters import query_logs as mock_query_logs
from app.tools.adapters import query_metrics as mock_query_metrics
from app.tools.adapters import query_deployments as mock_query_deployments
from app.tools.adapters import query_runbook as mock_query_runbook
from app.tools.adapters import execute_action as mock_execute_action
from app.tools.adapters import query_ticket_by_id as mock_query_ticket_by_id
from app.tools.adapters import query_service_metadata as mock_query_service_metadata
from app.tools.adapters import query_k8s_deployment_status as mock_query_k8s_deployment_status
from app.tools.adapters import query_k8s_pods as mock_query_k8s_pods
from app.tools.adapters import query_k8s_events as mock_query_k8s_events
from app.tools.adapters import query_k8s_pod_logs_summary as mock_query_k8s_pod_logs_summary
from app.tools.adapters import query_lb_health_status as mock_query_lb_health_status
from app.tools.adapters import query_lb_traffic_metrics as mock_query_lb_traffic_metrics
from app.tools.adapters import mock_query_db_processlist
from app.tools.adapters import mock_query_db_slow_queries
from app.tools.adapters import mock_query_db_table_status
from app.tools.adapters import mock_query_db_variables
from app.tools.adapters import mock_write_rca_to_oss
from app.tools.adapters import mock_write_evidence_to_oss
from app.tools.adapters.mysql_adapter import (
    query_db_processlist as real_query_db_processlist,
    query_db_slow_queries as real_query_db_slow_queries,
    query_db_table_status as real_query_db_table_status,
    query_db_variables as real_query_db_variables,
    query_logs_from_db as real_query_logs_from_db,
)
from app.tools.adapters.k8s_adapter import (
    query_k8s_deployment_status as real_query_k8s_deployment_status,
    query_k8s_pods as real_query_k8s_pods,
    query_k8s_events as real_query_k8s_events,
    query_k8s_pod_logs_summary as real_query_k8s_pod_logs_summary,
    query_deployments as real_query_deployments,
)
from app.tools.adapters.slb_adapter import (
    query_lb_health_status as real_query_lb_health_status,
    query_lb_traffic_metrics as real_query_lb_traffic_metrics,
)
from app.tools.adapters.oss_adapter import (
    write_rca_to_oss as real_write_rca_to_oss,
    write_evidence_to_oss as real_write_evidence_to_oss,
)
from app.tools.adapters.metrics_adapter import (
    query_metrics as real_query_metrics,
)

logger = logging.getLogger(__name__)

ADAPTER_MODE = os.getenv("TOOL_ADAPTER_MODE", "mock")

tool_handlers: Dict[str, Any] = {}

audit_log: List[Dict[str, Any]] = []


async def _real_adapter_not_configured(tool_name: str) -> Dict[str, Any]:
    raise RuntimeError(
        f"Real adapter '{tool_name}' is not configured. "
        "Install a concrete platform adapter before using TOOL_ADAPTER_MODE=real."
    )


async def get_real_query_logs(
    service: str, env: str, time_range: Dict = None, query: str = "*", limit: int = 100
):
    return await _real_adapter_not_configured("query_logs")


async def get_real_query_metrics(
    service: str, env: str, time_range: Dict = None, metric_names: List = None
):
    return await _real_adapter_not_configured("query_metrics")


async def get_real_query_deployments(service: str, env: str, time_range: Dict = None):
    return await _real_adapter_not_configured("query_deployments")


async def get_real_query_runbook(service: str, env: str, incident_type: str = None):
    return await _real_adapter_not_configured("query_runbook")


async def get_real_execute_action(
    action_type: str, service: str, env: str, params: Dict = None, idempotency_key: str = None
):
    return await _real_adapter_not_configured("execute_action")


def select_adapter(tool_name: str):
    """Select mock or real adapter based on environment."""
    if ADAPTER_MODE == "real":
        if tool_name == "query_logs":
            return real_query_logs_from_db
        elif tool_name == "query_metrics":
            return real_query_metrics
        elif tool_name == "query_deployments":
            return real_query_deployments
        elif tool_name == "query_runbook":
            return get_real_query_runbook
        elif tool_name == "execute_action":
            return get_real_execute_action
        elif tool_name == "query_db_processlist":
            return real_query_db_processlist
        elif tool_name == "query_db_slow_queries":
            return real_query_db_slow_queries
        elif tool_name == "query_db_table_status":
            return real_query_db_table_status
        elif tool_name == "query_db_variables":
            return real_query_db_variables
        elif tool_name == "query_k8s_deployment_status":
            return real_query_k8s_deployment_status
        elif tool_name == "query_k8s_pods":
            return real_query_k8s_pods
        elif tool_name == "query_k8s_events":
            return real_query_k8s_events
        elif tool_name == "query_k8s_pod_logs_summary":
            return real_query_k8s_pod_logs_summary
        elif tool_name == "query_lb_health_status":
            return real_query_lb_health_status
        elif tool_name == "query_lb_traffic_metrics":
            return real_query_lb_traffic_metrics
        elif tool_name == "write_rca_to_oss":
            return real_write_rca_to_oss
        elif tool_name == "write_evidence_to_oss":
            return real_write_evidence_to_oss
    return None


def register_handler(name: str, handler: Any):
    tool_handlers[name] = handler


register_handler("query_logs", mock_query_logs)
register_handler("query_metrics", mock_query_metrics)
register_handler("query_deployments", mock_query_deployments)
register_handler("query_runbook", mock_query_runbook)
register_handler("execute_action", mock_execute_action)
register_handler("query_ticket_by_id", mock_query_ticket_by_id)
register_handler("query_service_metadata", mock_query_service_metadata)
register_handler("query_k8s_deployment_status", mock_query_k8s_deployment_status)
register_handler("query_k8s_pods", mock_query_k8s_pods)
register_handler("query_k8s_events", mock_query_k8s_events)
register_handler("query_k8s_pod_logs_summary", mock_query_k8s_pod_logs_summary)
register_handler("query_lb_health_status", mock_query_lb_health_status)
register_handler("query_lb_traffic_metrics", mock_query_lb_traffic_metrics)
register_handler("query_db_processlist", mock_query_db_processlist)
register_handler("query_db_slow_queries", mock_query_db_slow_queries)
register_handler("query_db_table_status", mock_query_db_table_status)
register_handler("query_db_variables", mock_query_db_variables)
register_handler("write_rca_to_oss", mock_write_rca_to_oss)
register_handler("write_evidence_to_oss", mock_write_evidence_to_oss)

register_tool(
    ToolMetadata(
        name="query_logs",
        description="Query logs from a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "time_range": {"type": "object"},
                "query": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_metrics",
        description="Query metrics from a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "time_range": {"type": "object"},
                "metric_names": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_deployments",
        description="Query deployment history",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "time_range": {"type": "object"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_runbook",
        description="Query runbook for a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "incident_type": {"type": "string"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="execute_action",
        description="Execute an action on a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "action_type": {"type": "string"},
                "service": {"type": "string"},
                "env": {"type": "string"},
                "params": {"type": "object"},
                "idempotency_key": {"type": "string"},
            },
            "required": ["action_type", "service", "env"],
        },
        risk_level="HIGH",
        requires_approval=True,
        timeout_ms=60000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_ticket_by_id",
        description="Look up an incident ticket by its ID",
        parameters_schema={
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
            },
            "required": ["ticket_id"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=10000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_service_metadata",
        description="Retrieve service metadata for precondition checks",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=10000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_k8s_deployment_status",
        description="Query Kubernetes deployment status for a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
                "deployment_name": {"type": "string"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_k8s_pods",
        description="Query Kubernetes pods for a service deployment",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
                "deployment_name": {"type": "string"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_k8s_events",
        description="Query Kubernetes events for a service deployment",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
                "deployment_name": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_k8s_pod_logs_summary",
        description="Query summarized Kubernetes pod logs for a service deployment",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
                "deployment_name": {"type": "string"},
                "tail_lines": {"type": "integer"},
                "limit_pods": {"type": "integer"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_lb_health_status",
        description="Query load balancer health status for a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_lb_traffic_metrics",
        description="Query load balancer traffic metrics (QPS, error rate, latency)",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "window_minutes": {"type": "integer"},
            },
            "required": ["service", "env"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_db_processlist",
        description="Query active MySQL connections and lock waits (filters Sleep state)",
        parameters_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_db_slow_queries",
        description="Query slow running queries from MySQL processlist",
        parameters_schema={
            "type": "object",
            "properties": {
                "threshold_seconds": {"type": "integer", "default": 5},
            },
            "required": [],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_db_table_status",
        description="Query MySQL table status (row count, size, fragmentation)",
        parameters_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="query_db_variables",
        description="Query key MySQL status variables (connections, buffer pool, lock waits)",
        parameters_schema={
            "type": "object",
            "properties": {},
            "required": [],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=15000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="write_rca_to_oss",
        description="Write RCA report markdown to Alibaba Cloud OSS for archival",
        parameters_schema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "service": {"type": "string"},
                "env": {"type": "string"},
                "content": {"type": "string"},
                "content_type": {"type": "string"},
            },
            "required": ["run_id", "content"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)

register_tool(
    ToolMetadata(
        name="write_evidence_to_oss",
        description="Write evidence bundle JSON to Alibaba Cloud OSS for archival",
        parameters_schema={
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "service": {"type": "string"},
                "env": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["run_id", "content"],
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
        retries=1,
    )
)


class ToolGateway:
    def __init__(self):
        self.handlers = tool_handlers
        self.registry = TOOL_REGISTRY
        self.audit_log = audit_log
        self.adapter_mode = ADAPTER_MODE
        logger.info(f"ToolGateway initialized with adapter mode: {ADAPTER_MODE}")

    async def call_tool(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        span_id = tracer.start_span(
            f"tool.{request.tool_name}",
            run_id=request.run_id,
            parent_id=tracer.get_active_span_id(),
        )
        tracer.add_event(span_id, "tool_called", {"params": request.params})

        if request.tool_name not in self.handlers:
            tracer.end_span(span_id, status="error", error="tool_not_found")
            return ToolResponse(
                tool_name=request.tool_name,
                success=False,
                error=f"Tool '{request.tool_name}' not found",
                latency_ms=int((time.time() - start_time) * 1000),
            )

        metadata = self.registry.get(request.tool_name)
        validation_error = self._validate_params(request.params, metadata)
        if validation_error:
            latency = int((time.time() - start_time) * 1000)
            tracer.end_span(span_id, status="error", error=validation_error)
            return ToolResponse(
                tool_name=request.tool_name,
                success=False,
                error=validation_error,
                latency_ms=latency,
            )

        real_handler = select_adapter(request.tool_name)
        if real_handler and ADAPTER_MODE == "real":
            handler = real_handler
            adapter_info = "real"
        else:
            handler = self.handlers[request.tool_name]
            adapter_info = "mock"

        try:
            result = await self._execute_with_retry(handler, request.params, metadata)
            if isinstance(result, dict):
                result["_adapter_info"] = adapter_info

            latency = int((time.time() - start_time) * 1000)
            self._log_audit(request, latency, True, result, adapter_info=adapter_info)
            tracer.add_event(
                span_id,
                "tool_succeeded",
                {"adapter": adapter_info, "latency_ms": latency},
            )
            tracer.end_span(span_id, status="ok")

            return ToolResponse(
                tool_name=request.tool_name,
                success=True,
                result=result,
                latency_ms=latency,
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            error_result = {"error": str(e)}
            self._log_audit(request, latency, False, error_result, adapter_info=adapter_info)
            tracer.end_span(span_id, status="error", error=str(e))

            return ToolResponse(
                tool_name=request.tool_name,
                success=False,
                error=str(e),
                latency_ms=latency,
            )

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _execute_with_retry(
        self,
        handler: Any,
        params: Dict[str, Any],
        metadata: ToolMetadata,
    ) -> Dict[str, Any]:
        result = handler(**params)
        if inspect.isawaitable(result):
            return await result
        return result

    def _validate_params(self, params: Dict[str, Any], metadata: ToolMetadata) -> str:
        schema = metadata.parameters_schema if metadata else {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for key in required:
            if key not in params:
                return f"Missing required parameter: {key}"

        for key, value in params.items():
            if key not in properties:
                continue

            expected_type = properties[key].get("type")
            if expected_type == "string" and not isinstance(value, str):
                return f"Invalid parameter '{key}': expected string"
            if expected_type == "integer" and not isinstance(value, Integral):
                return f"Invalid parameter '{key}': expected integer"
            if expected_type == "object" and not isinstance(value, dict):
                return f"Invalid parameter '{key}': expected object"
            if expected_type == "array" and not isinstance(value, list):
                return f"Invalid parameter '{key}': expected array"

        return ""

    def _log_audit(
        self,
        request: ToolRequest,
        latency_ms: int,
        success: bool,
        result: Dict[str, Any],
        adapter_info: str = "unknown",
    ):
        entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": request.run_id,
            "tool_name": request.tool_name,
            "params": request.params,
            "adapter": adapter_info,
            "latency_ms": latency_ms,
            "success": success,
            "result": result if success else None,
            "error": result.get("error") if not success else None,
        }
        self.audit_log.append(entry)
        logger.info(f"Tool audit: {entry}")

    def get_audit_log(self, run_id: str = None) -> List[Dict[str, Any]]:
        if run_id:
            return [e for e in self.audit_log if e.get("run_id") == run_id]
        return self.audit_log


gateway = ToolGateway()
