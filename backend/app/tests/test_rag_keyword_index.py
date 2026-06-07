import os
import tempfile
import pytest
from app.rag.keyword_index import init_fts_db, write_chunks_to_fts, search_fts


@pytest.fixture
def fts_db(tmp_path):
    db_path = str(tmp_path / "test_fts.db")
    init_fts_db(db_path)
    return db_path


def test_init_creates_fts_table(fts_db):
    import sqlite3
    conn = sqlite3.connect(fts_db)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    conn.close()
    assert "rag_chunks_fts" in tables


def test_write_and_search_returns_matching_chunks(fts_db):
    write_chunks_to_fts(fts_db, [
        {"chunk_id": "c1", "content": "数据库连接池耗尽导致 5xx", "doc_type": "rca", "service": "payment-service"},
        {"chunk_id": "c2", "content": "K8s Pod OOMKilled 重启", "doc_type": "runbook", "service": "order-service"},
    ])
    results = search_fts(fts_db, "数据库 连接池", top_k=5)
    chunk_ids = [r["chunk_id"] for r in results]
    assert "c1" in chunk_ids
    assert "c2" not in chunk_ids


def test_search_returns_empty_on_no_match(fts_db):
    write_chunks_to_fts(fts_db, [
        {"chunk_id": "c1", "content": "数据库连接池耗尽", "doc_type": "rca", "service": "svc"},
    ])
    results = search_fts(fts_db, "kubernetes deployment rollout", top_k=5)
    assert results == []


def test_write_is_idempotent(fts_db):
    chunk = {"chunk_id": "c1", "content": "连接池耗尽", "doc_type": "rca", "service": "svc"}
    write_chunks_to_fts(fts_db, [chunk])
    write_chunks_to_fts(fts_db, [chunk])  # 重复写入
    results = search_fts(fts_db, "连接池", top_k=10)
    assert len([r for r in results if r["chunk_id"] == "c1"]) == 1


def test_search_fts_returns_score_field(fts_db):
    write_chunks_to_fts(fts_db, [
        {"chunk_id": "c1", "content": "慢查询导致超时", "doc_type": "rca", "service": "svc"},
    ])
    results = search_fts(fts_db, "慢查询", top_k=5)
    assert "score" in results[0]
    assert results[0]["score"] > 0


def test_rag_settings_has_fts_db_path():
    from app.rag.settings import RagSettings
    s = RagSettings()
    assert hasattr(s, "fts_db_path")
    assert isinstance(s.fts_db_path, str)
