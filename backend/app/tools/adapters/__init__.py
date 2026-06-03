from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


async def query_logs(
    service: str,
    env: str,
    time_range: Dict[str, str] = None,
    query: str = "*",
    limit: int = 100,
) -> Dict[str, Any]:
    logs = []
    base_time = datetime.utcnow() - timedelta(hours=1)
    for i in range(min(limit, 10)):
        logs.append(
            {
                "timestamp": (base_time + timedelta(minutes=i * 5)).isoformat(),
                "level": random.choice(["INFO", "WARNING", "ERROR"]),
                "message": f"Sample log message {i} for {service}",
                "source": f"{service}-provider",
            }
        )
    return {
        "logs": logs,
        "count": len(logs),
        "query": query,
    }


async def query_metrics(
    service: str,
    env: str,
    time_range: Dict[str, str] = None,
    metric_names: List[str] = None,
) -> Dict[str, Any]:
    if metric_names is None:
        metric_names = ["cpu_usage", "memory_usage", "request_latency", "error_rate"]
    metrics = {}
    for name in metric_names:
        metrics[name] = {
            "values": [
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=i * 5)).isoformat(),
                    "value": random.uniform(0, 100),
                }
                for i in range(10)
            ],
            "unit": "%" if "usage" in name or "rate" in name else "ms",
        }
    return {"metrics": metrics, "service": service, "env": env}


async def query_deployments(
    service: str,
    env: str,
    time_range: Dict[str, str] = None,
) -> Dict[str, Any]:
    deployments = [
        {
            "deployment_id": f"deploy-{i}",
            "service": service,
            "version": f"v1.{i}.0",
            "timestamp": (datetime.utcnow() - timedelta(hours=i * 6)).isoformat(),
            "status": "success" if i > 0 else "failed",
            "commit": f"abc{123 + i}",
        }
        for i in range(5)
    ]
    return {"deployments": deployments, "count": len(deployments)}


async def query_runbook(
    service: str,
    env: str,
    incident_type: str = None,
) -> Dict[str, Any]:
    runbooks = [
        {
            "runbook_id": f"rb-{service}-{incident_type or 'default'}",
            "title": f"Runbook for {service} {incident_type or 'incident'}",
            "steps": [
                {
                    "step": 1,
                    "description": "Check service health",
                    "command": f"curl -s {service}/health",
                },
                {
                    "step": 2,
                    "description": "Review recent logs",
                    "command": f"kubectl logs -l service={service}",
                },
                {
                    "step": 3,
                    "description": "Check metrics",
                    "command": f"curl -s {service}/metrics",
                },
            ],
            "tags": [service, env, incident_type or "general"],
        }
    ]
    return {"runbooks": runbooks, "count": len(runbooks)}


async def execute_action(
    action_type: str,
    service: str,
    env: str,
    params: Dict[str, Any],
    idempotency_key: str = None,
) -> Dict[str, Any]:
    return {
        "action_id": f"act_{random.randint(1000, 9999)}",
        "action_type": action_type,
        "service": service,
        "env": env,
        "status": "executed",
        "result": f"Action {action_type} executed successfully on {service} in {env}",
        "idempotency_key": idempotency_key,
    }


async def query_ticket_by_id(ticket_id: str) -> Dict[str, Any]:
    """Return a mock ticket for the given ticket_id."""
    return {
        "ticket_id": ticket_id,
        "title": f"Incident: {ticket_id}",
        "description": f"Auto-retrieved ticket for {ticket_id}",
        "service": "api-service",
        "env": "prod",
        "severity": "P2",
        "source": "ticket_lookup",
        "time_range": {
            "from": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "to": datetime.utcnow().isoformat(),
        },
    }


async def query_service_metadata(service: str, env: str) -> Dict[str, Any]:
    """Return mock service metadata for precondition checks."""
    return {
        "service": service,
        "env": env,
        "exists": True,
        "owner_team": "platform",
        "tier": "critical",
        "dependencies": [],
    }


async def query_k8s_deployment_status(
    service: str, env: str, namespace: str = "default", deployment_name: str = ""
) -> Dict[str, Any]:
    """Return mock Kubernetes deployment status."""
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment_name or service,
        "status": "running",
        "replicas": 3,
        "ready_replicas": 3,
        "unavailable_replicas": 0,
        "last_rollout": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
    }


