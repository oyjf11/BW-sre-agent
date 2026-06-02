# OpsPilot 故障处置可靠性闭环设计

## 目标

在 Phase 8 离线评测前，修复真实适配器模式下暴露出的可靠性缺口，确保 OpsPilot
不会把弱证据当作有效诊断依据，不会创建注定失败的审批，不会把自动化能力缺失
误报为业务执行失败，也不会在 RCA 中把候选假设表述为已确认根因。

本轮保留现有 LangGraph 节点和主流程，不接入真实 `execute_action` 实现。真实执行
能力继续 fail-closed，但必须在审批前被识别并转为人工接管。

## 问题样本

样本 run：

```text
878ae18a-25c0-49ed-9f96-7f16150ddf64
```

该 run 的实际流程为：

```text
创建工单
  -> 三轮证据采集
  -> 缺少 deployments / runbook，达到循环上限
  -> critic 强制 PASS
  -> 默认生成 restart api/prod
  -> 创建审批
  -> 人工批准
  -> execute_action 真实适配器未接入
  -> 动作失败
  -> RCA 将未证实假设表述为根因
```

已确认的具体问题：

- 空日志和空指标被当作高置信度证据。
- K8s 配置无效、MySQL 查询断连、`query_runbook` 未接入等采集失败被静默丢弃。
- 重复采集相同空指标仍累积证据条数。
- critic 达到循环上限后强制 `PASS`，混淆“允许转人工”和“允许自动执行”。
- remediation 在没有有效证据引用时仍默认生成 `restart`。
- `execute_action` 未接入，但审批前没有 capability preflight。
- 审批恢复读取旧的 `node_risk_gate` checkpoint，导致 `step_count` 从 19 回退到 18。
- `WAITING_HUMAN` 暂停被 GraphRunner 记录为完成。
- Gateway 的 audit 只写内存列表，没有写入已有的 `incident_tool_audits` 表。
- 前端步骤条缺少“风险评估”和“验证中”，也不能表达人工接管或失败发生在哪一步。

## 范围

### 本轮包含

- 新增 `NEEDS_HUMAN` 终态。
- 修复证据可用性判断、质量评分和失败记录。
- 修复 critic 循环上限后的人工接管逻辑。
- 限制 remediation 只能基于有效证据生成自动动作。
- 在审批创建前执行自动化能力预检。
- 修复审批恢复的 checkpoint 和步数连续性。
- 区分暂停事件与终态事件。
- 将工具审计持久化到数据库并脱敏。
- 为人工接管生成降级 RCA。
- 同步 API、前端类型、状态标签和步骤条。
- 补充 Alembic migration 和回归测试。

### 本轮不包含

- 实现真实 `execute_action`。
- 接入新的工单系统、K8s 集群、OSS 配置或外部基础设施。
- 重构整个 LangGraph 拓扑。
- 将 SQLite 替换为其他数据库。
- 引入队列、Redis 或跨进程事件总线。

## 状态模型

### Run 终态语义

| 状态 | 含义 | 是否终态 | 是否允许审批恢复 |
| --- | --- | --- | --- |
| `WAITING_HUMAN` | 已生成可执行动作，等待人工审批 | 否 | 是 |
| `NEEDS_HUMAN` | 自动化无法继续，需要人工接管 | 是 | 否 |
| `FAILED` | 动作已尝试执行但失败，或图执行异常 | 是 | 否 |
| `COMPLETED` | 自动流程正常完成 | 是 | 否 |

`WAITING_HUMAN` 仅用于“存在可审批且通过预检的动作”。证据不足、能力缺失、必要
配置缺失和必要前置条件不满足均使用 `NEEDS_HUMAN`。

### 展示阶段

前端步骤条使用 10 个展示阶段：

```text
新建
  -> 已分诊
  -> 已计划
  -> 收集证据中
  -> 已诊断
  -> 风险评估
  -> 待审批
  -> 执行中
  -> 验证中
  -> 已完成
```

“风险评估”是 `node_risk_gate` 的展示阶段，不新增 LangGraph 节点。后端通过
`current_node`、`halted_at_node` 和 run 状态映射展示位置。

### 终态原因

