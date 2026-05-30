# External Tracing Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect OpsPilot's existing local tracing spans to LangSmith or Langfuse so a run can be replayed in an external tracing console.

**Architecture:** Keep `backend/app/tracing.py` as the single tracing API used by GraphRunner, ToolGateway, and LLMClient. Add a small provider boundary in `backend/app/tracing_providers.py`; the local tracer remains the source of truth for API responses, and external providers receive best-effort span/event lifecycle calls without breaking graph execution if the vendor SDK fails. The API returns local spans plus provider metadata and an external trace URL when configured.

**Tech Stack:** Python 3, FastAPI, Pydantic Settings, pytest, LangSmith Python SDK, Langfuse Python SDK, React/Vitest for type and UI alignment.

---

## Scope

This plan implements only Phase 7 external tracing provider integration from `ACTION_PLAN.md`. It does not implement Phase 8 offline evals, Phase 9 prompt/RAG evaluation, or Phase 10 Redis/job queues.

The current code already has:

- Local in-memory tracing in `backend/app/tracing.py`
- Span creation in `backend/app/services/graph_runner.py`
- Tool spans in `backend/app/tools/gateway.py`
- LLM spans in `backend/app/llm_client.py`
- `GET /incidents/runs/{run_id}/trace`
- Frontend `View Trace` link in `frontend/src/pages/RunDetailPage.tsx`

External references checked before writing this plan:

- Langfuse Python SDK uses `langfuse = get_client()`, `start_as_current_observation(...)`, and `flush()` for short-lived processes: https://langfuse.com/docs/observability/get-started
- Langfuse Python SDK v4 keeps unified observation APIs such as `start_observation(...)` / `start_as_current_observation(...)`: https://langfuse.com/docs/observability/sdk/upgrade-path/python-v3-to-v4
- LangSmith custom instrumentation supports `@traceable`, `trace`, and low-level `RunTree`: https://docs.langchain.com/langsmith/annotate-code
- LangSmith configuration uses `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, and `LANGSMITH_PROJECT`: https://docs.langchain.com/langsmith/trace-without-env-vars

## File Structure

- Create `backend/app/tracing_providers.py`
  - Defines the provider protocol, no-op local provider, provider result models, `LangfuseTraceProvider`, `LangSmithTraceProvider`, and `create_trace_provider(settings)`.
  - Owns all optional imports from Langfuse/LangSmith so the rest of the backend does not directly depend on either SDK.

- Modify `backend/app/tracing.py`
  - Keeps the existing `AgentTracer` public methods.
  - Adds provider lifecycle calls in `start_span`, `add_event`, `end_span`, and `flush`.
  - Stores provider metadata per span and exposes `get_trace_metadata(run_id)`.
  - Fails open when provider calls fail.

- Modify `backend/app/core/config.py`
  - Adds LangSmith and Langfuse credentials/config fields.
  - Adds production validation for `TRACING_PROVIDER=langsmith|langfuse`.

- Modify `backend/app/api/incidents.py`
  - Extends `RunTraceResponse` with `external_trace_id`, `external_root_span_id`, and `external_trace_url`.
  - Builds trace URLs from tracer metadata first, then deterministic settings fallback, then local URL fallback.

- Modify `backend/app/main.py`
  - Calls `tracer.flush()` during FastAPI shutdown so queued vendor SDK events are submitted.

- Modify `backend/requirements.txt`
  - Installs optional provider SDKs as normal backend dependencies because provider selection is runtime configuration.

- Modify `frontend/src/types/index.ts`
  - Adds optional external trace fields to `RunTrace`.

- Modify `frontend/src/pages/RunDetailPage.tsx`
  - Keeps the existing `View Trace` action, but uses `external_trace_url` before `trace_url`.

- Tests:
  - Create `backend/app/tests/test_tracing_providers.py`
  - Modify `backend/app/tests/test_incidents_api.py`
  - Modify `frontend/src/pages/RunDetailPage.test.tsx`

---

### Task 1: Provider Boundary and Factory

**Files:**
- Create: `backend/app/tracing_providers.py`
- Test: `backend/app/tests/test_tracing_providers.py`

- [ ] **Step 1: Write failing tests for provider factory behavior**

Create `backend/app/tests/test_tracing_providers.py` with this initial content:

```python
import sys
from types import SimpleNamespace

import pytest

