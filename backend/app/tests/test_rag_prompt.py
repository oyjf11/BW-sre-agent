"""Tests for RAG anti-hallucination prompt template and citation tools."""

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
