from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum
from app.models.incident import IncidentTicket
from app.models.triage import TriageResult
from app.models.evidence import EvidenceItem
from app.models.root_cause import RootCauseCandidate
from app.models.remediation import RemediationPlan
from app.models.approval import ApprovalRequest, ApprovalResult
from app.models.rca import RcaReport
from app.models.planning import MemoryHit, InvestigationPlan


class RunStatus(str, Enum):
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    PLANNED = "PLANNED"
    GATHERING_EVIDENCE = "GATHERING_EVIDENCE"
    DIAGNOSED = "DIAGNOSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    WAITING_HUMAN = "WAITING_HUMAN"
    NEEDS_HUMAN = "NEEDS_HUMAN"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentError(TypedDict):
    code: str
    message: str
    node_name: Optional[str]
    retryable: bool
    details: Optional[Dict[str, Any]]


class IncidentAgentState(TypedDict, total=False):
    run_id: str
    thread_id: str
    schema_version: int
    current_node: Optional[str]
    ticket: Optional[IncidentTicket]
    triage: Optional[TriageResult]
    memory_hits: List[MemoryHit]
    investigation_plan: Optional[InvestigationPlan]
    plan: Optional[Dict[str, Any]]
    evidence_items: List[EvidenceItem]
    root_cause_candidates: List[RootCauseCandidate]
    remediation_plan: Optional[RemediationPlan]
    pending_approval: Optional[ApprovalRequest]
    approval_result: Optional[ApprovalResult]
    rca_report: Optional[RcaReport]
    status: RunStatus
    step_count: int
    loop_count: int
    max_loop_count: int
    retries: Dict[str, int]
    error: Optional[AgentError]
    errors: List[AgentError]
    evidence_summary: Optional[str]
    evidence_quality_score: Optional[float]
    missing_evidence_categories: List[str]
    failed_evidence_tools: List[str]
    evidence_collection_results: List[Dict[str, Any]]
    critic_decision: Optional[str]
    risk_decision: Optional[str]
    verify_decision: Optional[str]
    action_results: List[Dict[str, Any]]
    verification_evidence_ids: List[str]
    execution_results: List[Dict[str, Any]]
    final_outcome: Optional[str]
    terminal_reason: Optional[Dict[str, Any]]
    halted_at_node: Optional[str]
    user_context: Optional[Dict[str, Any]]
    # Internal resume control
    _resume_from_node: Optional[str]
