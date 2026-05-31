import sys
from types import SimpleNamespace

import pytest

from app.tracing import AgentTracer
from app.tracing_providers import (
    LocalTraceProvider,
    ProviderSpanResult,
    TraceProviderConfig,
    config_from_settings,
    create_trace_provider,
)


def make_config(provider: str, **overrides):
    values = {
        "tracing_provider": provider,
        "tracing_project": "opspilot",
        "tracing_base_url": "",
        "tracing_public_base_url": "",
        "langsmith_api_key": "",
        "langsmith_endpoint": "",
        "langfuse_public_key": "",
        "langfuse_secret_key": "",
        "langfuse_base_url": "",
    }
    values.update(overrides)
    return TraceProviderConfig(**values)


class RecordingProvider:
    name = "recording"

    def __init__(self):
        self.started = []
        self.events = []
        self.ended = []
        self.flushed = False

    def start_span(self, span):
        self.started.append(span)
        return ProviderSpanResult(
            external_trace_id=f"trace-{span['run_id']}",
            external_span_id=f"external-{span['span_id']}",
            external_trace_url=f"https://trace.example/{span['run_id']}",
        )

    def add_event(self, span_id, event_name, data):
        self.events.append((span_id, event_name, data))

    def end_span(self, span):
        self.ended.append(span)

    def get_trace_url(self, run_id):
        return f"https://trace.example/{run_id}"

    def flush(self):
        self.flushed = True


class FailingProvider(RecordingProvider):
    name = "failing"

    def start_span(self, span):
        raise RuntimeError("provider down")

    def add_event(self, span_id, event_name, data):
        raise RuntimeError("provider down")

    def end_span(self, span):
        raise RuntimeError("provider down")

    def flush(self):
        raise RuntimeError("provider down")


class FakeLangfuseObservation:
    def __init__(self, name, observation_id):
        self.name = name
        self.id = observation_id
        self.children = []
        self.updates = []
        self.ended = False

    def start_observation(self, **kwargs):
        child = FakeLangfuseObservation(kwargs["name"], f"obs-{kwargs['name']}")
        self.children.append((kwargs, child))
        return child

    def update(self, **kwargs):
        self.updates.append(kwargs)

    def end(self):
        self.ended = True


class FakeLangfuseClient:
    def __init__(self):
        self.started = []
        self.flushed = False

    def create_trace_id(self, seed):
        return f"trace-{seed}"

    def start_observation(self, **kwargs):
        observation = FakeLangfuseObservation(kwargs["name"], f"obs-{kwargs['name']}")
        self.started.append((kwargs, observation))
        return observation

    def flush(self):
        self.flushed = True


class FakeLangSmithClient:
    def __init__(self, api_key=None, api_url=None):
        self.api_key = api_key
        self.api_url = api_url
        self.flushed = False

    def flush(self):
        self.flushed = True

    def list_runs(self, project_name=None, limit=1):
        run = SimpleNamespace(
            url="https://smith.example/o/opspilot/projects/p/default/runs/dummy-run-1"
        )
        return [run]


class FakeRunTree:
    counter = 0

    def __init__(self, **kwargs):
        FakeRunTree.counter += 1
        self.id = f"run-tree-{FakeRunTree.counter}"
        self.kwargs = kwargs
        self.children = []
        self.extra = {}
        self.posted = False
        self.ended = False
        self.patched = False
        self.outputs = None
        self.error = None
        self.url = f"https://smith.example/o/opspilot/projects/p/default/runs/{self.id}"

    def create_child(self, **kwargs):
        child = FakeRunTree(**kwargs)
        self.children.append(child)
        return child

    def post(self):
        self.posted = True

    def end(self, outputs=None, error=None):
        self.ended = True
        self.outputs = outputs
        self.error = error

    def patch(self):
        self.patched = True


# ---------- Task 1: Provider Factory ----------

def test_create_trace_provider_returns_local_for_default_provider():
    provider = create_trace_provider(make_config("local"))

    assert isinstance(provider, LocalTraceProvider)
    assert provider.name == "local"


def test_create_trace_provider_falls_back_to_local_when_langfuse_credentials_missing():
    provider = create_trace_provider(make_config("langfuse"))

    assert isinstance(provider, LocalTraceProvider)
    assert provider.name == "local"


def test_create_trace_provider_falls_back_to_local_when_langsmith_credentials_missing():
    provider = create_trace_provider(make_config("langsmith"))

    assert isinstance(provider, LocalTraceProvider)
    assert provider.name == "local"


# ---------- Task 2: AgentTracer wiring ----------

def test_agent_tracer_records_external_metadata():
    provider = RecordingProvider()
    tracer = AgentTracer(provider=provider)

    span_id = tracer.start_span("graph.run", run_id="run-123")
    tracer.add_event(span_id, "node_started", {"node_name": "node_intake"})
    tracer.end_span(span_id)

    spans = tracer.get_spans("run-123")
    metadata = tracer.get_trace_metadata("run-123")

    assert spans[0]["external_trace_id"] == "trace-run-123"
    assert spans[0]["external_span_id"] == f"external-{span_id}"
    assert metadata == {
        "provider": "recording",
        "external_trace_id": "trace-run-123",
        "external_root_span_id": f"external-{span_id}",
        "external_trace_url": "https://trace.example/run-123",
    }
    assert provider.events == [(span_id, "node_started", {"node_name": "node_intake"})]
    assert provider.ended[0]["status"] == "ok"


