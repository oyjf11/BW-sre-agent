---
description: Skill 路由：根据 task-classification 精确判定 required/optional/skip skills。
agent: plan
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请读取 `task-classification.yaml`，为每个 skill 判定路由并输出 `skill-routing.yaml`。

## 执行步骤

1. 读取 `.vibe-workflow/tasks/<task-dir>/task-classification.yaml`
2. 以 `task_size`、`task_type`、各维度值作为输入
3. 对每个 skill 输出路由决策
4. 严格遵守路由规则引擎
5. 禁止无理由加载全部 skills

## 输出

输出文件: `.vibe-workflow/tasks/<task-dir>/skill-routing.yaml`

格式见模板: `.vibe-workflow/templates/skill-routing.yaml`

## 路由决策规则

### 检查清单（必答）

对每个 skill 回答以下问题：

1. 该 task 是否需要此 skill？为什么？
2. 是否可被其他 skill 覆盖？（是 → optional）
3. 是否存在明确的 skip 条件？（是 → skip）
4. 任务大小是否建议省略此 skill？（XS/S → skip 大部分设计/测试 skills）

### 默认路由表（严格遵守，除非有 strong override）

| Skill | XS | S | M | L |
|-------|----|---|---|---|
| requirements-clarification | optional | required | required | required |
| requirements-design | skip | required | required | required |
| technical-detailed-design | skip | skip | required | required |
| frontend-detailed-design | skip | skip | optional | required |
| backend-detailed-design | skip | skip | optional | required |
| implementation-slice | required | required | required | required |
| unit-test-generation | skip | optional | required | required |
| integration-test-design | skip | skip | required | required |
| playwright-e2e | skip | skip | optional | required |
| review-and-risk-control | required | required | required | required |
| stage-gate-workflow | skip | skip | skip | skip |
| knowledge-capture | skip | skip | optional | required |

### 特殊覆盖

- Bug 修复 + XS/S：跳过 requirements-clarification、requirements-design
- 纯后端（无 UI 变更）：跳过 frontend-detailed-design、playwright-e2e
- 无 API/DB 变更：跳过 integration-test-design
- 配置/文档类：只保留 review-and-risk-control，其余全部 skip

## 禁止事项

- 禁止全部 skills 标记为 required
- 禁止缺少每个 skill 的路由理由
- 禁止跳过路由直接进入实现阶段

$ARGUMENTS