async def query_k8s_pods(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
) -> Dict[str, Any]:
    """Return mock Kubernetes pod status."""
    deployment = deployment_name or service
    pods = [
        {
            "name": f"{deployment}-6b8b8d9d7f-abc12",
            "phase": "Running",
            "ready": True,
            "restart_count": 0,
            "node_name": "node-a",
            "pod_ip": "10.0.0.11",
            "start_time": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
        },
        {
            "name": f"{deployment}-6b8b8d9d7f-def34",
            "phase": "Running",
            "ready": True,
            "restart_count": 1,
            "node_name": "node-b",
            "pod_ip": "10.0.0.12",
            "start_time": (datetime.utcnow() - timedelta(minutes=18)).isoformat(),
        },
    ]
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment,
        "pods": pods,
        "count": len(pods),
        "response_size_limit_kb": 128,
    }


async def query_k8s_events(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    limit: int = 20,
) -> Dict[str, Any]:
    """Return mock Kubernetes events."""
    deployment = deployment_name or service
    events = [
        {
            "reason": "BackOff",
            "message": "Back-off restarting failed container",
            "type": "Warning",
            "object": f"{deployment}-6b8b8d9d7f-abc12",
            "timestamp": (datetime.utcnow() - timedelta(minutes=9)).isoformat(),
        },
        {
            "reason": "Pulled",
            "message": "Successfully pulled image",
            "type": "Normal",
            "object": deployment,
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
        },
    ][: max(1, min(limit, 20))]
    top_reasons = {}
    for event in events:
        top_reasons[event["reason"]] = top_reasons.get(event["reason"], 0) + 1
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment,
        "events": events,
        "top_reasons": [
            {"reason": reason, "count": count} for reason, count in top_reasons.items()
        ],
        "count": len(events),
        "response_size_limit_kb": 128,
    }


async def query_k8s_pod_logs_summary(
    service: str,
    env: str,
    namespace: str = "default",
    deployment_name: str = "",
    tail_lines: int = 100,
    limit_pods: int = 5,
) -> Dict[str, Any]:
    """Return mock Kubernetes pod log summary."""
    deployment = deployment_name or service
    pod_count = min(limit_pods, 2)
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment,
        "tail_window": min(tail_lines, 100),
        "lines_scanned": pod_count * min(tail_lines, 100),
        "pod_count": pod_count,
        "pods": [
            {
                "name": f"{deployment}-6b8b8d9d7f-abc12",
                "phase": "Running",
                "restart_count": 0,
            }
        ],
        "top_patterns": [
            {"pattern": "timeout", "count": 3},
            {"pattern": "error", "count": 2},
        ],
        "sample_logs": [
            {
                "pod": f"{deployment}-6b8b8d9d7f-abc12",
                "pattern": "timeout",
                "line": "database timeout while waiting for connection",
            }
        ],
        "truncated": False,
        "response_size_limit_kb": 128,
    }


async def query_lb_health_status(service: str, env: str) -> Dict[str, Any]:
    """Return mock load balancer health status."""
    return {
        "service": service,
        "env": env,
        "status": "healthy",
        "healthy_hosts": 3,
        "unhealthy_hosts": 0,
        "health_check_path": "/healthz",
    }


async def query_lb_traffic_metrics(
    service: str, env: str, window_minutes: int = 5
) -> Dict[str, Any]:
    """Return mock load balancer traffic metrics."""
    return {
        "service": service,
        "env": env,
        "qps": round(random.uniform(100, 500), 1),
        "error_rate": round(random.uniform(0.001, 0.02), 4),
        "p50_latency_ms": round(random.uniform(10, 50), 1),
        "p99_latency_ms": round(random.uniform(100, 300), 1),
        "window": "5m",
    }


