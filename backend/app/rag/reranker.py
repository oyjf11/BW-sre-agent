"""BGE reranker adapter."""

from functools import lru_cache
from typing import List

from sentence_transformers import CrossEncoder

from app.rag.schemas import RetrievedChunk


@lru_cache(maxsize=1)
def get_reranker_model() -> CrossEncoder:
    return CrossEncoder("BAAI/bge-reranker-base")


def rerank(query: str, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
    if not chunks:
        return []

    scores = get_reranker_model().predict([(query, chunk.content) for chunk in chunks])
    rescored = [
        RetrievedChunk(
            doc_id=chunk.doc_id,
            chunk_id=chunk.chunk_id,
            doc_type=chunk.doc_type,
            content=chunk.content,
            score=float(score),
            metadata=chunk.metadata,
        )
        for chunk, score in zip(chunks, scores)
    ]
    return sorted(rescored, key=lambda chunk: chunk.score, reverse=True)
