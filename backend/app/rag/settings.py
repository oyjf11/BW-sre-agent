from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class RagSettings:
    enabled: bool = settings.rag_enabled
    persist_dir: str = settings.rag_persist_dir
    collection_name: str = settings.rag_collection_name
    embedding_model: str = settings.rag_embedding_model
    chunk_size: int = settings.rag_chunk_size
    chunk_overlap: int = settings.rag_chunk_overlap
    runbook_dir: str = settings.rag_runbook_dir
    top_k: int = settings.rag_top_k
    enable_reranker: bool = settings.rag_enable_reranker
