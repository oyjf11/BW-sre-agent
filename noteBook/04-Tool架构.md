# 04 — Tool 架构

> 工具层详解：gateway 调度、schema 注册、adapter 模式、真实平台对接。

---

## 1. 什么是 Tool

在 Agent 语境中，**Tool** 就是 Agent 能调用的外部能力。类比：你的 TypeScript 函数可以调 `fetch()` 访问 HTTP API，Agent 的节点可以调 `gateway.call_tool("query_logs")` 访问运维平台。

OpsPilot 目前有 **20 个 Tool**，分为四类：

| 类别 | 工具数 | 用途 | 例子 |
|------|--------|------|------|
| 诊断查询 | 12 | 收集信息 | query_logs, query_metrics, query_deployments |
| 知识检索 | 2 | 查资料 | query_runbook, query_ticket_by_id |
| 执行控制 | 1 | 干活的 | execute_action |
| 归档存储 | 2 | 存结果 | write_rca_to_oss, write_evidence_to_oss |
| 元数据查询 | 3 | 查配置 | query_service_metadata, query_db_* |

---

## 2. 整体架构

```
Agent Node
    │
    ├─→ gateway.call_tool("query_logs", {...params})
    │       │
    │       ├─→ 1. 查找 handler（mock 或 real）
    │       ├─→ 2. Schema 校验（_validate_params）
    │       ├─→ 3. 选择 adapter（根据 TOOL_ADAPTER_MODE）
    │       ├─→ 4. 执行 + 重试（_execute_with_retry）
    │       ├─→ 5. 审计记录（_log_audit → incident_tool_audits 表）
    │       └─→ 6. 返回 ToolResponse
    │
    └─→ 拿到 result，封装为 EvidenceItem
```

---

## 3. ToolGateway (`backend/app/tools/gateway.py`)

### 3.1 核心接口

```python
class ToolGateway:
    def __init__(self, adapter_mode: str = "mock"):
        self.adapter_mode = adapter_mode
        self.tool_handlers = {}  # tool_name → handler function

    def register(self, tool_name: str, handler: Callable):
        self.tool_handlers[tool_name] = handler

    async def call_tool(self, request: ToolRequest) -> ToolResponse:
        # 1. tracing span
        # 2. handler lookup
        # 3. schema validation
        # 4. adapter selection
        # 5. execute with retry
        # 6. audit log
        # 7. return response
```

### 3.2 Adapter 模式切换

```python
# 通过环境变量 TOOL_ADAPTER_MODE 控制

# mock 模式（默认）→ 使用 mock handler，返回仿真数据
TOOL_ADAPTER_MODE=mock

# real 模式 → 使用真实 adapter，调用真实运维平台
TOOL_ADAPTER_MODE=real
```

**关键设计**：Gateway 从 `Settings` 对象读取配置（而非直接读 `os.getenv`），避免配置漂移。

### 3.3 重试机制

使用 Python `tenacity` 库实现：

```python
@retry(
    stop=stop_after_attempt(2),         # 最多 2 次
    wait=wait_exponential(multiplier=1) # 指数退避
)
async def _execute_with_retry(self, tool_name, handler, params):
    return await handler(params)
```

类比：`p-retry` 库的 `pRetry(fn, { retries: 2 })`。

---

## 4. Tool Schema 注册 (`backend/app/tools/schemas/__init__.py`)

### 4.1 数据结构

```python
# 请求
class ToolRequest:
    tool_name: str          # 工具名称
    params: dict            # 参数
    run_id: str             # 关联的 run

# 响应
class ToolResponse:
    tool_name: str
    success: bool
    result: Any             # 成功时的返回值
    error: str | None       # 失败时的错误信息
    latency_ms: int         # 执行耗时
    timestamp: datetime

# 元数据（注册信息）
class ToolMetadata:
    name: str
    description: str
    parameters_schema: dict  # JSON Schema 格式的参数定义
    risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    requires_approval: bool
    timeout_ms: int
    retries: int
```

### 4.2 全局注册表

