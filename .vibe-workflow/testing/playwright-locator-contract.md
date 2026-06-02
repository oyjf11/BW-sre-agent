# Playwright Locator Contract

> vibe-dev-toolkit v3 | 所有 E2E 测试必须遵守

## 核心原则

**用户可见行为优先** — 选择器应模拟真实用户如何找到元素，而非依赖 DOM 实现细节。

## Locator 优先级（严格遵守）

| 优先级 | API | 适用场景 | 示例 |
|--------|-----|---------|------|
| 1 | `getByRole()` | 按钮、链接、输入框、表格、列表等有 ARIA role 的元素 | `page.getByRole('button', { name: '提交' })` |
| 2 | `getByLabel()` | 表单输入框（关联 label） | `page.getByLabel('用户名')` |
| 3 | `getByText()` | 用户可见文本 | `page.getByText('订单详情')` |
| 4 | `getByTestId()` | 任何需要稳定的元素 | `page.getByTestId('submit-order-btn')` |
| 5 | `getByPlaceholder()` | 有 placeholder 的输入框 | `page.getByPlaceholder('请输入手机号')` |

### 严禁使用的脆弱选择器

| 禁止 | 原因 | 替代方案 |
|------|------|---------|
| `.btn-primary` | CSS class 因 UI 重构频繁变更 | `getByRole('button', { name: '...' })` |
| `.list > li:nth-child(3)` | DOM 结构变更后断裂 | `getByRole('listitem').filter({ hasText: '...' })` |
| `//div[@class='card']//span[2]` | 深层 XPath 极其脆弱 | `getByTestId('card-title')` |
| `#userId` | id 可能因组件库 hash 变动 | `getByLabel('用户 ID')` |
| `[data-reactid]` | 框架内部属性随时变化 | `getByTestId('...')` |

## 稳定选择器契约

### 前端开发者必须提供

任何需要 E2E 覆盖的 UI 元素，必须添加 `data-testid` 属性：

```tsx
// ✅ 正确
<button data-testid="login-submit-btn" onClick={handleLogin}>登录</button>

// ✅ 正确（语义化 testid 命名）
<Table data-testid="order-list-table" ... />
<Input data-testid="search-keyword-input" ... />

// ❌ 错误：依赖 CSS class
<button className="btn btn-primary" onClick={handleLogin}>登录</button>
```

### testid 命名规范

```
{模块}-{组件}-{用途}
```

示例：`order-list-table`、`login-submit-btn`、`search-keyword-input`

### 对动态数据使用 role + name 组合

```ts
// ✅ 正确：复合定位
const row = page.getByRole('row', { name: /INC-001/ });
await row.getByRole('button', { name: '详情' }).click();

// ❌ 错误：依赖表格结构
await page.locator('table tbody tr:nth-child(2) td:nth-child(5) button').click();
```

## POM（Page Object Model）强制要求

每个页面/组件必须封装为 Page Object：

```ts
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  usernameInput = () => this.page.getByLabel('用户名');
  passwordInput = () => this.page.getByLabel('密码');
  submitBtn = () => this.page.getByRole('button', { name: '登录' });
  errorToast = () => this.page.getByRole('alert');

  async login(username: string, password: string) {
    await this.usernameInput().fill(username);
    await this.passwordInput().fill(password);
    await this.submitBtn().click();
  }
}
```

### POM 禁止事项

- 禁止在 spec 文件中直接写 `page.locator()`
- 禁止 POM 包含断言（断言属于 spec）
- 禁止 POM 方法返回 `Promise<void>` 后不提供状态查询方法

## Fixtures 规范

```ts
// fixtures/auth.fixture.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('用户名').fill(process.env.TEST_USERNAME!);
    await page.getByLabel('密码').fill(process.env.TEST_PASSWORD!);
    await page.getByRole('button', { name: '登录' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

## 存储状态（storageState）

登录态必须在 `globalSetup` 中缓存，避免每个 spec 重新登录：

```ts
// playwright.config.ts
export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  use: {
    storageState: 'tests/e2e/.auth/state.json',
  },
});
```

## Trace / Screenshot 证据保留

```ts
// playwright.config.ts — 推荐配置
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
  },
});
```

### 失败定位规范

```
测试失败时，证据查找路径：
1. test-results/{spec-name}/trace.zip  ← Playwright Trace Viewer
2. test-results/{spec-name}/test-failed-1.png  ← 失败截图
3. test-results/{spec-name}/video.webm  ← 失败录像
```

## 测试隔离

- 每个 `test()` 必须独立，不依赖其他 test 的执行顺序
- 不要在测试间共享可变状态
- 使用 `test.beforeEach()` 重置状态，不使用 `test.beforeAll()`

## 检查清单

每个 E2E spec 提交前必须通过：

- [ ] 所有选择器符合优先级表（无禁止项）
- [ ] 存在 POM，spec 中无直接 locator 调用
- [ ] 关键元素有 `data-testid`
- [ ] 登录态使用 storageState（非每个 test 重新登录）
- [ ] 配置了 `trace: 'retain-on-failure'` 和 `screenshot: 'only-on-failure'`
- [ ] 每个 test 独立可运行
