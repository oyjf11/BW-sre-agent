# Phase 9 RAG Hybrid Search + Specialist Timeout 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 OpsPilot RAG 检索升级为向量 + FTS5 关键词的 hybrid search（RRF 融合），并将 specialist pool 的 timeout 参数从偏小的默认值校准到真实 DeepSeek 延迟水平。

**Architecture:** 新增 `app/rag/keyword_index.py` 维护一张 SQLite FTS5 表（与 ChromaDB 并存），`retriever.py` 升级为并行查两路后 RRF(K=60) 合并；`indexer.py` 写 ChromaDB 时同步写 FTS5；specialist 相关 timeout 常量集中到 `agent_configs.yaml` 和 `planning.py` 中，fanout 节点总 timeout 同步放大。

**Tech Stack:** Python 3.9, SQLite FTS5（内置）, ChromaDB, LlamaIndex, asyncio, pytest

---

## 文件地图

| 文件 | 变更 |
|------|------|
| `backend/app/rag/keyword_index.py` | **新建** — FTS5 索引的 init/write/search 三个函数 |
| `backend/app/rag/retriever.py` | **修改** — `retrieve()` 升级为 hybrid，调用 keyword_index |
| `backend/app/rag/indexer.py` | **修改** — `index_documents()` 写 ChromaDB 后同步写 FTS5 |
| `backend/app/rag/settings.py` | **修改** — 新增 `rag_fts_db_path` 配置字段 |
| `backend/app/core/config.py` | **修改** — 新增 `rag_fts_db_path` Settings 字段 |
| `backend/app/graph/nodes/specialist_agent.py` | **修改** — LLM deadline 上限 15s → 30s，final analysis timeout 放大 |
| `backend/app/graph/nodes/__init__.py` | **修改** — fanout 总 timeout 60s → 150s |
| `backend/app/graph/nodes/agent_configs.yaml` | **修改** — 各 specialist 新增 `timeout_ms: 90000` |
| `backend/app/models/planning.py` | **修改** — `AgentTask.timeout_ms` 默认值 30000 → 90000 |
| `backend/app/tests/test_rag_keyword_index.py` | **新建** — FTS5 单元测试 |
| `backend/app/tests/test_rag_retriever.py` | **修改** — 新增 hybrid 检索测试 |
| `backend/app/tests/test_specialist_timeout.py` | **新建** — timeout 参数回归测试 |

---

## Task 1: 新增 FTS5 关键词索引模块

**Files:**
- Create: `backend/app/rag/keyword_index.py`
- Create: `backend/app/tests/test_rag_keyword_index.py`

- [ ] **Step 1: 写失败测试**

新建 `backend/app/tests/test_rag_keyword_index.py`：

```python
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
```

- [ ] **Step 2: 运行确认测试失败**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_keyword_index.py -v 2>&1 | tail -15
```

预期：`ImportError: cannot import name 'init_fts_db'`

- [ ] **Step 3: 实现 keyword_index.py**

新建 `backend/app/rag/keyword_index.py`：

```python
"""SQLite FTS5 keyword index for hybrid RAG search."""

import sqlite3
from typing import Any, Dict, List


