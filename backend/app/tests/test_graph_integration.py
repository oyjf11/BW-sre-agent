"""Integration tests for the incident graph."""
import json

import pytest
from app.graph.builder import create_incident_graph
from app.graph.state import IncidentAgentState, RunStatus
from app.models.incident import IncidentTicket
from app.llm_client import llm_client


class TestIncidentGraph:
    def test_graph_creation(self):
        """Test that graph can be created."""
        graph = create_incident_graph()
        assert graph is not None
        assert hasattr(graph, "ainvoke")

    def test_graph_accepts_checkpointer_kwarg(self):
        """create_incident_graph(checkpointer=...) compiles; default None unchanged."""
        from langgraph.checkpoint.memory import MemorySaver

        default_graph = create_incident_graph()
        assert default_graph is not None

        cp_graph = create_incident_graph(checkpointer=MemorySaver())
        assert cp_graph is not None
        assert hasattr(cp_graph, "ainvoke")
    
    @pytest.mark.asyncio
    async def test_graph_execution(self, monkeypatch):
        """Test that graph executes a complete low-risk flow end-to-end."""
        import app.graph.builder as builder_module

        def low_risk_gate(state: IncidentAgentState) -> IncidentAgentState:
            state["risk_decision"] = "LOW_ONLY"
            state["step_count"] = (state.get("step_count") or 0) + 1
            return state

        async def passing_verify(state: IncidentAgentState) -> IncidentAgentState:
            state["verify_decision"] = "SUCCESS"
            state["status"] = RunStatus.COMPLETED
            state["step_count"] = (state.get("step_count") or 0) + 1
            return state

        def force_pass_critic(state: IncidentAgentState) -> IncidentAgentState:
            state["critic_decision"] = "PASS"
            state["evidence_quality_score"] = 0.9
            state["missing_evidence_categories"] = []
            state["step_count"] = (state.get("step_count") or 0) + 1
            return state

        monkeypatch.setattr(builder_module, "risk_gate_node", low_risk_gate)
        monkeypatch.setattr(builder_module, "verify_outcome_node", passing_verify)
        monkeypatch.setattr(builder_module, "critic_node", force_pass_critic)

        graph = create_incident_graph()

        ticket = IncidentTicket(
            ticket_id="test-001",
            title="Test Incident",
            description="Testing the graph",
            service="test-service",
            env="prod",
            severity="P2",
            source="test"
        )

        initial_state: IncidentAgentState = {
            "run_id": "test-run-001",
            "thread_id": "test-thread-001",
            "ticket": ticket,
            "evidence_items": [],
            "root_cause_candidates": [],
            "evidence_collection_results": [],
            "evidence_quality_score": 0.0,
            "step_count": 0,
        }

        result = await graph.ainvoke(initial_state)

        assert result is not None
        assert result.get("status") == RunStatus.COMPLETED
        assert result.get("step_count") > 0
        assert result.get("verify_decision") == "SUCCESS"
        assert len(result.get("evidence_items", [])) >= 4
    
    @pytest.mark.asyncio
    async def test_graph_flow(self, monkeypatch):
        """Test that graph executes expected nodes through the full chain."""
        import app.graph.builder as builder_module

        def low_risk_gate(state: IncidentAgentState) -> IncidentAgentState:
            state["risk_decision"] = "LOW_ONLY"
            state["step_count"] = (state.get("step_count") or 0) + 1
            return state

        def force_pass_critic(state: IncidentAgentState) -> IncidentAgentState:
            state["critic_decision"] = "PASS"
            state["evidence_quality_score"] = 0.9
            state["missing_evidence_categories"] = []
            state["step_count"] = (state.get("step_count") or 0) + 1
            return state

        monkeypatch.setattr(builder_module, "risk_gate_node", low_risk_gate)
        monkeypatch.setattr(builder_module, "critic_node", force_pass_critic)

        graph = create_incident_graph()

        ticket = IncidentTicket(
            ticket_id="test-002",
            title="CPU High Alert",
            description="Service CPU is at 95%",
            service="api-service",
            env="prod",
            severity="P1",
            source="monitoring"
        )

        initial_state: IncidentAgentState = {
            "run_id": "test-run-002",
            "thread_id": "test-thread-002",
            "ticket": ticket,
            "evidence_items": [],
            "root_cause_candidates": [],
            "evidence_collection_results": [],
            "evidence_quality_score": 0.0,
            "step_count": 0,
        }

        nodes_executed = []
        async for step in graph.astream(initial_state):
            nodes_executed.extend(step.keys())

        assert "node_intake" in nodes_executed
        assert "node_triage" in nodes_executed
        assert "node_planner" in nodes_executed
        assert "node_evidence_fanout" in nodes_executed
        assert "node_evidence_aggregate" in nodes_executed
        assert "node_executor" in nodes_executed
        assert "node_verify_outcome" in nodes_executed
        assert "node_rca" in nodes_executed

    @pytest.mark.asyncio
    async def test_graph_waits_for_approval_on_high_risk_action(self, monkeypatch):
        """High-risk remediation should stop at approval interrupt."""
        import app.graph.builder as builder_module

        def force_pass_critic(state: IncidentAgentState) -> IncidentAgentState:
            state["critic_decision"] = "PASS"
            state["evidence_quality_score"] = 0.9
            state["missing_evidence_categories"] = []
            state["step_count"] = (state.get("step_count") or 0) + 1
            return state

        monkeypatch.setattr(builder_module, "critic_node", force_pass_critic)

        graph = create_incident_graph()

        ticket = IncidentTicket(
            ticket_id="test-003",
            title="Release regression",
            description="Errors started after deployment",
            service="api-service",
            env="prod",
            severity="P1",
            source="monitoring"
        )

        def fake_complete_sync(prompt: str, system_prompt: str = None, temperature: float = 0.7):
            if "root cause candidates" in prompt:
                return """
                [
                  {
                    "hypothesis": "Recent deployment caused the incident",
                    "confidence": 0.9,
                    "next_checks": ["Check deployment logs"]
                  }
                ]
                """
            if "triage information" in prompt:
                return """
                {
                  "incident_type": "deployment_regression",
                  "severity": "P1",
                  "suspected_services": ["api-service"],
                  "suggested_time_window": {"start": "2h ago", "end": "now"},
                  "requires_immediate_human": false,
                  "rationale": "Deployment regression test"
                }
                """
            return "fallback_response"

        async def fake_complete_async(messages, tools=None, temperature: float = 0.7, max_tokens: int = 2000):
            if tools:
                has_tool_result = any(m.get("role") == "tool" for m in messages)
                if has_tool_result:
                    return {"content": "tool collection complete", "tool_calls": None}

                tool_calls = []
                for idx, tool in enumerate(tools):
                    tool_name = tool.get("function", {}).get("name")
                    args = {"service": "api-service", "env": "prod"}
                    if tool_name and tool_name.startswith("query_k8s_"):
                        args["namespace"] = "default"
                    tool_calls.append(
                        {
                            "id": f"call_{idx}",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(args),
                            },
                        }
                    )
                return {"content": "", "tool_calls": tool_calls}

            return {
                "content": json.dumps(
                    {
                        "conclusion": "异常: deterministic specialist analysis",
                        "severity": "warning",
                        "anomalies": [],
                        "correlation_hints": [],
                        "confidence": 0.8,
                    }
                ),
                "tool_calls": None,
            }

        monkeypatch.setattr(llm_client, "complete_sync", fake_complete_sync)
        monkeypatch.setattr(llm_client, "complete_async", fake_complete_async)

        initial_state: IncidentAgentState = {
            "run_id": "test-run-003",
            "thread_id": "test-thread-003",
            "ticket": ticket,
            "evidence_items": [],
            "root_cause_candidates": [],
            "evidence_collection_results": [],
            "evidence_quality_score": 0.0,
            "step_count": 0,
        }

        result = await graph.ainvoke(initial_state)

        assert result.get("status") == RunStatus.WAITING_HUMAN
        assert result.get("risk_decision") == "NEEDS_APPROVAL"
        assert result.get("pending_approval") is not None
