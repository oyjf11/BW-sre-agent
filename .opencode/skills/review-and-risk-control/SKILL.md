---
name: review-and-risk-control
description: 审查与风险控制技能，只读检查 diff 的正确性、范围、风险、测试缺口和是否可进入下一阶段。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v1
---


## 何时使用

每个实现切片完成后使用。必须只读，不修改文件。

## 审查维度

- 需求满足度
- 修改范围是否失控
- 架构一致性
- 类型安全
- 空值和异常
- 并发和幂等
- 权限和安全
- 测试充分性
- 文档/知识沉淀需求

## 输出格式

```markdown
# Code Review

## 结论
- 是否通过：是/否

## 必须修复

## 建议优化

## 可接受风险

## 测试缺口

## 下一步
```

