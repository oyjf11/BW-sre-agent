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

export interface TerminalReason {
  code: string;
  stage: string;
  message: string;
  failed_tools?: string[];
  missing_evidence_categories?: string[];
}

export interface RunDetail extends RunSummary {
  ticket?: IncidentTicket;
  current_node?: string;
  halted_at_node?: string;
  terminal_reason?: TerminalReason;
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

export interface TraceEvent {
  name: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface TraceSpan {
  span_id: string;
  name: string;
  run_id?: string;
  parent_id?: string;
  start_time: number;
  start_timestamp: string;
  end_time?: number;
  end_timestamp?: string;
  duration_ms?: number;
  status?: string;
  error?: string;
  events: TraceEvent[];
}

export interface RunTrace {
  run_id: string;
  provider: string;
  trace_url: string;
  external_trace_id?: string;
  external_root_span_id?: string;
  external_trace_url?: string;
  spans: TraceSpan[];
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
  supporting_evidence_ids?: string[];
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
  ticket_id?: string;
  title?: string;
  description?: string;
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
  root_cause_status?: string;
  resolution: string;
  prevention_items: string[];
  confirmed_by_human: boolean;
  candidate_hypotheses?: Array<{ hypothesis: string; confidence: number }>;
  automation_outcome?: Record<string, unknown>;
  manual_next_steps?: string[];
}

export interface LlmConfig {
  provider: string;
  openai_api_key: string;
  openai_model: string;
  minimax_api_key: string;
  minimax_group_id: string;
  minimax_model: string;
  deepseek_api_key: string;
  deepseek_model: string;
}

export interface EvidenceCollectionResult {
  status: string;
  tool_name: string;
  category: string;
  summary?: string;
  error_summary?: string;
  latency_ms: number;
  collected_at: string;
}

export interface EvidenceCollectionResults {
  run_id: string;
  collection_results: EvidenceCollectionResult[];
  evidence_quality_score?: number;
  missing_evidence_categories: string[];
  failed_evidence_tools: string[];
}
