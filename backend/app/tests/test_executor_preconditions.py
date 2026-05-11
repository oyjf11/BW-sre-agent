import pytest

from app.services.executor import ControlledExecutor
from app.tools.schemas import ToolResponse


class _FakeGateway:
    def __init__(self, response: ToolResponse):
        self._response = response

    async def call_tool(self, request):
        return self._response


@pytest.mark.asyncio
async def test_deployment_healthy_precondition_checks_status():
    executor = ControlledExecutor.__new__(ControlledExecutor)
    executor.gateway = _FakeGateway(
        ToolResponse(
            tool_name="query_k8s_deployment_status",
            success=True,
            result={"status": "degraded"},
            latency_ms=1,
        )
    )

    failed = await executor._check_preconditions(
        run_id="run-pre-001",
        service="payment-service",
        env="prod",
        preconditions=["deployment_healthy"],
    )

    assert failed == ["deployment_healthy: deployment not healthy for payment-service"]
