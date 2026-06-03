# OpsPilot 深度架构解析 — 14 节点细节设计

**文档定位**: 面向技术面试和代码审计，逐节点讲解设计决策、实现细节、常见问题  
**生成时间**: 2026-06-03  
**关键读者**: 后端工程师、系统架构师、AI/Agent 方向候选人

---

## 一、StateGraph 拓扑总览与状态转移

### 1.1 节点拓扑（有向无环图 DAG）

```
                  ┌─────────────┐
                  │  dispatcher │
                  └──────┬──────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      (新run)        (恢复)          (恢复)
          ▼              ▼              ▼
      ┌────────┐  ┌──────────┐  ┌────────────┐
      │ intake │  │executor  │  │risk_gate   │
      └───┬────┘  └────┬─────┘  └─────┬──────┘
          │            │              │
          ▼            ▼              ▼
      ┌────────┐  ┌──────────────┐   rca (终点)
      │ triage │  │verify_outcome│
      └───┬────┘  └──────────────┘
          │
          ▼
    ┌──────────────┐
    │retrieve_     │
    │memory        │
    └───┬──────────┘
        │
        ▼
    ┌───────────┐
    │  planner  │
    └─────┬─────┘
          │
          ▼
    ┌──────────────┐
    │evidence_     │ ◄──┐ (循环: NEED_MORE_EVIDENCE)
    │fanout        │    │
    └─────┬────────┘    │
          │             │
          ▼             │
    ┌──────────────┐    │
    │evidence_     │────┤ (冲突/多领域不足)
    │aggregate     │    │
    └─────┬────────┘    │
          │             │
          ▼             │
    ┌──────────────┐    │
    │  diagnose    │    │
    └─────┬────────┘    │
          │             │
          ▼             │
    ┌──────────────┐    │
    │  critic      ├────┴─ (4路路由)
    └─────┬────────┘
          │
    ┌─────┼─────┬────────────┐
    ▼     ▼     ▼            ▼
  PASS REPLAN  NEED_  NEEDS_
    │     │    MORE   HUMAN
    │     └──→planner │
    │             │   └──→ rca
    ▼             ▼
remediation  planner(循环)
    │
    ▼
┌─────────────┐
│ risk_gate   │ (3路路由)
└──┬──┬────┬──┘
   │  │    │
   ▼  ▼    ▼
  LOW NEEDS BLOCKED
  ONLY APPROVAL
   │    │     │
   ▼    ▼     ▼
executor  approval_  rca
   │      interrupt
   └─────→ executor(循环)
   │
   ▼
verify_outcome (3路路由)
   │
   ├─→ SUCCESS    → rca
   ├─→ RETRYABLE  → executor (retry, max 2)
   └─→ FATAL      → rca
```

### 1.2 故障模式: 14 节点的容错设计

| 节点 | 失败表现 | 容错策略 |
|------|---------|---------|
| intake | ticket 字段缺失 | Pydantic 校验阻塞，返回 400 |
| triage | LLM 不可用 | 默认分为 unknown/P2 |
| retrieve_memory | RAG 检索失败 | 无历史，继续正常流程 |
| planner | 无该 incident_type 的映射 | 空 task list，直接进 evidence_aggregate |
| evidence_fanout | 所有工具失败 | evidence_items 为空，quality_score=0 |
| evidence_aggregate | 计算异常 | 捕获异常，使用默认评分 |
| diagnose | LLM JSON 解析失败 | fallback 空候选 + 置信度=0 |
| critic | 无法决策 | 默认 PASS（倾向于继续） |
| remediation | LLM 生成失败 | fallback 空方案，后续 risk_gate 阻塞 |
| risk_gate | 无法评估风险 | 默认 NEEDS_APPROVAL（保守） |
| approval_interrupt | 人工超时未响应 | 定时提醒或自动转人工审核 |
| executor | 执行失败 | 可重试 max 2 次 |
| verify_outcome | 验证失败 | 触发重试或直接宣布失败 |
| rca | RCA 生成失败 | 最小化 RCA 模板，至少保留基本信息 |

---

## 二、核心节点的实现细节

### 2.1 Evidence Fanout 并行模式

