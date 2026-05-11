import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ApprovalDetailPage } from './ApprovalDetailPage';
import * as approvalsModule from '../services/approvals';
import { renderWithProviders } from '../test/render';

vi.mock('../services/approvals', () => ({
  approvals: {
    getApproval: vi.fn(),
    postDecision: vi.fn(),
  },
}));

describe('ApprovalDetailPage', () => {
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
    reason: 'High memory usage detected',
    evidence_refs: ['ev-001'],
    expected_impact: 'Minimal downtime',
  };

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders loading state', () => {
    vi.mocked(approvalsModule.approvals.getApproval).mockImplementation(
      () => new Promise(() => {})
    );

    renderWithProviders(
      <MemoryRouter initialEntries={['/approvals/apr-001']}>
        <Routes>
          <Route path="/approvals/:id" element={<ApprovalDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders approval details', async () => {
    vi.mocked(approvalsModule.approvals.getApproval).mockResolvedValue(mockApproval as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/approvals/apr-001']}>
        <Routes>
          <Route path="/approvals/:id" element={<ApprovalDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Approval Request')).toBeInTheDocument();
    });

    expect(screen.getByText('High memory usage detected')).toBeInTheDocument();
  });

  it('has approve and reject buttons', async () => {
    vi.mocked(approvalsModule.approvals.getApproval).mockResolvedValue(mockApproval as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/approvals/apr-001']}>
        <Routes>
          <Route path="/approvals/:id" element={<ApprovalDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /approve/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reject/i })).toBeInTheDocument();
    });
  });

  it('calls postDecision when approve is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(approvalsModule.approvals.getApproval).mockResolvedValue(mockApproval as any);
    vi.mocked(approvalsModule.approvals.postDecision).mockResolvedValue({ status: 'approved' });

    renderWithProviders(
      <MemoryRouter initialEntries={['/approvals/apr-001']}>
        <Routes>
          <Route path="/approvals/:id" element={<ApprovalDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /approve/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /approve/i }));

    expect(approvalsModule.approvals.postDecision).toHaveBeenCalledWith('apr-001', { decision: 'approved' });
  });
});
