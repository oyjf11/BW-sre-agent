"""Hybrid retrieval: vector (ChromaDB) + FTS5 keyword, merged by RRF."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from llama_index.core.vector_stores import FilterOperator, MetadataFilter, MetadataFilters

from app.models.evidence import EvidenceItem
from app.rag.keyword_index import init_fts_db, search_fts
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


def _vector_retrieve(
    query: str,
    filters: Dict[str, Any],
    top_k: int,
) -> List[RetrievedChunk]:
    retriever = build_index().as_retriever(
        similarity_top_k=top_k,
        filters=_build_filters(filters),
    )
    return _to_retrieved_chunks(retriever.retrieve(query))


def _fts_retrieve(
    query: str,
    fts_db_path: str,
    top_k: int,
) -> List[RetrievedChunk]:
    init_fts_db(fts_db_path)
    rows = search_fts(fts_db_path, query, top_k=top_k)
    return [
        RetrievedChunk(
            doc_id=row.get("doc_type", "unknown") + ":" + row["chunk_id"],
            chunk_id=row["chunk_id"],
            doc_type=row.get("doc_type", "unknown"),
            content=row["content"],
            score=float(row["score"]),
            metadata={"service": row.get("service", ""), "doc_type": row.get("doc_type", "")},
        )
        for row in rows
    ]


def _rrf_merge(
    vec_chunks: List[RetrievedChunk],
    fts_chunks: List[RetrievedChunk],
    top_k: int,
    k: int = 60,
) -> List[RetrievedChunk]:
    """Reciprocal Rank Fusion merge of two ranked lists."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, RetrievedChunk] = {}

    for rank, chunk in enumerate(vec_chunks):
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (rank + k)
        chunk_map[chunk.chunk_id] = chunk

    for rank, chunk in enumerate(fts_chunks):
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (rank + k)
        if chunk.chunk_id not in chunk_map:
            chunk_map[chunk.chunk_id] = chunk

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        RetrievedChunk(
            doc_id=chunk_map[cid].doc_id,
            chunk_id=cid,
            doc_type=chunk_map[cid].doc_type,
            content=chunk_map[cid].content,
            score=rrf_score,
            metadata=chunk_map[cid].metadata,
        )
        for cid, rrf_score in ranked
    ]


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
    if not rag_settings.enabled:
        return []

    effective_top_k = top_k or rag_settings.top_k
    candidate_k = effective_top_k * 3

    vec_chunks = _vector_retrieve(query, filters, top_k=candidate_k)
    fts_chunks = _fts_retrieve(query, rag_settings.fts_db_path, top_k=candidate_k)

    merged = _rrf_merge(vec_chunks, fts_chunks, top_k=effective_top_k)

    return rerank(query, merged, rag_settings.reranker_top_n) if rag_settings.enable_reranker else merged
