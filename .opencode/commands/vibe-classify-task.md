---
description: 任务分档：根据需求自动判定 XS/S/M/L 并推荐最简流程。小任务不默认跑全流程。
agent: plan
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请分析当前任务，输出 `task-classification.yaml`。

## 分档规则（严格遵守）

### XS（微任务）
触发条件（满足 ≥3 条）：
- 预计修改 1 个文件
- 不涉及 API 变更
- 不涉及 DB schema
- 不涉及 UI 变更
- 纯文案/配置/注释/拼写修复
- Bug 修复只改一行逻辑

→ **最短流程: clarify → implement → review**（3 阶段）
→ 允许合并: clarify + implement 一步完成

### S（小任务）
触发条件（满足 ≥3 条）：
- 预计修改 2-5 个文件
- 单一模块内变更
- 最多 1 个新 API 或 1 个 UI 组件
- 不新增 DB 表（可新增字段）
- 不变更权限模型

→ **最短流程: clarify → design → implement → unit-tests → review**（5 阶段）
→ 允许合并: design + detailed

### M（中任务）
触发条件（满足 ≥3 条）：
- 预计修改 5-15 个文件
- 跨 2-3 个模块
- 新增 API + 前端页面
- 可能涉及 DB migration
- 需要集成测试

→ **最短流程: clarify → design → detailed → implement → unit → integration → review**（7 阶段）
→ 前端/后端设计可并行但必须分别产出

### L（大任务）
触发条件（满足 ≥3 条）：
- 预计修改 15+ 个文件
- 跨 3+ 个模块
- 新增子系统/子域
- DB migration + 权限模型变更
- 需要架构评审

→ **完整流程: 全部 11 阶段**
→ 不允许合并阶段

## 输出

输出文件: `.vibe-workflow/tasks/<task-dir>/task-classification.yaml`

必须包含：
- `dimensions`: 10 个维度的估计值
- `size`: XS/S/M/L
- `confidence`: 置信度
- `recommended_flow`: 推荐阶段列表（标记哪些必跑、哪些可跳过及原因）
- `merge_allowed`: 是否允许合并阶段
- `rationale`: 分类理由（2-3 句）

## 禁止事项

- 禁止 XS/S 任务推荐全流程 11 阶段
- 禁止跳过分类直接进入实现
- 禁止仅凭情感判断分档，必须基于维度

$ARGUMENTS
