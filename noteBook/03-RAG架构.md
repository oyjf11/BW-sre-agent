# 03 — RAG 架构

> RAG（Retrieval-Augmented Generation，检索增强生成）子系统详解。

---

## 1. 什么是 RAG

一句话：**让 LLM 在回答之前，先从知识库里检索相关资料，再结合资料生成答案**。避免 LLM 瞎编（幻觉）。

在 OpsPilot 里，RAG 做两件事：
- **检索历史经验**：过去处理过的类似故障是怎么解决的（RCA 报告）
- **检索运维手册**：这个服务的标准操作流程是什么（runbook）

---

## 2. 整体架构

```
┌──────────────────────────────────────────────────────┐
│                    数据写入线                          │
│                                                      │
│  本地 Markdown 文档 ──→ indexer ──→ ChromaDB         │
│  已确认 RCA 报告  ──→ indexer ──→ ChromaDB         │
│                                                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    数据检索线                          │
│                                                      │
│  retrieve_memory_node ──→ retriever ──→ ChromaDB     │
│        │                      │                      │
│        │                  reranker（可选）             │
│        │                      │                      │
│        └────── MemoryHit + EvidenceItem ──→ state    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 3. 配置 (`backend/app/rag/settings.py`)

```python
@dataclass(frozen=True)
class RagSettings:
    enabled: bool = False                # 默认关闭
    persist_dir: str = "./storage/chroma" # 向量存储目录
    collection_name: str = "opspilot_knowledge"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"  # 中文嵌入模型
    chunk_size: int = 512                # 文档分块大小
    chunk_overlap: int = 80              # 分块重叠区域
    runbook_dir: str = "./knowledge/runbooks"  # 运维手册目录
    top_k: int = 5                       # 检索返回条数
    enable_reranker: bool = False        # 默认关闭重排序
```

所有配置从 `backend/.env` 读取，前缀 `RAG_`（如 `RAG_ENABLED=true`）。

类比：就像 `vite.config.ts` 里的各种配置项。

---

## 4. 嵌入层 (`embeddings.py`)

**作用**：把文本变成向量（一串数字），让计算机能「理解」语义。

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def get_embedding_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
```

- 使用 BGE（BAAI General Embedding）中文模型
- 懒加载：import 在函数内部，不调用就不加载（节省启动时间）
- `@lru_cache` 缓存单例

类比：`text.split('').map(char => charCodeAt(char))` 的升级版，但保留了语义关系。

---

## 5. 向量存储 (`store.py`)

```python
# 使用 ChromaDB 作为向量存储后端
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex

# 初始化
client = chromadb.PersistentClient(path="./storage/chroma")
collection = client.get_or_create_collection("opspilot_knowledge")
vector_store = ChromaVectorStore(chroma_collection=collection)
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=model)
```

**ChromaDB** 是一个嵌入式向量数据库，数据存在本地磁盘，无需单独部署服务。

类比：SQLite 之于关系数据库，ChromaDB 之于向量数据库 —— 轻量、嵌入式、零配置。

---

## 6. 索引层 (`indexer.py`)

### 6.1 索引文档

```python
# 两种文档来源

# 1. 本地 runbook 文档
def index_runbook_documents():
    documents = SimpleDirectoryReader(runbook_dir).load_data()
    for doc in documents:
        knowledge_doc = KnowledgeDocument(
            doc_type="runbook",
            content=doc.text,
            metadata={"service": ..., "category": ...}
        )
    index_documents(knowledge_docs)

# 2. 已确认的 RCA 报告（从数据库读取）
def index_confirmed_rca_reports():
    reports = db.query(RcaReport).filter(confirmed_by_human == True)
    for report in reports:
        knowledge_doc = KnowledgeDocument(
            doc_type="rca",
            content=report.report_markdown,
            metadata={"service": ..., "incident_type": ...}
        )
    index_documents(knowledge_docs)
```

### 6.2 统一索引入口

```python
def index_documents(documents: List[KnowledgeDocument]):
    # 1. 用 SentenceSplitter 分块（每块 512 字符，重叠 80 字符）
    # 2. 每块生成向量嵌入
    # 3. 写入 ChromaDB
    for doc in documents:
        nodes = splitter.get_nodes_from_documents([doc])
        index.insert_nodes(nodes)
```

类比：
- `SentenceSplitter` ≈ 把长文本按段落+句子切成小段
- `index.insert_nodes()` ≈ `db.insert(messages)` 但存的是向量

---

## 7. 检索层 (`retriever.py`)

### 7.1 主检索流程

