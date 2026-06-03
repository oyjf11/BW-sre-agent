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


async def query_k8s_nodes(
    service: str,
    env: str,
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    nodes = await asyncio.to_thread(client.list_nodes)
    serialized = []
    for node in nodes:
        conditions = {}
        for cond in (node.status.conditions or []):
            if cond is None:
                continue
            conditions[str(cond.type)] = str(cond.status)

        capacity = node.status.capacity or {}
        allocatable = node.status.allocatable or {}
        labels = node.metadata.labels or {}
        role = labels.get(
            "node-role.kubernetes.io/control-plane",
            labels.get(
                "node-role.kubernetes.io/master",
                labels.get("kubernetes.io/role", "worker"),
            ),
        )

        serialized.append({
            "name": node.metadata.name,
            "role": role,
            "conditions": conditions,
            "capacity_cpu": str(capacity.get("cpu", "")),
            "capacity_memory": str(capacity.get("memory", "")),
            "allocatable_cpu": str(allocatable.get("cpu", "")),
            "allocatable_memory": str(allocatable.get("memory", "")),
            "kubelet_version": node.status.node_info.kubelet_version if node.status.node_info else "",
            "kernel_version": node.status.node_info.kernel_version if node.status.node_info else "",
            "container_runtime": node.status.node_info.container_runtime_version if node.status.node_info else "",
            "unschedulable": bool(node.spec.unschedulable),
        })
    return {
        "service": service,
        "env": env,
        "nodes": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_services(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    svc_list = await asyncio.to_thread(client.list_services, ns)
    svc_lower = service.lower()
    serialized = []
    for svc in svc_list:
        name = svc.metadata.name.lower()
        if svc_lower not in name:
            continue
        ports = []
        for port in (svc.spec.ports or []):
            ports.append({
                "name": port.name or "",
                "port": port.port,
                "target_port": str(port.target_port) if port.target_port else "",
                "protocol": port.protocol or "TCP",
            })
        lb_status = None
        if svc.status.load_balancer and svc.status.load_balancer.ingress:
            lb_status = [
                {"ip": ing.ip, "hostname": ing.hostname}
                for ing in svc.status.load_balancer.ingress
            ]
        serialized.append({
            "name": svc.metadata.name,
            "type": svc.spec.type,
            "cluster_ip": svc.spec.cluster_ip,
            "external_ip": svc.spec.external_i_ps or [],
            "ports": ports,
            "selector": svc.spec.selector or {},
            "lb_status": lb_status,
        })
    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "services": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_hpa(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, "deployment_name": deployment_name, **kwargs},
    )
    target["namespace"], target["deployment_name"] = client.resolve_target(
        service, target["namespace"], target["deployment_name"],
    )
    ns = target["namespace"]
    dep_name = target["deployment_name"]

    hpas = await asyncio.to_thread(client.list_hpas, ns)
    serialized = []
    for hpa in hpas:
        ref = hpa.spec.scale_target_ref
        if not ref or dep_name.lower() not in (ref.name or "").lower():
            continue

        current_metrics = []
        if hasattr(hpa.status, "current_metrics") and hpa.status.current_metrics:
            for m in hpa.status.current_metrics:
                entry = {"type": str(m.type)}
                if m.resource:
                    entry["resource_name"] = m.resource.name
                    if m.resource.current and m.resource.current.average_utilization:
                        entry["current_average_utilization"] = m.resource.current.average_utilization
                    if m.resource.current and m.resource.current.average_value:
                        entry["current_average_value"] = m.resource.current.average_value
                current_metrics.append(entry)
        elif hasattr(hpa.status, "current_cpu_utilization_percentage") and hpa.status.current_cpu_utilization_percentage is not None:
            current_metrics.append({
                "type": "Resource",
                "resource_name": "cpu",
                "current_average_utilization": hpa.status.current_cpu_utilization_percentage,
            })

        conditions = []
        raw_conditions = getattr(hpa.status, "conditions", None) or []
        for cond in raw_conditions:
            if cond is None:
                continue
            conditions.append({
                "type": str(cond.type),
                "status": str(cond.status),
                "reason": cond.reason or "",
                "message": cond.message or "",
            })

        serialized.append({
            "name": hpa.metadata.name,
            "min_replicas": hpa.spec.min_replicas,
            "max_replicas": hpa.spec.max_replicas,
            "current_replicas": hpa.status.current_replicas,
            "desired_replicas": hpa.status.desired_replicas,
            "current_metrics": current_metrics,
            "conditions": conditions,
        })

    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "deployment_name": dep_name,
        "hpas": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_ingresses(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    ingresses = await asyncio.to_thread(client.list_ingresses, ns)
    svc_lower = service.lower()
    serialized = []
    for ing in ingresses:
        ing_name = ing.metadata.name.lower()
        svc_match = svc_lower in ing_name

        hosts = []
        tls_enabled = False
        for rule in (ing.spec.rules or []):
            if rule.host:
                hosts.append(rule.host)
            if rule.http:
                for path in (rule.http.paths or []):
                    if path.backend:
                        backend_svc = (
                            getattr(path.backend.service, "name", None)
                            or getattr(path.backend, "service_name", None)
                            or getattr(path.backend, "serviceName", None)
                        )
                        if backend_svc and svc_lower in backend_svc.lower():
                            svc_match = True

        if ing.spec.tls:
            tls_enabled = True

        lb_status = None
        if ing.status.load_balancer and ing.status.load_balancer.ingress:
            lb_status = [
                {"ip": lb_ing.ip, "hostname": lb_ing.hostname}
                for lb_ing in ing.status.load_balancer.ingress
            ]

        ingress_class = ""
        if hasattr(ing.spec, "ingress_class_name") and ing.spec.ingress_class_name:
            ingress_class = ing.spec.ingress_class_name
        else:
            annotations = ing.metadata.annotations or {}
            ingress_class = annotations.get("kubernetes.io/ingress.class", "")

        if svc_match:
            serialized.append({
                "name": ing.metadata.name,
                "namespace": ns,
                "hosts": hosts,
                "tls_enabled": tls_enabled,
                "ingress_class": ingress_class,
                "lb_status": lb_status,
            })

    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "ingresses": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_statefulsets(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    sts_list = await asyncio.to_thread(client.list_statefulsets, ns)
    svc_lower = service.lower()
    serialized = []
    for sts in sts_list:
        if svc_lower not in sts.metadata.name.lower():
            continue
        replicas = sts.spec.replicas or 0
        ready = sts.status.ready_replicas or 0
        if ready >= replicas and replicas > 0:
            health = "running"
        elif ready > 0:
            health = "degraded"
        else:
            health = "unavailable"
        serialized.append({
            "name": sts.metadata.name,
            "replicas": replicas,
            "ready_replicas": sts.status.ready_replicas or 0,
            "current_replicas": sts.status.current_replicas or 0,
            "current_revision": sts.status.current_revision or "",
            "update_revision": sts.status.update_revision or "",
            "status": health,
        })
    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "statefulsets": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_daemonsets(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    ds_list = await asyncio.to_thread(client.list_daemonsets, ns)
    svc_lower = service.lower()
    serialized = []
    for ds in ds_list:
        if svc_lower not in ds.metadata.name.lower():
            continue
        desired = ds.status.desired_number_scheduled or 0
        ready = ds.status.number_ready or 0
        if ready >= desired and desired > 0:
            health = "running"
        elif ready > 0:
            health = "degraded"
        else:
            health = "unavailable"
        serialized.append({
            "name": ds.metadata.name,
            "desired_number_scheduled": ds.status.desired_number_scheduled or 0,
            "current_number_scheduled": ds.status.current_number_scheduled or 0,
            "number_ready": ds.status.number_ready or 0,
            "number_available": ds.status.number_available or 0,
            "status": health,
        })
    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "daemonsets": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_configmaps(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    cm_list = await asyncio.to_thread(client.list_configmaps, ns)
    svc_lower = service.lower()
    serialized = []
    SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "access_key", "private_key", "key", "cert", "tls"}
    for cm in cm_list:
        if svc_lower not in cm.metadata.name.lower():
            continue
        data_keys = list((cm.data or {}).keys())
        binary_keys = list((cm.binary_data or {}).keys())
        data_sample = {}
        for k, v in (cm.data or {}).items():
            k_lower = k.lower()
            if any(sk in k_lower for sk in SENSITIVE_KEYS):
                data_sample[k] = "***REDACTED***"
            else:
                data_sample[k] = v[:500] if len(v) > 500 else v
        serialized.append({
            "name": cm.metadata.name,
            "data_keys": data_keys,
            "binary_data_keys": binary_keys,
            "data_sample": data_sample,
            "immutable": bool(cm.immutable) if cm.immutable else False,
        })
    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "configmaps": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_resource_quotas(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    quotas = await asyncio.to_thread(client.list_resource_quotas, ns)
    serialized = []
    for q in quotas:
        hard = {}
        used = {}
        for resource, quantity in (q.status.hard or {}).items():
            hard[str(resource)] = str(quantity)
        for resource, quantity in (q.status.used or {}).items():
            used[str(resource)] = str(quantity)
        serialized.append({
            "name": q.metadata.name,
            "hard": hard,
            "used": used,
        })
    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "resource_quotas": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_pvc(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    pvcs = await asyncio.to_thread(client.list_pvcs, ns)
    svc_lower = service.lower()
    serialized = []
    for pvc in pvcs:
        if svc_lower not in pvc.metadata.name.lower():
            continue
        capacity_storage = ""
        if pvc.status.capacity and "storage" in pvc.status.capacity:
            capacity_storage = str(pvc.status.capacity["storage"])
        serialized.append({
            "name": pvc.metadata.name,
            "status": pvc.status.phase,
            "capacity": capacity_storage,
            "access_modes": pvc.spec.access_modes or [],
            "storage_class": pvc.spec.storage_class_name or "",
            "volume_name": pvc.spec.volume_name or "",
        })
    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "pvcs": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_replicasets(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, "deployment_name": deployment_name, **kwargs},
    )
    target["namespace"], target["deployment_name"] = client.resolve_target(
        service, target["namespace"], target["deployment_name"],
    )
    ns = target["namespace"]
    dep_name = target["deployment_name"]

    rs_list = await asyncio.to_thread(client.list_replicasets, ns)
    serialized = []
    for rs in rs_list:
        owner_refs = rs.metadata.owner_references or []
        owned_by = [
            {"kind": ref.kind, "name": ref.name}
            for ref in owner_refs if ref and ref.name.lower() == dep_name.lower()
        ] if owner_refs else []
        if dep_name.lower() not in rs.metadata.name.lower() and not owned_by:
            continue
        containers = rs.spec.template.spec.containers or []
        images = [c.image for c in containers if c.image]
        timestamp = rs.metadata.creation_timestamp.isoformat() if rs.metadata.creation_timestamp else None
        serialized.append({
            "name": rs.metadata.name,
            "replicas": rs.status.replicas or 0,
            "ready_replicas": rs.status.ready_replicas or 0,
            "available_replicas": rs.status.available_replicas or 0,
            "images": images,
            "owner_references": [
                {"kind": ref.kind, "name": ref.name}
                for ref in (rs.metadata.owner_references or [])
                if ref
            ],
            "creation_timestamp": timestamp,
        })

    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "deployment_name": dep_name,
        "replicasets": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


async def query_k8s_jobs(
    service: str,
    env: str,
    namespace: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    client = K8sClient()
    target = _resolve_k8s_target(
        service, env, {"namespace": namespace, **kwargs},
    )
    target["namespace"], _ = client.resolve_target(service, target["namespace"], "")
    ns = target["namespace"]

    jobs = await asyncio.to_thread(client.list_jobs, ns)
    cronjobs = await asyncio.to_thread(client.list_cronjobs, ns)
    svc_lower = service.lower()
    serialized = []
    for job in jobs:
        if svc_lower not in job.metadata.name.lower():
            continue
        conditions = []
        for cond in (job.status.conditions or []):
            if cond is None:
                continue
            conditions.append({"type": str(cond.type), "status": str(cond.status)})
        serialized.append({
            "name": job.metadata.name,
            "namespace": ns,
            "completions": job.spec.completions,
            "parallelism": job.spec.parallelism,
            "succeeded": job.status.succeeded or 0,
            "active": job.status.active or 0,
            "failed": job.status.failed or 0,
            "conditions": conditions,
        })
    for cj in cronjobs:
        if svc_lower not in cj.metadata.name.lower():
            continue
        last_schedule = cj.status.last_schedule_time.isoformat() if cj.status.last_schedule_time else None
        serialized.append({
            "name": cj.metadata.name,
            "namespace": ns,
            "schedule": cj.spec.schedule,
            "suspend": bool(cj.spec.suspend),
            "last_schedule_time": last_schedule,
            "active_jobs": len(cj.status.active or []),
        })

    return {
        "service": service,
        "env": env,
        "namespace": ns,
        "jobs": serialized,
        "count": len(serialized),
        "response_size_limit_kb": RESPONSE_SIZE_LIMIT_KB,
    }


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
