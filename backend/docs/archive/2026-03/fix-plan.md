# 实现缺陷修复计划（修订版）

更新日期: 2026-03-29

来源审查: `claude实现现状审查.md`

---

## 总体目标

将当前“可串起来的主流程骨架”升级为**闭环可验证**的状态：审批可查、resume 可继续、执行链不断、测试可稳定全绿、数据库初始化路径单一。

---

## 当前基线

- 当前后端测试命令应以 `PYTHONPATH=. pytest app/tests -q` 为准。
- 当前实测结果：**60 collected, 60 passed, 0 failed**（已验证）。
- 已完成修复：
  - `ControlledExecutor` 的 `EXECUTION_*` 事件枚举不匹配 → 已统一为 `ACTION_*`。
  - `critic_node` 的 `None` 默认值风险 → 已加固（`or 0` / `or []` / `or {}`）。
  - `test_graph_execution`：monkeypatch risk_gate + verify_outcome，确保低风险完整链路可测。
  - `test_graph_flow`：`node_logs` 断言已更新为 `node_evidence_fanout` / `node_evidence_aggregate`，加 monkeypatch 保证全链路可达。
- 当前无红测，下一个优先级是 **P0-1（审批请求落库）**。

---

## P0 — 必须修复（阻断主流程）

### P0-1 审批请求落库与审批详情字段一次性打通

**问题**：
`approval_interrupt_node` 只在 state 里构造 `pending_approval`，没有写库；同时审批表和 API 又缺 `reason`、`expected_impact`、`rollback_plan`。如果分两次修，会先引入一版 ID 不一致、字段不全的半成品。

**修复位置**：
- `backend/app/graph/nodes/__init__.py`
- `backend/app/repositories/approvals_repo.py`
- `backend/app/models/db_models.py`
- `backend/app/api/approvals.py`
- `backend/alembic/versions/`（新增 migration）

**修复方案**：
1. 在 `IncidentApproval` 表新增 `reason`、`expected_impact`、`rollback_plan`。
2. 新增 Alembic migration，例如 `006_approval_fields.py`。
3. `ApprovalsRepo.create()` 改为支持传入显式 `approval_id` 和上述字段，不再在 repo 内重新生成一个新的审批 ID。
4. `approval_interrupt_node` 生成审批请求后，立即持久化，并保证：
   - state 中的 `pending_approval.approval_id`
   - 数据库中的 `incident_approvals.approval_id`
   - 后续审批通过写入 `approval_result.approval_id`
   三者一致。
5. `ApprovalResponse` 补齐上述字段，保证审批详情页能直接展示。

**验收标准**：
- 主流程跑到 `approval_interrupt` 后，`incident_approvals` 表有新记录。
- `/approvals/pending` 和审批详情接口能查到同一张审批单。
- 审批详情页中的 `reason`、`expected_impact`、`rollback_plan` 不再是 `undefined`。

---

### P0-2 Resume 机制改为”明确可实现的恢复策略”，不再假设 `ainvoke(state)` 自动续跑

**问题**：
当前 `/incidents/runs/{run_id}/resume` 和审批通过后的 `_resume_run_bg()` 都只是读取 checkpoint state 再重新调用统一 runner；但图入口仍固定为 `node_intake`，`checkpoint.node_name` 没被真正用于调度。现有代码并不能证明“把 checkpoint state 传回图，就会从中断节点继续”。

**修复位置**：
- `backend/app/api/incidents.py`
- `backend/app/api/approvals.py`
- `backend/app/services/runtime.py`
- `backend/app/services/graph_runner.py`
- `backend/app/services/approval_runtime.py`
- `backend/app/graph/builder.py`

**修复方案**：
1. 不再把“LangGraph 可直接从任意 checkpoint state 恢复”当成默认事实；先验证当前 `langgraph==0.0.55` 的实际能力。
2. 如果当前版本不能原生恢复，则落业务层 resume dispatcher：
   - 读取最近 checkpoint 的 `node_name`。
   - 显式决定从哪个节点续跑，而不是重新走 `node_intake`。
3. `GraphRunner.run()` / `RuntimeService.start_run()` 增加 resume 参数，例如：
   - `resume_mode`
   - `start_from_node`
   - `resume_state`
