"""Index local runbooks and confirmed RCA reports into ChromaDB."""

from pathlib import Path
from typing import Iterable, List, Optional

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from sqlalchemy.orm import Session

from app.models.db_models import IncidentRcaReport
from app.rag.schemas import IndexingResult, KnowledgeDocument
from app.rag.settings import RagSettings
from app.rag.store import build_index
from app.repositories.runs_repo import RunsRepo


def load_runbook_documents(directory: Path) -> List[KnowledgeDocument]:
    if not directory.exists():
        return []

    raw_documents = SimpleDirectoryReader(input_dir=str(directory), recursive=True).load_data()
    documents: List[KnowledgeDocument] = []
    for raw in raw_documents:
        source_path = str(raw.metadata.get("file_path", ""))
        stem = Path(source_path).stem or "runbook"
        documents.append(
            KnowledgeDocument(
                doc_id=f"runbook:{stem}",
                doc_type="runbook",
                text=raw.text,
                metadata={
                    "doc_type": "runbook",
                    "source_path": source_path,
                    "validated": True,
                },
            )
        )
    return documents


def _to_llama_documents(documents: Iterable[KnowledgeDocument]) -> List[Document]:
    return [
        Document(
            id_=doc.doc_id,
            text=doc.text,
            metadata={
                key: _normalize_metadata_value(value)
                for key, value in {"doc_id": doc.doc_id, "doc_type": doc.doc_type, **doc.metadata}.items()
            },
        )
        for doc in documents
    ]


def _normalize_metadata_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    return value


def index_documents(documents: Iterable[KnowledgeDocument]) -> IndexingResult:
    docs = list(documents)
    if not docs:
        return IndexingResult(document_count=0, chunk_count=0, doc_ids=[])

    rag_settings = RagSettings()
    splitter = SentenceSplitter(
        chunk_size=rag_settings.chunk_size,
        chunk_overlap=rag_settings.chunk_overlap,
    )
    nodes = splitter.get_nodes_from_documents(_to_llama_documents(docs))
    build_index().insert_nodes(nodes)
    return IndexingResult(
        document_count=len(docs),
        chunk_count=len(nodes),
        doc_ids=[doc.doc_id for doc in docs],
    )


def index_runbook_documents(runbook_dir: Optional[str] = None) -> IndexingResult:
    rag_settings = RagSettings()
    directory = Path(runbook_dir or rag_settings.runbook_dir)
    return index_documents(load_runbook_documents(directory))


def build_rca_document(rca, run) -> KnowledgeDocument:
    prevention_items = rca.prevention_items_json or []
    prevention_text = "\n".join(f"- {item}" for item in prevention_items)
    text = "\n".join(
        [
            f"根因：{rca.root_cause}",
            f"处置：{rca.resolution}",
            "预防项：",
            prevention_text,
            "",
            rca.report_markdown or "",
        ]
    ).strip()
    return KnowledgeDocument(
        doc_id=f"rca:{rca.run_id}",
        doc_type="rca",
        text=text,
        metadata={
            "doc_type": "rca",
            "source_run_id": rca.run_id,
            "service": getattr(run, "service", None),
            "env": getattr(run, "env", None),
            "severity": getattr(run, "severity", None),
            "validated": bool(rca.confirmed_by_human),
        },
    )


def index_confirmed_rca_reports(db: Session) -> IndexingResult:
    runs_repo = RunsRepo(db)
    reports = (
        db.query(IncidentRcaReport)
        .filter(IncidentRcaReport.confirmed_by_human == 1)
        .all()
    )
    documents = [build_rca_document(report, runs_repo.get(report.run_id)) for report in reports]
    return index_documents(documents)
