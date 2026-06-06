# 知识沉淀

## 关键设计决策

- specialist agent_id 不能从 category 简单拼接，应由集中映射维护。
- 图集成测试开启 specialist pool 时必须 stub 同步和异步 LLM，否则测试会受外部网络与模型行为影响。
- 后端单元测试默认应隔离本地 `.env`，特别是 `TOOL_ADAPTER_MODE=real` 这种会触达线上只读接口的配置。

## 踩坑

- `from app.tools import gateway` 取到的是全局 gateway 实例，不是 `app.tools.gateway` 模块；读取 `ADAPTER_MODE` 应使用 `importlib.import_module("app.tools.gateway")`。
- P0 失败表现有不稳定性：真实 async LLM 若在第一轮前失败会进入 `NEEDS_HUMAN`，若先产出部分证据则进入 `COMPLETED`，但根因都是 deployments 证据缺失导致无法生成高风险 rollback 审批。
- Python 3.9 没有内置 `anext()`。

## 下次可复用检查清单

- 新增 graph task generator 后，检查生成 ID 是否能命中配置文件。
- 开启 feature flag 的集成测试必须显式 stub 新增外部边界。
- 测试里默认 mock 的断言必须由夹具保证，不能依赖开发机 `.env`。
- 运行全套测试时记录 focused、backend full、frontend test/build/lint 的结果和差异。

## 应写入长期规则

- 后端 pytest 默认强制 `TOOL_ADAPTER_MODE=mock`；真实 adapter 测试必须显式 opt-in。
- specialist pool 的 category 与 agent_id 映射应使用 `agent_id_for_category()`。

## 可沉淀成 Skill 的流程

- “graph feature flag 回归排查”：固定 LLM/tool adapter 边界，比较 feature flag 开关前后的 state 关键字段，包括 `agent_tasks`、`specialist_analyses`、`evidence_items`、`remediation_plan`、`risk_decision`。

## 架构与测试建议

- 后续可在 `_evidence_fanout_v2()` 增加更明确的配置缺失事件，避免 agent_id miss 只表现为静默降级。
- 前端 lint 已存在多处历史错误，建议单独开任务处理，不与后端回归修复混在一起。

