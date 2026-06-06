"""Tests for eval fixture injection via ContextVar + gateway short-circuit."""
import asyncio

import pytest

from app.tools import gateway, ToolRequest
from app.evals.fixture_context import fixture_scope, get_active_fixtures


def _req(tool_name):
    return ToolRequest(
        tool_name=tool_name, params={"service": "s", "env": "e"}, run_id="r"
    )


def test_no_scope_returns_none():
    assert get_active_fixtures() is None


@pytest.mark.asyncio
async def test_scope_short_circuits_to_fixture():
    with fixture_scope({"query_logs": {"logs": [], "count": 7}}):
        resp = await gateway.call_tool(_req("query_logs"))
    assert resp.success is True
    assert resp.result["count"] == 7
    assert resp.result["_adapter_info"] == "eval_fixture"


@pytest.mark.asyncio
async def test_unprovided_readonly_tool_returns_controlled_empty():
    # query_k8s_pods not provided -> controlled empty, NOT fail-loud, NOT mock data
    with fixture_scope({"query_logs": {"count": 1}}):
        resp = await gateway.call_tool(_req("query_k8s_pods"))
    assert resp.success is True
    assert resp.result.get("_adapter_info") == "eval_fixture"
    # No payload keys other than the adapter marker
    assert set(resp.result.keys()) == {"_adapter_info"}


@pytest.mark.asyncio
async def test_write_tool_returns_success_stub():
    with fixture_scope({"query_logs": {"count": 1}}):
        resp = await gateway.call_tool(
            ToolRequest(
                tool_name="write_rca_to_oss",
                params={"run_id": "r", "content": "x"},
                run_id="r",
            )
        )
    assert resp.success is True
    assert resp.result.get("_eval_stub") is True


@pytest.mark.asyncio
async def test_scope_exit_restores_normal_path():
    with fixture_scope({"query_logs": {"count": 1}}):
        pass
    resp = await gateway.call_tool(_req("query_logs"))
    # Back to mock adapter - not the eval marker
    assert resp.result.get("_adapter_info") != "eval_fixture"


@pytest.mark.asyncio
async def test_concurrent_cases_are_isolated():
    async def run_case(count):
        with fixture_scope({"query_logs": {"count": count}}):
            await asyncio.sleep(0.01)
            resp = await gateway.call_tool(_req("query_logs"))
            return resp.result["count"]

    results = await asyncio.gather(run_case(1), run_case(2), run_case(3))
    assert sorted(results) == [1, 2, 3]
