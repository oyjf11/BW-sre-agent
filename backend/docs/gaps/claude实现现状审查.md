# Claude 实现现状审查

更新日期: 2026-03-29

## 审查范围

- 后端 FastAPI API、LangGraph 主链路、运行时与持久化
- 工具网关、LLM 接入、知识写回与归档
- 前端页面、API 接入、审批与 RCA 展示
- 本地测试与当前可验证状态

## 结论摘要

当前仓库已经具备一条可以串起来的主流程骨架:

- `incidents` / `approvals` API 已接上数据库和后台任务
- LangGraph 主图已经包含 `intake -> triage -> retrieve_memory -> planner -> evidence -> diagnose -> critic -> remediation -> risk -> approval/executor -> verify -> rca`
- 事件、checkpoint、evidence、action、RCA 都已有表结构和仓储层
- 前端已经有 Dashboard、创建 run、run 详情、审批列表/详情、RCA 页面

但它还不能算“生产可用”或“已完整收口”，主要原因是:

- 审批中断与恢复闭环没有真正打通
- 审批请求没有真正落库
- 部分节点调用了根本没注册的 tool
- LLM 与 real adapter 仍大量依赖 fallback / stub
- 运行库与 Alembic migration 存在漂移风险

## 主要问题

### P0. 审批请求没有真正落库，审批页面可能拿不到待审批数据

现状:

- `approval_interrupt_node` 只是在 state 里构造 `pending_approval`，没有调用 `ApprovalsRepo.create()` 持久化审批记录。
- `ApprovalsRepo.create()` 已存在，但没有被图节点或运行时使用。
- 前端审批列表和审批详情都依赖数据库中的审批记录。

证据:

- `backend/app/graph/nodes/__init__.py:795`
- `backend/app/graph/nodes/__init__.py:821`
- `backend/app/repositories/approvals_repo.py:13`
- `backend/app/api/approvals.py:70`

影响:

- 高风险动作进入 `WAITING_HUMAN` 后，UI 不一定能在 `/approvals/pending` 看见对应审批单。
- 审批决策接口依赖 `approval_id` 查库，真实闭环会断。

### P0. “resume from checkpoint” 只取回 state，没有从中间节点恢复执行

现状:

- `/incidents/runs/{run_id}/resume` 会取出 checkpoint 的 state，但最终仍调用 `_run_graph_bg()`。
- `_run_graph_bg()` 内部走 `RuntimeService.start_run()`，而 `GraphRunner.run()` 总是从 `create_incident_graph()` 的固定入口开始执行。
- 图入口在 builder 中被固定为 `node_intake`。

证据:

- `backend/app/api/incidents.py:314`
- `backend/app/api/incidents.py:329`
- `backend/app/services/runtime.py:55`
- `backend/app/services/graph_runner.py:63`
- `backend/app/graph/builder.py:90`

影响:

- “恢复执行”本质上更像“拿着旧 state 再从头跑一次”。
- `modify`、`more_evidence`、审批通过后的精确分支恢复都没有真正实现。

### P0. 审批 decision 只有 `approved` 会继续执行，`modify` / `more_evidence` 只是记状态

现状:

- `submit_decision()` 里只有 `approved` 会触发 `_resume_run_bg()`。
- `ApprovalRuntime.handle_decision()` 对 `modify` 和 `more_evidence` 只更新审批状态，没有改写 graph state，也没有重新路由。

证据:

- `backend/app/api/approvals.py:85`
- `backend/app/api/approvals.py:108`
- `backend/app/services/approval_runtime.py:26`

影响:

- 文档里写的四种审批分支，当前实际上只实现了“批准后继续”和“拒绝后失败”。
- `modify` / `more_evidence` 属于表面支持、实际上未闭环。

### P0. 运行库与模型字段已发生漂移，当前后端测试有 2 条集成测试失败

现状:

- ORM 中 `incident_actions` 已新增 `approval_id`、`attempt_no`、`executor_name` 等字段。
- 运行时仍通过 `init_db()` 直接 `Base.metadata.create_all()`，没有在应用启动阶段强制执行 Alembic migration。
- 本地测试执行时，图跑到 `executor` 会因为表缺少 `approval_id` 列而失败。

证据:

- `backend/app/models/db_models.py:99`
- `backend/app/repositories/__init__.py:37`
- `backend/app/api/incidents.py:21`
- `backend/alembic/versions/004_extend_actions.py:15`

实测:

