# E2E 测试说明

本文档用于说明当前项目中的 E2E 测试布局、运行方式、维护约定和后续扩展策略，避免前后端两套 Playwright 测试混淆。

## 总览

当前仓库里有两套 E2E 测试：

1. 根目录 `tests/e2e/`
用途：偏后端 API / 流程级验证。
配置文件：[`playwright.config.ts`](/Users/ouyangjinfeng/sre-agent/playwright.config.ts)

2. 前端 `frontend/e2e/`
用途：偏前端页面主流程冒烟。
配置文件：[`frontend/playwright.config.ts`](/Users/ouyangjinfeng/sre-agent/frontend/playwright.config.ts)

这两套都使用 Playwright，但目标不同，不要混用命令和配置。

## 一、根目录 API E2E

目录：
- [`tests/e2e/incident.create.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/incident.create.spec.ts)
- [`tests/e2e/incident.lifecycle.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/incident.lifecycle.spec.ts)
- [`tests/e2e/triage.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/triage.spec.ts)
- [`tests/e2e/evidence.collection.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/evidence.collection.spec.ts)
- [`tests/e2e/diagnose.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/diagnose.spec.ts)
- [`tests/e2e/executor.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/executor.spec.ts)
- [`tests/e2e/approval.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/approval.spec.ts)
- [`tests/e2e/events.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/events.spec.ts)
- [`tests/e2e/rca.spec.ts`](/Users/ouyangjinfeng/sre-agent/tests/e2e/rca.spec.ts)

特点：
- 面向后端接口和 graph 生命周期
- 默认使用根目录 Playwright 配置
- `webServer` 会启动后端服务
- `baseURL` 默认指向 `http://localhost:8000`

适用场景：
- 检查 `/incidents/runs`、`/approvals/*`、`/events`、`/rca` 等 API
- 检查 run 生命周期是否从 `NEW` 进入后续状态
- 检查审批、执行、RCA 等后端链路

运行方式：

```bash
npx playwright test
```

如果只跑 API 某个场景：

```bash
npx playwright test tests/e2e/approval.spec.ts
```

## 二、前端 UI Playwright 冒烟

目录：
- [`frontend/e2e/smoke-run-create.spec.ts`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/smoke-run-create.spec.ts)
- [`frontend/e2e/smoke-run-detail.spec.ts`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/smoke-run-detail.spec.ts)
- [`frontend/e2e/smoke-approval-flow.spec.ts`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/smoke-approval-flow.spec.ts)
- [`frontend/e2e/smoke-rca.spec.ts`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/smoke-rca.spec.ts)

辅助文件：
- [`frontend/e2e/fixtures/mockApi.ts`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/fixtures/mockApi.ts)
- [`frontend/e2e/README.md`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/README.md)

特点：
- 面向前端页面主流程
- 默认使用浏览器端 API mock
- 不依赖真实后端数据
- 重点验证页面跳转、tab 展示、审批入口、RCA 页面

当前覆盖链路：
1. 新建事件并跳转详情页
2. 详情页 `事件流 / 证据 / 诊断 / 方案` 四个 tab
3. `WAITING_HUMAN -> 审批页 -> 审批详情 -> 批准`
4. 从详情页进入 RCA 页面

运行方式：

```bash
cd frontend
npm install
npx playwright install
npm run test:e2e:smoke
```

如果只跑一个用例：

```bash
cd frontend
npx playwright test e2e/smoke-approval-flow.spec.ts
```

## 三、两套测试的边界

根目录 `tests/e2e/` 负责：
- API 契约
- graph 状态流转
- 后端异步处理和审批恢复
- RCA / 事件 / 证据等接口结果

前端 `frontend/e2e/` 负责：
- 页面是否能打开
- 表单是否能提交
- 路由跳转是否正确
- 页面是否正确消费接口数据
- 最近改动后的 UI 主流程是否还活着

不要让前端冒烟去承担复杂后端真实联调，也不要让根目录 API E2E 去验证页面文案或前端交互。

## 四、维护约定

### 1. 新增页面时

如果新增的是用户主路径页面，至少补 1 个前端冒烟用例：
- 页面能打开
- 核心数据能展示
- 至少一个主按钮可点击

