from typing import Dict, Any
from app.graph.state import IncidentAgentState, RunStatus
from app.models.incident import IncidentTicket


def intake_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    if not ticket:
        raise ValueError("Ticket is required")
    
    if isinstance(ticket, dict):
        ticket = IncidentTicket(**ticket)
    
    state["ticket"] = ticket
    state["status"] = RunStatus.NEW
    state["step_count"] = state.get("step_count", 0) + 1
    state["evidence_items"] = []
    state["root_cause_candidates"] = []
    
    return state