- 在 `backend/` 目录执行 `PYTHONPATH=. pytest app/tests -q`
- 结果: `57 passed, 2 failed`
- 失败用例: `app/tests/test_graph_integration.py::test_graph_execution` 与 `test_graph_flow`
- 失败原因: `sqlite3.OperationalError: table incident_actions has no column named approval_id`

影响:

- 当前仓库不是“拉下来即可稳定运行”的状态。
- 已有本地数据库或测试数据库如果没迁移，会直接打断主流程。

### P1. 工具调用面与实际注册的 tool 不一致，多个分支只能走降级或空转

现状:

- 网关当前只注册了 5 个 tool: `query_logs`、`query_metrics`、`query_deployments`、`query_runbook`、`execute_action`
- 但代码中还直接调用了:
  - `query_ticket_by_id`
  - `query_service_metadata`
  - `query_k8s_deployment_status`
  - `query_lb_health_status`
  - `query_lb_traffic_metrics`

证据:

- `backend/app/tools/gateway.py:71`
- `backend/app/services/intake.py:31`
- `backend/app/services/executor.py:207`
- `backend/app/services/executor.py:216`
- `backend/app/graph/nodes/__init__.py:910`
- `backend/app/graph/nodes/__init__.py:936`
- `backend/app/graph/nodes/__init__.py:962`

影响:

- `ticket_id` 入口无法真正查工单，只会退回最小 ticket fallback。
- verify 阶段拿不到真正的 K8s / SLB 验证证据。
- precondition 检查不是“真实校验”，而是“查不到 tool 后失败”。

### P1. OpenAI 实际未接通到图节点使用的同步 LLM 路径

现状:

- 图节点调用的都是 `llm_client.complete_sync()`
- `complete_sync()` 会走 `_openai_complete_sync()` 或 `_minimax_complete_sync()`
- 其中 `_openai_complete_sync()` 直接返回 fallback，没有真正调用 OpenAI

证据:

- `backend/app/graph/nodes/__init__.py:119`
- `backend/app/graph/nodes/__init__.py:574`
- `backend/app/graph/nodes/__init__.py:1110`
- `backend/app/llm_client.py:154`
- `backend/app/llm_client.py:200`

影响:

- 当前真正可用的同步 LLM 只有 MiniMax 路径。
- 即使配置了 `LLM_PROVIDER=openai`，图节点仍会退化到 fallback。

### P1. 配置校验和实际 provider 逻辑不一致

现状:

- `Settings.validate_for_production()` 在非 `dev` 环境下硬性要求 `OPENAI_API_KEY`
- 但默认 provider 是 `minimax`
- 校验逻辑没有根据 `LLM_PROVIDER` 分支判断

证据:

- `backend/app/core/config.py:46`
- `backend/app/core/config.py:60`
- `backend/app/llm_client.py:19`

影响:

- 如果准备在 `staging` / `prod` 用 MiniMax，当前配置校验会误报。
- 配置说明和实际代码行为不一致。

### P1. 审批详情页需要的字段后端并未提供

现状:

- 前端 `ApprovalDetailPage` 读取 `reason`、`expected_impact`、`rollback_plan`
- 后端 `ApprovalResponse` 只返回 `approval_id/run_id/action/risk_level/status/...`
- 审批表本身也没保存 `reason`、`expected_impact`、`rollback_plan`

证据:

- `frontend/src/pages/ApprovalDetailPage.tsx:115`
- `frontend/src/types/index.ts:91`
- `backend/app/api/approvals.py:39`
- `backend/app/models/db_models.py:83`

影响:

- 审批详情页的信息不完整，部分字段会是空值或 `undefined`
- 审批链路的审计信息不足

### P2. 前端没有接上后端新增的三种 run 创建模式

现状:

- 后端 `/incidents/runs` 支持 `ticket`、`ticket_id`、`alert_event` 三种互斥输入
- 前端 `runs.createRun()` 只支持 `{ ticket }`
- 创建页面虽然有 `ticket_id` 输入框，但最终仍组装成完整 `ticket`
- 标题、服务、环境、severity 仍要求手工填，无法走“只输 ticket_id”模式

证据:

- `backend/app/api/incidents.py:48`
- `frontend/src/services/runs.ts:4`
- `frontend/src/pages/RunCreatePage.tsx:32`
- `frontend/src/pages/RunCreatePage.tsx:84`

影响:

- 前端无法验证和使用后端已经实现的 `ticket_id` / `alert_event` 能力。

### P2. GraphRunner 的节点事件并不是真正的“节点开始/结束包装器”

