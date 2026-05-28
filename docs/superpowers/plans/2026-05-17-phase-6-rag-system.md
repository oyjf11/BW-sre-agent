# Phase 6 RAG 系统技术实现方案

> **面向执行代理：** 必须使用子技能 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，按任务逐项执行本方案。所有步骤均使用复选框（`- [ ]`）格式追踪。

**目标：** 为 OpsPilot 构建一条可运行的 Evidence RAG 闭环，使已确认的 RCA 报告与本地 Runbook 能够通过 LlamaIndex + ChromaDB + BGE 建立索引，在故障处理过程中被检索并注入证据链，并在人工确认 RCA 后回写到知识库。

**架构：** 将 RAG 子系统独立放在 `backend/app/rag/` 下。LlamaIndex 负责文档加载、切分、向量化与基于 ChromaDB 的检索；BGE-Reranker 作为第二阶段精排能力，通过配置开关控制启用；LangGraph 节点只依赖窄接口的检索服务，并将命中结果转换为现有的 `MemoryHit` 与 `EvidenceItem` 模型。Phase 6 有意只完成“向量检索 + 重排序 + 元数据过滤 + 写回闭环”，混合检索与离线 RAG 评测留到后续阶段。

**技术栈：** Python、LlamaIndex、ChromaDB、`BAAI/bge-small-zh-v1.5`、BGE-Reranker、FastAPI、LangGraph、Pytest

---

## 范围锁定

### Phase 6 范围内

- 为本地 Runbook 与已确认 RCA 报告建立索引。
- 使用 `SimpleDirectoryReader` 读取本地知识文档。
- 使用 `BAAI/bge-small-zh-v1.5` 作为默认嵌入模型。
- 将向量存储到本地持久化 ChromaDB。
- 基于语义相似度与元数据过滤进行检索。
- 将检索到的知识同时注入 `state["memory_hits"]` 与 `state["evidence_items"]`。
- 在人工确认 RCA 后，将其回写到向量库。
- 将 BGE-Reranker 实现为真实的第二阶段精排模块，但在本地模型资源准备就绪前，默认通过配置关闭。

### Phase 6 明确不做

- 混合检索 / BM25 / RRF（Reciprocal Rank Fusion）。
- RAG 评测 CLI 与基准数据集。
- 多租户权限与知识 ACL。
- PDF OCR / 扫描件解析。
- 前端证据引用 UI 改造。

## 文件结构

### 新增文件

- `backend/app/rag/__init__.py`  
  RAG 子系统的包标记。
- `backend/app/rag/schemas.py`  
  索引文档、检索切片与索引结果的共享类型模型。
- `backend/app/rag/settings.py`  
  RAG 专属配置默认值：存储路径、collection 名称、嵌入模型、chunk 大小与 overlap。
- `backend/app/rag/embeddings.py`  
  BGE 嵌入模型工厂。
- `backend/app/rag/store.py`  
  ChromaDB 持久化客户端与 LlamaIndex 向量存储初始化。
- `backend/app/rag/indexer.py`  
  本地 Runbook 与已确认 RCA 记录的文档入库逻辑。
- `backend/app/rag/retriever.py`  
  查询构造、元数据过滤、语义检索与重排序编排。
- `backend/app/rag/reranker.py`  
  用于第二阶段精排的 BGE-Reranker 适配器。
- `backend/app/rag/writer.py`  
  已确认 RCA 的写回入口。
- `backend/app/tests/test_rag_indexer.py`  
  索引行为测试。
- `backend/app/tests/test_rag_retriever.py`  
  检索与元数据过滤测试。
- `backend/app/tests/test_rag_writer.py`  
  仅允许已确认 RCA 写回的测试。
- `backend/app/tests/test_retrieve_memory_rag.py`  
  记忆注入与证据注入的图节点集成测试。

### 修改文件

- `backend/requirements.txt`  
  增加 LlamaIndex、ChromaDB 与 sentence-transformers 相关依赖。
- `backend/app/core/config.py`  
  在主配置对象中增加 RAG 相关设置。
- `backend/app/graph/nodes/retrieve_memory.py`  
  将仅依赖工具调用的占位检索替换为 RAG 检索，并保留兼容性的 Runbook 回退逻辑。
- `backend/app/services/knowledge_writeback.py`  
  用 `rag.writer.write_back_confirmed_rca(...)` 替换仅记录日志的写回占位实现。
