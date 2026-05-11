# OpsPilot Agent - 编码指南

> 所有 AI 编码助手（Qwen/Claude/Codex 等）启动时必读。用中文回复用户。

## 项目一句话介绍

OpsPilot 是一个 SRE 故障处置智能体，使用 LangGraph 编排 13 个节点的工作流：
intake -> triage -> retrieve_memory -> planner -> evidence_fanout -> evidence_aggregate -> diagnose -> critic -> remediation -> risk_gate -> approval_interrupt/executor -> verify -> rca

## 启动命令

```bash
# 后端
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm run dev

# 后端测试
cd backend && pytest app/tests/ -x -q

# 前端测试
cd frontend && npx vitest run

# 健康检查（注意是 /healthz 不是 /health）
curl http://127.0.0.1:8000/healthz
```

## 关键 API 契约（必读，避免 422）

### POST /incidents/runs 创建工单

三种模式互斥，必须且只能提供一种：

**模式 A：手工工单（所有字段必填）**
```json
{
  "ticket": {
    "ticket_id": "INC-001",
    "title": "支付服务5xx升高",
    "description": "发布后部分用户下单失败",
    "service": "payment-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  }
}
```

**模式 B：ticket_id 拉取**
```json
{ "ticket_id": "INC-001" }
```

**模式 C：告警事件**
```json
{
  "alert_event": {
    "alert_name": "HighErrorRate",
    "service": "payment-service",
    "env": "staging",
    "severity": "P2"
  }
}
```

### 审批 API

```bash
# 查看待审批
GET /approvals/pending

# 审批决策
POST /approvals/{approval_id}/decision
{ "decision": "approved", "comment": "ok", "approver": "human" }
```

## 已知陷阱（Qwen/所有 Agent 必读）

### 1. Pydantic 对象 vs dict 二义性

**graph state 中的对象可��是 Pydantic 模型，也可能是 dict**（从 checkpoint 反序列化后变成 dict）。访问属性时必须兼容两种形式：

```python
# 错误写法
service = ticket.service  # 如果 ticket 是 dict 会崩溃

# 正确写法
service = ticket.service if hasattr(ticket, 'service') else ticket.get('service', 'unknown')
```

同理，遍历 list 中的元素时要防 None：
```python
for a in actions:
    if a is None:
        continue
    if isinstance(a, dict):
        action_type = a.get("action_type")
    else:
        action_type = a.action_type
```

### 2. Evidence 持久化

evidence_items 存在于 graph state 内存中，通过 GraphRunner._persist_evidence() 在每个节点完成后写入 DB。如果新增节点产生 evidence，确保它 append 到 state["evidence_items"]，GraphRunner 会自动处理持久化。

### 3. LLM 配置

- 默认 LLM_PROVIDER=minimax，需要 MINIMAX_API_KEY + MINIMAX_GROUP_ID
- 可切换为 openai，需要 OPENAI_API_KEY
- dev 环境不强制校验 key，但 LLM 调用会失败
- LLM 调用失败时节点应有 fallback 逻辑，不能让整个 graph 崩溃

### 4. Tool Adapter 模式

- 默认 TOOL_ADAPTER_MODE=mock，使用 mock 适配器返回仿真数据
- 真实适配器尚未实现（MySQL/K8s/SLB/OSS）
- 切换方式：在 backend/.env 设置 TOOL_ADAPTER_MODE=real

### 5. 前端类型与后端对齐

前端类型定义在 `frontend/src/types/index.ts`，后端 response 模型在 `backend/app/api/incidents.py`。修改 API 返回结构时必须同步更新前端类型。

## 关键文件速查

| 文件 | 用途 |
|------|------|
| `backend/app/graph/builder.py` | LangGraph 图构建（节点、边、条件路由） |
| `backend/app/graph/state.py` | IncidentAgentState 定义（TypedDict） |
| `backend/app/graph/nodes/__init__.py` | 所有 13 个图节点实现（~1200 行） |
| `backend/app/api/incidents.py` | Incidents API 路由 |
| `backend/app/api/approvals.py` | Approvals API 路由 |
| `backend/app/services/graph_runner.py` | 图执行器（事件、checkpoint、evidence 持久化） |
| `backend/app/services/executor.py` | ControlledExecutor（幂等执行 + 审计） |
| `backend/app/tools/gateway.py` | Tool Gateway（schema 校验、重试、审计） |
| `backend/app/tools/adapters/__init__.py` | 11 个 mock 适配器 |
| `backend/app/core/config.py` | Settings（环境变量配置） |
| `backend/app/llm_client.py` | LLM 客户端（OpenAI + MiniMax） |
| `frontend/src/pages/RunDetailPage.tsx` | 运行详情页（Stepper + Tabs） |
| `frontend/src/types/index.ts` | 前端类型定义 |
| `frontend/src/services/runs.ts` | Runs API 封装 |

## 调试 graph 执行

当 run 失败时，按这个顺序排查：

```bash
# 1. 查看 run 状态（注意 current_node 字段，表示卡在哪）
curl -s http://127.0.0.1:8000/incidents/runs/{run_id} | python3 -m json.tool

# 2. 查看事件流（找 ERROR 级别��事件）
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/events | \
  python3 -c "import sys,json; [print(f'[{e[\"level\"]}] {e[\"type\"]:20s} {e.get(\"node_name\",\"\"):30s} {e.get(\"message\",\"\")[:120]}') for e in json.load(sys.stdin)]"

# 3. 查看证据（如果为空说明 evidence_fanout 有问题）
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/evidence | python3 -m json.tool

# 4. 查看诊断结果
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/diagnosis | python3 -m json.tool

# 5. 查看修复方案
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/remediation | python3 -m json.tool
```

## 当前进度

详见 ACTION_PLAN.md。已完成 Phase 1-2-4，当前执行 Phase 3（全链路验证）。

## 编码规范

- Python: 4 空格缩进，snake_case，Ruff 100 字符行宽
- TypeScript: 2 空格缩进，PascalCase 组件名，semicolons
- 测试文件命名：Python `test_*.py`，TS `*.test.ts(x)`
- commit 信息格式：`backend: xxx` 或 `frontend: xxx`
- 不要提交 .env、*.db、node_modules、venv