from app.tracing_providers import (
    LocalTraceProvider,
    TraceProviderConfig,
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.tracing_providers'`.

- [ ] **Step 3: Add provider boundary implementation**

Create `backend/app/tracing_providers.py`:

```python
"""External tracing provider adapters for OpsPilot.

The local tracer owns the in-process span list. Provider adapters receive
best-effort lifecycle notifications and must never be imported by graph nodes.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TraceProviderConfig:
    tracing_provider: str = "local"
    tracing_project: str = "opspilot"
    tracing_base_url: str = ""
    tracing_public_base_url: str = ""
    langsmith_api_key: str = ""
    langsmith_endpoint: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = ""


@dataclass(frozen=True)
class ProviderSpanResult:
    external_trace_id: Optional[str] = None
    external_span_id: Optional[str] = None
    external_trace_url: Optional[str] = None


class TraceProvider(Protocol):
    name: str

    def start_span(self, span: Dict[str, Any]) -> ProviderSpanResult:
        ...

    def add_event(self, span_id: str, event_name: str, data: Dict[str, Any]) -> None:
        ...

    def end_span(self, span: Dict[str, Any]) -> None:
        ...

    def get_trace_url(self, run_id: str) -> Optional[str]:
        ...

    def flush(self) -> None:
        ...


class LocalTraceProvider:
    name = "local"

    def start_span(self, span: Dict[str, Any]) -> ProviderSpanResult:
        return ProviderSpanResult()

    def add_event(self, span_id: str, event_name: str, data: Dict[str, Any]) -> None:
        return None

    def end_span(self, span: Dict[str, Any]) -> None:
        return None

    def get_trace_url(self, run_id: str) -> Optional[str]:
        return None

    def flush(self) -> None:
        return None


def config_from_settings(settings: Any) -> TraceProviderConfig:
    return TraceProviderConfig(
        tracing_provider=getattr(settings, "tracing_provider", "local"),
        tracing_project=getattr(settings, "tracing_project", "opspilot"),
        tracing_base_url=getattr(settings, "tracing_base_url", ""),
        tracing_public_base_url=getattr(settings, "tracing_public_base_url", ""),
        langsmith_api_key=getattr(settings, "langsmith_api_key", ""),
        langsmith_endpoint=getattr(settings, "langsmith_endpoint", ""),
        langfuse_public_key=getattr(settings, "langfuse_public_key", ""),
        langfuse_secret_key=getattr(settings, "langfuse_secret_key", ""),
        langfuse_base_url=getattr(settings, "langfuse_base_url", ""),
    )


def _seed_env_if_missing(key: str, value: str) -> None:
    if value and not os.getenv(key):
        os.environ[key] = value


def create_trace_provider(config: TraceProviderConfig) -> TraceProvider:
    provider = config.tracing_provider.lower().strip()

    if provider == "langfuse":
        if not config.langfuse_public_key or not config.langfuse_secret_key:
            logger.warning("Langfuse tracing selected without Langfuse credentials")
            return LocalTraceProvider()
        return LangfuseTraceProvider(config)

    if provider == "langsmith":
        if not config.langsmith_api_key:
            logger.warning("LangSmith tracing selected without LANGSMITH_API_KEY")
            return LocalTraceProvider()
        return LangSmithTraceProvider(config)

    return LocalTraceProvider()


class LangfuseTraceProvider:
    name = "langfuse"

    def __init__(self, config: TraceProviderConfig):
        self.config = config
        self._observations: Dict[str, Any] = {}
        self._trace_ids_by_run: Dict[str, str] = {}
        self._trace_urls_by_run: Dict[str, str] = {}

        _seed_env_if_missing("LANGFUSE_PUBLIC_KEY", config.langfuse_public_key)
        _seed_env_if_missing("LANGFUSE_SECRET_KEY", config.langfuse_secret_key)
        _seed_env_if_missing("LANGFUSE_BASE_URL", config.langfuse_base_url)

        from langfuse import get_client

        self.client = get_client()

    def _base_url(self) -> str:
        return (
            self.config.tracing_public_base_url
            or self.config.tracing_base_url
            or self.config.langfuse_base_url
            or os.getenv("LANGFUSE_BASE_URL", "")
            or "https://cloud.langfuse.com"
        ).rstrip("/")

    def _trace_id_for_run(self, run_id: str) -> str:
        if run_id in self._trace_ids_by_run:
            return self._trace_ids_by_run[run_id]
        if hasattr(self.client, "create_trace_id"):
            trace_id = self.client.create_trace_id(seed=run_id)
        else:
            trace_id = run_id
        self._trace_ids_by_run[run_id] = trace_id
        self._trace_urls_by_run[run_id] = f"{self._base_url()}/project/{self.config.tracing_project}/traces/{trace_id}"
        return trace_id

    def start_span(self, span: Dict[str, Any]) -> ProviderSpanResult:
        run_id = span.get("run_id") or "unknown-run"
        trace_id = self._trace_id_for_run(run_id)
        parent_id = span.get("parent_id")
        parent_observation = self._observations.get(parent_id) if parent_id else None
        observation_kwargs = {
            "name": span["name"],
            "as_type": "span",
            "input": {
                "run_id": run_id,
                "local_span_id": span["span_id"],
                "parent_id": parent_id,
            },
            "metadata": {"project": self.config.tracing_project},
        }
        if parent_observation and hasattr(parent_observation, "start_observation"):
            observation = parent_observation.start_observation(**observation_kwargs)
        else:
            observation_kwargs["trace_id"] = trace_id
            if hasattr(self.client, "start_observation"):
                observation = self.client.start_observation(**observation_kwargs)
            else:
                observation = self.client.start_span(
                    name=span["name"],
                    input=observation_kwargs["input"],
                    metadata=observation_kwargs["metadata"],
                    trace_id=trace_id,
                )
        self._observations[span["span_id"]] = observation
        external_span_id = getattr(observation, "id", None) or getattr(observation, "observation_id", None)
        return ProviderSpanResult(
            external_trace_id=trace_id,
            external_span_id=external_span_id,
            external_trace_url=self.get_trace_url(run_id),
        )

    def add_event(self, span_id: str, event_name: str, data: Dict[str, Any]) -> None:
        observation = self._observations.get(span_id)
        if not observation:
            return
        if hasattr(observation, "update"):
            observation.update(metadata={"last_event": event_name, "last_event_data": data})

    def end_span(self, span: Dict[str, Any]) -> None:
        observation = self._observations.pop(span["span_id"], None)
        if not observation:
            return
        output = {
            "status": span.get("status"),
            "duration_ms": span.get("duration_ms"),
            "events": span.get("events", []),
        }
        if span.get("error"):
            output["error"] = span["error"]
        if hasattr(observation, "update"):
            observation.update(output=output, metadata={"status": span.get("status")})
        if hasattr(observation, "end"):
            observation.end()

    def get_trace_url(self, run_id: str) -> Optional[str]:
        return self._trace_urls_by_run.get(run_id)

    def flush(self) -> None:
        if hasattr(self.client, "flush"):
            self.client.flush()


class LangSmithTraceProvider:
    name = "langsmith"

    def __init__(self, config: TraceProviderConfig):
        self.config = config
        self._runs: Dict[str, Any] = {}
        self._root_run_ids_by_run: Dict[str, str] = {}

        _seed_env_if_missing("LANGSMITH_API_KEY", config.langsmith_api_key)
        _seed_env_if_missing("LANGSMITH_ENDPOINT", config.langsmith_endpoint)
        _seed_env_if_missing("LANGSMITH_PROJECT", config.tracing_project)
        _seed_env_if_missing("LANGSMITH_TRACING", "true")

        from langsmith import Client

        self.client = Client(
            api_key=config.langsmith_api_key,
            api_url=config.langsmith_endpoint or None,
        )

    def _base_url(self) -> str:
        return (
            self.config.tracing_public_base_url
            or self.config.tracing_base_url
            or "https://smith.langchain.com"
        ).rstrip("/")

    def _run_type(self, name: str) -> str:
        if name.startswith("tool."):
            return "tool"
        if name.startswith("llm."):
            return "llm"
        return "chain"

    def start_span(self, span: Dict[str, Any]) -> ProviderSpanResult:
        from langsmith.run_trees import RunTree

        parent_id = span.get("parent_id")
        parent_run = self._runs.get(parent_id) if parent_id else None
        run_kwargs = {
            "name": span["name"],
            "run_type": self._run_type(span["name"]),
            "inputs": {
                "run_id": span.get("run_id"),
                "local_span_id": span["span_id"],
                "parent_id": parent_id,
            },
            "project_name": self.config.tracing_project,
            "client": self.client,
        }
        if parent_run and hasattr(parent_run, "create_child"):
            run_tree = parent_run.create_child(**run_kwargs)
        else:
            run_tree = RunTree(**run_kwargs)
        run_tree.post()
        self._runs[span["span_id"]] = run_tree

        run_id = span.get("run_id") or ""
        external_run_id = str(getattr(run_tree, "id", ""))
        if run_id and not parent_id:
            self._root_run_ids_by_run[run_id] = external_run_id

        return ProviderSpanResult(
            external_trace_id=self._root_run_ids_by_run.get(run_id) or external_run_id,
            external_span_id=external_run_id,
            external_trace_url=self.get_trace_url(run_id),
        )

    def add_event(self, span_id: str, event_name: str, data: Dict[str, Any]) -> None:
        run_tree = self._runs.get(span_id)
        if not run_tree:
            return
        extra = getattr(run_tree, "extra", None) or {}
        events = list(extra.get("events", []))
        events.append({"name": event_name, "data": data})
        run_tree.extra = {**extra, "events": events}

    def end_span(self, span: Dict[str, Any]) -> None:
        run_tree = self._runs.pop(span["span_id"], None)
        if not run_tree:
            return
        output = {
            "status": span.get("status"),
            "duration_ms": span.get("duration_ms"),
            "events": span.get("events", []),
        }
        if span.get("error"):
            output["error"] = span["error"]
            run_tree.end(outputs=output, error=span["error"])
        else:
            run_tree.end(outputs=output)
        run_tree.patch()

    def get_trace_url(self, run_id: str) -> Optional[str]:
        root_run_id = self._root_run_ids_by_run.get(run_id)
        if not root_run_id:
            return None
        return f"{self._base_url()}/o/{self.config.tracing_project}/projects/p/default/runs/{root_run_id}"

    def flush(self) -> None:
        if hasattr(self.client, "flush"):
            self.client.flush()
```

- [ ] **Step 4: Run tests to verify provider factory passes**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py -q
```

Expected: PASS with `3 passed`.

- [ ] **Step 5: Commit provider boundary**

Run:

```bash
git add backend/app/tracing_providers.py backend/app/tests/test_tracing_providers.py
git commit -m "backend: add tracing provider boundary"
```

Expected: commit succeeds.

---

### Task 2: Wire Provider Lifecycle Into AgentTracer

**Files:**
- Modify: `backend/app/tracing.py`
- Modify: `backend/app/tests/test_tracing_providers.py`

- [ ] **Step 1: Add failing tests for external metadata and fail-open provider calls**

Append these tests to `backend/app/tests/test_tracing_providers.py`:

```python
from app.tracing import AgentTracer
from app.tracing_providers import ProviderSpanResult


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py -q
```

Expected: FAIL with `TypeError: AgentTracer.__init__() got an unexpected keyword argument 'provider'`.

- [ ] **Step 3: Modify `AgentTracer` to call provider lifecycle hooks**

Replace `backend/app/tracing.py` with:

```python
"""Observability utilities for the agent system."""

from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any, Dict, Optional

from app.tracing_providers import (
    LocalTraceProvider,
    TraceProvider,
    config_from_settings,
    create_trace_provider,
)

logger = logging.getLogger(__name__)

run_id_var: ContextVar[Optional[str]] = ContextVar("run_id", default=None)
step_id_var: ContextVar[Optional[str]] = ContextVar("step_id", default=None)


class AgentTracer:
    """Local span recorder with optional external provider forwarding."""

    def __init__(self, provider: Optional[TraceProvider] = None):
        self.spans: list[Dict[str, Any]] = []
        self.provider: TraceProvider = provider or self._build_provider_from_settings()

    def _build_provider_from_settings(self) -> TraceProvider:
        try:
            from app.core.config import get_settings

            return create_trace_provider(config_from_settings(get_settings()))
        except Exception:
            logger.warning("Failed to initialize external tracing provider", exc_info=True)
            return LocalTraceProvider()

    def configure_provider(self, provider: TraceProvider) -> None:
        self.provider = provider

    def start_span(
        self,
        name: str,
        run_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        span_id = f"span_{uuid.uuid4().hex[:8]}"
        span = {
            "span_id": span_id,
            "name": name,
            "run_id": run_id or run_id_var.get(),
            "parent_id": parent_id,
            "start_time": time.time(),
            "start_timestamp": datetime.now(UTC).isoformat(),
        }
        self.spans.append(span)
        try:
            provider_result = self.provider.start_span(span.copy())
            if provider_result.external_trace_id:
                span["external_trace_id"] = provider_result.external_trace_id
            if provider_result.external_span_id:
                span["external_span_id"] = provider_result.external_span_id
            if provider_result.external_trace_url:
                span["external_trace_url"] = provider_result.external_trace_url
        except Exception:
            logger.warning("External tracing start_span failed", exc_info=True)
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "ok",
        error: Optional[str] = None,
    ):
        for span in self.spans:
            if span["span_id"] == span_id:
                span["end_time"] = time.time()
                span["duration_ms"] = int((span["end_time"] - span["start_time"]) * 1000)
                span["end_timestamp"] = datetime.now(UTC).isoformat()
                span["status"] = status
                if error:
                    span["error"] = error
                try:
                    self.provider.end_span(span.copy())
                except Exception:
                    logger.warning("External tracing end_span failed", exc_info=True)
                break

    def add_event(self, span_id: str, event_name: str, data: Optional[Dict[str, Any]] = None):
        event_data = data or {}
        for span in self.spans:
            if span["span_id"] == span_id:
                if "events" not in span:
                    span["events"] = []
                span["events"].append(
                    {
                        "name": event_name,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "data": event_data,
                    }
                )
                try:
                    self.provider.add_event(span_id, event_name, event_data)
                except Exception:
                    logger.warning("External tracing add_event failed", exc_info=True)
                break

    def get_spans(self, run_id: Optional[str] = None) -> list[Dict[str, Any]]:
        if run_id:
            return [s for s in self.spans if s.get("run_id") == run_id]
        return self.spans

    def get_trace_metadata(self, run_id: str) -> Dict[str, Optional[str]]:
        spans = self.get_spans(run_id)
        root_span = next((span for span in spans if not span.get("parent_id")), None)
        external_trace_url = None
        try:
            external_trace_url = self.provider.get_trace_url(run_id)
        except Exception:
            logger.warning("External tracing get_trace_url failed", exc_info=True)
        if not external_trace_url and root_span:
            external_trace_url = root_span.get("external_trace_url")
        return {
            "provider": getattr(self.provider, "name", "local"),
            "external_trace_id": root_span.get("external_trace_id") if root_span else None,
            "external_root_span_id": root_span.get("external_span_id") if root_span else None,
            "external_trace_url": external_trace_url,
        }

    def get_active_span_id(self) -> Optional[str]:
        return step_id_var.get()

    def set_run_context(self, run_id: str):
        return run_id_var.set(run_id)

    def reset_run_context(self, token) -> None:
        run_id_var.reset(token)

    def set_step_context(self, span_id: Optional[str]):
        return step_id_var.set(span_id)

    def reset_step_context(self, token) -> None:
        step_id_var.reset(token)

    def flush(self) -> None:
        try:
            self.provider.flush()
        except Exception:
            logger.warning("External tracing flush failed", exc_info=True)

    def clear(self):
        self.spans.clear()


tracer = AgentTracer()
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py app/tests/test_tool_gateway.py app/tests/test_incidents_api.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit tracer lifecycle wiring**

Run:

```bash
git add backend/app/tracing.py backend/app/tests/test_tracing_providers.py
git commit -m "backend: forward local spans to tracing providers"
```

Expected: commit succeeds.

---

### Task 3: Configuration and Dependencies

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/requirements.txt`
- Modify: `backend/app/tests/test_tracing_providers.py`

- [ ] **Step 1: Add failing tests for settings-to-provider config**

Append this test to `backend/app/tests/test_tracing_providers.py`:

```python
from app.core.config import Settings
from app.tracing_providers import config_from_settings


def test_config_from_settings_reads_external_tracing_fields():
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py::test_config_from_settings_reads_external_tracing_fields -q
```

Expected: FAIL because `Settings` does not yet define the new LangSmith/Langfuse fields.

- [ ] **Step 3: Add tracing configuration fields and production validation**

In `backend/app/core/config.py`, extend the tracing section:

```python
    tracing_provider: str = "local"
    tracing_project: str = "opspilot"
    tracing_base_url: str = ""
    tracing_public_base_url: str = ""
    langsmith_api_key: str = ""
    langsmith_endpoint: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = ""
```

Then add this validation block inside `validate_for_production`, after LLM validation:

```python
        tracing_provider = self.tracing_provider.lower()
        if tracing_provider == "langsmith" and self.app_env != AppEnv.DEV:
            if not self.langsmith_api_key:
                errors.append("LANGSMITH_API_KEY is required when TRACING_PROVIDER=langsmith")
        if tracing_provider == "langfuse" and self.app_env != AppEnv.DEV:
            if not self.langfuse_public_key or not self.langfuse_secret_key:
                errors.append(
                    "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are required when "
                    "TRACING_PROVIDER=langfuse"
                )
```

- [ ] **Step 4: Add SDK dependencies**

In `backend/requirements.txt`, replace:

```text
# Observability (Optional)
# langsmith==0.1.0
# langfuse==2.0.0
```

with:

```text
# Observability
langsmith>=0.3.18
langfuse>=3.0.0
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py -q
```

Expected: PASS.

- [ ] **Step 6: Install dependencies and run import check**

Run:

```bash
cd backend && python -m pip install -r requirements.txt
python - <<'PY'
import langsmith
import langfuse
print("observability imports ok")
PY
```

Expected output includes:

```text
observability imports ok
```

- [ ] **Step 7: Commit configuration and dependencies**

Run:

```bash
git add backend/app/core/config.py backend/requirements.txt backend/app/tests/test_tracing_providers.py
git commit -m "backend: add external tracing configuration"
```

Expected: commit succeeds.

---

### Task 4: Langfuse Provider Tests

**Files:**
- Modify: `backend/app/tests/test_tracing_providers.py`
- Modify: `backend/app/tracing_providers.py`

- [ ] **Step 1: Add failing Langfuse provider tests using a fake SDK module**

Append this test to `backend/app/tests/test_tracing_providers.py`:

```python
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
```

- [ ] **Step 2: Run Langfuse test**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py::test_langfuse_provider_creates_root_and_child_observations -q
```

Expected: PASS if Task 1 implementation already included `LangfuseTraceProvider`. If it fails because the SDK method name changed, update `LangfuseTraceProvider.start_span` with this compatibility branch:

```python
            if hasattr(self.client, "start_observation"):
                observation = self.client.start_observation(**observation_kwargs)
            elif hasattr(self.client, "start_span"):
                observation = self.client.start_span(
                    name=span["name"],
                    input=observation_kwargs["input"],
                    metadata=observation_kwargs["metadata"],
                    trace_id=trace_id,
                )
            else:
                raise RuntimeError("Langfuse client does not expose observation start API")
```

- [ ] **Step 3: Run all provider tests**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py -q
```

Expected: PASS.

- [ ] **Step 4: Commit Langfuse provider tests**

Run:

```bash
git add backend/app/tracing_providers.py backend/app/tests/test_tracing_providers.py
git commit -m "backend: verify langfuse tracing provider"
```

Expected: commit succeeds.

---

### Task 5: LangSmith Provider Tests

**Files:**
- Modify: `backend/app/tests/test_tracing_providers.py`
- Modify: `backend/app/tracing_providers.py`

- [ ] **Step 1: Add failing LangSmith provider tests using fake SDK modules**

Append this test to `backend/app/tests/test_tracing_providers.py`:

```python
class FakeLangSmithClient:
    def __init__(self, api_key=None, api_url=None):
        self.api_key = api_key
        self.api_url = api_url
        self.flushed = False

    def flush(self):
        self.flushed = True


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
    assert root_result.external_trace_url == "https://smith.example/o/opspilot/projects/p/default/runs/run-tree-1"
    root_run = provider._runs.get("span_root")
    assert root_run is None
    assert fake_client_holder["client"].flushed is True
```

- [ ] **Step 2: Run LangSmith test**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py::test_langsmith_provider_creates_root_and_child_runs -q
```

Expected: PASS if Task 1 implementation already included `LangSmithTraceProvider`. If it fails because `RunTree` requires a different client argument name, update the provider and fake together so `RunTree` construction receives `client=self.client`, `project_name=config.tracing_project`, and `run_type` based on span name.

- [ ] **Step 3: Run all provider tests**

Run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py -q
```

Expected: PASS.

- [ ] **Step 4: Commit LangSmith provider tests**

Run:

```bash
git add backend/app/tracing_providers.py backend/app/tests/test_tracing_providers.py
git commit -m "backend: verify langsmith tracing provider"
```

Expected: commit succeeds.

---

### Task 6: Trace API Metadata and Shutdown Flush

**Files:**
- Modify: `backend/app/api/incidents.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/tests/test_incidents_api.py`

- [ ] **Step 1: Add failing API response test for external trace metadata**

Append this test to `backend/app/tests/test_incidents_api.py`:

```python
from app.tracing_providers import ProviderSpanResult


class ApiTraceProvider:
    name = "recording"

    def start_span(self, span):
        return ProviderSpanResult(
            external_trace_id="external-trace-run-123",
            external_span_id="external-root-span",
            external_trace_url="https://trace.example/run-123",
        )

    def add_event(self, span_id, event_name, data):
        return None

    def end_span(self, span):
        return None

    def get_trace_url(self, run_id):
        return f"https://trace.example/{run_id}"

    def flush(self):
        return None


def test_get_run_trace_returns_external_trace_metadata():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)
    tracer.clear()
    tracer.configure_provider(ApiTraceProvider())
    span_id = tracer.start_span("graph.run", run_id="run-123")
    tracer.end_span(span_id)

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/trace")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "recording"
    assert payload["trace_url"] == "https://trace.example/run-123"
    assert payload["external_trace_id"] == "external-trace-run-123"
    assert payload["external_root_span_id"] == "external-root-span"
    assert payload["external_trace_url"] == "https://trace.example/run-123"
    tracer.configure_provider(LocalTraceProvider())
