import pytest

import app.tools.adapters.mysql_adapter as mysql_adapter_module
from app.tools.adapters import (
    mock_query_db_processlist,
    mock_query_db_slow_queries,
    mock_query_db_table_status,
    mock_query_db_variables,
)
from app.tools.adapters.mysql_adapter import query_logs_from_db
from app.tools.gateway import ToolGateway, select_adapter, ADAPTER_MODE
from app.tools.schemas import ToolRequest


class TestMySQLMockAdapters:
    @pytest.mark.asyncio
    async def test_mock_query_db_processlist_returns_active_connections(self):
        result = await mock_query_db_processlist()

        assert "processlist" in result
        assert "total_connections" in result
        assert "active_connections" in result
        assert result["response_size_limit_kb"] == 64
        assert len(result["processlist"]) > 0
        for conn in result["processlist"]:
            assert conn["Command"].lower() != "sleep"

    @pytest.mark.asyncio
    async def test_mock_query_db_slow_queries_filters_by_threshold(self):
        result = await mock_query_db_slow_queries(threshold_seconds=10)

        assert "slow_queries" in result
        assert "threshold_seconds" in result
        assert result["threshold_seconds"] == 10
        for q in result["slow_queries"]:
            assert q["Time"] >= 10

    @pytest.mark.asyncio
    async def test_mock_query_db_slow_queries_default_threshold(self):
        result = await mock_query_db_slow_queries()

        assert result["threshold_seconds"] == 5

    @pytest.mark.asyncio
    async def test_mock_query_db_table_status_returns_top_tables(self):
        result = await mock_query_db_table_status()

        assert "table_status" in result
        assert "total_tables" in result
        assert "returned_tables" in result
        assert result["response_size_limit_kb"] == 64
        assert len(result["table_status"]) <= 20
        data_lengths = [t["Data_length"] for t in result["table_status"]]
        assert data_lengths == sorted(data_lengths, reverse=True)

    @pytest.mark.asyncio
    async def test_mock_query_db_variables_returns_status(self):
        result = await mock_query_db_variables()

        assert "variables" in result
        assert result["response_size_limit_kb"] == 64
        variables = result["variables"]
        assert "Threads_connected" in variables
        assert "buffer_pool_hit_rate_pct" in variables


class TestMySQLToolsViaGateway:
    @pytest.mark.asyncio
    async def test_query_db_processlist_via_gateway(self):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_db_processlist",
            params={},
            run_id="run-mysql-001",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result["_adapter_info"] == "mock"
        assert "processlist" in response.result

    @pytest.mark.asyncio
    async def test_query_db_slow_queries_via_gateway(self):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_db_slow_queries",
            params={"threshold_seconds": 10},
            run_id="run-mysql-002",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result["threshold_seconds"] == 10

    @pytest.mark.asyncio
    async def test_query_db_table_status_via_gateway(self):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_db_table_status",
            params={},
            run_id="run-mysql-003",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert len(response.result["table_status"]) <= 20

    @pytest.mark.asyncio
    async def test_query_db_variables_via_gateway(self):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_db_variables",
            params={},
            run_id="run-mysql-004",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert "variables" in response.result


class TestQueryLogsFromDB:
    @pytest.mark.asyncio
    async def test_query_logs_from_db_returns_empty_when_no_matching_logs(self, monkeypatch):
        monkeypatch.setattr(
            mysql_adapter_module.MySQLClient,
            "execute_query",
            lambda self, sql, params=None: [],
        )

        result = await query_logs_from_db(service="crm-service", env="prod")

        assert "logs" in result
        assert "count" in result
        assert "query" in result
        assert result["query"] == "*"
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_query_logs_from_db_applies_category_filters(self, monkeypatch):
        captured = {}

        def fake_execute_query(self, sql, params=None):
            captured["sql"] = sql
            captured["params"] = params
            return [
                {
                    "id": 1,
                    "level": 1,
                    "category": "crm-service.prod.order",
                    "log_time": 1712550000.0,
                    "prefix": "",
                    "message": "Lock wait timeout exceeded",
                    "created_at": "2026-04-08 10:00:00",
                }
            ]

        monkeypatch.setattr(
            mysql_adapter_module.MySQLClient,
            "execute_query",
            fake_execute_query,
        )

        result = await query_logs_from_db(
            service="crm-service",
            env="prod",
            time_range={"from": "2026-04-08 00:00:00", "to": "2026-04-08 23:59:59"},
            query="Lock wait timeout",
            limit=5,
        )

        assert "category LIKE %s ESCAPE '\\\\'" in captured["sql"]
        assert "message LIKE %s ESCAPE '\\\\'" in captured["sql"]
        assert "created_at >= %s" in captured["sql"]
        assert "created_at <= %s" in captured["sql"]
        assert "%crm-service%" in captured["params"]
        assert "%prod%" in captured["params"]
        assert "%production%" in captured["params"]
        assert "%Lock wait timeout%" in captured["params"]
        assert captured["params"][-1] == 5
        assert result["count"] == 1
        assert result["logs"][0]["level"] == "ERROR"
        assert result["logs"][0]["source"] == "crm-service.prod.order"
        assert result["query"] == "Lock wait timeout"

    @pytest.mark.asyncio
    async def test_query_logs_from_db_sql_injection_safe(self, monkeypatch):
        captured = {}

        def fake_execute_query(self, sql, params=None):
            captured["sql"] = sql
            captured["params"] = params
            return []

        monkeypatch.setattr(
            mysql_adapter_module.MySQLClient,
            "execute_query",
            fake_execute_query,
        )

        await query_logs_from_db(
            service="test",
            env="prod",
            query="'; DROP TABLE--",
        )

        assert "DROP TABLE" not in captured.get("sql", "")

    @pytest.mark.asyncio
    async def test_query_logs_from_db_respects_limit(self, monkeypatch):
        captured = {}

        def fake_execute_query(self, sql, params=None):
            captured["sql"] = sql
            captured["params"] = params
            return []

        monkeypatch.setattr(
            mysql_adapter_module.MySQLClient,
            "execute_query",
            fake_execute_query,
        )

        result = await query_logs_from_db(limit=500)

        assert result["count"] == 0
        assert "error" not in result
        assert captured["params"][-1] == 200

    @pytest.mark.asyncio
    async def test_query_logs_select_adapter_routes_to_real(self, monkeypatch):
        import importlib

        gw_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gw_module, "ADAPTER_MODE", "real")

        handler = gw_module.select_adapter("query_logs")

        assert handler is not None
        assert handler.__name__ == "query_logs_from_db"
