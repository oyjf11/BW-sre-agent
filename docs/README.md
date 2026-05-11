# OpsPilot 文档索引

本文档用于区分“当前有效文档”和“历史归档”，避免后续开发被旧计划误导。

## 当前事实源

- `ACTION_PLAN.md`：唯一项目进度源。Phase、Task 完成状态以它为准。
- `AGENTS.md` / `CLAUDE.md`：AI 编码助手启动指南，内容应保持同步。
- `E2E_TESTING.md`：E2E 测试边界、运行方式和维护约定。
- `backend/README.md`：后端启动、测试、API 与 adapter 状态。
- `frontend/README.md`：前端启动、测试、页面与 API 同步约定。
- `backend/docs/gaps/current.md`：当前仍未完成或需谨慎处理的工程缺口。

## 设计与规格

- `backend/docs/design/aliyun-integration-design.md`：阿里云平台接入设计，仍可指导 SLB/OSS 后续实现。
- `guide/产品需求/OpsPilot_PRD_完整产品文档.md`：产品需求与定位。
- `guide/产品需求/OpsPilot_操作手册.md`：面向使用者的操作说明，后续需要按真实 UI 更新。
- `guide/技术规划/OpsPilot_TDD_完整技术文档.md`：技术总设计，作为架构参考，不作为当前进度依据。
- `.qa-artifacts/specs/`：黑盒 E2E 规格。
- `.qa-artifacts/generated-tests/spec-to-test-map.md`：规格到测试的映射，后续需要修正相对链接。

## 归档文档

- `docs/archive/2026-03/`：已解决或过期的 bug 汇总。
- `docs/archive/sisyphus/`：早期执行计划和工具计划。
- `docs/archive/agent-memory/`：旧 agent memory。
- `backend/docs/archive/2026-03/`：早期后端审查、gap 和修复计划。

归档文档只用于追溯历史，不作为当前实现依据。