```

- [ ] **Step 2: Run API test to verify it fails**

Run:

```bash
cd backend && pytest app/tests/test_incidents_api.py::test_get_run_trace_returns_external_trace_metadata -q
```

Expected: FAIL because `RunTraceResponse` does not expose the new fields.

- [ ] **Step 3: Extend trace response models and URL helper**

In `backend/app/api/incidents.py`, import `LocalTraceProvider` near the tracer import:

```python
from app.tracing_providers import LocalTraceProvider
```

Extend `RunTraceResponse`:

```python
class RunTraceResponse(BaseModel):
    run_id: str
    provider: str
    trace_url: str
    external_trace_id: Optional[str] = None
    external_root_span_id: Optional[str] = None
    external_trace_url: Optional[str] = None
    spans: List[TraceSpanResponse]
```

Replace `_build_trace_url` with:

```python
def _build_trace_url(run_id: str, external_trace_url: Optional[str] = None) -> str:
    if external_trace_url:
        return external_trace_url

    settings = get_settings()
    base_url = settings.tracing_public_base_url or settings.tracing_base_url
    provider = settings.tracing_provider.lower()
    if provider == "langfuse" and base_url:
        return f"{base_url.rstrip('/')}/project/{settings.tracing_project}/traces/{run_id}"
    if provider == "langsmith" and base_url:
        return f"{base_url.rstrip('/')}/o/{settings.tracing_project}/projects/p/default/runs/{run_id}"
    if base_url:
        return f"{base_url.rstrip('/')}/incidents/runs/{run_id}/trace"
    return f"/incidents/runs/{run_id}/trace"
