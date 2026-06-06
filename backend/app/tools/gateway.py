from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import logging
import inspect
import json
import re
import uuid
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
from app.tools.adapters import query_k8s_nodes as mock_query_k8s_nodes
from app.tools.adapters import query_k8s_services as mock_query_k8s_services
from app.tools.adapters import query_k8s_hpa as mock_query_k8s_hpa
from app.tools.adapters import query_k8s_ingresses as mock_query_k8s_ingresses
from app.tools.adapters import query_k8s_statefulsets as mock_query_k8s_statefulsets
from app.tools.adapters import query_k8s_daemonsets as mock_query_k8s_daemonsets
from app.tools.adapters import query_k8s_configmaps as mock_query_k8s_configmaps
from app.tools.adapters import query_k8s_resource_quotas as mock_query_k8s_resource_quotas
from app.tools.adapters import query_k8s_pvc as mock_query_k8s_pvc
from app.tools.adapters import query_k8s_replicasets as mock_query_k8s_replicasets
from app.tools.adapters import query_k8s_jobs as mock_query_k8s_jobs
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
    query_k8s_nodes as real_query_k8s_nodes,
    query_k8s_services as real_query_k8s_services,
    query_k8s_hpa as real_query_k8s_hpa,
    query_k8s_ingresses as real_query_k8s_ingresses,
    query_k8s_statefulsets as real_query_k8s_statefulsets,
    query_k8s_daemonsets as real_query_k8s_daemonsets,
    query_k8s_configmaps as real_query_k8s_configmaps,
    query_k8s_resource_quotas as real_query_k8s_resource_quotas,
    query_k8s_pvc as real_query_k8s_pvc,
    query_k8s_replicasets as real_query_k8s_replicasets,
    query_k8s_jobs as real_query_k8s_jobs,
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

from app.core.config import get_settings

ADAPTER_MODE = get_settings().tool_adapter_mode

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


async def get_real_query_ticket_by_id(ticket_id: str):
    return await _real_adapter_not_configured("query_ticket_by_id")


async def get_real_query_service_metadata(service: str, env: str):
    return await _real_adapter_not_configured("query_service_metadata")


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
        elif tool_name == "query_ticket_by_id":
            return get_real_query_ticket_by_id
        elif tool_name == "query_service_metadata":
            return get_real_query_service_metadata
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
        elif tool_name == "query_k8s_nodes":
            return real_query_k8s_nodes
        elif tool_name == "query_k8s_services":
            return real_query_k8s_services
        elif tool_name == "query_k8s_hpa":
            return real_query_k8s_hpa
        elif tool_name == "query_k8s_ingresses":
            return real_query_k8s_ingresses
        elif tool_name == "query_k8s_statefulsets":
            return real_query_k8s_statefulsets
        elif tool_name == "query_k8s_daemonsets":
            return real_query_k8s_daemonsets
        elif tool_name == "query_k8s_configmaps":
            return real_query_k8s_configmaps
        elif tool_name == "query_k8s_resource_quotas":
            return real_query_k8s_resource_quotas
        elif tool_name == "query_k8s_pvc":
            return real_query_k8s_pvc
        elif tool_name == "query_k8s_replicasets":
            return real_query_k8s_replicasets
        elif tool_name == "query_k8s_jobs":
            return real_query_k8s_jobs
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
register_handler("query_k8s_nodes", mock_query_k8s_nodes)
register_handler("query_k8s_services", mock_query_k8s_services)
register_handler("query_k8s_hpa", mock_query_k8s_hpa)
register_handler("query_k8s_ingresses", mock_query_k8s_ingresses)
register_handler("query_k8s_statefulsets", mock_query_k8s_statefulsets)
register_handler("query_k8s_daemonsets", mock_query_k8s_daemonsets)
register_handler("query_k8s_configmaps", mock_query_k8s_configmaps)
register_handler("query_k8s_resource_quotas", mock_query_k8s_resource_quotas)
register_handler("query_k8s_pvc", mock_query_k8s_pvc)
register_handler("query_k8s_replicasets", mock_query_k8s_replicasets)
register_handler("query_k8s_jobs", mock_query_k8s_jobs)
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
        name="query_k8s_nodes",
        description="Query Kubernetes node status, capacity, and conditions (MemoryPressure, DiskPressure, PIDPressure)",
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
        name="query_k8s_services",
        description="Query Kubernetes Service and Endpoint health for a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_hpa",
        description="Query HorizontalPodAutoscaler status for a deployment (current/desired replicas, resource utilization)",
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
        name="query_k8s_ingresses",
        description="Query Kubernetes Ingress rules, hosts, TLS config for a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_statefulsets",
        description="Query Kubernetes StatefulSet status for a service (replicas, revision, health)",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_daemonsets",
        description="Query Kubernetes DaemonSet status for a service (desired/available/ready)",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_configmaps",
        description="Query Kubernetes ConfigMap keys and data sample for a service (sensitive values redacted)",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_resource_quotas",
        description="Query Kubernetes ResourceQuota hard limits and used resources in a namespace",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_pvc",
        description="Query Kubernetes PersistentVolumeClaim status and capacity matching a service",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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
        name="query_k8s_replicasets",
        description="Query Kubernetes ReplicaSet history for a deployment (useful for rollout debugging)",
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
        name="query_k8s_jobs",
        description="Query Kubernetes Job and CronJob status for a service (completions, failures, schedule)",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "namespace": {"type": "string"},
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