- `backend/app/models/evidence.py`  
  扩展类别说明，使其包含 `history`。

## 任务 1：增加 RAG 依赖与配置

**文件：**
- 修改： `backend/requirements.txt`
- 修改： `backend/app/core/config.py`
- 新增： `backend/app/rag/__init__.py`
- 新增： `backend/app/rag/settings.py`
- 测试： `backend/app/tests/test_main_startup.py`

- [ ] **步骤 1: 编写失败的配置测试**

将以下测试加入 `backend/app/tests/test_main_startup.py`:

```python
def test_settings_expose_rag_defaults():
    from app.core.config import settings

    assert settings.rag_collection_name == "opspilot_knowledge"
    assert settings.rag_embedding_model == "BAAI/bge-small-zh-v1.5"
    assert settings.rag_chunk_size == 512
    assert settings.rag_chunk_overlap == 80
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_main_startup.py::test_settings_expose_rag_defaults -q
```

预期： `FAIL`，因为当前还不存在 RAG 配置。

- [ ] **步骤 3: 增加最小依赖**

追加到 `backend/requirements.txt`:

```txt
# RAG
llama-index>=0.10.0
llama-index-vector-stores-chroma>=0.1.0
llama-index-embeddings-huggingface>=0.2.0
chromadb>=0.5.0
sentence-transformers>=2.7.0
```

- [ ] **步骤 4: 增加主配置字段**

将以下字段加入 `backend/app/core/config.py`:

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
```

- [ ] **步骤 5: 增加 RAG 包与配置辅助模块**

创建 `backend/app/rag/__init__.py`:

```python
"""RAG subsystem for OpsPilot knowledge retrieval and writeback."""
```

创建 `backend/app/rag/settings.py`:

```python
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class RagSettings:
    enabled: bool = settings.rag_enabled
    persist_dir: str = settings.rag_persist_dir
    collection_name: str = settings.rag_collection_name
    embedding_model: str = settings.rag_embedding_model
    chunk_size: int = settings.rag_chunk_size
    chunk_overlap: int = settings.rag_chunk_overlap
    runbook_dir: str = settings.rag_runbook_dir
    top_k: int = settings.rag_top_k
    enable_reranker: bool = settings.rag_enable_reranker
```

- [ ] **步骤 6: 运行测试并确认其通过**

运行：

```bash
cd backend && pytest app/tests/test_main_startup.py::test_settings_expose_rag_defaults -q
```

预期： `PASS`。

- [ ] **步骤 7: 提交**

```bash
git add backend/requirements.txt backend/app/core/config.py backend/app/rag backend/app/tests/test_main_startup.py
git commit -m "backend: add rag configuration skeleton"
```

## 任务 2：定义 RAG 模型并初始化 ChromaDB + BGE

**文件：**
- 新增： `backend/app/rag/schemas.py`
- 新增： `backend/app/rag/embeddings.py`
- 新增： `backend/app/rag/store.py`
- 测试： `backend/app/tests/test_rag_retriever.py`

- [ ] **步骤 1: 编写失败的模型/存储测试**

创建 `backend/app/tests/test_rag_retriever.py`:

```python
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
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py::test_retrieved_chunk_exposes_required_metadata -q
```

预期： `FAIL`，因为当前还不存在 `app.rag.schemas`。

- [ ] **步骤 3: 实现类型模型**

创建 `backend/app/rag/schemas.py`:

```python
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    doc_type: str
    text: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class RetrievedChunk:
    doc_id: str
    chunk_id: str
    doc_type: str
    content: str
    score: float
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class IndexingResult:
    document_count: int
    chunk_count: int
    doc_ids: List[str]
```

- [ ] **步骤 4: 增加嵌入模型工厂**

创建 `backend/app/rag/embeddings.py`:

```python
from functools import lru_cache

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.rag.settings import RagSettings


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbedding:
    rag_settings = RagSettings()
    return HuggingFaceEmbedding(model_name=rag_settings.embedding_model)
```

- [ ] **步骤 5: 增加持久化 Chroma 向量存储初始化**

创建 `backend/app/rag/store.py`:

```python
from pathlib import Path

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.rag.embeddings import get_embedding_model
from app.rag.settings import RagSettings


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
```

- [ ] **步骤 6: 运行测试并确认其通过**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py::test_retrieved_chunk_exposes_required_metadata -q
```

预期： `PASS`。

