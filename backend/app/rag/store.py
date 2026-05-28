"""ChromaDB + LlamaIndex vector store bootstrap for RAG."""

from functools import lru_cache
from pathlib import Path

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.rag.embeddings import get_embedding_model
from app.rag.settings import RagSettings


@lru_cache(maxsize=1)
def get_collection():
    rag_settings = RagSettings()
    Path(rag_settings.persist_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=rag_settings.persist_dir)
    return client.get_or_create_collection(rag_settings.collection_name)


def build_index() -> VectorStoreIndex:
    vector_store = ChromaVectorStore(chroma_collection=get_collection())
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=get_embedding_model(),
    )
