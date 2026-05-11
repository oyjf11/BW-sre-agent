# OpsPilot Frontend

OpsPilot 前端是基于 React + TypeScript + Vite 的故障处置控制台，用于创建工单、查看运行详情、处理审批和查看 RCA 报告。

## 主要页面

- `/`：运行列表与概览
- `/runs/new`：创建故障工单
- `/runs/:id`：运行详情，包含事件、证据、诊断和修复方案
- `/runs/:id/rca`：RCA 报告
- `/approvals`：待审批列表
- `/approvals/:id`：审批详情与决策

## 启动

```bash
cd frontend
npm install
npm run dev
```

默认开发服务由 Vite 启动。后端地址通过前端服务层配置读取，联调时确认后端已在 `http://127.0.0.1:8000` 启动。

## 测试

```bash
cd frontend
npm run test
npm run test:e2e:smoke
```

单元测试使用 Vitest + React Testing Library。前端 E2E 使用 Playwright，默认通过 `frontend/e2e/fixtures/mockApi.ts` 在浏览器端 mock API，不依赖真实后端。

## 修改 API 时必须同步

后端响应结构变更时，至少检查：

- `frontend/src/types/index.ts`
- `frontend/src/services/runs.ts`
- `frontend/src/services/approvals.ts`
- `frontend/e2e/fixtures/mockApi.ts`
- 相关页面和组件测试

更完整的 E2E 边界说明见根目录 `E2E_TESTING.md`。
