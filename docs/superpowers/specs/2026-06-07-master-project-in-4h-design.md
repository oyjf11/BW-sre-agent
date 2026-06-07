# 4 小时吃透 OpsPilot — 面试准备学习方案

> 目标：Agent 应用开发工程师面试，重点维度 A（系统设计）+ B（工程深度），4 小时内能清晰讲解整个系统架构和每个模块的设计决策。

---

## 学习路径（地图优先）

| 阶段 | 时长 | 目标 |
|------|------|------|
| 一、建全局地图 | 0–30 min | 在脑中有完整的系统全景图 |
| 二、节点设计决策 | 30–90 min | 每个节点能说清楚"为什么这么做" |
| 三、工程空白答法 | 90–150 min | 把缺失点转化为"我知道差距在哪、生产怎么做" |
| 四、模拟开场白 | 150–240 min | 能流畅讲出 2-3 分钟的系统介绍 |

---

## 一、系统全景图

### 数据流主干

```
外部输入
  │
  ├─ POST /incidents/runs (ticket / alert_event / ticket_id)
  │
  ▼
[API Layer]  incidents.py
  │  创建 incident_run 记录，BackgroundTask 启动 GraphRunner
  ▼
[GraphRunner]  graph_runner.py
  │  包装执行：emit events、checkpoint、evidence 持久化
  ▼
[LangGraph StateGraph]
  │  IncidentAgentState 贯穿所有节点（TypedDict，内存中流转）
  │
  ▼ node_dispatcher
  │ （路由：新 run → intake；审批恢复 → risk_gate/executor）
  ▼
[node_intake] → [node_triage] → [node_retrieve_memory] → [node_planner]
  │
  ▼
[node_evidence_fanout]  ←─────────────────────────────┐
  asyncio.gather 并行调用所有 plan.tasks               │ NEED_MORE_EVIDENCE
  每个 task → ToolGateway → Adapter → EvidenceItem     │
  v2：SpecialistAgent 并行 ReAct loop                  │
  │                                                     │
  ▼                                                     │
[node_evidence_aggregate]                              │
  汇总 evidence_items，计算 quality_score              │
  │                                                     │
  ▼                                                     │
[node_diagnose]                                        │
  LLM 生成 root_cause_candidates                       │
  │                                                     │
  ▼                                                     │
[node_critic] ────────────────────────────────────────┘
  quality_score < 0.4 → NEED_MORE_EVIDENCE（loop，最多 2 次）
  contradiction       → REPLAN → node_planner
  loop_count >= 2     → NEEDS_HUMAN → node_rca
  else                → PASS
  │
  ▼（PASS）
[node_remediation] → [node_risk_gate]
                          │
         ┌────────────────┼────────────────┐
    BLOCKED           NEEDS_APPROVAL    LOW_ONLY
         │                │                │
       node_rca   node_approval_interrupt  │
                          │（审批后恢复）   │
                          └────────────────┘
                                           ▼
                                    [node_executor]  ←──────────────┐
                                           │                         │ RETRYABLE_FAILURE
                                           ▼                         │ （最多 2 次）
                                  [node_verify_outcome] ─────────────┘
                                           │
                                    SUCCESS / FATAL_FAILURE
                                           ▼
                                       [node_rca]
                                           │
                                          END
```

### 核心依赖关系

```
IncidentAgentState（TypedDict）
  └─ 贯穿所有节点，节点只读写自己关心的字段

LangGraph StateGraph
  └─ 管理节点编排、条件路由、checkpoint

GraphRunner
  ├─ 注入 ContextVar event hook → 节点完成时自动持久化
  ├─ 每次 state 变化 → checkpoint DB
  └─ 收集 evidence_items → EvidenceRepo

Tool Gateway（gateway.py）
  ├─ 统一入口：schema 校验、tenacity 重试、审计写入
  ├─ TOOL_ADAPTER_MODE=mock → mock adapters
  └─ TOOL_ADAPTER_MODE=real → real adapters（MySQL/K8s/SLB/OSS/CMS）

LLM Client（llm_client.py）
  └─ 统一封装：OpenAI / MiniMax / DeepSeek，由 LLM_PROVIDER 切换

RAG（rag/）
  ├─ retrieve_memory_node 调用 retriever → 向量检索 + rerank
  └─ rca_node 完成后 writeback_knowledge 写回新知识

Specialist Pool（graph/nodes/specialist_agent.py）
  └─ evidence_fanout v2：多个 SpecialistAgent 并行 ReAct loop
```