```python
TOOL_REGISTRY: dict[str, ToolMetadata] = {
    "query_logs": ToolMetadata(
        name="query_logs",
        description="查询应用日志",
        parameters_schema={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "env": {"type": "string"},
                "keyword": {"type": "string"},
                "time_range_minutes": {"type": "integer"}
            },
            "required": ["service", "env"]
        },
        risk_level="LOW",
        requires_approval=False,
        timeout_ms=30000,
    ),
    # ... 其余 19 个工具
}
```

类比：像 OpenAPI / Swagger 的 schema 定义，描述每个 API 的参数格式。

---

## 5. 完整工具清单

| 工具 | 风险 | 需审批 | Real Adapter | 说明 |
|------|------|--------|-------------|------|
| query_logs | LOW | No | mysql_adapter | 应用日志查询 |
| query_metrics | LOW | No | metrics_adapter | K8s/阿里云指标 |
| query_deployments | LOW | No | k8s_adapter | Deployment 列表 |
| query_runbook | LOW | No | ❌ fail-closed | 运维手册查询 |
| execute_action | HIGH | Yes | ❌ fail-closed | 执行修复动作 |
| query_ticket_by_id | LOW | No | ❌ fail-closed | 外部工单查询 |
| query_service_metadata | LOW | No | ❌ fail-closed | 服务元数据 |
| query_k8s_deployment_status | LOW | No | k8s_adapter | Deployment 状态 |
| query_k8s_pods | LOW | No | k8s_adapter | Pod 列表 |
| query_k8s_events | LOW | No | k8s_adapter | K8s 事件 |
| query_k8s_pod_logs_summary | LOW | No | k8s_adapter | Pod 日志摘要 |
| query_lb_health_status | LOW | No | slb_adapter | SLB 后端健康 |
| query_lb_traffic_metrics | LOW | No | slb_adapter | SLB 流量指标 |
| query_db_processlist | LOW | No | mysql_adapter | MySQL 进程列表 |
| query_db_slow_queries | LOW | No | mysql_adapter | 慢查询 |
| query_db_table_status | LOW | No | mysql_adapter | 表状态 |
| query_db_variables | LOW | No | mysql_adapter | 数据库变量 |
| write_rca_to_oss | LOW | No | oss_adapter | RCA 归档上传 |
| write_evidence_to_oss | LOW | No | oss_adapter | Evidence 归档上传 |

**`❌ fail-closed`** 表示该工具在 `real` 模式下尚未实现真实 adapter，调用会抛 `RuntimeError`。这是安全设计——宁可失败也不返回假数据。

---

## 6. Adapter 模式

### 6.1 Mock Adapter (`adapters/__init__.py`)

所有 20 个工具都有 mock 实现，返回**仿真的结构化数据**。例如：

```python
def mock_query_k8s_deployment_status(params):
    return {
        "deployments": [
            {
                "name": "payment-service",
                "namespace": "production",
                "replicas": 3,
                "ready_replicas": 2,  # ← 故意少一个，模拟故障
                "status": "degraded"
            }
        ]
    }
```

用途：开发调试、演示、单元测试。

### 6.2 真实 Adapter

**MySQL Adapter** (`mysql_adapter.py`)：
```python
# 5 个已实现的工具
query_logs_from_db()        # → SELECT * FROM common_app_log WHERE ...
query_db_processlist()      # → SHOW FULL PROCESSLIST
query_db_slow_queries()     # → 慢查询分析（阈值 5 秒）
query_db_table_status()     # → SHOW TABLE STATUS（按大小排序 top 20）
query_db_variables()        # → SHOW GLOBAL STATUS（15 个关键变量 + buffer_pool_hit_rate）
```

**K8s Adapter** (`k8s_adapter.py`)：
```python
# 5 个已实现的工具
query_k8s_deployment_status()  # → 真实 K8s API 调用
query_k8s_pods()               # → pod 列表（含 phase/ready/restart_count）
query_k8s_events()             # → 事件过滤 + top_reasons 统计
query_k8s_pod_logs_summary()   # → 日志扫描（正则匹配 OOM/timeout/connection refused/...）
query_deployments()            # → deployment 列表（含 images/status/conditions）
```