```

Replace the return body in `get_run_trace`:

```python
    metadata = tracer.get_trace_metadata(run_id)
    provider = metadata.get("provider") or settings.tracing_provider
    external_trace_url = metadata.get("external_trace_url")
    return RunTraceResponse(
        run_id=run_id,
        provider=provider,
        trace_url=_build_trace_url(run_id, external_trace_url),
        external_trace_id=metadata.get("external_trace_id"),
        external_root_span_id=metadata.get("external_root_span_id"),
        external_trace_url=external_trace_url,
        spans=tracer.get_spans(run_id),
    )
```

Update the existing local trace test cleanup in `backend/app/tests/test_incidents_api.py` by adding this line after assertions in both trace tests:

```python
    tracer.configure_provider(LocalTraceProvider())
```

- [ ] **Step 4: Flush tracer during FastAPI shutdown**

In `backend/app/main.py`, import tracer:

```python
from app.tracing import tracer
```

Replace the lifespan function with:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_alembic_upgrade()
    try:
        yield
    finally:
        tracer.flush()
```

- [ ] **Step 5: Run focused backend tests**

Run:

```bash
cd backend && pytest app/tests/test_incidents_api.py app/tests/test_tracing_providers.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit API metadata and shutdown flush**

Run:

```bash
git add backend/app/api/incidents.py backend/app/main.py backend/app/tests/test_incidents_api.py
git commit -m "backend: expose external trace metadata"
```

Expected: commit succeeds.

---

### Task 7: Frontend Trace URL Alignment

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/pages/RunDetailPage.tsx`
- Modify: `frontend/src/pages/RunDetailPage.test.tsx`

