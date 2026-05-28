"""Embedding model factory for the RAG subsystem."""

from functools import lru_cache
from typing import Any

from app.rag.settings import RagSettings


def get_embedding_model_name() -> str:
    return RagSettings().embedding_model


@lru_cache(maxsize=1)
def get_embedding_model() -> Any:
    """Lazily construct the configured embedding model.

    Importing the HuggingFace integration can trigger heavy dependencies, so the
    import stays inside this function and is only used by deployments that opt
    into a real vector backend.
    """
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ModuleNotFoundError as exc:
        raise RuntimeError("llama-index-embeddings-huggingface is not installed") from exc

    return HuggingFaceEmbedding(model_name=get_embedding_model_name())
