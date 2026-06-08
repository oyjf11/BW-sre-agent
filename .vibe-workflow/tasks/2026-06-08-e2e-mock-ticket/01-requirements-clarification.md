# 需求澄清：模拟工单端到端全流程测试

## 任务理解

创建模拟工单，通过 OpsPilot 后端 API 执行端到端流程，并记录过程中发现的问题。

## 范围

- 使用 `POST /incidents/runs` 的手工工单模式创建模拟工单。
- 使用 mock tool adapter 避免依赖真实外部系统。
- 覆盖 graph 主链路：intake -> triage -> retrieve_memory -> planner -> evidence_fanout -> evidence_aggregate -> diagnose -> critic -> remediation -> risk_gate -> executor -> verify -> rca。
- 尝试覆盖审批分支：risk_gate -> approval_interrupt -> approval decision -> executor。
- 采集 run 状态、事件、证据、诊断、修复方案、动作、RCA、trace。

## 不在范围

- 不修改业务代码。
- 不修改 `backend/.env`。
- 不连接真实生产 adapter。
- 不执行真实生产动作；执行器使用 mock adapter。
- 不做前端 UI Playwright 测试，本次验证目标是后端 graph/API 端到端链路。

## 验收方式

- 至少一个模拟工单达到 `COMPLETED`。
- 事件流覆盖完整主链路节点。
- evidence/actions/RCA/trace API 可查询。
- 记录未覆盖或异常分支。

