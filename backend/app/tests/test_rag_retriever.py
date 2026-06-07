from types import SimpleNamespace

import app.rag.store as rag_store
from app.rag.retriever import _build_filters, _to_retrieved_chunks, build_query
from app.rag.reranker import rerank
from app.rag.schemas import RetrievedChunk


def test_retrieved_chunk_exposes_required_metadata():
    chunk = RetrievedChunk(
        doc_id="doc-1",
        chunk_id="chunk-1",
        doc_type="runbook",
        content="检查数据库连接池",
        score=0.91,
        metadata={"service": "payment-service", "env": "staging"},
    )

    assert chunk.doc_id == "doc-1"
    assert chunk.chunk_id == "chunk-1"
    assert chunk.doc_type == "runbook"
    assert chunk.metadata["service"] == "payment-service"


def test_rag_store_does_not_expose_mock_or_json_store():
    assert not hasattr(rag_store, "InMemoryKnowledgeStore")
    assert not hasattr(rag_store, "JsonKnowledgeStore")


def test_to_retrieved_chunks_preserves_score_and_metadata():
    node = SimpleNamespace(
        node=SimpleNamespace(
            node_id="chunk-1",
            text="检查数据库连接池",
            metadata={"doc_id": "rca:run-1", "doc_type": "rca", "service": "payment-service"},
        ),
        score=0.88,
    )

    chunks = _to_retrieved_chunks([node])

    assert chunks[0].doc_id == "rca:run-1"
    assert chunks[0].chunk_id == "chunk-1"
    assert chunks[0].doc_type == "rca"
    assert chunks[0].score == 0.88


def test_build_query_and_filters_keep_business_context():
    assert build_query("payment-service", "database", "5xx 升高") == "payment-service database 5xx 升高"

    filters = _build_filters(
        {"service": "payment-service", "env": "staging", "validated": True}
    )

    assert len(filters.filters) == 3
    assert filters.filters[2].value == "true"


def test_rerank_sorts_chunks_by_cross_encoder_score(monkeypatch):
    chunks = [
        RetrievedChunk(
            doc_id="doc-1",
            chunk_id="chunk-1",
            doc_type="runbook",
            content="检查数据库连接池",
            score=0.8,
            metadata={},
        ),
        RetrievedChunk(
            doc_id="doc-2",
            chunk_id="chunk-2",
            doc_type="rca",
            content="历史案例：数据库连接池耗尽",
            score=0.7,
            metadata={},
        ),
    ]

    class FakeModel:
        def predict(self, pairs):
            assert pairs == [
                ("5xx 升高", "检查数据库连接池"),
                ("5xx 升高", "历史案例：数据库连接池耗尽"),
            ]
            return [0.2, 0.9]

    monkeypatch.setattr("app.rag.reranker.get_reranker_model", lambda: FakeModel())

    reranked = rerank("5xx 升高", chunks)

    assert [chunk.doc_id for chunk in reranked] == ["doc-2", "doc-1"]
    assert reranked[0].score == 0.9


def test_rerank_respects_top_n(monkeypatch):
    chunks = [
        RetrievedChunk(
            doc_id="doc-1", chunk_id="chunk-1", doc_type="runbook",
            content="内容1", score=0.8, metadata={},
        ),
        RetrievedChunk(
            doc_id="doc-2", chunk_id="chunk-2", doc_type="rca",
            content="内容2", score=0.7, metadata={},
        ),
        RetrievedChunk(
            doc_id="doc-3", chunk_id="chunk-3", doc_type="runbook",
            content="内容3", score=0.6, metadata={},
        ),
        RetrievedChunk(
            doc_id="doc-4", chunk_id="chunk-4", doc_type="rca",
            content="内容4", score=0.9, metadata={},
        ),
        RetrievedChunk(
            doc_id="doc-5", chunk_id="chunk-5", doc_type="runbook",
            content="内容5", score=0.5, metadata={},
        ),
    ]

    class FakeModel:
        def predict(self, pairs):
            return [float(chunk.score) for chunk in chunks]

    monkeypatch.setattr("app.rag.reranker.get_reranker_model", lambda: FakeModel())

    result = rerank("query", chunks, top_n=3)
    assert len(result) == 3
    assert result[0].doc_id == "doc-4"

    result_all = rerank("query", chunks, top_n=None)
    assert len(result_all) == 5

    result_zero = rerank("query", chunks, top_n=0)
    assert len(result_zero) == 5


def test_hybrid_retrieve_merges_vector_and_fts(monkeypatch):
    """retrieve() should call both vector and FTS search and RRF-merge results."""
    from unittest.mock import patch, MagicMock
    from app.rag.retriever import retrieve
    from app.rag.schemas import RetrievedChunk

    vector_chunk = RetrievedChunk(
        doc_id="rca:run-1", chunk_id="c1", doc_type="rca",
        content="数据库连接池耗尽", score=0.85,
        metadata={"service": "payment-service"},
    )
    fts_chunk = RetrievedChunk(
        doc_id="runbook:pay", chunk_id="c2", doc_type="runbook",
        content="检查连接池配置", score=3.2,
        metadata={"service": "payment-service"},
    )

    with patch("app.rag.retriever.RagSettings") as MockSettings, \
         patch("app.rag.retriever._vector_retrieve", return_value=[vector_chunk]), \
         patch("app.rag.retriever._fts_retrieve", return_value=[fts_chunk]):

        settings = MagicMock()
        settings.enabled = True
        settings.top_k = 5
        settings.enable_reranker = False
        settings.fts_db_path = "/tmp/fake.db"
        MockSettings.return_value = settings

        results = retrieve("数据库 连接池", {}, top_k=5)

    chunk_ids = [r.chunk_id for r in results]
    assert "c1" in chunk_ids
    assert "c2" in chunk_ids


def test_rrf_merge_deduplicates_and_ranks():
    """RRF merge should deduplicate by chunk_id and give higher rank to items in both lists."""
    from app.rag.retriever import _rrf_merge
    from app.rag.schemas import RetrievedChunk

    def make_chunk(cid, score):
        return RetrievedChunk(
            doc_id=f"doc-{cid}", chunk_id=cid, doc_type="rca",
            content="content", score=score, metadata={},
        )

    vec = [make_chunk("c1", 0.9), make_chunk("c2", 0.7)]
    fts = [make_chunk("c2", 3.0), make_chunk("c3", 2.0)]  # c2 in both

    merged = _rrf_merge(vec, fts, top_k=3)
    ids = [c.chunk_id for c in merged]
    assert "c2" in ids
    assert len(ids) == 3
    assert ids.index("c2") < ids.index("c3")  # c2 beats c3 (only in fts)


def test_retrieve_returns_empty_when_rag_disabled(monkeypatch):
    from unittest.mock import patch, MagicMock
    from app.rag.retriever import retrieve

    with patch("app.rag.retriever.RagSettings") as MockSettings:
        settings = MagicMock()
        settings.enabled = False
        MockSettings.return_value = settings
        results = retrieve("任意查询", {})

    assert results == []