def init_fts_db(db_path: str) -> None:
    """Create FTS5 table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rag_chunks_meta (
                chunk_id TEXT PRIMARY KEY,
                doc_type TEXT,
                service TEXT
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS rag_chunks_fts USING fts5(
                content,
                chunk_id UNINDEXED,
                tokenize='unicode61 remove_diacritics 1'
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_rag_meta_chunk ON rag_chunks_meta(chunk_id)"
        )
        conn.commit()
    finally:
        conn.close()


def write_chunks_to_fts(db_path: str, chunks: List[Dict[str, Any]]) -> None:
    """Write chunks to FTS5 index. Idempotent: deletes existing chunk_id before insert."""
    conn = sqlite3.connect(db_path)
    try:
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            content = chunk.get("content", "")
            doc_type = chunk.get("doc_type", "")
            service = chunk.get("service", "")
            # delete-then-insert for idempotency
            conn.execute(
                "DELETE FROM rag_chunks_fts WHERE chunk_id = ?", (chunk_id,)
            )
            conn.execute(
                "DELETE FROM rag_chunks_meta WHERE chunk_id = ?", (chunk_id,)
            )
            conn.execute(
                "INSERT INTO rag_chunks_fts(content, chunk_id) VALUES (?, ?)",
                (content, chunk_id),
            )
            conn.execute(
                "INSERT INTO rag_chunks_meta(chunk_id, doc_type, service) VALUES (?, ?, ?)",
                (chunk_id, doc_type, service),
            )
        conn.commit()
    finally:
        conn.close()


def search_fts(db_path: str, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """FTS5 keyword search. Returns list of {chunk_id, content, doc_type, service, score}."""
    # Sanitize query: remove FTS5 special chars, join tokens with OR
    safe_q = (
        query.replace('"', " ")
             .replace("'", " ")
             .replace("(", " ")
             .replace(")", " ")
             .replace("*", " ")
             .replace(":", " ")
             .replace("^", " ")
    )
    tokens = [t for t in safe_q.strip().split() if t]
    if not tokens:
        return []
    fts_query = " OR ".join(tokens)

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT f.chunk_id, f.content, (-f.rank) AS score,
                   m.doc_type, m.service
            FROM rag_chunks_fts f
            LEFT JOIN rag_chunks_meta m ON m.chunk_id = f.chunk_id
            WHERE rag_chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, top_k),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

    return [
        {
            "chunk_id": row[0],
            "content": row[1],
            "score": float(row[2]),
            "doc_type": row[3] or "",
            "service": row[4] or "",
        }
        for row in rows
    ]
```

- [ ] **Step 4: 运行确认测试通过**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_keyword_index.py -v 2>&1 | tail -10
```

预期：`5 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag/keyword_index.py backend/app/tests/test_rag_keyword_index.py
git commit -m "rag: add FTS5 keyword index module with idempotent write and search"
```

---

## Task 2: 配置层新增 FTS5 DB 路径

**Files:**
- Modify: `backend/app/rag/settings.py`
- Modify: `backend/app/core/config.py`

- [ ] **Step 1: 写失败测试**

在 `backend/app/tests/test_rag_keyword_index.py` 末尾追加：

```python
def test_rag_settings_has_fts_db_path():
    from app.rag.settings import RagSettings
    s = RagSettings()
    assert hasattr(s, "fts_db_path")
    assert isinstance(s.fts_db_path, str)
```

- [ ] **Step 2: 运行确认测试失败**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_keyword_index.py::test_rag_settings_has_fts_db_path -v 2>&1 | tail -10
```

预期：`AttributeError: 'RagSettings' object has no attribute 'fts_db_path'`

- [ ] **Step 3: 修改 config.py，新增字段**

在 `backend/app/core/config.py` 的 `rag_reranker_top_n` 行后追加：

```python
    rag_fts_db_path: str = "./storage/rag_fts.db"
```

- [ ] **Step 4: 修改 settings.py，读取新字段**

在 `backend/app/rag/settings.py` 的 `RagSettings` dataclass 中，在 `reranker_top_n` 字段后添加：

```python
    fts_db_path: str = "./storage/rag_fts.db"
```

在 `__init__` 方法末尾追加：

```python
        object.__setattr__(self, "fts_db_path", settings.rag_fts_db_path)
```

- [ ] **Step 5: 运行确认测试通过**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_keyword_index.py -v 2>&1 | tail -10
```

预期：`6 passed`

- [ ] **Step 6: Commit**

```bash
git add backend/app/core/config.py backend/app/rag/settings.py
git commit -m "rag: add rag_fts_db_path config for FTS5 keyword index"
```

---

## Task 3: indexer 写 ChromaDB 时同步写 FTS5

**Files:**
- Modify: `backend/app/rag/indexer.py`
- Modify: `backend/app/tests/test_rag_indexer.py`

- [ ] **Step 1: 读现有 indexer 测试**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_indexer.py -v 2>&1 | tail -15
```

确认现有测试全部通过后再继续。

- [ ] **Step 2: 写失败测试**

在 `backend/app/tests/test_rag_indexer.py` 末尾追加（需先阅读现有 fixtures 结构）：

```python
def test_index_documents_writes_to_fts(tmp_path, monkeypatch):
    """index_documents should write chunks to FTS5 alongside ChromaDB."""
    from unittest.mock import MagicMock, patch
    from app.rag.indexer import index_documents
    from app.rag.schemas import KnowledgeDocument

    fts_db_path = str(tmp_path / "test_fts.db")

    written_chunks = []

    def fake_write_chunks(db_path, chunks):
        written_chunks.extend(chunks)

    with patch("app.rag.indexer.build_index") as mock_index, \
         patch("app.rag.indexer.get_fts_db_path", return_value=fts_db_path), \
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
```

- [ ] **Step 3: 运行确认测试失败**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_indexer.py::test_index_documents_writes_to_fts -v 2>&1 | tail -15
```

预期：`ImportError: cannot import name 'get_fts_db_path'` 或类似。

- [ ] **Step 4: 修改 indexer.py，同步写 FTS5**

在 `backend/app/rag/indexer.py` 顶部 import 区追加：

```python
from app.rag.keyword_index import init_fts_db, write_chunks_to_fts
from app.rag.settings import RagSettings
```

在 `index_documents` 函数内，`build_index().insert_nodes(nodes)` 这行**之后**追加：

```python
    # Sync to FTS5 keyword index
    fts_db_path = get_fts_db_path()
    init_fts_db(fts_db_path)
    fts_chunks = [
        {
            "chunk_id": node.node_id,
            "content": node.text,
            "doc_type": node.metadata.get("doc_type", ""),
            "service": node.metadata.get("service", ""),
        }
        for node in nodes
    ]
    write_chunks_to_fts(fts_db_path, fts_chunks)
```

在文件底部（`index_confirmed_rca_reports` 之后）新增辅助函数：

```python
def get_fts_db_path() -> str:
    return RagSettings().fts_db_path
```

- [ ] **Step 5: 运行确认测试通过**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_indexer.py -v 2>&1 | tail -15
```

预期：所有 indexer 测试通过，包含新增的 `test_index_documents_writes_to_fts`。

- [ ] **Step 6: Commit**

```bash
git add backend/app/rag/indexer.py backend/app/tests/test_rag_indexer.py
git commit -m "rag: sync FTS5 keyword index on index_documents"
```

---

## Task 4: retriever 升级为 hybrid search（向量 + FTS5 + RRF）

**Files:**
- Modify: `backend/app/rag/retriever.py`
- Modify: `backend/app/tests/test_rag_retriever.py`

- [ ] **Step 1: 写失败测试**

在 `backend/app/tests/test_rag_retriever.py` 末尾追加：

```python
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
    # c2 appears in both lists → higher RRF score → should rank first or second
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
```

- [ ] **Step 2: 运行确认测试失败**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_retriever.py::test_hybrid_retrieve_merges_vector_and_fts app/tests/test_rag_retriever.py::test_rrf_merge_deduplicates_and_ranks -v 2>&1 | tail -15
```

预期：`ImportError: cannot import name '_vector_retrieve'` 或 `'_fts_retrieve'` 或 `'_rrf_merge'`

- [ ] **Step 3: 重写 retriever.py**

完整替换 `backend/app/rag/retriever.py` 内容：

```python
"""Hybrid retrieval: vector (ChromaDB) + FTS5 keyword, merged by RRF."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from llama_index.core.vector_stores import FilterOperator, MetadataFilter, MetadataFilters

