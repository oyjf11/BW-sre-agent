# OpsPilot Agent 技术文档（TDD）

版本: v1.0  
范围: MVP + P1 技术方案（含阿里云平台接入补充）  
目标: 指导实现、支持面试讲解、支持后续迭代

---

## 1. 文档目标

本文档定义 OpsPilot Agent（生产级运维工单排障与修复智能体）的技术架构、状态模型、LangGraph 编排、工具契约、审批机制、阿里云平台集成、可观测与评测方案，用于指导 MVP 与 P1 实现。

**关键目标特性**
- 状态化编排（LangGraph）
- 可中断/可恢复（checkpoint + HITL）
- 多工具编排（日志、指标、发布、Runbook、执行动作）
- 风险分级 + 审批门禁
- 可观测（trace / latency / cost / failure taxonomy）
- 可评测（离线回放 + 在线指标）
- 真实平台集成（MySQL / K8s / SLB / OSS）

---

## 2. 技术目标与约束

### 2.1 技术目标
1. **可控性**: 避免自由 ReAct 失控循环，采用显式图编排 + 条件路由
2. **可恢复性**: 支持节点失败重试、审批挂起恢复、系统重启后续跑
3. **安全性**: 执行类动作必须经过风险分级与审批
4. **可观测性**: 能定位错误发生在模型、工具、流程还是数据层
5. **可演示性**: 2-3 周内完成面试级 MVP，后续可平滑升级到 P1

### 2.2 范围约束（MVP）
- 工具层先使用 mock adapters + 可选真实只读适配器
- 执行类工具默认 mock，不直接操作生产环境
- 多 Agent 先做“逻辑角色拆分”，不强依赖多进程
- 前端允许简化为单页 + tabs

---

## 3. 总体架构

### 3.1 分层架构

#### A. Presentation Layer（前端 / API）
- 工单输入页
- 执行态页面（实时进展）
- 审批页面
- RCA 报告页面
- FastAPI 提供 REST / SSE 接口

#### B. Orchestration Layer（LangGraph）
- Incident State 状态机
- 节点编排（triage / plan / evidence / diagnose / critic / remediation / approval / execute / verify / rca）
- 条件路由与错误分支
- checkpoint 持久化
- interrupt / resume（HITL）

#### C. Tool Adapter Layer
- Logs Adapter
- Metrics Adapter
- Deployment Adapter
- Runbook / RAG Adapter
- Action Executor Adapter
- Aliyun Adapters（MySQL / K8s / SLB / OSS）
- 统一 schema、超时、重试、权限控制、审计

#### D. Persistence & Observability Layer
- DB（SQLite / Postgres）
- LangGraph Checkpoint Store
- 业务数据表（runs/evidence/approvals/actions/reports）
- Tracing（LangSmith / Langfuse）
- Metrics（可选 Prometheus）

#### E. Knowledge / RAG Layer（P1）
- 向量存储（pgvector / Chroma）
- 文档切分与 metadata 索引
- 检索 + 压缩 + 注入
- RCA 写回（人工确认后）

---

## 4. 核心模块设计

### 4.1 Orchestrator（LangGraph 编排核心）
**职责**
- 驱动 LangGraph 执行
- 控制状态迁移
- 管理 step limit / timeout / retry / fallback
- 管理 interrupt/resume（审批）
- 向前端输出运行事件流（RunEvent）

**设计要点**
- 图编排优先于自由 loop
- 每节点输入输出结构化
- 显式失败分支，避免异常直接中断用户体验

### 4.2 Agent Roles（逻辑角色）

#### Planner Agent
- 输入: ticket + triage + retrieved memory
- 输出: `InvestigationPlan`

#### Investigator Agent
- 执行证据采集步骤
- 聚合工具结果为 `EvidenceItem[]`

#### Critic Agent
- 校验证据与结论一致性
- 决定补证据 / 降低置信度 / 通过

#### Executor Agent
- 将修复方案转为动作
- 触发审批（如需）
- 执行、验证、记录审计

> 角色可先用不同节点 + prompt/策略实现，不必立即多模型化。

