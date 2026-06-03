"""Unit tests for SpecialistAgent — ReAct loop, degradation paths, rule fallback."""

import json
import pytest

from app.models.planning import (
    AgentTask,
    AgentRunStatus,
    SpecialistAnalysis,
    SpecialistEvidence,
    AnomalySignal,
)
from app.graph.nodes.specialist_agent import (
    SpecialistAgent,
    SpecialistAgentConfig,
    load_agent_configs,
    validate_agent_config,
    FORBIDDEN_TOOLS,
    _build_default_agent_tasks,
)


def make_config(**overrides) -> SpecialistAgentConfig:
    defaults = {
        "agent_id": "k8s_specialist",
        "category": "k8s",
        "description": "Test K8s agent",
        "enabled": True,
        "max_tool_rounds": 2,
        "system_prompt_version": "1.0.0",
        "tool_names": ["query_k8s_pods", "query_k8s_events"],
        "system_prompt": "You are a K8s expert. Output JSON.",
    }
    defaults.update(overrides)
    return SpecialistAgentConfig(**defaults)


class TestConfigLoading:
    def test_load_from_yaml(self):
        configs = load_agent_configs()
        assert len(configs) == 5
        assert "k8s_specialist" in configs
        assert configs["k8s_specialist"].enabled is True

    def test_load_nonexistent_file(self):
        configs = load_agent_configs(path="/nonexistent/config.yaml")
        assert configs == {}

    def test_each_agent_has_prompt(self):
        configs = load_agent_configs()
        for aid, cfg in configs.items():
            assert cfg.system_prompt, f"{aid} missing system_prompt"
            assert cfg.system_prompt_version, f"{aid} missing version"

    def test_tool_names_non_overlapping(self):
        configs = load_agent_configs()
        all_tools = set()
        for cfg in configs.values():
            for tn in cfg.tool_names:
                assert tn not in all_tools, f"Tool '{tn}' appears in multiple agents"
                all_tools.add(tn)


class TestValidateAgentConfig:
    def test_forbidden_tool_blocked(self):
        ok = validate_agent_config("test_agent", "k8s", ["execute_action", "query_k8s_pods"])
        assert ok is False

    def test_category_prefix_mismatch_blocked(self):
        ok = validate_agent_config("test_agent", "k8s", ["query_k8s_pods", "query_db_processlist"])
        assert ok is False

    def test_valid_config_passes(self):
        ok = validate_agent_config("k8s_specialist", "k8s", ["query_k8s_pods", "query_k8s_events"])
        assert ok is True

    def test_logs_category_exact_match(self):
        ok = validate_agent_config("log_specialist", "logs", ["query_logs"])
        assert ok is True

    def test_forbidden_tools_empty(self):
        assert FORBIDDEN_TOOLS == {"execute_action"}


