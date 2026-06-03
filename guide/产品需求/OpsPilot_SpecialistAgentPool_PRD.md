# OpsPilot 方案一：Specialist Agent 池 — 独立需求文档

版本: v1.0（从 `OpsPilot_多Agent协同演进_PRD.md` 方案一章节提取）  
定位: 将证据采集 Fan-out 升级为由 5 个独立 Specialist Agent 组成的分析池  
关联文档: `OpsPilot_多Agent协同演进_PRD.md`（完整三方案）、`ACTION_PLAN.md`（进度跟踪）  
状态: 详细设计完成，待评审后进入开发

---

## 1. 背景与动机

### 1.1 现状

OpsPilot 当前为单 Agent + Pipeline 架构。evidence_fanout_node 使用 `asyncio.gather` 并行调用工具，每个 `_collect_one()` 是一次纯数据拉取（调 ToolGateway → 返回 ToolResult → classify_result → EvidenceItem），返回的 raw data 交由 evidence_aggregate_node 做简单规则评分。

### 1.2 痛点

| 痛点 | 表现 | 根因 |
|------|------|------|
| 证据采集缺乏分析能力 | 工具返回的 raw payload 未经分析，aggregate 只能做规则评分 | 每个工具调用是纯数据拉取，无推理 |
| 异常信号被淹没 | 几百条 K8s events 中 1 条 CrashLoopBackOff → aggregate 无法识别 | 无结构化分析 |
| 工具调用间无关联分析 | K8s pod 重启时间与 DB 慢查询时间窗口的关系未被发现 | 各工具独立返回，无 Agent 做交叉推理 |

### 1.3 目标

不改变 StateGraph 拓扑骨架，将 evidence_fanout_node 中 `asyncio.gather(*[_collect_one(...)])` 的纯工具调用升级为每个工具类别对应一个独立 Specialist Agent（自带 ReAct 循环），Agent 对工具返回的原始数据做一级分析，产出结构化分析结论而非 raw data。

---'

## 2. 方案一：证据采集 Fan-out → Specialist Agent 池

### 2.1 改造目标

将 `evidence_fanout_node` 中 `asyncio.gather(*[_collect_one(...)])` 的纯工具调用，升级为每个工具类别对应一个 **独立 Specialist Agent**（自带 ReAct 循环），Agent 对工具返回的原始数据做一级分析，产出**结构化分析结论**而非 raw data。

### 2.2 现状分析

**当前代码路径**: `backend/app/graph/nodes/__init__.py:346-449`

```python
# 当前：纯工具调用，无推理
async def _collect_one(tool_name, params, category, degrade):
    req = ToolRequest(tool_name=tool_name, params=params, run_id=run_id)
    result = await gateway.call_tool(req)  # 原始 ToolResult
    # 直接对 ToolResult 做简单分类 → EvidenceItem
    classification = classify_result(...)
    return (evidence, classification)

results = await asyncio.gather(*[_collect_one(t, p, c, d) for t, p, c, d in tasks_to_run])
```

**问题**：
- 工具返回的 raw payload 未经分析，下游 `evidence_aggregate` 只能做规则评分（计数、category 分类）
- 异常信号被淹没在 raw data 中（如几百条 K8s events 里只有 1 条 CrashLoopBackOff）
- 每个工具调用之间无关联分析（如 K8s pod 重启时间与 DB 慢查询时间窗口的关系）

### 2.3 目标架构

**v1 实现（当前方案）：全量并行调用，无调度器。**

```
planner_node (产出 AgentTask 列表，见 2.4.1)
       │
       ▼
evidence_fanout_node_v2
       │
       │  AgentTask → SpecialistAgent.run(agent_task)
       │  asyncio.gather 并行调用所有启用的 Agent
       │
    ┌──┴───┬───┬───┬───┐
    ▼      ▼   ▼   ▼   ▼
  K8s    DB  Log Metr Depl   ← 5 个 Specialist Agent 同时启动
  Spec   Spec Spec Spec Spec
    │      │   │   │   │
    ▼      ▼   ▼   ▼   ▼
  SpecialistAnalysis[]
       │
       ▼
evidence_aggregate_v2: 对 Agent 结论做冲突检测 + 全局关联分析
```

**调度决策**：v1 不做动态调度。`planner_node` 产出的 `AgentTask` 列表中包含哪些 Agent，就全量并行调用哪些。每个 Agent 内部的 ReAct 循环自主决定调用什么工具、调用几轮。Supervisor/动态选择推迟到方案三。

**v2 演进（方案三 Dynamic Orchestrator）**：
```                        ┌─────────────┐
planner(初始) → Orchestrator ←─┐         │
                   │    │    │   (循环)  │
                   ▼    │    └───────────┘
              Round 1: K8s + Metrics
                   │
              分析结论
                   │
              Round 2: Deployment + DB  (根据 Round 1 结果动态选择)
                   │
              分析结论
                   │
              Round 3: 证据足够 → 进入 diagnose
```

### 2.4 Specialist Agent 详细设计

#### 2.4.1 Agent 定义与任务类型

```python
class SpecialistAgentConfig(BaseModel):
    agent_id: str                          # e.g. "k8s_specialist"
    category: str                          # e.g. "k8s"
    tool_names: List[str]                  # 可调用的工具列表（白名单）
    system_prompt: str                     # 角色定义 + 分析指令
    max_tool_rounds: int = 3               # ReAct 最大轮次
    time_budget_ms: int = 30_000           # 单 Agent 总时间预算
    temperature: float = 0.3               # 分析型任务用低温度
    enabled: bool = True                   # 是否启用（校验失败时自动置为 False）

# v1 加载方式：启动时从 YAML 配置文件硬编码，不依赖 DB
# 配置文件路径：backend/app/graph/nodes/agent_configs.yaml
# 开关：AGENT_FEATURE_SPECIALIST_POOL=true 时加载，false 时跳过
# v2 演进方向：支持从管理 API/DB 动态加载，允许热更新 system_prompt 和 tool_names
# 安全校验详见 2.4.7

class AgentTask(BaseModel):
    """Agent 级别的任务——替代工具级别的 InvestigationTask 作为 Agent.run() 的输入。

    与 InvestigationTask 的区别：
      InvestigationTask: tool_name + params  → 一次工具调用
      AgentTask:          agent_id + context → 一个 Agent 的完整分析任务（Agent 内部自行决定调哪些工具）
    """
    agent_id: str                          # 对应 SpecialistAgentConfig.agent_id
    category: str
    service: str                           # 目标服务名
    env: str                               # 目标环境
    incident_type: str                     # 从 triage 传入的故障类型
    time_window_start: Optional[str] = None  # ISO 8601，如 "2025-06-03T12:00:00Z"
    time_window_end: Optional[str] = None    # ISO 8601
    extra_context: Dict[str, Any] = {}     # 额外上下文（如 ticket title/description）
    timeout_ms: int = 30_000               # 此 Agent 的总时间预算（可覆盖 config 默认值）
```

**planner_node 改造**（配合 AgentTask）：
- 方案一阶段，`planner_node` 的逻辑从「根据 incident_type 生成 tool 级任务」改为「根据 incident_type 生成 agent 级任务」
- 改动量小：将现有的 `_add("k8s", "query_k8s_deployment_status", 2, s)` 模式替换为产出 `AgentTask` 列表
- 默认行为：对所有非空 category 各生成一个 AgentTask
- `_category_applies()` 规则——根据 incident_type 决定哪些 category 有分析价值：

  ```python
  def _category_applies(category: str, incident_type: str, service: str) -> bool:
      """根据故障类型判断是否调度该 category 的 Specialist Agent。

      当前策略: 全调度（方案一 v1）。可后续优化为按类型裁剪。
      保留此函数接口以便方案三按需覆盖。
      """
      # v1: 对所有已知故障类型全量调度 5 个 Agent
      # 依据：即使某领域非首因，其分析结论（尤其是 correlation_hint）对全局因果链有价值
      return True
  ```

  v1 简化：`_category_applies()` 始终返回 True。这意味着 deployment_regression 也会调 DB Specialist，
  resource_exhaustion 也会调 Deployment Specialist——因为跨领域关联线索对 aggregate 的因果链推断至关重要。
  v2（方案三）可改为按 incident_type 动态裁剪。
- 示例：

  ```python
  # planner_node v1（改造后）
  agent_tasks = []
  for cat in ["k8s", "db", "logs", "metrics", "deployments"]:
      if _category_applies(cat, incident_type, service):
          agent_tasks.append(AgentTask(
              agent_id=f"{cat}_specialist",
              category=cat,
              service=service,
              env=env,
              incident_type=incident_type,
              time_window_start=time_start,
              time_window_end=time_end,
          ))
  state["agent_tasks"] = [t.model_dump() for t in agent_tasks]
  # 同时写入旧 plan 格式，兼容 flag=false 的回退路径
  state["plan"] = {
      "tasks": [task_to_legacy(t) for t in agent_tasks],
      "rationale": rationale,
  }
  ```
- `InvestigationPlan` / `InvestigationTask` 在方案一中**仍写入 state（兼容 flag=false）**，新逻辑优先读 `agent_tasks`

**feature flag 回退数据流：**

