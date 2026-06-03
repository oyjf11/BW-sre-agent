# RAG 服务优化设计

> 基于 `.case/RAG/case.md` 案例对比，补齐当前 RAG 服务中缺失的 3 个能力。

## 背景

当前 `backend/app/rag/` 已完成检索+排序的基础链路，但与标准 RAG 案例对比存在 3 个缺口：

1. **无反幻觉 Prompt 模板** — 当前 RAG 层只做纯检索，不提供 LLM prompt 模板。下游 graph 节点（diagnose/rca）各自用 f-string 拼 prompt，缺少统一的溯源约束。
2. **重排序不截断** — `reranker.py` 对全部 chunk 重排分后全量返回，不按 top_n 截断，下游可能收到低相关度噪音。
3. **无来源标注格式** — 案例中定义了 `[来源：文件名]` 格式，当前项目未在 RAG 层定义来源追溯规范。

## 目标

在 RAG 模块内部补齐上述 3 项能力，不改动下游 graph 节点现有逻辑。

## 非目标

- 不改 `diagnose_node` / `rca_node` / `planner_node` 的现有 prompt
- 不改 `retrieve_memory_node` 的检索调用方式
- 不改 `writer.py`、`indexer.py`、`store.py`、`embeddings.py`

## 详细设计

### 优化 1：反幻觉 Prompt 模板 — 新增 `prompt.py`

**文件**：`backend/app/rag/prompt.py`

提供 3 个可导出的符号：

| 符号 | 类型 | 说明 |
|------|------|------|
| `ANTI_HALLUCINATION_TEMPLATE` | `str` | 反幻觉 prompt 模板字符串，含 `{context_str}` 和 `{query_str}` 占位符 |
| `format_rag_context(chunks)` | 函数 | 将 `List[RetrievedChunk]` 格式化为带来源标注的上下文文本 |
| `build_rag_prompt(query, chunks)` | 函数 | 一步生成完整反幻觉 prompt（模板填充） |

行为约束：
- `format_rag_context` 每个 chunk 标注 `[来源：{doc_id}]`，内容截断至 512 字符
- 模板 4 条规则：只答文档内容、强制标注来源、无匹配拒答、不引入外部知识

### 优化 2：重排序 top_n 截断

**涉及文件**：`settings.py`、`reranker.py`、`retriever.py`、`core/config.py`

| 变更 | 位置 | 说明 |
|------|------|------|
| 新增 `reranker_top_n: int = 5` | `settings.py` | 默认保留前 5 个 chunk |
| 新增 `RAG_RERANKER_TOP_N` 环境变量 | `core/config.py` | 可配置截断数量 |
| `rerank()` 增加 `top_n` 参数 | `reranker.py` | 重排分后 `[:top_n]` 截断 |
| 调用传 `rag_settings.reranker_top_n` | `retriever.py:90` | 与现有 `enable_reranker` 联动 |

行为约束：
- `top_n=0` 或 `None` 时返回全部（保持向后兼容）
- 重排分后按 score 降序排列再截断

### 优化 3：来源标注格式 — 合入 `prompt.py`

新增 2 个公开工具函数（与反幻觉模板在同一个文件）：

| 函数 | 签名 | 说明 |
|------|------|------|
| `format_chunk_citation` | `(chunk: RetrievedChunk) -> str` | 单个 chunk 的来源标注 |
| `format_chunks_with_citations` | `(chunks: List[RetrievedChunk]) -> str` | 多个 chunk 的编目来源列表 |

返回格式示例：
```
[来源：rca:run-abc123] 根因：数据库连接池耗尽...
```

`format_rag_context()` 内部复用 `format_chunk_citation`。

### 修改文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/rag/prompt.py` | **新增** | 反幻觉 prompt 模板 + 上下文格式化工具 |
| `backend/app/rag/settings.py` | 修改 | 新增 `reranker_top_n` 字段 |
| `backend/app/rag/reranker.py` | 修改 | `rerank()` 增加 top_n 参数和截断逻辑 |
| `backend/app/rag/retriever.py` | 修改 | 传 `reranker_top_n` 给 `rerank()` |
| `backend/app/core/config.py` | 修改 | 新增 `rag_reranker_top_n` 环境变量字段 |
| `backend/app/rag/__init__.py` | 修改 | 导出 `prompt.py` 新增函数 |
| `backend/app/tests/test_rag_retriever.py` | 修改 | 补 top_n 截断测试 |
| `backend/app/tests/test_rag_prompt.py` | **新增** | prompt 模板填充 + citation 格式单元测试 |

## 验收标准

1. `RAG_RERANKER_TOP_N` 环境变量可控制重排截断数量，默认 5
2. `rerank()` 重排后只返回 top_n 个 chunk（按 score 降序）
3. `ANTI_HALLUCINATION_TEMPLATE` 含 4 条反幻觉规则且 `format()` 可正确填充
4. `format_rag_context()` 产出带 `[来源：...]` 标注的上下文文本
5. 现有测试全部通过（`python -m pytest app/tests/ -x -q`）
6. 新增测试覆盖 prompt 模板填充、top_n 截断、citation 格式

## 风险与回滚

- **风险**：top_n 默认 5 可能丢弃高相关度 chunk（当前 `top_k=5` 时重排不截断无差异）。缓解：`top_n=0` 或 `None` 不截断。
- **回滚**：还原文件到 git HEAD 即可，无数据迁移。

## 待确认问题

- 无。设计已获批准。
