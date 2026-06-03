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
