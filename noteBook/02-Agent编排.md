# 02 — Agent 编排

> LangGraph 工作流编排详解：state 设计、graph 构建、14 个节点逐个解读。

---

## 1. 什么是 LangGraph

LangGraph 是一个 Python 库，让你能**用有向图定义 Agent 的工作流**。核心概念：

| 概念 | 说明 | TS 类比 |
|------|------|---------|
| State | 贯穿整个工作流的数据对象 | Redux state / zustand store |
| Node | 图中一个节点，接收 state 返回 state | async thunk / saga |
| Edge | 普通边，A 完了必然走到 B | 顺序执行 |
| Conditional Edge | 条件边，根据 state 决定下一步 | switch / if-else 路由 |
| Graph | 由节点+边组成的有向图 | 状态机定义 |
| Checkpoint | 每次节点执行后的 state 快照 | state snapshot |

---

## 2. State 设计 (`backend/app/graph/state.py`)

### 2.1 核心状态定义

`IncidentAgentState` 是一个 Python `TypedDict(total=False)`，语义上等价于：

```typescript
// TypeScript 等价视角
interface IncidentAgentState {
  run_id: string;
  thread_id: string;
  ticket: IncidentTicket;
  triage: TriageResult;
  memory_hits: MemoryHit[];
  investigation_plan: InvestigationPlan;
  evidence_items: EvidenceItem[];
  root_cause_candidates: RootCauseCandidate[];
  remediation_plan: RemediationPlan;
  pending_approval: ApprovalRequest;
  approval_result: ApprovalResult;
  rca_report: RcaReport;
  status: RunStatus;
  step_count: number;
  loop_count: number;
  critic_decision: 'PASS' | 'NEED_MORE_EVIDENCE' | 'REPLAN' | 'CONTRADICTION';
  risk_decision: 'LOW_ONLY' | 'NEEDS_APPROVAL' | 'BLOCKED';
  verify_decision: 'SUCCESS' | 'RETRYABLE_FAILURE' | 'FATAL_FAILURE';
  action_results: Record<string, any>[];
  execution_results: Record<string, any>[];
}
```

所有字段的初始值都是 `None` / `[]`，由各个节点逐步填充。`total=False` 意味着不是所有字段都必须存在——类比 TS 的 `Partial<IncidentAgentState>`。

### 2.2 RunStatus 枚举（11 种状态）

```
NEW → TRIAGED → PLANNING → GATHERING_EVIDENCE
  → DIAGNOSING → REMEDIATING → EXECUTING
  → VERIFYING → COMPLETED / FAILED / WAITING_HUMAN
```

### 2.3 「Pydantic vs dict」 兼容性问题

这是整个项目里最常踩的坑。从 checkpoint 反序列化后，Pydantic 模型会变成普通 dict：

```python
# ❌ 错误写法（假设 ticket 一定是 Pydantic 对象）
service = ticket.service  # 如果 ticket 是 dict，报 AttributeError

# ✅ 正确写法（兼容两种形式）
service = ticket.service if hasattr(ticket, 'service') else ticket.get('service', '')
```

类比：就像 JSON.parse 之后你不知道拿到的是 class 实例还是 plain object，需要用 `?.` 或类型守卫。

---

## 3. Graph 构建 (`backend/app/graph/builder.py`)

### 3.1 完整工作流图

```
                    ┌──────────┐
                    │ dispatch │ ← 入口裁决（新运行 vs 恢复运行）
                    └────┬─────┘
                         ↓
                    ┌──────────┐
                    │  intake  │ ← 输入规范化
                    └────┬─────┘
                         ↓
                    ┌──────────┐
                    │  triage  │ ← 分诊分类
                    └────┬─────┘
                         ↓
                    ┌────────────────┐
                    │ retrieve_memory│ ← RAG + runbook 检索
                    └──────┬─────────┘
                           ↓
                    ┌──────────┐
                    │ planner  │ ← 制定排查计划
                    └────┬─────┘
                         ↓
                 ┌──────────────┐
                 │evidence_fanout│ ← 并行收集证据（asyncio.gather）
                 └──────┬───────┘
                        ↓
              ┌─────────────────┐
              │evidence_aggregate│ ← 聚合分析证据
              └──────┬──────────┘
                     ↓
              ┌──────────┐
              │diagnose  │ ← LLM 诊断根因
              └────┬─────┘
                   ↓
              ┌──────────┐
              │ critic   │ ← 自我审查
              └────┬─────┘
                   │ ← 4 路路由：PASS / NEED_MORE_EVIDENCE / REPLAN / CONTRADICTION
            ┌──────┼──────┐
            ↓      ↓      ↓
       [evidence] [planner] [PASS ↓]
            │      │              │
            └──────┴──────────────┘
                   ↓
            ┌────────────┐
            │ remediation│ ← 制定修复方案
            └─────┬──────┘
                  ↓
            ┌───────────┐
            │ risk_gate │ ← 风险评估
            └─────┬─────┘
                  │ ← 3 路路由：LOW_ONLY / NEEDS_APPROVAL / BLOCKED
          ┌───────┼───────┐
          ↓       ↓       ↓
     [executor] [approval] [rca]
          │       ↓        │
          │   [resume后]   │
          │       ↓        │
          └───────┴────────┘
                  ↓
           ┌───────────┐
           │  verify   │ ← 验证修复结果
           └─────┬─────┘
                 │ ← 3 路路由：SUCCESS / RETRYABLE_FAILURE / FATAL_FAILURE
           ┌─────┼─────┐
           ↓     ↓     ↓
        [rca] [executor] [rca]
         (重试最多2次)
```