4. 审批通过后不要写死 `approval_id = "resumed"`，要带回真实审批单 ID。
5. 记录 `RUN_RESUMED`、`CHECKPOINT_RESTORED` 等事件，便于排查。

**验收标准**：
- resume 后，`events` 表里没有重复的 `intake` / `triage` 事件。
- 审批通过后能直接衔接到正确的后续节点。
- `approval_result.approval_id` 与审批表中的真实记录一致。

---

### P0-3 完整实现四种审批决策分支，并修正 `modify` / `more_evidence` 的落点

**问题**：
当前 `submit_decision()` 只有 `approved` 触发 resume，`modify` 和 `more_evidence` 只改审批状态；而且原计划里把 `modify` 落到 `remediation` 节点不合理，因为 `remediation_node` 会重建 plan，覆盖人工修改结果。

**修复位置**：
- `backend/app/api/approvals.py`
- `backend/app/services/approval_runtime.py`
- 与 resume 相关的 runner/runtime 代码

**修复方案**：

| Decision | 期望行为 |
|----------|---------|
| `approved` | 继续执行，进入 `executor` |
| `rejected` | 结束 run，标记 `FAILED` |
| `modify` | 更新 checkpoint 中的 `remediation_plan`，重新进入 `risk_gate` |
| `more_evidence` | 更新 `investigation_plan/plan/user_context`，重新进入 `evidence_fanout` |

补充要求：
1. `ApprovalDecision` request body 补充结构化字段，不能只收一个 comment。
2. `modify` 必须写回人工修改后的 remediation plan。
3. `more_evidence` 不能只改审批状态，必须把“需要补什么证据”写回 state，否则重跑只会采同一批任务。
4. `approved` / `modify` / `more_evidence` 都要走统一 resume 机制。

**验收标准**：
- `modify` 后不会被 `remediation_node` 再次覆盖人工修改的 plan。
- `more_evidence` 后会产生新的证据采集任务，而不是简单重复原任务。
- `rejected` 后 run 状态正确终止为 `FAILED`。

---

### P0-4 数据库初始化策略统一（Alembic 成为唯一权威路径）

**问题**：
当前运行时仍通过 `init_db()` 执行 `create_all()`，同时再用 SQLite patch 修补老库。这是一条“能启动但不权威”的路径，会继续制造 schema 漂移。它是风险点，但不是当前 3 条红测的直接根因，文档里原先的归因需要修正。

**修复位置**：
- `backend/app/repositories/__init__.py`
- `backend/app/api/incidents.py`
- `backend/app/main.py`
- `backend/alembic/versions/004_extend_actions.py`
- `backend/alembic/versions/005_extend_rca_add_writebacks.py`
- 新增 `006_approval_fields.py`

**修复方案**：
1. 运行时只保留 Alembic 作为 schema authority。
2. `create_all()` 仅保留给隔离的内存测试或 test fixture，不再作为应用启动路径。
3. 应用启动时通过 lifespan / startup 明确执行 `alembic upgrade head`，或在启动文档和 CI 中强制先 migrate。
4. 若保留 `ensure_sqlite_schema()`，需明确它只是本地 legacy SQLite 过渡补丁，不等同于正式 migration。
5. 校验 `004`、`005`、`006` migration 的 upgrade / downgrade 完整性。

**验收标准**：
- 新建库和旧库都能通过 `alembic upgrade head` 对齐字段。
- 运行时不再依赖 `create_all()` 来“偷偷补表补列”。
- 完整后端测试结果达到 **60 passed, 0 failed**。

---

## P1 — 应尽快修复（功能残缺）

### P1-1 补齐缺失的 Tool 注册

**问题**：
代码中调用了 5 个未注册的 tool，导致相关节点只能走 fallback 或空转。

**缺失的 tool**：

| Tool 名称 | 调用位置 | 用途 |
|-----------|---------|------|
| `query_ticket_by_id` | `intake.py:31` | `ticket_id` 入口查工单 |
| `query_service_metadata` | `executor.py:207` | precondition 检查服务存在性 |
| `query_k8s_deployment_status` | `nodes/__init__.py:910` / `executor.py:216` | verify 与 precondition |
| `query_lb_health_status` | `nodes/__init__.py:936` | verify 阶段查 LB 健康 |
| `query_lb_traffic_metrics` | `nodes/__init__.py:962` | verify 阶段查流量与错误率 |

