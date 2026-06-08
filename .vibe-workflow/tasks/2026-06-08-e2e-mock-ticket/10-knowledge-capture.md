# 知识沉淀

## 关键设计决策

- 使用进程级环境变量覆盖 `TOOL_ADAPTER_MODE=mock`，不修改 `.env`。
- 使用本任务目录下的临时 SQLite 数据库，避免污染现有开发数据库。
- 第一轮保留当前 `.env` 的 specialist pool 行为，用于验证默认配置风险。
- 第二/三轮关闭 specialist pool，用于验证稳定 happy path。

## 踩坑与绕路

- zsh 中未加引号的 URL query string 会被 `?` 当成 glob，后续 curl 需要加引号或避免 query string。
- zsh 的 `status` 是只读变量，轮询脚本不要使用 `status=`。
- specialist pool 的异常只出现在服务日志，没有同步成 run ERROR event。
- `prod/P2` 不一定触发审批，审批是否出现取决于 remediation action 的 `risk_level` 和 `requires_approval`。

## 下次复用检查清单

- 启动前确认 8000 端口和 `/healthz`。
- 明确记录 `TOOL_ADAPTER_MODE`、`AGENT_FEATURE_SPECIALIST_POOL`、数据库路径。
- 每个 run 固定采集：run、events、evidence、diagnosis、remediation、actions、rca、trace、approvals。
- 同时看 run events 和后端日志，不能只依赖 events 判断 LLM/tool 异常。
- 如果要覆盖审批分支，需要准备一个确定会生成 `requires_approval=true` 或高风险 action 的 fixture。

## 建议写入长期规则

- E2E smoke 测试应默认使用临时数据库和 mock adapter，除非明确做 real adapter 验收。
- 审批分支 E2E 需要固定测试入口或 fixture，不能依赖 LLM 自由生成高风险动作。
- specialist pool 的内部 LLM/tool 失败应映射到可查询事件或 trace error，便于 API 侧排障。

## 可沉淀成 Skill 的流程

- OpsPilot API E2E smoke：启动临时 DB 后端、创建模拟工单、轮询状态、处理审批、采集完整证据包、生成报告。

## 架构/测试改进建议

- 增加 deterministic E2E fixture：强制 remediation 生成高风险 action，用于覆盖 approval resume。
- 为 specialist pool 子任务增加事件上报，至少记录 WARN/ERROR 到 run events。
- 修复 RCA markdown 中 action type 显示为 `unknown` 的问题。
- 定位全量 pytest 长耗时/挂起用例，并补充分组测试脚本。

