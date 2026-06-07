---
description: 影响面结构化分析：输出 affected_files/routes/apis/tests/risk_level/forbidden_touch。
agent: plan
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请基于设计文档和当前代码结构，产出结构化影响面分析 `impact.json`。

## 执行步骤

1. 读取 03-detailed-design.md / 04-frontend-detailed-design.md / 05-backend-detailed-design.md
2. 逐文件分析变更影响
3. 输出结构化的 impact.json
4. 后续 implement/review/test 命令必须读取此文件

## 输出格式

输出文件: `.vibe-workflow/tasks/<task-dir>/impact.json`

模板见: `.vibe-workflow/templates/impact.json`

## 必需字段

### affected_files（每个文件必须说明）
- `path`: 文件路径
- `change_type`: add | modify | delete
- `reason`: 为什么需要修改此文件（1 句话）
- `risk`: high | medium | low
- `tested_by`: 被哪些测试覆盖（路径）

### affected_routes（如有 API 变更）
- `method` + `path`: 完整路由
- `change_type`: new | modified | deprecated
- `breaking`: 是否 breaking change

### affected_apis（如有接口/函数签名变更）
- `function`: 函数名
- `consumers`: 调用方路径列表

### affected_tests（现有测试影响评估）
- `status`: must_update | may_break | unaffected

### forbidden_touch（严禁修改文件）
- 列出绝对不能改的文件及原因
- 示例：AGENTS.md、.opencode/opencode.json（权限相关）、锁文件等

### risk_analysis
- regression_risk: 回归风险
- security_risk: 安全风险
- performance_risk: 性能风险
- data_risk: 数据风险（DB migration / 数据格式变更）

### verification_checklist
- 按 unit/integration/e2e/manual 分类
- 每项标记 must/should/nice_to_have

## 禁止事项

- 禁止预估文件数而不实际分析代码结构
- 禁止将 forbidden_touch 置空
- 禁止 risk_analysis 全部标记 low

$ARGUMENTS