**修复方案**：
1. 在 `backend/app/tools/gateway.py` 的 tool registry 中注册以上 5 个 tool。
2. 对应 mock 实现放在 `backend/app/tools/adapters/__init__.py`。
3. 增加 gateway 测试，覆盖这些工具都能被成功调度。

**验收标准**：
- 所有图节点不再出现 “tool not found” 类错误。
- `ticket_id` 入口能返回一个合理的 mock ticket，而不是最小 fallback。

---

### P1-2 明确 LLM 策略

**问题**：
`_openai_complete_sync()` 直接返回 fallback，配置了 OpenAI 也不会生效。

**选项 A：短期只正式支持 MiniMax**
1. 明确禁止未实现的 OpenAI sync 路径。
2. `Settings.validate_for_production()` 只在 `LLM_PROVIDER=openai` 时要求 `OPENAI_API_KEY`。

**选项 B：补齐 OpenAI sync 路径**
1. 在 `_openai_complete_sync()` 中实现真实同步调用。
2. 为同步调用增加错误处理与测试覆盖。

**修复位置**：
- `backend/app/llm_client.py`
- `backend/app/core/config.py`

**验收标准**：
- `LLM_PROVIDER=minimax` 时不会误要求 `OPENAI_API_KEY`。
- OpenAI 路径要么可用，要么明确 fail fast，不再静默 fallback。

---

### P1-3 清除 `.env.example` 凭证

**问题**：
`backend/.env.example` 中包含一段看起来像真实格式凭证的 `MINIMAX_API_KEY`。

**修复方案**：
将该值替换为 `your_minimax_api_key_here` 之类的占位符。

**修复位置**：
- `backend/.env.example`

**验收标准**：
- `.env.example` 中所有 key 都是占位符，不含真实格式凭证。

---

## P2 — 可延后处理

### P2-1 前端补齐三种创建入口

**目标**：
补充 `ticket_id` 和 `alert_event` 创建模式，让前端能验证后端已实现的能力。

**修复位置**：
- `frontend/src/services/runs.ts`
- `frontend/src/pages/RunCreatePage.tsx`

**方案**：
RunCreatePage 增加模式切换（ticket / ticket_id / alert_event），不同模式下展示不同表单字段。

---

### P2-2 节点事件时序修正

**目标**：
`NODE_STARTED` 应在节点开始执行前写入，失败时写 `NODE_FAILED`，与当前 `astream()` 后置写法解耦。

**修复位置**：
- `backend/app/services/graph_runner.py`

**方案**：
在节点执行前后做统一包装，记录精确的开始、结束、失败时间戳。

---

### P2-3 SSE 前端接入

**目标**：
让 run 详情页使用 `sse.ts` 替代 HTTP polling，降低延迟和无效请求。

**前提**：
后端 `/runs/{run_id}/stream` 端点稳定可用。

---

## 执行检查清单

```text
P0-0 [x] 集成测试全绿（EventType枚举、critic_node None加固、过期断言修正）
P0-1 [x] 审批请求落库 + 审批详情字段一次性打通（006 migration、ApprovalsRepo、approval_interrupt_node）
P0-2 [x] 设计并实现明确可执行的 resume 机制（dispatcher节点、prepare_resume_state、真实approval_id）
P0-3 [x] 完整实现 approved / rejected / modify / more_evidence 四种分支
P0-4 [x] 统一 Alembic，运行时移除 create_all() 权威地位（lifespan + alembic upgrade head）

P1-1 [x] 补齐 5 个缺失 tool 注册（query_ticket_by_id 等 5 个 mock + gateway 注册）
P1-2 [x] 明确 LLM 策略（MiniMax + OpenAI sync 路径均实现，config 按 provider 验证 key）
P1-3 [x] .env.example 凭证占位符替换

P2-1 [x] 前端补 ticket_id / alert_event 入口（RunCreatePage 三模式切换）
P2-2 [x] 节点事件时序修正（NODE_FAILED、duration_ms、last_node 追踪）
P2-3 [x] run 详情页接入 SSE（sseClient + 慢轮询 fallback，终态自动断开）
```

---

最终验收：PYTHONPATH=. pytest app/tests -q → **60 passed, 0 failed**（2026-03-30 验证）