- [ ] **步骤 7: 提交**

```bash
git add backend/app/rag backend/app/tests/test_rag_retriever.py
git commit -m "backend: add rag schemas and vector store bootstrap"
```

## 任务 3：使用 SimpleDirectoryReader 实现本地 Runbook 索引

**文件：**
- 新增： `backend/app/rag/indexer.py`
- 新增： `backend/app/tests/test_rag_indexer.py`

- [ ] **步骤 1: 编写失败的 Runbook 索引测试**

创建 `backend/app/tests/test_rag_indexer.py`:

```python
from pathlib import Path

from app.rag.indexer import load_runbook_documents


def test_load_runbook_documents_attaches_metadata(tmp_path: Path):
    doc_path = tmp_path / "payment-service.md"
    doc_path.write_text("# 支付服务\n\n连接池耗尽时先检查慢 SQL。", encoding="utf-8")

    docs = load_runbook_documents(tmp_path)

    assert len(docs) == 1
    assert docs[0].doc_type == "runbook"
    assert docs[0].metadata["source_path"].endswith("payment-service.md")
    assert "连接池耗尽" in docs[0].text
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_indexer.py::test_load_runbook_documents_attaches_metadata -q
```

预期： `FAIL`，因为当前还不存在 `load_runbook_documents`。

- [ ] **步骤 3: 实现 Runbook 加载**

创建 `backend/app/rag/indexer.py`:

```python
from pathlib import Path
from typing import Iterable, List

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

from app.rag.schemas import IndexingResult, KnowledgeDocument
from app.rag.settings import RagSettings
from app.rag.store import build_index


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
            metadata={"doc_id": doc.doc_id, "doc_type": doc.doc_type, **doc.metadata},
        )
        for doc in documents
    ]


def index_documents(documents: Iterable[KnowledgeDocument]) -> IndexingResult:
    docs = list(documents)
    if not docs:
        return IndexingResult(document_count=0, chunk_count=0, doc_ids=[])

    rag_settings = RagSettings()
    splitter = SentenceSplitter(
        chunk_size=rag_settings.chunk_size,
        chunk_overlap=rag_settings.chunk_overlap,
    )
    llama_docs = _to_llama_documents(docs)
    nodes = splitter.get_nodes_from_documents(llama_docs)
    build_index().insert_nodes(nodes)
    return IndexingResult(
        document_count=len(docs),
        chunk_count=len(nodes),
        doc_ids=[doc.doc_id for doc in docs],
    )
```

- [ ] **步骤 4: 运行测试并确认其通过**

运行：

```bash
cd backend && pytest app/tests/test_rag_indexer.py::test_load_runbook_documents_attaches_metadata -q
```

预期： `PASS`。

- [ ] **步骤 5: 补充实际索引结果的失败测试**

追加到 `backend/app/tests/test_rag_indexer.py`:

```python
from app.rag.indexer import index_documents
from app.rag.schemas import KnowledgeDocument


def test_index_documents_returns_chunk_counts(monkeypatch):
    class FakeIndex:
        def insert_nodes(self, nodes):
            self.nodes = nodes

    fake_index = FakeIndex()
    monkeypatch.setattr("app.rag.indexer.build_index", lambda: fake_index)

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
```

- [ ] **步骤 6: 运行完整的索引测试文件**

运行：

```bash
cd backend && pytest app/tests/test_rag_indexer.py -q
```

预期： `PASS`。

- [ ] **步骤 7: 提交**

```bash
git add backend/app/rag/indexer.py backend/app/tests/test_rag_indexer.py
git commit -m "backend: add runbook indexing pipeline"
```

## 任务 4：增加已确认 RCA 索引能力

**文件：**
- 修改： `backend/app/rag/indexer.py`
- 新增： `backend/app/tests/test_rag_writer.py`

- [ ] **步骤 1: 编写失败的已确认 RCA 文档测试**

创建 `backend/app/tests/test_rag_writer.py`:

```python
from types import SimpleNamespace

from app.rag.indexer import build_rca_document


def test_build_rca_document_includes_confirmed_metadata():
    rca = SimpleNamespace(
        run_id="run-1",
        root_cause="数据库连接池耗尽",
        resolution="扩容连接池并回滚慢 SQL",
        prevention_items_json=["增加慢 SQL 告警"],
        report_markdown="# RCA",
        confirmed_by_human=1,
    )
    run = SimpleNamespace(
        service="payment-service",
        env="staging",
        severity="P2",
    )

    doc = build_rca_document(rca, run)

    assert doc.doc_id == "rca:run-1"
    assert doc.doc_type == "rca"
    assert doc.metadata["validated"] is True
    assert doc.metadata["service"] == "payment-service"
    assert "数据库连接池耗尽" in doc.text
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_writer.py::test_build_rca_document_includes_confirmed_metadata -q
```

