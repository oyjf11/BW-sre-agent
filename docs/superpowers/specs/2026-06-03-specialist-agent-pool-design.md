# OpsPilot Specialist Agent Pool Design

## 目标

将 `evidence_fanout_node` 从 `asyncio.gather` 纯工具并行调用升级为 5 个独立 Specialist
Agent 组成的分析池。每个 Agent 自带 ReAct 循环，对工具返回的原始数据做一级分析，
产出结构化分析结论（`SpecialistAnalysis`），而非 raw data。

不改变 StateGraph 拓扑骨架。`planner_node` 的产出从 tool 级任务升级为 agent 级任务。
`evidence_aggregate_node` 升级为跨 Agent 全局关联分析（关联图 + 因果链 + 矛盾检测）。
下游节点（diagnose、critic、remediation、rca）本轮不改。

通过 `AGENT_FEATURE_SPECIALIST_POOL` feature flag 控制新旧路径切换。

## 当前问题

| 痛点 | 表现 | 根因 |
|------|------|------|
| 证据采集缺乏分析能力 | 工具返回的 raw payload 未经分析，aggregate 只能做规则评分 | 每个工具调用是纯数据拉取，无推理 |
| 异常信号被淹没 | 几百条 K8s events 中 1 条 CrashLoopBackOff → aggregate 无法识别 | 无结构化分析 |
| 工具调用间无关联分析 | K8s pod 重启时间与 DB 慢查询时间窗口的关系未被发现 | 各工具独立返回，无 Agent 做交叉推理 |

## 范围

### 本轮包含

- 新增 `SpecialistAgent` 类：ReAct 循环（max 3 rounds）+ 4 层降级路径 + 5 类规则兜底。
- 新增 5 个 Agent 配置（YAML 静态加载）：K8s / DB / Log / Metrics / Deployment。
- 重写 `evidence_fanout_node`：feature flag 双路径，Agent 并行调用，双写 `specialist_analyses` + `evidence_items`。
- 重写 `evidence_aggregate_node`：跨 Agent 关联图 + DFS 因果链 + 6 条矛盾规则 + 加权质量评分。
- 改造 `planner_node`：产出 `AgentTask` 列表，同时双写旧 `plan` 格式。
- 新增 6 个 Pydantic 模型 + 4 个 State 字段。
- 新增 `gateway.get_tool_schema()`：返回 OpenAI function calling 兼容 JSON Schema。
- tool_names 白名单边界校验（初始化时 3 项检查）。
- `AGENT_FEATURE_SPECIALIST_POOL` feature flag + .env 控制。
- mock LLM 单元测试（8 类）+ mock adapter 集成测试（6 类）。

### 本轮不包含

- Dynamic Orchestrator（方案三：LLM 驱动的多轮按需调度 Agent）。
- Supervisor Agent（方案二：择一 Agent 主导全局决策）。
- 从管理 API/DB 动态加载 Agent 配置（v2 演进）。
- critic_node / diagnose_node / rca_node / remediation_node 改造。
- `_category_applies()` 智能裁剪（v1 全调度 5 个 Agent）。
- 实时热更新 Agent system_prompt。

## 架构

```
planner_node（改造）
  │  产出 AgentTask 列表（5 个）+ 旧 plan（双写兼容）
  │
  ▼
evidence_fanout_node（改造：feature flag 双路径）
  │
  │  AGENT_FEATURE_SPECIALIST_POOL=true:
  │    agent_tasks → SpecialistAgent.run() × N (asyncio.gather 并行)
  │    → specialist_analyses (新增) + evidence_items (重建兼容)
  │
  │  AGENT_FEATURE_SPECIALIST_POOL=false:
  │    plan.tasks → _collect_one() (原逻辑)
  │
  ▼
evidence_aggregate_node（改造：v2）
  │  消费 specialist_analyses
  │    → _build_correlation_graph() → _infer_causual_chains()
  │    → _detect_cross_agent_contradictions() → _compute_weighted_quality()
  │
  ▼
diagnose_node（无改动） → critic_node（无改动） → ...
```

### Feature flag 配置

在 `backend/app/core/config.py` 的 `Settings` 中新增字段：

```python
agent_feature_specialist_pool: bool = False
```

.env 配置：`AGENT_FEATURE_SPECIALIST_POOL=true`。默认 `false`（渐进式上线）。

访问方式：`get_settings().agent_feature_specialist_pool`。
作用域：仅 `planner_node`、`evidence_fanout_node`、`evidence_aggregate_node` 中读取。

