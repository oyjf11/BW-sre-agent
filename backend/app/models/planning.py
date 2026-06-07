"""Planning models for memory retrieval and investigation.
用于记忆检索和排查规划的模型定义。

@deprecated: InvestigationTask, InvestigationPlan — replaced by AgentTask / SpecialistAnalysis for Specialist Agent Pool.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class MemoryHit(BaseModel):
    source: str = Field(
        ..., description="Memory source (runbook/rca_history/service_doc/alert_experience)"
    )
    content: str = Field(..., description="Retrieved content")
    relevance_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Relevance to current incident"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class InvestigationTask(BaseModel):
    """@deprecated: Replaced by AgentTask for Specialist Agent Pool."""

    task_id: str = Field(..., description="Unique task identifier")
    category: str = Field(
        ..., description="Evidence category (logs/metrics/deployments/runbook/k8s/lb/db)"
    )
    tool_name: str = Field(..., description="Tool to call")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10 (1=highest)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    depends_on: List[str] = Field(
        default_factory=list, description="Task IDs this depends on"
    )
    degrade_on_failure: bool = Field(
        default=True, description="If true, failure degrades but doesn't terminate run"
    )
    timeout_ms: int = Field(default=30000, description="Timeout in milliseconds")


class InvestigationPlan(BaseModel):
    """@deprecated: Replaced by AgentTask list for Specialist Agent Pool."""

    tasks: List[InvestigationTask] = Field(
        default_factory=list, description="Investigation tasks"
    )
    rationale: str = Field(
        default="", description="Rationale for this investigation plan"
    )
    estimated_duration: Optional[str] = Field(
        default=None, description="Estimated total duration"
    )


# --- Specialist Agent Pool models (v2) ---


class AgentRunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    DEGRADED = "DEGRADED"
    TIMEOUT = "TIMEOUT"
    LLM_FAILED = "LLM_FAILED"


class AgentTask(BaseModel):
    agent_id: str = Field(..., description="Maps to SpecialistAgentConfig.agent_id")
    category: str = Field(..., description="k8s / db / logs / metrics / deployments")
    service: str = Field(..., description="Target service name")
    env: str = Field(..., description="Target environment")
    incident_type: str = Field(default="", description="From triage result")
    time_window_start: Optional[str] = Field(default=None, description="ISO 8601")
    time_window_end: Optional[str] = Field(default=None, description="ISO 8601")
    extra_context: Dict[str, Any] = Field(default_factory=dict, description="title/description etc.")
    timeout_ms: int = Field(default=90000, description="Agent total timeout in ms")


class AnomalySignal(BaseModel):
    signal_type: str = Field(..., description="e.g. CrashLoopBackOff, high_error_rate")
    evidence_ref: str = Field(default="", description="Reference to raw evidence source")
    description: str = Field(default="", description="Human-readable description")
    timestamp_hint: Optional[str] = Field(default=None, description="ISO 8601")


class CorrelationHint(BaseModel):
    source_category: str = Field(..., description="Agent category that produced this hint")
    target_category: str = Field(..., description="Agent category this hint points to")
    reason: str = Field(default="", description="Why this correlation exists")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence score")
    source: str = Field(default="rule", description="rule | llm")


class SpecialistEvidence(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence identifier")
    category: str = Field(..., description="Agent category (k8s/db/logs/metrics/deployments)")
    conclusion: str = Field(..., description="Prefix: 正常: | 异常: | 部分: | 失败:")
    severity: str = Field(default="info", description="info | warning | critical")
    anomalies: List[AnomalySignal] = Field(default_factory=list)
    correlation_hints: List[CorrelationHint] = Field(default_factory=list)


class SpecialistAnalysis(BaseModel):
    agent_id: str = Field(..., description="e.g. k8s_specialist")
    agent_category: str = Field(..., description="k8s / db / logs / metrics / deployments")
    evidence_items: List[SpecialistEvidence] = Field(default_factory=list)
    collected_tool_names: List[str] = Field(default_factory=list)
    raw_tool_results: Dict[str, Any] = Field(default_factory=dict)
    execution_summary: str = Field(default="", description="Debug info incl. system_prompt_version")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    run_status: AgentRunStatus = AgentRunStatus.LLM_FAILED
    partial: bool = Field(default=False, description="True = degraded analysis")
    truncated: bool = Field(default=False, description="True = cut off by timeout/rounds")