预期： `FAIL`，因为当前还不存在 `build_rca_document`。

- [ ] **步骤 3: 实现 RCA 文档构造**

追加到 `backend/app/rag/indexer.py`:

```python
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
```

- [ ] **步骤 4: 运行测试并确认其通过**

运行：

```bash
cd backend && pytest app/tests/test_rag_writer.py::test_build_rca_document_includes_confirmed_metadata -q
```

预期： `PASS`。

- [ ] **步骤 5: 提交**

```bash
git add backend/app/rag/indexer.py backend/app/tests/test_rag_writer.py
git commit -m "backend: add confirmed rca document builder"
```

## 任务 5：实现 BGE 重排序

**文件：**
- 新增： `backend/app/rag/reranker.py`
- 修改： `backend/app/tests/test_rag_retriever.py`

- [ ] **步骤 1: 编写失败的重排序测试**

追加到 `backend/app/tests/test_rag_retriever.py`:

```python
from app.rag.reranker import rerank


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
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py::test_rerank_sorts_chunks_by_cross_encoder_score -q
```

预期： `FAIL`，因为当前还不存在 `app.rag.reranker`。

- [ ] **步骤 3: 实现重排序适配器**

创建 `backend/app/rag/reranker.py`:

```python
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
```

- [ ] **步骤 4: 运行重排序测试**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py::test_rerank_sorts_chunks_by_cross_encoder_score -q
```

预期： `PASS`。

- [ ] **步骤 5: 提交**

```bash
git add backend/app/rag/reranker.py backend/app/tests/test_rag_retriever.py
git commit -m "backend: add bge reranker adapter"
```

## 任务 6：实现带元数据过滤与重排序编排的语义检索

**文件：**
- 新增： `backend/app/rag/retriever.py`
- 修改： `backend/app/tests/test_rag_retriever.py`

- [ ] **步骤 1: 编写失败的检索结果转换测试**

追加到 `backend/app/tests/test_rag_retriever.py`:

```python
from types import SimpleNamespace

from app.rag.retriever import _to_retrieved_chunks


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
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py::test_to_retrieved_chunks_preserves_score_and_metadata -q
```

预期： `FAIL`，因为当前还不存在 `app.rag.retriever`。

- [ ] **步骤 3: 实现检索模块**

创建 `backend/app/rag/retriever.py`:

```python
from typing import Any, Dict, Iterable, List

from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

from app.rag.schemas import RetrievedChunk
from app.rag.reranker import rerank
from app.rag.settings import RagSettings
from app.rag.store import build_index


def build_query(service: str, incident_type: str, symptom: str) -> str:
    parts = [service, incident_type, symptom]
    return " ".join(part for part in parts if part).strip()


def _build_filters(filters: Dict[str, Any]) -> MetadataFilters | None:
    metadata_filters = [
        MetadataFilter(key=key, value=value, operator=FilterOperator.EQ)
        for key, value in filters.items()
        if value is not None
    ]
    return MetadataFilters(filters=metadata_filters) if metadata_filters else None


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


def retrieve(query: str, filters: Dict[str, Any], top_k: int | None = None) -> List[RetrievedChunk]:
    rag_settings = RagSettings()
    retriever = build_index().as_retriever(
        similarity_top_k=top_k or rag_settings.top_k,
        filters=_build_filters(filters),
    )
    chunks = _to_retrieved_chunks(retriever.retrieve(query))
    return rerank(query, chunks) if rag_settings.enable_reranker else chunks
```

- [ ] **步骤 4: 运行检索测试并确认其通过**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py::test_to_retrieved_chunks_preserves_score_and_metadata -q
```

预期： `PASS`。

- [ ] **步骤 5: 补充查询/过滤器失败测试**

追加到 `backend/app/tests/test_rag_retriever.py`:

```python
from app.rag.retriever import build_query, _build_filters


def test_build_query_and_filters_keep_business_context():
    assert build_query("payment-service", "database", "5xx 升高") == "payment-service database 5xx 升高"

    filters = _build_filters(
        {"service": "payment-service", "env": "staging", "validated": True}
    )

    assert len(filters.filters) == 3
```

