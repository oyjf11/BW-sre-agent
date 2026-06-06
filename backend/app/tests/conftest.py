import importlib

import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def force_mock_tool_adapter(monkeypatch):
    """Keep unit tests isolated from local .env TOOL_ADAPTER_MODE=real."""
    monkeypatch.setenv("TOOL_ADAPTER_MODE", "mock")
    get_settings.cache_clear()

    gateway_module = importlib.import_module("app.tools.gateway")
    monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "mock")
    try:
        yield
    finally:
        get_settings.cache_clear()
