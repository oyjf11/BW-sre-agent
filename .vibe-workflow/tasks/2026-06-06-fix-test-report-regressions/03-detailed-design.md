# 详细设计

## 根因证据

P0 数据流：

1. `planner_node()` 开启 specialist pool 后调用 `_generate_agent_tasks()`。
2. 任务生成逻辑使用 `f"{category}_specialist"`。
3. `agent_configs.yaml` 中实际 ID 是 `log_specialist` 和 `deployment_specialist`，不是 `logs_specialist` / `deployments_specialist`。
4. `_evidence_fanout_v2()` 通过 `agent_configs.get(task.agent_id)` 查不到配置，静默生成 LLM_FAILED shell。
5. deployments 证据缺失，`remediation_node()` 的 `_has_deployment_evidence()` 为 false。
6. 发布回归候选根因生成 LOW risk `restart`，`risk_gate_node()` 判定 `LOW_ONLY`，绕过审批。

额外确认：

- 固定 async LLM 输出后，原始 ID 得到 `LOW_ONLY + restart + COMPLETED`。
- 仅修正 ID 映射后，得到 `NEEDS_APPROVAL + rollback + WAITING_HUMAN`。

P1 根因：

- `backend/.env` 当前为 real，`gateway.ADAPTER_MODE` 在模块 import 时固化。
- mock 期望测试没有隔离 adapter mode，导致本地 real 配置下真实 K8s 只读请求被触发。

P2 根因：

- Python 3.9 没有内置 `anext()`。

## 修复设计

1. 在 `specialist_agent.py` 新增集中映射 `CATEGORY_AGENT_ID_MAP` 和 `agent_id_for_category()`。
2. `_generate_agent_tasks()`、`_fallback_from_plan_to_agent_tasks()`、`_build_default_agent_tasks()` 都使用该映射。
3. 新增测试确保 planner/default task 生成的 agent_id 都存在于 YAML 配置。
4. 高风险图集成测试补齐 async LLM stub，避免真实 LLM 网络影响审批断言。
5. 新增 `backend/app/tests/conftest.py`，每个测试默认强制 mock adapter；需要 real 的测试仍可在用例内 monkeypatch。
6. `test_event_bus.py` 改用 `iterator.__anext__()` 兼容 Python 3.9。

## 回滚方式

回滚本次改动文件即可：

- `backend/app/graph/nodes/specialist_agent.py`
- `backend/app/graph/nodes/__init__.py`
- `backend/app/tests/conftest.py`
- `backend/app/tests/test_graph_integration.py`
- `backend/app/tests/test_specialist_agent.py`
- `backend/app/tests/test_event_bus.py`
- `.vibe-workflow/tasks/2026-06-06-fix-test-report-regressions/`
- `ACTION_PLAN.md`

