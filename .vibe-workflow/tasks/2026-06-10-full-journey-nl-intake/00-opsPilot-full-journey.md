# OpsPilot 全旅程 + 自然语言输入节点设计

> 2026-06-10 | 根目录落库

---

## 一、当前状态（as-is）

### API 入口（3 种模式，均在 Graph 外处理）

```
  ┌─ [ticket 结构体] ──┐
  ├─ [ticket_id 拉取] ──┤── IntakeService ──→ IncidentTicket ──→ Graph
  └─ [alert_event 告警]─┘         ↑
                          (不在 graph 内)
```

API 定义：`backend/app/api/incidents.py:56-61`

```python
class IncidentRunCreate(BaseModel):
    ticket: Optional[IncidentTicketCreate] = None
    ticket_id: Optional[str] = None
    alert_event: Optional[AlertEventCreate] = None
```

IntakeService：`backend/app/services/intake.py`

| 方法 | 功能 |
|------|------|
| `from_ticket_payload()` | 结构化工单直接映射（+ 归一化） |
| `from_ticket_id()` | 通过工具适配器查询外部系统拉取工单 |
| `from_alert_event()` | 告警事件模板化转工单 |

### Graph 内 14 个节点

```
intake → triage → retrieve_memory → planner → evidence_fanout
  → evidence_aggregate → diagnose → critic
      ├─ PASS → remediation → risk_gate
      │           ├─ LOW_ONLY → executor → verify
      │           ├─ NEEDS_APPROVAL → approval_interrupt → [人工] → executor → verify
      │           └─ BLOCKED → rca → END
      ├─ NEED_MORE_EVIDENCE → evidence_fanout (loop)
      ├─ REPLAN / CONTRADICTION → planner (loop)
      └─ NEEDS_HUMAN → rca → END
```

| 节点 | 位置 | 职责 |
|------|------|------|
| `intake_node` | `nodes/__init__.py:49` | 归一化 env/service/time_range，初始化空列表 |
| `triage_node` | `nodes/__init__.py:191` | 3 级分流：规则 → LLM → 兜底 |
| `retrieve_memory_node` | `nodes/retrieve_memory.py:45` | RAG 检索 runbook/RCA/服务文档 |
| `planner_node` | `nodes/__init__.py:227` | 按 incident_type 编排取证计划（5 专科） |
| `evidence_fanout_node` | `nodes/__init__.py` | 并行调用 5 专科工具 |
| `evidence_aggregate_node` | `nodes/aggregator.py` | 质量打分 + 跨层矛盾检测 |
| `diagnose_node` | `nodes/__init__.py` | LLM 根因分析 → 候选排序 |
| `critic_node` | `nodes/__init__.py:1074` | 4 路裁决 + loop guard |
| `remediation_node` | `nodes/__init__.py:1136` | 生成修复方案 |
| `risk_gate_node` | `nodes/__init__.py:1208` | 风险评估 + 能力预检 |
| `approval_interrupt_node` | `nodes/__init__.py:1321` | 人工审批中断点 |
| `executor_node` | `nodes/__init__.py:1477` | 幂等执行修复动作 |
| `verify_outcome_node` | `nodes/__init__.py:1596` | 验证修复效果（3 检查） |
| `rca_node` | `nodes/__init__.py:1772` | 生成 RCA 报告 + OSS 归档 |

---

## 二、目标状态（to-be）

### 新增 `nl_intake_node` 节点

放在 `intake_node` 之前，把自然语言解析也纳入 Graph：

```
nl_intake → intake → triage → ... → critic → ... → rca → END
```

#### 节点设计

```python
def nl_intake_node(state: IncidentAgentState) -> IncidentAgentState:
    """LLM-based natural language intake: parse user raw text into IncidentTicket."""
    user_input = state.get("user_input")
    if not user_input:
        raise ValueError("user_input is required")

    llm_prompt = f"""Parse the following SRE incident description into a structured ticket.
Extract: ticket_id (generate if missing), title, description, service, env, severity (P1-P4), time_range.

User input: {user_input}

Respond in JSON format with keys: title, description, service, env, severity, time_range (optional)."""

    llm_response = llm_client.complete_sync(llm_prompt, ...)
    parsed = json.loads(llm_response)
    ticket = IncidentTicket(
        ticket_id=f"nl-{uuid.uuid4().hex[:8]}",
        title=parsed["title"],
        description=parsed["description"],
        service=parsed["service"],
        env=parsed["env"],
        severity=parsed["severity"],
        time_range=parsed.get("time_range"),
        source="natural_language",
    )

    state["ticket"] = ticket
    state["status"] = RunStatus.NEW
    return state
```

#### API 层新增第 4 种模式

