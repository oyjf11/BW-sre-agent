---
description: E2E 调试：Playwright 测试失败时，读取 trace + screenshot 定位根因。
agent: e2e-playwright-engineer
subtask: true
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

请以调试模式分析失败的 Playwright E2E 测试。

## 执行步骤

1. 运行 Playwright 测试并捕获失败（保留 trace + screenshot）
2. 从 `test-results/` 目录读取：
   - `trace.zip` — Playwright Trace Viewer
   - `test-failed-*.png` — 失败截图
   - `video.webm` — 失败录像
3. 逐帧分析 trace 中的错误时刻
4. 定位根因并给出修复建议

## 输出

```
## E2E 调试报告

### 失败测试
- 文件: {{SPEC_FILE}}
- 测试名: {{TEST_NAME}}
- 失败阶段: {{FAILURE_STAGE}}

### 根因分析
{{ROOT_CAUSE}}

### 关键证据
- trace: {{TRACE_PATH}}
- screenshot: {{SCREENSHOT_PATH}}

### 修复方案
{{FIX_SUGGESTION}}
```

## 禁止事项

- 禁止不看 trace 直接猜测
- 禁止不改 test/代码直接重跑
- 禁止把 flaky 测试标记为「偶发」而不修复定位器

$ARGUMENTS
