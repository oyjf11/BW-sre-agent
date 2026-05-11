import inspect
from langgraph.graph import StateGraph, END
from app.graph.state import IncidentAgentState
from app.graph.nodes import (
    intake_node,
    triage_node,
    planner_node,
    evidence_fanout_node,
    evidence_aggregate_node,
    diagnose_node,
    critic_node,
    remediation_node,
    risk_gate_node,
    approval_interrupt_node,
    executor_node,
    verify_outcome_node,
    rca_node,
)
from app.graph.nodes.retrieve_memory import retrieve_memory_node

MAX_STEPS = 30
MAX_EXECUTOR_RETRIES = 2


def _wrap_with_events(node_name: str, fn):
    """Wrap a node function to emit NODE_STARTED before execution and NODE_FAILED on error.

    Uses a ContextVar hook injected by GraphRunner so that the builder stays
    decoupled from the database/event system. In test runs where no hook is set
    the wrapper is a transparent pass-through.
    """
    from app.graph.context import get_node_event_hook
    from app.services.event_bus import EventType

    if inspect.iscoroutinefunction(fn):

        async def _async_wrapped(state: IncidentAgentState) -> IncidentAgentState:
            hook = get_node_event_hook()
            if hook:
                hook(
                    EventType.NODE_STARTED,
                    node_name,
                    message=f"Node {node_name} started",
                    level="INFO",
                )
            try:
                return await fn(state)
            except Exception as exc:
                if hook:
                    hook(
                        EventType.NODE_FAILED,
                        node_name,
                        message=f"Node {node_name} failed: {exc}",
                        level="ERROR",
                        data={"error": str(exc)[:500]},
                    )
                raise

        _async_wrapped.__name__ = fn.__name__ if hasattr(fn, "__name__") else node_name
        return _async_wrapped
    else:

        def _sync_wrapped(state: IncidentAgentState) -> IncidentAgentState:
            hook = get_node_event_hook()
            if hook:
                hook(
                    EventType.NODE_STARTED,
                    node_name,
                    message=f"Node {node_name} started",
                    level="INFO",
                )
            try:
                return fn(state)
            except Exception as exc:
                if hook:
                    hook(
                        EventType.NODE_FAILED,
                        node_name,
                        message=f"Node {node_name} failed: {exc}",
                        level="ERROR",
                        data={"error": str(exc)[:500]},
                    )
                raise

        _sync_wrapped.__name__ = fn.__name__ if hasattr(fn, "__name__") else node_name
        return _sync_wrapped


# Allowed resume entry points for the dispatcher
_RESUME_ALLOWED_NODES = {
    "node_intake",
    "node_executor",
    "node_risk_gate",
    "node_evidence_fanout",
}


def _route_dispatcher(state: IncidentAgentState) -> str:
    """Entry dispatcher: route to the correct start node for fresh runs or resumes."""
    import logging

    logger = logging.getLogger(__name__)
    resume_node = state.get("_resume_from_node")
    logger.info(f"_route_dispatcher: resume_node={resume_node}, state keys={list(state.keys())}")
    if resume_node and resume_node in _RESUME_ALLOWED_NODES:
        logger.info(f"_route_dispatcher: routing to {resume_node}")
        return resume_node
    logger.info(f"_route_dispatcher: routing to node_intake (default)")
    return "node_intake"


def _route_after_critic(state: IncidentAgentState) -> str:
    decision = state.get("critic_decision", "PASS")
    if decision == "NEED_MORE_EVIDENCE":
        return "node_evidence_fanout"
    if decision in ("REPLAN", "CONTRADICTION"):
        return "node_planner"
    return "node_remediation"


def _route_after_risk_gate(state: IncidentAgentState) -> str:
    decision = state.get("risk_decision", "LOW_ONLY")
    if decision == "BLOCKED":
        return "node_rca"  # Skip execution, go straight to RCA for failed run
    if decision == "NEEDS_APPROVAL":
        return "node_approval_interrupt"
    return "node_executor"


def _route_after_verify(state: IncidentAgentState) -> str:
    decision = state.get("verify_decision", "SUCCESS")
    if decision == "SUCCESS":
        return "node_rca"
    if decision == "RETRYABLE_FAILURE":
        retries = state.get("retries", {})
        executor_retries = retries.get("executor", 0)
        if executor_retries < MAX_EXECUTOR_RETRIES:
            return "node_executor"
        # Exhausted retries - treat as fatal
        return "node_rca"
    # FATAL_FAILURE → go to RCA with failure context
    return "node_rca"