```
AGENT_FEATURE_SPECIALIST_POOL=true:
  planner_node → state["agent_tasks"]  (AgentTask 列表)
              → state["plan"]          (兼容旧格式，task_to_legacy 转换)
  evidence_fanout_node_v2 → 读 agent_tasks → SpecialistAgent.run()
  evidence_aggregate_node_v2 → 读 specialist_analyses

AGENT_FEATURE_SPECIALIST_POOL=false:
  planner_node → state["plan"]         (旧格式，InvestigationTask 列表)
  evidence_fanout_node  → 读 plan → _collect_one()（旧逻辑）
  evidence_aggregate_node → 读 evidence_items（旧逻辑）
```
```

#### 2.4.2 五种 Specialist Agent 定义（含工具归属与边界）

**核心原则：每个工具只归属于一个 Specialist Agent，不存在共享工具。Agent 的 `tool_names` 白名单互不相交。**

| Agent | 独占工具 | 核心分析职责 | 输出重点 |
|-------|---------|-------------|---------|
| **K8s Specialist** | `query_k8s_deployment_status`, `query_k8s_pods`, `query_k8s_events` | K8s 集群层面：Deployment 状态（replicas/ready/updated）、Pod 生命周期（CrashLoop/OOM/Pending）、集群 Events（FailedScheduling/Unhealthy） | Pod 级别的健康信号与故障原因（OOMKilled、ImagePullBackOff 等），但不分析应用层日志内容 |
| **DB Specialist** | `query_db_processlist`, `query_db_slow_queries`, `query_db_table_status`, `query_db_variables` | DB 实例层面：连接池状态、慢查询模式、锁等待链、配置参数异常 | DB 是否是当前故障的瓶颈或受害者（连接耗尽、慢查询突增、死锁） |
| **Log Specialist** | `query_logs` | **应用层日志**：从业务日志中提取 ERROR/WARN 级别异常、异常堆栈、按时间窗口聚合错误模式 | **应用视角**的异常信号（Exception 类型、错误频率变化），注意与 K8s `query_k8s_pod_logs_summary` 的区别见下方边界说明 |
| **Metrics Specialist** | `query_metrics` | **K8s Pod 级资源指标**（CPU/Memory usage、OOM kill count、restart count）+ **阿里云 CMS 业务指标**（QPS、P95 latency、error rate）。`query_metrics` 的底层数据源由 adapter 模式决定：mock 返回仿真数据，real 通过阿里云 CMS API 拉取（含 K8s 容器指标和业务 SLB 指标） | 指标趋势分析：确认「什么时候开始恶化」「恶化速率」「当前是否仍在恶化」，标注指标类型和数据源 |
| **Deployment Specialist** | `query_deployments` | 发布历史层面：近期 Deployment 变更记录、版本 diff、灰度比例、回滚历史 | 发布是否是故障诱因（变更时间与故障开始的时序关系） |

**边界说明（共 3 处易混淆点）**：

1.  **K8s `query_k8s_pod_logs_summary` vs Log `query_logs`**
    | 维度 | `query_k8s_pod_logs_summary`（K8s Specialist） | `query_logs`（Log Specialist） |
    |------|------|------|
    | 数据源 | kubectl logs（容器 stdout/stderr 尾部摘要） | 集中式日志平台（如 ELK/Loki/阿里云 SLS），全文检索 |
    | 内容粒度 | 最后 N 行原始文本，无结构化解析 | 按时间范围 + 关键字过滤的结构化日志，含 timestamp/level/thread/traceId |
    | 分析职责 | **K8s 视角**：判断 Pod 是否因启动报错而 crash（如 `FATAL: config file not found`） | **应用视角**：分析业务错误的模式、频率、堆栈分布（如 `NullPointerException` 在发布后激增 200%） |
    | 决策规则 | K8s Specialist 用此工具作为 Pod 状态异常的**补充信息**，不替代 Log Specialist | Log Specialist 是应用日志的**唯一入口**，不依赖 K8s 的日志工具 |

2.  **K8s `query_k8s_deployment_status` vs Deployment `query_deployments`**
    | 维度 | `query_k8s_deployment_status`（K8s Specialist） | `query_deployments`（Deployment Specialist） |
    |------|------|------|
    | 数据类型 | K8s Deployment 资源的**实时状态**（readyReplicas、updatedReplicas、conditions） | 发布系统的**变更历史记录**（谁、什么时间、发布了什么版本、变更内容） |
    | 回答的问题 | "Deployment 现在健康吗？rollout 是否卡住？" | "最近是否有发布？发布改了什么？" |
    | 工具归属 | K8s Specialist 独占 | Deployment Specialist 独占 |

3.  **Metrics 数据源归属**：`query_metrics` 是唯一指标查询入口。K8s 的 Pod CPU/Memory 指标和阿里云 CMS 的 SLB QPS/Latency 指标**通过同一个 `query_metrics` 工具按不同 `metric_type` 参数查询**，统一由 Metrics Specialist 分析。K8s Specialist **不**查询指标。

#### 2.4.3 ReAct 循环伪代码（含降级路径）

```python
from enum import Enum

class AgentRunStatus(str, Enum):
    COMPLETED = "COMPLETED"          # 正常完成，产出完整 SpecialistAnalysis
    PARTIAL = "PARTIAL"              # 部分成功（LLM 最终分析失败但有 raw data）
    DEGRADED = "DEGRADED"            # 降级成功（规则兜底分析）
    TIMEOUT = "TIMEOUT"              # 时间预算耗尽
    LLM_FAILED = "LLM_FAILED"        # LLM 不可用，无任何产出

