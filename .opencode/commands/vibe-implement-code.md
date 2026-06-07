---
description: 代码编写：只按设计文档执行一个最小垂直切片。
agent: implementation-engineer
subtask: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v2
---

请使用 `implementation-slice` skill。

任务参数：

$ARGUMENTS

执行规则：
1. 先读取需求/设计/详细设计/前后端设计产物。
2. 只执行一个最小垂直切片。
3. 实现前列出：目标、修改文件、不修改文件、验收方式。
4. 不做计划外重构。
5. 改完后运行可用的 lint/typecheck/test/build 命令。
6. 输出修改摘要、测试结果、风险、下一步。