### 2. 修改 API 返回结构时

如果修改了这些接口：
- `/incidents/runs`
- `/incidents/runs/{id}`
- `/incidents/runs/{id}/events`
- `/incidents/runs/{id}/evidence`
- `/incidents/runs/{id}/diagnosis`
- `/incidents/runs/{id}/remediation`
- `/incidents/runs/{id}/rca`
- `/approvals/pending`
- `/approvals/{id}`

需要同步更新：
- 前端类型 [`frontend/src/types/index.ts`](/Users/ouyangjinfeng/sre-agent/frontend/src/types/index.ts)
- 前端服务 [`frontend/src/services/runs.ts`](/Users/ouyangjinfeng/sre-agent/frontend/src/services/runs.ts)
- 前端 E2E mock [`frontend/e2e/fixtures/mockApi.ts`](/Users/ouyangjinfeng/sre-agent/frontend/e2e/fixtures/mockApi.ts)
- 相关 API E2E

### 3. 修改审批/恢复/执行链路时

至少更新两类测试：
- 根目录 API E2E：验证审批和恢复接口行为
- 前端 UI 冒烟：验证 `WAITING_HUMAN` 页面入口和审批跳转

这是本项目高风险区域，不能只改单测不改 E2E。

### 4. 修改详情页 tab 或组件时

如果动了这些页面或组件：
- [`frontend/src/pages/RunDetailPage.tsx`](/Users/ouyangjinfeng/sre-agent/frontend/src/pages/RunDetailPage.tsx)
- [`frontend/src/pages/ApprovalsPage.tsx`](/Users/ouyangjinfeng/sre-agent/frontend/src/pages/ApprovalsPage.tsx)
- [`frontend/src/pages/ApprovalDetailPage.tsx`](/Users/ouyangjinfeng/sre-agent/frontend/src/pages/ApprovalDetailPage.tsx)
- [`frontend/src/pages/RcaPage.tsx`](/Users/ouyangjinfeng/sre-agent/frontend/src/pages/RcaPage.tsx)

要优先检查：
- 按钮文本是否变了
- 路由是否变了
- tab 名称是否变了
- mock 数据是否仍能驱动页面渲染

## 五、推荐执行顺序

日常开发建议按这个顺序跑：

1. 单元测试

```bash
cd backend && pytest app/tests/ -q
cd frontend && npm run test
```

2. 前端冒烟

```bash
cd frontend && npm run test:e2e:smoke
```

3. 根目录 API E2E

```bash
npx playwright test
```

如果只是改了页面展示，通常跑到第 2 步即可。
如果改了审批、恢复、graph、API 契约，必须至少跑到第 3 步。

## 六、后续扩展建议

### 短期

- 给前端冒烟补一个真实接口模式，不只走 mock
- 给 `RunCreatePage` 的 `ticket_id` / `alert_event` 两种模式各补 1 个用例
- 给 RCA 页补“空态 / pending 态 / error 态”

### 中期

- 把前端 E2E 的 mock 数据从单文件拆成按领域组织
- 给审批链路增加 `rejected`、`modify`、`more_evidence` 三个 UI 用例
- 给 run detail 加一个 SSE / polling 降级场景

### 长期

- 将前端 E2E 接入 CI
- 将根目录 API E2E 和前端 UI E2E 分成两个独立 job
- 对真实 `TOOL_ADAPTER_MODE=real` 增加单独的受控联调环境

## 七、当前已知限制

- 前端 Playwright 还依赖本地安装 `@playwright/test` 和浏览器二进制
- 前端 UI 冒烟默认走 mock，不代表真实后端联调已经验证
- 根目录 API E2E 目前更偏“接口存在与流程基本可走通”，不是严格的生产级验收

## 八、维护者快速检查清单

每次改动 E2E 相关代码后，至少自查：

- 是否改了路由路径
- 是否改了按钮/标题文案，导致定位器失效
- 是否改了接口字段，导致 mock 数据失真
- 是否改了审批/恢复逻辑，导致 UI 和 API E2E 都要同步
- 是否区分清楚根目录 Playwright 配置和 `frontend/playwright.config.ts`

如果不确定该更新哪一层，默认两层都检查。
