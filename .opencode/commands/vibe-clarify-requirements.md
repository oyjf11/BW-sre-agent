---
description: 需求采集与需求澄清：把模糊需求转成可执行需求说明。
agent: req-analyst
subtask: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v2
---

请使用 `requirements-clarification` skill。

输入需求：

$ARGUMENTS

要求：
1. 不写代码。
2. 先识别业务目标、用户角色、核心场景。
3. 把需求拆成：目标、非目标、功能、规则、边界、验收标准、待确认问题。
4. 信息不足时给出合理默认假设，不要中断流程。
5. 输出可保存到：`.vibe-workflow/tasks/<date>-<slug>/01-requirements-clarification.md`。
