import { describe, it, expect, vi, beforeEach } from 'vitest';
import { approvals } from './approvals';
import * as apiModule from './api';

vi.mock('./api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApi = apiModule.api as ReturnType<typeof vi.fn>;

describe('approvals', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('listPendingApprovals', () => {
    it('fetches pending approvals', async () => {
      const mockApprovals = [
        {
          approval_id: 'apr-001',
          run_id: 'run-123',
          action: {
            action_type: 'restart',
            service: 'api-gateway',
            env: 'prod',
            params: {},
            risk_level: 'HIGH',
            requires_approval: true,
          },
          risk_level: 'HIGH',
          status: 'pending',
          created_at: '2024-01-15T10:00:00Z',
        },
      ];
      
      vi.mocked(mockApi.get).mockResolvedValue(mockApprovals);

      const result = await approvals.listPendingApprovals();
      
      expect(mockApi.get).toHaveBeenCalledWith('/approvals/pending');
      expect(result).toEqual(mockApprovals);
    });

    it('returns empty array when no approvals', async () => {
      vi.mocked(mockApi.get).mockResolvedValue([]);

      const result = await approvals.listPendingApprovals();
      
      expect(result).toEqual([]);
    });
  });

  describe('getApproval', () => {
    it('fetches approval by ID', async () => {
      const mockApproval = {
        approval_id: 'apr-001',
        run_id: 'run-123',
        action: {
          action_type: 'restart',
          service: 'api-gateway',
          env: 'prod',
          params: { pods: ['api-gateway-0'] },
          risk_level: 'MEDIUM',
          requires_approval: true,
        },
        risk_level: 'MEDIUM',
        status: 'pending',
        created_at: '2024-01-15T10:00:00Z',
        reason: 'Need to restart due to high memory usage',
        evidence_refs: ['ev-001', 'ev-002'],
        expected_impact: 'Minimal downtime',
      };
      
      vi.mocked(mockApi.get).mockResolvedValue(mockApproval);

      const result = await approvals.getApproval('apr-001');
      
      expect(mockApi.get).toHaveBeenCalledWith('/approvals/apr-001');
      expect(result).toEqual(mockApproval);
    });
  });

  describe('postDecision', () => {
    it('posts approval decision', async () => {
      vi.mocked(mockApi.post).mockResolvedValue({ status: 'approved' });

      const result = await approvals.postDecision('apr-001', {
        decision: 'approve',
        comment: 'Looks good',
      });
      
      expect(mockApi.post).toHaveBeenCalledWith('/approvals/apr-001/decision', {
        decision: 'approve',
        comment: 'Looks good',
      });
      expect(result).toEqual({ status: 'approved' });
    });

    it('posts rejection decision', async () => {
      vi.mocked(mockApi.post).mockResolvedValue({ status: 'rejected' });

      const result = await approvals.postDecision('apr-001', {
        decision: 'reject',
        comment: 'Too risky',
      });
      
      expect(mockApi.post).toHaveBeenCalledWith('/approvals/apr-001/decision', {
        decision: 'reject',
        comment: 'Too risky',
      });
      expect(result).toEqual({ status: 'rejected' });
    });

    it('posts decision without comment', async () => {
      vi.mocked(mockApi.post).mockResolvedValue({ status: 'approved' });

      await approvals.postDecision('apr-001', { decision: 'approve' });
      
      expect(mockApi.post).toHaveBeenCalledWith('/approvals/apr-001/decision', {
        decision: 'approve',
      });
    });
  });
});
