"""Observability utilities for the agent system."""

from __future__ import annotations

import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
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
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
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
                span["end_timestamp"] = datetime.now(timezone.utc).isoformat()
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
                        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        run_id_var.set(None)

    def set_step_context(self, span_id: Optional[str]):
        return step_id_var.set(span_id)

    def reset_step_context(self, token) -> None:
        step_id_var.set(None)

    def flush(self) -> None:
        try:
            self.provider.flush()
        except Exception:
            logger.warning("External tracing flush failed", exc_info=True)

    def clear(self):
        self.spans.clear()


tracer = AgentTracer()