### 4.3 Internal Tool Gateway（内部工具网关）
**职责**
- 参数校验（Pydantic/JSON Schema）
- timeout / retry / backoff
- 风险等级与审批要求判定
- 审计日志记录
- 响应标准化封装
- 环境隔离与白名单检查

**原则**
- 模型不能直接执行 shell / kubectl 命令
- 执行动作必须通过受控 Action API/Adapter
- LLM 不可见云凭证或数据库密码

### 4.4 Approval Service（审批服务）
**职责**
- 创建审批请求
- 管理审批状态（pending/approved/rejected/modified/request_more_evidence）
- 提供审批 API
- 审批完成后触发/允许 graph resume

### 4.5 Evaluation Service（P1）
**职责**
- 回放模拟事故案例
- 统计命中率/延迟/成本/漏审批率
- 输出版本对比报告

---

## 5. 数据模型与状态模型

### 5.1 领域模型（TypeScript 表达，便于前后端对齐）

#### IncidentTicket
```ts
export type IncidentTicket = {
  ticket_id: string
  title?: string
  description: string
  service?: string
  env?: "dev" | "staging" | "prod"
  severity?: "P1" | "P2" | "P3"
  time_range?: { start: string; end: string }
  source?: "manual" | "alert" | "ticket_system"
  metadata?: Record<string, any>
}
```

#### TriageResult
```ts
export type TriageResult = {
  incident_type:
    | "ERROR_RATE_SPIKE"
    | "LATENCY_REGRESSION"
    | "RESOURCE_SATURATION"
    | "DEPENDENCY_FAILURE"
    | "DEPLOYMENT_REGRESSION"
    | "UNKNOWN"
  severity: "P1" | "P2" | "P3"
  suspected_services: string[]
  suggested_time_window?: { start: string; end: string }
  requires_immediate_human: boolean
  rationale: string
}
```

#### EvidenceItem
```ts
export type EvidenceItem = {
  evidence_id: string
  tool_name: string
  category: "logs" | "metrics" | "deployments" | "runbook" | "history" | "verification"
  source_ref?: string
  source_timestamp?: string
  summary: string
  raw_payload: any
  confidence?: number
  freshness_score?: number
  completeness_score?: number
}
```

#### RootCauseCandidate
```ts
export type RootCauseCandidate = {
  candidate_id: string
  hypothesis: string
  confidence: number
  supporting_evidence_ids: string[]
  contradicting_evidence_ids: string[]
  next_checks?: string[]
}
```

#### ActionSpec / RemediationPlan
```ts
export type ActionSpec = {
  action_type:
    | "RESTART_SERVICE"
    | "ROLLBACK_DEPLOYMENT"
    | "UPDATE_CONFIG"
    | "SCALE_SERVICE"
    | "RUN_HEALTHCHECK"
  service: string
  env: "dev" | "staging" | "prod"
  params: Record<string, any>
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  requires_approval: boolean
  idempotency_key?: string
}

export type RemediationPlan = {
  summary: string
  actions: ActionSpec[]
  expected_outcome: string
  rollback_plan?: string
  risk_notes?: string[]
}
```

---

### 5.2 LangGraph State（Python / Pydantic 建议实现）

```python
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

RunStatus = Literal[
    "NEW",
    "TRIAGED",
    "PLANNED",
    "GATHERING_EVIDENCE",
    "DIAGNOSED",
    "PENDING_APPROVAL",
    "WAITING_HUMAN",
    "EXECUTING",
    "VERIFYING",
    "COMPLETED",
    "FAILED",
]

class AgentError(BaseModel):
    code: str
    message: str
    node_name: Optional[str] = None
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None

class IncidentAgentState(BaseModel):
    # identity
    run_id: str
    thread_id: str
    schema_version: int = 1

    # input
    ticket: Dict[str, Any]
    user_context: Dict[str, Any] = Field(default_factory=dict)

    # planning
    triage: Optional[Dict[str, Any]] = None
    plan: Optional[Dict[str, Any]] = None

    # evidence & diagnosis
    evidence_items: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_summary: Optional[str] = None
    root_cause_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    remediation_plan: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None

    # approval & execution
    pending_approval: Optional[Dict[str, Any]] = None
    approval_result: Optional[Dict[str, Any]] = None
    execution_results: List[Dict[str, Any]] = Field(default_factory=list)

    # runtime control
    status: RunStatus = "NEW"
    retries: Dict[str, int] = Field(default_factory=dict)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    step_count: int = 0

    # output
    rca_report: Optional[Dict[str, Any]] = None
```