class SpecialistAgent:
    def __init__(self, config: SpecialistAgentConfig):
        self.config = config
        self.messages: List[Dict] = []
        self.collected_raw: Dict[str, Any] = {}
        self.run_status = AgentRunStatus.COMPLETED

    async def run(self, agent_task: AgentTask, run_id: str) -> SpecialistAnalysis:
        deadline = time.monotonic() + agent_task.timeout_ms / 1000
        # 重置实例状态（防多次调用间泄漏）
        self.collected_raw = {}
        self.run_status = AgentRunStatus.COMPLETED
        self.messages = [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": self._build_initial_prompt(agent_task)}
        ]

        # —— Phase 1: ReAct 循环 ——
        round_truncated = False
        response = None  # 初始化，防止 UnboundLocalError
        for round_idx in range(self.config.max_tool_rounds):
            remaining_ms = (deadline - time.monotonic()) * 1000
            if remaining_ms <= 2000:  # < 2s 不够再调一轮 LLM
                self.run_status = AgentRunStatus.TIMEOUT
                round_truncated = True
                break

            try:
                response = await asyncio.wait_for(
                    llm_client.complete_async(
                        messages=self.messages,
                        tools=self._get_tool_definitions(),
                        temperature=self.config.temperature,
                    ),
                    timeout=min(remaining_ms / 1000, 15.0)  # LLM 调用超时 ≤ 15s
                )
            except asyncio.TimeoutError:
                logger.warning(
                    f"Agent {self.config.agent_id}: LLM timeout at round {round_idx}, "
                    f"remaining {remaining_ms:.0f}ms"
                )
                self.run_status = AgentRunStatus.TIMEOUT
                round_truncated = True
                break
            except Exception as e:
                logger.error(f"Agent {self.config.agent_id}: LLM failed at round {round_idx}: {e}")
                self.run_status = AgentRunStatus.LLM_FAILED
                break

            if response.tool_calls:
                # 并行执行本轮所有工具调用。
                # 单工具超时 = min(30s, 剩余 Agent 预算 / len(tool_calls))，
                # 确保 asyncio.gather 的总等待时间不超过 Agent 剩余时间预算
                per_tool_timeout = min(30.0, max(remaining_ms / 1000 / len(response.tool_calls), 2.0))
                tool_tasks = []
                for tc in response.tool_calls:
                    tool_tasks.append(
                        asyncio.wait_for(
                            gateway.call_tool(ToolRequest(
                                tool_name=tc.name, params=tc.params, run_id=run_id
                            )),
                            timeout=per_tool_timeout
                        )
                    )
                tool_results = await asyncio.gather(*tool_tasks, return_exceptions=True)

                # 将结果注入消息历史（失败的工具也注入错误信息）
                for i, tr in enumerate(tool_results):
                    tc = response.tool_calls[i]
                    if isinstance(tr, Exception):
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps({
                                "tool_name": tc.name,
                                "success": False,
                                "error": f"ToolError: {type(tr).__name__}: {str(tr)[:300]}",
                                "result": None
                            })
                        })
                        logger.warning(
                            f"Agent {self.config.agent_id}: tool '{tc.name}' failed: {str(tr)[:100]}"
                        )
                    elif tr.success:
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps({
                                "tool_name": tc.name,
                                "success": True,
                                "result": tr.result
                            })
                        })
                        # 收集 raw data：同工具多轮调用时追加而非覆盖
                        key = tc.name
                        if key in self.collected_raw:
                            # 同一工具第二次调用 → 转为列表存储
                            prev = self.collected_raw[key]
                            if isinstance(prev, list):
                                prev.append(tr.result)
                            else:
                                self.collected_raw[key] = [prev, tr.result]
                        else:
                            self.collected_raw[key] = tr.result
                    else:
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps({
                                "tool_name": tc.name,
                                "success": False,
                                "error": tr.error or "Unknown tool error",
                                "result": tr.result if tr.result else None
                            })
                        })
            else:
                break  # Agent 认为分析足够，无需继续

        # 检查是否 3 轮全部用完且 Agent 最后一轮仍在调工具（被强制截断）
        if round_idx == self.config.max_tool_rounds - 1 and not round_truncated and response is not None:
            if response.tool_calls:
                # 最后轮还在调工具 → 标注截断
                round_truncated = True
                logger.info(f"Agent {self.config.agent_id}: max rounds reached, forced truncation")

        # —— Phase 2: 产出最终结论 ——
        return await self._produce_final_analysis(round_truncated=round_truncated)

    def _build_initial_prompt(self, agent_task: AgentTask) -> str:
        """
        从 AgentTask 构建初始用户 prompt。
        Agent 从 prompt 中获取：故障背景（三要素 + title/description）、时间窗口、自身类别。
        tool_names 通过 LLM function calling 的 tools 参数传入，Agent 自行决定调哪个。
        """
        extra = ""
        if agent_task.extra_context:
            title = agent_task.extra_context.get("title", "")
            description = agent_task.extra_context.get("description", "")
            if title or description:
                extra = f"\n- 故障标题: {title}\n- 故障描述: {description}"

        return f"""## 任务：{self.config.category} 领域证据分析

### 故障背景
- 服务: {agent_task.service}
- 环境: {agent_task.env}
- 故障类型: {agent_task.incident_type}
- 时间窗口: {agent_task.time_window_start or '未知'} ~ {agent_task.time_window_end or '未知'}{extra}

### 你的角色
你是 {self.config.category} 领域的 SRE 专家。你只能调用 {self.config.category} 类别的工具。
请执行以下步骤：
1. 先调用你认为最相关的 1-2 个工具获取数据（避免一次调用过多工具，单轮建议 ≤ 2 个）
2. 根据返回结果判断是否需要补充查询（如需要可继续调用工具）
3. 当你认为信息足够时，停止调用工具

使用 function calling 调用工具，用中文简短回复你的决策思路即可。"""

    async def _produce_final_analysis(self, round_truncated: bool = False) -> SpecialistAnalysis:
        """
        降级层级（从高到低尝试）:
          L0: LLM 产出结构化 JSON → 解析为完整 SpecialistAnalysis（COMPLETED）
          L1: LLM 调用成功但 JSON 解析失败 → 规则兜底（PARTIAL）
          L2: LLM 调用失败/超时，但有 raw data → 规则兜底（PARTIAL）
          L3: 无 LLM 产出 + 无 raw data → 最小空壳（LLM_FAILED）

        最终分析是额外一次 LLM 调用（不计入 max_tool_rounds）。
        仅在 run_status 非异常时发起；TIMEOUT/LLM_FAILED 直接走规则兜底。
        round_truncated=True 时在 prompt 中告知 LLM 被截断，要求基于现有数据产出结论。
        """
        if self.run_status in (AgentRunStatus.TIMEOUT, AgentRunStatus.LLM_FAILED):
            return self._build_degraded_analysis(
                reason=f"Agent {self.config.agent_id}: {self.run_status.value}",
                round_truncated=round_truncated,
            )

        truncation_note = ""
        if round_truncated:
            truncation_note = (
                "\n注意：你的工具调用被时间或轮次限制截断。"
                "请基于以下已收集到的数据产出分析结论，标注哪些结论因数据不足而推测。"
            )

        final_prompt = f"""基于以上所有工具调用结果，请输出最终分析结论。

{truncation_note}

请严格按以下 JSON schema 输出（不要包含任何额外文本）：

{{
  "conclusion": "<一句话总结本领域的关键发现，格式: [正常|异常] <具体发现>。如 '异常: payment-service 2个Pod处于CrashLoopBackOff，原因为OOMKilled(exit code 137)，最近一次重启在14:31:22' >",
  "severity": "normal|warning|critical",
  "anomalies": [
    {{
      "signal_type": "<异常类型，如 OOMKilled|high_latency|connection_pool_exhausted|crash_loop>",
      "description": "<人类可读的描述>",
      "timestamp_hint": "<ISO 8601 格式时间，如 2025-06-03T14:30:00Z，或 null>"
    }}
  ],
  "correlation_hints": [
    {{
      "target_category": "<建议关联分析的领域: k8s|db|logs|metrics|deployments>",
      "reason": "<关联原因，引用具体数据>",
       "confidence": <0.0-1.0, LLM 推测的关联最大 0.6，有数据支撑的可给 0.7+>
    }}
  ],
  "execution_summary": "<执行摘要: 调用了哪些工具、几轮、核心发现>",
  "confidence": <本分析的总体置信度 0.0-1.0>
}}

规则：
- anomalies: 只列出有数据支撑的异常，不要猜测。没有异常则输出空数组 []
- correlation_hints: 仅当你发现跨领域的关联线索时才给出，confidence 不超过 0.6（LLM 推测，代码层封顶 0.6）
- 如果所有工具都返回错误，conclusion 写 '异常: 所有工具调用失败，无法完成分析'，severity='normal'"""

        try:
            llm_output = await asyncio.wait_for(
                llm_client.complete_async(
                    messages=self.messages + [{"role": "user", "content": final_prompt}],
                    temperature=0.2,
                ),
                timeout=15.0,  # 最终分析 LLM 调用最多 15s
            )
            # 提取 JSON（可能被 markdown 包裹）
            json_match = re.search(r'\{[\s\S]*\}', llm_output)
            if not json_match:
                raise ValueError("No JSON found in LLM response")
            parsed = json.loads(json_match.group())

            # 构建 evidence_items：一个 SpecialistEvidence 包含该 Agent 的所有 anomaly
            # （不是每个 anomaly 一个 SpecialistEvidence）
            evidence_items = []
            if parsed.get("anomalies") or parsed.get("conclusion"):
                se_evidence_id = f"se_{self.config.agent_id}_{uuid.uuid4().hex[:8]}"
                evidence_items.append(SpecialistEvidence(
                    evidence_id=se_evidence_id,
                    category=self.config.category,
                    conclusion=parsed.get("conclusion", ""),
                    severity=parsed.get("severity", "normal"),
                    anomalies=[
                        # AnomalySignal.evidence_ref 由代码填入（LLM 不输出此字段），
                        # 指向父级 SpecialistEvidence 的 evidence_id，构建 1:N 引用关系
                        AnomalySignal(
                            evidence_ref=se_evidence_id,
                            **{k: v for k, v in a.items() if k != "evidence_ref"}
                        )
                        for a in parsed.get("anomalies", [])
                    ],
                    correlation_hints=[
                        CorrelationHint(
                            source_category=self.config.category,  # ← 代码自动填入
                            source="llm",
                            # LLM 推测的 confidence 代码层强制封顶 0.6（满足 aggregate 的 ≥0.6 阈值，允许 LLM hint 参与因果链）
                            confidence=min(h.get("confidence", 0.3), 0.6),
                            **{k: v for k, v in h.items() if k not in ("source_category", "confidence", "source")}
                        )
                        for h in parsed.get("correlation_hints", [])
                    ],
                ))

            return SpecialistAnalysis(
                agent_id=self.config.agent_id,
                agent_category=self.config.category,
                evidence_items=evidence_items,
                collected_tool_names=list(self.collected_raw.keys()),
                raw_tool_results=self.collected_raw,  # 嵌入 raw 数据，model_dump 后不丢失
                execution_summary=parsed.get("execution_summary", ""),
                # LLM 自评 confidence 代码层封顶 0.9（防备 LLM 输出 0.99 等过于自信的值），
                # 下限 0.0 保持
                confidence=min(max(parsed.get("confidence", 0.5), 0.0), 0.9),
                run_status=AgentRunStatus.COMPLETED,
                partial=False,
                truncated=round_truncated,
            )
        except (asyncio.TimeoutError, json.JSONDecodeError, KeyError, ValidationError, ValueError) as e:
            logger.warning(f"Agent {self.config.agent_id}: final analysis failed: {e}")
            return self._build_degraded_analysis(
                reason=f"Final analysis error: {str(e)[:100]}",
                round_truncated=round_truncated,
            )
        except Exception as e:
            logger.error(f"Agent {self.config.agent_id}: unexpected error in final analysis: {e}")
            return self._build_degraded_analysis(
                reason=str(e)[:200], round_truncated=round_truncated
            )

    def _build_degraded_analysis(self, reason: str, round_truncated: bool = False) -> SpecialistAnalysis:
        """
        规则兜底：不依赖 LLM，从 collected_raw 中提取可识别的信号。
        每种 Agent 有各自的规则提取函数（见 2.4.5）。
        round_truncated 用于标记是否因超时/轮次被截断。
        """
        degraded_evidence = self._extract_signals_by_rules()

        if degraded_evidence or self.collected_raw:
            return SpecialistAnalysis(
                agent_id=self.config.agent_id,
                agent_category=self.config.category,
                evidence_items=degraded_evidence or [],
                collected_tool_names=list(self.collected_raw.keys()),
                raw_tool_results=self.collected_raw,
                execution_summary=f"DEGRADED: {reason}",
                confidence=0.25,  # 规则兜底的置信度固定为 0.25
                run_status=AgentRunStatus.PARTIAL,  # collected_raw is truthy here (guarded by 'or' above)
                partial=True,
                truncated=round_truncated,
            )
        else:
            return SpecialistAnalysis(
                agent_id=self.config.agent_id,
                agent_category=self.config.category,
                evidence_items=[SpecialistEvidence(
                    evidence_id=f"degraded_{self.config.agent_id}",
                    category=self.config.category,
                    conclusion=f"失败: Agent {self.config.agent_id} 未能完成分析: {reason}",
                    severity="normal",
                    anomalies=[],
                    correlation_hints=[],
                )],
                collected_tool_names=[],
                raw_tool_results={},
                execution_summary=f"FAILED: {reason}",
                confidence=0.0,
                run_status=AgentRunStatus.LLM_FAILED,
                partial=True,
                truncated=round_truncated,
            )
