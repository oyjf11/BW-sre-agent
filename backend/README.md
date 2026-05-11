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

## 核心 API

- `POST /incidents/runs`：创建运行，支持 `ticket`、`ticket_id`、`alert_event` 三种互斥入口
- `GET /incidents/runs/{run_id}`：查看运行状态
- `GET /incidents/runs/{run_id}/events`：查看事件流
- `GET /incidents/runs/{run_id}/evidence`：查看证据
- `GET /incidents/runs/{run_id}/diagnosis`：查看诊断
- `GET /incidents/runs/{run_id}/remediation`：查看修复方案
- `GET /incidents/runs/{run_id}/rca`：查看 RCA
- `GET /approvals/pending`：查看待审批
- `POST /approvals/{approval_id}/decision`：提交审批决策

## Adapter 模式

默认使用 mock adapter：

```bash
TOOL_ADAPTER_MODE=mock
```

真实 adapter 当前进度：

- 已实现：MySQL 诊断工具、MySQL 应用日志 `query_logs`、K8s 只读工具
- 待实现：SLB、OSS、Prometheus/ARMS 指标、CI/CD 部署记录、RAG、Tracing、Eval

切换到真实 adapter 前，需要配置对应凭证、白名单和只读权限。

## 文档

- 当前进度：`../ACTION_PLAN.md`
- AI 编码指南：`../AGENTS.md`
- 阿里云接入设计：`docs/design/aliyun-integration-design.md`
- 过期审查和历史计划：`docs/archive/`