### 三条关键路径

| 路径 | 触发条件 | 关键节点 |
|------|---------|---------|
| 全自动成功 | 低风险动作、高置信 | ...→ risk_gate(LOW_ONLY) → executor → verify(SUCCESS) → rca |
| 人工审批 | 高风险 action 或 P1/P2 | ...→ risk_gate(NEEDS_APPROVAL) → approval_interrupt（暂停）→ 恢复 → executor |
| 证据不足循环 | quality_score < 0.4 | ...→ critic(NEED_MORE_EVIDENCE) → fanout（重跑，最多 2 次）→ ...→ critic(NEEDS_HUMAN) → rca |

---

## 二、每个节点的设计决策

### node_intake — 规范化入口

- **做什么**：对 ticket 字段幂等标准化（env/service/time_range），初始化 state 容器字段。
- **为什么放这里而不在 API 层**：checkpoint 恢复时 API 层已经过了，intake_node 是 graph 内部的第二道保障，保证任何入口进来的数据都是干净的。
- **关键细节**：`evidence_items = []` 在这里强制清空——从 checkpoint 恢复时历史 state 会带回旧数据，必须重置。

### node_triage — 三级分类

- **做什么**：判断 `incident_type`，结果决定 planner 里的工具优先级。
- **三级降级**：规则匹配（快、确定）→ LLM（处理长尾）→ fallback（永不崩溃）。
- **关键决策**：`requires_immediate_human=True` 时不终止流程，打标记继续跑——保证 RCA 报告仍然生成，人工看完整报告而不是空白。

### node_retrieve_memory — RAG 召回

- **做什么**：检索相似历史故障经验，写入 `memory_hits`。
- **为什么放 planner 前**：历史记忆影响"采集什么证据"，越早注入越能减少无效工具调用。
- **关键设计**：不强制依赖，检索为空时 planner 靠规则兜底，不影响主流程。

### node_planner — 调查计划生成

- **做什么**：`incident_type → tools` 映射，生成 `InvestigationPlan`。
- **为什么不用 LLM 自由生成**：工具调用有副作用，LLM 幻觉可能生成不存在的工具名或错误参数；规则可控、可审计。
- **v2 路径**：`agent_feature_specialist_pool=True` 时额外生成 `agent_tasks`，由 evidence_fanout 按 feature flag 选择 v1/v2。

### node_evidence_fanout — 并行取证

- **做什么**：`asyncio.gather` 并行调所有 plan.tasks，成功的转为 EvidenceItem。
- **degrade_on_failure**：单个工具失败不影响其他工具——取证阶段高可用比完整性更重要。
- **v1 vs v2**：v1 直接并行调工具；v2 每个 SpecialistAgent 有独立 ReAct loop，可多轮调用，代价是耗时更长，收益是复杂故障的证据质量更好。

### node_evidence_aggregate — 质量评估

- **做什么**：计算 `quality_score`，识别 `missing_categories` 和 `failed_tools`。
- **quality_score 是 critic 的核心输入**：成功工具数/总任务数加权计算，关键 category 权重更高。
- **矛盾检测**：简单文本匹配 "error" + "healthy" → 标记 `contradiction_signals`，触发 CONTRADICTION 路由。

### node_diagnose — 根因推断

- **做什么**：LLM 分析 evidence 摘要，生成 2-3 个 `RootCauseCandidate`。
- **只传摘要不传原始 payload**：原始数据几十 KB，超 context window 且噪声大；摘要在 evidence_fanout 时由 `classify_result` 生成。
- **fallback**：LLM 失败时硬编码两个通用候选，confidence 较低，会触发 critic 的 NEED_MORE_EVIDENCE。

### node_critic — 质检守门

- **做什么**：4 路路由决定是否接受当前诊断结果。
- **循环守卫是最重要的安全阀**：`loop_count >= max_loop_count(2)` 强制 `NEEDS_HUMAN`，防止无限循环打爆 LLM 费用。
- **CONTRADICTION 路由回 planner**：矛盾意味着调查方向错了，需要重新规划；NEED_MORE_EVIDENCE 路由回 fanout，只是数据不够。