async def mock_query_db_processlist(**kwargs) -> Dict[str, Any]:
    """Return mock MySQL processlist data."""
    processlist = [
        {
            "Id": 1001,
            "User": "app_user",
            "Host": "10.0.1.50:45678",
            "db": "hoo_ai",
            "Command": "Query",
            "Time": 12,
            "State": "Sending data",
            "Info": "SELECT o.*, u.name FROM orders o JOIN users u ON o.user_id = u.id WHERE o.status = 'pending'",
        },
        {
            "Id": 1002,
            "User": "app_user",
            "Host": "10.0.1.51:45679",
            "db": "hoo_ai",
            "Command": "Query",
            "Time": 3,
            "State": "Locked",
            "Info": "UPDATE inventory SET stock = stock - 1 WHERE sku = 'SKU-12345'",
        },
        {
            "Id": 1003,
            "User": "root",
            "Host": "10.0.1.1:50000",
            "db": None,
            "Command": "Sleep",
            "Time": 300,
            "State": "",
            "Info": None,
        },
        {
            "Id": 1004,
            "User": "app_user",
            "Host": "10.0.1.52:45680",
            "db": "hoo_ai",
            "Command": "Query",
            "Time": 0,
            "State": "init",
            "Info": "SELECT id, name FROM products WHERE category_id = 42",
        },
    ]
    active = [p for p in processlist if p["Command"].lower() != "sleep"]
    return {
        "processlist": active,
        "total_connections": len(processlist),
        "active_connections": len(active),
        "response_size_limit_kb": 64,
    }


async def mock_query_db_slow_queries(threshold_seconds: int = 5, **kwargs) -> Dict[str, Any]:
    """Return mock slow query data."""
    threshold = threshold_seconds
    slow_queries = [
        {
            "Id": 2001,
            "User": "app_user",
            "Host": "10.0.1.50:45678",
            "db": "hoo_ai",
            "Command": "Query",
            "Time": 45,
            "State": "Copying to tmp table",
            "Info": "SELECT COUNT(*) FROM orders o JOIN order_items oi ON o.id = oi.order_id JOIN products p ON oi.product_id = p.id WHERE o.created_at > '2024-01-01' GROUP BY p.category_id",
        },
        {
            "Id": 2002,
            "User": "app_user",
            "Host": "10.0.1.53:45681",
            "db": "hoo_ai",
            "Command": "Query",
            "Time": 8,
            "State": "Sending data",
            "Info": "SELECT u.*, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id HAVING order_count > 10 ORDER BY order_count DESC",
        },
    ]
    filtered = [q for q in slow_queries if q["Time"] >= threshold]
    return {
        "slow_queries": filtered,
        "threshold_seconds": threshold,
        "count": len(filtered),
        "response_size_limit_kb": 64,
    }


