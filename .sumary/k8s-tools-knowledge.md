# OpsPilot K8s 只读工具 — 全量知识文档

> 最后更新：2026-06-03

---

## 一、工具全景

| # | 工具名 | K8s 资源 | 命名空间？ | K8s API 客户端 | 超时 |
|---|--------|----------|-----------|----------------|------|
| 1 | `query_k8s_deployment_status` | Deployment | 是 | AppsV1Api | 15s |
| 2 | `query_k8s_pods` | Pod | 是 | AppsV1Api + CoreV1Api | 15s |
| 3 | `query_k8s_events` | Event | 是 | CoreV1Api | 15s |
| 4 | `query_k8s_pod_logs_summary` | Pod Log | 是 | CoreV1Api | 30s |
| 5 | `query_k8s_nodes` | Node | **否**（集群级） | CoreV1Api | 15s |
| 6 | `query_k8s_services` | Service | 是 | CoreV1Api | 15s |
| 7 | `query_k8s_hpa` | HPA | 是 | AutoscalingV2Api | 15s |
| 8 | `query_k8s_ingresses` | Ingress | 是 | NetworkingV1Api | 15s |
| 9 | `query_k8s_statefulsets` | StatefulSet | 是 | AppsV1Api | 15s |
| 10 | `query_k8s_daemonsets` | DaemonSet | 是 | AppsV1Api | 15s |
| 11 | `query_k8s_configmaps` | ConfigMap | 是 | CoreV1Api | 15s |
| 12 | `query_k8s_resource_quotas` | ResourceQuota | 是 | CoreV1Api | 15s |
| 13 | `query_k8s_pvc` | PVC | 是 | CoreV1Api | 15s |
| 14 | `query_k8s_replicasets` | ReplicaSet | 是 | AppsV1Api | 15s |
| 15 | `query_k8s_jobs` | Job + CronJob | 是 | BatchV1Api | 15s |
| 16 | `query_deployments` | Deployment（跨 ns） | **否**（遍历 allowed_ns） | AppsV1Api | 30s |

**所有工具共享属性**：`risk_level=LOW`、`requires_approval=False`、`retries=1`。

---

## 二、核心架构

### 3 层调用链

```
graph node (_add_k8s_tasks)
  → ToolGateway.call_tool()
    → adapter_mode 判定: mock (adapters/__init__.py) | real (adapters/k8s_adapter.py)
      → K8sClient (clients/k8s_client.py)
        → kubernetes Python SDK
```

### 命名空间安全（fail-closed）

```python
K8sClient.ensure_namespace_allowed(namespace)
  → k8s_allowed_namespaces 为空 → PermissionError  # 所有 real 查询被拒绝
  → namespace 不在白名单中 → PermissionError
  → resolve_target() 是所有命名空间级工具的准入点
```

**例外**：
- `query_k8s_nodes` — 集群级 API，不经过 `resolve_target()`
- `query_deployments` — 通过 `list_all_deployments()` 仅遍历 `allowed_namespaces`

### 响应大小限制

全局 `RESPONSE_SIZE_LIMIT_KB = 128`（128 KB）。

`query_k8s_pod_logs_summary` 额外有 3 级截断机制：
1. 清空 `sample_logs` → 设 `truncated = true`
2. 精简 pod 信息为 `{name, phase, restart_count}`
3. 裁剪 `top_patterns` 到 top 10

---

## 三、配置

文件：`backend/app/core/config.py`

| 配置项 | 类型 | 默认 | 说明 |
|--------|------|------|------|
| `k8s_config_path` | `str` | `""` | kubeconfig 路径；空则先试 incluster 再试默认 kubeconfig |
| `k8s_context` | `str` | `""` | K8s context 名称 |
| `k8s_allowed_namespaces` | `List[str]` | `[]` | 命名空间白名单；空则 fail-closed |
| `k8s_cluster_id` | `str` | `""` | 阿里云集群 ID（CMS/metrics adapter 用） |

---

## 四、各工具输入输出详情

### 通用参数约定
- `service`（string, required）
- `env`（string, required）
- `namespace`（string, optional, 默认 `"default"`）
- `deployment_name`（string, optional, 默认同 `service`）

---

### query_k8s_deployment_status

**额外参数**：`namespace`, `deployment_name`

**返回值**：
```python
{
    "service": str,
    "env": str,
    "deployment_name": str,
    "status": "running" | "degraded" | "unavailable",
    "replicas": int,
    "ready_replicas": int,
    "unavailable_replicas": int,
    "last_rollout": str | None,   # ISO timestamp
}
```
**注意**：不含 `response_size_limit_kb`（与其他工具不同）。

---

### query_k8s_pods