### 5.3 状态设计规范
1. 所有字段可序列化、可恢复（禁止连接句柄/对象实例）
2. 副作用结果（执行回执）独立记录，不混入 messages 文本
3. `pending_approval` 与 `approval_result` 分离建模
4. 错误结构化，便于归因与评测
5. 使用 `schema_version` 支持后续状态演进兼容

---

## 6. LangGraph 图设计

### 6.1 主图节点列表
1. `intake_node`
2. `triage_node`
3. `retrieve_memory_node`（P1，可选）
4. `planner_node`
5. `evidence_fanout_node`
6. `logs_node`
7. `metrics_node`
8. `deployments_node`
9. `runbook_node`
10. `evidence_aggregate_node`
11. `diagnose_node`
12. `critic_node`
13. `remediation_node`
14. `risk_gate_node`
15. `approval_interrupt_node`
16. `executor_node`
17. `verify_outcome_node`
18. `rca_node`
19. `writeback_knowledge_node`（P1）
20. `end_node`

### 6.2 条件路由规则

#### `critic_node`
- `PASS` -> `remediation_node`
- `NEED_MORE_EVIDENCE` -> `evidence_fanout_node`
- `CONTRADICTION` -> `diagnose_node` 或 `planner_node`

#### `risk_gate_node`
- `LOW_ONLY` -> `executor_node`
- `NEEDS_APPROVAL` -> `approval_interrupt_node`

#### `verify_outcome_node`
- `SUCCESS` -> `rca_node`
- `RETRYABLE_FAILURE` -> `executor_node`（受 retry 限制）
- `FATAL_FAILURE` -> `rca_node`（失败 RCA）

### 6.3 防失控策略（非常重要）
- `step_count` 每节点 +1
- `MAX_STEPS`（建议 30）超限 -> fail-safe（转人工/终止）
- 节点级 timeout 与 retry 限制
- 补证据回环次数限制（建议 1-2 次）
- 节点执行记录完整 trace，便于回放和定位循环

---

## 7. 节点实现规范（Node Contract）

### 7.1 节点签名（示意）
```python
def node_fn(state: IncidentAgentState, config: dict) -> dict:
    """
    Return partial state update dict.
    Side effects only via Tool Gateway / services.
    """
```

### 7.2 节点实现原则
1. 返回增量状态更新（partial state）
2. 不直接修改外部全局状态
3. 工具调用统一经 Tool Gateway
4. 异常转结构化 `AgentError`
5. 优先结构化输出，减少自由文本依赖
6. 记录关键决策依据（evidence refs / rationale）

---

## 8. Tool Gateway 技术设计

### 8.1 标准 ToolRequest / ToolResponse

```python
from pydantic import BaseModel, Field
from typing import Optional

class ToolRequest(BaseModel):
    tool_name: str
    params: dict
    run_id: str
    node_name: str
    timeout_ms: int = 5000
    retry_policy: dict = Field(default_factory=dict)
    idempotency_key: Optional[str] = None

class ToolResponse(BaseModel):
    ok: bool
    tool_name: str
    request_id: str
    data: Optional[dict] = None
    error: Optional[dict] = None
    latency_ms: int
    source_timestamp: Optional[str] = None
```

### 8.2 Tool Registry（通用）
每个工具注册项建议包含:
- 参数 schema
- 风险等级
- 是否需要审批
- 默认 timeout
- 默认 retry
- 允许环境
- 响应大小限制（可选）