### Feature flag 数据流

```
AGENT_FEATURE_SPECIALIST_POOL=true:
  planner_node → state["agent_tasks"] + state["plan"]
  evidence_fanout_node_v2 → 读 agent_tasks → SpecialistAgent.run()
  evidence_aggregate_node_v2 → 读 specialist_analyses

AGENT_FEATURE_SPECIALIST_POOL=false:
  planner_node → state["plan"]
  evidence_fanout_node → 读 plan → _collect_one()
  evidence_aggregate_node → 读 evidence_items
```

### agent_tasks 降级链（三级 fallback）

fanout 读取 agent_tasks 的三级降级：

| 优先级 | 数据源 | 触发条件 | 行为 |
|--------|--------|---------|------|
| 1 | `state["agent_tasks"]` 非空 | 正常 v2 路径 | 直接使用 |
| 2 | `state["plan"]` 有 tasks | agent_tasks 为空（如 checkpoint resume） | `fallback_from_plan()` 转为 AgentTask 列表 |
| 3 | 两者都为空 | planner 完全失败 / 空工单 | 生成 5 个默认 AgentTask（必含 service，timeout_ms=30000） |

第 3 级默认 AgentTask 结构：`agent_id=f"{cat}_specialist"`, `category=cat`, `service=从 ticket 提取`。保证 fanout 在任何极端情况下仍可执行，只是缺少 incident_type 等上下文。

### specialist_analyses 与 evidence_items 并存

| 字段 | 职责 | 消费方 |
|------|------|--------|
| `evidence_items`（已有） | raw 工具返回数据（EvidenceItem），保持与现有节点兼容 | diagnose_node、rca_node |
| `specialist_analyses`（新增） | Agent 分析后的结构化结论（SpecialistAnalysis） | evidence_aggregate_v2 |

fanout 同时写入两套数据。aggregate_v2 只读不写 evidence_items。diagnose 和 rca 无需改动。

## 状态模型

### AgentRunStatus

```
START → COMPLETED | TIMEOUT | LLM_FAILED
TIMEOUT ──→ PARTIAL (有 raw data) 或 LLM_FAILED (无 raw data)
LLM_FAILED ──→ PARTIAL (有 raw data) 或 LLM_FAILED (无 raw data)
```

`DEGRADED` 枚举保留，当前代码路径不可达，仅供未来扩展。

### 降级层级 L0–L3

| 层级 | 触发条件 | run_status | partial | confidence |
|------|---------|------------|---------|------------|
| L0 | LLM 产出合法 JSON | COMPLETED | False | LLM 自评（代码封顶 0.9） |
| L1 | LLM 返回但 JSON 解析失败 | PARTIAL | True | 0.25（固定） |
| L2 | LLM 超时/失败，有 raw data | PARTIAL | True | 0.25（固定） |
| L3 | 无 LLM + 无 data | LLM_FAILED | True | 0.0 |

### ReAct 循环状态

| 条件 | 行为 |
|------|------|
| round < max_tool_rounds AND remaining_ms ≥ 2000 AND LLM 返回 tool_calls | 执行工具调用，进入下一轮 |
| LLM 返回 tool_calls=None | 退出循环，进入 Phase 2 |
| remaining_ms < 2000 | 标记 TIMEOUT，退出循环 |
| round == max_tool_rounds-1 且仍返回 tool_calls | 标记 truncated=True，退出循环 |
| LLM 调用抛异常 | 标记 LLM_FAILED，退出循环 |

**时间预算严格优先于轮次**：每轮前检查 `deadline - now()`，< 2s 强制退出。
LLM 调用 `asyncio.wait_for(timeout=min(remaining_ms/1000, 15.0))`。
单工具调用 ≤ 30s，且 ≤ 剩余 Agent 预算 / len(tool_calls)。

### partial / truncated 下游处理约定

- `partial=True`：evidence_aggregate_v2 降权 confidence×0.5；diagnose 标记为降级分析。
- `truncated=True`：aggregate 在 evidence_summary 中标注截断。
- critic：partial 比例 ≥ 40% → 触发 NEED_MORE_EVIDENCE。truncated 不自动触发。

## 组件行为

### 5 种 Specialist Agent（工具归属边界）

每个工具只归属于一个 Agent，`tool_names` 白名单互不相交。

