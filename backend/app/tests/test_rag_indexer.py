from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.db_models import Base, IncidentRcaReport, IncidentRun, RunStatusEnum
from app.rag.indexer import (
    build_rca_document,
    index_confirmed_rca_reports,
    index_documents,
    index_runbook_documents,
    load_runbook_documents,
)
from app.rag.schemas import KnowledgeDocument


def create_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    db.add(
        IncidentRun(
            run_id="run-index-1",
            thread_id="thread-index-1",
            status=RunStatusEnum.COMPLETED,
            service="payment-service",
            env="prod",
            severity="P1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    db.add(
        IncidentRcaReport(
            run_id="run-index-1",
            report_markdown="支付服务 5xx，根因是连接池耗尽",
            root_cause="连接池耗尽",
            resolution="扩大连接池并限流",
            confirmed_by_human=1,
        )
    )
    db.add(
        IncidentRcaReport(
            run_id="run-index-draft",
            report_markdown="未确认 RCA",
            root_cause="unknown",
            resolution="none",
            confirmed_by_human=0,
        )
    )
    db.commit()
    return db


def test_load_runbook_documents_attaches_metadata(tmp_path: Path):
    doc_path = tmp_path / "payment-service.md"
    doc_path.write_text("# 支付服务\n\n连接池耗尽时先检查慢 SQL。", encoding="utf-8")

    docs = load_runbook_documents(tmp_path)

    assert len(docs) == 1
    assert docs[0].doc_type == "runbook"
    assert docs[0].metadata["source_path"].endswith("payment-service.md")
    assert "连接池耗尽" in docs[0].text


def test_index_documents_returns_chunk_counts(monkeypatch):
    class FakeIndex:
        def __init__(self):
            self.nodes = []

        def insert_nodes(self, nodes):
            self.nodes = nodes

    fake_index = FakeIndex()
    monkeypatch.setattr("app.rag.indexer.build_index", lambda: fake_index)
    monkeypatch.setattr("app.rag.indexer.get_fts_db_path", lambda: ":memory:")
    monkeypatch.setattr("app.rag.indexer.init_fts_db", lambda db_path: None)
    monkeypatch.setattr("app.rag.indexer.write_chunks_to_fts", lambda db_path, chunks: None)

    result = index_documents(
        [
            KnowledgeDocument(
                doc_id="runbook:payment",
                doc_type="runbook",
                text="数据库连接池耗尽时先检查慢 SQL。",
                metadata={"validated": True},
            )
        ]
    )

    assert result.document_count == 1
    assert result.chunk_count >= 1
    assert result.doc_ids == ["runbook:payment"]
    assert fake_index.nodes


def test_index_runbook_documents_uses_simple_directory_reader(monkeypatch, tmp_path: Path):
    doc_path = tmp_path / "payment-service.md"
    doc_path.write_text("# 支付服务\n\n连接池耗尽时先检查慢 SQL。", encoding="utf-8")

    captured = {}

    def fake_index_documents(documents):
        docs = list(documents)
        captured["docs"] = docs
        return type("Result", (), {"document_count": len(docs), "chunk_count": len(docs), "doc_ids": [doc.doc_id for doc in docs]})()

    monkeypatch.setattr("app.rag.indexer.index_documents", fake_index_documents)

    result = index_runbook_documents(str(tmp_path))

    assert result.document_count == 1
    assert captured["docs"][0].doc_id == "runbook:payment-service"


def test_build_rca_document_includes_confirmed_metadata():
    db = create_db()
    try:
        rca = db.query(IncidentRcaReport).filter_by(run_id="run-index-1").first()
        run = db.query(IncidentRun).filter_by(run_id="run-index-1").first()

        doc = build_rca_document(rca, run)

        assert doc.doc_id == "rca:run-index-1"
        assert doc.doc_type == "rca"
        assert doc.metadata["validated"] is True
        assert doc.metadata["service"] == "payment-service"
        assert "连接池耗尽" in doc.text
    finally:
        db.close()


def test_index_confirmed_rca_reports_skips_unconfirmed_reports(monkeypatch):
    indexed = {}

    def fake_index_documents(documents):
        docs = list(documents)
        indexed["docs"] = docs
        return type("Result", (), {"document_count": len(docs), "chunk_count": len(docs), "doc_ids": [doc.doc_id for doc in docs]})()

    monkeypatch.setattr("app.rag.indexer.index_documents", fake_index_documents)

    db = create_db()
    try:
        result = index_confirmed_rca_reports(db)

        assert result.document_count == 1
        assert result.doc_ids == ["rca:run-index-1"]
        assert indexed["docs"][0].metadata["service"] == "payment-service"
    finally:
        db.close()


def test_index_documents_writes_to_fts(tmp_path, monkeypatch):
    """index_documents should write chunks to FTS5 alongside ChromaDB."""
    from unittest.mock import MagicMock, patch
    from app.rag.indexer import index_documents
    from app.rag.schemas import KnowledgeDocument

    written_chunks = []

    def fake_write_chunks(db_path, chunks):
        written_chunks.extend(chunks)

    with patch("app.rag.indexer.build_index") as mock_index, \
         patch("app.rag.indexer.get_fts_db_path", return_value=str(tmp_path / "test_fts.db")), \
         patch("app.rag.indexer.write_chunks_to_fts", side_effect=fake_write_chunks), \
         patch("app.rag.indexer.init_fts_db"):
        mock_index.return_value.insert_nodes = MagicMock()

        from llama_index.core.node_parser import SentenceSplitter
        real_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=80)

        with patch("app.rag.indexer.SentenceSplitter", return_value=real_splitter):
            result = index_documents([
                KnowledgeDocument(
                    doc_id="rca:run-1",
                    doc_type="rca",
                    text="数据库连接池耗尽，支付服务5xx升高",
                    metadata={"service": "payment-service", "env": "staging"},
                )
            ])

    assert result.document_count == 1
    assert len(written_chunks) >= 1
    assert written_chunks[0]["doc_type"] == "rca"
    assert "chunk_id" in written_chunks[0]
    assert "content" in written_chunks[0]