class TestSpecialistAgentProduceFinalAnalysis:
    @pytest.mark.asyncio
    async def test_l0_completed_with_valid_json(self, monkeypatch):
        config = make_config()
        agent = SpecialistAgent(config)
        task = AgentTask(agent_id="k8s_specialist", category="k8s", service="test", env="staging")

        async def fake_complete_async(messages, tools=None, temperature=0.7, max_tokens=2000):
            return {
                "content": json.dumps({
                    "conclusion": "正常: all pods healthy",
                    "severity": "info",
                    "anomalies": [],
                    "correlation_hints": [],
                    "confidence": 0.85,
                }),
                "tool_calls": None,
            }

        monkeypatch.setattr("app.graph.nodes.specialist_agent.llm_client.complete_async", fake_complete_async)

        agent.messages = [{"role": "system", "content": "you are k8s expert"}]
        agent.raw_tool_results = {"query_k8s_pods": {"pods": []}}
        agent.llm_had_error = False
        agent.round_truncated = False

        result = await agent._produce_final_analysis(task, "run_1", "")
        assert result.run_status == AgentRunStatus.COMPLETED
        assert result.confidence > 0.0
        assert len(result.evidence_items) > 0

    @pytest.mark.asyncio
    async def test_l1_json_parse_fail_degraded(self, monkeypatch):
        config = make_config()
        agent = SpecialistAgent(config)
        task = AgentTask(agent_id="k8s_specialist", category="k8s", service="test", env="staging")

        async def fake_bad_json(messages, tools=None, temperature=0.7, max_tokens=2000):
            return {"content": "not json at all", "tool_calls": None}

        monkeypatch.setattr("app.graph.nodes.specialist_agent.llm_client.complete_async", fake_bad_json)

        agent.messages = [{"role": "system", "content": "you are k8s expert"}]
        agent.raw_tool_results = {"query_k8s_pods": {"pods": []}}
        agent.llm_had_error = False

        result = await agent._produce_final_analysis(task, "run_1", "")
        assert result.run_status == AgentRunStatus.PARTIAL
        assert result.partial is True
        assert result.confidence <= 0.25

    @pytest.mark.asyncio
    async def test_l2_llm_error_with_raw_data(self, monkeypatch):
        config = make_config()
        agent = SpecialistAgent(config)
        task = AgentTask(agent_id="k8s_specialist", category="k8s", service="test", env="staging")

        async def fake_error(messages, tools=None, temperature=0.7, max_tokens=2000):
            raise RuntimeError("LLM crash")

        monkeypatch.setattr("app.graph.nodes.specialist_agent.llm_client.complete_async", fake_error)

        agent.messages = [{"role": "system", "content": "you are k8s expert"}]
        agent.raw_tool_results = {"query_k8s_pods": {"pods": [{"name": "pod1", "container_statuses": []}]}}
        agent.llm_had_error = True

        result = await agent._produce_final_analysis(task, "run_1", "")
        assert result.run_status == AgentRunStatus.PARTIAL
        assert result.partial is True

    @pytest.mark.asyncio
    async def test_l3_no_llm_no_data(self, monkeypatch):
        config = make_config()
        agent = SpecialistAgent(config)
        task = AgentTask(agent_id="k8s_specialist", category="k8s", service="test", env="staging")

        async def fake_error(messages, tools=None, temperature=0.7, max_tokens=2000):
            raise RuntimeError("LLM crash")

        monkeypatch.setattr("app.graph.nodes.specialist_agent.llm_client.complete_async", fake_error)

        agent.messages = [{"role": "system", "content": "you are k8s expert"}]
        agent.raw_tool_results = {}
        agent.llm_had_error = True

        result = await agent._produce_final_analysis(task, "run_1", "")
        assert result.run_status == AgentRunStatus.LLM_FAILED
        assert result.confidence == 0.0
        assert result.partial is True