run 记录增加结构化 `terminal_reason_json`，API 返回 `terminal_reason`：

```json
{
  "code": "AUTOMATION_CAPABILITY_UNAVAILABLE",
  "stage": "risk_gate",
  "message": "execute_action real adapter is not configured",
  "failed_tools": ["execute_action"],
  "missing_evidence_categories": ["deployments", "runbook"]
}
```

run 记录同时增加 `halted_at_node`，用于标记人工接管或失败发生的位置。
graph state 同步增加 `terminal_reason` 和 `halted_at_node`，GraphRunner 在每个节点完成后
将最新值同步到 run 记录。

## 证据可靠性

### 采集结果分类

每个调查任务必须留下结构化结果，不再静默返回 `None`：

| 状态 | 含义 | 是否计入有效覆盖率 |
| --- | --- | --- |
| `SUCCESS_USABLE` | 调用成功且返回可用于诊断的数据 | 是 |
| `SUCCESS_EMPTY` | 调用成功但日志、指标或列表为空 | 否 |
| `FAILED_CONFIG` | 配置缺失、adapter 未接入等环境问题 | 否 |
| `FAILED_RUNTIME` | 超时、断连、外部 API 错误等运行时问题 | 否 |

调查结果应记录工具、类别、状态、错误摘要、延迟和采集时间。成功且可用的数据继续
写入 `evidence_items`；空结果和失败结果写入新的 state 字段
`evidence_collection_results`，供 aggregate、critic、RCA 和 UI 使用。

`evidence_collection_results` 随 checkpoint 持久化。工具调用的完整审计另外写入
`incident_tool_audits`。前者用于工作流决策和 UI 展示，后者用于排障追溯。

### 可用性判断

Gateway 只负责判断工具调用是否成功。节点层根据工具类型判断 payload 是否可用：

- `query_logs`：`logs` 非空。
- `query_metrics`：至少一个指标包含非空 `values`。
- `query_deployments`：包含 deployment 数据。
- `query_runbook`：包含 runbook 数据。
- K8s、DB、SLB 工具：至少包含该工具约定的诊断数据字段。

判断逻辑集中在独立 helper，避免散落在 fanout、aggregate 和 RCA 中。

### 质量评分

质量评分仅使用 `SUCCESS_USABLE` 结果：

- 有效类别覆盖率。
- 有效证据平均置信度。
- 关键类别缺失项。

相同工具、类别和请求参数产生的重复空结果不提高质量分。重复可用结果可以保留
审计记录，但 aggregate 计算覆盖率时按类别去重。

## 节点行为

### evidence_fanout

- 并行执行调查任务。
- 每个任务生成结构化采集结果。
- 持久化成功证据和失败摘要。
- 对可降级任务保留失败结果后继续流程。
- 对不可降级任务转 `NEEDS_HUMAN`，记录原因。

### evidence_aggregate

- 仅基于有效证据计算质量分。
- 输出 `missing_evidence_categories`。
- 输出 `failed_evidence_tools`。
- 不把空结果计入覆盖率。

### critic

- 证据足够时返回 `PASS`。
- 仍可补充证据且未达到循环上限时返回 `NEED_MORE_EVIDENCE`。
- 达到循环上限后不再强制 `PASS`，改为：
  - 设置 `status=NEEDS_HUMAN`。
  - 写入 state 字段 `terminal_reason`。
  - 路由到 RCA。

### remediation

- 自动动作必须引用有效证据 ID。
- `ActionSpec` 增加 `supporting_evidence_ids: List[str]`。
- 没有满足支持度要求的证据时，不生成默认 `restart`。
- 无法生成可信动作时设置 `NEEDS_HUMAN` 并路由到 RCA。

### risk_gate

- 保留现有风险等级判断。
- 在创建审批前执行 capability preflight。
- preflight 检查动作是否有真实 adapter、必要配置和必要前置条件。
- capability 不可用时设置 `NEEDS_HUMAN`，不创建审批。
- 只有通过 preflight 且需要人工批准的动作进入 `WAITING_HUMAN`。

### 路由闭环

修改 graph 条件路由，保证人工接管不会继续沿正常边执行：

