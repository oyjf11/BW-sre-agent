# 集成测试报告

## 测试环境

- 后端：`uvicorn app.main:app --reload --port 8000`
- 数据库：临时 SQLite，位于本任务目录 `e2e-opspilot.db`
- Tool adapter：`TOOL_ADAPTER_MODE=mock`
- 第一轮：沿用 `.env` 的 `AGENT_FEATURE_SPECIALIST_POOL=true`
- 第二/三轮：进程级覆盖 `AGENT_FEATURE_SPECIALIST_POOL=false`

## 健康检查

```bash
curl http://127.0.0.1:8000/healthz
```

结果：`{"status":"ok"}`。

## API 采集结果

- `GET /incidents/runs/{run_id}`：三次 run 均可查询。
- `GET /incidents/runs/{run_id}/events`：三次 run 均可查询，事件流无 ERROR。
- `GET /incidents/runs/{run_id}/evidence`：第二轮 completed run 返回 11 条 evidence。
- `GET /incidents/runs/{run_id}/actions`：第二/三轮均返回 1 条 completed restart action。
- `GET /incidents/runs/{run_id}/rca`：第二/三轮均返回 RCA。
- `GET /incidents/runs/{run_id}/trace`：第二/三轮均返回 32 个 spans，errored spans 为 0。
- `GET /approvals/pending`：第二/三轮均为空。

## 原始文件

本目录保留了 `create-run*.json`、`run-*-final.json`、`events-*-final.json`、`evidence-*-final.json`、`remediation-*-final.json`、`actions-*-final.json`、`rca-*-final.json`、`trace-*-final.json` 等原始响应。

