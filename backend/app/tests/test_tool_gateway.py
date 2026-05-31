import pytest
import importlib

from app.tools.gateway import ToolGateway
from app.tools.schemas import ToolRequest
from app.tracing import tracer


class TestToolGateway:
    @pytest.mark.asyncio
    async def test_mock_adapter_calls_succeed(self):
        tracer.clear()
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_logs",
            params={"service": "api", "env": "prod"},
            run_id="run-001",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result is not None
        assert response.result["_adapter_info"] == "mock"
        spans = tracer.get_spans("run-001")
        assert any(span["name"] == "tool.query_logs" for span in spans)

    @pytest.mark.asyncio
    async def test_real_adapter_fails_closed_when_not_configured(self, monkeypatch):
        gateway_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "real")
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_runbook",
            params={"service": "api", "env": "prod"},
            run_id="run-002",
        )

        response = await gateway.call_tool(request)

        assert response.success is False
        assert "Real adapter" in response.error

    @pytest.mark.asyncio
    async def test_invalid_params_fail_before_handler_execution(self, monkeypatch):
        gateway = ToolGateway()
        called = {"value": False}

        async def fake_handler(**kwargs):
            called["value"] = True
            return {"ok": True}

        monkeypatch.setitem(gateway.handlers, "query_db_slow_queries", fake_handler)
        request = ToolRequest(
            tool_name="query_db_slow_queries",
            params={"threshold_seconds": "bad"},
            run_id="run-invalid-001",
        )

        response = await gateway.call_tool(request)

        assert response.success is False
        assert response.error == "Invalid parameter 'threshold_seconds': expected integer"
        assert called["value"] is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "tool_name,params",
        [
            (
                "query_ticket_by_id",
                {"ticket_id": "INC-0001"},
            ),
            (
                "query_service_metadata",
                {"service": "payment-service", "env": "prod"},
            ),
            (
                "query_k8s_deployment_status",
                {"service": "payment-service", "env": "prod", "namespace": "default"},
            ),
            (
                "query_k8s_pods",
                {"service": "payment-service", "env": "prod", "namespace": "default"},
            ),
            (
                "query_k8s_events",
                {"service": "payment-service", "env": "prod", "namespace": "default", "limit": 10},
            ),
            (
                "query_k8s_pod_logs_summary",
                {
                    "service": "payment-service",
                    "env": "prod",
                    "namespace": "default",
                    "tail_lines": 100,
                },
            ),
            (
                "query_lb_health_status",
                {"service": "payment-service", "env": "prod"},
            ),
            (
                "query_lb_traffic_metrics",
                {"service": "payment-service", "env": "prod", "window_minutes": 5},
            ),
        ],
    )
    async def test_new_mock_tools_succeed(self, tool_name, params):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name=tool_name,
            params=params,
            run_id="run-003",
        )

        response = await gateway.call_tool(request)

        assert response.success is True, f"{tool_name} returned error: {response.error}"
        assert response.result is not None
        assert response.result.get("_adapter_info") == "mock"
