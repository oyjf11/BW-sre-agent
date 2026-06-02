from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class RunStatusEnum(str, enum.Enum):
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


class IncidentRun(Base):
    __tablename__ = "incident_runs"

    run_id = Column(String, primary_key=True)
    thread_id = Column(String, nullable=False)
    ticket_id = Column(String, nullable=True)
    status = Column(SQLEnum(RunStatusEnum), nullable=False, default=RunStatusEnum.NEW)
    severity = Column(String, nullable=True)
    service = Column(String, nullable=True)
    env = Column(String, nullable=True)
    current_node = Column(String, nullable=True)
    halted_at_node = Column(String, nullable=True)
    terminal_reason_json = Column(JSON, nullable=True)
    input_source = Column(String, nullable=True)
    schema_version = Column(Integer, nullable=False, default=1)
    step_count = Column(Integer, nullable=False, default=0)
    last_error_code = Column(String, nullable=True)
    last_error_message = Column(Text, nullable=True)
    requires_human = Column(Integer, nullable=False, default=0)
    summary_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    started_by = Column(String, nullable=True)

    checkpoints = relationship("IncidentCheckpoint", back_populates="run")
    evidence_items = relationship("IncidentEvidence", back_populates="run")
    approvals = relationship("IncidentApproval", back_populates="run")
    actions = relationship("IncidentAction", back_populates="run")
    rca_report = relationship("IncidentRcaReport", back_populates="run", uselist=False)
    events = relationship("IncidentRunEvent", back_populates="run")


class IncidentCheckpoint(Base):
    __tablename__ = "incident_checkpoints"

    checkpoint_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False)
    node_name = Column(String, nullable=False)
    state_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run = relationship("IncidentRun", back_populates="checkpoints")


class IncidentEvidence(Base):
    __tablename__ = "incident_evidence"

    evidence_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False)
    tool_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    source_ref = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    raw_payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run = relationship("IncidentRun", back_populates="evidence_items")


class IncidentApproval(Base):
    __tablename__ = "incident_approvals"

    approval_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False)
    action_json = Column(JSON, nullable=False)
    risk_level = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    reason = Column(Text, nullable=True)
    expected_impact = Column(Text, nullable=True)
    rollback_plan = Column(Text, nullable=True)
    approver = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    run = relationship("IncidentRun", back_populates="approvals")


class IncidentAction(Base):
    __tablename__ = "incident_actions"

    action_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False)
    idempotency_key = Column(String, nullable=True, unique=True)
    action_type = Column(String, nullable=False)
    params_json = Column(JSON, nullable=False)
    execution_status = Column(String, nullable=False, default="PENDING")
    result_json = Column(JSON, nullable=True)
    approval_id = Column(String, nullable=True)
    attempt_no = Column(Integer, nullable=False, default=1)
    executor_name = Column(String, nullable=True)
    request_json = Column(JSON, nullable=True)
    verification_status = Column(String, nullable=True)
    verification_details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    run = relationship("IncidentRun", back_populates="actions")


class IncidentRcaReport(Base):
    __tablename__ = "incident_rca_reports"

    run_id = Column(String, ForeignKey("incident_runs.run_id"), primary_key=True)
    report_markdown = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    root_cause_status = Column(String, nullable=True)
    resolution = Column(Text, nullable=False)
    prevention_items_json = Column(JSON, nullable=True)
    confirmed_by_human = Column(Integer, default=0)
    timeline_summary = Column(Text, nullable=True)
    impact_assessment = Column(Text, nullable=True)
    supporting_evidence_ids_json = Column(JSON, nullable=True)
    executed_action_ids_json = Column(JSON, nullable=True)
    candidate_hypotheses_json = Column(JSON, nullable=True)
    automation_outcome_json = Column(JSON, nullable=True)
    manual_next_steps_json = Column(JSON, nullable=True)
    archive_ref = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run = relationship("IncidentRun", back_populates="rca_report")


class IncidentKnowledgeWriteback(Base):
    __tablename__ = "incident_knowledge_writebacks"

    writeback_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False, index=True)
    target = Column(String, nullable=False)
    content_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IncidentToolAudit(Base):
    __tablename__ = "incident_tool_audits"

    audit_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False, index=True)
    tool_name = Column(String, nullable=False)
    adapter_mode = Column(String, nullable=False)
    request_json = Column(JSON, nullable=True)
    response_json = Column(JSON, nullable=True)
    success = Column(Integer, nullable=False, default=1)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class IncidentRunEvent(Base):
    __tablename__ = "incident_run_events"

    event_id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("incident_runs.run_id"), nullable=False, index=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String, nullable=False, default="INFO")
    type = Column(String, nullable=False)
    node_name = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    data_json = Column(JSON, nullable=True)

    run = relationship("IncidentRun", back_populates="events")