| Agent | 独占工具 | 核心职责 | 输出重点 |
|-------|---------|---------|---------|
| K8s | `query_k8s_deployment_status`, `query_k8s_pods`, `query_k8s_events` | Deployment 状态、Pod 生命周期、集群 Events | Pod 级别健康信号 |
| DB | `query_db_processlist`, `query_db_slow_queries`, `query_db_table_status`, `query_db_variables` | 连接池、慢查询、锁等待、配置参数 | DB 是否是瓶颈/受害者 |
| Log | `query_logs` | 应用层日志：ERROR/WARN、异常堆栈、错误模式聚合 | 应用视角异常信号 |
| Metrics | `query_metrics` | K8s Pod CPU/Memory + 阿里云 CMS 业务指标（QPS, P95, error rate） | 指标趋势分析 |
| Deployment | `query_deployments` | 发布变更历史、版本 diff、灰度比例、回滚历史 | 发布是否诱发故障 |

边界澄清：
- `query_k8s_pod_logs_summary`（K8s Specialist）：容器 stdout/stderr 尾部摘要，K8s 视角。
- `query_logs`（Log Specialist）：集中式日志平台全文检索，应用视角，是应用日志唯一入口。
- `query_k8s_deployment_status`（K8s Specialist）：K8s Deployment 实时状态。
- `query_deployments`（Deployment Specialist）：发布系统变更历史记录。
- Metrics Specialist 是唯一指标查询入口；K8s Specialist 不查询指标。

### SpecialistAgent ReAct 循环

```text
run(agent_task, run_id):
  Phase 1: for round in 0..max_tool_rounds-1:
    check remaining time → timeout? break
    llm_client.complete_async(messages, tools) → timeout? break | error? LLM_FAILED
    if no tool_calls: break
    asyncio.gather gateway.call_tool() × N (return_exceptions=True)
    inject results into messages
  Phase 2: _produce_final_analysis(round_truncated)
    L0: LLM → JSON → COMPLETED
    L1: JSON parse fail → _build_degraded_analysis() → PARTIAL
    L2: LLM fail + raw data → _build_degraded_analysis() → PARTIAL
    L3: no LLM + no data → LLM_FAILED
```

`return_exceptions=True`：单工具失败不中断整轮。共享 ToolGateway 保证审计一致性。

### 规则兜底（_extraact_signals_by_rules）

| Agent | 规则 |
|-------|------|
| K8s | containerStatuses.waiting.reason ∈ {CrashLoopBackOff, ErrImagePull, OOMKilled} → AnomalySignal；readyReplicas < desiredReplicas → warning |
| DB | COMMAND≠'Sleep' 连接数 > 50 → warning；slow_queries 行数 > 10 → anomaly |
| Log | 正则计数 `ERROR\|FATAL\|Exception` > 10 → warning |
| Metrics | 相邻两点变化率 > 50% → anomaly |
| Deployment | 最近部署 < 2h → correlation_hint(target="k8s" or "logs", confidence=0.6, source="rule") |

### agent_configs.yaml 与配置加载

v1 采用启动时 YAML 硬编码，不依赖 DB：
- 路径：`backend/app/graph/nodes/agent_configs.yaml`
- `load_agent_configs()` 加载为 `Dict[str, SpecialistAgentConfig]`
- 每个 config 调用 `validate_agent_config()`，校验失败 → `enabled=False`
- `AGENT_FEATURE_SPECIALIST_POOL=true` 时加载并实例化；false 时跳过
- 每个 Agent 配置含 `system_prompt_version: "1.0.0"` 字段，写入 `SpecialistAnalysis.execution_summary` 用于问题追溯

校验规则（3 项，任一失败即 disable）：
1. `tool_names` 不含 `FORBIDDEN_TOOLS = {"execute_action"}`
2. 工具前缀匹配 category（如 K8s Agent 只能调 `query_k8s_*`）
3. 工具在 gateway 中已注册（`describe_capability` 检查，未注册仅 warning 不阻断）

配置加载失败处理：
| 场景 | 行为 |
|------|------|
| YAML 文件不存在 | 所有 Agent disabled → fanout 自动 fallback 到 `_collect_one()` 原路径 |
| 单个 Agent YAML 解析错误 | 该 Agent disabled，其余正常加载 |
| 全部 disabled | fanout 走原路径，对下游无影响 |

prompt 变更流程：
1. 修改 `agent_configs.yaml` → 递增 `system_prompt_version` → PR + code review
2. staging 验证 → prod 滚动发布
3. 通过 execution_summary 中的 version 追溯到每次分析使用的 prompt 版本