```python
# 关键代码
async def evidence_fanout_node(state: IncidentAgentState):
    tasks = state["plan"]["tasks"]
    
    # 方案一（未来）：Specialist Agent 池
    # 当前（v0）：纯工具调用
    
    async def _collect_one(task):
        req = ToolRequest(
            tool_name=task["tool"],
            params={
                "service": state["ticket"]["service"],
                "env": state["ticket"]["env"],
            },
            run_id=state["run_id"]
        )
        try:
            result = await asyncio.wait_for(
                gateway.call_tool(req),
                timeout=30.0  # 单工具 30s 超时
            )
            return EvidenceItem(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                tool_name=task["tool"],
                category=task["category"],
                raw_payload=result.result,
                confidence=0.8 if result.success else 0.0,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Tool {task['tool']} timeout")
            return EvidenceItem(
                tool_name=task["tool"],
                confidence=0.0,
                raw_payload={"error": "timeout"},
            )
        except Exception as e:
            logger.error(f"Tool {task['tool']} failed: {e}")
            return None
    
    # 关键：return_exceptions=True 保证单工具失败不中断
    results = await asyncio.gather(
        *[_collect_one(t) for t in tasks],
        return_exceptions=True
    )
    
    # 过滤失败的结果
    state["evidence_items"].extend(
        [r for r in results if r is not None and not isinstance(r, Exception)]
    )
    
    return state
```

**性能分析**:
- 10 个工具，单工具 2s → 串行 20s，并行 2s（10 倍加速）
- 3 个工具超时，其他 7 个仍可完成（容错）

---

### 2.2 Critic 的 4 路路由逻辑

```python
def _route_after_critic(state: IncidentAgentState) -> str:
    """
    四路决策树：
    1. 证据不足 → 再调一轮工具
    2. 诊断矛盾 → 重新规划
    3. 诊断不确定 → 跳过自动修复
    4. 诊断高质量 → 继续修复
    """
    quality = state.get("evidence_quality_score", 0)
    contradictions = state.get("contradiction_signals", [])
    candidates = state.get("root_cause_candidates", [])
    loop_count = state.get("_loop_count", {}).get("critic", 0)
    
    # 防死循环
    if loop_count > 5:
        logger.warning("Critic loop exceeded 5 times, forcing NEEDS_HUMAN")
        return "node_rca"
    
    # 路由逻辑（优先级）
    if len(contradictions) > 2:
        logger.info("High contradiction detected, replan")
        state["_loop_count"]["critic"] = loop_count + 1
        return "node_planner"
    
    if quality < 0.5:
        logger.info(f"Low evidence quality {quality:.2f}, need more evidence")
        state["_loop_count"]["critic"] = loop_count + 1
        return "node_evidence_fanout"
    
    if not candidates or candidates[0].get("confidence", 0) < 0.3:
        logger.info("Low diagnosis confidence, needs human")
        return "node_rca"
    
    logger.info("Quality check passed, proceed to remediation")
    return "node_remediation"
```

**设计思想**:
- 优先解决"矛盾"（可能规划错误）
- 其次补充"证据"（可能信息不足）
- 最后考虑"人工"（诊断不确定）

---

### 2.3 Checkpoint 恢复机制

```python
# builder.py 中的分发器
def _route_dispatcher(state: IncidentAgentState) -> str:
    """
    入口分发器，决定从哪个节点开始执行
    """
    _resume_from_node = state.get("_resume_from_node")
    _RESUME_ALLOWED = {
        "node_intake",        # 重新开始
        "node_evidence_fanout", # 补充证据
        "node_executor",       # 执行修复
        "node_risk_gate",      # 重新评估风险
    }
    
    if _resume_from_node and _resume_from_node in _RESUME_ALLOWED:
        logger.info(f"Resuming from {_resume_from_node}")
        return _resume_from_node
    else:
        return "node_intake"  # 默认从头开始

# 恢复流程
graph.add_node("dispatcher", _route_dispatcher)
graph.add_edge("START", "dispatcher")
graph.add_edge("dispatcher", "node_intake")
graph.add_edge("dispatcher", "node_evidence_fanout")
graph.add_edge("dispatcher", "node_executor")
graph.add_edge("dispatcher", "node_risk_gate")
```

**使用场景**:
1. **人工审批后恢复**: approval_interrupt 设置 `_resume_from_node="node_executor"`
2. **补充证据后恢复**: critic 返回 NEED_MORE_EVIDENCE，evidence_fanout 运行后 diagnose 会用新证据
3. **修复失败重试**: verify_outcome 返回 RETRYABLE_FAILURE，直接恢复到 executor

---

## 三、State 管理最佳实践

### 3.1 为什么用 TypedDict 而不是 Pydantic Model？

