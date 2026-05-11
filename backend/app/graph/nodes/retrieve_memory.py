"""Memory retrieval node: fetches relevant runbooks, historical RCA, service docs, alert experience."""

import logging
from typing import List

from app.graph.state import IncidentAgentState
from app.models.planning import MemoryHit
from app.tools import ToolRequest, gateway

logger = logging.getLogger(__name__)


async def _retrieve_from_source(source: str, tool_name: str, params: dict, run_id: str) -> List[MemoryHit]:
    """Attempt to retrieve memory hits from a single source. Returns empty list on failure."""
    try:
        req = ToolRequest(tool_name=tool_name, params=params, run_id=run_id)
        result = await gateway.call_tool(req)
        if result.success and result.result:
            data = result.result
            items = data.get("items", []) if isinstance(data, dict) else []
            hits = []
            for item in items:
                hits.append(MemoryHit(
                    source=source,
                    content=item.get("content", str(item)),
                    relevance_score=item.get("relevance_score", 0.5),
                    metadata=item.get("metadata"),
                ))
            if not items and isinstance(data, dict):
                # Single result, not a list
                hits.append(MemoryHit(
                    source=source,
                    content=data.get("content", str(data)),
                    relevance_score=data.get("relevance_score", 0.5),
                    metadata=data,
                ))
            return hits
    except Exception as e:
        logger.warning(f"Memory retrieval from {source} failed: {e}")
    return []


async def retrieve_memory_node(state: IncidentAgentState) -> IncidentAgentState:
    """Retrieve relevant memory from multiple sources and store in state.memory_hits."""
    ticket = state.get("ticket")
    triage = state.get("triage")
    run_id = state.get("run_id", "unknown")

    service = getattr(ticket, "service", "") if ticket else ""
    env = getattr(ticket, "env", "") if ticket else ""
    incident_type = getattr(triage, "incident_type", "") if triage else ""

    memory_hits: List[MemoryHit] = []

    # Retrieve from runbook source (already available via query_runbook mock)
    hits = await _retrieve_from_source(
        source="runbook",
        tool_name="query_runbook",
        params={"service": service, "env": env, "incident_type": incident_type},
        run_id=run_id,
    )
    memory_hits.extend(hits)

    # Future: retrieve from rca_history, service_doc, alert_experience sources
    # These will be added as real adapters become available

    state["memory_hits"] = memory_hits
    state["step_count"] = state.get("step_count", 0) + 1

    return state
