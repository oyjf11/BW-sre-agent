"""Memory retrieval node: fetches relevant runbooks, historical RCA, service docs, alert experience."""

import logging
from typing import List

from app.graph.state import IncidentAgentState
from app.models.evidence import EvidenceItem
from app.models.planning import MemoryHit
from app.rag.retriever import chunks_to_evidence, retrieve
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

    service = (
        getattr(ticket, "service", "")
        if hasattr(ticket, "service")
        else (ticket.get("service", "") if isinstance(ticket, dict) else "")
    )
    env = (
        getattr(ticket, "env", "")
        if hasattr(ticket, "env")
        else (ticket.get("env", "") if isinstance(ticket, dict) else "")
    )
    title = (
        getattr(ticket, "title", "")
        if hasattr(ticket, "title")
        else (ticket.get("title", "") if isinstance(ticket, dict) else "")
    )
    description = (
        getattr(ticket, "description", "")
        if hasattr(ticket, "description")
        else (ticket.get("description", "") if isinstance(ticket, dict) else "")
    )
    incident_type = (
        getattr(triage, "incident_type", "")
        if hasattr(triage, "incident_type")
        else (triage.get("incident_type", "") if isinstance(triage, dict) else "")
    )

    memory_hits: List[MemoryHit] = []
    evidence_items: List[EvidenceItem] = list(state.get("evidence_items", []) or [])

    try:
        query = " ".join(part for part in [title, description, service, incident_type] if part)
        filters = {"service": service, "env": env}
        rag_chunks = retrieve(
            query=query,
            filters=filters,
            top_k=5,
        )
        for chunk in rag_chunks:
            memory_hits.append(
                MemoryHit(
                    source=chunk.doc_type,
                    content=chunk.content,
                    relevance_score=chunk.score,
                    metadata={
                        **chunk.metadata,
                        "doc_id": chunk.doc_id,
                        "chunk_id": chunk.chunk_id,
                    },
                )
            )
        evidence_items.extend(chunks_to_evidence(rag_chunks))
    except Exception as e:
        logger.warning(f"RAG memory retrieval failed: {e}")

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
    state["evidence_items"] = evidence_items
    state["step_count"] = state.get("step_count", 0) + 1

    return state