```

**关键设计决策**：
- **每轮可并行调多个工具**：Agent 一轮决策可同时调用 `query_k8s_pods` + `query_k8s_events`
- **`max_tool_rounds=3`**：最多 3 轮 ReAct；耗尽后直接进入 `_produce_final_analysis()`（可能是 PARTIAL 状态）
- **`return_exceptions=True`**：单工具调用失败不中断整轮，失败的 tool_result 作为 `Exception` 对象注入消息历史
- **共享 `ToolGateway`**：所有 Agent 共用同一网关，保证审计、追踪、权限一致性
- **时间预算优先于轮次**：见 2.4.6 节

#### 2.4.4 结构化分析结论（SpecialistAnalysis）

```python
class SpecialistEvidence(BaseModel):
    """Specialist Agent 产出的单个证据项"""
    evidence_id: str
    category: str
    conclusion: str                       # 分析结论（人类可读）
    severity: Literal["normal", "warning", "critical"]
    anomalies: List[AnomalySignal] = []   # 降级模式下可为空
    correlation_hints: List[CorrelationHint] = []


class AnomalySignal(BaseModel):
    signal_type: str                      # e.g. "OOMKilled", "high_latency", "connection_pool_exhausted"
    evidence_ref: str                     # 关联的 raw tool_result evidence ID
    description: str
    timestamp_hint: Optional[str] = None  # ISO 8601 格式，如 "2025-06-03T14:30:00Z"；规则提取时用工具返回的时间戳填充，LLM 输出时按 prompt 要求填写


class CorrelationHint(BaseModel):
    """Agent 对跨域关联的建议。

    source_category 由 SpecialistAgent 在 _produce_final_analysis 中自动填写（= agent_category），
    不依赖 LLM 输出。经过 model_dump() 序列化后仍可通过此字段反查来源。

    confidence 来源优先级:
      1. 工具数据直接支撑的关联（如日志时间戳对齐）→ confidence 由规则计算，不使用 LLM 自评
      2. LLM 推测的关联（无数据支撑，仅凭经验）→ confidence 由 LLM 自评，但代码层强制封顶 0.6
      3. evidence_aggregate_v2 消费时启用阈值：concrete（≥0.6）参与因果链构建，
         speculative（0.3-0.6）仅作为辅助提示，<0.3 丢弃
    """
    source_category: str = ""              # 由代码自动填写（= Agent 的 category），不来自 LLM
    target_category: str                   # 建议关联分析的目标领域，e.g. "db"
    reason: str                            # 关联原因
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["rule", "llm"] = "llm" # 标记 confidence 来源


class SpecialistAnalysis(BaseModel):
    agent_id: str
    agent_category: str
    evidence_items: List[SpecialistEvidence] = []
    collected_tool_names: List[str] = []    # 此 Agent 成功调用过的工具名列表
    raw_tool_results: Dict[str, Any] = {}   # 工具名 → 原始返回结果（model_dump 后保留，供 fanout 重建 evidence_items）
    execution_summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    run_status: AgentRunStatus
    partial: bool = False
    truncated: bool = False
```

**`conclusion` 字段格式约束**：为支持下游 evidence_aggregate_v2 解析，conclusion 必须包含以下结构化前缀之一：
- `正常: <发现>` → 该领域无异常
- `异常: <发现>` → 该领域有异常
- `部分: <发现>` → Agent 产出不完整（partial 或 truncated）
- `失败: <原因>` → Agent 完全失败（LLM_FAILED）

evidence_aggregate_v2 通过 conclusion 前缀快速分类，不需要再次调用 LLM 来比对 Agent 结论。

`partial=True` 时下游处理约定：
- `evidence_aggregate_v2` 对 `partial=True` 的分析降低权重（confidence 乘以 0.5）
- `diagnose_node` 在 prompt 中标记该 Agent 产出为 "Partial/降级分析"
- `critic_node` 将 `partial` 比例计入证据质量评估（超过 40% Agent 为 partial → 触发 NEED_MORE_EVIDENCE）

`truncated=True` 时额外处理：
- `evidence_aggregate_v2` 在 `evidence_summary` 中标注 "N 个 Agent 因超时/轮次被截断"
- `critic_node` 将 truncated Agent 数量计入质量评估
- `max_tool_rounds` 耗尽导致的截断**不**自动触发 NEED_MORE_EVIDENCE（因为 Agent 已拿到数据，只是分析可能不完整）

#### 2.4.5 降级与容错路径（详细设计）

**总体原则**：每个降级层级都产出确定性的 `SpecialistAnalysis`（永不抛异常），通过 `run_status` 和 `partial` 字段向上游传递质量信号。

**降级分类矩阵**：

| 失败场景 | run_status | partial | confidence | 产出内容 |
|---------|-----------|---------|------------|---------|
| 正常完成 | COMPLETED | False | 0.5-0.9（LLM自评） | LLM 结构化 JSON |
| LLM 最终分析成功，但 JSON 解析失败 | PARTIAL | True | 0.25（固定） | 规则从 raw data 提取信号 |
| LLM ReAct 阶段超时，有 raw data | PARTIAL | True | 0.25（固定） | 规则从 raw data 提取信号 |
| LLM ReAct 阶段超时，无 raw data | LLM_FAILED | True | 0.0 | 空结论 + 原因说明 |
| LLM 完全不可用（API 5xx），有 raw data | PARTIAL | True | 0.25（固定） | 规则从 raw data 提取信号 |
| LLM 完全不可用，无 raw data | LLM_FAILED | True | 0.0 | 空结论 + 原因说明 |
| 所有工具调用均失败，LLM 可用 | COMPLETED | False | 0.3-0.6 | LLM 基于失败消息上下文分析（无实际数据），可产出结论但置信度低 |
| 工具调用超时（单工具级别） | 不影响整体状态 | — | — | `return_exceptions=True`，该工具结果以 Exception 形式注入，Agent 可跳过继续 |

> **注意**：`DEGRADED`（行530-572 的 `not self.collected_raw and degraded_evidence` 分支）在规则提取需依赖 raw data 的前提下不可达，保留枚举值仅供未来扩展。`TIMEOUT` 作为 `AgentRunStatus` 仅用于 ReAct 循环内部控制流（`self.run_status`），在最终 `SpecialistAnalysis.run_status` 中始终被转换为 `PARTIAL`（有 raw data）或 `LLM_FAILED`（无 raw data）。

**各 Agent 的规则提取函数（`_extract_signals_by_rules`）**：

| Agent | 规则提取逻辑（不依赖 LLM） |
|-------|--------------------------|
| K8s Specialist | 检查 `query_k8s_pods` 返回的 containerStatuses：`waiting.reason` 含 CrashLoopBackOff/ErrImagePull/OOMKilled → 生成 AnomalySignal；检查 `query_k8s_deployment_status` 的 readyReplicas < desiredReplicas → 生成 warning |
| DB Specialist | 检查 `query_db_processlist` 的 COMMAND != 'Sleep' 连接数 > 阈值（默认 50）→ 生成 warning；`query_db_slow_queries` 结果行数 > 10 → 生成 anomaly |
| Log Specialist | 用正则 `ERROR\|FATAL\|Exception` 对 `query_logs` 结果计数，超过阈值（默认 10）→ 生成 warning |
| Metrics Specialist | 检查 `query_metrics` 返回的每个 metric 的时间序列：相邻两点变化率 > 50% → 生成 anomaly |
| Deployment Specialist | 检查 `query_deployments` 返回的最近一次部署时间距当前 < 2h → 生成 correlation_hint（target="k8s" 或 "logs"，source_category="deployments"，**confidence=0.6**，source="rule"）。规则提取的 hint 级 confidence 独立于 SpecialistAnalysis 级 confidence（0.25） |

#### 2.4.6 超时与轮次优先级、全量/选择性调度

**(a) time_budget_ms 与 max_tool_rounds 的优先级**

**time_budget_ms 严格优先于 max_tool_rounds。** 实现方式：

1. 每轮 ReAct 开始前检查剩余时间：`remaining_ms = deadline - now()`。若 `remaining_ms < 2000`（不足一次 LLM 调用的最小时间），强制退出循环，标记 `TIMEOUT`，直接进入 `_produce_final_analysis()`
2. LLM 调用本身加 `asyncio.wait_for(timeout=min(remaining_ms/1000, 15.0))`——单次 LLM 最多等 15s，且不超过剩余时间预算
3. 时间耗尽时，若已有 raw data，走 PARTIAL 降级（规则提取）；若无 data，走 LLM_FAILED 空壳

**(b) max_tool_rounds=3 耗尽后的行为**

不是返回空，而是**直接进入 Phase 2（`_produce_final_analysis`）**。Agent 已有 3 轮的 raw data 积累，即使没有显式的 "stop" 信号，也要强制要求 LLM 基于现有数据产出结论。此行为与时间耗尽一致（COMPLETED/PARTIAL），不走空壳。

**(c) Agent 调度方式（纠正"全量调用"歧义）**

**v1 实现：按 planner 产出的 AgentTask 列表并行调用。**

- `planner_node` 产出 `agent_tasks` 列表——包含哪些 Agent 就调哪些（目前 5 个，但可通过 `_category_applies()` 裁剪）
- `evidence_fanout_node_v2` 遍历 `agent_tasks`，`asyncio.gather` 并行执行所有启用的 Agent（`config.enabled=True`）
- **"全量"在 v1 中的准确含义：对 planner 产出的每个 AgentTask 无一遗漏地并行调用。** 不是永远 5 个，而是「planner 输出多少就调多少」
- 校验失败（`enabled=False`）的 Agent：planner 仍会为其生成 AgentTask，但 fanout 调度时检测到 `enabled=False` → 跳过 runner，直接写入一个 `LLM_FAILED` 空壳 `SpecialistAnalysis`（`confidence=0.0, partial=True`）。这样 aggregate 能感知到该 Agent 未参与分析，而不是默默缺失
- 每个 Agent 内部的 ReAct 循环的**实际工具调用次数由 LLM 自行决策**（可能 0 次直接产出结论，也可能 3 轮）

方案一和方案三的调度对比：

| 维度 | 方案一（v1） | 方案三（v2，Dynamic Orchestrator） |
|------|------------|----------------------------------|
| 调度决策 | 无：plan 包含哪些 category 就全调 | LLM-driven：每轮根据已有证据动态选择 2-3 个 Agent |
| Agent 调用次数 | 固定（每 category 1 次） | 动态（同一 Agent 可能被多轮调用，参数不同） |
| 证据积累 | 一次性并行采集 | 逐轮增量，后轮可依赖前轮结论 |
| 实现位置 | `evidence_fanout_node` | `orchestrate_node`（合并 planner + fanout + aggregate） |

#### 2.4.7 SpecialistAgentConfig 动态加载与安全校验

**(a) 加载方式**

v1 采用 **启动时硬编码 + YAML 配置文件**，不依赖 DB：
- 5 个 Agent 的 `system_prompt`、`tool_names`、默认 `time_budget_ms` 等配置存放在 `backend/app/graph/nodes/agent_configs.yaml`
- 启动时通过 `load_agent_configs()` 加载为 `Dict[str, SpecialistAgentConfig]`
- 开关控制：`AGENT_FEATURE_SPECIALIST_POOL=true` 时加载配置并实例化 Agent；`false` 时回退到原有 `_collect_one` 逻辑
- v2（方案三后）可扩展为从管理 API/DB 读取，支持热更新

**(b) tool_names 白名单边界校验**

校验发生在 **Agent 初始化时**（而非每次调用时），校验失败 → 该 Agent 降级为不可用（`enabled=False`）：

```python
# 高危工具列表（硬编码，不可被任何 Specialist Agent 调用）
FORBIDDEN_TOOLS = {"execute_action"}

