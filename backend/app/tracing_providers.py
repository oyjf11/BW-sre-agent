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
            elif hasattr(self.client, "start_span"):
                observation = self.client.start_span(
                    name=span["name"],
                    input=observation_kwargs["input"],
                    metadata=observation_kwargs["metadata"],
                    trace_id=trace_id,
                )
            else:
                raise RuntimeError("Langfuse client does not expose observation start API")
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
        self._trace_urls_by_run: Dict[str, str] = {}
        self._org_id: Optional[str] = None
        self._project_id: Optional[str] = None

        _seed_env_if_missing("LANGSMITH_API_KEY", config.langsmith_api_key)
        _seed_env_if_missing("LANGSMITH_ENDPOINT", config.langsmith_endpoint)
        _seed_env_if_missing("LANGSMITH_PROJECT", config.tracing_project)
        _seed_env_if_missing("LANGSMITH_TRACING", "true")

        from langsmith import Client

        self.client = Client(
            api_key=config.langsmith_api_key,
            api_url=config.langsmith_endpoint or None,
        )

        try:
            runs = list(self.client.list_runs(project_name=config.tracing_project, limit=1))
            if runs:
                run_url = runs[0].url
                if "/o/" in run_url:
                    o_start = run_url.index("/o/") + len("/o/")
                    o_end = run_url.index("/", o_start)
                    self._org_id = run_url[o_start:o_end]
                if "/projects/p/" in run_url:
                    prefix = run_url.index("/projects/p/") + len("/projects/p/")
                    proj_end = run_url.index("/", prefix)
                    self._project_id = run_url[prefix:proj_end]
        except Exception:
            logger.warning("Failed to resolve LangSmith org/project IDs", exc_info=True)

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
            child_kwargs = {
                k: v for k, v in run_kwargs.items()
                if k not in ("project_name", "client")
            }
            run_tree = parent_run.create_child(**child_kwargs)
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
        cached = self._trace_urls_by_run.get(run_id)
        if cached:
            return cached
        root_run_id = self._root_run_ids_by_run.get(run_id)
        if not root_run_id or not self._org_id or not self._project_id:
            return None
        return (
            f"{self._base_url()}/o/{self._org_id}/projects/p/{self._project_id}"
            f"/r/{root_run_id}?trace_id={root_run_id}"
        )

    def flush(self) -> None:
        if hasattr(self.client, "flush"):
            self.client.flush()