### evidence_fanout_node 改造

```python
if not settings.agent_feature_specialist_pool:
    return _original_evidence_fanout(state)  # 回退

# v2 路径
agent_tasks = state["agent_tasks"] or fallback_from_plan(state["plan"])
# 三级 fallback：plan 也为空 → 生成 5 个默认 AgentTask
if not agent_tasks:
    agent_tasks = _build_default_agent_tasks(ticket)

for task in agent_tasks:
    config = agent_configs[task.agent_id]
    if not config.enabled:
        specialist_results.append(_build_llm_failed_shell(task))  # 空壳
        continue
    enabled_tasks.append(task)

# Phase 1: 并行执行所有 Agent
results = await asyncio.wait_for(
    asyncio.gather(*[
        SpecialistAgent(agent_configs[t.agent_id]).run(t, run_id)
        for t in enabled_tasks
    ]),
    timeout=60.0  # 总超时 60s
)

# Phase 2: Agent 级原子写入（顺序，保证一致性）
for result in results:
    agent_evidence = []
    for tool_name, raw_result in result.raw_tool_results.items():
        agent_evidence.append(_build_raw_evidence_item(tool_name, raw_result, result, run_id))
    try:
        state["evidence_items"].extend(agent_evidence)
        state["specialist_analyses"].append(result.model_dump())
    except Exception:
        # 回滚已写入的 evidence，保证 Agent 级原子性
        evidence_set = set(id(e) for e in agent_evidence)
        state["evidence_items"] = [e for e in state["evidence_items"] if id(e) not in evidence_set]
        # 注入降级空壳
        state["specialist_analyses"].append(
            _build_degraded_shell(result.agent_id, result.agent_category, error="write_failed", partial=True)
        )
```

### evidence_aggregate_node 升级 v2

```text
输入: state["specialist_analyses"]
  入口防御：每条 analysis 统一做 isinstance(obj, dict) 检查，兼容 checkpoint 反序列化
处理:
  1. _build_correlation_graph(concrete_hints) → 邻接表
     concrete: confidence ≥ 0.6 的 hint
     speculative: 0.3 ≤ confidence < 0.6（仅辅助提示）
     < 0.3: 丢弃
  2. _infer_causual_chains(graph, anomalies) → 因果链
     - 入度=0 为起点，DFS 收集路径
     - 路径上每个节点必须有 ≥1 个 anomaly
     - 按平均权重降序，取前 5
  3. _detect_cross_agent_contradictions(analyses_raw) → 矛盾列表
     直接按 SpecialistAnalysis.agent_category 分类（无需 SIGNAL_CATEGORY_MAP）
     取 conclusion 前缀（"正常:" / "异常:" / "部分:" / "失败:"）进行规则匹配
     6 条硬编码矛盾规则
  4. _compute_weighted_quality(analyses_raw) → 质量分
     avg = sum(conf × 0.5 if partial else conf) / N
     penalty = max(1 - 0.1 × truncated_count, 0.5)
     coverage = min(active_categories / 5, 1.0)
     return max(avg × penalty × coverage, 0.0)
  5. _format_global_summary() → evidence_summary 文本
输出:
  state["evidence_summary"], state["evidence_quality_score"]
  state["cross_agent_causual_chains"], state["contradiction_signals"]
```

conclusion 前缀约定：`正常:` / `异常:` / `部分:` / `失败:`。aggregate 通过前缀快速分类，
不依赖 LLM 比对。

矛盾规则（6 条）：
- K8s 异常 + Metrics 正常 → "可能非资源级故障"
- K8s 异常 + Deployment 正常 → "故障可能非发布导致"
- DB 异常 + K8s 正常 → "DB 自身问题，非容器层"
- DB 异常 + Metrics 正常 → "可能是慢查询/锁争用等非资源瓶颈"
- Log 异常 + K8s 正常 → "应用层故障，非基础设施"
- Metrics 异常 + K8s 正常 → "资源压力未导致 Pod 级故障"

### planner_node 改造

从「生成 tool 级任务」改为「生成 agent 级任务」：