**Metrics Adapter** (`metrics_adapter.py`)：
```python
query_metrics()  # → 阿里云 CMS API → K8s Pod 指标（CPU/Memory/Network）
```

**SLB Adapter** (`slb_adapter.py`)：
```python
query_lb_health_status()    # → SLB 后端服务器健康状态
query_lb_traffic_metrics()  # → QPS / error_rate / p50 / p99
```

**OSS Adapter** (`oss_adapter.py`)：
```python
write_rca_to_oss()      # → 上传 RCA 报告 markdown
write_evidence_to_oss()  # → 上传 evidence JSON
```

### 6.3 响应大小限制

所有真实 adapter 都有响应大小限制（通常 64KB-128KB），防止超大响应导致内存溢出。超出部分会被截断并标记 `truncated: true`。

---

## 7. 审计机制

每次工具调用都会记录到 `incident_tool_audits` 表：

```sql
-- 审计记录结构
INSERT INTO incident_tool_audits (
    run_id,
    tool_name,
    adapter_mode,     -- mock 还是 real
    request_json,     -- 完整请求
    response_json,    -- 完整响应
    success,          -- 是否成功
    error_message,    -- 错误信息
    latency_ms,       -- 耗时
    created_at
)
```

类比：就像每次 HTTP 请求的 access log。

---

## 8. Tool 在当前流程中的使用

```
planner → 生成 InvestigationTask[] ────┐
                                       ↓
evidence_fanout → 并发执行 → gateway.call_tool() → 每个 task 调一个 tool
                                       ↓
                              成功 → EvidenceItem → state.evidence_items
                              失败 → warning/error（根据 degrade_on_failure）

executor → execute_action() → ControlledExecutor → gateway.call_tool("execute_action")

verify → gateway.call_tool("query_k8s_deployment_status")
       → gateway.call_tool("query_lb_health_status")
       → gateway.call_tool("query_lb_traffic_metrics")

rca → gateway.call_tool("write_rca_to_oss")
    → gateway.call_tool("write_evidence_to_oss")
```

---

## 9. 如何添加新 Tool

```python
# 1. 在 schemas/__init__.py 注册 metadata
TOOL_REGISTRY["my_new_tool"] = ToolMetadata(
    name="my_new_tool",
    description="...",
    parameters_schema={...},
    risk_level="LOW",
    requires_approval=False,
    timeout_ms=15000,
)

# 2. 在 adapters/__init__.py 添加 mock handler
def mock_my_new_tool(params):
    return {"status": "ok", "data": {...}}

# 3. 在 gateway.py 注册 handler
gateway.register("my_new_tool", mock_my_new_tool)

# 4. （可选）实现真实 adapter
# 在 adapters/ 下新建文件，实现真实逻辑
```

---

## 10. 关键文件速查

| 文件 | 作用 |
|------|------|
| `app/tools/gateway.py` | ToolGateway — 调度、校验、重试、审计 |
| `app/tools/schemas/__init__.py` | ToolRequest/ToolResponse/ToolMetadata + TOOL_REGISTRY |
| `app/tools/adapters/__init__.py` | 20 个 mock adapter 实现 |
| `app/tools/adapters/mysql_adapter.py` | 5 个真实 MySQL adapter |
| `app/tools/adapters/k8s_adapter.py` | 5 个真实 K8s adapter |
| `app/tools/adapters/metrics_adapter.py` | 阿里云 CMS 指标 adapter |
| `app/tools/adapters/slb_adapter.py` | SLB 健康/流量 adapter |
| `app/tools/adapters/oss_adapter.py` | OSS 归档 adapter |

---

## 小结

Tool 层的设计哲学：

1. **统一接口** — 所有 tool 通过 `gateway.call_tool()` 调用，对上层透明
2. **Mock/Real 分离** — 开发用 mock，生产切 real，切换只需一个环境变量
3. **安全优先** — 未实现真实 adapter 的工具 fail-closed，宁可失败不给假数据
4. **审计完备** — 每次调用完整记录，可追溯

下一篇：[05 — 数据库设计](./05-数据库设计.md)