- [ ] **Step 1: Add failing frontend test for external trace URL preference**

Append this test to `frontend/src/pages/RunDetailPage.test.tsx`:

```tsx
  it('uses external trace URL for the View Trace action when present', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
    vi.mocked(runsModule.runs.getRunTrace).mockResolvedValue({
      run_id: 'run-123',
      provider: 'langfuse',
      trace_url: '/incidents/runs/run-123/trace',
      external_trace_id: 'trace-run-123',
      external_root_span_id: 'span-root',
      external_trace_url: 'https://langfuse.example/project/opspilot/traces/trace-run-123',
      spans: [],
    } as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('api-gateway')).toBeInTheDocument();
    });

    expect(screen.getByRole('link', { name: 'View Trace' })).toHaveAttribute(
      'href',
      'https://langfuse.example/project/opspilot/traces/trace-run-123',
    );
  });
```

- [ ] **Step 2: Run frontend test to verify it fails**

Run:

```bash
cd frontend && npx vitest run src/pages/RunDetailPage.test.tsx
```

Expected: FAIL because the component uses `runTrace.trace_url`.

- [ ] **Step 3: Extend frontend type**

In `frontend/src/types/index.ts`, replace `RunTrace` with:

```ts
export interface RunTrace {
  run_id: string;
  provider: string;
  trace_url: string;
  external_trace_id?: string;
  external_root_span_id?: string;
  external_trace_url?: string;
  spans: TraceSpan[];
}
```