### node_remediation — 修复方案生成

- **做什么**：LLM 生成 `RemediationPlan`，每个 action 带 `risk_level` 和 `requires_approval`。
- **LLM 的风险判断不可完全信任**：risk_gate 会对 action 做二次规则校验兜底。

### node_risk_gate — 风险把关

- **做什么**：多维度判断执行路径，综合 action 风险 + severity + env + 置信度 + capability preflight。
- **capability preflight**：执行前先查 `execute_action` adapter 是否可用——fail-fast 比 fail-late 更友好。
- **BLOCKED vs NEEDS_APPROVAL 分界**：CRITICAL + prod + 置信度 < 0.5 → BLOCKED，不允许审批后强行执行。

### node_approval_interrupt — 人工审批

- **做什么**：写 `incident_approvals` 表，图暂停（LangGraph interrupt）。
- **暂停机制本质**：不是 sleep，是 state checkpoint 到 DB，进程可以退出；审批后 resume API 重建 graph 从 checkpoint 恢复——连接生命周期与任务生命周期分离的实现。
- **4 种决策**：approved / rejected / modify_plan / request_more_evidence。

### node_executor — 幂等执行

- **做什么**：调用 ControlledExecutor 执行 actions，写审计记录。
- **idempotency_key**：唯一标识一次执行意图，DB 查到 `COMPLETED/EXECUTING` 直接跳过返回已有结果——防止模型重试或审批重入时同一操作执行两次。
- **retry 计数跨 checkpoint 持久化**：`retries["executor"]` 存在 state 里，进程重启后仍然有效。

### node_verify_outcome — 效果验证

- **做什么**：重调监控工具对比执行前后指标，3 路路由。
- **不只看 action 返回值**：看业务指标是否恢复——pod restart 了不代表服务恢复了。
- **RETRYABLE_FAILURE**：执行了但效果没出来（如 pod 还没 ready），等一下重试；FATAL_FAILURE：验证工具本身失败，无法判断，走 rca 记录失败。

### node_rca — 根因报告

- **做什么**：综合全链路信息生成 `RcaReport`，所有路径的终点。
- **三种 outcome 分支**：SUCCESS / NEEDS_HUMAN / FAILED 输出完全不同的报告内容。
- **知识闭环**：执行后 writeback_knowledge 把处置经验存回 RAG，下次类似故障能在 retrieve_memory 召回。

---

## 三、工程空白的面试答法

### 1. 任务队列用 BackgroundTasks，无独立 Worker

**现状**：`incidents.py:224` — `background_tasks.add_task(_run_graph_bg, ...)`，同进程异步执行。

**答法**：
> 当前用 FastAPI BackgroundTasks，适合开发环境。生产问题是进程重启时正在执行的任务直接丢失，无重试，无法水平扩展。生产方案：API 只写 PENDING 记录，独立 Worker 用 `FOR UPDATE SKIP LOCKED` 拉任务，配合 `lease_expires_at` 租约，watchdog 超时重分配，任务不丢。

### 2. 没有 lease_expires_at，没有 watchdog

**现状**：`incident_runs` 有 `status` 字段，无租约字段，Worker 崩溃后任务永久卡在 RUNNING。

**答法**：
> 生产上需要两个东西：`lease_expires_at` 字段（Worker 每 N 秒 UPDATE 续租）+ watchdog 定时任务（扫描超时任务重置为 PENDING）。两者配合才能保证 Worker 崩溃后任务被其他 Worker 捡起来。

### 3. 没有乐观锁，状态更新无并发保护

**现状**：`_sync_run_progress` 直接 UPDATE，无 version 字段，多 Worker 并发会发生 Lost Update。

**答法**：
> 单进程暂时没问题。水平扩展后需要乐观锁：`incident_runs` 加 `version` INT 列，UPDATE 时带 `WHERE version = :old_version`，影响行数为 0 说明被抢先更新，重试或报错。

### 4. 没有 Transactional Outbox，事件可能丢失

**现状**：`event_bus.publish()` 和业务状态更新是两次独立操作，进程崩溃可能丢事件。

