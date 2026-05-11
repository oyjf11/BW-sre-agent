import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ApprovalsPage } from './ApprovalsPage';
import * as approvalsModule from '../services/approvals';
import { renderWithProviders } from '../test/render';

vi.mock('../services/approvals', () => ({
  approvals: {
    listPendingApprovals: vi.fn(),
  },
}));

describe('ApprovalsPage', () => {
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
    {
      approval_id: 'apr-002',
      run_id: 'run-456',
      action: {
        action_type: 'scale',
        service: 'user-service',
        env: 'staging',
        params: {},
        risk_level: 'LOW',
        requires_approval: true,
      },
      risk_level: 'LOW',
      status: 'pending',
      created_at: '2024-01-15T11:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders loading state', () => {
    vi.mocked(approvalsModule.approvals.listPendingApprovals).mockImplementation(
      () => new Promise(() => {})
    );

    renderWithProviders(
      <BrowserRouter>
        <ApprovalsPage />
      </BrowserRouter>,
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders approvals list', async () => {
    vi.mocked(approvalsModule.approvals.listPendingApprovals).mockResolvedValue(mockApprovals);

    renderWithProviders(
      <BrowserRouter>
        <ApprovalsPage />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Pending Approvals')).toBeInTheDocument();
    });

    expect(screen.getByText('apr-001...')).toBeInTheDocument();
    expect(screen.getByText('apr-002...')).toBeInTheDocument();
  });

  it('renders empty state when no approvals', async () => {
    vi.mocked(approvalsModule.approvals.listPendingApprovals).mockResolvedValue([]);

    renderWithProviders(
      <BrowserRouter>
        <ApprovalsPage />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('No data')).toBeInTheDocument();
    });
  });

  it('renders error state', async () => {
    vi.mocked(approvalsModule.approvals.listPendingApprovals).mockRejectedValue(new Error('Network error'));

    renderWithProviders(
      <BrowserRouter>
        <ApprovalsPage />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('filters by service', async () => {
    vi.mocked(approvalsModule.approvals.listPendingApprovals).mockResolvedValue(mockApprovals);

    renderWithProviders(
      <BrowserRouter>
        <ApprovalsPage />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('apr-001...')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search by service...');
    await userEvent.setup().type(searchInput, 'api');

    expect(screen.getByText('apr-001...')).toBeInTheDocument();
    expect(screen.queryByText('apr-002...')).not.toBeInTheDocument();
  });
});
