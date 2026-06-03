# RAG 服务优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补齐 RAG 模块中缺失的 3 项能力：反幻觉 prompt 模板、重排序 top_n 截断、来源标注格式。

**Architecture:** 在现有 `backend/app/rag/` 下新增 `prompt.py`（反幻觉模板 + citation 工具），修改 `reranker.py` 增加 top_n 截断、`retriever.py` 透传截断参数、`settings.py` + `core/config.py` 新增配置项。不改动下游 graph 节点。

**Tech Stack:** Python, LlamaIndex, sentence-transformers, Pydantic (Settings)

---

### Task 1: Add `reranker_top_n` config fields

**Files:**
- Modify: `backend/app/rag/settings.py:1-28`
- Modify: `backend/app/core/config.py:88-96`

- [ ] **Step 1: Add `rag_reranker_top_n` to Settings**

Edit `backend/app/core/config.py`:

```python
    rag_enabled: bool = False
    rag_persist_dir: str = "./storage/chroma"
    rag_collection_name: str = "opspilot_knowledge"
    rag_embedding_model: str = "BAAI/bge-small-zh-v1.5"
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 80
    rag_runbook_dir: str = "./knowledge/runbooks"
    rag_top_k: int = 5
    rag_enable_reranker: bool = False
    rag_reranker_top_n: int = 5
```

- [ ] **Step 2: Add `reranker_top_n` to RagSettings.dataclass and __init__**

Edit `backend/app/rag/settings.py`:

```python
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
```

- [ ] **Step 3: Verify config loads correctly**

Run: `cd backend && source venv/bin/activate && python -c "from app.rag.settings import RagSettings; s = RagSettings(); print(s.reranker_top_n)"`
Expected: `5`

- [ ] **Step 4: Commit**

```bash
git add backend/app/rag/settings.py backend/app/core/config.py
git commit -m "rag: add reranker_top_n config field"
```

---

### Task 2: Add `top_n` truncation to `rerank()` function

**Files:**
- Modify: `backend/app/tests/test_rag_retriever.py:59-92`
- Modify: `backend/app/rag/reranker.py:1-32`

- [ ] **Step 1: Write failing test for top_n truncation**

Append to `backend/app/tests/test_rag_retriever.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_retriever.py::test_rerank_respects_top_n -v`
Expected: FAIL with `TypeError: rerank() got an unexpected keyword argument 'top_n'`

- [ ] **Step 3: Add `top_n` parameter to `rerank()`**

Edit `backend/app/rag/reranker.py` (full file):

```python
"""BGE reranker adapter."""

from functools import lru_cache
from typing import List, Optional

from sentence_transformers import CrossEncoder

from app.rag.schemas import RetrievedChunk


@lru_cache(maxsize=1)
def get_reranker_model() -> CrossEncoder:
    return CrossEncoder("BAAI/bge-reranker-base")


def rerank(
    query: str,
    chunks: List[RetrievedChunk],
    top_n: Optional[int] = None,
) -> List[RetrievedChunk]:
    if not chunks:
        return []

    scores = get_reranker_model().predict(
        [(query, chunk.content) for chunk in chunks]
    )
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
    sorted_chunks = sorted(rescored, key=lambda chunk: chunk.score, reverse=True)
    if top_n and top_n > 0:
        return sorted_chunks[:top_n]
    return sorted_chunks
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_retriever.py::test_rerank_respects_top_n -v`
Expected: PASS

- [ ] **Step 5: Verify existing rerank test still passes**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_retriever.py::test_rerank_sorts_chunks_by_cross_encoder_score -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/rag/reranker.py backend/app/tests/test_rag_retriever.py
git commit -m "rag: add top_n truncation to rerank()"
```

---

### Task 3: Pass `reranker_top_n` from `retrieve()` to `rerank()`

**Files:**
- Modify: `backend/app/rag/retriever.py:81-90`

- [ ] **Step 1: Pass `reranker_top_n` to `rerank()` call**

Edit `backend/app/rag/retriever.py:90` — change the rerank call line:

```python
    return rerank(query, chunks, rag_settings.reranker_top_n) if rag_settings.enable_reranker else chunks
```

The full `retrieve()` function stays the same except for this line.

- [ ] **Step 2: Verify existing tests still pass**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_retriever.py -v`
Expected: all 5 tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/rag/retriever.py
git commit -m "rag: pass reranker_top_n from retrieve() to rerank()"
```

---

### Task 4: Create `prompt.py` with anti-hallucination template and citation tools

**Files:**
- Create: `backend/app/rag/prompt.py`
- Create: `backend/app/tests/test_rag_prompt.py`

- [ ] **Step 1: Write tests for all prompt.py functions**

Create `backend/app/tests/test_rag_prompt.py`:

```python
from app.rag.prompt import (
    ANTI_HALLUCINATION_TEMPLATE,
    build_rag_prompt,
    format_chunk_citation,
    format_chunks_with_citations,
    format_rag_context,
)
from app.rag.schemas import RetrievedChunk


def test_format_chunk_citation():
    chunk = RetrievedChunk(
        doc_id="runbook:test",
        chunk_id="c1",
        doc_type="runbook",
        content="test content",
        score=0.9,
        metadata={},
    )
    assert format_chunk_citation(chunk) == "[来源：runbook:test]"