- [ ] **Step 4: Prefer external URL in the quick action**

In `frontend/src/pages/RunDetailPage.tsx`, add this constant after state declarations:

```tsx
  const traceHref = runTrace?.external_trace_url || runTrace?.trace_url;
```

Replace:

```tsx
              {runTrace?.trace_url && (
                <a
                  href={runTrace.trace_url}
```

with:

```tsx
              {traceHref && (
                <a
                  href={traceHref}
```

- [ ] **Step 5: Run frontend tests**

Run:

```bash
cd frontend && npx vitest run src/pages/RunDetailPage.test.tsx
```

Expected: PASS.

- [ ] **Step 6: Commit frontend alignment**

Run:

```bash
git add frontend/src/types/index.ts frontend/src/pages/RunDetailPage.tsx frontend/src/pages/RunDetailPage.test.tsx
git commit -m "frontend: prefer external trace links"
```

Expected: commit succeeds.

---

### Task 8: Documentation and Phase Status

**Files:**
- Modify: `backend/README.md`
- Modify: `backend/docs/gaps/current.md`
- Modify: `ACTION_PLAN.md`

- [ ] **Step 1: Update backend README adapter status**

In `backend/README.md`, replace the tracing bullets under "真实 adapter 当前进度" with:

```markdown
- 已实现：MySQL 诊断工具、MySQL 应用日志 `query_logs`、K8s 只读工具、`query_metrics`（阿里云 CMS/K8s 指标）、`query_deployments`（K8s deployment 列表与状态）、SLB 健康/流量、OSS RCA/evidence 写归档、本地 tracing 闭环、LangSmith / Langfuse 外部 tracing provider 接入
- 已实现但仍需真实环境联调：RAG 知识检索与写回、各 real adapter 的线上凭证/白名单/region 配置、LangSmith / Langfuse 控制台回放验收
- 尚未实现：离线评测框架、`execute_action` real 模式、`query_runbook` gateway real 模式、`query_ticket_by_id` / `query_service_metadata` 真实数据源
```

