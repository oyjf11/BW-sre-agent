import asyncio
import json
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

from app.tools.clients.k8s_client import K8sClient

RESPONSE_SIZE_LIMIT_KB = 128
_PATTERN_RULES = [
    ("oom", re.compile(r"(oom|out of memory|killed)", re.IGNORECASE)),
    ("timeout", re.compile(r"(timeout|timed out)", re.IGNORECASE)),
    ("connection_refused", re.compile(r"connection refused", re.IGNORECASE)),
    ("backoff", re.compile(r"(back[- ]?off|crashloopbackoff)", re.IGNORECASE)),
    ("exception", re.compile(r"(exception|traceback)", re.IGNORECASE)),
    ("error", re.compile(r"\berror\b", re.IGNORECASE)),
]


def _resolve_k8s_target(service: str, env: str, params: Dict[str, Any]) -> Dict[str, str]:
    namespace = params.get("namespace") or "default"
    deployment_name = params.get("deployment_name") or service
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment_name,
    }


def _json_size_bytes(data: Dict[str, Any]) -> int:
    return len(json.dumps(data, ensure_ascii=False, default=str).encode("utf-8"))


def _truncate_logs_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    max_bytes = RESPONSE_SIZE_LIMIT_KB * 1024
    if _json_size_bytes(payload) <= max_bytes:
        return payload

    payload["sample_logs"] = []
    payload["truncated"] = True
    if _json_size_bytes(payload) <= max_bytes:
        return payload

    payload["pods"] = [
        {
            "name": pod.get("name"),
            "phase": pod.get("phase"),
            "restart_count": pod.get("restart_count", 0),
        }
        for pod in payload.get("pods", [])
    ]
    if _json_size_bytes(payload) <= max_bytes:
        return payload

    payload["top_patterns"] = payload.get("top_patterns", [])[:10]
    return payload


def _serialize_pod(pod: Any) -> Dict[str, Any]:
    statuses = pod.status.container_statuses or []
    restart_count = sum((status.restart_count or 0) for status in statuses if status is not None)
    ready = all(bool(status.ready) for status in statuses) if statuses else False

    return {
        "name": pod.metadata.name,
        "phase": pod.status.phase,
        "ready": ready,
        "restart_count": restart_count,
        "node_name": pod.spec.node_name,
        "pod_ip": pod.status.pod_ip,
        "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None,
    }


def _event_timestamp(event: Any):
    return (
        event.last_timestamp
        or event.event_time
        or event.first_timestamp
        or getattr(event.metadata, "creation_timestamp", None)
        or datetime.min
    )


async def query_k8s_deployment_status(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service,
        env,
        {"namespace": namespace, "deployment_name": deployment_name, **kwargs},
    )
    target["namespace"], target["deployment_name"] = client.resolve_target(
        service,
        target["namespace"],
        target["deployment_name"],
    )
    result = await asyncio.to_thread(
        client.get_deployment_status,
        target["namespace"],
        target["deployment_name"],
    )
    result["service"] = service
    result["env"] = env
    result["deployment_name"] = target["deployment_name"]
    return result


