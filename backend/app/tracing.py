"""Observability utilities for the agent system."""
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from contextvars import ContextVar

run_id_var: ContextVar[Optional[str]] = ContextVar("run_id", default=None)
step_id_var: ContextVar[Optional[str]] = ContextVar("step_id", default=None)


class AgentTracer:
    """Simple tracer for agent execution."""
    
    def __init__(self):
        self.spans: list[Dict[str, Any]] = []
    
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
            "start_timestamp": datetime.utcnow().isoformat(),
        }
        self.spans.append(span)
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
                span["end_timestamp"] = datetime.utcnow().isoformat()
                span["status"] = status
                if error:
                    span["error"] = error
                break
    
    def add_event(self, span_id: str, event_name: str, data: Dict[str, Any] = None):
        for span in self.spans:
            if span["span_id"] == span_id:
                if "events" not in span:
                    span["events"] = []
                span["events"].append({
                    "name": event_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data or {},
                })
                break
    
    def get_spans(self, run_id: Optional[str] = None) -> list[Dict[str, Any]]:
        if run_id:
            return [s for s in self.spans if s.get("run_id") == run_id]
        return self.spans
    
    def clear(self):
        self.spans.clear()


tracer = AgentTracer()
