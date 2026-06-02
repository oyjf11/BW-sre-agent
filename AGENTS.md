# OpsPilot Agent — 编码指南 + 工程化开发总规则

> 所有 AI 编码助手（Qwen/Claude/Codex 等）启动时必读。用中文回复用户。

## 总原则

1. **先理解，再计划，再修改。** 不允许在需求不清、影响面不清、验收标准不清的情况下直接改代码。
2. **小步闭环。** 每次只完成一个可验证的最小垂直切片。
3. **测试与实现同步。** 新功能、重构、修复都必须补充或更新测试。
4. **禁止计划外重构。** 除非任务明确要求，否则不要顺手重构无关模块。
5. **禁止隐式扩大范围。** 修改范围必须与任务设计文档一致。
6. **所有结论必须可追溯。** 关键判断要说明依据：文件、接口、测试结果、日志或现有约定。
7. **人类拥有最终决策权。** 任何破坏性操作、依赖升级、数据库迁移、接口协议变更必须先说明风险并请求确认。

## 项目一句话介绍

OpsPilot 是一个 SRE 故障处置智能体，使用 LangGraph 编排 14 个节点的工作流：
intake -> triage -> retrieve_memory -> planner -> evidence_fanout -> evidence_aggregate -> diagnose -> critic -> remediation -> risk_gate -> approval_interrupt/executor -> verify -> rca

## 启动命令

```bash
# 后端
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# 前端
cd frontend && npm run dev

# 后端测试
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q

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

**graph state 中的对象可能是 Pydantic 模型，也可能是 dict**（从 checkpoint 反序列化后变成 dict）。访问属性时必须兼容两种形式：

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
- 可切换为 deepseek，需要 DEEPSEEK_API_KEY；模型通过 DEEPSEEK_MODEL 配置
- dev 环境不强制校验 key，但 LLM 调用会失败
- LLM 调用失败时节点应有 fallback 逻辑，不能让整个 graph 崩溃

### 4. Tool Adapter 模式

- 默认 TOOL_ADAPTER_MODE=mock，使用 mock 适配器返回仿真数据
- 真实适配器进度：已实现 MySQL 诊断、MySQL 应用日志 `query_logs`、K8s 只读、`query_metrics`（阿里云 CMS/K8s 指标）、`query_deployments`（K8s deployment 列表与状态）、SLB 健康/流量、OSS RCA/evidence 写归档
- `query_ticket_by_id` / `query_service_metadata` / `query_runbook` / `execute_action` 在 real 模式下均 fail-closed（抛出 RuntimeError），需实现真实 adapter 后才能使用；RAG 检索走 `backend/app/rag/`，执行动作仍需人工审批与受控接入
- 切换方式：在 backend/.env 设置 TOOL_ADAPTER_MODE=real（gateway.py 从 Settings 对象读取，而非 os.getenv，避免配置漂移）

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
| `backend/app/tools/adapters/__init__.py` | mock 适配器集合 |
| `backend/app/rag/` | RAG 索引、检索、rerank、写回 |
| `backend/app/tracing.py` | 本地 tracing span/event 记录 |
| `backend/app/core/config.py` | Settings（环境变量配置） |
| `backend/app/llm_client.py` | LLM 客户端（OpenAI + MiniMax + DeepSeek） |
| `frontend/src/pages/RunDetailPage.tsx` | 运行详情页（Stepper + Tabs） |
| `frontend/src/types/index.ts` | 前端类型定义 |
| `frontend/src/services/runs.ts` | Runs API 封装 |

## 调试 graph 执行

当 run 失败时，按这个顺序排查：

```bash
# 1. 查看 run 状态（注意 current_node 字段，表示卡在哪）
curl -s http://127.0.0.1:8000/incidents/runs/{run_id} | python3 -m json.tool

# 2. 查看事件流（找 ERROR 级别事件）
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/events | \
  python3 -c "import sys,json; [print(f'[{e[\"level\"]}] {e[\"type\"]:20s} {e.get(\"node_name\",\"\"):30s} {e.get(\"message\",\"\")[:120]}') for e in json.load(sys.stdin)]"

# 3. 查看证据（如果为空说明 evidence_fanout 有问题）
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/evidence | python3 -m json.tool