```python
# ❌ 问题：Pydantic Model 序列化开销大
class IncidentAgentStateModel(BaseModel):
    run_id: str
    ticket: IncidentTicket
    triage: TriageResult
    # ... 30+ 字段
    
    class Config:
        arbitrary_types_allowed = True

# 序列化：约 200ms（对于大 state）
json_str = state_model.model_dump_json()  # 包括递归序列化所有嵌套对象
state_model = IncidentAgentStateModel.parse_raw(json_str)  # 再反序列化

# ✅ 方案：TypedDict（纯类型提示，无序列化开销）
class IncidentAgentState(TypedDict, total=False):
    run_id: str
    ticket: dict  # 存储为原始 dict，不必序列化
    triage: dict
    # ...

# checkpoint 时
json_str = json.dumps(state)  # 原生 dict 序列化，只需 ~20ms
state = json.loads(json_str)
```

**权衡**:
- **TypedDict**: 序列化快，但无字段验证（需要手动 validate）
- **Pydantic**: 验证完整，但序列化慢

**当前项目选择**: **TypedDict** 用于 state，Pydantic 仅用于模型对象

---

### 3.2 State 字段写入约定

```python
# 节点函数的标准模板
async def my_node(state: IncidentAgentState) -> IncidentAgentState:
    # 1. 读取输入（只读）
    ticket = state["ticket"]  # 来自 intake_node 的标准化结果
    
    # 2. 处理逻辑
    result = await some_computation(ticket)
    
    # 3. 写入输出（新字段或追加）
    state["my_field"] = result  # 新字段
    state["evidence_items"].append(...)  # 追加而非覆盖
    
    # 4. 更新状态
    state["status"] = RunStatus.XXX
    
    # 5. 可选：埋点
    GraphRunner._emit_event("node_completed", {"node_name": "my_node"})
    
    return state
```

**约定**:
- 不要覆盖已有的复合字段（如 evidence_items），而是追加
- 始终更新 status 字段
- 新字段命名用蛇形 (snake_case)

---

## 四、可观测性与调试

### 4.1 Tracing 埋点完整链路

```
graph.run() [span: duration 120s]
├─ node_intake [span: duration 100ms]
│  └─ validate IncidentTicket [event]
├─ node_triage [span: duration 1500ms]
│  ├─ llm.complete [span: duration 1400ms]
│  │  ├─ prompt_tokens: 150
│  │  ├─ completion_tokens: 50
│  │  └─ model: "deepseek-chat"
│  └─ parse_response [event]
├─ node_evidence_fanout [span: duration 10000ms]
│  ├─ tool.call [span: duration 2000ms]
│  │  ├─ tool_name: "query_metrics"
│  │  ├─ params: {...}
│  │  └─ status: "success"
│  ├─ tool.call [span: duration 1500ms]
│  │  ├─ tool_name: "query_k8s_pods"
│  │  └─ status: "success"
│  └─ gather_results [event]
└─ ... (其他节点)
```

**实现方式** (`tracing.py`):
```python
class LocalTracer:
    def __init__(self):
        self.spans: Dict[str, Span] = {}
        self.events: List[Event] = []
    
    @contextmanager
    def trace_span(self, name: str, attributes: dict = None):
        span = Span(
            span_id=uuid4().hex[:8],
            name=name,
            start_time=time.time(),
            attributes=attributes or {}
        )
        self.spans[span.span_id] = span
        try:
            yield span
        finally:
            span.end_time = time.time()
            span.duration_ms = (span.end_time - span.start_time) * 1000
    
    def log_event(self, event_name: str, data: dict = None):
        self.events.append(Event(
            name=event_name,
            timestamp=time.time(),
            data=data or {}
        ))

# 在节点中使用
async def evidence_fanout_node(state):
    tracer = state["_tracer"]
    with tracer.trace_span("evidence_fanout", {"tool_count": len(state["plan"]["tasks"])}):
        # 并行调用工具
        for task in state["plan"]["tasks"]:
            with tracer.trace_span(f"tool.{task['tool']}", {"params": task.get("params")}):
                result = await gateway.call_tool(...)
    return state
```

---

### 4.2 调试技巧