from app.models.evidence import EvidenceItem
from app.rag.keyword_index import init_fts_db, search_fts
from app.rag.reranker import rerank
from app.rag.schemas import RetrievedChunk
from app.rag.settings import RagSettings
from app.rag.store import build_index


def build_query(service: str, incident_type: str, symptom: str) -> str:
    parts = [service, incident_type, symptom]
    return " ".join(part for part in parts if part).strip()


def _build_filters(filters: Dict[str, Any]) -> Optional[MetadataFilters]:
    metadata_filters = [
        MetadataFilter(key=key, value=_normalize_filter_value(value), operator=FilterOperator.EQ)
        for key, value in filters.items()
        if value is not None and value != ""
    ]
    return MetadataFilters(filters=metadata_filters) if metadata_filters else None


def _normalize_filter_value(value: Any) -> Any:
    if isinstance(value, bool):
        return str(value).lower()
    return value


def _to_retrieved_chunks(nodes: Iterable[Any]) -> List[RetrievedChunk]:
    chunks: List[RetrievedChunk] = []
    for result in nodes:
        metadata = dict(result.node.metadata or {})
        chunks.append(
            RetrievedChunk(
                doc_id=metadata.get("doc_id", "unknown"),
                chunk_id=result.node.node_id,
                doc_type=metadata.get("doc_type", "unknown"),
                content=result.node.text,
                score=float(result.score or 0.0),
                metadata=metadata,
            )
        )
    return chunks