- [ ] **步骤 6: 运行完整的检索测试文件**

运行：

```bash
cd backend && pytest app/tests/test_rag_retriever.py -q
```

预期： `PASS`。

- [ ] **步骤 7: 提交**

```bash
git add backend/app/rag/retriever.py backend/app/tests/test_rag_retriever.py
git commit -m "backend: add rag retrieval service"
```

## 任务 7：实现已确认 RCA 写回

**文件：**
- 新增： `backend/app/rag/writer.py`
- 修改： `backend/app/services/knowledge_writeback.py`
- 修改： `backend/app/tests/test_rag_writer.py`

- [ ] **步骤 1: 编写失败的仅允许已确认写回测试**

追加到 `backend/app/tests/test_rag_writer.py`:

```python
from app.rag.writer import write_back_confirmed_rca


def test_write_back_confirmed_rca_skips_unconfirmed(monkeypatch):
    class FakeRca:
        confirmed_by_human = 0

    class FakeRepo:
        def get(self, run_id):
            return FakeRca()

    result = write_back_confirmed_rca(
        run_id="run-1",
        rca_repo=FakeRepo(),
        runs_repo=object(),
        index_documents_fn=lambda docs: (_ for _ in ()).throw(AssertionError("should not index")),
    )

    assert result is None
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_writer.py::test_write_back_confirmed_rca_skips_unconfirmed -q
```

预期： `FAIL`，因为当前还不存在 `app.rag.writer`。

- [ ] **步骤 3: 实现写回模块**

创建 `backend/app/rag/writer.py`:

```python
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
    document = build_rca_document(rca, run)
    return index_documents_fn([document])
```

- [ ] **步骤 4: 运行测试并确认其通过**

运行：

```bash
cd backend && pytest app/tests/test_rag_writer.py::test_write_back_confirmed_rca_skips_unconfirmed -q
```

预期： `PASS`。

- [ ] **步骤 5: 补充正向写回测试**

追加到 `backend/app/tests/test_rag_writer.py`:

```python
def test_write_back_confirmed_rca_indexes_validated_document():
    class FakeRca:
        run_id = "run-2"
        root_cause = "数据库连接池耗尽"
        resolution = "扩容连接池"
        prevention_items_json = []
        report_markdown = "# RCA"
        confirmed_by_human = 1

    class Fake运行：
        service = "payment-service"
        env = "staging"
        severity = "P2"

    class FakeRcaRepo:
        def get(self, run_id):
            return FakeRca()

    class FakeRunsRepo:
        def get(self, run_id):
            return FakeRun()

    captured = {}

    def fake_index_documents(docs):
        captured["docs"] = docs
        return "indexed"

    result = write_back_confirmed_rca(
        run_id="run-2",
        rca_repo=FakeRcaRepo(),
        runs_repo=FakeRunsRepo(),
        index_documents_fn=fake_index_documents,
    )

    assert result == "indexed"
    assert captured["docs"][0].doc_id == "rca:run-2"
    assert captured["docs"][0].metadata["validated"] is True
```

- [ ] **步骤 6: 替换仅记录日志的服务占位实现**

在 `backend/app/services/knowledge_writeback.py` 中，将 `_do_writeback(...)` 替换为：

```python
    def _do_writeback(
        self,
        record: IncidentKnowledgeWriteback,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
    ):
        """Write confirmed RCA into the RAG vector store."""
        from app.rag.writer import write_back_confirmed_rca
        from app.repositories.runs_repo import RunsRepo

        result = write_back_confirmed_rca(
            run_id=record.run_id,
            rca_repo=self.rca_repo,
            runs_repo=RunsRepo(self.db),
        )
        if result is None:
            raise ValueError(f"RCA for run {record.run_id} is not confirmed and cannot be indexed")
```

- [ ] **步骤 7: 运行写回测试**

运行：

```bash
cd backend && pytest app/tests/test_rag_writer.py -q
```

预期： `PASS`。

- [ ] **步骤 8: 提交**

```bash
git add backend/app/rag/writer.py backend/app/services/knowledge_writeback.py backend/app/tests/test_rag_writer.py
git commit -m "backend: connect confirmed rca writeback to rag"
```

## 任务 8：将 RAG 检索接入图中的记忆节点

