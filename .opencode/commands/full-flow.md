---
description: [DEPRECATED] 请使用 /vibe-full-flow
agent: plan
deprecated: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
  replaced_by: vibe-full-flow
---

请使用 `stage-gate-workflow` skill。

输入需求：

$ARGUMENTS

请按以下阶段生成完整执行路线图：
1. 需求采集/澄清
2. 需求设计
3. 详细设计
4. 前端详细设计
5. 后端详细设计
6. 代码编写
7. 前后端单元测试
8. 集成测试
9. Playwright E2E
10. 知识沉淀

默认只输出路线图和阶段产物，不直接改代码。
每个阶段必须包含：输入、输出、执行 Agent、推荐命令、验收标准、风险点。
