---
description: [DEPRECATED] 请使用 /vibe-review-diff
agent: code-reviewer
subtask: true
deprecated: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
  replaced_by: vibe-review-diff
---

请使用 `review-and-risk-control` skill。

只读审查当前变更：

!`git status --short`

!`git diff --stat`

!`git diff`

禁止修改文件。

输出：
- 必须修复
- 建议优化
- 可接受风险
- 测试缺口
- 是否可以进入下一阶段