现状:

- `GraphRunner.run()` 是在 `graph.astream()` 产出节点结果后，才写 `NODE_STARTED` 和 `NODE_COMPLETED`
- 它没有在节点执行前注入 wrapper，也没有在单节点失败时写 `NODE_FAILED`

证据:

- `backend/app/services/graph_runner.py:73`
- `backend/app/services/graph_runner.py:79`
- `backend/app/services/graph_runner.py:91`
- `backend/app/services/graph_runner.py:117`

影响:

- `NODE_STARTED` 时间语义不准确
- 节点级失败事件和精确耗时信息不完整

### P2. `.env.example` 中包含真实凭证样式的 MiniMax Key，存在泄漏风险

现状:

- 示例文件中直接写入了一段看起来像真实 key 的 `MINIMAX_API_KEY`

证据:

- `backend/.env.example:17`

影响:

- 即使它是测试 key，也不应该出现在示例配置中
- 容易误导后续协作者继续把真实凭证写进版本库

## 当前实现概览

### 后端

#### API 层

- `incidents`:
  - 创建 run
  - 查询 run 列表/详情
  - 查询事件、evidence、actions、RCA
  - RCA 确认
  - resume
- `approvals`:
  - 待审批列表
  - 审批详情
  - 审批 decision

主要入口:

- `backend/app/api/incidents.py`
- `backend/app/api/approvals.py`

#### LangGraph 主链路

当前 builder 已经定义完整主图:

- `intake`
- `triage`
- `retrieve_memory`
- `planner`
- `evidence_fanout`
- `evidence_aggregate`
- `diagnose`
- `critic`
- `remediation`
- `risk_gate`
- `approval_interrupt`
- `executor`
- `verify_outcome`
- `rca`

条件路由:

- `critic`: `PASS / NEED_MORE_EVIDENCE / REPLAN / CONTRADICTION`
- `risk_gate`: `LOW_ONLY / NEEDS_APPROVAL / BLOCKED`
- `verify`: `SUCCESS / RETRYABLE_FAILURE / FATAL_FAILURE`

主要入口:

- `backend/app/graph/builder.py`
- `backend/app/graph/nodes/__init__.py`

#### 运行时与持久化

已实现:

- `RuntimeService`
- `GraphRunner`
- `EventBus`
- `RunsRepo / EventsRepo / CheckpointsRepo / EvidenceRepo / ActionsRepo / RcaRepo / ApprovalsRepo`
- Alembic migration `001` 到 `005`

主要入口:

- `backend/app/services/runtime.py`
- `backend/app/services/graph_runner.py`
- `backend/app/services/event_bus.py`
- `backend/app/repositories/`
- `backend/alembic/versions/`

#### LLM 参与点

当前 LLM 只用于增强分析，不是流程硬依赖:

- triage
- diagnose
- rca

未配置 LLM 时的行为:

- triage 走 `rules -> fallback`
- diagnose 生成默认候选根因
- rca 生成默认 RCA 内容

主要入口:

- `backend/app/llm_client.py`
- `backend/app/graph/nodes/__init__.py`

#### 工具层

当前工具层分三部分:

- Tool schema 注册
- Gateway 路由与 retry
- mock adapters

已注册 tool:

- `query_logs`
- `query_metrics`
- `query_deployments`
- `query_runbook`
- `execute_action`

real adapter 状态:

- 只有 `not configured` 占位
- `backend/app/tools/adapters/` 还没有拆分成 `mysql/k8s/slb/oss`

### 前端

已实现页面:

- Dashboard
- Run 创建
- Run 详情
- Approvals 列表
- Approval 详情
- RCA 页面

接入方式:

- 统一通过 `frontend/src/services/api.ts`
- 主要使用 HTTP polling
- `sse.ts` 已存在，但当前没有页面接入

已知限制:

- 创建页只走 `ticket` 模式
- run 详情页轮询 `/events`
- 审批详情页依赖的字段比后端实际返回更多

## 待配置的信息

### 后端基础配置

必须确认:

- `APP_ENV`
- `DATABASE_URL`
- `TOOL_ADAPTER_MODE`
- `LOG_LEVEL`

当前默认值:

- `APP_ENV=dev`
- `DATABASE_URL=sqlite+aiosqlite:///./opspilot.db`
- `TOOL_ADAPTER_MODE=mock`

注意:

- 仓储层会把 `sqlite+aiosqlite:///` 转成同步 SQLAlchemy 可用的 `sqlite:///`
- 当前应用启动没有自动跑 Alembic，切换环境前应先确认 migration 已执行

