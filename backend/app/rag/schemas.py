"""Shared schemas for RAG indexing, retrieval, and writeback."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    doc_type: str
    text: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class RetrievedChunk:
    doc_id: str
    chunk_id: str
    doc_type: str
    content: str
    score: float
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class IndexingResult:
    document_count: int
    chunk_count: int
    doc_ids: List[str]