```python
agent_tasks = []
for cat in ["k8s", "db", "logs", "metrics", "deployments"]:
    if _category_applies(cat, incident_type, service):  # v1 始终 True
        agent_tasks.append(AgentTask(
            agent_id=f"{cat}_specialist",
            category=cat,
            service=service, env=env,
            incident_type=incident_type,
            time_window_start=time_start, time_window_end=time_end,
        ))
state["agent_tasks"] = [t.model_dump() for t in agent_tasks]
state["plan"] = {"tasks": [task_to_legacy(t) for t in agent_tasks], "rationale": rationale}
```

## 数据模型与 State 改动

### 新增 Pydantic 模型（planning.py）

| 模型 | 核心字段 |
|------|---------|
| `AgentRunStatus(Enum)` | COMPLETED, PARTIAL, DEGRADED, TIMEOUT, LLM_FAILED |
| `AgentTask` | agent_id, category, service, env, incident_type, time_window_start/end, extra_context, timeout_ms |
| `AnomalySignal` | signal_type, evidence_ref, description, timestamp_hint |
| `CorrelationHint` | source_category（代码填入）, target_category, reason, confidence(0-1), source("rule"\|"llm") |
| `SpecialistEvidence` | evidence_id, category, conclusion（前缀约束）, severity, anomalies[], correlation_hints[] |
| `SpecialistAnalysis` | agent_id, agent_category, evidence_items[], collected_tool_names[], raw_tool_results{}, execution_summary, confidence(0-1), run_status, partial, truncated |

`InvestigationPlan` / `InvestigationTask` 标记 `@deprecated`，不删除。

### State 新增字段（state.py）

```python
agent_tasks: List[Dict[str, Any]]              # planner → fanout
specialist_analyses: List[Dict[str, Any]]       # fanout → aggregate
cross_agent_causual_chains: List[Dict[str, Any]] # aggregate 产出
contradiction_signals: List[Dict[str, Any]]      # aggregate 产出
```

所有 State 字段使用 `List[Dict[str, Any]]` 以保证 checkpoint 反序列化兼容。

### Pydantic vs dict 二义性防护

从 checkpoint 反序列化后的 `specialist_analyses` 元素是 dict 而非 Pydantic 对象。
所有访问必须兼容两种形式：

```python
cat = obj.get("agent_category", "") if isinstance(obj, dict) else obj.agent_category
```

### 文件变更清单

| 文件 | 动作 | 内容 |
|------|------|------|
| `backend/app/graph/nodes/specialist_agent.py` | CREATE | SpecialistAgent 类 + ReAct 循环 + 降级 |
| `backend/app/graph/nodes/agent_configs.yaml` | CREATE | 5 个 Agent 静态配置 |
| `backend/app/graph/nodes/aggregator.py` | CREATE | 关联图/因果链/矛盾检测/质量评分纯函数 |
| `backend/app/graph/nodes/__init__.py` | MODIFY | 重写 planner、fanout、aggregate 三个节点 |
| `backend/app/graph/state.py` | MODIFY | 新增 4 个 State 字段 |
| `backend/app/models/planning.py` | MODIFY | 新增 6 个模型 + deprecated 标记 |
| `backend/app/core/config.py` | MODIFY | 新增 `AGENT_FEATURE_SPECIALIST_POOL` |
| `backend/app/tools/gateway.py` | MODIFY | 新增 `get_tool_schema()` |
| `backend/app/graph/builder.py` | NO CHANGE | 图拓扑不变，节点函数签名不变 |

## API 契约

### AgentTask（planner → fanout 输入）

```
agent_id: str          # 对应 SpecialistAgentConfig.agent_id
category: str          # k8s / db / logs / metrics / deployments
service: str           # 目标服务名
env: str               # 目标环境
incident_type: str     # 从 triage 传入
time_window_start: Optional[str]  # ISO 8601
time_window_end: Optional[str]    # ISO 8601
extra_context: Dict[str, Any]     # title/description 等
timeout_ms: int = 30000
```

### SpecialistAnalysis（Agent.run() 输出）

```
agent_id: str
agent_category: str
evidence_items: List[SpecialistEvidence]  # ≥ 1（含全部 anomaly 的单个 SE）
collected_tool_names: List[str]  # Agent 成功调用过的工具名
raw_tool_results: Dict[str, Any]  # 工具名 → 原始返回
execution_summary: str
confidence: float [0.0, 1.0]
run_status: AgentRunStatus
partial: bool        # True = 降级分析
truncated: bool      # True = 因超时/轮次被截断
```

### gateway.get_tool_schema()

从 TOOL_REGISTRY 的 param_schema 或 Pydantic model 推导，返回 OpenAI function calling 格式：