async def query_k8s_pods(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service,
        env,
        {"namespace": namespace, "deployment_name": deployment_name, **kwargs},
    )
    target["namespace"], target["deployment_name"] = client.resolve_target(
        service,
        target["namespace"],
        target["deployment_name"],
    )
    pods = await asyncio.to_thread(
        client.list_pods_for_target,
        target["namespace"],
        target["deployment_name"],
        service,
    )
    serialized = [_serialize_pod(pod) for pod in pods]
    return {
        "service": service,
        "env": env,
        "namespace": target["namespace"],
        "deployment_name": target["deployment_name"],
        "pods": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_events(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    limit: int = 20,
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service,
        env,
        {"namespace": namespace, "deployment_name": deployment_name, **kwargs},
    )
    target["namespace"], target["deployment_name"] = client.resolve_target(
        service,
        target["namespace"],
        target["deployment_name"],
    )

    pods = await asyncio.to_thread(
        client.list_pods_for_target,
        target["namespace"],
        target["deployment_name"],
        service,
    )
    pod_names = {pod.metadata.name for pod in pods}
    deployment_name = target["deployment_name"]

    events = await asyncio.to_thread(client.list_events, target["namespace"])
    filtered = []
    for event in events:
        involved = event.involved_object
        involved_name = involved.name if involved else ""
        if involved_name == deployment_name or involved_name in pod_names or service in involved_name:
            filtered.append(event)

    filtered.sort(key=_event_timestamp, reverse=True)
    limited = filtered[: max(1, min(limit, 50))]
    reason_counter = Counter((event.reason or "Unknown") for event in limited)

    return {
        "service": service,
        "env": env,
        "namespace": target["namespace"],
        "deployment_name": deployment_name,
        "events": [
            {
                "reason": event.reason or "Unknown",
                "message": event.message or "",
                "type": event.type or "Normal",
                "object": event.involved_object.name if event.involved_object else "",
                "timestamp": _event_timestamp(event).isoformat()
                if _event_timestamp(event) != datetime.min
                else None,
            }
            for event in limited
        ],
        "top_reasons": [
            {"reason": reason, "count": count}
            for reason, count in reason_counter.most_common(10)
        ],
        "count": len(limited),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_pod_logs_summary(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    tail_lines: int = 100,
    limit_pods: int = 5,
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service,
        env,
        {"namespace": namespace, "deployment_name": deployment_name, **kwargs},
    )
    target["namespace"], target["deployment_name"] = client.resolve_target(
        service,
        target["namespace"],
        target["deployment_name"],
    )

    pods = await asyncio.to_thread(
        client.list_pods_for_target,
        target["namespace"],
        target["deployment_name"],
        service,
    )
    pods = pods[: max(1, min(limit_pods, 10))]

    pattern_counter: Counter[str] = Counter()
    sample_logs: List[Dict[str, str]] = []
    lines_scanned = 0
    serialized_pods = [_serialize_pod(pod) for pod in pods]

    for pod in pods:
        log_text = await asyncio.to_thread(
            client.read_pod_log,
            target["namespace"],
            pod.metadata.name,
            max(1, min(tail_lines, 500)),
        )
        lines = [line for line in log_text.splitlines() if line.strip()]
        lines_scanned += len(lines)
        for line in lines:
            for label, pattern in _PATTERN_RULES:
                if pattern.search(line):
                    pattern_counter[label] += 1
                    if len(sample_logs) < 20:
                        sample_logs.append({"pod": pod.metadata.name, "pattern": label, "line": line[:500]})
                    break

    payload = {
        "service": service,
        "env": env,
        "namespace": target["namespace"],
        "deployment_name": target["deployment_name"],
        "tail_window": max(1, min(tail_lines, 500)),
        "lines_scanned": lines_scanned,
        "pod_count": len(pods),
        "pods": serialized_pods,
        "top_patterns": [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_counter.most_common(10)
        ],
        "sample_logs": sample_logs,
        "truncated": False,
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }
    return _truncate_logs_summary(payload)


async def query_deployments(
    service: str,
    env: str,
    time_range: Dict[str, str] = None,
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    all_deployments = await asyncio.to_thread(client.list_all_deployments)
    result_deployments = []
    svc_lower = service.lower()

    for dep in all_deployments:
        dep_namespace = dep.metadata.namespace
        dep_name = dep.metadata.name
        dep_lower = dep_name.lower()

        if svc_lower not in dep_lower and service not in dep_namespace:
            continue

        containers = dep.spec.template.spec.containers or []
        images = [c.image for c in containers if c.image]

        conditions = dep.status.conditions or []
        available = any(
            c.type == "Available" and c.status == "True" for c in conditions
        )
        progressing = any(
            c.type == "Progressing" and c.status == "True" for c in conditions
        )

        if available:
            dep_status = "success"
        elif progressing:
            dep_status = "progressing"
        else:
            dep_status = "failed"

        last_rollout = None
        if dep.metadata.creation_timestamp:
            last_rollout = dep.metadata.creation_timestamp.isoformat()

        result_deployments.append({
            "deployment_id": f"{dep_namespace}/{dep_name}",
            "service": dep_name,
            "namespace": dep_namespace,
            "images": images,
            "version": images[0] if images else "",
            "replicas": dep.status.replicas or 0,
            "ready_replicas": dep.status.ready_replicas or 0,
            "timestamp": last_rollout or "",
            "status": dep_status,
            "conditions": [
                {"type": c.type, "status": c.status, "message": c.message or ""}
                for c in conditions
            ],
        })

    return {
        "deployments": result_deployments,
        "count": len(result_deployments),
        "service": service,
        "env": env,
        "response_size_limit_kb": 128,
    }
