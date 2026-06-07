---
description: 测试选择：根据 impact.json 和 git diff 精确判定 must_run/should_run/skip。
agent: plan
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请基于 impact.json、git diff 和 package.json，产出精确的测试选择计划。

## 前置条件

必须先产出：
- `impact.json`（来自 /vibe-impact）
- `task-classification.yaml`（来自 /vibe-classify-task）

## 执行步骤

1. 读取 impact.json，提取 `affected_files`、`affected_apis`、`affected_routes`
2. 执行 `git diff --name-only HEAD` 获取实际变更文件
3. 读取 package.json 获取可用测试命令
4. 扫描项目测试目录，匹配测试文件与变更文件的关联
5. 按选择规则引擎分类输出

## 输出

输出文件: `.vibe-workflow/tasks/<task-dir>/test-selection.yaml`

模板见: `.vibe-workflow/templates/test-selection.yaml`

## 选择规则

### must_run（必须跑，失败阻塞后续）
- 测试文件的源文件出现在 git diff 中
- 被修改 API 的消费者测试
- 被修改路由的 E2E spec
- regression_risk == high → 全模块测试 must_run

### should_run（建议跑，失败不阻塞）
- 同一模块内但非直接修改文件的测试
- 共享 util/helper 被修改，所有消费者测试
- 被标记 affected_tests.status == may_break

### skip（跳过，附原因）
- 测试文件所在模块完全不在 impact.affected_files 中
- task_size == XS 且非直接关联
- 项目无对应测试脚本（如无 playwright config → skip E2E）

## 禁止事项

- 禁止无理由全量测试（must_run 全部测试）
- 禁止无理由跳过测试（skip 全部测试）
- 禁止 skip_all_reason 为空字符串
- 禁止不读取 impact.json 就开始执行

## 输出要求

每个 test group（backend_unit / frontend_unit / integration / e2e）必须分别评估。
如果某个 group 全部 skip，填 `skip_all_reason`。
如果项目不存在某个 group 的测试脚本，填 `skip_all_reason: "项目无对应测试命令"`。

$ARGUMENTS
