"""Write confirmed RCA reports back to the RAG vector store."""

from typing import Callable, Optional

from app.rag.indexer import build_rca_document, index_documents
from app.rag.schemas import IndexingResult


def write_back_confirmed_rca(
    run_id: str,
    rca_repo,
    runs_repo,
    index_documents_fn: Callable = index_documents,
) -> Optional[IndexingResult]:
    rca = rca_repo.get(run_id)
    if not rca or not bool(rca.confirmed_by_human):
        return None

    run = runs_repo.get(run_id)
    return index_documents_fn([build_rca_document(rca, run)])
