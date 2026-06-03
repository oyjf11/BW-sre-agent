from dataclasses import dataclass

from app.core.config import get_settings


@dataclass(frozen=True)
class RagSettings:
    enabled: bool = False
    persist_dir: str = "./storage/chroma"
    collection_name: str = "opspilot_knowledge"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    chunk_size: int = 512
    chunk_overlap: int = 80
    runbook_dir: str = "./knowledge/runbooks"
    top_k: int = 5
    enable_reranker: bool = False
    reranker_top_n: int = 5

    def __init__(self):
        settings = get_settings()
        object.__setattr__(self, "enabled", settings.rag_enabled)
        object.__setattr__(self, "persist_dir", settings.rag_persist_dir)
        object.__setattr__(self, "collection_name", settings.rag_collection_name)
        object.__setattr__(self, "embedding_model", settings.rag_embedding_model)
        object.__setattr__(self, "chunk_size", settings.rag_chunk_size)
        object.__setattr__(self, "chunk_overlap", settings.rag_chunk_overlap)
        object.__setattr__(self, "runbook_dir", settings.rag_runbook_dir)
        object.__setattr__(self, "top_k", settings.rag_top_k)
        object.__setattr__(self, "enable_reranker", settings.rag_enable_reranker)
        object.__setattr__(self, "reranker_top_n", settings.rag_reranker_top_n)
