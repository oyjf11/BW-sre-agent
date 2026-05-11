# Playwright Smoke Tests

当前这组 Playwright 用例面向前端主流程冒烟，默认走浏览器端 API mock，不依赖真实后端数据。

覆盖范围：

- `smoke-run-create.spec.ts`
- `smoke-run-detail.spec.ts`
- `smoke-approval-flow.spec.ts`
- `smoke-rca.spec.ts`

运行方式：

```bash
cd frontend
npm install
npx playwright install
npm run test:e2e:smoke
```

如果要切到真实接口联调：

1. 启动前端和后端服务
2. 移除或替换 `e2e/fixtures/mockApi.ts` 的路由 mock
3. 将 `playwright.config.ts` 中的 `VITE_API_URL` 指向真实后端