```bash
# 1. 打印完整 state
python -c "
import json
from backend.app.services.graph_runner import GraphRunner
runner = GraphRunner()
state = runner.load_checkpoint('run_12345')
print(json.dumps(state, indent=2, default=str))
"

# 2. 查看某个字段的演变
python -c "
import json
from backend.app.repositories import run_repo
events = run_repo.get_events('run_12345')
for event in events:
    if 'evidence_items' in event.get('data', {}):
        print(f\"{event['timestamp']}: {len(event['data']['evidence_items'])} items\")
"

# 3. 跟踪特定工具调用
python -c "
from backend.app.repositories import event_repo
tool_calls = event_repo.search_events(
    run_id='run_12345',
    event_type='tool_called',
    filters={'tool_name': 'query_metrics'}
)
for call in tool_calls:
    print(f\"Call: {call['tool_name']}, Result: {call['status']}\")
"

# 4. 重放流程（用 fixture 替换真实工具）
python backend/app/tests/test_replay.py --run-id run_12345 --mode mock
```

---

## 五、性能对标

### 5.1 各节点的典型耗时

| 节点 | 典型耗时 | 瓶颈 | 优化空间 |
|------|---------|------|---------|
| intake | 10ms | Pydantic 校验 | 无（可忽略） |
| triage | 1500ms | LLM 调用 | 缓存同类故障的分类 |
| retrieve_memory | 800ms | RAG 向量搜索 | Rerank 可选关闭 |
| planner | 5ms | 规则映射 | 无（可忽略） |
| evidence_fanout | 15000ms | 并行工具调用 | 减少工具数量 / 增加 timeout |
| evidence_aggregate | 50ms | 质量计算 | 无（很快） |
| diagnose | 2500ms | LLM 多轮调用 | 减少 context 长度 |
| critic | 10ms | 路由决策 | 无（很快） |
| remediation | 2000ms | LLM 生成方案 | 缓存模板 |
| risk_gate | 5ms | 规则评估 | 无（很快） |
| executor | 300ms | 执行命令 | 并行执行步骤 |
| verify_outcome | 5000ms | 验证工具调用 | 并行验证多个指标 |
| rca | 200ms | 报告生成 | 无（很快） |

**总计**: Happy path 约 30s（单工具调用为主）

### 5.2 如何在实际场景中优化到 < 20s

```python
# 1. Triage 缓存（对同服务同故障类型）
@cache(ttl=3600)
def triage_incident(title: str, description: str) -> TriageResult:
    # LLM 分类
    pass

# 2. Evidence 并行化（已实现）
results = await asyncio.gather(
    *[gateway.call_tool(t) for t in tasks],
    return_exceptions=True
)

# 3. Diagnose 上下文精简
# 不是拼接所有 evidence，而是精选关键 evidence
key_evidence = _select_top_k_evidence(
    state["evidence_items"],
    k=5,  # 只传 top 5，减少 token
    method="relevance_score"
)

# 4. Verify 并行（改 verify_outcome_node）
verification_results = await asyncio.gather(
    *[verify_single_item(item) for item in verification_items],
    return_exceptions=True
)
```

**预期结果**:
- Triage 缓存命中: -1500ms
- Evidence 并行: 已是 15s
- Diagnose 精简: -800ms（减少 token，LLM 更快）
- Verify 并行: -3000ms
- **总计**: 30s → 15-18s（50% 加速）

---

## 六、已知限制与改进计划

### 限制 1: 工具调用不支持依赖链

**当前**: K8s 查询和 DB 查询独立并行

**问题**: 若 K8s 查询发现 Pod IP，无法自动用该 IP 去查询 DB 连接状态

**解决方案**: Phase 9 引入 Specialist Agent + ReAct，支持多轮反复

---

### 限制 2: Diagnose 单轮推理

**当前**: 一次 LLM 调用生成 3 个候选

**问题**: LLM 无法自主补充证据，只能被动接收

**解决方案**: Phase 2 引入 Diagnosis Agent Debate，3 个 Agent 独立诊断后交叉质疑

---

### 限制 3: 循环没有上界保证

**当前**: critic 支持 NEED_MORE_EVIDENCE → evidence_fanout，可能死循环

**防护**: loop_count < 5，超过后强制 NEEDS_HUMAN

**改进**: Phase 8 引入动态"充分性评估"，自动判断证据何时足够

---

## 七、下一步深度阅读

- `03-interview-qa.md` — 6 道高频技术问题与标准答案
- `04-code-walkthrough.md` — 关键代码行详解（100+ 行精选）
- 源代码 `backend/app/graph/nodes/__init__.py` — 1200 行完整实现
- PR 评审对比 `backend/app/graph/builder.py` — LangGraph StateGraph 构建
