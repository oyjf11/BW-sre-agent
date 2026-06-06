# 需求澄清

## 任务理解

根据 `.test/OpsPilot Agent 测试报告-20260606.md` 排查并修复后端回归测试中的 3 类问题：

1. P0：specialist pool 开启时，高风险发布回归动作没有进入人工审批。
2. P1：本地 `.env` 为 `TOOL_ADAPTER_MODE=real` 时，mock 期望测试误触真实 adapter。
3. P2：`test_event_bus.py` 使用 Python 3.10+ 的内置 `anext()`，与当前 Python 3.9.6 venv 不兼容。

## 明确边界

涉及模块：

- `backend/app/graph/nodes/`
- `backend/app/tests/`
- `ACTION_PLAN.md`

明确不改：

- 不改 API 请求/响应契约。
- 不改真实 adapter 的实现语义。
- 不改前端代码。
- 不引入新依赖，不改锁文件。
- 不处理既有前端 lint 债务。

## 验收方式

- P0 最小复现测试先失败再通过。
- 默认 `.env` real 下后端测试不再触达真实 K8s。
- Python 3.9 下 `test_event_bus.py` 通过。
- 后端全套 `python -m pytest app/tests/ -x -q` 通过。
- 前端 Vitest 与 build 通过；lint 若失败需记录具体既有问题。