- `_route_after_critic`：`status=NEEDS_HUMAN` 时进入 `node_rca`。
- remediation 后新增条件路由：`status=NEEDS_HUMAN` 时进入 `node_rca`，否则进入
  `node_risk_gate`。
- `_route_after_risk_gate`：`status=NEEDS_HUMAN` 时进入 `node_rca`。
- `node_rca` 保留人工接管状态，不改写为 `COMPLETED`。

### approval_interrupt 与恢复

- `approval_interrupt` 保存完整 checkpoint。
- 审批通过后从最新 `node_approval_interrupt` checkpoint 读取状态。
- 写入 `_resume_from_node="node_executor"`，由 dispatcher 直接跳转执行器。
- 不覆盖原始 `risk_decision`。
- `step_count` 从暂停时的值继续增长，不允许倒退。

### executor 与 verify

- 动作真实尝试失败时使用 `FAILED`。
- 动作成功后进入 `VERIFYING`。
- 验证失败根据现有可重试策略执行；重试耗尽后使用 `FAILED`。

### rca

- `COMPLETED` 和 `FAILED` 保留完整 RCA。
- `NEEDS_HUMAN` 生成降级 RCA，不将候选假设表述为确定结论。
- RCA 增加：
  - `root_cause_status`: `CONFIRMED | SUSPECTED | UNKNOWN`
  - `candidate_hypotheses`
  - `automation_outcome`
  - `manual_next_steps`

## 自动化能力预检

Gateway 提供只读 capability 查询，不真正执行动作：

```python
gateway.describe_capability("execute_action")
```

返回：

```json
{
  "available": false,
  "adapter_mode": "real",
  "reason": "real adapter is not configured"
}
```

该查询基于 Tool Gateway 已注册 handler、当前 adapter mode 和真实路由，不调用外部
系统。未来接入真实执行 adapter 后，可扩展动作类型、环境白名单和必要配置检查。

## GraphRunner 生命周期

GraphRunner 结束一次 graph 调用时区分暂停和终态：

- `WAITING_HUMAN`：
  - 清理 `current_node`。
  - 不写 `completed_at`。
  - 发送 `RUN_PAUSED`。
- `COMPLETED`、`FAILED`、`NEEDS_HUMAN`：
  - 写入 `completed_at`。
  - 清理 `current_node`。
  - 发送 `RUN_COMPLETED`。
- 图执行异常：
  - 写入 `FAILED`。
  - 写入 `halted_at_node` 和异常原因。
  - 发送 `RUN_FAILED`。

## 工具审计持久化

`ToolGateway` 每次调用都写入 `incident_tool_audits`：

- `run_id`
- `tool_name`
- `adapter_mode`
- `request_json`
- `response_json`
- `success`
- `error_message`
- `latency_ms`
- `created_at`

内存 `audit_log` 保留用于本地调试，但数据库是事实源。

参数校验失败、工具未注册、真实 adapter 缺失等早期返回路径也必须写入审计，确保
每一次调用都有可追溯记录。

持久化前递归脱敏以下键名及其常见变体：

```text
password
secret
token
api_key
access_key
authorization
cookie
```

审计写入失败不能中断工具调用，但必须记录 warning。

## 数据模型与迁移

Alembic migration 增加：

- `incident_runs.halted_at_node`
- `incident_runs.terminal_reason_json`
- `incident_rca_reports.root_cause_status`
- `incident_rca_reports.candidate_hypotheses_json`
- `incident_rca_reports.automation_outcome_json`
- `incident_rca_reports.manual_next_steps_json`

同时为 `RunStatusEnum` 增加 `NEEDS_HUMAN`。SQLite 开发库和测试库必须通过 Alembic
迁移验证。已有旧库兼容补丁只用于开发环境兜底，不替代 migration。

`ActionSpec` 增加 `supporting_evidence_ids`，用于在 remediation 和 risk gate 中校验
动作是否有有效证据支持。

## API 契约

`GET /incidents/runs/{run_id}` 增加：

```json
{
  "halted_at_node": "node_risk_gate",
  "terminal_reason": {
    "code": "AUTOMATION_CAPABILITY_UNAVAILABLE",
    "stage": "risk_gate",
    "message": "execute_action real adapter is not configured"
  }
}
```