# category 白名单：每个 Agent 只能调用自己 category 对应的工具前缀
CATEGORY_TOOL_PREFIXES = {
    "k8s":     ["query_k8s_"],
    "db":      ["query_db_"],
    "logs":    ["query_logs"],
    "metrics": ["query_metrics"],
    "deployments": ["query_deployments"],
}

def validate_agent_config(config: SpecialistAgentConfig) -> bool:
    """初始化时校验。返回 False 则该 Agent 被禁用。"""
    # 检查 1: 禁止包含高危工具
    for tool in config.tool_names:
        if tool in FORBIDDEN_TOOLS:
            logger.error(f"Agent {config.agent_id}: forbidden tool '{tool}' in tool_names")
            return False

    # 检查 2: 工具前缀必须匹配 category（防止误配，如 K8s Agent 调了 DB 工具）
    allowed_prefixes = CATEGORY_TOOL_PREFIXES.get(config.category, [])
    for tool in config.tool_names:
        if not any(tool.startswith(prefix) for prefix in allowed_prefixes):
            logger.error(
                f"Agent {config.agent_id}: tool '{tool}' does not match "
                f"category '{config.category}' (allowed prefixes: {allowed_prefixes})"
            )
            return False

    # 检查 3: 工具是否在 gateway 中注册（describe_capability 返回 available=True 即注册）
    for tool in config.tool_names:
        cap = gateway.describe_capability(tool)
        if not cap.get("available"):
            logger.warning(
                f"Agent {config.agent_id}: tool '{tool}' not registered/available "
                f"(adapter_mode={cap.get('adapter_mode')}, reason={cap.get('reason')})"
            )
            # 不阻断，仅警告（允许超前配置 or mock 不可用场景）
    return True
```

校验失败的 Agent 被标记为 `enabled=False`，行为：
- **planner** 仍然为其生成 AgentTask（不感知 Agent 是否可用）
- **fanout** 检测到 `AgentTask.agent_id` 对应的 AgentConfig 的 `enabled=False` → 跳过 runner，直接注入空壳 `SpecialistAnalysis`：
  ```python
  SpecialistAnalysis(
      agent_id=agent_task.agent_id,
      agent_category=agent_task.category,
      evidence_items=[],
      collected_tool_names=[],
      execution_summary=f"SKIPPED: agent disabled due to config validation failure",
      confidence=0.0,
      run_status=AgentRunStatus.LLM_FAILED,
      partial=True,
      truncated=False,
  )
  ```
- **aggregate** 收到 `LLM_FAILED` 的 Agent → 不计入质量评分，标记为缺失 category

### 2.5 evidence_aggregate 升级

#### 2.5.1 现状

`evidence_aggregate_node`（`__init__.py:577-620`）做的是简单的规则统计：
- 计数量化 `quality_score`
- 简单的文本关键字冲突检测（"error" + "healthy" 同时出现）

#### 2.5.2 升级后

接收各 Specialist Agent 的 `SpecialistAnalysis` 列表，执行：

1. **冲突检测升级**：不再是文本匹配，而是对比各 Agent 的 conclusion 前缀和 severity：若 Agent A 报告"异常"而 Agent B 报告"正常"，且两者领域之间存在关联关系，标记为 CONTRADICTION
   - 例：K8s Agent 结论为"异常: Pod OOMKilled"，但 Metrics Agent 结论为"正常: 资源使用率正常" → 标记矛盾
2. **全局关联分析**：收集所有 Agent 的 `CorrelationHint`，发现跨领域的因果链
   - 例：Deployment Agent 报告 14:32 发布 → Log Agent 报告 14:33 错误激增 → DB Agent 报告 14:34 连接池满 → 自动构建时间线因果链
3. **缺失检测升级**：不仅检测缺失的 category，还检测 Agent 未覆盖的 `CorrelationHint.target_category`

```python
def evidence_aggregate_node_v2(state: IncidentAgentState) -> IncidentAgentState:
    # state["specialist_analyses"] 从 checkpoint 反序列化后是 List[Dict]，不是 List[SpecialistAnalysis]。
    # 所有字段访问使用 isinstance(obj, dict) else obj 防御模式（见下文）。
    analyses_raw = state["specialist_analyses"]

    # 收集所有异常信号（跳过 partial=True 的空 Agent）
    all_anomalies = []
    for obj in analyses_raw:
        if obj.get("partial", False) if isinstance(obj, dict) else obj.partial:
            continue
        for ev in (obj.get("evidence_items", []) if isinstance(obj, dict) else obj.evidence_items):
            anomalies = ev.get("anomalies", []) if isinstance(ev, dict) else ev.anomalies
            all_anomalies.extend(anomalies)

    # 全局关联分析：仅 confidence ≥ 0.6 的 concrete hint 参与因果链构建
    concrete_hints = []
    speculative_hints = []
    for obj in analyses_raw:
        is_partial = obj.get("partial", False) if isinstance(obj, dict) else obj.partial
        if is_partial:
            continue
        for ev in (obj.get("evidence_items", []) if isinstance(obj, dict) else obj.evidence_items):
            hints = ev.get("correlation_hints", []) if isinstance(ev, dict) else ev.correlation_hints
            for h in hints:
                conf = h.get("confidence", 0) if isinstance(h, dict) else h.confidence
                if conf >= 0.6:
                    concrete_hints.append(h)
                elif conf >= 0.3:
                    speculative_hints.append(h)
    # confidence < 0.3 的 hint 直接丢弃

    # 传递给核心算法（纯函数，接受 dict 或 Pydantic 对象均可）
    correlation_graph = _build_correlation_graph(concrete_hints)
    causual_chains = _infer_causual_chains(correlation_graph, all_anomalies)

    contradictions = _detect_cross_agent_contradictions(analyses_raw)

    quality_score = _compute_weighted_quality(analyses_raw)

    state["evidence_summary"] = _format_global_summary(
        analyses_raw, causual_chains, speculative_hints
    )
    state["evidence_quality_score"] = quality_score
    state["contradiction_signals"] = contradictions
    state["cross_agent_causual_chains"] = causual_chains

    return state