def _vector_retrieve(
    query: str,
    filters: Dict[str, Any],
    top_k: int,
) -> List[RetrievedChunk]:
    retriever = build_index().as_retriever(
        similarity_top_k=top_k,
        filters=_build_filters(filters),
    )
    return _to_retrieved_chunks(retriever.retrieve(query))


def _fts_retrieve(
    query: str,
    fts_db_path: str,
    top_k: int,
) -> List[RetrievedChunk]:
    init_fts_db(fts_db_path)
    rows = search_fts(fts_db_path, query, top_k=top_k)
    return [
        RetrievedChunk(
            doc_id=row.get("doc_type", "unknown") + ":" + row["chunk_id"],
            chunk_id=row["chunk_id"],
            doc_type=row.get("doc_type", "unknown"),
            content=row["content"],
            score=float(row["score"]),
            metadata={"service": row.get("service", ""), "doc_type": row.get("doc_type", "")},
        )
        for row in rows
    ]


def _rrf_merge(
    vec_chunks: List[RetrievedChunk],
    fts_chunks: List[RetrievedChunk],
    top_k: int,
    k: int = 60,
) -> List[RetrievedChunk]:
    """Reciprocal Rank Fusion merge of two ranked lists."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, RetrievedChunk] = {}

    for rank, chunk in enumerate(vec_chunks):
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (rank + k)
        chunk_map[chunk.chunk_id] = chunk

    for rank, chunk in enumerate(fts_chunks):
        scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (rank + k)
        if chunk.chunk_id not in chunk_map:
            chunk_map[chunk.chunk_id] = chunk

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        RetrievedChunk(
            doc_id=chunk_map[cid].doc_id,
            chunk_id=cid,
            doc_type=chunk_map[cid].doc_type,
            content=chunk_map[cid].content,
            score=rrf_score,
            metadata=chunk_map[cid].metadata,
        )
        for cid, rrf_score in ranked
    ]


def _chunk_to_evidence(chunk: RetrievedChunk) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"ev_rag_{uuid.uuid4().hex[:8]}",
        tool_name="rag_retriever",
        category="history",
        source_ref=chunk.chunk_id,
        source_timestamp=datetime.now(timezone.utc),
        summary=chunk.content[:240],
        raw_payload={
            "doc_id": chunk.doc_id,
            "chunk_id": chunk.chunk_id,
            "doc_type": chunk.doc_type,
            "score": chunk.score,
            "metadata": chunk.metadata,
        },
        confidence=min(max(chunk.score, 0.0), 1.0),
        freshness_score=0.6,
        completeness_score=0.7,
        tags=["rag", chunk.doc_type],
    )


def chunks_to_evidence(chunks: Iterable[RetrievedChunk]) -> List[EvidenceItem]:
    return [_chunk_to_evidence(chunk) for chunk in chunks]


def retrieve(query: str, filters: Dict[str, Any], top_k: Optional[int] = None) -> List[RetrievedChunk]:
    rag_settings = RagSettings()
    if not rag_settings.enabled:
        return []

    effective_top_k = top_k or rag_settings.top_k
    candidate_k = effective_top_k * 3

    vec_chunks = _vector_retrieve(query, filters, top_k=candidate_k)
    fts_chunks = _fts_retrieve(query, rag_settings.fts_db_path, top_k=candidate_k)

    merged = _rrf_merge(vec_chunks, fts_chunks, top_k=effective_top_k)

    return rerank(query, merged, rag_settings.reranker_top_n) if rag_settings.enable_reranker else merged
```

- [ ] **Step 4: 运行确认 retriever 所有测试通过**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_retriever.py -v 2>&1 | tail -15
```

预期：所有测试通过（含新增 3 个）。

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag/retriever.py backend/app/tests/test_rag_retriever.py
git commit -m "rag: upgrade retrieve() to hybrid vector+FTS5 with RRF merge"
```

---

## Task 5: 全量 RAG 回归 + .env.example 更新

**Files:**
- Modify: `backend/.env.example`

- [ ] **Step 1: 运行全量 RAG 测试**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_*.py app/tests/test_retrieve_memory_rag.py -v 2>&1 | tail -20
```

预期：全部通过，无新增失败。

- [ ] **Step 2: 更新 .env.example**

在 `backend/.env.example` 的 RAG 配置区块末尾追加：

```
# FTS5 keyword index DB（与 ChromaDB 并存，用于 hybrid search）
RAG_FTS_DB_PATH=./storage/rag_fts.db
```

- [ ] **Step 3: 运行全量后端测试**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q 2>&1 | tail -10
```

预期：全部通过，warnings 不超过 3 个。

- [ ] **Step 4: Commit**

```bash
git add backend/.env.example
git commit -m "rag: document RAG_FTS_DB_PATH in .env.example"
```

---

## Task 6: Specialist timeout 参数校准

**Files:**
- Modify: `backend/app/models/planning.py`
- Modify: `backend/app/graph/nodes/agent_configs.yaml`
- Modify: `backend/app/graph/nodes/specialist_agent.py`
- Modify: `backend/app/graph/nodes/__init__.py`
- Create: `backend/app/tests/test_specialist_timeout.py`

- [ ] **Step 1: 写失败测试**

新建 `backend/app/tests/test_specialist_timeout.py`：

```python
"""Regression tests: specialist timeout values must match calibrated DeepSeek latency."""
from app.models.planning import AgentTask
import yaml
from pathlib import Path


def test_agent_task_default_timeout_is_90s():
    task = AgentTask(agent_id="k8s_specialist", category="k8s", service="svc", env="staging")
    assert task.timeout_ms == 90000, (
        f"AgentTask.timeout_ms default should be 90000, got {task.timeout_ms}. "
        "Reason: single DeepSeek specialist worst-case = 3 rounds × 30s + final 30s = 120s; "
        "90s covers P95 for mock and fast-path real calls."
    )


def test_agent_configs_yaml_all_specialists_have_timeout_ms():
    yaml_path = Path(__file__).parent.parent / "graph" / "nodes" / "agent_configs.yaml"
    data = yaml.safe_load(yaml_path.read_text())
    for agent in data["agents"]:
        assert "timeout_ms" in agent, (
            f"agent_configs.yaml entry '{agent['agent_id']}' missing timeout_ms. "
            "All specialists must have explicit timeout_ms >= 90000."
        )
        assert agent["timeout_ms"] >= 90000, (
            f"agent '{agent['agent_id']}' timeout_ms={agent['timeout_ms']} < 90000."
        )


def test_specialist_agent_llm_deadline_ceiling_is_30s():
    """LLM single-call deadline should be 30s, not 15s."""
    import inspect
    from app.graph.nodes import specialist_agent
    source = inspect.getsource(specialist_agent)
    # The old ceiling was 15.0 — ensure it's been raised to 30.0
    assert "min(remaining_ms / 1000, 30.0)" in source, (
        "specialist_agent.py: single LLM call deadline ceiling must be 30.0s "
        "(was 15.0s, too small for DeepSeek P95 latency)"
    )


def test_fanout_total_timeout_is_150s():
    """evidence_fanout asyncio.wait_for total timeout must be 150s."""
    import inspect
    from app.graph import nodes as graph_nodes
    source = inspect.getsource(graph_nodes)
    assert "timeout=150.0" in source, (
        "evidence_fanout node: asyncio.wait_for total timeout must be 150.0s "
        "(was 60.0s, insufficient for 5 parallel specialists at DeepSeek latency)"
    )
```

- [ ] **Step 2: 运行确认测试失败**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_specialist_timeout.py -v 2>&1 | tail -15
```

预期：4 个测试均 FAIL。

- [ ] **Step 3: 修改 AgentTask 默认 timeout_ms**

在 `backend/app/models/planning.py` 的 `AgentTask` class 中，将：

```python
    timeout_ms: int = Field(default=30000, description="Agent total timeout in ms")
```

改为：

```python
    timeout_ms: int = Field(default=90000, description="Agent total timeout in ms")
```

- [ ] **Step 4: 修改 agent_configs.yaml，各 specialist 新增 timeout_ms**

在 `backend/app/graph/nodes/agent_configs.yaml` 中，每个 agent 条目（k8s_specialist、db_specialist、log_specialist、metrics_specialist、deployment_specialist）的 `enabled: true` 下方添加 `timeout_ms: 90000`，例如：

```yaml
  - agent_id: k8s_specialist
    category: k8s
    description: K8s 集群状态诊断专家，分析 Deployment/Pod/Events
    enabled: true
    timeout_ms: 90000
    max_tool_rounds: 3
    # ... 其余字段不变
```

对全部 5 个 agent 条目重复此操作。

- [ ] **Step 5: 修改 specialist_agent.py，LLM deadline 上限 15s → 30s**

在 `backend/app/graph/nodes/specialist_agent.py` 第 194 行，将：

```python
                llm_deadline = min(remaining_ms / 1000, 15.0)
```

改为：

```python
                llm_deadline = min(remaining_ms / 1000, 30.0)
```

- [ ] **Step 6: 修改 nodes/__init__.py，fanout 总 timeout 60s → 150s**

在 `backend/app/graph/nodes/__init__.py`，将：

```python
                timeout=60.0,
```

改为：

```python
                timeout=150.0,
```

（该行在 `asyncio.wait_for` 的 evidence_fanout 节点内，通过 `grep -n "timeout=60" app/graph/nodes/__init__.py` 确认行号）

- [ ] **Step 7: 运行确认 timeout 测试通过**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/test_specialist_timeout.py -v 2>&1 | tail -10
```

预期：`4 passed`

- [ ] **Step 8: 运行全量回归**

```bash
cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q 2>&1 | tail -10
```

预期：全部通过。

- [ ] **Step 9: Commit**

```bash
git add backend/app/models/planning.py \
        backend/app/graph/nodes/agent_configs.yaml \
        backend/app/graph/nodes/specialist_agent.py \
        backend/app/graph/nodes/__init__.py \
        backend/app/tests/test_specialist_timeout.py
git commit -m "backend: calibrate specialist timeout to DeepSeek P95 latency (30s/90s/150s)"
```

---

## 自查清单（已执行）

- [x] **Spec 覆盖**：hybrid search（FTS5 + RRF）、timeout 三处修改均有对应 Task
- [x] **Placeholder 扫描**：无 TBD/TODO，所有代码步骤均完整
- [x] **类型一致性**：`_vector_retrieve`、`_fts_retrieve`、`_rrf_merge` 均在 Task 4 Step 3 中定义，测试中 import 名称与实现一致；`get_fts_db_path` 在 Task 3 中定义，Task 3 测试中通过 `patch` 引用
- [x] **测试命令可执行**：所有 pytest 命令使用绝对模块路径，在 `cd backend && source venv/bin/activate` 后可直接运行