**答法**：
> 生产上用 Transactional Outbox：把事件和状态更新放在同一个 DB 事务里写 `outbox_events` 表，独立 Publisher 轮询发到 MQ 并标记 `sent=true`。保证"写 DB 必有事件"，进程崩溃也不丢。

### 5. 没有 Redis，没有分布式锁

**现状**：全工程无 Redis，幂等全靠 DB 唯一约束（`idempotency_key`）。

**答法**：
> DB 唯一约束对单实例够用，也是推荐做法（能用 DB 解决的不优先用分布式锁）。Redis 适合做：SSE 心跳状态、限流计数（单用户并发 run 数）、短期缓存（相同 ticket 的 triage 结果）。不适合做唯一权威状态（run status），那个必须在 DB。

### 6. 没有 Semaphore，并发无限制

**现状**：`asyncio.gather` 在 evidence_fanout 里无限并发，`create_run` 接口无 admission control。

**答法**：
> 生产上需要两层控制：API 层 `asyncio.Semaphore` 限制同时 RUNNING 的 run 数；fanout 内部 Semaphore 限制单个 run 的并发工具调用数（比如最多 5 个），防止打爆 LLM 和 K8s API。

### 7. 模型超时没有强制 enforcement

**现状**：`config.py` 声明了 `llm_timeout=60`，但 `llm_client.py` 的 aiohttp 调用未实际设置 timeout 参数。

**答法**：
> 生产上需要四层超时分开设：连接超时 5s、首 Token 超时 30s（流式）、总请求超时按任务类型区分、流式空闲超时 30s（防止模型卡住不吐）。用 `asyncio.wait_for` 包裹调用来强制执行。

### 8. 没有 dry_run，没有容器沙箱

**现状**：`execute_action` 在 real 模式下 fail-closed，是 fail-safe 设计，不是真正的 dry_run。

**答法**：
> 真正的 dry_run 是 action 执行前返回"会做什么"而不是真做，人确认后再提交。代码沙箱方面，生产上执行 shell/Python 的 Worker 要和 API 服务强隔离，用 K8s Job + gVisor，不能在同一个 Pod——当前全是 mock，这个隔离还没有建立。

---

## 四、面试开场白模板（2-3 分钟）

> "OpsPilot 是一个 SRE 故障自动处置 Agent。核心是一条 13 节点的 LangGraph 工作流：告警进来后，先做三级 triage（规则→LLM→fallback），再由 planner 根据故障类型生成调查计划，evidence_fanout 并行调所有工具取证，critic 做质量把关（最多循环 2 轮），diagnose 生成根因候选，最后 risk_gate 决定是直接执行还是走人工审批，verify 验证效果，rca 输出完整报告。
>
> 工程上有几个设计亮点：Tool Gateway 统一了所有工具的入口，带 schema 校验、重试和审计；ControlledExecutor 用 idempotency_key 防止 action 重复执行；LangGraph 的 interrupt 机制让审批暂停后可以从 checkpoint 精确恢复，连接生命周期和任务生命周期完全解耦。
>
> 当前是 MVP 阶段，还有几个生产级差距：任务队列用的是 BackgroundTasks 而不是独立 Worker，没有 lease 机制，并发控制还不完善——这些我清楚知道怎么做，是下一步的重点。"

---

## 阅读顺序速查

| 顺序 | 文件 | 目的 |
|------|------|------|
| 1 | `CLAUDE.md` | 项目全局约定 |
| 2 | `backend/app/graph/builder.py` | 节点和边的完整结构 |
| 3 | `backend/app/graph/state.py` | State 所有字段 |
| 4 | `backend/app/graph/nodes/__init__.py` | 每个节点实现（重点看 intake/triage/planner/critic/risk_gate/executor） |
| 5 | `backend/app/services/graph_runner.py` | GraphRunner 包装层 |
| 6 | `backend/app/tools/gateway.py` | Tool Gateway 统一入口 |
| 7 | `backend/app/services/executor.py` | ControlledExecutor 幂等执行 |
| 8 | `backend/app/llm_client.py` | LLM 多模型封装 |
| 9 | `backend/app/rag/retriever.py` | RAG 检索逻辑 |
| 10 | `backend/app/api/incidents.py` | API 层，BackgroundTasks 入口 |