```json
{
  "type": "function",
  "function": {
    "name": "query_k8s_pods",
    "description": "查询指定服务和环境的 K8s Pod 列表与状态",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {"type": "string", "description": "服务名称"},
        "env": {"type": "string", "description": "环境"},
        "limit": {"type": "integer", "default": 50}
      },
      "required": ["service", "env"]
    }
  }
}
```

### conclusion 字段格式约束

| 前缀 | 含义 | aggregate 处理 |
|------|------|---------------|
| `正常:` | 该领域无异常 | 正常纳入 |
| `异常:` | 该领域有异常 | 用于矛盾检测 |
| `部分:` | Agent 产出不完整 | 降权 ×0.5 |
| `失败:` | Agent 完全失败 | 不计入评分 |

### correlation_hints confidence 来源

| source | confidence 封顶 | aggregate 行为 |
|--------|-----------------|---------------|
| "llm" | 0.6（代码层强制封顶） | ≥0.6 → concrete hint；0.3-0.6 → speculative 辅助；<0.3 → 丢弃 |
| "rule" | 无封顶（规则直接设定） | 如 Deployment 规则 hint=0.6 → concrete |

## 安全

### tool_names 白名单校验（Agent 初始化时）

1. 禁止 `FORBIDDEN_TOOLS = {"execute_action"}` 出现在任何 Agent 的 tool_names 中。
2. category 前缀强制匹配（如 K8s Agent 只能 `query_k8s_*`）。
3. 工具注册检查（`gateway.describe_capability`），未注册仅 warning 不阻断。

校验失败的 Agent → `enabled=False`。planner 仍为其生成 AgentTask，但 fanout 跳过 runner
并注入 `LLM_FAILED` 空壳 `SpecialistAnalysis(confidence=0.0, partial=True)`。

### 其他安全措施

- 共享 ToolGateway 审计一致性。
- SpecialistAnalysis.confidence（LLM 自评）代码层封顶 0.9。
- time_budget_ms 严格优先于 max_tool_rounds。
- `return_exceptions=True` 确保单工具失败不中断整轮。
- Agent 实例状态在 `run()` 入口重置，防多次调用间泄漏。
- Feature flag 双路径，不回退到半切换状态。

### 运行时二次校验

除 Agent 初始化时的白名单校验外，`SpecialistAgent._execute_tool()` 中增加运行时 guard：
- LLM 可能幻觉出不在 `tool_names` 白名单中的工具名
- 调 gateway 前检查 `tool_name in self.config.tool_names`
- 不在白名单 → 注入 error message 到 ReAct messages → 继续下一轮，不调 gateway

## 可观测性

### tracing 设计

不改动 `tracing.py` 和 `gateway.py`，使用现有 `AgentTracer` API。

**Span 层级结构（以 fanout 节点为根）**：

```
fanout 节点 span (parent)
├── specialist.k8s_specialist      ← tracer.start_span("specialist.k8s_specialist")
│   ├── react.round.0               ← set_step_context(round_span)
│   │   ├── tool.query_k8s_pods          ← gateway 自动继承 parent
│   │   └── tool.query_k8s_events
│   ├── react.round.1
│   │   └── tool.query_k8s_deployment_status
│   └── agent.final_analysis         ← add_event: degradation=L0, conf=0.85, truncated=false
├── specialist.db_specialist
│   ├── react.round.0
│   │   ├── tool.query_db_processlist
│   │   └── tool.query_db_slow_queries
│   └── agent.final_analysis
├── specialist.log_specialist
├── specialist.metrics_specialist
└── specialist.deployment_specialist
```

**机制**：
- 每轮 ReAct 开始时 `tracer.set_step_context(round_span_id)` → gateway 的 `call_tool()` 自动将工具 span 挂到当前轮次下（通过 `tracer.get_active_span_id()`）
- 分析产出时 `tracer.add_event()` 记录：degradation level、confidence、truncated、partial
- 总计约 15–25 个 span（5 Agent × 平均 3–5 个 span），与现有 trace 粒度一致

**调试定位**：通过 `/runs/{run_id}/trace` 可查看每个 Agent 的每轮 LLM 调用和工具调用详情。

## 性能预算

