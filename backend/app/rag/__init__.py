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
