import { api } from './api';
import type {
  RunSummary,
  RunDetail,
  RunEvent,
  RunTrace,
  RcaReport,
  IncidentTicket,
  EvidenceItem,
  RunDiagnosis,
  RunRemediation,
  EvidenceCollectionResults,
} from '../types';

interface CreateRunByTicket {
  ticket: IncidentTicket;
}

interface CreateRunByTicketId {
  ticket_id: string;
}

interface AlertEventPayload {
  alert_name: string;
  service: string;
  env: string;
  severity: string;
  description?: string;
  labels?: Record<string, string>;
  started_at?: string;
}

interface CreateRunByAlertEvent {
  alert_event: AlertEventPayload;
}

export type CreateRunRequest = CreateRunByTicket | CreateRunByTicketId | CreateRunByAlertEvent;

export const runs = {
  createRun: (data: CreateRunRequest) =>
    api.post<RunSummary>('/incidents/runs', data),

  getRun: (runId: string) =>
    api.get<RunDetail>(`/incidents/runs/${runId}`),

  listRuns: (limit = 100, offset = 0) =>
    api.get<RunSummary[]>(`/incidents/runs?limit=${limit}&offset=${offset}`),

  getRunEvents: (runId: string, lastEventId?: string) => {
    const url = lastEventId
      ? `/incidents/runs/${runId}/events?last_event_id=${encodeURIComponent(lastEventId)}`
      : `/incidents/runs/${runId}/events`;
    return api.get<RunEvent[]>(url);
  },

  getRunTrace: (runId: string) =>
    api.get<RunTrace>(`/incidents/runs/${runId}/trace`),

  getRunEvidence: (runId: string) =>
    api.get<EvidenceItem[]>(`/incidents/runs/${runId}/evidence`),

  getEvidenceCollectionResults: (runId: string) =>
    api.get<EvidenceCollectionResults>(`/incidents/runs/${runId}/evidence/collection-results`),

  getRunActions: (runId: string) =>
    api.get<any[]>(`/incidents/runs/${runId}/actions`),

  getRunDiagnosis: (runId: string) =>
    api.get<RunDiagnosis>(`/incidents/runs/${runId}/diagnosis`),

  getRunRemediation: (runId: string) =>
    api.get<RunRemediation>(`/incidents/runs/${runId}/remediation`),

  getRunRca: (runId: string) =>
    api.get<RcaReport>(`/incidents/runs/${runId}/rca`),
};
