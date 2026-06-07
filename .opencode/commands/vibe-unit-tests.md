---
description: 前后端单元测试：补充核心业务规则、边界、异常和回归测试。
agent: unit-test-engineer
subtask: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v2
---

请使用 `unit-test-generation` skill。

要求：
1. 先识别前端和后端的核心逻辑。
2. 优先覆盖业务规则、边界条件、异常路径、权限判断、数据转换。
3. 不为了覆盖率写无意义测试。
4. 写完后运行对应单元测试命令。
5. 输出测试文件、测试场景、断言点、运行结果和失败根因。