def test_format_chunks_with_citations_multiple():
    chunks = [
        RetrievedChunk(
            doc_id="runbook:a", chunk_id="c1", doc_type="runbook",
            content="内容A", score=0.9, metadata={},
        ),
        RetrievedChunk(
            doc_id="rca:b", chunk_id="c2", doc_type="rca",
            content="内容B", score=0.8, metadata={},
        ),
    ]
    result = format_chunks_with_citations(chunks)
    assert "[来源：runbook:a]" in result
    assert "[来源：rca:b]" in result
    assert "内容A" in result
    assert "内容B" in result


def test_format_chunks_with_citations_empty():
    assert format_chunks_with_citations([]) == ""


def test_format_rag_context_aliases_format_chunks_with_citations():
    chunks = [
        RetrievedChunk(
            doc_id="d1", chunk_id="c1", doc_type="t",
            content="x", score=0.5, metadata={},
        )
    ]
    assert format_rag_context(chunks) == format_chunks_with_citations(chunks)


def test_build_rag_prompt_fills_template():
    chunks = [
        RetrievedChunk(
            doc_id="runbook:a", chunk_id="c1", doc_type="runbook",
            content="数据库连接池配置", score=0.9, metadata={},
        )
    ]
    prompt = build_rag_prompt("如何排查连接池问题", chunks)
    assert "数据库连接池配置" in prompt
    assert "如何排查连接池问题" in prompt
    assert "只回答文档中明确记载的内容" in prompt
    assert "文档中暂无相关记录" in prompt


def test_build_rag_prompt_empty_chunks():
    prompt = build_rag_prompt("问题", [])
    assert "暂无检索到相关文档" in prompt


def test_anti_hallucination_template_has_required_rules():
    assert "只回答文档中明确记载的内容" in ANTI_HALLUCINATION_TEMPLATE
    assert "标注来源" in ANTI_HALLUCINATION_TEMPLATE
    assert "文档中暂无相关记录" in ANTI_HALLUCINATION_TEMPLATE
    assert "不要在答案中混入文档以外的知识" in ANTI_HALLUCINATION_TEMPLATE
    assert "{context_str}" in ANTI_HALLUCINATION_TEMPLATE
    assert "{query_str}" in ANTI_HALLUCINATION_TEMPLATE
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_prompt.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.rag.prompt'`

- [ ] **Step 3: Create `prompt.py`**

Create `backend/app/rag/prompt.py`:

```python
"""Anti-hallucination prompt template and citation formatting tools."""

from typing import List

from app.rag.schemas import RetrievedChunk

ANTI_HALLUCINATION_TEMPLATE = """你是企业内部知识库助手。请严格基于以下检索到的文档内容回答问题。

规则（必须遵守）：
1. 只回答文档中明确记载的内容，不要推断或编造
2. 每个关键信息点必须标注来源（格式：[来源：doc_id]）
3. 如果文档中没有相关信息，直接回答"文档中暂无相关记录"
4. 不要在答案中混入文档以外的知识

参考文档：
{context_str}

用户问题：{query_str}

请基于以上文档内容回答："""


def format_chunk_citation(chunk: RetrievedChunk) -> str:
    return f"[来源：{chunk.doc_id}]"


def format_chunks_with_citations(chunks: List[RetrievedChunk]) -> str:
    if not chunks:
        return ""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        citation = format_chunk_citation(chunk)
        content = chunk.content[:512]
        lines.append(f"{i}. {citation} {content}")
    return "\n".join(lines)


def format_rag_context(chunks: List[RetrievedChunk]) -> str:
    return format_chunks_with_citations(chunks)


def build_rag_prompt(query: str, chunks: List[RetrievedChunk]) -> str:
    context_str = format_chunks_with_citations(chunks)
    if not context_str:
        context_str = "（暂无检索到相关文档）"
    return ANTI_HALLUCINATION_TEMPLATE.format(
        context_str=context_str,
        query_str=query,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_prompt.py -v`
Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/rag/prompt.py backend/app/tests/test_rag_prompt.py
git commit -m "rag: add anti-hallucination prompt template and citation tools"
```

---

### Task 5: Export new functions from `__init__.py`

**Files:**
- Modify: `backend/app/rag/__init__.py:1`

- [ ] **Step 1: Update `__init__.py` docstring**

Edit `backend/app/rag/__init__.py`:

```python
"""RAG subsystem for OpsPilot knowledge retrieval and writeback.

Public API:
    retrieve()          — semantic retrieval via ChromaDB + LlamaIndex
    chunks_to_evidence()— convert RetrievedChunk list to EvidenceItem list
    rerank()            — BGE cross-encoder reranking with optional top_n truncation

    ANTI_HALLUCINATION_TEMPLATE — prompt template for LLM generation
    build_rag_prompt()  — assemble anti-hallucination prompt from query + chunks
    format_rag_context()— format chunks as cited context text
    format_chunk_citation()     — single chunk citation string
    format_chunks_with_citations() — multi-chunk cited text

    write_back_confirmed_rca() — write confirmed RCA to vector store
    index_runbook_documents()  — index runbook Markdown files
"""
```

- [ ] **Step 2: Verify the module still imports cleanly**

Run: `cd backend && source venv/bin/activate && python -c "from app.rag.prompt import ANTI_HALLUCINATION_TEMPLATE, build_rag_prompt, format_rag_context; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/rag/__init__.py
git commit -m "rag: update __init__.py docstring with public API"
```

---

### Task 6: Run full backend test suite

**Files:** (none — verification only)

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q`
Expected: all tests PASS

- [ ] **Step 2: Verify no regressions in RAG-specific tests**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_rag_*.py -v`
Expected: all tests PASS (covering test_rag_embeddings.py, test_rag_indexer.py, test_rag_retriever.py, test_rag_prompt.py, test_rag_writer.py, test_retrieve_memory_rag.py)
