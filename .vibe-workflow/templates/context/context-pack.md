# Context Pack: {{TASK_SLUG}}

> 生成时间: {{TIMESTAMP}} | 生成方式: vibe-build-context.sh
> 原则：只含任务必要信息，不复制大段源码。引用路径即可。

## 1. 任务标识

| 字段 | 值 |
|------|-----|
| task_id | {{TASK_ID}} |
| slug | {{TASK_SLUG}} |
| type | {{TASK_TYPE}} |
| size | {{TASK_SIZE}} |
| status | {{TASK_STATUS}} |

## 2. 需求摘要

<!-- 300 字内，只写核心目标和边界 -->

{{REQUIREMENTS_SUMMARY}}

## 3. 关键设计决策

<!-- 每个决策一行：选择 + 理由 + 替代方案 -->

| # | 决策 | 理由 | 替代方案（弃用原因） |
|---|------|------|---------------------|
| 1 | {{DECISION}} | {{RATIONALE}} | {{ALTERNATIVES}} |

## 4. 受影响文件

<!-- 只列路径，不复制内容 -->

### 需修改
{{AFFECTED_FILES}}

### 禁止触碰
{{FORBIDDEN_FILES}}

## 5. 当前状态

| 已完成阶段 | 产物路径 | 通过闸门 |
|------------|---------|---------|
| {{STAGE_NAME}} | {{ARTIFACT_PATH}} | {{GATE_PASSED}} |

### 当前阻塞
{{BLOCKERS}}

### 下一步
{{NEXT_STEPS}}

## 6. 关键约束

- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}

## 7. 风险备忘

| 风险 | 等级 | 缓解 |
|------|------|------|
| {{RISK}} | {{LEVEL}} | {{MITIGATION}} |

## 8. 相关链接

- 设计文档: {{DESIGN_DOC_PATH}}
- impact.json: {{IMPACT_PATH}}
- test-selection.yaml: {{TEST_SELECTION_PATH}}