| 指标 | 值 | 说明 |
|------|-----|------|
| 单 Agent timeout | 30s | `AgentTask.timeout_ms=30000` |
| fanout 节点总上限 | 60s | `asyncio.wait_for(gather(...), timeout=60)`，5 Agent 并行 × 2 倍安全系数 |
| LLM 调用单次上限 | 15s | `asyncio.wait_for(llm, timeout=min(remaining_ms/1000, 15.0))` |
| 工具调用单次上限 | 30s | 与 `ToolMetadata.timeout_ms` 取 min(metadata, remaining_budget/tool_count) |
| fanout 超时行为 | 返回已完成 Agent 结果 + 未完成的注入 TIMEOUT 空壳 | `asyncio.wait(..., timeout=60)` 收集部分结果 |
| confidence 封顶 | LLM 自评 ≤ 0.6 | LLM 自评准确率约 60-70%，封顶 0.6 预留跨 Agent 加权空间。规则 hint 不受此限

## 测试策略

### 单元测试（mock LLM）

| 测试对象 | 覆盖 |
|---------|------|
| `SpecialistAgent._produce_final_analysis` | 正常 JSON → COMPLETED；非法 JSON → PARTIAL；超时 → PARTIAL |
| `SpecialistAgent._build_degraded_analysis` | 各 Agent 规则提取函数：给定 raw data → 正确 AnomalySignal 列表 |
| `SpecialistAgent.run` ReAct 循环 | 轮次 0 无 tool_calls；2 轮 + 最终分析；3 轮耗尽 truncated |
| `SpecialistAgent` 工具失败注入 | gateway.call_tool 抛异常 → 注入错误信息 |
| `SpecialistAgent` LLM 幻觉工具名守卫 | LLM 返回不在白名单的 tool_name → 注入 error message，不调 gateway |
| `_build_correlation_graph` | 3 concrete hints → 正确邻接表 |
| `_infer_causual_chains` | K8s→DB graph + anomalies → 正确因果链 |
| `_detect_cross_agent_contradictions` | K8s "异常:" + Metrics "正常:" → 矛盾条目（直接用 agent_category 分类） |
| `planner_node` v1 | incident_type → 5 个 AgentTask + 双写旧 plan |
| `planner_node` 三级 fallback | agent_tasks 为空 → plan 转 AgentTask；plan 也为空 → 5 个默认 AgentTask |
| `evidence_fanout_node_v2` | 3 个 AgentTask → 并行 SpecialistAgent → 3 个 SpecialistAnalysis |
| `evidence_fanout_node_v2` agent_id 不存在 | 跳过 runner，注入 LLM_FAILED 空壳 |
| `load_agent_configs` 文件缺失 | YAML 不存在 → 所有 Agent disabled → fallback 原路径 |
| `load_agent_configs` 单 Agent 解析错 | 该 Agent disabled，其余正常 |
| `checkpoint resume` dict 兼容 | 完整 run 后 resume → specialist_analyses 元素为 dict 仍可正常工作 |

### 集成测试（mock adapter）

| 场景 | 预期 |
|------|------|
| Happy path | 5 Agent 全部 COMPLETED，aggregate 高质量评分 |
| Partial degradation | 2 Agent LLM 超时 + 3 正常 → aggregate 降权不崩溃 |
| All LLM failed | 所有 Agent → 规则兜底 → aggregate 低质量但完整 |
| Contradiction detection | 构造 K8s "异常:" + Metrics "正常:" → contradictions 非空 |
| No evidence | 所有工具空返回 → LLM_FAILED → quality_score ≈ 0 |
| Checkpoint round-trip | 完整 run 后 resume → specialist_analyses 正确反序列化 |
| Feature flag off 回归 | `AGENT_FEATURE_SPECIALIST_POOL=false` 时所有现有集成测试通过 |

### 覆盖率目标

- Agent 函数：≥ 90%（不含胶水代码）
- aggregator 纯函数：100%
- 7 种 run_status 每种 ≥ 1 个测试用例

## 验收场景

### 场景 1：5 Agent 全量并行分析

- `AGENT_FEATURE_SPECIALIST_POOL=true`。
- 5 个 Agent 同时启动 ReAct。
- 全部产出 COMPLETED，conclusion 含 "正常:" 或 "异常:"。
- aggregate 正确构建关联图，检测矛盾（如有），产出 quality_score ≥ 0.5。
- specialist_analyses 和 evidence_items 双写成功。
- diagnose 和 rca 无需改动即可运行。

### 场景 2：部分 Agent 降级

