# OpsPilot Backend

OpsPilot 后端是 FastAPI + LangGraph + SQLAlchemy 实现的 SRE 故障处置智能体。主流程由 13 个节点编排：

```text
intake -> triage -> retrieve_memory -> planner -> evidence_fanout ->
evidence_aggregate -> diagnose -> critic -> remediation -> risk_gate ->
approval_interrupt/executor -> verify -> rca
```

## 启动

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/healthz
```

## 测试

```bash
cd backend
pytest app/tests/ -x -q
```

重点测试文件：

- `app/tests/test_graph_integration.py`
- `app/tests/test_resume_and_evidence.py`
- `app/tests/test_tool_gateway.py`
- `app/tests/test_mysql_adapter.py`
- `app/tests/test_k8s_adapter.py`
- `app/tests/test_slb_adapter.py`
- `app/tests/test_oss_adapter.py`
- `app/tests/test_rag_*.py`

## 核心 API

- `POST /incidents/runs`：创建运行，支持 `ticket`、`ticket_id`、`alert_event` 三种互斥入口
- `GET /incidents/runs/{run_id}`：查看运行状态
- `GET /incidents/runs/{run_id}/events`：查看事件流
- `GET /incidents/runs/{run_id}/evidence`：查看证据
- `GET /incidents/runs/{run_id}/diagnosis`：查看诊断
- `GET /incidents/runs/{run_id}/remediation`：查看修复方案
- `GET /incidents/runs/{run_id}/rca`：查看 RCA
- `GET /incidents/runs/{run_id}/trace`：查看本地 tracing span/event
- `GET /approvals/pending`：查看待审批
- `POST /approvals/{approval_id}/decision`：提交审批决策

## Adapter 模式

默认使用 mock adapter：

```bash
TOOL_ADAPTER_MODE=mock
```

真实 adapter 当前进度：

- 已实现：MySQL 诊断工具、MySQL 应用日志 `query_logs`、K8s 只读工具、`query_metrics`（阿里云 CMS/K8s 指标）、`query_deployments`（K8s deployment 列表与状态）、SLB 健康/流量、OSS RCA/evidence 写归档
- 已实现但仍需真实环境联调：RAG 知识检索与写回、本地 tracing 闭环、各 real adapter 的线上凭证/白名单/region 配置
- 尚未实现：LangSmith / Langfuse 外部 tracing provider、离线评测框架、`execute_action` real 模式、`query_runbook` gateway real 模式、`query_ticket_by_id` / `query_service_metadata` 真实数据源

切换到真实 adapter 前，需要配置对应凭证、白名单和只读权限。

## 文档

- 当前进度：`../ACTION_PLAN.md`
- AI 编码指南：`../AGENTS.md`
- 阿里云接入设计：`docs/design/aliyun-integration-design.md`
- 过期审查和历史计划：`docs/archive/`