```python
def retrieve(query: str, filters: dict = None, top_k: int = 5):
    # 1. 构建元数据过滤条件
    metadata_filters = MetadataFilters(
        filters=[
            MetadataFilter(key="service", value=filters.get("service")),
            MetadataFilter(key="env", value=filters.get("env")),
            MetadataFilter(key="doc_type", value=filters.get("doc_type")),
        ]
    )

    # 2. 语义搜索
    retriever = index.as_retriever(
        similarity_top_k=top_k,
        filters=metadata_filters
    )
    chunks = retriever.retrieve(query)

    # 3. 可选重排序
    if settings.enable_reranker:
        chunks = rerank(query, chunks)

    return chunks
```

### 7.2 查询构建

```python
def build_query(service: str, incident_type: str, symptom: str) -> str:
    # 拼接检索 query
    return f"{service} {incident_type} {symptom}"
```

### 7.3 结果转换

```python
def chunks_to_evidence(chunks, run_id):
    evidence_items = []
    for chunk in chunks:
        evidence_items.append(EvidenceItem(
            run_id=run_id,
            source="rag",
            tool_name="rag_retrieve",
            category=chunk.metadata.get("doc_type"),
            summary=chunk.text[:200],
            confidence=chunk.score
        ))
    return evidence_items
```

---

## 8. 重排序层 (`reranker.py`)

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("BAAI/bge-reranker-base")

def rerank(query, chunks):
    # 对每对 (query, chunk) 打分
    pairs = [(query, chunk.text) for chunk in chunks]
    scores = model.predict(pairs)

    # 按分数降序排序
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in ranked]
```

**为什么需要 rerank？**

向量检索是用「向量近似度」排序，但精确度有限。CrossEncoder reranker 直接比较 query 和每个 chunk，更准确。代价是更慢——所以默认关闭，只在需要高质量检索时开启。

类比：向量检索 ≈ 搜索引擎的初筛，reranker ≈ 人工精排。

---

## 9. 写回层 (`writer.py`)

当人工确认了一个 RCA 报告后，将它写回向量存储，供未来检索使用：

```python
def write_back_confirmed_rca(run_id: str):
    # 1. 从 DB 读取已确认的 RCA 报告
    report = rca_repo.get(run_id)

    # 2. 构建 KnowledgeDocument
    doc = KnowledgeDocument(
        doc_type="rca",
        content=report.report_markdown,
        metadata={
            "source_run_id": run_id,
            "service": ...,
            "incident_type": ...,
        }
    )

    # 3. 索引到 ChromaDB
    index_documents([doc])
```

这样形成一个闭环：故障处置 → 产出报告 → 写回知识库 → 未来相似故障能检索到。

---

## 10. 与 Agent 工作流的集成

```
retrieve_memory_node(state):
  │
  ├─→ RAG 检索
  │     query = build_query(service, incident_type, symptom)
  │     chunks = retrieve(query, filters)
  │     memory_hits = chunks_to_memory_hits(chunks)
  │     evidence_items += chunks_to_evidence(chunks)
  │
  ├─→ Runbook 工具调用
  │     result = gateway.call_tool("query_runbook", params)
  │     memory_hits += result_to_memory_hits(result)
  │
  └─→ state["memory_hits"] = memory_hits
      state["evidence_items"] += evidence_items
```

---

## 11. RAG 完整数据流

```
写入阶段：
  runbook/*.md → SimpleDirectoryReader → 分块 → 嵌入 → ChromaDB
  数据库 RCA 报告 → build_rca_document → 分块 → 嵌入 → ChromaDB

检索阶段：
  故障 query → 嵌入 → ChromaDB 相似度搜索 → top_k chunks
    → (可选) reranker 精排
    → MemoryHit[] + EvidenceItem[]
    → 注入 state.evidence_items

写回阶段：
  RCA 确认 → write_back_confirmed_rca → 分块 → 嵌入 → ChromaDB
```

---

## 12. 关键文件速查

| 文件 | 作用 |
|------|------|
| `app/rag/settings.py` | RAG 配置 |
| `app/rag/embeddings.py` | 嵌入模型工厂 |
| `app/rag/store.py` | ChromaDB + LlamaIndex 初始化 |
| `app/rag/indexer.py` | 文档索引（runbook + RCA） |
| `app/rag/retriever.py` | 语义检索 + metadata filter |
| `app/rag/reranker.py` | BGE reranker 精排 |
| `app/rag/writer.py` | RCA → 向量存储写回 |

---

## 小结

RAG 的本质是**外挂了一个可检索的长期记忆**。三个核心流程：

1. **写入**（index）→ 把文档变成向量存起来
2. **检索**（retrieve）→ 根据 query 找到最相关的几段
3. **写回**（writeback）→ 确认后的知识反哺知识库

下一篇：[04 — Tool 架构](./04-Tool架构.md)