示例:
```python
TOOL_REGISTRY = {
    "query_logs": {
        "risk_level": "LOW",
        "requires_approval": False,
        "timeout_ms": 4000,
        "retries": 1,
    },
    "rollback_deployment": {
        "risk_level": "HIGH",
        "requires_approval": True,
        "timeout_ms": 10000,
        "retries": 0,
    },
}
```

### 8.3 幂等与副作用控制
执行类工具必须具备:
- `idempotency_key`
- 审计落库（action 表）
- 重试前查历史执行记录，避免重复动作

---

## 9. 人工审批（HITL）技术实现

### 9.1 审批触发条件
满足任一条件进入审批:
- `risk_level >= MEDIUM`（可按策略调整）
- 目标环境为 `prod`
- 涉及重启/回滚/改配置/批量操作
- 模型置信度低但仍建议执行

### 9.2 审批请求对象（示意）
```json
{
  "approval_id": "appr_001",
  "run_id": "run_123",
  "action": {
    "type": "rollback_deployment",
    "service": "payment-service",
    "target_version": "v2026.03.02-1",
    "env": "prod"
  },
  "reason": "发布后5xx激增，证据表明连接池配置异常来自最新版本",
  "risk_level": "HIGH",
  "evidence_refs": ["ev_12", "ev_18", "ev_21"],
  "expected_impact": "5xx率应在5分钟内下降",
  "rollback_plan": "若失败，恢复至当前版本并切换流量"
}
```

### 9.3 审批节点流程
在 `approval_interrupt_node` 中:
1. 构造 `ApprovalRequest`
2. 写入 `incident_approvals`
3. 更新 state `pending_approval`
4. checkpoint
5. interrupt（状态 `WAITING_HUMAN`）

### 9.4 Resume 机制
审批 API 写入 `approval_result` 后，调用 graph resume 恢复执行。

---

## 10. 持久化设计

### 10.1 数据库选型
- MVP: SQLite（简单易部署）
- P1: Postgres（更适合并发与查询，方便接 pgvector）

### 10.2 关键表设计（简版）

#### `incident_runs`
- run_id / thread_id / status / severity / service / env
- created_at / updated_at / completed_at
- started_by

#### `incident_checkpoints`
- checkpoint_id / run_id / node_name / state_json / created_at

#### `incident_evidence`
- evidence_id / run_id / tool_name / source_type / source_ref
- summary / raw_payload_json / created_at

#### `incident_approvals`
- approval_id / run_id / action_json / risk_level
- status / approver / comment / created_at / updated_at

#### `incident_actions`
- action_id / run_id / idempotency_key / action_type
- params_json / execution_status / result_json / created_at

#### `incident_rca_reports`
- run_id / report_markdown / root_cause / resolution
- prevention_items_json / confirmed_by_human

### 10.3 Checkpoint 策略
- 每节点完成后 checkpoint（默认）
- interrupt 前强制 checkpoint
- 执行类动作前后强制 checkpoint

---

## 11. RAG 技术设计（P1）

### 11.1 知识源类型
- Runbook / SOP
- 历史事故 RCA
- FAQ
- 服务说明与依赖信息（service notes）

### 11.2 Metadata 建议字段
- `service`
- `team`
- `env`
- `doc_type`
- `severity`（事故类）
- `updated_at`
- `validated`（是否人工确认）

### 11.3 检索流程
1. 构造 query（service + symptom + incident_type + error keywords）
2. metadata filter（service/env/doc_type）
3. top-k 召回
4. rerank / LLM 压缩
5. 以 `EvidenceItem(category=runbook/history)` 注入 state

### 11.4 防污染机制
- 仅写入人工确认 RCA（`validated=true`）
- 未确认推断仅作为运行日志，不入知识库

---

## 12. 可观测性与日志设计

### 12.1 Trace（推荐 LangSmith / Langfuse）
按 run 追踪:
- node start/end
- llm invocation
- tool invocation
- routing decisions
- interrupt/resume events

### 12.2 Metrics（最少这些）
- `run_total_count`
- `run_success_count`
- `run_failure_count`
- `run_duration_ms`
- `node_duration_ms{node_name}`
- `tool_call_count{tool_name}`
- `tool_success_rate{tool_name}`
- `approval_wait_duration_ms`
- `llm_token_total`
- `llm_cost_total`