def _format_global_summary(
    analyses_raw: List[Any],
    causual_chains: List[Dict],
    speculative_hints: List[Any],
) -> str:
    """汇总所有 Agent 的分析结论，生成人类可读的全局证据摘要。"""
    parts = []
    for obj in analyses_raw:
        cat = obj.get("agent_category", "") if isinstance(obj, dict) else obj.agent_category
        truncated = obj.get("truncated", False) if isinstance(obj, dict) else obj.truncated
        partial = obj.get("partial", False) if isinstance(obj, dict) else obj.partial
        ev_items = obj.get("evidence_items", []) if isinstance(obj, dict) else obj.evidence_items
        for ev in ev_items:
            conclusion = ev.get("conclusion", "") if isinstance(ev, dict) else ev.conclusion
            tag = "[截断]" if truncated else ("[降级]" if partial else "")
            parts.append(f"- {cat}{tag}: {conclusion}")
    if causual_chains:
        chain_str = " -> ".join(causual_chains[0].get("chain", [])) if causual_chains else ""
        parts.append(f"因果链: {len(causual_chains)} 条 (示例: {chain_str})")
    if speculative_hints:
        parts.append(f"辅助线索: {len(speculative_hints)} 条 speculative hint")
    return "\n".join(parts) if parts else "No evidence collected"


# ═══════════════════════════════════════════════════════
# 核心算法实现
# ═══════════════════════════════════════════════════════

def _build_correlation_graph(
    hints: List[Any],
) -> Dict[str, List[Tuple[str, float]]]:
    """
    构建跨 Agent 关联图。

    图结构：有向加权图
    - 节点 = agent_category 字符串 ("k8s", "db", "logs", "metrics", "deployments")
    - 有向边 A → B = Agent A 建议关联分析 B 领域，权重 = hint.confidence
    - 多个 hint 指向同一边时，取最大 confidence
    - source_category 来自 CorrelationHint.source_category（兼容 dict 访问）

    返回：邻接表 { source_category: [(target_category, weight), ...] }

    输入可以是 Pydantic CorrelationHint 或 dict（checkpoint 反序列化后）。
    """
    graph: Dict[str, Dict[str, float]] = {}
    for h in hints:
        source = h.source_category if hasattr(h, 'source_category') else h.get('source_category', '')
        target = h.target_category if hasattr(h, 'target_category') else h.get('target_category', '')
        conf = h.confidence if hasattr(h, 'confidence') else h.get('confidence', 0.0)
        if not source or source == target:
            continue
        graph.setdefault(source, {})
        graph[source][target] = max(graph[source].get(target, 0.0), conf)
    return {k: [(t, w) for t, w in v.items()] for k, v in graph.items()}


def _infer_causual_chains(
    graph: Dict[str, List[Tuple[str, float]]],
    anomalies: List[AnomalySignal],
) -> List[Dict[str, Any]]:
    """
    从关联图推断因果链。

    算法：
    1. 找出图中入度为 0 的节点作为起点（无其他 Agent 关联到它→可能是根因）
     2. 从每个起点 DFS，收集路径上所有边
     3. 路径上**每个节点**都必须在该 Agent 的 anomaly 列表中有至少一个异常信号（否则该路径被丢弃）
     4. 按平均权重（总权重 / 路径长度）排序，取前 5 条

    返回：[{
        "chain": ["deployments", "logs", "db"],
        "edges": [("deployments", "logs", 0.8), ("logs", "db", 0.7)],
        "total_weight": 0.75,
        "root_cause_category": "deployments",
        "supporting_anomalies": ["deployment_found", "error_spike", "connection_pool_full"]
    }, ...]
    """
    # 计算入度
    in_degree: Dict[str, int] = {}
    for src, edges in graph.items():
        in_degree.setdefault(src, 0)
        for tgt, _ in edges:
            in_degree[tgt] = in_degree.get(tgt, 0) + 1

    # 收集各 category 的异常类型（anomalies 元素可能是 Pydantic 对象或 dict）
    category_anomalies: Dict[str, List[str]] = {}
    for a in anomalies:
        cat = _anomaly_to_category(a)
        sig = a.signal_type if hasattr(a, "signal_type") else a.get("signal_type", "")
        category_anomalies.setdefault(cat, []).append(sig)

    # 选出起点（入度=0 的节点优先；若全部入度>0，取入度最小的作为降级起点）
    roots = [n for n, deg in in_degree.items() if deg == 0]
    if not roots and in_degree:
        min_deg = min(in_degree.values())
        roots = [n for n, deg in in_degree.items() if deg == min_deg]
        logger.info(
            f"_infer_causual_chains: no zero-indegree nodes, "
            f"fallback to min-indegree={min_deg} nodes: {roots}"
        )

    # 从起点 DFS
    chains = []
    for root in roots:
        _dfs_chains(graph, root, [], 1.0, chains, category_anomalies)

    # 按 total_weight 降序，取前 5
    chains.sort(key=lambda c: c["total_weight"], reverse=True)
    return chains[:5]


def _dfs_chains(
    graph, node, path, weight_product, results, category_anomalies
):
    """DFS 获取因果链。路径上每个节点都必须有至少一个异常信号。
    权重使用平均值（total_weight / len(path)）排序。"""
    if node not in graph or not graph[node]:
        # 终端节点：检查完整路径上每个节点是否都有异常信号
        full_path = path + [node]
        if len(full_path) >= 2 and all(
            _node_has_anomaly(n, category_anomalies) for n in full_path
        ):
            # 收集路径上所有边
            edges = []
            for i in range(len(full_path) - 1):
                edge_weight = dict(graph.get(full_path[i], [])).get(full_path[i+1], 0)
                edges.append((full_path[i], full_path[i+1], edge_weight))
            avg_weight = (weight_product ** (1.0 / len(full_path))) if edges else 0.0
            results.append({
                "chain": full_path,
                "edges": edges,
                "total_weight": avg_weight,       # 平均权重，非连乘积
                "root_cause_category": full_path[0],
                "supporting_anomalies": category_anomalies.get(node, []),
            })
        return
    for tgt, weight in graph[node]:
        if tgt in path:
            continue
        _dfs_chains(graph, tgt, path + [node], weight_product * weight, results, category_anomalies)


def _node_has_anomaly(node: str, category_anomalies: Dict[str, List[str]]) -> bool:
    """检查该 category 的节点是否有至少一个异常信号（critical/warning 级别）。
    所有已录入 category_anomalies 的信号均来自 anomaly 列表，因此存在即满足条件。
    """
    return bool(category_anomalies.get(node, []))


def _anomaly_to_category(anomaly: AnomalySignal) -> str:
    """根据 anomaly 的 signal_type 反查其所属 category（基于已知映射）"""
    SIGNAL_CATEGORY_MAP = {
        ...
    }
    return SIGNAL_CATEGORY_MAP.get(
        anomaly.signal_type if hasattr(anomaly, 'signal_type') else anomaly.get('signal_type', ''),
        "unknown"
    )


def _detect_cross_agent_contradictions(
    analyses_raw: List[Any],
) -> List[Dict[str, Any]]:
    """
    检测跨 Agent 矛盾。analyses_raw 兼容 Pydantic 对象和 dict。

    矛盾定义：Agent A 报告了某领域的异常，但 Agent B（负责关联领域）的分析结论为"正常"。
    通过比对 conclusion 前缀（"正常:" / "异常:" / "部分:" / "失败:"）检测，
    不依赖 Agent 显式输出"一切正常"信号（因为 Agent 不会生成此类信号）。
    """
    # 预处理：收集每个 Agent 的 conclusion 前缀和 severity
    agent_states: Dict[str, Dict] = {}  # { category: {"is_anomaly": bool, "severity": str} }
    for obj in analyses_raw:
        cat = obj.get("agent_category", "") if isinstance(obj, dict) else obj.agent_category
        if (obj.get("partial", False) if isinstance(obj, dict) else obj.partial):
            continue
        ev_items = obj.get("evidence_items", []) if isinstance(obj, dict) else obj.evidence_items
        for ev in ev_items:
            conclusion = ev.get("conclusion", "") if isinstance(ev, dict) else ev.conclusion
            severity = ev.get("severity", "normal") if isinstance(ev, dict) else ev.severity
            is_anomaly = conclusion.startswith("异常:")
            if cat not in agent_states or (is_anomaly and not agent_states[cat].get("is_anomaly", False)):
                agent_states[cat] = {"is_anomaly": is_anomaly, "severity": severity}

    # 矛盾规则：(agent_A 必须为异常, agent_B 结论必须为正常)
    CONTRADICTION_RULES = [
        ("k8s", "metrics",
         "K8s 报告异常但 Metrics 分析正常——可能非资源级故障（如配置/代码错误）"),
        ("k8s", "deployments",
         "K8s 报告异常但 Deployment 分析正常——故障可能非发布导致"),
        ("db", "k8s",
         "DB 报告异常但 K8s 分析正常——DB 自身问题，非容器层故障"),
        ("db", "metrics",
         "DB 报告异常但 Metrics 正常——可能是慢查询/锁争用等非资源瓶颈"),
        ("logs", "k8s",
         "Logs 报告异常但 K8s 分析正常——应用层故障，非基础设施问题"),
        ("metrics", "k8s",
         "Metrics 报告异常但 K8s 分析正常——资源压力未导致 Pod 级故障"),
    ]

    contradictions = []
    for cat_a, cat_b, desc in CONTRADICTION_RULES:
        state_a = agent_states.get(cat_a, {})
        state_b = agent_states.get(cat_b, {})
        if state_a.get("is_anomaly") and not state_b.get("is_anomaly", False):
            contradictions.append({
                "type": "cross_agent_contradiction",
                "anomaly_agent": cat_a,
                "anomaly_severity": state_a.get("severity", "unknown"),
                "normal_agent": cat_b,
                "normal_severity": state_b.get("severity", "normal"),
                "description": desc,
                "severity": "warning",
            })

    return contradictions