- Metrics Agent LLM 超时 → run_status=PARTIAL, confidence=0.25。
- 其余 4 个 Agent 正常 → COMPLETED。
- aggregate weight 公式正确降权（partial confidence×0.5）。
- evidence_summary 标注 "[降级] metrics"。
- 整体流程不崩溃。

### 场景 3：LLM 完全不可用

- 所有 LLM 调用失败。
- 5 个 Agent 各自走规则兜底 → PARTIAL（有 raw data）/ LLM_FAILED（无 raw data）。
- aggregate 产出低 confidence 但结构完整的分析。
- quality_score ≈ 0，但 state 字段完整性不缺失。

### 场景 4：Feature flag 回退

- `AGENT_FEATURE_SPECIALIST_POOL=false`。
- evidence_fanout 原 `_collect_one` 逻辑生效。
- evidence_aggregate 原逻辑生效。
- 所有现有集成测试通过，无回归。

### 场景 5：Agent 配置安全校验

- K8s Agent tool_names 误配 `execute_action` → 初始化校验失败 → enabled=False。
- fanout 跳过该 Agent，注入 LLM_FAILED 空壳。
- aggregate 标记缺失 category "k8s"。
- 不执行任何危险工具。

## 实施 Slice

| Slice | 内容 | 估时 | 依赖 |
|-------|------|------|------|
| S1 | 模型 + State + Config：planning.py 新增模型、state.py 新增字段、config.py 新增 flag、agent_configs.yaml 新建 | 0.5d | — |
| S2 | SpecialistAgent 核心：ReAct 循环 + 降级路径 + 规则兜底 + gateway.get_tool_schema() | 2d | S1 |
| S3 | Fanout 集成：重写 evidence_fanout_node（feature flag 双路径）+ evidence_items 双写 + task_to_legacy | 1.5d | S2 |
| S4 | Aggregate v2：aggregator.py 纯函数 + 重写 evidence_aggregate_node | 1d | S1 |
| S5 | Planner 更新：产出 AgentTask + 双写旧 plan + _category_applies() | 0.5d | S1 |
| S6 | 测试 + 集成：8 类单元测试 + 6 类集成测试 + feature flag 回退验证 | 1.5d | S3,S4,S5 |

**总计**：约 5–7 人天。

## Open Questions

1. ~~**`AGENT_FEATURE_SPECIALIST_POOL` 字段不存在**（P0）~~ → **已闭环**：在 `Settings` 中新增 `agent_feature_specialist_pool: bool = False`，.env 对应 `AGENT_FEATURE_SPECIALIST_POOL=true`。见 `config.py` 改动。
2. ~~**`_anomaly_to_category()` 的 SIGNAL_CATEGORY_MAP 未完整定义**（P0）~~ → **已闭环**：删除 `SIGNAL_CATEGORY_MAP` 和 `_anomaly_to_category()`。矛盾检测直接使用 `SpecialistAnalysis.agent_category`，无需额外映射表。
3. ~~**`gateway.get_tool_schema()` 与 `describe_capability()` 职责重叠**~~（P1）→ **已闭环**：`get_tool_schema()` 是新增方法，从 `TOOL_REGISTRY` 的 `parameters_schema` 提取 OpenAI function calling 格式。`describe_capability()` 返回可用性布尔值，职责不同，不合并。
4. ~~**Pydantic vs dict 二义性防护不统一**（P1）~~ → **已闭环**：在 `evidence_fanout_node_v2` 和 `evidence_aggregate_node_v2` 入口统一做防御转换（`isinstance(obj, dict)` 检查），不引入 `parse_obj_as` 依赖。
5. ~~**specialist_analyses 与 evidence_items 双写非原子**（P2）~~ → **已闭环**：采用 Agent 级原子写入 + 失败回滚 + 降级空壳。见「Fanout 原子写入」章节。
6. **`DEGRADED` 枚举不可达**（P3）：保留供未来扩展，代码注释说明。
7. **拼写 `causual` → `causal`**（P3）：实现时统一修正为 `causal`。
8. **builder.py 无需改动**：节点函数签名不变，TypedDict total=False 自动兼容新字段。实现时验证即可。

## 实施边界

本轮目标是在不改动 StateGraph 拓扑的前提下，让 evidence fan-out 具备 Agent 级别的分析推理能力。
后续方案二（Supervisor）和方案三（Dynamic Orchestrator）依赖本轮产出的 `SpecialistAnalysis` 数据结构和
`AgentTask` / `SpecialistAgent` 抽象，但它们的调度逻辑和路由改动不在此轮范围。