Add this section after "Adapter 模式":

```markdown
## Tracing Provider

默认使用本地 tracing：

```bash
TRACING_PROVIDER=local
```

Langfuse：

```bash
TRACING_PROVIDER=langfuse
TRACING_PROJECT=opspilot
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
TRACING_PUBLIC_BASE_URL=https://cloud.langfuse.com
```

LangSmith：

```bash
TRACING_PROVIDER=langsmith
TRACING_PROJECT=opspilot
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
TRACING_PUBLIC_BASE_URL=https://smith.langchain.com
```

`GET /incidents/runs/{run_id}/trace` 会返回本地 span 列表，并在外部 provider 已配置且 run 已产生 span 时返回 `external_trace_id`、`external_root_span_id`、`external_trace_url`。
```

- [ ] **Step 2: Update current gaps**

In `backend/docs/gaps/current.md`, replace the Phase 7 section with:

```markdown
## P1：Phase 7 外部 Tracing Provider

状态：已完成代码接入，待真实控制台验收。

当前已有：

- `backend/app/tracing.py`
- `backend/app/tracing_providers.py`
- `GET /incidents/runs/{run_id}/trace`
- GraphRunner / ToolGateway / LLMClient tracing 埋点
- RunDetailPage trace 外链入口
- LangSmith / Langfuse provider 配置和 best-effort 上报
- API 返回 `external_trace_id`、`external_root_span_id`、`external_trace_url`

剩余验收：

- 使用真实 LangSmith 或 Langfuse 凭证运行一条工单
- 在外部 tracing 控制台打开该 run 的 trace 页面
- 确认 trace 包含 graph、node、tool、llm span
```

- [ ] **Step 3: Update ACTION_PLAN Phase 7**

In `ACTION_PLAN.md`, update the top status line from:

```markdown
> Phase 1-6 已完成；当前处于 Phase 7（可观测性接入）。本地 tracing 闭环已完成，下一步是接入 LangSmith / Langfuse 外部 provider；Phase 8 离线评测尚未启动。
```

to:

```markdown
> Phase 1-7 已完成代码接入；LangSmith / Langfuse 外部 provider 已落地，仍需真实控制台回放验收；Phase 8 离线评测尚未启动。
```

Update the Phase 7 heading:

```markdown
## Phase 7: 可观测性接入（P1，预计 1-2 天） — ✅ 已完成代码接入，待真实控制台验收
```

Update the Phase 7 current progress block:

```markdown
**当前进度（2026-05-30）**:
- 已完成本地 tracing 基础闭环：
  - `backend/app/tracing.py` 已支持 span / event 记录与 run 级上下文
  - `GraphRunner`、`ToolGateway`、`LLMClient` 已接入关键 span 埋点
  - 新增 `GET /incidents/runs/{run_id}/trace`
  - `RunDetailPage` 已增加 `View Trace` 快捷入口
- 已完成外部 provider 代码接入：
  - 新增 `backend/app/tracing_providers.py`
  - 支持 `TRACING_PROVIDER=langfuse`
  - 支持 `TRACING_PROVIDER=langsmith`
  - API 返回 `external_trace_id`、`external_root_span_id`、`external_trace_url`
  - FastAPI shutdown 会 flush provider
- 尚需真实环境验收：
  - 配置 LangSmith / Langfuse 真实凭证
  - 运行一条工单并在外部控制台确认完整 trace 可回放
```

