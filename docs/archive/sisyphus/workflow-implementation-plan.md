# Plan: 实现 Workflow 执行层

## 分析结果

### 问题
用户提交工单后，系统只创建了数据库记录，但没有触发 Agent Workflow 执行，导致分诊和排查从未开始。

### 根因
- 文档定义了 LangGraph 状态、节点、图构建器
- 但没有实现 "如何执行这个图"
- `create_run` API 缺少触发 workflow 的代码

---

## 需要实现的内容

### 1. 创建 Workflow 执行器
- 新建 `backend/app/graph/workflow.py`
- 实现 `run_agent_workflow()` 函数
- 按顺序执行各个节点（intake → triage → planner → evidence...）
- 支持条件路由（critic PASS/NEED_MORE_EVIDENCE）

### 2. 修改 API 触发执行
- 修改 `backend/app/api/incidents.py`
- 在 `create_run` 中调用 workflow
- 考虑同步执行或后台任务

### 3. 添加事件推送（可选，增强体验）
- 节点执行时向前端发送事件
- 支持 SSE 或轮询

---

## 预期文件变更

```
backend/app/graph/workflow.py         [新建]
backend/app/api/incidents.py         [修改]
```