SENSITIVE_KEYS = {
    "password", "secret", "token", "api_key", "access_key",
    "authorization", "cookie",
}


def _sanitize_for_audit(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS or any(
                sk in k.lower() for sk in SENSITIVE_KEYS
            ) else _sanitize_for_audit(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_sanitize_for_audit(item) for item in data]
    if isinstance(data, str):
        for sk in SENSITIVE_KEYS:
            if sk in data.lower():
                return "***REDACTED***"
    return data


EVAL_WRITE_LIKE_TOOLS = {"execute_action"}


def _maybe_eval_fixture_response(
    request: ToolRequest, start_time: float
) -> Optional[ToolResponse]:
    """Short-circuit tool calls to fixed fixtures when inside an eval fixture_scope.

    Returns None outside any scope (production / normal tests) so the gateway
    proceeds with its mock/real adapter logic unchanged. Inside a scope:
      - tool provided in fixtures   -> wrapped fixture result
      - write_* / execute_action    -> success stub (not required as fixtures)
      - other read-only tool        -> controlled empty {} (NOT mock data)
    """
    from app.evals.fixture_context import get_active_fixtures

    fixtures = get_active_fixtures()
    if fixtures is None:
        return None

    tool_name = request.tool_name
    if tool_name in fixtures:
        raw = fixtures[tool_name]
        result = dict(raw) if isinstance(raw, dict) else {"value": raw}
    elif tool_name.startswith("write_") or tool_name in EVAL_WRITE_LIKE_TOOLS:
        result = {"success": True, "_eval_stub": True}
    else:
        result = {}

    result["_adapter_info"] = "eval_fixture"
    latency = int((time.time() - start_time) * 1000)
    return ToolResponse(
        tool_name=tool_name,
        success=True,
        result=result,
        latency_ms=latency,
    )


class ToolGateway:
    def __init__(self):
        self.handlers = tool_handlers
        self.registry = TOOL_REGISTRY
        self.audit_log = audit_log
        self.adapter_mode = ADAPTER_MODE
        logger.info(f"ToolGateway initialized with adapter mode: {ADAPTER_MODE}")

    def describe_capability(self, tool_name: str) -> Dict[str, Any]:
        """Return capability descriptor for a tool without executing it."""
        if tool_name not in self.handlers:
            return {"available": False, "adapter_mode": self.adapter_mode, "reason": "tool not registered"}

        real_handler = select_adapter(tool_name)
        if ADAPTER_MODE == "mock":
            return {
                "available": True,
                "adapter_mode": "mock",
                "reason": "mock adapter available",
            }

        has_real_adapter = real_handler is not None
        if has_real_adapter and ADAPTER_MODE == "real":
            return {
                "available": True,
                "adapter_mode": "real",
                "reason": "real adapter available",
            }

        return {
            "available": False,
            "adapter_mode": self.adapter_mode,
            "reason": f"{tool_name} real adapter is not configured",
        }

    async def call_tool(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()
        # Eval fixture short-circuit (active only inside fixture_scope). Happens
        # before mock/real selection, so it composes with the autouse mock conftest.
        fixture_resp = _maybe_eval_fixture_response(request, start_time)
        if fixture_resp is not None:
            return fixture_resp

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
        elif ADAPTER_MODE == "real":
            latency = int((time.time() - start_time) * 1000)
            tracer.end_span(span_id, status="error", error=f"No real adapter for {request.tool_name}")
            return ToolResponse(
                tool_name=request.tool_name,
                success=False,
                error=f"Tool '{request.tool_name}' has no real adapter configured",
                latency_ms=latency,
            )
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

        try:
            from app.repositories import SessionLocal
            from app.models.db_models import IncidentToolAudit
            from app.tools.gateway import _sanitize_for_audit

            db = SessionLocal()
            try:
                audit_record = IncidentToolAudit(
                    audit_id=f"audit_{uuid.uuid4().hex[:8]}",
                    run_id=request.run_id,
                    tool_name=request.tool_name,
                    adapter_mode=adapter_info,
                    request_json=_sanitize_for_audit(dict(request.params) if request.params else {}),
                    response_json=_sanitize_for_audit(result if success else None) if success else None,
                    success=1 if success else 0,
                    error_message=result.get("error") if not success else None,
                    latency_ms=latency_ms,
                )
                db.add(audit_record)
                db.commit()
            except Exception as db_err:
                db.rollback()
                logger.warning(f"Failed to persist tool audit: {db_err}")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Failed to persist tool audit (outer): {e}")

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        metadata = self.registry.get(tool_name)
        if not metadata:
            return {}
        schema = metadata.parameters_schema or {}
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": metadata.description or "",
                "parameters": schema,
            },
        }

    def get_audit_log(self, run_id: str = None) -> List[Dict[str, Any]]:
        if run_id:
            return [e for e in self.audit_log if e.get("run_id") == run_id]
        return self.audit_log


gateway = ToolGateway()
