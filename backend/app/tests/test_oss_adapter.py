import pytest

from app.tools.adapters import mock_write_rca_to_oss, mock_write_evidence_to_oss
from app.tools.clients.oss_client import OssClientWrapper, ALLOWED_PREFIXES
from app.tools.gateway import ToolGateway
from app.tools.schemas import ToolRequest


class TestOSSMockAdapters:
    @pytest.mark.asyncio
    async def test_mock_write_rca_to_oss_returns_success(self):
        result = await mock_write_rca_to_oss(
            run_id="run-oss-001",
            service="payment-service",
            env="prod",
            content="# RCA Report",
            content_type="markdown",
        )

        assert result["run_id"] == "run-oss-001"
        assert result["service"] == "payment-service"
        assert result["oss_key"] == "rca/payment-service/run-oss-001.md"
        assert "oss_url" in result
        assert result["content_type"] == "markdown"
        assert result["response_size_limit_kb"] == 64

    @pytest.mark.asyncio
    async def test_mock_write_rca_to_oss_json_type(self):
        result = await mock_write_rca_to_oss(
            run_id="run-oss-002",
            service="payment-service",
            env="prod",
            content='{"key": "value"}',
            content_type="json",
        )

        assert result["oss_key"] == "rca/payment-service/run-oss-002.json"

    @pytest.mark.asyncio
    async def test_mock_write_rca_to_oss_no_service(self):
        result = await mock_write_rca_to_oss(
            run_id="run-oss-003",
            content="# RCA Report",
        )

        assert result["oss_key"] == "rca/unknown/run-oss-003.md"

    @pytest.mark.asyncio
    async def test_mock_write_evidence_to_oss_returns_success(self):
        result = await mock_write_evidence_to_oss(
            run_id="run-oss-001",
            service="payment-service",
            env="prod",
            content='[{"evidence_id": "ev-1"}]',
        )

        assert result["run_id"] == "run-oss-001"
        assert result["service"] == "payment-service"
        assert result["oss_key"] == "evidence/payment-service/run-oss-001.json"
        assert "oss_url" in result
        assert result["response_size_limit_kb"] == 64

    @pytest.mark.asyncio
    async def test_mock_write_evidence_to_oss_no_service(self):
        result = await mock_write_evidence_to_oss(
            run_id="run-oss-004",
            content='[{"evidence_id": "ev-1"}]',
        )

        assert result["oss_key"] == "evidence/unknown/run-oss-004.json"


class TestOSSToolGatewayRouting:
    """Test that OSS tools route correctly through ToolGateway."""

    def _patch_client_init(self, monkeypatch):
        def fake_init(self, bucket_name=None, endpoint=None,
                      access_key_id=None, access_key_secret=None):
            self.bucket_name = bucket_name or "test-bucket"
            self.endpoint = endpoint or "oss-cn-shenzhen.aliyuncs.com"
            self.access_key_id = access_key_id or "fake-key"
            self.access_key_secret = access_key_secret or "fake-secret"

        monkeypatch.setattr(OssClientWrapper, "__init__", fake_init)

    @pytest.mark.asyncio
    async def test_write_rca_to_oss_real_mode(self, monkeypatch):
        import importlib

        gateway_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "real")
        self._patch_client_init(monkeypatch)

        monkeypatch.setattr(
            OssClientWrapper,
            "put_object",
            lambda self, key, content: {
                "oss_key": key,
                "oss_url": f"https://{self.bucket_name}.{self.endpoint}/{key}",
                "bucket": self.bucket_name,
                "etag": "abc123",
                "status": 200,
            },
        )

        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="write_rca_to_oss",
            params={
                "run_id": "run-oss-001",
                "service": "payment-service",
                "env": "prod",
                "content": "# RCA Report",
                "content_type": "markdown",
            },
            run_id="run-oss-001",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result["oss_key"] == "rca/payment-service/run-oss-001.md"
        assert "oss_url" in response.result
        assert response.result["content_type"] == "markdown"

    @pytest.mark.asyncio
    async def test_write_evidence_to_oss_real_mode(self, monkeypatch):
        import importlib

        gateway_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "real")
        self._patch_client_init(monkeypatch)

        monkeypatch.setattr(
            OssClientWrapper,
            "put_object",
            lambda self, key, content: {
                "oss_key": key,
                "oss_url": f"https://{self.bucket_name}.{self.endpoint}/{key}",
                "bucket": self.bucket_name,
                "etag": "def456",
                "status": 200,
            },
        )

        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="write_evidence_to_oss",
            params={
                "run_id": "run-oss-001",
                "service": "payment-service",
                "env": "prod",
                "content": '[{"evidence_id": "ev-1"}]',
            },
            run_id="run-oss-001",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result["oss_key"] == "evidence/payment-service/run-oss-001.json"

    @pytest.mark.asyncio
    async def test_write_rca_to_oss_missing_required_param(self, monkeypatch):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="write_rca_to_oss",
            params={"service": "payment-service"},
            run_id="run-oss-005",
        )

        response = await gateway.call_tool(request)

        assert response.success is False
        assert "Missing required parameter: run_id" in response.error

    @pytest.mark.asyncio
    async def test_write_evidence_to_oss_missing_required_param(self, monkeypatch):
        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="write_evidence_to_oss",
            params={"service": "payment-service"},
            run_id="run-oss-006",
        )

        response = await gateway.call_tool(request)

        assert response.success is False
        assert "Missing required parameter: run_id" in response.error

    @pytest.mark.asyncio
    async def test_mock_mode_used_by_default(self, monkeypatch):
        import importlib

        gateway_module = importlib.import_module("app.tools.gateway")
        monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "mock")

        gateway = ToolGateway()
        request = ToolRequest(
            tool_name="write_rca_to_oss",
            params={
                "run_id": "run-oss-007",
                "content": "# RCA Report",
            },
            run_id="run-oss-007",
        )

        response = await gateway.call_tool(request)

        assert response.success is True
        assert response.result["bucket"] == "mock-bucket"


class TestOssClientPrefixValidation:
    def test_rca_prefix_allowed(self):
        wrapper = OssClientWrapper.__new__(OssClientWrapper)
        wrapper._validate_key_prefix("rca/payment-service/run-001.md")

    def test_evidence_prefix_allowed(self):
        wrapper = OssClientWrapper.__new__(OssClientWrapper)
        wrapper._validate_key_prefix("evidence/payment-service/run-001.json")

    def test_other_prefix_rejected(self):
        wrapper = OssClientWrapper.__new__(OssClientWrapper)
        with pytest.raises(ValueError, match="not allowed"):
            wrapper._validate_key_prefix("logs/payment-service/run-001.md")

    def test_root_key_rejected(self):
        wrapper = OssClientWrapper.__new__(OssClientWrapper)
        with pytest.raises(ValueError, match="not allowed"):
            wrapper._validate_key_prefix("run-001.md")

    def test_empty_key_rejected(self):
        wrapper = OssClientWrapper.__new__(OssClientWrapper)
        with pytest.raises(ValueError, match="not allowed"):
            wrapper._validate_key_prefix("")


class TestOssClientConfig:
    def test_allowed_prefixes_tuple(self):
        assert isinstance(ALLOWED_PREFIXES, tuple)
        assert "rca/" in ALLOWED_PREFIXES
        assert "evidence/" in ALLOWED_PREFIXES
        assert len(ALLOWED_PREFIXES) == 2