class TestSpecialistAgentRuleExtraction:
    def test_k8s_crashloopbackoff_signal(self):
        config = make_config(category="k8s")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_k8s_pods": {
                "pods": [
                    {
                        "name": "payment-7d5f8b9c-abcde",
                        "container_statuses": [
                            {
                                "state": {
                                    "waiting": {"reason": "CrashLoopBackOff"}
                                }
                            }
                        ]
                    }
                ]
            }
        }
        agent._extraact_signals_by_rules()
        assert len(agent._rule_anomalies) >= 1
        signals = [a.signal_type for a in agent._rule_anomalies]
        assert "CrashLoopBackOff" in signals

    def test_k8s_oomkilled_signal(self):
        config = make_config(category="k8s")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_k8s_pods": {
                "pods": [
                    {
                        "name": "pod-1",
                        "container_statuses": [
                            {"state": {"terminated": {"reason": "OOMKilled"}}}
                        ]
                    }
                ]
            }
        }
        agent._extraact_signals_by_rules()
        assert any(a.signal_type == "OOMKilled" for a in agent._rule_anomalies)

    def test_k8s_replicas_mismatch(self):
        config = make_config(category="k8s")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_k8s_deployment_status": {
                "ready_replicas": 1,
                "desired_replicas": 3,
            }
        }
        agent._extraact_signals_by_rules()
        assert any(a.signal_type == "replicas_mismatch" for a in agent._rule_anomalies)

    def test_db_high_connections(self):
        config = make_config(category="db")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_db_processlist": {
                "processlist": [
                    {"COMMAND": "Query"}, {"COMMAND": "Query"},
                    {"COMMAND": "Query"}, {"COMMAND": "Query"},
                    {"COMMAND": "Query"}, {"COMMAND": "Query"},
                    {"COMMAND": "Query"}, {"COMMAND": "Query"},
                    {"COMMAND": "Query"}, {"COMMAND": "Query"},
                ] * 6
            }
        }
        agent._extraact_signals_by_rules()
        assert any(a.signal_type == "high_connections" for a in agent._rule_anomalies)

    def test_db_slow_queries(self):
        config = make_config(category="db")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_db_slow_queries": {
                "slow_queries": list(range(15))
            }
        }
        agent._extraact_signals_by_rules()
        assert any(a.signal_type == "slow_queries" for a in agent._rule_anomalies)

    def test_log_high_error_count(self):
        config = make_config(category="logs")
        agent = SpecialistAgent(config)
        error_log = " ".join(["ERROR timeout"] * 15 + ["FATAL oom"] * 3)
        agent.raw_tool_results = {
            "query_logs": {"logs": [error_log], "count": 1}
        }
        agent._extraact_signals_by_rules()
        assert any(a.signal_type == "high_error_logs" for a in agent._rule_anomalies)

    def test_metrics_spike(self):
        config = make_config(category="metrics")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_metrics": {
                "metrics": {
                    "cpu_usage": {"values": [10, 80]},
                }
            }
        }
        agent._extraact_signals_by_rules()
        assert any("spike" in a.signal_type for a in agent._rule_anomalies)

    def test_deployment_rule_hints(self):
        config = make_config(category="deployments")
        agent = SpecialistAgent(config)
        agent.raw_tool_results = {
            "query_deployments": {"deployments": [{"id": "dep-1"}]}
        }
        task = AgentTask(agent_id="deployment_specialist", category="deployments", service="s", env="p")
        hints = agent._extraact_correlation_hints_by_rules(task)
        assert len(hints) >= 2
        assert all(h.source == "rule" for h in hints)
        assert all(h.confidence == 0.6 for h in hints)


class TestSpecialistAgentToolGuard:
    def test_tool_allowed_blocks_hallucinated(self):
        config = make_config(tool_names=["query_k8s_pods"])
        agent = SpecialistAgent(config)
        tool_call = {
            "id": "call_1",
            "function": {"name": "query_db_processlist", "arguments": "{}"},
        }
        allowed = agent._tool_allowed(tool_call)
        assert allowed is False

    def test_tool_allowed_permits_valid(self):
        config = make_config(tool_names=["query_k8s_pods"])
        agent = SpecialistAgent(config)
        tool_call = {
            "id": "call_1",
            "function": {"name": "query_k8s_pods", "arguments": '{"service":"s","env":"e"}'},
        }
        allowed = agent._tool_allowed(tool_call)
        assert allowed is True


class TestBuildDefaultAgentTasks:
    def test_generates_5_tasks(self):
        from app.models.incident import IncidentTicket
        ticket = IncidentTicket(
            ticket_id="INC-001", title="test", description="test",
            service="payment-service", env="staging", severity="P2",
            source="manual",
        )
        tasks = _build_default_agent_tasks(ticket)
        assert len(tasks) == 5
        categories = {t.category for t in tasks}
        assert categories == {"k8s", "db", "logs", "metrics", "deployments"}

    def test_uses_ticket_service(self):
        from app.models.incident import IncidentTicket
        ticket = IncidentTicket(
            ticket_id="INC-001", title="test", description="test",
            service="order-service", env="prod", severity="P1",
            source="alertmanager",
        )
        tasks = _build_default_agent_tasks(ticket)
        assert all(t.service == "order-service" for t in tasks)

    def test_dict_ticket(self):
        ticket_dict = {"service": "auth-service", "env": "prod", "title": "test"}
        tasks = _build_default_agent_tasks(ticket_dict)
        assert all(t.service == "auth-service" for t in tasks)


class TestAgentResetState:
    def test_reset_on_new_run(self):
        config = make_config()
        agent = SpecialistAgent(config)
        agent._reset()
        assert agent.messages == []
        assert agent.raw_tool_results == {}
        assert agent.collected_tool_names == []
        assert agent.round_truncated is False
        assert agent.llm_had_error is False
