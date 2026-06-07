---
name: implementation-slice
description: 代码实现切片技能，按已批准设计执行一个最小垂直切片并完成验证。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---


## 何时使用

设计已明确，需要开始写代码时使用。

## 执行步骤

1. 读取设计文档。
2. 选择一个最小垂直切片。
3. 明确本次修改文件和禁止修改文件。
4. 实现代码。
5. 补充测试。
6. 运行验证命令。
7. 输出结果和风险。

## 垂直切片示例

- 一个 API + 一个页面调用 + 一个测试。
- 一个表单校验规则 + 一个组件测试 + 一个 E2E 断言。
- 一个 Bug 根因修复 + 一个回归测试。

## 禁止事项

- 禁止顺手重构。
- 禁止一次性做完整大需求。
- 禁止测试失败仍声称完成。