### 12.3 Failure Taxonomy（枚举化）
- `MODEL_REASONING_ERROR`
- `TOOL_SCHEMA_ERROR`
- `TOOL_TIMEOUT`
- `TOOL_UPSTREAM_5XX`
- `INSUFFICIENT_EVIDENCE`
- `APPROVAL_REJECTED`
- `EXECUTION_FAILED`
- `STATE_RECOVERY_FAILED`

### 12.4 前端实时事件模型（RunEvent）
```ts
export type RunEvent = {
  ts: string
  run_id: string
  level: "INFO" | "WARN" | "ERROR"
  type:
    | "NODE_STARTED"
    | "NODE_COMPLETED"
    | "TOOL_CALLED"
    | "TOOL_RETURNED"
    | "ROUTE_DECISION"
    | "APPROVAL_REQUIRED"
    | "APPROVAL_RECEIVED"
    | "EXECUTION_DONE"
    | "RUN_COMPLETED"
    | "RUN_FAILED"
  node_name?: string
  message: string
  data?: Record<string, any>
}
```

---

## 13. 错误处理与恢复策略

### 13.1 分层错误处理

#### A. 节点内部错误
- 捕获异常 -> 转 `AgentError`
- 根据 retry policy 重试/降级/失败

#### B. 工具层错误
- schema 错误: 通常不可重试，直接 fail node
- timeout/5xx: 有限重试 + backoff
- 权限错误: 记录并转人工

#### C. 执行层错误（副作用动作）
- 落审计
- 标记 `EXECUTION_FAILED`
- 生成补偿/回滚建议
- 进入 verify/rca 失败分支

### 13.2 恢复策略
- 审批挂起恢复
- 系统重启后按 `run_id + checkpoint` 恢复
- P1 可支持从指定 checkpoint 重放（debug/replay）

---

## 14. 安全设计（通用）

### 14.1 工具执行安全边界
- 禁止模型直接执行任意命令
- 仅允许注册表中的动作类型
- 参数白名单（service/env/action fields）
- prod 动作强制审批
- 后续支持双人审批（P2）

### 14.2 Prompt / Tool Injection 基础防护
- 工具输出视为数据，不视为系统指令
- 系统 prompt 明确工具返回可能含恶意文本，不得覆盖策略
- 所有执行动作再次经过 `risk_gate_node`

### 14.3 审计要求
记录:
- 谁审批
- 执行了什么
- 参数是什么（脱敏）
- 何时执行
- 结果如何

---

## 15. API 设计（FastAPI）

### 15.1 运行类 API
- `POST /incidents/runs`：创建并启动 run
- `GET /incidents/runs/{run_id}`：查询运行状态
- `GET /incidents/runs/{run_id}/events`：拉取事件流（或 SSE）
- `GET /incidents/runs/{run_id}/rca`：获取 RCA 报告

### 15.2 审批类 API
- `GET /approvals/pending`
- `GET /approvals/{approval_id}`
- `POST /approvals/{approval_id}/decision`
  - body: `{ decision, comment, modified_action? }`

### 15.3 评测类 API（P1）
- `POST /evals/replay`
- `GET /evals/reports/{report_id}`

---

## 16. 前端技术实现建议（最小可用）

### 16.1 页面路由
- `/runs/new`：创建工单
- `/runs/:id`：执行态页面
- `/approvals`：审批列表
- `/approvals/:id`：审批详情
- `/runs/:id/rca`：RCA 报告页

### 16.2 执行态页面关键组件
- 状态 Stepper（triage/planning/gathering/approval/executing/rca）
- 事件流面板（RunEvent）
- 证据面板（按 category 分组）
- 根因候选 / 修复建议卡片
- 审批状态卡片（等待审批时突出显示）

---

## 17. 项目目录结构（建议）

