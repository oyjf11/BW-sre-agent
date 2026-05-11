"""Knowledge writeback node: writes confirmed RCA to knowledge base after human confirmation."""

import logging
from app.graph.state import IncidentAgentState

logger = logging.getLogger(__name__)


def writeback_knowledge_node(state: IncidentAgentState) -> IncidentAgentState:
    """Write RCA knowledge to store. Only executes if RCA is confirmed by human.

    This node is designed to be called after human confirmation via API,
    not as part of the main graph flow. It can be invoked as a post-confirm hook.
    """
    run_id = state.get("run_id", "unknown")
    rca_report = state.get("rca_report")

    if not rca_report:
        logger.info(f"No RCA report for run {run_id}, skipping writeback")
        return state

    confirmed = rca_report.confirmed_by_human if hasattr(rca_report, 'confirmed_by_human') else rca_report.get('confirmed_by_human', False)
    if not confirmed:
        logger.info(f"RCA for run {run_id} not confirmed, skipping writeback")
        return state

    from app.repositories import SessionLocal
    from app.services.knowledge_writeback import KnowledgeWritebackService

    db = SessionLocal()
    try:
        service = KnowledgeWritebackService(db)
        service.writeback(run_id, target="runbook")
    except Exception:
        logger.exception(f"Knowledge writeback failed for run {run_id}")
    finally:
        db.close()

    state["step_count"] = state.get("step_count", 0) + 1
    return state
