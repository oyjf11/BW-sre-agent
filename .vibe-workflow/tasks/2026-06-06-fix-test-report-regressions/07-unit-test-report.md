# 单元测试报告

## RED

命令：

```bash
cd backend && source venv/bin/activate && TOOL_ADAPTER_MODE=mock AGENT_FEATURE_SPECIALIST_POOL=true python -m pytest app/tests/test_specialist_agent.py::TestBuildDefaultAgentTasks::test_default_task_agent_ids_exist_in_config app/tests/test_specialist_agent.py::TestBuildDefaultAgentTasks::test_planner_agent_ids_exist_in_config app/tests/test_graph_integration.py::TestIncidentGraph::test_graph_waits_for_approval_on_high_risk_action -q
```

结果：

- 3 failed。
- 失败点分别为 `logs_specialist` / `deployments_specialist` 不在配置中，以及高风险审批用例得到 `COMPLETED` 而不是 `WAITING_HUMAN`。

## GREEN / Focused

```bash
cd backend && source venv/bin/activate && TOOL_ADAPTER_MODE=mock AGENT_FEATURE_SPECIALIST_POOL=true python -m pytest app/tests/test_specialist_agent.py::TestBuildDefaultAgentTasks::test_default_task_agent_ids_exist_in_config app/tests/test_specialist_agent.py::TestBuildDefaultAgentTasks::test_planner_agent_ids_exist_in_config app/tests/test_graph_integration.py::TestIncidentGraph::test_graph_waits_for_approval_on_high_risk_action -q
```

结果：`3 passed`。

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_event_bus.py -q
```

结果：`5 passed`。

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_tool_gateway.py app/tests/test_mysql_adapter.py -q
```

结果：`25 passed`。

## Backend Full

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q
```

结果：`251 passed, 2 warnings in 152.26s`。

## Frontend

```bash
cd frontend && npm run test
```

结果：`24 passed / 156 tests passed`。

```bash
cd frontend && npm run build
```

结果：通过，包含 `tsc -b` 类型检查和 Vite build。

```bash
cd frontend && npm run lint
```

结果：失败，27 errors / 1 warning。失败集中在既有前端 `no-explicit-any`、`react-refresh/only-export-components` 和一个 hook dependency warning；本次未改前端代码，未扩大范围处理。

