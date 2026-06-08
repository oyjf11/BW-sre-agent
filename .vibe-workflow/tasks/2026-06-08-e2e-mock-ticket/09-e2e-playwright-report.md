# E2E 测试报告

## 说明

本次未执行浏览器 Playwright UI 测试。用户目标是创建模拟工单并执行 OpsPilot 端到端全流程，因此本次采用后端 API E2E 验证 graph/API/DB/checkpoint/event/action/RCA/trace 链路。

## Run 1：specialist pool 开启

- Ticket：`INC-E2E-20260608-001`
- Run ID：`9fd9699d-ba40-45da-b7c3-e2b1504d8138`
- 环境：`staging`
- 结果：`NEEDS_HUMAN`
- step_count：17
- halted_at_node：`node_critic`
- terminal_reason：`EVIDENCE_LOOP_EXHAUSTED`
- 事件数：55
- ERROR 事件数：0

结论：specialist pool 分支未完成自动闭环，critic 两轮补证据后触发人工介入。

## Run 2：specialist pool 关闭，staging

- Ticket：`INC-E2E-20260608-002`
- Run ID：`de077f74-3566-48cb-98b6-b064f7bd8480`
- 环境：`staging`
- 结果：`COMPLETED`
- step_count：13
- 事件数：45
- ERROR 事件数：0
- evidence：11 条
- remediation：1 个 `restart` action，`risk_level=LOW`，`requires_approval=false`
- action：`restart` 执行完成
- trace：32 spans，errored spans 0

主链路覆盖：

intake -> triage -> retrieve_memory -> planner -> evidence_fanout -> evidence_aggregate -> diagnose -> critic -> remediation -> risk_gate -> executor -> verify_outcome -> rca。

## Run 3：specialist pool 关闭，prod

- Ticket：`INC-E2E-20260608-003`
- Run ID：`44ab7ee4-1527-4d1a-8db6-a339d71131ac`
- 环境：`prod`
- 结果：`COMPLETED`
- step_count：13
- 事件数：45
- ERROR 事件数：0
- remediation：1 个 `restart` action，`risk_level=LOW`，`requires_approval=false`
- action：`restart` 对 `payment-service/prod` 执行完成，mock adapter
- pending approvals：空

结论：生产环境分支也未覆盖审批恢复，因为 risk gate 收到的 action 是低风险且不需要审批。

## 发现的问题

1. Specialist pool 开启时，mock E2E 未能自动闭环。
   - 证据：后端日志出现 `Final LLM call failed`、`LLM timeout round 1`；run 最终 `NEEDS_HUMAN`，`terminal_reason.code=EVIDENCE_LOOP_EXHAUSTED`。
   - 影响：默认 `.env` 下 `AGENT_FEATURE_SPECIALIST_POOL=true` 时，模拟工单可能无法完成 happy path。

2. Specialist pool 的 LLM 失败未体现在 run events 的 ERROR 事件中。
   - 证据：Run 1 后端日志有 specialist LLM error/warning，但 `/events` 返回 55 条事件且 ERROR 数为 0。
   - 影响：仅看事件流会误判没有异常，排障需要同时看服务日志。

3. `prod/P2` 的 `restart` 被判定为 `LOW` 且 `requires_approval=false`，直接执行。
   - 证据：Run 3 remediation API 返回 `env=prod`、`action_type=restart`、`risk_level=LOW`、`requires_approval=false`，pending approvals 为空，events 显示直接进入 `node_executor`。
   - 影响：审批分支无法通过常规 mock 工单覆盖；生产动作是否应强制审批需要产品/安全策略确认。

4. RCA markdown 的 Execution Results 出现 `unknown: SUCCESS` 文案。
   - 证据：Run 2 RCA markdown 中出现 `- unknown: SUCCESS`，而 actions API 可正确返回 `action_type=restart`。
   - 影响：RCA 可读性和审计解释性不足。

5. 后端全量测试命令本次未在观察窗口内完成。
   - 证据：`python -m pytest app/tests/ -x -q` 运行超过 3 分钟仍未退出，已终止；focused 回归 16 个通过。
   - 影响：全量测试耗时/挂起点需要单独定位。

