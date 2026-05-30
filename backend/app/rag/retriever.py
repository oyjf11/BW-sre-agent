"""Semantic retrieval service backed by LlamaIndex + ChromaDB."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from llama_index.core.vector_stores import FilterOperator, MetadataFilter, MetadataFilters

from app.models.evidence import EvidenceItem
from app.rag.reranker import rerank
from app.rag.schemas import RetrievedChunk
from app.rag.settings import RagSettings
from app.rag.store import build_index


def build_query(service: str, incident_type: str, symptom: str) -> str:
    parts = [service, incident_type, symptom]
    return " ".join(part for part in parts if part).strip()


def _build_filters(filters: Dict[str, Any]) -> Optional[MetadataFilters]:
    metadata_filters = [
        MetadataFilter(key=key, value=_normalize_filter_value(value), operator=FilterOperator.EQ)
        for key, value in filters.items()
        if value is not None and value != ""
    ]
    return MetadataFilters(filters=metadata_filters) if metadata_filters else None


def _normalize_filter_value(value: Any) -> Any:
    if isinstance(value, bool):
        return str(value).lower()
    return value


def _to_retrieved_chunks(nodes: Iterable[Any]) -> List[RetrievedChunk]:
    chunks: List[RetrievedChunk] = []
    for result in nodes:
        metadata = dict(result.node.metadata or {})
        chunks.append(
            RetrievedChunk(
                doc_id=metadata.get("doc_id", "unknown"),
                chunk_id=result.node.node_id,
                doc_type=metadata.get("doc_type", "unknown"),
                content=result.node.text,
                score=float(result.score or 0.0),
                metadata=metadata,
            )
        )
    return chunks


def _chunk_to_evidence(chunk: RetrievedChunk) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"ev_rag_{uuid.uuid4().hex[:8]}",
        tool_name="rag_retriever",
        category="history",
        source_ref=chunk.chunk_id,
        source_timestamp=datetime.now(timezone.utc),
        summary=chunk.content[:240],
        raw_payload={
            "doc_id": chunk.doc_id,
            "chunk_id": chunk.chunk_id,
            "doc_type": chunk.doc_type,
            "score": chunk.score,
            "metadata": chunk.metadata,
        },
        confidence=min(max(chunk.score, 0.0), 1.0),
        freshness_score=0.6,
        completeness_score=0.7,
        tags=["rag", chunk.doc_type],
    )


def chunks_to_evidence(chunks: Iterable[RetrievedChunk]) -> List[EvidenceItem]:
    return [_chunk_to_evidence(chunk) for chunk in chunks]


def retrieve(query: str, filters: Dict[str, Any], top_k: Optional[int] = None) -> List[RetrievedChunk]:
    rag_settings = RagSettings()
    retriever = build_index().as_retriever(
        similarity_top_k=top_k or rag_settings.top_k,
        filters=_build_filters(filters),
    )
    chunks = _to_retrieved_chunks(retriever.retrieve(query))
    return rerank(query, chunks) if rag_settings.enable_reranker else chunks
