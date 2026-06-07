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
        conn.commit()
    finally:
        conn.close()


def write_chunks_to_fts(db_path: str, chunks: List[Dict[str, Any]]) -> None:
    """Write chunks to FTS5 index. Idempotent: deletes existing chunk_id before insert."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("BEGIN")
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            content = chunk.get("content", "")
            doc_type = chunk.get("doc_type", "")
            service = chunk.get("service", "")
            conn.execute("DELETE FROM rag_chunks_fts WHERE chunk_id = ?", (chunk_id,))
            conn.execute("DELETE FROM rag_chunks_meta WHERE chunk_id = ?", (chunk_id,))
            conn.execute(
                "INSERT INTO rag_chunks_fts(content, chunk_id) VALUES (?, ?)",
                (content, chunk_id),
            )
            conn.execute(
                "INSERT INTO rag_chunks_meta(chunk_id, doc_type, service) VALUES (?, ?, ?)",
                (chunk_id, doc_type, service),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def search_fts(db_path: str, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """FTS5 keyword search. Returns list of {chunk_id, content, doc_type, service, score}."""
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
    # Use prefix matching (token*) so Chinese substrings are found even when
    # unicode61 does not split CJK runs into individual words.
    fts_query = " OR ".join(t + "*" for t in tokens)

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
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return []  # index not yet built — expected during cold start
        raise
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