### 3.2 路由策略

| 路由点 | 决策逻辑 | 类比 |
|--------|----------|------|
| `_route_dispatcher()` | 新运行 → intake，恢复运行 → 上次中断的节点 | Express middleware 分流 |
| `_route_after_critic()` | PASS→remediation, 缺证据→fanout, 矛盾→planner | switch-case |
| `_route_after_risk_gate()` | 低风险→executor, 需审批→approval, 封禁→rca | 权限门控 |
| `_route_after_verify()` | 全通过→rca, 部分失败重试, 严重失败→rca | retry policy |

### 3.3 循环守卫

```
MAX_STEPS = 30           # 总步数上限
MAX_EXECUTOR_RETRIES = 2 # 执行器最多重试2次
critic 循环最多 2 次     # 强制 PASS 避免无限循环
recursion_limit = 50     # LangGraph 递归硬限制
```

---

## 4. 14 个节点详解

### 4.1 `dispatcher` — 入口裁决

- 判断是**新运行**还是**恢复运行**（审批通过后继续）
- 新运行 → 路由到 `intake`
- 恢复运行 → 检查 `_resume_from_node` 字段，跳到对应节点

### 4.2 `intake` — 输入规范化

```python
# 做了什么
1. 提取 ticket 信息
2. 规范化字段（env/service/time_range）
3. 初始化 evidence_items = [], root_cause_candidates = []
4. 设置 status = NEW
```

类比：表单提交后的数据清洗，确保后续节点拿到的数据格式一致。

### 4.3 `triage` — 分诊

```python
# 三级分诊策略
1. _triage_by_rules()   # 关键词规则匹配（deployment/资源/依赖）
2. _triage_by_llm()     # LLM 增强分类（调用 LLM 返回 JSON）
3. _triage_fallback()   # 兜底：默认 service_degradation
```

输出 `TriageResult`，包含 `incident_type` 和 `suspected_services`，是整个后续流程的「方向盘」。

### 4.4 `retrieve_memory` — 记忆检索

```python
# 双源检索
1. RAG 向量检索  → RAG.retrieve(query, filters) → MemoryHit
2. Runbook 工具  → gateway.call_tool("query_runbook") → MemoryHit

# 输出
memory_hits += [...]
evidence_items += [...]  # 检索结果也作为证据
```

### 4.5 `planner` — 排查规划

根据 `triage` 的 `incident_type` 排定工具调用优先级：

| incident_type | 优先级顺序 |
|---------------|-----------|
| deployment_regression | deployments(1) > logs(2) > k8s(2-4) > metrics(3) > db(4) |
| resource_exhaustion | metrics(1) > k8s(2-4) > db(2-3) > logs(3) > deployments(4) |
| dependency_failure | logs(1) > metrics(2) > k8s(2-3) > db(2) > runbook(3) |

输出 `InvestigationPlan`，包含一组 `InvestigationTask`（每个 task 指定调哪个 tool、什么参数）。

类比：测试计划，决定先跑哪些测试用例。

### 4.6 `evidence_fanout` — 并行取证

```python
# 核心：asyncio.gather 并行执行所有 InvestigationTask
tasks = [gateway.call_tool(task.tool_name, task.params) for task in plan.tasks]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

- 成功 → 创建 `EvidenceItem` 追加到 state
- 失败 + `degrade_on_failure=True` → 记录 warning，不中断流程
- 失败 + `degrade_on_failure=False` → 记录 error，可能中断

类比：`Promise.allSettled()` — 全部执行，不管个别失败。

### 4.7 `evidence_aggregate` — 证据聚合

```python
1. 按 category 统计分布
2. 计算质量评分：coverage * 0.6 + avg_confidence * 0.4
3. 检测矛盾（如同时出现 "error" 和 "healthy"）
4. 识别缺失的证据类别
```

### 4.8 `diagnose` — LLM 诊断

```python
# 构建 evidence summary → LLM → JSON 输出
prompt = f"""根据以下证据，给出 2-3 个根因假设...
{evidence_summary}
请返回 JSON 格式: [{{"hypothesis":..., "confidence":..., "supporting_evidence":..., "contradicting_evidence":...}}]"""

