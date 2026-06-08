# 实施计划

## 修改文件清单

仅新增本目录下的测试记录与原始响应文件，不修改业务代码。

## 执行步骤

1. 检查 8000 端口和 `/healthz`。
2. 用临时 SQLite 数据库启动后端，覆盖 `TOOL_ADAPTER_MODE=mock`。
3. 创建模拟工单并轮询 run 状态。
4. 若进入审批，提交 approved 决策并继续轮询。
5. 采集 run/events/evidence/diagnosis/remediation/actions/rca/trace。
6. 运行相关后端测试。
7. 汇总问题与知识沉淀。

## 失败回滚

删除 `.vibe-workflow/tasks/2026-06-08-e2e-mock-ticket/` 即可移除本次记录和临时 DB。

