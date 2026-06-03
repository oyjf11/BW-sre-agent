from types import SimpleNamespace

import pytest

import app.tools.adapters.k8s_adapter as k8s_adapter_module
from app.tools.adapters import (
    query_k8s_events,
    query_k8s_pod_logs_summary,
    query_k8s_pods,
    query_k8s_nodes,
    query_k8s_services,
    query_k8s_hpa,
    query_k8s_ingresses,
    query_k8s_statefulsets,
    query_k8s_daemonsets,
    query_k8s_configmaps,
    query_k8s_resource_quotas,
    query_k8s_pvc,
    query_k8s_replicasets,
    query_k8s_jobs,
)
from app.tools.gateway import ToolGateway
from app.tools.schemas import ToolRequest


class TestK8sMockAdapters:
    @pytest.mark.asyncio
    async def test_mock_query_k8s_pods_returns_pods(self):
        result = await query_k8s_pods(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert result["namespace"] == "default"
        assert result["response_size_limit_kb"] == 128

    @pytest.mark.asyncio
    async def test_mock_query_k8s_events_returns_top_reasons(self):
        result = await query_k8s_events(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert result["top_reasons"]
        assert result["response_size_limit_kb"] == 128

    @pytest.mark.asyncio
    async def test_mock_query_k8s_pod_logs_summary_returns_patterns(self):
        result = await query_k8s_pod_logs_summary(
            service="payment-service",
            env="prod",
            namespace="default",
        )

        assert result["tail_window"] == 100
        assert result["lines_scanned"] > 0
        assert result["top_patterns"]
        assert result["response_size_limit_kb"] == 128

    @pytest.mark.asyncio
    async def test_mock_query_k8s_nodes_returns_nodes(self):
        result = await query_k8s_nodes(service="payment-service", env="prod")

        assert result["count"] == 3
        assert result["nodes"][0]["name"] == "node-a"
        assert result["nodes"][2]["role"] == "control-plane"

    @pytest.mark.asyncio
    async def test_mock_query_k8s_services_returns_services(self):
        result = await query_k8s_services(service="payment-service", env="prod", namespace="default")

        assert result["count"] == 2
        assert result["services"][0]["type"] == "ClusterIP"
        assert result["services"][1]["type"] == "LoadBalancer"

    @pytest.mark.asyncio
    async def test_mock_query_k8s_hpa_returns_hpas(self):
        result = await query_k8s_hpa(service="payment-service", env="prod", namespace="default")

        assert result["count"] == 1
        assert result["hpas"][0]["current_replicas"] == 4
        assert result["hpas"][0]["min_replicas"] == 2

    @pytest.mark.asyncio
    async def test_mock_query_k8s_ingresses_returns_ingresses(self):
        result = await query_k8s_ingresses(service="payment-service", env="prod", namespace="default")

        assert result["count"] == 1
        assert result["ingresses"][0]["tls_enabled"] is True
        assert "hosts" in result["ingresses"][0]

    @pytest.mark.asyncio
    async def test_mock_query_k8s_statefulsets_returns_sts(self):
        result = await query_k8s_statefulsets(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert result["statefulsets"][0]["status"] == "running"

    @pytest.mark.asyncio
    async def test_mock_query_k8s_daemonsets_returns_ds(self):
        result = await query_k8s_daemonsets(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert result["daemonsets"][0]["status"] == "running"

    @pytest.mark.asyncio
    async def test_mock_query_k8s_configmaps_returns_cms(self):
        result = await query_k8s_configmaps(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert "data_keys" in result["configmaps"][0]
        assert "data_sample" in result["configmaps"][0]

    @pytest.mark.asyncio
    async def test_mock_query_k8s_resource_quotas_returns_quotas(self):
        result = await query_k8s_resource_quotas(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert "hard" in result["resource_quotas"][0]
        assert "used" in result["resource_quotas"][0]

    @pytest.mark.asyncio
    async def test_mock_query_k8s_pvc_returns_pvcs(self):
        result = await query_k8s_pvc(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert result["pvcs"][0]["status"] == "Bound"

    @pytest.mark.asyncio
    async def test_mock_query_k8s_replicasets_returns_rs(self):
        result = await query_k8s_replicasets(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0
        assert "owner_references" in result["replicasets"][0]

    @pytest.mark.asyncio
    async def test_mock_query_k8s_jobs_returns_jobs(self):
        result = await query_k8s_jobs(service="payment-service", env="prod", namespace="default")

        assert result["count"] > 0


class TestK8sRealAdapterRouting:
    @pytest.mark.asyncio
    async def test_query_k8s_pods_real_fail_closed_when_namespace_forbidden(self, monkeypatch):
        import importlib

        gateway_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "real")

        def fake_resolve_target(self, service, namespace="", deployment_name=""):
            raise PermissionError("Namespace 'default' is not in K8S_ALLOWED_NAMESPACES")

        monkeypatch.setattr(
            k8s_adapter_module.K8sClient,
            "resolve_target",
            fake_resolve_target,
        )

        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_k8s_pods",
            params={"service": "payment-service", "env": "prod"},
            run_id="run-k8s-001",
        )

        response = await gateway.call_tool(request)

        assert response.success is False
        assert "K8S_ALLOWED_NAMESPACES" in response.error

    @pytest.mark.asyncio
    async def test_query_k8s_events_real_formats_result(self, monkeypatch):
        import importlib

        gateway_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "real")

        pod = SimpleNamespace(
            metadata=SimpleNamespace(name="payment-service-abc12"),
            status=SimpleNamespace(
                phase="Running",
                container_statuses=[SimpleNamespace(ready=True, restart_count=0)],
                pod_ip="10.0.0.10",
                start_time=None,
            ),
            spec=SimpleNamespace(node_name="node-a"),
        )
        event = SimpleNamespace(
            reason="BackOff",
            message="Back-off restarting failed container",
            type="Warning",
            involved_object=SimpleNamespace(name="payment-service-abc12"),
            last_timestamp=None,
            event_time=None,
            first_timestamp=None,
            metadata=SimpleNamespace(creation_timestamp=None),
        )

        monkeypatch.setattr(
            k8s_adapter_module.K8sClient,
            "resolve_target",
            lambda self, service, namespace="", deployment_name="": ("default", "payment-service"),
        )
        monkeypatch.setattr(
            k8s_adapter_module.K8sClient,
            "list_pods_for_target",
            lambda self, namespace, deployment_name, service: [pod],
        )
        monkeypatch.setattr(
            k8s_adapter_module.K8sClient,
            "list_events",
            lambda self, namespace: [event],
        )

        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="query_k8s_events",
            params={"service": "payment-service", "env": "prod"},
            run_id="run-k8s-002",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result["count"] == 1
        assert response.result["top_reasons"][0]["reason"] == "BackOff"