新增独立端点，避免破坏现有证据列表消费者。该端点从最新 checkpoint 的
`evidence_collection_results` 返回采集状态，使 UI 可以展示失败工具和空结果：

```text
GET /incidents/runs/{run_id}/evidence/collection-results
```

`GET /incidents/runs/{run_id}/rca` 返回新增 RCA 字段。

## 前端展示

### 步骤条

`RunStepper` 使用显式映射，不再直接依赖 `STEPS.indexOf(status)`：

- 接收 `status`、`currentNode` 和 `haltedAtNode`。
- 补齐“风险评估”和“验证中”。
- `WAITING_HUMAN` 高亮“待审批”。
- `NEEDS_HUMAN` 在 `halted_at_node` 对应阶段显示橙色 `!`。
- `FAILED` 在 `halted_at_node` 对应阶段显示红色 `×`。
- 后续阶段置灰。
- 未知状态使用保守 fallback，不重置为全部未开始。

### 详情页

- 顶部状态标签展示 `NEEDS_HUMAN`。
- 人工接管时显示 `terminal_reason`。
- 证据页展示失败工具、空结果和有效证据。
- RCA 页展示根因状态、候选假设、自动化停止原因和人工下一步。

## 测试策略

### 后端单元测试

- 空日志和空指标标记为 `SUCCESS_EMPTY`。
- 重复空指标不提高质量分。
- 配置失败和运行时失败保留结构化结果。
- critic 达到循环上限后转 `NEEDS_HUMAN`。
- remediation 没有有效证据引用时不生成动作。
- capability preflight 识别未接入的 `execute_action`。
- 证据不足时降级 RCA 使用 `UNKNOWN`，能力缺失但已有有效证据时使用 `SUSPECTED`。
- 降级 RCA 不输出确定性结论。

### 后端集成测试

- `WAITING_HUMAN` 不写 `completed_at`，发送 `RUN_PAUSED`。
- 审批恢复从暂停 checkpoint 继续，`step_count` 单调递增。
- capability 不可用时不创建审批。
- `NEEDS_HUMAN` 正确持久化终态原因和停止位置。
- 工具调用成功和失败均写入 `incident_tool_audits`。
- 审计敏感字段被脱敏。

### 前端测试

- 步骤条渲染 10 个展示阶段。
- `VERIFYING` 高亮“验证中”。
- `WAITING_HUMAN` 高亮“待审批”。
- `NEEDS_HUMAN` 在停止阶段显示橙色人工接管标记。
- `FAILED` 在停止阶段显示红色失败标记。
- 顶部状态标签和详情卡展示终态原因。
- 现有实时刷新控制器把 `NEEDS_HUMAN` 当作停止轮询的终态。

### 回归验证

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q
cd frontend && npx vitest run
cd frontend && npm run build
```

## 验收场景

### 场景 1：真实执行 adapter 未接入

- evidence 和 diagnosis 正常推进到风险评估。
- capability preflight 发现 `execute_action` 不可用。
- run 进入 `NEEDS_HUMAN`。
- 不创建审批。
- 步骤条停在“风险评估”，显示橙色人工接管标记。
- RCA 明确写“根因尚未确认”和人工下一步。

### 场景 2：高风险动作可执行

- capability preflight 通过。
- run 进入 `WAITING_HUMAN`。
- 不写 `completed_at`。
- 人工批准后从暂停 checkpoint 继续。
- `step_count` 单调递增。

### 场景 3：动作真实执行失败

- executor 已真实尝试动作。
- run 进入 `FAILED`。
- 步骤条停在“执行中”，显示红色失败标记。
- RCA 区分业务诊断候选和动作失败原因。

### 场景 4：证据循环耗尽

- 空证据和失败结果不提高有效质量分。
- 达到循环上限后进入 `NEEDS_HUMAN`。
- 不生成默认重启动作。
- RCA 输出缺失类别、失败工具和人工排查建议。

## 实施边界

本轮目标是让系统在无法可靠自动处置时诚实地停止。真实执行 adapter 的设计和接入
应作为后续独立任务处理，不与本轮可靠性修复耦合。
