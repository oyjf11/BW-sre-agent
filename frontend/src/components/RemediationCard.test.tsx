import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import type { RemediationPlan } from '../types';
import { RemediationCard } from './RemediationCard';

describe('RemediationCard', () => {
  const mockPlan: RemediationPlan = {
    summary: 'Restart API Gateway pods',
    actions: [
      {
        action_type: 'restart',
        service: 'api-gateway',
        env: 'prod',
        params: { pods: ['api-gateway-0'] },
        risk_level: 'MEDIUM',
        requires_approval: true,
      },
    ],
    expected_outcome: 'Reduced memory usage',
    rollback_plan: 'Scale back to 3 replicas',
  };

  it('renders no plan message when plan is undefined', () => {
    render(<RemediationCard />);
    expect(screen.getByText('No remediation plan yet')).toBeInTheDocument();
  });

  it('renders plan summary', () => {
    render(<RemediationCard plan={mockPlan} />);
    expect(screen.getByText('Restart API Gateway pods')).toBeInTheDocument();
  });

  it('renders expected outcome', () => {
    render(<RemediationCard plan={mockPlan} />);
    expect(screen.getByText('Reduced memory usage')).toBeInTheDocument();
  });

  it('renders actions', () => {
    render(<RemediationCard plan={mockPlan} />);
    expect(screen.getByText('restart')).toBeInTheDocument();
    expect(screen.getByText('api-gateway')).toBeInTheDocument();
    expect(screen.getByText('prod')).toBeInTheDocument();
  });

  it('renders risk level badge', () => {
    render(<RemediationCard plan={mockPlan} />);
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
  });

  it('renders rollback plan', () => {
    render(<RemediationCard plan={mockPlan} />);
    expect(screen.getByText(/Rollback:/)).toBeInTheDocument();
    expect(screen.getByText('Scale back to 3 replicas')).toBeInTheDocument();
  });

  it('renders waiting for approval message when status is WAITING_HUMAN', () => {
    render(<RemediationCard plan={mockPlan} approvalStatus="WAITING_HUMAN" />);
    expect(screen.getByText('Waiting for human approval')).toBeInTheDocument();
  });

  it('does not render waiting message when status is not WAITING_HUMAN', () => {
    render(<RemediationCard plan={mockPlan} approvalStatus="approved" />);
    expect(screen.queryByText('Waiting for human approval')).not.toBeInTheDocument();
  });
});