async def mock_query_db_table_status(**kwargs) -> Dict[str, Any]:
    """Return mock table status data (top 20 by size)."""
    tables = [
        {
            "Name": "orders",
            "Engine": "InnoDB",
            "Rows": 1500000,
            "Data_length": 524288000,
            "Index_length": 104857600,
            "Data_free": 52428800,
        },
        {
            "Name": "order_items",
            "Engine": "InnoDB",
            "Rows": 5000000,
            "Data_length": 419430400,
            "Index_length": 83886080,
            "Data_free": 31457280,
        },
        {
            "Name": "users",
            "Engine": "InnoDB",
            "Rows": 200000,
            "Data_length": 104857600,
            "Index_length": 20971520,
            "Data_free": 10485760,
        },
        {
            "Name": "products",
            "Engine": "InnoDB",
            "Rows": 50000,
            "Data_length": 52428800,
            "Index_length": 10485760,
            "Data_free": 5242880,
        },
        {
            "Name": "inventory",
            "Engine": "InnoDB",
            "Rows": 50000,
            "Data_length": 20971520,
            "Index_length": 4194304,
            "Data_free": 2097152,
        },
        {
            "Name": "categories",
            "Engine": "InnoDB",
            "Rows": 500,
            "Data_length": 1048576,
            "Index_length": 262144,
            "Data_free": 0,
        },
        {
            "Name": "coupons",
            "Engine": "InnoDB",
            "Rows": 10000,
            "Data_length": 8388608,
            "Index_length": 1048576,
            "Data_free": 524288,
        },
        {
            "Name": "payments",
            "Engine": "InnoDB",
            "Rows": 1200000,
            "Data_length": 314572800,
            "Index_length": 62914560,
            "Data_free": 20971520,
        },
        {
            "Name": "refunds",
            "Engine": "InnoDB",
            "Rows": 30000,
            "Data_length": 10485760,
            "Index_length": 2097152,
            "Data_free": 1048576,
        },
        {
            "Name": "sessions",
            "Engine": "InnoDB",
            "Rows": 800000,
            "Data_length": 209715200,
            "Index_length": 41943040,
            "Data_free": 15728640,
        },
        {
            "Name": "notifications",
            "Engine": "InnoDB",
            "Rows": 3000000,
            "Data_length": 629145600,
            "Index_length": 125829120,
            "Data_free": 41943040,
        },
        {
            "Name": "audit_log",
            "Engine": "InnoDB",
            "Rows": 10000000,
            "Data_length": 1073741824,
            "Index_length": 209715200,
            "Data_free": 104857600,
        },
        {
            "Name": "addresses",
            "Engine": "InnoDB",
            "Rows": 350000,
            "Data_length": 83886080,
            "Index_length": 16777216,
            "Data_free": 8388608,
        },
        {
            "Name": "reviews",
            "Engine": "InnoDB",
            "Rows": 600000,
            "Data_length": 157286400,
            "Index_length": 31457280,
            "Data_free": 10485760,
        },
        {
            "Name": "wishlist",
            "Engine": "InnoDB",
            "Rows": 150000,
            "Data_length": 31457280,
            "Index_length": 6291456,
            "Data_free": 3145728,
        },
        {
            "Name": "cart_items",
            "Engine": "InnoDB",
            "Rows": 400000,
            "Data_length": 104857600,
            "Index_length": 20971520,
            "Data_free": 5242880,
        },
        {
            "Name": "shipping",
            "Engine": "InnoDB",
            "Rows": 900000,
            "Data_length": 209715200,
            "Index_length": 41943040,
            "Data_free": 15728640,
        },
        {
            "Name": "invoices",
            "Engine": "InnoDB",
            "Rows": 1100000,
            "Data_length": 262144000,
            "Index_length": 52428800,
            "Data_free": 20971520,
        },
        {
            "Name": "tags",
            "Engine": "InnoDB",
            "Rows": 2000,
            "Data_length": 524288,
            "Index_length": 131072,
            "Data_free": 0,
        },
        {
            "Name": "product_tags",
            "Engine": "InnoDB",
            "Rows": 100000,
            "Data_length": 8388608,
            "Index_length": 4194304,
            "Data_free": 524288,
        },
    ]
    sorted_tables = sorted(tables, key=lambda t: t.get("Data_length", 0), reverse=True)[:20]
    return {
        "table_status": sorted_tables,
        "total_tables": len(tables),
        "returned_tables": len(sorted_tables),
        "response_size_limit_kb": 64,
    }


async def mock_query_db_variables(**kwargs) -> Dict[str, Any]:
    """Return mock MySQL global status variables."""
    variables = {
        "Threads_connected": "42",
        "Threads_running": "5",
        "Max_used_connections": "128",
        "Innodb_buffer_pool_reads": "15234",
        "Innodb_buffer_pool_read_requests": "9876543",
        "Innodb_buffer_pool_pages_total": "65536",
        "Innodb_buffer_pool_pages_free": "32768",
        "Innodb_row_lock_waits": "23",
        "Innodb_row_lock_time": "45678",
        "Innodb_row_lock_time_avg": "1986",
        "Connections": "123456",
        "Aborted_connects": "12",
        "Slow_queries": "89",
        "Questions": "5678901",
        "Uptime": "2592000",
        "buffer_pool_hit_rate_pct": 99.85,
    }
    return {
        "variables": variables,
        "response_size_limit_kb": 64,
    }


async def query_k8s_nodes(service: str, env: str, **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "nodes": [
            {
                "name": "node-a",
                "role": "worker",
                "conditions": {"Ready": "True", "MemoryPressure": "False", "DiskPressure": "False", "PIDPressure": "False"},
                "capacity_cpu": "8",
                "capacity_memory": "32Gi",
                "allocatable_cpu": "7800m",
                "allocatable_memory": "28Gi",
                "kubelet_version": "v1.28.0",
                "kernel_version": "5.10.0",
                "container_runtime": "containerd://1.6.21",
                "unschedulable": False,
            },
            {
                "name": "node-b",
                "role": "worker",
                "conditions": {"Ready": "True", "MemoryPressure": "True", "DiskPressure": "False", "PIDPressure": "False"},
                "capacity_cpu": "8",
                "capacity_memory": "32Gi",
                "allocatable_cpu": "7800m",
                "allocatable_memory": "28Gi",
                "kubelet_version": "v1.28.0",
                "kernel_version": "5.10.0",
                "container_runtime": "containerd://1.6.21",
                "unschedulable": False,
            },
            {
                "name": "node-c",
                "role": "control-plane",
                "conditions": {"Ready": "True", "MemoryPressure": "False", "DiskPressure": "False", "PIDPressure": "False"},
                "capacity_cpu": "4",
                "capacity_memory": "16Gi",
                "allocatable_cpu": "3800m",
                "allocatable_memory": "12Gi",
                "kubelet_version": "v1.28.0",
                "kernel_version": "5.10.0",
                "container_runtime": "containerd://1.6.21",
                "unschedulable": True,
            },
        ],
        "count": 3,
        "response_size_limit_kb": 128,
    }


