# OpsPilot 文档索引

本文档用于区分“当前有效文档”和“历史归档”，避免后续开发被旧计划误导。

## 当前事实源

- `ACTION_PLAN.md`：唯一项目进度源。Phase、Task 完成状态以它为准。
- `AGENTS.md` / `CLAUDE.md`：AI 编码助手启动指南，内容应保持同步。
- `E2E_TESTING.md`：E2E 测试边界、运行方式和维护约定。
- `backend/README.md`：后端启动、测试、API 与 adapter 状态。
- `frontend/README.md`：前端启动、测试、页面与 API 同步约定。
- `backend/docs/gaps/current.md`：当前仍未完成或需谨慎处理的工程缺口。

维护规则：当前进度不要在多个文档里重复维护；需要判断 Phase / Task 状态时只看 `ACTION_PLAN.md`。其他文档可以写能力现状或使用说明，但必须引用 `ACTION_PLAN.md`，不能覆盖它的进度结论。

## 设计与规格

- `backend/docs/design/aliyun-integration-design.md`：阿里云平台接入设计与后续联调/扩展参考，不作为当前进度源。
- `guide/产品需求/OpsPilot_PRD_完整产品文档.md`：产品需求与定位。
- `guide/产品需求/OpsPilot_操作手册.md`：面向使用者的操作说明，后续需要按真实 UI 更新。
- `guide/技术规划/OpsPilot_TDD_完整技术文档.md`：技术总设计，作为架构参考，不作为当前进度依据。
- `docs/superpowers/specs/`、`docs/superpowers/plans/`：历史设计与实施计划记录，不作为当前完成状态依据。

## 归档文档

（归档文档已清理，如需追溯历史请查看 git log。）
