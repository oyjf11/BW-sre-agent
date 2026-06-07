---
description: E2E trace 回放：打开 Playwright Trace Viewer，逐步骤回放定位根因。
agent: e2e-playwright-engineer
subtask: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请打开 Playwright Trace Viewer 并逐步骤分析。

## 执行步骤

1. 找到最近的 trace 文件：
   ```
   ls test-results/*/trace.zip
   ```
2. 打开 Trace Viewer：
   ```
   npx playwright show-trace test-results/<dir>/trace.zip
   ```
3. 逐步骤检查：
   - 哪个 action 失败？
   - 失败前的页面状态是什么？
   - 选择器是否匹配到元素？
   - 是否有网络错误？
   - 超时发生在哪个阶段？

## 输出

```
## Trace 回放报告

### 执行时间线
| 步骤 | Action | 目标 | 耗时 | 结果 |
|------|--------|------|------|------|
| 1 | goto | /login | 200ms | ✅ |
| 2 | fill | 用户名 | 50ms | ✅ |
| 3 | click | 登录按钮 | 5001ms | ❌ timeout |

### 失败根因
{{ROOT_CAUSE}}

### 修复建议
{{FIX_SUGGESTION}}
```

## 禁止事项

- 禁止跳步分析
- 禁止不看 DOM snapshot

$ARGUMENTS