**文件：**
- 修改： `backend/app/graph/nodes/retrieve_memory.py`
- 修改： `backend/app/models/evidence.py`
- 新增： `backend/app/tests/test_retrieve_memory_rag.py`

- [ ] **步骤 1: 编写失败的图节点集成测试**

创建 `backend/app/tests/test_retrieve_memory_rag.py`:

```python
import pytest

from app.graph.nodes.retrieve_memory import retrieve_memory_node
from app.rag.schemas import RetrievedChunk


@pytest.mark.asyncio
async def test_retrieve_memory_node_injects_history_evidence(monkeypatch):
    monkeypatch.setattr(
        "app.graph.nodes.retrieve_memory.retrieve",
        lambda query, filters, top_k: [
            RetrievedChunk(
                doc_id="rca:run-1",
                chunk_id="chunk-1",
                doc_type="rca",
                content="历史案例：数据库连接池耗尽",
                score=0.93,
                metadata={"service": "payment-service", "env": "staging"},
            )
        ],
    )

    state = {
        "run_id": "run-current",
        "ticket": {"service": "payment-service", "env": "staging", "description": "5xx 升高"},
        "triage": {"incident_type": "database"},
        "evidence_items": [],
    }

    result = await retrieve_memory_node(state)

    assert result["memory_hits"][0].source == "rca"
    assert result["evidence_items"][0].category == "history"
    assert result["evidence_items"][0].raw_payload["doc_id"] == "rca:run-1"
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_retrieve_memory_rag.py::test_retrieve_memory_node_injects_history_evidence -q
```

预期： `FAIL`，因为当前 `retrieve_memory_node` 还没有使用 RAG 检索器。

- [ ] **步骤 3: 升级节点实现**

Replace `backend/app/graph/nodes/retrieve_memory.py` with:

```python
"""Memory retrieval node: fetches relevant runbooks and historical RCA knowledge."""

import logging
import uuid
from typing import List

from app.graph.state import IncidentAgentState
from app.models.evidence import EvidenceItem
from app.models.planning import MemoryHit
from app.rag.retriever import build_query, retrieve

logger = logging.getLogger(__name__)


def _safe_get(obj, key: str, default=""):
    if obj is None:
        return default
    return getattr(obj, key, obj.get(key, default) if isinstance(obj, dict) else default)


async def retrieve_memory_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    triage = state.get("triage")
    service = _safe_get(ticket, "service")
    env = _safe_get(ticket, "env")
    description = _safe_get(ticket, "description")
    incident_type = _safe_get(triage, "incident_type")

    query = build_query(service, incident_type, description)
    chunks = retrieve(
        query=query,
        filters={"service": service, "env": env, "validated": True},
        top_k=5,
    )

    memory_hits: List[MemoryHit] = []
    evidence_items = state.get("evidence_items", [])
    for chunk in chunks:
        memory_hits.append(
            MemoryHit(
                source=chunk.doc_type,
                content=chunk.content,
                relevance_score=chunk.score,
                metadata=chunk.metadata,
            )
        )
        evidence_items.append(
            EvidenceItem(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                tool_name="rag_retriever",
                category="history" if chunk.doc_type == "rca" else "runbook",
                source_ref=chunk.doc_id,
                summary=chunk.content[:120],
                raw_payload={
                    "doc_id": chunk.doc_id,
                    "chunk_id": chunk.chunk_id,
                    "doc_type": chunk.doc_type,
                    "score": chunk.score,
                    "metadata": chunk.metadata,
                },
                confidence=min(max(chunk.score, 0.0), 1.0),
                freshness_score=0.8,
                completeness_score=0.8,
                tags=[chunk.doc_type],
            )
        )

    state["memory_hits"] = memory_hits
    state["evidence_items"] = evidence_items
    state["step_count"] = state.get("step_count", 0) + 1
    return state
```

- [ ] **步骤 4: 扩展证据类别说明**

在 `backend/app/models/evidence.py` 中，将类别字段说明改为：

```python
        ..., description="Evidence category (logs/metrics/deployments/runbook/history)"
```

- [ ] **步骤 5: 运行集成测试**

运行：

```bash
cd backend && pytest app/tests/test_retrieve_memory_rag.py -q
```

预期： `PASS`。

- [ ] **步骤 6: 提交**