```

**`_compute_weighted_quality` 公式**：

```python
def _compute_weighted_quality(analyses_raw: List[Any]) -> float:
    active_categories = len({
        obj.get("agent_category", "") if isinstance(obj, dict) else obj.agent_category
        for obj in analyses_raw
    })
    truncated_count = sum(1 for obj in analyses_raw
        if (obj.get("truncated", False) if isinstance(obj, dict) else obj.truncated))
    partial_count = sum(1 for obj in analyses_raw
        if (obj.get("partial", False) if isinstance(obj, dict) else obj.partial))

    total = sum(
        (obj.get("confidence", 0.0) if isinstance(obj, dict) else obj.confidence) * 0.5
        if (obj.get("partial", False) if isinstance(obj, dict) else obj.partial)
        else (obj.get("confidence", 0.0) if isinstance(obj, dict) else obj.confidence)
        for obj in analyses_raw
    )
    avg = total / max(len(analyses_raw), 1)
    penalty = max(1 - 0.1 * truncated_count, 0.5)
    coverage = min(active_categories / 5, 1.0)
    return max(avg * penalty * coverage, 0.0)
```

### 2.6 State 改动与数据兼容

#### 2.6.1 新增字段

`IncidentAgentState` 新增字段：

```python
class IncidentAgentState(TypedDict, total=False):
    # ... existing fields ...

    # Planner 产出（v1：Agent 级任务列表，替代 InvestigationTask）
    agent_tasks: List[Dict[str, Any]]                 # List[AgentTask]，planner_node 写入，fanout 读取

    # Specialist Agent 的产出
    specialist_analyses: List[Dict[str, Any]]          # List[SpecialistAnalysis]

    # evidence_aggregate v2 的产出
    cross_agent_causual_chains: List[Dict[str, Any]]   # 跨域因果链
    contradiction_signals: List[Dict[str, Any]]         # 矛盾信号详情
```

**planner → fanout 数据流约定（纠正不一致）：**
- `planner_node` 写入 `state["agent_tasks"]`（List[AgentTask]），同时写入 `state["plan"]`（向后兼容旧格式）
- `evidence_fanout_node_v2` 读取 `state["agent_tasks"]`（优先）→ 若无则回退读 `state["plan"]`
- `InvestigationPlan.tasks`（tool 级）在新的 Planner 中不再产出，除非 flag=false 回退

#### 2.6.2 specialist_analyses 与 evidence_items 的关系（明确说明）

**两套数据并存，各司其职：**

```
                    evidence_fanout_node_v2
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    specialist_analyses    evidence_items  collected_tool_names
    (新增，Agent 分析结论)  (保留，兼容下游) (新增，溯源用)
            │              │              │
            ├──────────────┴──────────────┤
            ▼                             ▼
    evidence_aggregate_v2          diagnose / rca
    (消费 specialist_analyses)    (消费 evidence_items)
```

**各字段职责：**

| 字段 | 职责 | 消费方 |
|------|------|--------|
| `evidence_items`（已有） | **raw 工具返回数据**（`EvidenceItem`），保持与现有节点兼容 | `diagnose_node`、`rca_node`（它们读 `evidence_items` 的 summary/raw_payload） |
| `specialist_analyses`（新增） | **Agent 分析后的结构化结论**（`SpecialistAnalysis`），含 anomalies/correlation_hints/conclusion | `evidence_aggregate_v2`（主要消费者） |
| `collected_tool_names`（在 `SpecialistAnalysis` 内部） | Agent 成功调用过的工具名列表 | 调试/审计/前端展示 |

**写入规则：**

1. `evidence_fanout_node_v2` 调用 Specialist Agent 后，同时写入两个字段：
   ```python
   # 1. 写入 specialist_analyses（Agent 分析结论，model_dump 后含 raw_tool_results）
   state["specialist_analyses"] = [sa.model_dump() for sa in specialist_results]

   # 2. 从 specialist_analyses 中的 raw_tool_results 重建 evidence_items（兼容下游）
   for sa in specialist_results:
       for tool_name, raw_result in sa.raw_tool_results.items():
           evidence = _build_raw_evidence_item(tool_name, raw_result, sa, run_id)
           state["evidence_items"].append(evidence)
   ```

   `_build_raw_evidence_item` 定义：
   ```python
   def _build_raw_evidence_item(
       tool_name: str, raw_result: Any, sa: SpecialistAnalysis, run_id: str
   ) -> EvidenceItem:
       """从 SpecialistAgent 的 raw tool result 重建 EvidenceItem（兼容下游）"""
       return EvidenceItem(
           evidence_id=f"ev_{sa.agent_id}_{tool_name}_{uuid.uuid4().hex[:8]}",
           tool_name=tool_name,
           category=sa.agent_category,
           source_ref=f"{sa.agent_id}-{run_id}",
           summary=f"Raw {tool_name} result from {sa.agent_id}",
           raw_payload=raw_result if isinstance(raw_result, dict) else {"data": str(raw_result)},
           confidence=sa.confidence,
           freshness_score=0.9,
           completeness_score=0.7 if sa.partial else 0.9,
       )
   ```

   `task_to_legacy` 定义（planner 双写兼容）：
   ```python
   def task_to_legacy(task: AgentTask) -> Dict[str, Any]:
       """将 AgentTask 转为旧 InvestigationTask 格式（写入 state["plan"] 做兼容）"""
       return {
           "task_id": task.agent_id,
           "category": task.category,
           "tool": task.category,        # 旧格式 tool 字段≈category
           "priority": 2,
           "params": {"service": task.service, "env": task.env},
           "degrade_on_failure": True,
       }
   ```

2. `evidence_aggregate_v2` **只读不写** `evidence_items`——它消费 `specialist_analyses`，产出 `evidence_summary` / `evidence_quality_score` / `causual_chains`

3. `diagnose_node` **无需改动**——它继续消费 `evidence_summary`（由 aggregate_v2 更新）和 `evidence_items`（raw data 作为补充上下文）

4. `rca_node` **无需改动**——它继续消费 `evidence_items` 和 `root_cause_candidates`

**feature flag 关闭时的回退：**

```python
# evidence_fanout_node 内部
if not settings.AGENT_FEATURE_SPECIALIST_POOL:
    # 回退到原有逻辑：_collect_one → evidence_items
    return original_evidence_fanout_node(state)
