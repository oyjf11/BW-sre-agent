import pytest

from app.graph.nodes.retrieve_memory import retrieve_memory_node
from app.models.incident import IncidentTicket
from app.models.triage import TriageResult
from app.rag.schemas import RetrievedChunk


@pytest.mark.asyncio
async def test_retrieve_memory_node_injects_rag_hits_and_history_evidence(monkeypatch):
    def fake_retrieve(query, filters, top_k=None):
        return [
            RetrievedChunk(
                doc_id="rca:payment-1",
                chunk_id="chunk-1",
                doc_type="rca",
                content="支付服务发布后出现 5xx，根因是数据库慢查询。",
                score=0.91,
                metadata={"service": "payment-service", "env": "prod"},
            )
        ]

    monkeypatch.setattr("app.graph.nodes.retrieve_memory.retrieve", fake_retrieve)

    state = {
        "run_id": "run-rag",
        "ticket": IncidentTicket(
            ticket_id="INC-RAG",
            title="支付服务 5xx 升高",
            description="发布后部分用户下单失败，怀疑慢查询",
            service="payment-service",
            env="prod",
            severity="P1",
            source="manual",
        ),
        "triage": TriageResult(
            incident_type="deployment_regression",
            severity="P1",
            suspected_services=["payment-service"],
            confidence=0.8,
            rationale="发布后异常",
        ),
        "evidence_items": [],
        "step_count": 0,
    }

    result = await retrieve_memory_node(state)

    assert result["memory_hits"][0].source == "rca"
    assert result["evidence_items"][0].category == "history"
