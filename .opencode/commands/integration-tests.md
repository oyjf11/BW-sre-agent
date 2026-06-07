---
description: [DEPRECATED] 请使用 /vibe-integration-tests
agent: integration-test-engineer
subtask: true
deprecated: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
  replaced_by: vibe-integration-tests
---

请使用 `integration-test-design` skill。

要求：
1. 识别需要真实协作的模块。
2. 设计成功路径、权限失败、参数错误、数据不存在、重复提交、外部依赖失败。
3. 优先 mock 不稳定外部系统，保留核心链路真实验证。
4. 写完后运行集成测试命令。
5. 输出测试报告和剩余风险。