async def query_k8s_services(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "services": [
            {
                "name": service,
                "type": "ClusterIP",
                "cluster_ip": "10.43.100.10",
                "external_ip": [],
                "ports": [
                    {"name": "http", "port": 8080, "target_port": "8080", "protocol": "TCP"},
                    {"name": "metrics", "port": 9090, "target_port": "9090", "protocol": "TCP"},
                ],
                "selector": {"app": service},
                "lb_status": None,
            },
            {
                "name": f"{service}-external",
                "type": "LoadBalancer",
                "cluster_ip": "10.43.100.20",
                "external_ip": ["192.168.1.100"],
                "ports": [
                    {"name": "https", "port": 443, "target_port": "8443", "protocol": "TCP"},
                ],
                "selector": {"app": service},
                "lb_status": [{"ip": "192.168.1.100", "hostname": "lb.example.com"}],
            },
        ],
        "count": 2,
        "response_size_limit_kb": 128,
    }


async def query_k8s_hpa(service: str, env: str, namespace: str = "default", deployment_name: str = "", **kwargs) -> Dict[str, Any]:
    deployment = deployment_name or service
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment,
        "hpas": [
            {
                "name": f"{deployment}-hpa",
                "min_replicas": 2,
                "max_replicas": 10,
                "current_replicas": 4,
                "desired_replicas": 4,
                "current_metrics": [
                    {"type": "Resource", "resource_name": "cpu", "current_average_utilization": 65},
                ],
                "conditions": [
                    {"type": "AbleToScale", "status": "True", "reason": "ReadyForNewScale", "message": ""},
                    {"type": "ScalingActive", "status": "True", "reason": "ValidMetricFound", "message": ""},
                ],
            }
        ],
        "count": 1,
        "response_size_limit_kb": 128,
    }


async def query_k8s_ingresses(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "ingresses": [
            {
                "name": f"{service}-ingress",
                "namespace": namespace,
                "hosts": [f"{service}.example.com", f"api.{service}.example.com"],
                "tls_enabled": True,
                "ingress_class": "nginx",
                "lb_status": [{"ip": "192.168.2.100", "hostname": "ingress.example.com"}],
            }
        ],
        "count": 1,
        "response_size_limit_kb": 128,
    }


async def query_k8s_statefulsets(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "statefulsets": [
            {
                "name": service,
                "replicas": 3,
                "ready_replicas": 3,
                "current_replicas": 3,
                "current_revision": f"{service}-v1-abc12",
                "update_revision": f"{service}-v1-abc12",
                "status": "running",
            }
        ],
        "count": 1,
        "response_size_limit_kb": 128,
    }


async def query_k8s_daemonsets(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "daemonsets": [
            {
                "name": f"{service}-agent",
                "desired_number_scheduled": 3,
                "current_number_scheduled": 3,
                "number_ready": 3,
                "number_available": 3,
                "status": "running",
            }
        ],
        "count": 1,
        "response_size_limit_kb": 128,
    }


async def query_k8s_configmaps(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "configmaps": [
            {
                "name": f"{service}-config",
                "data_keys": ["application.yml", "logback.xml", "features.json"],
                "binary_data_keys": [],
                "data_sample": {
                    "application.yml": "server:\n  port: 8080\nspring:\n  profiles:\n    active: prod\ndb:\n  max_pool_size: 50",
                    "logback.xml": "<configuration><root level=\"INFO\"/></configuration>",
                    "features.json": '{"feature_a": true, "feature_b": false}',
                },
                "immutable": False,
            }
        ],
        "count": 1,
        "response_size_limit_kb": 128,
    }