### 17.1 后端（Python）
```text
ops-pilot/
  backend/
    app/
      api/
        routes_runs.py
        routes_approvals.py
        routes_evals.py
      core/
        config.py
        logging.py
        errors.py
      graph/
        state.py
        graph_builder.py
        routing.py
        nodes/
          intake.py
          triage.py
          retrieve_memory.py
          planner.py
          evidence_fanout.py
          logs_node.py
          metrics_node.py
          deployments_node.py
          runbook_node.py
          evidence_aggregate.py
          diagnose.py
          critic.py
          remediation.py
          risk_gate.py
          approval_interrupt.py
          executor.py
          verify_outcome.py
          rca.py
          writeback_knowledge.py
      tools/
        registry.py
        gateway.py
        schemas.py
        adapters/
          logs_mock.py
          metrics_mock.py
          deployments_mock.py
          runbook_mock.py
          action_executor_mock.py
          mysql_adapter.py
          k8s_adapter.py
          slb_adapter.py
          oss_adapter.py
        policies/
          env_policy.py
          whitelist_policy.py
          risk_policy.py
        normalizers/
          service_identity.py
          timestamps.py
        clients/
          mysql_client.py
          k8s_client.py
          slb_client.py
          oss_client.py
      services/
        approval_service.py
        run_service.py
        event_stream_service.py
        checkpoint_service.py
        eval_service.py
      repositories/
        runs_repo.py
        evidence_repo.py
        approvals_repo.py
        actions_repo.py
        rca_repo.py
      models/
        db_models.py
        domain_models.py
      rag/
        indexer.py
        retriever.py
        writer.py
      evals/
        datasets/
        replay_runner.py
        metrics.py
      main.py
    tests/
      unit/
      integration/
      fixtures/
```

### 17.2 前端（React）
```text
frontend/
  src/
    pages/
      RunCreatePage.tsx
      RunDetailPage.tsx
      ApprovalsPage.tsx
      ApprovalDetailPage.tsx
      RcaPage.tsx
    components/
      RunStepper.tsx
      EventTimeline.tsx
      EvidencePanel.tsx
      DiagnosisCard.tsx
      RemediationCard.tsx
      ApprovalCard.tsx
      RcaViewer.tsx
    services/
      api.ts
      runs.ts
      approvals.ts
    types/
      run.ts
      approval.ts
      event.ts
```

---

## 18. 阿里云平台接入技术设计（补充整合版）

### 18.1 接入目标
将现有阿里云运维平台（MySQL / K8s / 负载均衡 / OSS）接入为:
- 工单与告警数据源
- 排障证据数据源
- RCA/证据包归档目标
- （后续）受控执行动作目标

### 18.2 核心原则
1. LLM 不直接接触基础设施凭证
2. 所有平台能力通过 `Internal Tool Gateway` 暴露
3. 先只读，后执行；先低风险，后高风险
4. `env` 必须显式（dev/staging/prod）
5. service/namespace/bucket prefix 白名单
6. 工具参数、响应结构化且可审计

### 18.3 平台资源映射

| 资源 | 角色 | 用途 | 风险 | MVP |
|---|---|---|---|---|
| MySQL | 工单/告警/变更结构化数据源 | ticket/alerts/deploy metadata | LOW（只读） | ✅ |
| Kubernetes | 核心排障证据源 | pods/deploy/events/logs summary | LOW-MEDIUM（只读） | ✅ |
| SLB/ALB | 入口层流量与健康证据源 | 5xx、QPS、健康状态、延迟 | LOW | ✅ |
| OSS | 日志归档/报告归档 | 读归档日志、写 RCA/evidence bundle | LOW/MEDIUM | ✅ |
| 受控动作 API | 执行目标 | 重启/回滚/扩容等 | HIGH | P1/P2 |

### 18.4 Aliyun 工具清单（建议）

#### MySQL（只读）
- `query_ticket_by_id`
- `query_alerts_by_service`
- `query_recent_deploy_records`
- `query_service_metadata`

#### Kubernetes（只读）
- `query_k8s_pods`
- `query_k8s_events`
- `query_k8s_deployment_status`
- `query_k8s_pod_logs_summary`

#### 负载均衡（只读）
- `query_lb_health_status`
- `query_lb_traffic_metrics`

