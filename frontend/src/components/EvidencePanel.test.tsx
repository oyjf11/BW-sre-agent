import { describe, it, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { EvidenceItem } from '../types';
import { EvidencePanel } from './EvidencePanel';
import { I18nProvider } from '../i18n';

function renderWithI18n(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

describe('EvidencePanel', () => {
  const mockEvidence: EvidenceItem[] = [
    {
      evidence_id: 'ev-001',
      tool_name: 'prometheus',
      category: 'logs',
      source_ref: '/var/log/app.log',
      summary: 'High error rate detected',
      confidence: 0.9,
      freshness_score: 0.8,
      completeness_score: 0.85,
    },
    {
      evidence_id: 'ev-002',
      tool_name: 'kubectl',
      category: 'deployments',
      source_ref: 'deployment/api-gateway',
      summary: 'Recent deployment found',
      confidence: 0.7,
      freshness_score: 0.9,
      completeness_score: 0.6,
    },
  ];

  it('renders no evidence message when empty', () => {
    renderWithI18n(<EvidencePanel evidence={[]} />);
    expect(screen.getByText('No evidence collected yet')).toBeInTheDocument();
  });

  it('renders evidence items', () => {
    renderWithI18n(<EvidencePanel evidence={mockEvidence} />);
    expect(screen.getByText('High error rate detected')).toBeInTheDocument();
    expect(screen.getByText('Recent deployment found')).toBeInTheDocument();
  });

  it('groups evidence by category', () => {
    renderWithI18n(<EvidencePanel evidence={mockEvidence} />);
    expect(screen.getByText('logs')).toBeInTheDocument();
    expect(screen.getByText('deployments')).toBeInTheDocument();
  });

  it('shows category count', () => {
    renderWithI18n(<EvidencePanel evidence={mockEvidence} />);
    expect(screen.getAllByText('(1)')).toHaveLength(2);
  });

  it('expands evidence on click', async () => {
    const user = userEvent.setup();
    renderWithI18n(<EvidencePanel evidence={mockEvidence} />);
    await user.click(screen.getByRole('button', { name: /High error rate detected/i }));
    
    expect(screen.getByText(/Confidence:/)).toBeInTheDocument();
  });

  it('shows evidence scores when expanded', async () => {
    const user = userEvent.setup();
    renderWithI18n(<EvidencePanel evidence={mockEvidence} />);
    await user.click(screen.getByRole('button', { name: /High error rate detected/i }));

    const scoreRow = screen.getByText(/Confidence:/).parentElement;
    expect(scoreRow).not.toBeNull();
    expect(within(scoreRow!).getByText(/Freshness:/)).toBeInTheDocument();
  });
});
