"""Regression tests: specialist timeout values must match calibrated DeepSeek latency."""
from app.models.planning import AgentTask
import yaml
from pathlib import Path


def test_agent_task_default_timeout_is_120s():
    task = AgentTask(agent_id="k8s_specialist", category="k8s", service="svc", env="staging")
    assert task.timeout_ms == 120000, (
        f"AgentTask.timeout_ms default should be 120000, got {task.timeout_ms}. "
        "Reason: single DeepSeek specialist worst-case = 3 rounds x 60s + final 60s = 240s; "
        "120s covers P95 for real calls with per-LLM 60s ceiling."
    )


def test_agent_configs_yaml_all_specialists_have_timeout_ms():
    yaml_path = Path(__file__).parent.parent / "graph" / "nodes" / "agent_configs.yaml"
    data = yaml.safe_load(yaml_path.read_text())
    for agent in data["agents"]:
        assert "timeout_ms" in agent, (
            f"agent_configs.yaml entry '{agent['agent_id']}' missing timeout_ms. "
            "All specialists must have explicit timeout_ms >= 120000."
        )
        assert agent["timeout_ms"] >= 120000, (
            f"agent '{agent['agent_id']}' timeout_ms={agent['timeout_ms']} < 120000."
        )


def test_specialist_agent_llm_deadline_ceiling_is_60s():
    """LLM single-call deadline should be 60s, not 30s."""
    import inspect
    from app.graph.nodes import specialist_agent
    source = inspect.getsource(specialist_agent)
    assert "min(remaining_ms / 1000, 60.0)" in source, (
        "specialist_agent.py: single LLM call deadline ceiling must be 60.0s "
        "(was 30.0s, too small for DeepSeek real eval latency)"
    )


def test_fanout_total_timeout_is_300s():
    """evidence_fanout asyncio.wait total timeout must be 300s."""
    import inspect
    from app.graph import nodes as graph_nodes
    source = inspect.getsource(graph_nodes)
    assert "timeout=300.0" in source, (
        "evidence_fanout node: asyncio.wait total timeout must be 300.0s "
        "(was 150.0s, insufficient for 5 parallel specialists at DeepSeek latency with 60s per-LLM ceiling)"
    )