# 4. 查看诊断结果
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/diagnosis | python3 -m json.tool

# 5. 查看修复方案
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/remediation | python3 -m json.tool

# 6. 查看本地 trace
curl -s http://127.0.0.1:8000/incidents/runs/{run_id}/trace | python3 -m json.tool
```

## 当前进度

详见 ACTION_PLAN.md（唯一项目进度源）。Phase 1-7 已完成；LangSmith 真实控制台验证已通过，Langfuse 代码已就绪待真实环境验收；Phase 8 启动前 real adapter 收口已完成。下一步是 Phase 8 离线评测，Phase 9/10 为后续增强。

## 开发流程与产物规范

每个需求应按以下阶段推进：

1. 需求采集 / 需求澄清
2. 需求设计
3. 详细设计 → 前端详细设计 → 后端详细设计
4. 代码编写
5. 前后端单元测试
6. 集成测试
7. Playwright 端到端测试
8. 知识沉淀

如果任务很小可合并阶段，但必须至少产出：**任务理解 → 修改计划 → 修改文件清单 → 验收方式 → 测试结果 → 风险说明**。

所有中间设计产物放在 `.vibe-workflow/tasks/<YYYY-MM-DD>-<task-slug>/` 下，推荐文件：

```
01-requirements-clarification.md    # 需求澄清
02-requirements-design.md           # 需求设计
03-detailed-design.md               # 详细设计
04-frontend-detailed-design.md      # 前端详细设计
05-backend-detailed-design.md       # 后端详细设计
06-implementation-plan.md           # 实现计划
07-unit-test-report.md              # 单元测试报告
08-integration-test-report.md       # 集成测试报告
09-e2e-playwright-report.md         # E2E 测试报告
10-knowledge-capture.md             # 知识沉淀
```

## 代码修改规则

修改代码前必须回答：

- 这次要解决什么问题？
- 涉及哪些模块？
- 要改哪些文件？
- 明确不改哪些文件？
- 如何验证？
- 失败如何回滚？

代码实现要求：

- 优先复用现有架构、工具函数、组件、请求封装、状态管理模式。
- 不引入新依赖，除非已说明原因、替代方案和风险。
- 不修改锁文件，除非任务明确需要依赖变更。
- 不改格式化无关的大面积文件。
- 不删除测试，除非明确说明测试过时并补充新测试。
- 不在业务代码中硬编码敏感信息。

## Review 规则

Review Agent 必须只读审查，不得直接修改文件。审查重点：

- 是否满足需求和验收标准
- 是否越权修改
- 是否引入回归
- 是否存在类型、空值、异常、并发、权限、安全问题
- 是否补充了必要测试
- 是否需要更新文档和知识库

## 知识沉淀规则

每次任务结束后，必须沉淀以下内容：

- 本次关键设计决策
- 失败/踩坑/绕路
- 下次可复用的检查清单
- 应写入 AGENTS.md 的长期规则
- 应沉淀成 Skill 的重复性流程
- 对项目架构或测试体系的改进建议

## 禁止事项

- 禁止直接执行 `rm -rf`、强制 reset、强制 push、删除数据库、清空数据等破坏性命令。
- 禁止在未说明风险时执行迁移、升级、重装依赖。
- 禁止把测试失败解释为「环境问题」后跳过，必须给出证据。
- 禁止用「可能」「应该」替代验证结果。
- 禁止跳过 Review 和知识沉淀。

## 测试命令

Agent 应先检查项目实际脚本是否存在，再执行。当前项目可用命令：

```bash
# 后端测试
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q

# 前端测试
cd frontend && npx vitest run

# 前端 lint / typecheck
cd frontend && npm run lint
cd frontend && npm run typecheck
```

若项目没有对应脚本，Agent 必须说明缺失，并建议补充 `package.json` scripts。

## 编码规范

- Python: 4 空格缩进，snake_case，Ruff 100 字符行宽
- TypeScript: 2 空格缩进，PascalCase 组件名，semicolons
- 测试文件命名：Python `test_*.py`，TS `*.test.ts(x)`
- commit 信息格式：`backend: xxx` 或 `frontend: xxx`
- 不要提交 .env、*.db、node_modules、venv
