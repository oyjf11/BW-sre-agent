---
description: [DEPRECATED] 请使用 /vibe-learn
agent: knowledge-curator
subtask: true
deprecated: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
  replaced_by: vibe-learn
---

请使用 `knowledge-capture` skill。

基于本次任务文档、git diff、测试结果和 review 结论，输出知识沉淀文档。

必须包含：
1. 关键设计决策
2. 改进意见
3. 踩坑与根因
4. 可复用检查清单
5. 应写入 AGENTS.md 的长期规则
6. 应新增/更新的 Skill
7. 后续架构演进建议

可保存到：`.vibe-workflow/tasks/<date>-<slug>/10-knowledge-capture.md`。