```python
class IncidentRunCreate(BaseModel):
    ticket: Optional[IncidentTicketCreate] = None
    ticket_id: Optional[str] = None
    alert_event: Optional[AlertEventCreate] = None
    user_input: Optional[str] = None  # NEW
```

路由逻辑：

```python
if data.user_input:
    initial_state = {"user_input": data.user_input, ...}
    # Graph begins at nl_intake_node → intake_node → ...
```

#### Builder 注册

```python
graph.add_node("node_nl_intake", _wrap_with_events("node_nl_intake", nl_intake_node))
graph.add_edge("node_nl_intake", "node_intake")
```

新增 dispatcher 入口：

```python
_RESUME_ALLOWED_NODES = {
    "node_intake",
    "node_nl_intake",   # NEW
    "node_executor",
    "node_risk_gate",
    "node_evidence_fanout",
}
```

### 全旅程完整图

```
[用户自然语言] ──→ nl_intake_node (LLM提取)
[结构化工单] ────→                                       
[ticket_id查单] ──→ IntakeService ──→ intake_node (归一化)
[告警事件] ──────→                                       
                       ↓
                  triage_node (规则→LLM→兜底 3级)
                       ↓
                  retrieve_memory_node (RAG: runbook/RCA/服务文档)
                       ↓
                  planner_node (按 incident_type 编排取证计划)
                       ↓
                  evidence_fanout_node (并行调用5专科: K8s/DB/日志/指标/部署)
                       ↓
                  evidence_aggregate_node (质量打分 + 跨层矛盾检测)
                       ↓
                  diagnose_node (LLM 根因分析 → 候选排序)
                       ↓
                  critic_node ←── loop_count guard (max=2)
                    ├─ PASS → remediation_node
                    ├─ NEED_MORE_EVIDENCE → → evidence_fanout (loop, count+1)
                    ├─ REPLAN/CONTRADICTION → → planner (loop, count+1)
                    └─ NEEDS_HUMAN → → rca → END
                       ↓
                  remediation_node (生成修复方案)
                       ↓
                  risk_gate_node (低风险→直行/高风险→审批/阻塞→失败)
                    ├─ LOW_ONLY → executor_node
                    ├─ NEEDS_APPROVAL → approval_interrupt_node → [人工审批] → executor_node
                    └─ BLOCKED → rca → END (FAILED)
                       ↓
                  executor_node → verify_outcome_node
                    ├─ SUCCESS → rca → END (COMPLETED)
                    ├─ RETRYABLE_FAILURE → executor_node (重试, max=2)
                    └─ FATAL_FAILURE → rca → END (FAILED)
                       ↓
                  rca_node → OSS 归档 → END
```

---

## 三、critic 仲裁机制在全旅程中的定位

对应你面试文 `实战-2026-06-10-critic仲裁打分机制.md` 的映射：

| 面试文概念 | 全旅程位置 | 关键文件:行 |
|---|---|---|
| 质量打分（会计） | evidence_aggregate_node 末尾 | `aggregator.py:159` |
| 跨层差分定位（6 条规则） | evidence_aggregate_node 末尾 | `aggregator.py:138` |
| 4 路裁决（领导） | critic_node | `__init__.py:1074` |
| loop guard 保险丝 | critic_node 顶部 | `__init__.py:1086` |
| 回退深度路由 | critic_node 之后 | `builder.py:115` |
| 候选字段留口（待灌装） | diagnose_node 产出 | `__init__.py:1017-1057` |

critic **不参与** NL intake — 它只管"证据够不够下结论"，不管"用户说了什么"。

---

## 四、关键文件变更清单

| 文件 | 变更 |
|------|------|
| `backend/app/graph/nodes/__init__.py` | 新增 `nl_intake_node()` 函数 |
| `backend/app/graph/builder.py` | 注册 `node_nl_intake`，加边 `nl_intake → intake` |
| `backend/app/graph/state.py` | `IncidentAgentState` 新增 `user_input: Optional[str]` |
| `backend/app/api/incidents.py` | `IncidentRunCreate` 新增 `user_input` 字段 + 路由分支 |
| `backend/app/services/intake.py` | 可选：新增 `from_natural_language()` 方法 |
| `frontend/src/types/index.ts` | 前端类型同步 |
| `frontend/src/pages/CreateRunPage.tsx` | 新增自然语言输入 UI（文本域 + 提交按钮） |

---

## 五、验收标准

1. `POST /incidents/runs` 接受 `{"user_input": "支付服务发布后错误率升高"}` → 返回 201 + run_id
2. `nl_intake_node` 调用 LLM 成功提取 title/service/severity 等字段
3. graph 从 `nl_intake` → `intake` → 后续节点正常流转
4. LLM 解析失败时返回清晰错误（非 500）
5. 前端有自然语言输入框
6. 单元测试覆盖：LLM 解析成功/失败/部分缺失情况