```bash
git add backend/app/graph/nodes/retrieve_memory.py backend/app/models/evidence.py backend/app/tests/test_retrieve_memory_rag.py
git commit -m "backend: inject rag results into graph evidence"
```

## 任务 9：增加本地索引的轻量启动入口

**文件：**
- 修改： `backend/app/rag/indexer.py`
- 修改： `backend/app/tests/test_rag_indexer.py`

- [ ] **步骤 1: 编写失败的启动入口测试**

追加到 `backend/app/tests/test_rag_indexer.py`:

```python
from app.rag.indexer import index_local_runbooks


def test_index_local_runbooks_uses_configured_directory(monkeypatch, tmp_path):
    monkeypatch.setattr("app.rag.indexer.RagSettings", lambda: type("S", (), {"runbook_dir": str(tmp_path)})())
    monkeypatch.setattr(
        "app.rag.indexer.load_runbook_documents",
        lambda directory: [
            KnowledgeDocument(
                doc_id="runbook:test",
                doc_type="runbook",
                text="hello",
                metadata={"validated": True},
            )
        ],
    )
    monkeypatch.setattr("app.rag.indexer.index_documents", lambda docs: "indexed")

    assert index_local_runbooks() == "indexed"
```

- [ ] **步骤 2: 运行测试并确认其失败**

运行：

```bash
cd backend && pytest app/tests/test_rag_indexer.py::test_index_local_runbooks_uses_configured_directory -q
```

预期： `FAIL`，因为当前还不存在 `index_local_runbooks`。

- [ ] **步骤 3: 实现启动辅助函数**

追加到 `backend/app/rag/indexer.py`:

```python
def index_local_runbooks() -> IndexingResult:
    rag_settings = RagSettings()
    documents = load_runbook_documents(Path(rag_settings.runbook_dir))
    return index_documents(documents)
```

- [ ] **步骤 4: 运行索引测试**

运行：

```bash
cd backend && pytest app/tests/test_rag_indexer.py -q
```

预期： `PASS`。

- [ ] **步骤 5: 提交**

```bash
git add backend/app/rag/indexer.py backend/app/tests/test_rag_indexer.py
git commit -m "backend: add local runbook indexing entrypoint"
```

## 任务 10：对 Phase 6 闭环做回归测试

**文件：**
- 仅测试

- [ ] **步骤 1: 运行聚焦的 RAG 测试集**

运行：

```bash
cd backend && pytest \
  app/tests/test_rag_indexer.py \
  app/tests/test_rag_retriever.py \
  app/tests/test_rag_writer.py \
  app/tests/test_retrieve_memory_rag.py \
  -q
```

预期： 全部测试通过。

- [ ] **步骤 2: 运行相邻图流程/API 回归测试**

运行：

```bash
cd backend && pytest \
  app/tests/test_graph_integration.py \
  app/tests/test_incidents_api.py \
  app/tests/test_resume_and_evidence.py \
  -q
```

预期： 全部测试通过。

- [ ] **步骤 3: 运行完整后端测试集**

运行：

```bash
cd backend && pytest app/tests/ -x -q
```

预期： 全部后端测试通过。

- [ ] **步骤 4: 提交**

```bash
git add .
git commit -m "backend: complete phase 6 rag loop"
```

## 自查

### 1. 需求覆盖检查

- 知识源入库：任务 3 与任务 4。
- LlamaIndex + ChromaDB + BGE 技术栈：任务 1 与任务 2。
- 带元数据过滤的检索：任务 6。
- 接入 LangGraph：任务 8。
- 仅允许已确认 RCA 写回：任务 7。
- BGE-Reranker 实现与编排：任务 5 与任务 6。
- 本地 Runbook 启动入口：任务 9。
- 回归验证：任务 10。

### 2. 占位符检查

- 文档中已不存在 `TODO`、`TBD`、“implement later” 或未指明内容的“add tests”等占位表述。
- 每个任务都包含明确的文件路径、测试代码、实现代码、执行命令与预期结果。

### 3. 类型一致性检查

- `KnowledgeDocument`、`RetrievedChunk` 与 `IndexingResult` 只在 `schemas.py` 中定义一次，并在后续任务中保持一致复用。
- `retrieve(...)` 返回 `List[RetrievedChunk]`，与 `retrieve_memory_node(...)` 的消费方式完全一致。
- 已确认 RCA 写回复用 `build_rca_document(...)` 与 `index_documents(...)`，避免重复实现入库逻辑。