**额外参数**：`namespace`, `deployment_name`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str, "deployment_name": str,
    "pods": [{
        "name": str, "phase": str, "ready": bool,
        "restart_count": int, "node_name": str,
        "pod_ip": str, "start_time": str | None,
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```

---

### query_k8s_events

**额外参数**：`namespace`, `deployment_name`, `limit`（integer, optional, 钳制 [1, 50], 默认 20）

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str, "deployment_name": str,
    "events": [{
        "reason": str, "message": str,
        "type": "Normal" | "Warning",
        "object": str, "timestamp": str | None,
    }],
    "top_reasons": [{"reason": str, "count": int}],  # top 10
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤逻辑**：`involved_object.name` 匹配 deployment_name 或 pod_name，或 service 子串匹配。

---

### query_k8s_pod_logs_summary

**额外参数**：`namespace`, `deployment_name`, `tail_lines`（integer, optional, 钳制 [1, 500], 默认 100）, `limit_pods`（integer, optional, 钳制 [1, 10], 默认 5）

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str, "deployment_name": str,
    "tail_window": int,         # 实际使用的 tail_lines
    "lines_scanned": int,
    "pod_count": int,
    "pods": [{...}],            # 同 _serialize_pod()
    "top_patterns": [{"pattern": str, "count": int}],  # top 10
    "sample_logs": [{"pod": str, "pattern": str, "line": str}],  # 最多 20 条
    "truncated": bool,
    "response_size_limit_kb": 128,
}
```

**6 个日志模式扫描规则**（首次命中即停止）：

| 顺序 | 标签 | 正则 |
|------|------|------|
| 1 | `oom` | `(oom\|out of memory\|killed)` |
| 2 | `timeout` | `(timeout\|timed out)` |
| 3 | `connection_refused` | `connection refused` |
| 4 | `backoff` | `(back[- ]?off\|crashloopbackoff)` |
| 5 | `exception` | `(exception\|traceback)` |
| 6 | `error` | `\berror\b` |

---

### query_k8s_nodes

**额外参数**：无（仅 `service`, `env`）

**返回值**：
```python
{
    "service": str, "env": str,
    "nodes": [{
        "name": str,
        "role": "control-plane" | "master" | "worker",
        "conditions": {str: str},     # e.g. {"Ready": "True", "MemoryPressure": "False"}
        "capacity_cpu": str, "capacity_memory": str,
        "allocatable_cpu": str, "allocatable_memory": str,
        "kubelet_version": str, "kernel_version": str, "container_runtime": str,
        "unschedulable": bool,
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**注意**：集群级查询，不依赖 namespace。

---

### query_k8s_services

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "services": [{
        "name": str, "type": str,  # ClusterIP / LoadBalancer / NodePort
        "cluster_ip": str, "external_ip": [str],
        "ports": [{"name": str, "port": int, "target_port": str, "protocol": str}],
        "selector": {str: str},
        "lb_status": [{"ip": str|None, "hostname": str|None}] | None,
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤**：仅返回 name 包含 `service` 子串（大小写不敏感）的 Service。

---

### query_k8s_hpa

**额外参数**：`namespace`, `deployment_name`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str, "deployment_name": str,
    "hpas": [{
        "name": str,
        "min_replicas": int, "max_replicas": int,
        "current_replicas": int, "desired_replicas": int,
        "current_metrics": [{
            "type": str, "resource_name": str | None,
            "current_average_utilization": int | None,
            "current_average_value": str | None,
        }],
        "conditions": [{"type": str, "status": str, "reason": str, "message": str}],
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤**：仅返回 `scale_target_ref.name` 含 `deployment_name` 子串的 HPA。

---

### query_k8s_ingresses

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "ingresses": [{
        "name": str, "namespace": str,
        "hosts": [str], "tls_enabled": bool,
        "ingress_class": str,
        "lb_status": [{"ip": str|None, "hostname": str|None}] | None,
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤**：仅返回 name 或 backend service name 含 `service` 子串的 Ingress。

---

### query_k8s_statefulsets

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "statefulsets": [{
        "name": str,
        "replicas": int, "ready_replicas": int, "current_replicas": int,
        "current_revision": str, "update_revision": str,
        "status": "running" | "degraded" | "unavailable",
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**健康判定**：`ready >= replicas and replicas > 0` → running；`ready > 0` → degraded；否则 unavailable。

---

### query_k8s_daemonsets

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "daemonsets": [{
        "name": str,
        "desired_number_scheduled": int, "current_number_scheduled": int,
        "number_ready": int, "number_available": int,
        "status": "running" | "degraded" | "unavailable",
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**健康判定**：`ready >= desired and desired > 0` → running；`ready > 0` → degraded；否则 unavailable。

---

### query_k8s_configmaps

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "configmaps": [{
        "name": str,
        "data_keys": [str], "binary_data_keys": [str],
        "data_sample": {str: str},  # 值截断 500 chars；敏感值 → "***REDACTED***"
        "immutable": bool,
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**脱敏规则**：adapter 层检测 data key 是否含以下子串（大小写不敏感），命中则脱敏：

```
password, secret, token, api_key, access_key, private_key, key, cert, tls
```

---

### query_k8s_resource_quotas

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "resource_quotas": [{
        "name": str,
        "hard": {str: str},  # 硬限制资源→量
        "used": {str: str},  # 已用资源→量
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```

---

### query_k8s_pvc

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "pvcs": [{
        "name": str,
        "status": str,         # e.g. "Bound", "Pending"
        "capacity": str,       # 存储容量
        "access_modes": [str], # e.g. ["ReadWriteOnce"]
        "storage_class": str,
        "volume_name": str,
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤**：仅返回 name 含 `service` 子串的 PVC。

---

### query_k8s_replicasets

**额外参数**：`namespace`, `deployment_name`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str, "deployment_name": str,
    "replicasets": [{
        "name": str,
        "replicas": int, "ready_replicas": int, "available_replicas": int,
        "images": [str],
        "owner_references": [{"kind": str, "name": str}],
        "creation_timestamp": str | None,  # ISO timestamp
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤**：返回 name 或 owner_references.name 含 `deployment_name` 子串的 ReplicaSet。

---

### query_k8s_jobs

**额外参数**：`namespace`

**返回值**：
```python
{
    "service": str, "env": str, "namespace": str,
    "jobs": [               # Job 和 CronJob 混合列表
        # Job:
        {
            "name": str, "namespace": str,
            "completions": int | None, "parallelism": int | None,
            "succeeded": int, "active": int, "failed": int,
            "conditions": [{"type": str, "status": str}],
        },
        # CronJob:
        {
            "name": str, "namespace": str,
            "schedule": str, "suspend": bool,
            "last_schedule_time": str | None,
            "active_jobs": int,
        },
    ],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**过滤**：返回 name 含 `service` 子串的 Job 和 CronJob，合并到 `jobs` 列表。

---

### query_deployments

**额外参数**：`time_range`（object, optional, 未实际使用）

**返回值**：
```python
{
    "service": str, "env": str,
    "deployments": [{
        "deployment_id": str,      # f"{namespace}/{name}"
        "service": str, "namespace": str,
        "images": [str], "version": str,  # version = first image
        "replicas": int, "ready_replicas": int,
        "timestamp": str,           # creation_timestamp ISO
        "status": "success" | "progressing" | "failed",
        "conditions": [{"type": str, "status": str, "message": str}],
    }],
    "count": int,
    "response_size_limit_kb": 128,
}
```
**status 判定**：`Available=True` → success；`Progressing=True` → progressing；否则 failed。

**过滤**：`service` 作为 deployment name 或 namespace 子串匹配。遍历所有 `allowed_namespaces`，单 ns 失败不影响其他。

---

## 五、Incident Type → 工具调度矩阵

文件：`backend/app/graph/nodes/__init__.py`，函数 `_add_k8s_tasks()`

| Incident Type | 调度工具（数字 = 优先级，越小越优先） |
|---------------|--------------------------------------|
| **resource_exhaustion** | 1: nodes, 2: deployment_status + pods + hpa, 3: events(20) + resource_quotas, 4: pod_logs_summary(100) + pvc |
| **dependency_failure** | 2: deployment_status + events(20) + services, 3: pod_logs_summary(100) + ingresses |
| **deployment_regression** | 2: deployment_status, 3: pods + events(20) + replicasets, 4: configmaps |
| **default / unknown** | 3: deployment_status + pods, 4: nodes + services + hpa, 5: statefulsets + daemonsets + jobs |

调度时 `namespace`/`deployment_name` 不传入，由 adapter 的 `resolve_target()` 自动推导（默认 ns = `"default"`，默认 deploy = service_name）。

---

## 六、K8sClient 方法 → API 映射

| K8sClient 方法 | API 客户端 | API 调用 | 校验 NS？ |
|---------------|-----------|----------|-----------|
| `resolve_target` | 本地逻辑 | - | **是** |
| `get_deployment` | AppsV1Api | `read_namespaced_deployment` | 否 |
| `get_deployment_status` | AppsV1Api | via `get_deployment()` | 否 |
| `list_pods_for_target` | AppsV1Api + CoreV1Api | `read_namespaced_deployment` → label selector → `list_namespaced_pod` | 否 |
| `list_events` | CoreV1Api | `list_namespaced_event` | 否 |
| `read_pod_log` | CoreV1Api | `read_namespaced_pod_log`（timestamp=True） | 否 |
| `list_nodes` | CoreV1Api | `list_node`（集群级） | 否 |
| `list_services` | CoreV1Api | `list_namespaced_service` | **是** |
| `list_hpas` | AutoscalingV2Api | `list_namespaced_horizontal_pod_autoscaler` | **是** |
| `list_ingresses` | NetworkingV1Api | `list_namespaced_ingress` | **是** |
| `list_statefulsets` | AppsV1Api | `list_namespaced_stateful_set` | **是** |
| `list_daemonsets` | AppsV1Api | `list_namespaced_daemon_set` | **是** |
| `list_configmaps` | CoreV1Api | `list_namespaced_config_map` | **是** |
| `get_configmap` | CoreV1Api | `read_namespaced_config_map` | **是** |
| `list_resource_quotas` | CoreV1Api | `list_namespaced_resource_quota` | **是** |
| `list_pvcs` | CoreV1Api | `list_namespaced_persistent_volume_claim` | **是** |
| `list_replicasets` | AppsV1Api | `list_namespaced_replica_set` | **是** |
| `list_jobs` | BatchV1Api | `list_namespaced_job` | **是** |
| `list_cronjobs` | BatchV1Api | `list_namespaced_cron_job` | **是** |
| `list_all_deployments` | AppsV1Api | `list_namespaced_deployment`（每个 allowed_ns 一次） | 隐式 |

---

## 七、辅助函数速查

文件：`backend/app/tools/adapters/k8s_adapter.py`

| 函数 | 职责 |
|------|------|
| `_resolve_k8s_target(service, env, params)` | 提取 namespace（默认 "default"）、deployment_name（默认 service） |
| `_serialize_pod(pod)` | Pod 对象 → `{name, phase, ready, restart_count, node_name, pod_ip, start_time}` |
| `_event_timestamp(event)` | 提取最佳时间戳：`last_timestamp > event_time > first_timestamp > creation_timestamp > datetime.min` |
| `_json_size_bytes(data)` | JSON 序列化后 UTF-8 字节数 |
| `_truncate_logs_summary(payload)` | 3 级截断：sample_logs → pods → top_patterns |

---

## 八、Gateway 适配器路由

文件：`backend/app/tools/gateway.py`

```
TOOL_ADAPTER_MODE（环境变量）
  ├─ "mock" → 使用 tool_handlers 中的 mock handler（adapters/__init__.py）
  └─ "real" → select_adapter(tool_name) 返回 real adapter（adapters/k8s_adapter.py）
               → 无 real adapter 的工具 → 返回错误
```

`ToolGateway.call_tool()` 流程：
1. 查 handler → 验证 params schema → `select_adapter()` 选适配器
2. tenacity 重试（最多 2 次，指数退避 1-10s）
3. 注入 `_adapter_info`（`"mock"` 或 `"real"`）到结果
4. 审计日志 → 持久化到 `IncidentToolAudit` 表

---

## 九、关键设计原则

1. **fail-closed**：`k8s_allowed_namespaces` 为空 → 所有 real 查询 `PermissionError`
2. **每次调用创建新 K8sClient**，API 客户端通过 `lru_cache` 缓存（按 config_path+context）
3. **`verify_ssl = False`** — 在 `_get_api_clients()` 无条件设置
4. **`list_all_deployments` 静默容错**：单 ns 失败继续其他 ns
5. **所有 async def**：real adapter 通过 `asyncio.to_thread()` 调用阻塞 K8s SDK
6. **ConfigMap 脱敏**：adapter 层独立脱敏，不依赖 gateway audit 的 `_sanitize_for_audit()`
7. **日志扫描首次匹配**：6 个正则按优先级顺序执行，命中即停止

---

## 十、涉及文件清单

| 文件 | 角色 |
|------|------|
| `backend/app/core/config.py` | K8s 配置项（k8s_config_path 等） |
| `backend/app/tools/clients/k8s_client.py` | K8sClient — 20 个底层 API 方法 |
| `backend/app/tools/adapters/k8s_adapter.py` | Real adapter — 16 个 async tool 函数 + 5 个辅助函数 |
| `backend/app/tools/adapters/__init__.py` | Mock adapter — 16 个 mock tool 函数 |
| `backend/app/tools/gateway.py` | ToolGateway — 注册/路由/重试/审计 |
| `backend/app/tools/schemas/__init__.py` | ToolRequest / ToolResponse / ToolMetadata / TOOL_REGISTRY |
| `backend/app/graph/nodes/__init__.py` | `_add_k8s_tasks()` — incident_type → 工具调度 |
| `backend/app/tests/test_k8s_adapter.py` | 16 个单元测试（mock + real routing） |