- [ ] **Step 4: Commit documentation updates**

Run:

```bash
git add ACTION_PLAN.md backend/README.md backend/docs/gaps/current.md
git commit -m "docs: update external tracing progress"
```

Expected: commit succeeds.

---

### Task 9: End-to-End Verification

**Files:**
- No source edits in this task.

- [ ] **Step 1: Run full backend tests**

Run:

```bash
cd backend && pytest app/tests/ -x -q
```

Expected: PASS.

- [ ] **Step 2: Run frontend tests**

Run:

```bash
cd frontend && npx vitest run
```

Expected: PASS.

- [ ] **Step 3: Run local trace smoke test**

Start backend:

```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
```

In a separate terminal, create a manual run:

```bash
curl -s -X POST http://127.0.0.1:8000/incidents/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket": {
      "ticket_id": "INC-TRACE-LOCAL",
      "title": "支付服务5xx升高",
      "description": "发布后部分用户下单失败",
      "service": "payment-service",
      "env": "staging",
      "severity": "P2",
      "source": "manual"
    }
  }' | python3 -m json.tool
```

Copy the returned `run_id`, then check trace:

```bash
curl -s http://127.0.0.1:8000/incidents/runs/<run_id>/trace | python3 -m json.tool
```

Expected JSON contains:

```json
{
  "provider": "local",
  "trace_url": "/incidents/runs/<run_id>/trace",
  "spans": [
    {
      "name": "graph.run"
    }
  ]
}
```

- [ ] **Step 4: Run one Langfuse smoke test when credentials are available**

Configure:

```bash
cd backend
export TRACING_PROVIDER=langfuse
export TRACING_PROJECT=opspilot
export LANGFUSE_PUBLIC_KEY=pk-lf-real
export LANGFUSE_SECRET_KEY=sk-lf-real
export LANGFUSE_BASE_URL=https://cloud.langfuse.com
export TRACING_PUBLIC_BASE_URL=https://cloud.langfuse.com
uvicorn app.main:app --reload --port 8000
```

Create one run using the same POST command from Step 3, then inspect:

```bash
curl -s http://127.0.0.1:8000/incidents/runs/<run_id>/trace | python3 -m json.tool
```

Expected JSON contains:

```json
{
  "provider": "langfuse",
  "external_trace_id": "non-empty",
  "external_root_span_id": "non-empty",
  "external_trace_url": "https://cloud.langfuse.com/project/opspilot/traces/non-empty"
}
```

Open `external_trace_url` and verify the console shows spans named `graph.run`, `node.*`, `tool.*`, and `llm.*` when that run exercised those paths.

- [ ] **Step 5: Run one LangSmith smoke test when credentials are available**

Configure:

```bash
cd backend
export TRACING_PROVIDER=langsmith
export TRACING_PROJECT=opspilot
export LANGSMITH_API_KEY=lsv2_real
export LANGSMITH_ENDPOINT=https://api.smith.langchain.com
export TRACING_PUBLIC_BASE_URL=https://smith.langchain.com
uvicorn app.main:app --reload --port 8000
```

Create one run using the same POST command from Step 3, then inspect:

```bash
curl -s http://127.0.0.1:8000/incidents/runs/<run_id>/trace | python3 -m json.tool
```

Expected JSON contains:

```json
{
  "provider": "langsmith",
  "external_trace_id": "non-empty",
  "external_root_span_id": "non-empty",
  "external_trace_url": "https://smith.langchain.com/o/opspilot/projects/p/default/runs/non-empty"
}
```

Open `external_trace_url` and verify the console shows spans named `graph.run`, `node.*`, `tool.*`, and `llm.*` when that run exercised those paths.

- [ ] **Step 6: Commit any smoke-test documentation correction**

If the real Langfuse or LangSmith console URL format differs from the generated URL, update only `LangfuseTraceProvider.get_trace_url`, `LangSmithTraceProvider.get_trace_url`, and the README examples. Then run:

```bash
cd backend && pytest app/tests/test_tracing_providers.py app/tests/test_incidents_api.py -q
git add backend/app/tracing_providers.py backend/README.md backend/app/tests/test_tracing_providers.py backend/app/tests/test_incidents_api.py
git commit -m "backend: align external trace urls with provider console"
```

Expected: tests pass and commit succeeds.

---

## Self-Review

Spec coverage:

- Phase 7 external provider code path: covered by Tasks 1-6.
- LangSmith provider: covered by Tasks 3, 5, 6, 8, and 9.
- Langfuse provider: covered by Tasks 3, 4, 6, 8, and 9.
- GraphRunner / ToolGateway / LLMClient capture: existing code remains the instrumentation surface; Task 2 provider forwarding makes all existing spans visible externally.
- RunDetailPage trace link: covered by Task 7.
- External control console validation: covered by Task 9.

Red-flag scan:

- No undefined-marker strings are present.
- No empty implementation steps are present.
- Each code-changing task includes concrete file paths, test commands, and code blocks.

Type consistency:

- Backend response fields are `external_trace_id`, `external_root_span_id`, and `external_trace_url` in Python and TypeScript.
- Provider metadata method is consistently named `get_trace_metadata(run_id)`.
- Provider factory input type is consistently named `TraceProviderConfig`.
