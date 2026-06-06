# 实现计划

## Slice 1: P0 specialist ID 回归

- RED：新增/稳定化测试，证明 generated agent_id 必须存在于 `agent_configs.yaml`，高风险发布回归必须进入 `WAITING_HUMAN`。
- GREEN：集中 category 到 agent_id 映射，并更新 planner/default/fallback task 生成。
- 验证：P0 相关 3 个测试通过。

## Slice 2: 测试 adapter 隔离

- 使用 pytest autouse fixture 将 `TOOL_ADAPTER_MODE` 和 `gateway.ADAPTER_MODE` 固定为 mock。
- 保留单测内 monkeypatch real 的能力。
- 验证：默认 `.env` real 下 `test_tool_gateway.py`、`test_mysql_adapter.py` 通过。

## Slice 3: Py3.9 测试兼容

- 将测试中的内置 `anext()` 替换为 async iterator 的 `__anext__()` 包装函数。
- 验证：Python 3.9.6 下 `test_event_bus.py` 通过。

## Slice 4: 回归验证与沉淀

- 后端全套测试。
- 前端 Vitest/build/lint。
- 更新任务文档和 `ACTION_PLAN.md`。