def create_incident_graph() -> StateGraph:
    """
    Create and compile the incident handling LangGraph.

    Flow:
        intake -> triage -> retrieve_memory -> planner -> evidence_fanout ->
        evidence_aggregate -> diagnose -> critic ->
          PASS -> remediation -> risk_gate -> (executor -> verify) | approval_interrupt
          NEED_MORE_EVIDENCE -> evidence_fanout (loop back)
          REPLAN/CONTRADICTION -> planner (loop back)

        verify ->
          SUCCESS -> rca -> END
          RETRYABLE_FAILURE -> executor (retry, limited)
          FATAL_FAILURE -> rca -> END
    """
    graph = StateGraph(IncidentAgentState)

    # Dispatcher: passthrough node that routes to correct start node (no wrap needed)
    graph.add_node("node_dispatcher", lambda state: state)
    graph.add_node("node_intake", _wrap_with_events("node_intake", intake_node))
    graph.add_node("node_triage", _wrap_with_events("node_triage", triage_node))
    graph.add_node(
        "node_retrieve_memory", _wrap_with_events("node_retrieve_memory", retrieve_memory_node)
    )
    graph.add_node("node_planner", _wrap_with_events("node_planner", planner_node))
    graph.add_node(
        "node_evidence_fanout", _wrap_with_events("node_evidence_fanout", evidence_fanout_node)
    )
    graph.add_node(
        "node_evidence_aggregate",
        _wrap_with_events("node_evidence_aggregate", evidence_aggregate_node),
    )
    graph.add_node("node_diagnose", _wrap_with_events("node_diagnose", diagnose_node))
    graph.add_node("node_critic", _wrap_with_events("node_critic", critic_node))
    graph.add_node("node_remediation", _wrap_with_events("node_remediation", remediation_node))
    graph.add_node("node_risk_gate", _wrap_with_events("node_risk_gate", risk_gate_node))
    graph.add_node(
        "node_approval_interrupt",
        _wrap_with_events("node_approval_interrupt", approval_interrupt_node),
    )
    graph.add_node("node_executor", _wrap_with_events("node_executor", executor_node))
    graph.add_node(
        "node_verify_outcome", _wrap_with_events("node_verify_outcome", verify_outcome_node)
    )
    graph.add_node("node_rca", _wrap_with_events("node_rca", rca_node))

    graph.set_entry_point("node_dispatcher")
    graph.add_conditional_edges(
        "node_dispatcher",
        _route_dispatcher,
        {
            "node_intake": "node_intake",
            "node_executor": "node_executor",
            "node_risk_gate": "node_risk_gate",
            "node_evidence_fanout": "node_evidence_fanout",
        },
    )
    graph.add_edge("node_intake", "node_triage")
    graph.add_edge("node_triage", "node_retrieve_memory")
    graph.add_edge("node_retrieve_memory", "node_planner")
    graph.add_edge("node_planner", "node_evidence_fanout")
    graph.add_edge("node_evidence_fanout", "node_evidence_aggregate")
    graph.add_edge("node_evidence_aggregate", "node_diagnose")
    graph.add_edge("node_diagnose", "node_critic")

    # Critic 4-way routing with loop-back edges
    graph.add_conditional_edges(
        "node_critic",
        _route_after_critic,
        {
            "node_remediation": "node_remediation",
            "node_evidence_fanout": "node_evidence_fanout",
            "node_planner": "node_planner",
        },
    )

    graph.add_edge("node_remediation", "node_risk_gate")
    graph.add_conditional_edges(
        "node_risk_gate",
        _route_after_risk_gate,
        {
            "node_rca": "node_rca",
            "node_approval_interrupt": "node_approval_interrupt",
            "node_executor": "node_executor",
        },
    )

    graph.add_edge("node_executor", "node_verify_outcome")

    # Verify 3-way routing: SUCCESS→rca, RETRYABLE→executor (retry), FATAL→rca
    graph.add_conditional_edges(
        "node_verify_outcome",
        _route_after_verify,
        {
            "node_rca": "node_rca",
            "node_executor": "node_executor",
        },
    )

    graph.add_edge("node_approval_interrupt", END)
    graph.add_edge("node_rca", END)

    return graph.compile()