#### OSS（读/写归档）
- `read_oss_log_object`
- `write_rca_report_to_oss`
- `write_evidence_bundle_to_oss`

### 18.5 Aliyun Tool Registry 扩展示例
```python
ALIYUN_TOOL_REGISTRY = {
    "query_ticket_by_id": {
        "risk_level": "LOW",
        "requires_approval": False,
        "allowed_envs": ["dev", "staging", "prod"],
        "timeout_ms": 3000,
        "retries": 1,
    },
    "query_k8s_pod_logs_summary": {
        "risk_level": "LOW",
        "requires_approval": False,
        "allowed_envs": ["dev", "staging", "prod"],
        "timeout_ms": 6000,
        "retries": 1,
        "response_size_limit_kb": 128,
    },
    "write_rca_report_to_oss": {
        "risk_level": "MEDIUM",
        "requires_approval": False,
        "allowed_envs": ["dev", "staging", "prod"],
        "timeout_ms": 5000,
        "retries": 1,
        "allowed_bucket_prefixes": ["rca/", "evidence/"],
    },
    "restart_k8s_deployment": {
        "risk_level": "HIGH",
        "requires_approval": True,
        "allowed_envs": ["dev", "staging"],
        "timeout_ms": 10000,
        "retries": 0,
    },
}
```

### 18.6 凭证与权限设计（Aliyun 集成）
- 云凭证/DB 密码仅保存在后端 Tool Gateway
- 前端只调你的 API，不直连云资源
- 按环境拆分凭证（dev/staging/prod）
- 最小权限原则（只读凭证优先）
- 所有工具请求必须带 `env`
- 白名单限制 namespace/service/bucket prefix

### 18.7 数据规范化层（Normalization Layer）
真实平台常见问题:
- 工单 service 名 != K8s deployment 名
- namespace 命名不一致
- 时间戳格式不统一
- LB 后端实例与服务映射复杂

建议通过 `service_registry`（MySQL）统一映射:
- service_name
- env
- namespace
- deployment_name
- lb_id
- owner_team
- log_source_type
- aliases

Agent 在 `triage/planner` 后优先调用 `query_service_metadata` 再 fanout 查询。

### 18.8 集成到 LangGraph 的节点改造点
- `intake_node`: 支持 ticket_id -> `query_ticket_by_id`
- `triage/planner`: 增加 `query_service_metadata` / `query_recent_deploy_records`
- `evidence_fanout`: 根据 metadata 动态选择 K8s/LB/OSS 分支
- `verify_outcome_node`: 用真实只读工具验证修复效果（K8s/LB）
- `rca_node`: 可调用 `write_rca_report_to_oss` 归档产物

### 18.9 MVP 接入顺序（强建议）
**Phase A（1-3 天）**
- MySQL: `query_service_metadata`, `query_recent_deploy_records`,（可选）`query_ticket_by_id`

**Phase B（2-4 天）**
- K8s: `query_k8s_pods`, `query_k8s_events`, `query_k8s_deployment_status`

**Phase C（1-2 天）**
- LB: `query_lb_health_status` 或 `query_lb_traffic_metrics`

**Phase D（1 天）**
- OSS: `write_rca_report_to_oss`, `write_evidence_bundle_to_oss`

**Phase E（P1）**
- 受控执行动作 API（非 prod 优先，审批+幂等+审计）

### 18.10 阿里云集成错误处理与降级策略
- MySQL 不可用 -> 回退手工工单模式，标记结构化上下文缺失
- K8s 不可用 -> 用 MySQL + LB + Runbook 继续，降低置信度
- LB 不可用 -> 用 K8s + logs 继续，标记入口层证据缺失
- OSS 归档失败 -> 先落 DB / 本地，不阻塞 RCA 主流程

---

## 19. 测试策略（必须有）

### 19.1 单元测试
- 节点函数测试（state -> partial state）
- tool schema 校验测试
- risk gate 路由测试
- approval decision 处理测试
- normalizer / policy 测试（Aliyun 集成）