### LLM 配置

如果只想让系统先跑通:

- 可以不配置 LLM
- 系统会走 fallback 逻辑

如果要启用真实 LLM:

- `LLM_PROVIDER`
- 当 `LLM_PROVIDER=minimax` 时:
  - `MINIMAX_API_KEY`
  - `MINIMAX_GROUP_ID`
  - `MINIMAX_MODEL`
- 当 `LLM_PROVIDER=openai` 时:
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`

当前真实情况:

- MiniMax 同步路径已接代码
- OpenAI 同步路径未实现

### 前端配置

必须确认:

- `VITE_API_URL`

默认值:

- `http://localhost:8000`

### 真正要上 real adapter 时还缺的配置

当前代码尚未实现这些 adapter，但按设计最终至少需要:

- MySQL / 工单系统连接配置
- K8s 集群连接配置
- SLB / LB 只读查询配置
- OSS 归档配置

这些配置项目前仓库里还没有正式定义出来。

## 仍然是 mock / stub / fallback 的逻辑

### 明确是 mock 的部分

- `backend/app/tools/adapters/__init__.py`
  - `query_logs`
  - `query_metrics`
  - `query_deployments`
  - `query_runbook`
  - `execute_action`

特点:

- 返回随机或静态拼装数据
- 没有真实平台连接

### 明确是 stub 的部分

- real adapter 路由:
  - `backend/app/tools/gateway.py:24`
  - 统一抛出 “Real adapter not configured”
- 知识写回:
  - `backend/app/services/knowledge_writeback.py:130`
  - 只是日志 stub
- RCA 归档:
  - `backend/app/services/knowledge_writeback.py:123`
  - 只返回伪造的 `rca/{run_id}/report.md`

### 明确是 fallback 的部分

- LLM 未配置时:
  - `backend/app/llm_client.py:149`
- triage fallback:
  - `backend/app/graph/nodes/__init__.py:151`
- diagnose fallback:
  - `backend/app/graph/nodes/__init__.py:606`
- rca fallback:
  - `backend/app/graph/nodes/__init__.py:1124`
- `ticket_id` 入口失败时最小 ticket fallback:
  - `backend/app/services/intake.py:53`

### 预留但未接入使用的部分

- `frontend/src/services/sse.ts`
  - 已实现客户端，但当前页面没有使用
- `backend/app/evals/`
  - 目录存在，但 P8 replay eval 还未实现
- `backend/app/tracing.py`
  - 只有轻量 span 记录，还不是完整可观测方案

## 测试与当前可验证状态

### 后端测试

已存在:

- `test_event_bus.py`
- `test_graph_integration.py`
- `test_models.py`
- `test_normalizers.py`
- `test_repositories.py`
- `test_serde.py`
- `test_tool_gateway.py`

本次执行结果:

- 命令: `PYTHONPATH=. pytest app/tests -q`
- 结果: `57 passed, 2 failed`

当前失败点:

- 图集成测试在 `executor` 阶段触发数据库字段漂移问题

### 前端测试

已存在:

- 组件测试
- 页面测试
- service / utils 测试

本次没有执行前端测试，因此不能确认当前全部通过。

### E2E

仓库内有 Playwright 规格:

- `tests/e2e/approval.spec.ts`
- `tests/e2e/diagnose.spec.ts`
- `tests/e2e/events.spec.ts`
- `tests/e2e/evidence.collection.spec.ts`
- `tests/e2e/executor.spec.ts`
- `tests/e2e/incident.create.spec.ts`
- `tests/e2e/incident.lifecycle.spec.ts`
- `tests/e2e/rca.spec.ts`
- `tests/e2e/triage.spec.ts`

本次没有执行 E2E。

## 建议的下一步

1. 先修复审批记录落库、decision 分支恢复、resume 从中间节点继续执行这三个 P0 问题。
2. 明确数据库初始化策略，只保留 Alembic 一条权威路径，清掉 `create_all()` 带来的漂移风险。
3. 对齐 tool registry 与 graph/service 的实际调用面，先补齐 `query_ticket_by_id`、`query_service_metadata`、`query_k8s_deployment_status`、`query_lb_health_status`、`query_lb_traffic_metrics`。
4. 明确 LLM 策略: 要么正式只支持 MiniMax，要么补上 OpenAI 的同步路径。
5. 前端补齐 `ticket_id` / `alert_event` 创建入口，并修正审批详情字段契约。