async def query_k8s_resource_quotas(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "resource_quotas": [
            {
                "name": "compute-resources",
                "hard": {
                    "limits.cpu": "20",
                    "limits.memory": "64Gi",
                    "requests.cpu": "10",
                    "requests.memory": "32Gi",
                    "count/pods": "100",
                },
                "used": {
                    "limits.cpu": "12",
                    "limits.memory": "38Gi",
                    "requests.cpu": "7",
                    "requests.memory": "22Gi",
                    "count/pods": "45",
                },
            }
        ],
        "count": 1,
        "response_size_limit_kb": 128,
    }


async def query_k8s_pvc(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "pvcs": [
            {
                "name": f"{service}-data",
                "status": "Bound",
                "capacity": "100Gi",
                "access_modes": ["ReadWriteOnce"],
                "storage_class": "ssd",
                "volume_name": "pvc-data-abc123",
            },
            {
                "name": f"{service}-cache",
                "status": "Bound",
                "capacity": "50Gi",
                "access_modes": ["ReadWriteOnce"],
                "storage_class": "ssd",
                "volume_name": "pvc-cache-def456",
            },
        ],
        "count": 2,
        "response_size_limit_kb": 128,
    }


async def query_k8s_replicasets(service: str, env: str, namespace: str = "default", deployment_name: str = "", **kwargs) -> Dict[str, Any]:
    deployment = deployment_name or service
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "deployment_name": deployment,
        "replicasets": [
            {
                "name": f"{deployment}-6b8b8d9d7f",
                "replicas": 3,
                "ready_replicas": 3,
                "available_replicas": 3,
                "images": [f"{service}:v1.5.0"],
                "owner_references": [{"kind": "Deployment", "name": deployment}],
                "creation_timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            },
            {
                "name": f"{deployment}-5a7a7c8c6e",
                "replicas": 0,
                "ready_replicas": 0,
                "available_replicas": 0,
                "images": [f"{service}:v1.4.0"],
                "owner_references": [{"kind": "Deployment", "name": deployment}],
                "creation_timestamp": (datetime.utcnow() - timedelta(hours=48)).isoformat(),
            },
        ],
        "count": 2,
        "response_size_limit_kb": 128,
    }


async def query_k8s_jobs(service: str, env: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
    return {
        "service": service,
        "env": env,
        "namespace": namespace,
        "jobs": [
            {
                "name": f"{service}-data-migration",
                "namespace": namespace,
                "completions": 1,
                "parallelism": 1,
                "succeeded": 1,
                "active": 0,
                "failed": 0,
                "conditions": [{"type": "Complete", "status": "True"}],
            },
            {
                "name": f"{service}-cleanup",
                "namespace": namespace,
                "schedule": "0 3 * * *",
                "suspend": False,
                "last_schedule_time": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                "active_jobs": 0,
            },
        ],
        "count": 2,
        "response_size_limit_kb": 128,
    }


async def mock_write_rca_to_oss(
    run_id: str,
    service: str = "",
    env: str = "",
    content: str = "",
    content_type: str = "markdown",
    **kwargs,
) -> Dict[str, Any]:
    """Return mock OSS RCA write result."""
    ext = "md" if content_type != "json" else "json"
    svc_part = service or "unknown"
    key = f"rca/{svc_part}/{run_id}.{ext}"
    return {
        "run_id": run_id,
        "service": service,
        "env": env,
        "oss_key": key,
        "oss_url": f"https://mock-bucket.oss-cn-hangzhou.aliyuncs.com/{key}",
        "bucket": "mock-bucket",
        "content_type": content_type,
        "response_size_limit_kb": 64,
    }


async def mock_write_evidence_to_oss(
    run_id: str,
    service: str = "",
    env: str = "",
    content: str = "",
    **kwargs,
) -> Dict[str, Any]:
    """Return mock OSS evidence write result."""
    svc_part = service or "unknown"
    key = f"evidence/{svc_part}/{run_id}.json"
    return {
        "run_id": run_id,
        "service": service,
        "env": env,
        "oss_key": key,
        "oss_url": f"https://mock-bucket.oss-cn-hangzhou.aliyuncs.com/{key}",
        "bucket": "mock-bucket",
        "response_size_limit_kb": 64,
    }
