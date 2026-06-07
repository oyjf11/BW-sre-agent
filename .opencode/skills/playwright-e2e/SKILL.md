---
name: playwright-e2e
description: Playwright 端到端测试技能，从真实用户旅程验证完整业务闭环。强制遵守 Locator Contract。
license: MIT
compatibility: opencode
metadata:
  toolkit: vibe-dev-toolkit
  version: v3
---

## 何时使用

需要验证浏览器中的真实用户路径时使用。

## 何时不用

- 纯后端 API 变更（无 UI 变更）
- 纯配置/文档变更
- task_size == XS 且无 UI 变更（由 test-selection.yaml 判定 skip）

## 设计步骤

1. 明确用户角色和入口。
2. 准备测试数据。
3. 处理登录态（优先 storageState，不要每个 test 重新登录）。
4. 编写稳定选择器（严格遵守 Locator Contract）。
5. 执行用户动作。
6. 断言页面和数据结果。
7. 配置截图/trace/video（failure 时保留证据）。
8. 输出失败定位建议。

## Locator Contract（强制）

详见 `.vibe-workflow/testing/playwright-locator-contract.md`

### 选择器优先级

1. `getByRole()` — 最高优先级
2. `getByLabel()` — 表单输入
3. `getByText()` — 用户可见文本
4. `getByTestId()` — 需要稳定锚点
5. `getByPlaceholder()` — 输入框有 placeholder 时

### 禁止使用的脆弱选择器

| 禁止 | 替代 |
|------|------|
| CSS class (`.btn-primary`) | `getByRole()` |
| `nth-child` | `filter({ hasText: ... })` |
| 深层 XPath | `getByTestId()` |
| `data-reactid` 等框架内部属性 | `getByTestId()` |

### POM（Page Object Model）

每个页面/组件必须封装为 POM，spec 文件中禁止直接使用 `page.locator()`。

```ts
class LoginPage {
  constructor(private page: Page) {}
  usernameInput = () => this.page.getByLabel('用户名');
  submitBtn = () => this.page.getByRole('button', { name: '登录' });
  async login(u: string, p: string) { /* ... */ }
}
```

### 测试隔离

- 每个 `test()` 独立，不依赖执行顺序
- 使用 `test.beforeEach()` 而非 `test.beforeAll()`

## 运行命令示例

```bash
npx playwright test
npx playwright test tests/e2e/login.spec.ts --headed
npx playwright show-report
npx playwright test --trace on  # 查看 trace
```

## 质量闸门

- [ ] 无禁止类选择器
- [ ] 存在 POM
- [ ] 关键元素有 `data-testid`
- [ ] 登录态使用 storageState
- [ ] 配置 trace + screenshot on failure
- [ ] 每个 test 独立

## Anti-patterns

- 在 spec 中直接写 `page.locator('.btn')`
- 依赖 DOM 顺序（`first()`, `nth()`）
- 每个 test 重新登录
- POM 中包含断言
- 测试间共享可变状态

## Handoff

完成后输出 E2E 报告到 `.vibe-workflow/tasks/<task-dir>/09-e2e-playwright-report.md`。

同时确保：
- trace 文件路径清晰
- 失败截图路径清晰
- 下一步建议明确（如有失败）
