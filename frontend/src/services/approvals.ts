import { api } from './api';
import type { ApprovalSummary, ApprovalDetail } from '../types';

interface DecisionRequest {
  decision: string;
  comment?: string;
}

export const approvals = {
  listPendingApprovals: () =>
    api.get<ApprovalSummary[]>('/approvals/pending'),

  getApproval: (id: string) =>
    api.get<ApprovalDetail>(`/approvals/${id}`),

  postDecision: (id: string, data: DecisionRequest) =>
    api.post<{ status: string }>(`/approvals/${id}/decision`, data),
};