### 19.2 集成测试
- 全链路 mock tools 运行
- 审批中断 + 恢复链路
- 执行失败 -> 失败 RCA 分支
- 证据不足回环后成功
- 真实只读 Aliyun adapter smoke test（隔离环境）

### 19.3 回归评测（P1）
固定 10-20 个案例回放，输出:
- 根因 Top1/Top3 命中率
- 风险判断准确率
- 漏审批率 / 过度审批率
- 平均步骤数
- 平均耗时 / 成本

---

## 20. 性能、成本与扩展性

### 20.1 性能优化
- 证据节点并行化（logs/metrics/deployments/runbook）
- 首次反馈流式化（先 triage + plan，再持续补证据）
- 工具层裁剪（日志摘要、事件聚合、时序降采样）

### 20.2 成本优化
- triage / critic / summarize 使用低成本模型（P1）
- diagnose 使用高质量模型
- 工具结果结构化压缩后再注入上下文
- 同 run 内工具结果缓存（params hash）

### 20.3 扩展性设计
- Tool Gateway 插件化（可替换真实平台适配器）
- Graph 节点可替换（更强 critic / policy engine）
- 未来支持多租户隔离（沿用你现有平台能力）

---

## 21. 开发里程碑（技术实现视角）

### Milestone 1：骨架跑通（3-5 天）
- [ ] `state.py` 与 domain models
- [ ] `graph_builder.py` + 基础节点与路由
- [ ] mock tools + gateway
- [ ] run API + 状态查询 API

### Milestone 2：生产味道（5-7 天）
- [ ] risk gate + approval interrupt/resume
- [ ] checkpoint 持久化
- [ ] execution audit + idempotency
- [ ] trace 接入
- [ ] RCA 报告生成与存储

### Milestone 3：阿里云只读接入（3-7 天）
- [ ] mysql_adapter（service metadata / deploy records / ticket）
- [ ] k8s_adapter（pods / events / deployment status）
- [ ] slb_adapter（health / metrics）
- [ ] oss_adapter（report/evidence write）
- [ ] whitelist / env policy / normalizer

### Milestone 4：上一个台阶（P1，5-7 天）
- [ ] critic 回环
- [ ] RAG 检索与写回（validated only）
- [ ] replay eval runner
- [ ] demo cases + README + 架构图

---

## 22. 面试讲解重点（技术版模板）

### 22.1 为什么选 LangGraph
因为这是一个状态化、可中断、可恢复、需要条件路由和并行分支的工作流，不适合仅靠自由循环的 chat agent。

### 22.2 如何保证可靠性
通过显式图编排、step limit、retry、critic 回环、risk gate、审批中断恢复来提升可控性，而不是只靠 prompt。

### 22.3 如何处理高风险动作
风险分级 + 审批 + 幂等 key + 审计日志；初期只读接入真实平台，执行动作走 mock 或受控 API。

### 22.4 如何做可观测与评测
节点/工具 trace、失败分类、成本归因、离线回放评测集，能知道问题在模型、工具还是流程。

### 22.5 如何避免 toy demo
先用 mock tools 跑通主链路，再分阶段替换为真实阿里云只读数据源（MySQL/K8s/SLB/OSS），保留安全边界和可审计性。

---

## 23. 后续可直接开工的实现建议
优先顺序:
1. `backend/app/graph/state.py` 与 domain models（先把骨架定死）
2. `graph_builder.py` + 节点路由伪代码（主链路跑通）
3. `tools/schemas.py` + `gateway.py`（统一工具契约）
4. `mysql_adapter.py` + `k8s_adapter.py`（先只读高价值数据源）
5. 审批 interrupt/resume 与 action audit

---

## 24. 结论

OpsPilot Agent 的技术方案重点不是“让模型回答问题”，而是把一个非确定性的多步智能体系统做成:
- 可控（图编排、步数限制、风险门禁）
- 可恢复（checkpoint、审批中断恢复）
- 可观测（trace、失败分类、成本归因）
- 可评测（离线回放、在线指标）
- 可落地（真实阿里云运维平台只读接入）

这套方案既适合面试展示，也具备继续演进为真实生产系统的架构基础。