# 新逻辑：Specialist Agent → specialist_analyses + evidence_items
return evidence_fanout_node_v2(state)
```

#### 2.6.3 下游节点兼容简表

| 下游节点 | 需要改动？ | 说明 |
|---------|-----------|------|
| `evidence_aggregate_node` | 是 | 重写为 v2，消费 specialist_analyses |
| `diagnose_node` | 否 | 继续消费 evidence_summary + evidence_items（无改动） |
| `critic_node` | 否 | 继续消费 evidence_quality_score + root_cause_candidates（无改动），但后续可升级为 v2（方案二） |
| `remediation_node` | 否 | 继续消费 root_cause_candidates（无改动） |
| `rca_node` | 否 | 继续消费 evidence_items + root_cause_candidates（无改动） |

### 2.7 改造范围

| 文件 | 改动 | 说明 |
|------|------|------|
| `backend/app/graph/nodes/__init__.py` | 重写 `planner_node` | **关键变更**：产出 `AgentTask` 列表替代 `InvestigationTask`；不再生成 tool 级任务 |
| `backend/app/graph/nodes/__init__.py` | 重写 `evidence_fanout_node` | 接收 `agent_tasks`，遍历并行调用 SpecialistAgent.run() 替代 `_collect_one` |
| `backend/app/graph/nodes/__init__.py` | 重写 `evidence_aggregate_node` | 升级为 v2：关联图构建、因果链推断、矛盾检测 |
| `backend/app/graph/nodes/specialist_agent.py` | **新增** | SpecialistAgent 类 + ReAct 循环 + `_produce_final_analysis` + 5 个 Agent 配置加载 + `AgentTask` 模型 |
| `backend/app/graph/nodes/agent_configs.yaml` | **新增** | 5 个 Agent 的 system_prompt/tool_names/time_budget_ms 配置 |
| `backend/app/graph/nodes/aggregator.py` | **新增** | `_build_correlation_graph` / `_infer_causual_chains` / `_detect_cross_agent_contradictions` 纯函数（独立于节点，便于单元测试） |
| `backend/app/graph/state.py` | 新增字段 | `specialist_analyses`, `agent_tasks`, `cross_agent_causual_chains`, `contradiction_signals`；标记 `plan` 为 deprecated（由 `agent_tasks` 替代） |
| `backend/app/tools/gateway.py` | 新增方法 | `get_tool_schema(tool_name) → Dict[str, Any]` 返回 OpenAI function calling 兼容 JSON Schema。格式示例见下方 |

**`gateway.get_tool_schema()` 返回格式：**

```python
{
    "type": "function",
    "function": {
        "name": "query_k8s_pods",
        "description": "查询指定服务和环境的 K8s Pod 列表与状态",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "服务名称"},
                "env":     {"type": "string", "description": "环境，staging/prod"},
                "limit":   {"type": "integer", "description": "返回数量上限", "default": 50},
            },
            "required": ["service", "env"]
        }
    }
}
```

实现方式：从 `TOOL_REGISTRY` 中已有的 `param_schema` 字段读取（若存在），或从 `ToolRequest.params` 的 Pydantic 模型推导。`BaseAgent._get_tool_definitions()` 直接调用此方法获取 tools 参数传给 LLM。
| `backend/app/models/planning.py` | 新增模型 + 废弃标记 | 新增 `AgentTask`, `SpecialistAnalysis`, `SpecialistEvidence`, `AnomalySignal`, `CorrelationHint`；`InvestigationPlan` / `InvestigationTask` 标记 `@deprecated` |
| `backend/app/graph/builder.py` | 无改动 | 图拓扑不变，仅替换节点函数和 State 字段 |

### 2.8 测试策略

#### 2.8.1 单元测试

| 测试对象 | 测试内容 | Mock 策略 |
|---------|---------|----------|
| `SpecialistAgent._produce_final_analysis` | 正常 LLM 返回合法 JSON → COMPLETED；LLM 返回非法 JSON → PARTIAL（规则兜底）；LLM 超时 → PARTIAL | Mock `llm_client.complete_async` 返回预设字符串 |
| `SpecialistAgent._build_degraded_analysis` | 各 Agent 的 `_extract_signals_by_rules` 输入预设 raw data → 输出正确的 AnomalySignal 列表 | 无需 Mock LLM |
| `SpecialistAgent.run` ReAct 循环 | round 0: LLM 无 tool_calls → 直接产出结论；round 2: 两轮工具调用 + 最终分析；3 轮耗尽仍调用工具 → truncated=True | Mock LLM 返回预设的 tool_calls 数组（预设 3 轮响应） |
| `SpecialistAgent` 工具失败注入 | 模拟 `gateway.call_tool` 抛异常 → 验证消息历史中注入 `{"success": false, "error": "..."}` | Mock `gateway.call_tool` |
| `_build_correlation_graph` | 输入 3 个 concrete hint → 输出正确邻接表 | 纯函数，无需 Mock |
| `_infer_causual_chains` | 输入 K8s→DB graph + anomalies → 输出正确的因果链 | 纯函数 |
| `_detect_cross_agent_contradictions` | 输入 K8s conclusion="异常: OOMKilled" + Metrics conclusion="正常: 资源正常" → 输出矛盾条目 | 纯函数 |
| `planner_node` v1 | incident_type="deployment_regression" → 产出 5 个 AgentTask | 无需 Mock |
| `evidence_fanout_node_v2` | 3 个 AgentTask → 并行调用 3 个 SpecialistAgent → 产出 3 个 SpecialistAnalysis | Mock SpecialistAgent（不调 LLM） |

#### 2.8.2 集成测试

| 测试场景 | 输入 | 预期行为 |
|---------|------|---------|
| Happy path | 正常 ticket + mock adapter | 5 个 Agent 全部 COMPLETED，aggregate 产出高质量评分 |
| Partial degradation | 2 个 Agent LLM 超时 + 3 个正常 | aggregate 降权计算，不崩溃，evidence_summary 标注 partial |
| All LLM failed | LLM 全部不可用 | 所有 Agent 走规则兜底，aggregate 产出低质量但结构完整的分析 |
| Contradiction detection | 人工构造 K8s "异常:" + Metrics "正常:" | aggregate 在 contradictions 中列出矛盾条目 |
| No evidence at all | 所有工具调用返回空 | Agent 产出 LLM_FAILED，aggregate quality_score ≈ 0，触发 NEED_MORE_EVIDENCE |
| Checkpoint round-trip | 完整 run 后 resume | specialist_analyses 正确从 checkpoint 反序列化 |

#### 2.8.3 LLM Mock 数据格式

测试中 Mock LLM 响应的最小格式：

```python
# Mock: 第 1 轮 ReAct - LLM 返回 tool_calls
MOCK_REACT_ROUND1 = {
    "tool_calls": [
        {"id": "call_1", "name": "query_k8s_pods", "params": {"service": "test-svc", "env": "staging"}},
        {"id": "call_2", "name": "query_k8s_events", "params": {"service": "test-svc", "limit": 10}},
    ]
}
# Mock: 第 2 轮 ReAct - LLM 无 tool_calls（认为足够）
MOCK_REACT_ROUND2 = {"tool_calls": None}
# Mock: 最终分析 - LLM 返回 JSON
MOCK_FINAL_ANALYSIS = """```json
{
  "conclusion": "异常: Pod test-svc-abc123 处于 CrashLoopBackOff，原因为 OOMKilled",
  "severity": "critical",
  "anomalies": [
    {"signal_type": "OOMKilled", "description": "Pod OOMKilled at restart", "timestamp_hint": "2025-06-03T14:30:00Z"}
  ],
  "correlation_hints": [],
  "execution_summary": "调用了 query_k8s_pods 和 query_k8s_events，共 2 轮",
  "confidence": 0.85
}
```"""
```

#### 2.8.4 测试覆盖目标

- **Agent 函数覆盖率**: ≥ 90%（除 `_get_tool_definitions` 等胶水代码）
- **aggregator 纯函数**: 100%（无外部依赖）
- **降级路径覆盖**: 7 种 run_status 每种至少 1 个测试用例

---


---

## 实施路线

| 步骤 | 内容 | 估时 |
|------|------|------|
| 1.1 | 新增 `SpecialistAgent` 类 + 5 个 Agent 配置 + ReAct 循环 | 2d |
| 1.2 | 新增 `SpecialistAnalysis` 等模型 | 0.5d |
| 1.3 | 重写 `evidence_fanout_node`：用 SpecialistAgent 替换 `_collect_one` | 1.5d |
| 1.4 | 重写 `evidence_aggregate_node`：全局关联分析 + 冲突检测 v2 | 1d |
| 1.5 | 单元测试（mock LLM） + 集成测试（mock adapter） | 1.5d |
| 1.6 | feature flag 接入 + 灰度验证 | 0.5d |

**总计**：约 5-7 人天

---

## 验收标准

### 功能正确性

- [ ] **A1-1**：5 种 Specialist Agent 均可独立完成 ReAct 循环（包括轮次 0 = LLM 决定不需要调工具直接产出结论的场景），产出结构化 `SpecialistAnalysis`（`run_status=COMPLETED`）
- [ ] **A1-2**：`evidence_aggregate_node_v2` 可正确检测跨 Agent 矛盾信号，至少覆盖以下 3 类 case（人工构造 conclusion 前缀输入）：

  - `case_contradiction_1`：K8s Agent conclusion="异常: Pod CrashLoopBackOff"，Log Agent conclusion="正常: 无错误日志" → 应标记 CONTRADICTION

  - `case_contradiction_2`：Metrics Agent conclusion="异常: CPU memory 突增"，K8s Agent conclusion="正常: 所有 Pod 健康" → 应标记 CONTRADICTION

  - `case_contradiction_3`：DB Agent conclusion="异常: 连接池耗尽"，K8s Agent conclusion="正常: 容器运行正常" → 应标记 CONTRADICTION
- [ ] **A1-3**：`evidence_aggregate_node_v2` 可生成全局关联分析，至少覆盖 1 类 case：2+ Agent 的 `correlation_hints` 置信度 ≥ 0.6 形成因果链（如 Deployment→Log→DB 时序链）
- [ ] **A1-4**：`specialist_analyses` 和 `evidence_items` 两套数据同步写入，`diagnose_node` 和 `rca_node` 无需改动即可正常运行

### 降级与容错

- [ ] **A1-5**：LLM 调用超时（模拟 1s 超时），Agent 产出 `SpecialistAnalysis(partial=True)`，不抛异常。若超时时已有 raw data → `run_status=PARTIAL`；无 raw data → `run_status=LLM_FAILED`
- [ ] **A1-6**：LLM 最终分析 JSON 解析失败（模拟返回非法 JSON），Agent 走规则兜底（PARTIAL），confidence=0.25
- [ ] **A1-7**：所有工具调用均返回错误（模拟 adapter 全 fail），Agent 产出 `LLM_FAILED`，confidence=0.0
- [ ] **A1-8**：`evidence_aggregate_v2` 正确处理 partial Agent——降权（confidence×0.5），不因单个 Agent 失败而崩溃

### 性能指标

- [ ] **A1-9**：单 run 的 LLM token 消耗 ≤ 基线的 **3 倍**（≤ 20K tokens）
- [ ] **A1-10**：`asyncio.gather` 并行 5 个 Agent 的端到端 wall-clock 时间 ≤ 单 Agent 最长时间 + 2s
- [ ] **A1-11**：在 mock adapter 环境下，evidence_fanout + evidence_aggregate 总延迟 ≤ 基线的 **1.8 倍**

### 向后兼容

- [ ] **A1-12**：`AGENT_FEATURE_SPECIALIST_POOL=false` 时完整回退到原有 `_collect_one` 逻辑，所有现有集成测试通过
- [ ] **A1-13**：`AGENT_FEATURE_SPECIALIST_POOL=true` 时与后续节点（diagnose/remediation/rca）无缝衔接

### 安全

- [ ] **A1-14**：任一 Agent 的 `tool_names` 被误配为 `execute_action`，Agent 初始化时校验失败，标记为 `enabled=False`，不执行
- [ ] **A1-15**：Agent 跨 category 工具调用被阻断（如 K8s Agent 配置了 `query_db_processlist` → 初始化校验失败）
