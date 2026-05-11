from typing import Dict, Any
from app.graph.state import IncidentAgentState, RunStatus
from app.models.triage import TriageResult


def triage_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    if not ticket:
        raise ValueError("Ticket is required for triage")
    
    service = ticket.service if hasattr(ticket, 'service') else ticket.get('service')
    env = ticket.env if hasattr(ticket, 'env') else ticket.get('env')
    severity = ticket.severity if hasattr(ticket, 'severity') else ticket.get('severity')
    
    triage_result = TriageResult(
        incident_type="service_degradation",
        severity=severity or "P2",
        suspected_services=[service] if service else [],
        suggested_time_window={"start": "1h ago", "end": "now"},
        requires_immediate_human=False,
        rationale=f"Based on ticket: {ticket.title if hasattr(ticket, 'title') else ticket.get('title', 'unknown')}",
    )
    
    state["triage"] = triage_result
    state["status"] = RunStatus.TRIAGED
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state
