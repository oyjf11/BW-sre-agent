export interface IncidentTicket {
  ticket_id: string;
  title: string;
  description: string;
  service: string;
  env: string;
  severity: string;
  source: string;
  time_range?: Record<string, string>;
  metadata?: Record<string, unknown>;
}

export interface RunSummary {
  ticket_id: string;
  run_id: string;
  thread_id: string;
  status: string;
  severity?: string;
  service?: string;
  env?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
}

export interface RunDetail extends RunSummary {
  ticket?: IncidentTicket;
  current_node?: string;
  step_count?: number;
}

export interface RunEvent {
  event_id: string;
  run_id: string;
  level: string;
  type: string;
  node_name?: string;
  message: string;
  data?: Record<string, unknown>;
  timestamp: string;
}

export interface EvidenceItem {
  evidence_id: string;
  run_id?: string;
  tool_name: string;
  category: string;
  source_ref: string;
  summary: string;
  raw_payload?: Record<string, unknown>;
  confidence?: number;
  freshness_score?: number;
  completeness_score?: number;
  created_at?: string | null;
}

export interface RunDiagnosis {
  run_id: string;
  root_cause_candidates: RootCauseCandidate[];
  confidence?: number;
}

export interface RunRemediation {
  run_id: string;
  remediation_plan?: RemediationPlan;
}

export interface RootCauseCandidate {
  candidate_id: string;
  hypothesis: string;
  confidence: number;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  next_checks: string[];
}

export interface ActionSpec {
  action_type: string;
  service: string;
  env: string;
  params: Record<string, unknown>;
  risk_level: string;
  requires_approval: boolean;
  idempotency_key?: string;
}

export interface RemediationPlan {
  summary: string;
  actions: ActionSpec[];
  expected_outcome: string;
  rollback_plan?: string;
  risk_notes?: string;
}

export interface ApprovalSummary {
  approval_id: string;
  run_id: string;
  action: ActionSpec;
  risk_level: string;
  status: string;
  approver?: string;
  comment?: string;
  created_at: string;
}

export interface ApprovalDetail extends ApprovalSummary {
  reason: string;
  evidence_refs: string[];
  expected_impact: string;
  rollback_plan?: string;
}

export interface RcaReport {
  run_id: string;
  report_markdown: string;
  root_cause: string;
  resolution: string;
  prevention_items: string[];
  confirmed_by_human: boolean;
}