def test_agent_tracer_flush_delegates_to_provider():
    provider = RecordingProvider()
    tracer = AgentTracer(provider=provider)

    tracer.flush()

    assert provider.flushed is True


def test_agent_tracer_does_not_raise_when_provider_fails():
    tracer = AgentTracer(provider=FailingProvider())

    span_id = tracer.start_span("graph.run", run_id="run-123")
    tracer.add_event(span_id, "node_started", {"node_name": "node_intake"})
    tracer.end_span(span_id)
    tracer.flush()

    spans = tracer.get_spans("run-123")
    assert spans[0]["name"] == "graph.run"
    assert spans[0]["status"] == "ok"


# ---------- Task 3: Config ----------

def test_config_from_settings_reads_external_tracing_fields():
    from app.core.config import Settings

    settings = Settings(
        tracing_provider="langfuse",
        tracing_project="opspilot-prod",
        tracing_base_url="https://internal.langfuse.example",
        tracing_public_base_url="https://langfuse.example",
        langfuse_public_key="pk-lf-test",
        langfuse_secret_key="sk-lf-test",
        langfuse_base_url="https://cloud.langfuse.com",
        langsmith_api_key="lsv2_test",
        langsmith_endpoint="https://api.smith.langchain.com",
    )

    config = config_from_settings(settings)

    assert config.tracing_provider == "langfuse"
    assert config.tracing_project == "opspilot-prod"
    assert config.tracing_public_base_url == "https://langfuse.example"
    assert config.langfuse_public_key == "pk-lf-test"
    assert config.langfuse_secret_key == "sk-lf-test"
    assert config.langsmith_api_key == "lsv2_test"
    assert config.langsmith_endpoint == "https://api.smith.langchain.com"


# ---------- Task 4: Langfuse provider ----------

def test_langfuse_provider_creates_root_and_child_observations(monkeypatch):
    fake_client = FakeLangfuseClient()
    monkeypatch.setitem(
        sys.modules,
        "langfuse",
        SimpleNamespace(get_client=lambda: fake_client),
    )
    provider = create_trace_provider(
        make_config(
            "langfuse",
            tracing_project="opspilot",
            tracing_public_base_url="https://langfuse.example",
            langfuse_public_key="pk-lf-test",
            langfuse_secret_key="sk-lf-test",
            langfuse_base_url="https://cloud.langfuse.com",
        )
    )

    root = {
        "span_id": "span_root",
        "name": "graph.run",
        "run_id": "run-123",
        "parent_id": None,
    }
    child = {
        "span_id": "span_child",
        "name": "node.node_intake",
        "run_id": "run-123",
        "parent_id": "span_root",
    }

    root_result = provider.start_span(root)
    child_result = provider.start_span(child)
    provider.add_event("span_child", "node_started", {"node_name": "node_intake"})
    provider.end_span({**child, "status": "ok", "duration_ms": 12, "events": []})
    provider.end_span({**root, "status": "ok", "duration_ms": 30, "events": []})
    provider.flush()

    assert provider.name == "langfuse"
    assert root_result.external_trace_id == "trace-run-123"
    assert root_result.external_trace_url == "https://langfuse.example/project/opspilot/traces/trace-run-123"
    assert child_result.external_trace_id == "trace-run-123"
    assert fake_client.started[0][0]["trace_id"] == "trace-run-123"
    root_observation = fake_client.started[0][1]
    assert root_observation.children[0][0]["name"] == "node.node_intake"
    assert root_observation.children[0][1].ended is True
    assert root_observation.ended is True
    assert fake_client.flushed is True


# ---------- Task 5: LangSmith provider ----------

def test_langsmith_provider_creates_root_and_child_runs(monkeypatch):
    fake_client_holder = {}

    def make_client(api_key=None, api_url=None):
        client = FakeLangSmithClient(api_key=api_key, api_url=api_url)
        fake_client_holder["client"] = client
        return client

    monkeypatch.setitem(sys.modules, "langsmith", SimpleNamespace(Client=make_client))
    monkeypatch.setitem(sys.modules, "langsmith.run_trees", SimpleNamespace(RunTree=FakeRunTree))
    FakeRunTree.counter = 0

    provider = create_trace_provider(
        make_config(
            "langsmith",
            tracing_project="opspilot",
            tracing_public_base_url="https://smith.example",
            langsmith_api_key="lsv2_test",
            langsmith_endpoint="https://api.smith.example",
        )
    )

    root = {
        "span_id": "span_root",
        "name": "graph.run",
        "run_id": "run-123",
        "parent_id": None,
    }
    child = {
        "span_id": "span_tool",
        "name": "tool.query_logs",
        "run_id": "run-123",
        "parent_id": "span_root",
    }

    root_result = provider.start_span(root)
    child_result = provider.start_span(child)
    provider.add_event("span_tool", "tool_called", {"params": {"service": "payment-service"}})
    provider.end_span({**child, "status": "ok", "duration_ms": 10, "events": []})
    provider.end_span({**root, "status": "ok", "duration_ms": 20, "events": []})
    provider.flush()

    assert provider.name == "langsmith"
    assert fake_client_holder["client"].api_key == "lsv2_test"
    assert fake_client_holder["client"].api_url == "https://api.smith.example"
    assert root_result.external_trace_id == "run-tree-1"
    assert child_result.external_span_id == "run-tree-2"
    assert root_result.external_trace_url == "https://smith.example/o/opspilot/projects/p/default/r/run-tree-1?trace_id=run-tree-1"
    root_run = provider._runs.get("span_root")
    assert root_run is None
    assert fake_client_holder["client"].flushed is True