response = llm_client.complete_sync(prompt)
candidates = parse_json(response)  # 解析出 RootCauseCandidate[]
```

如果 LLM 调用失败，fallback 两个预设候选：资源耗尽 + 部署引入。

### 4.9 `critic` — 自我审查

**4 路决策**：

| 决策 | 条件 |
|------|------|
| `PASS` | 证据充分、诊断置信度高、无矛盾 |
| `NEED_MORE_EVIDENCE` | 证据不足或 quality_score 低 |
| `REPLAN` | 诊断与证据有显著矛盾 |
| `CONTRADICTION` | 多个候选矛盾严重 |

**循环上限**：最多 2 次 critic 循环，超过后强制 PASS（同时降低所有候选置信度并标记需要人工介入）。

### 4.10 `remediation` — 修复方案

```python
# 逻辑
if 最高置信度候选与部署相关:
    actions = [rollback]  # HIGH 风险，需审批
else:
    actions = [restart]   # LOW 风险，无需审批
```

输出 `RemediationPlan`，包含 `actions` 列表。

### 4.11 `risk_gate` — 风险门控

**3 路决策**：

| 决策 | 条件 |
|------|------|
| `LOW_ONLY` | 所有 action 都是 LOW 风险，且非生产环境 |
| `NEEDS_APPROVAL` | 有 HIGH 风险 action，或生产环境，或 loop guard 触发 |
| `BLOCKED` | CRITICAL action + prod env + 低置信度 |

### 4.12 `approval_interrupt` — 审批中断

```python
1. 创建 ApprovalRequest
2. 写入 incident_approvals 表
3. 设置 status = WAITING_HUMAN
4. 图在此中断 ← LangGraph interrupt()
```

外部通过 `POST /approvals/:id/decision` 恢复执行，`_resume_from_node = "executor"`。

### 4.13 `executor` — 执行器

```python
# 调用 ControlledExecutor
from app.services.executor import ControlledExecutor

executor = ControlledExecutor(session)
results = executor.execute_plan(actions)
```

**ControlledExecutor 特性**：
- **幂等执行**：基于 `idempotency_key` 避免重复执行
- **前置条件检查**：执行前验证环境/服务状态
- **审计记录**：每次执行写入 `incident_actions` 表

### 4.14 `verify` — 结果验证

```python
# 三项验证检查
1. query_k8s_deployment_status  → deployment 是否 healthy
2. query_lb_health_status       → LB 后端是否健康
3. query_lb_traffic_metrics     → error_rate < 0.05

# 决策
全部通过 → SUCCESS
部分通过 → RETRYABLE_FAILURE（重试最多 2 次）
大部分失败 → FATAL_FAILURE
```

### 4.15 `rca` — 根因分析报告

```python
1. 收集所有上下文（candidates + remediation + execution + verification）
2. LLM 生成 JSON 格式 RCA 报告
3. 构建 Markdown 报告
4. 归档到 OSS（调用 write_rca_to_oss + write_evidence_to_oss）
5. 设置 status = COMPLETED
```

---

## 5. 序列化机制 (`backend/app/graph/serde.py`)

Graph 执行过程中需要将 state 存到 checkpoint。序列化规则：

```python
# 序列化
Pydantic 模型 → .model_dump(mode="json")
Enum          → .value
datetime      → .isoformat()

# 反序列化（根据字段名映射）
"ticket"              → IncidentTicket(**data)
"evidence_items"      → [EvidenceItem(**item) for item in data]
"root_cause_candidates" → [RootCauseCandidate(**c) for c in data]
# ...
```

类比：`JSON.stringify` / `JSON.parse` + reviver 函数。

---

## 6. GraphRunner 执行引擎 (`backend/app/services/graph_runner.py`)

```python
class GraphRunner:
    async def run(self, initial_state):
        # 核心调用：异步流式执行
        async for event in self.graph.astream(initial_state):
            node_name = event["node"]
            new_state = event["state"]

            # 每个节点完成后：
            self._sync_run_progress(new_state)     # → DB UPDATE
            self._save_checkpoint(new_state)        # → DB INSERT
            self._persist_evidence(new_state)       # → DB INSERT（去重）
            self._persist_rca(new_state)            # → DB UPSERT
```

**去重机制**：`_persisted_evidence_ids` 是一个 set，记录已写入的 evidence_id，同一 run 内不重复写入。

---

## 7. 事件系统

每个节点执行前后会发射事件：

```python
# 节点包装器
def _wrap_with_events(node_fn):
    async def wrapper(state):
        emit_event(NODE_STARTED, node_name=node_fn.__name__)
        try:
            result = await node_fn(state)
            return result
        except Exception as e:
            emit_event(NODE_FAILED, error=str(e))
            raise
```

前端通过 SSE 接收这些事件，实时展示节点流转。

---

## 小结

理解 Agent 编排的三个核心问题：

1. **数据在哪** → `IncidentAgentState`，一个大的 typed dict，在 14 个节点之间流转
2. **怎么流转** → LangGraph 编译的 DAG，用条件边控制分支和循环
3. **怎么持久化** → 每个节点执行后，GraphRunner 自动写 DB + 保存 checkpoint

下一篇：[03 — RAG 架构](./03-RAG架构.md)
