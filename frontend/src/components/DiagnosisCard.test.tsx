import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { RootCauseCandidate } from '../types';
import { DiagnosisCard } from './DiagnosisCard';
import { I18nProvider } from '../i18n';

function renderWithI18n(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

describe('DiagnosisCard', () => {
  const mockCandidate: RootCauseCandidate = {
    candidate_id: 'rc-001',
    hypothesis: 'Database connection pool exhausted',
    confidence: 0.85,
    supporting_evidence_ids: ['ev-001', 'ev-002'],
    contradicting_evidence_ids: [],
    next_checks: ['check_db_connections', 'check_pool_size'],
  };

  it('renders no candidates message when empty', () => {
    renderWithI18n(<DiagnosisCard candidates={[]} />);
    expect(screen.getByText('No root cause candidates yet')).toBeInTheDocument();
  });

  it('renders candidate hypothesis', () => {
    renderWithI18n(<DiagnosisCard candidates={[mockCandidate]} />);
    expect(screen.getByText('Database connection pool exhausted')).toBeInTheDocument();
  });

  it('renders confidence percentage', () => {
    renderWithI18n(<DiagnosisCard candidates={[mockCandidate]} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('renders supporting evidence IDs', () => {
    renderWithI18n(<DiagnosisCard candidates={[mockCandidate]} />);
    expect(screen.getByText('Supporting evidence:')).toBeInTheDocument();
    expect(screen.getByText('ev-001')).toBeInTheDocument();
    expect(screen.getByText('ev-002')).toBeInTheDocument();
  });

  it('renders next checks', () => {
    renderWithI18n(<DiagnosisCard candidates={[mockCandidate]} />);
    expect(screen.getByText('Next checks: check_db_connections, check_pool_size')).toBeInTheDocument();
  });

  it('calls onEvidenceClick when evidence button is clicked', async () => {
    const user = userEvent.setup();
    const onEvidenceClick = vi.fn();
    
    renderWithI18n(<DiagnosisCard candidates={[mockCandidate]} onEvidenceClick={onEvidenceClick} />);
    
    await user.click(screen.getByText('ev-001'));
    expect(onEvidenceClick).toHaveBeenCalledWith('ev-001');
  });

  it('renders multiple candidates', () => {
    const candidates: RootCauseCandidate[] = [
      mockCandidate,
      { ...mockCandidate, candidate_id: 'rc-002', hypothesis: 'Memory leak', confidence: 0.6 },
    ];
    
    renderWithI18n(<DiagnosisCard candidates={candidates} />);
    
    expect(screen.getByText('Database connection pool exhausted')).toBeInTheDocument();
    expect(screen.getByText('Memory leak')).toBeInTheDocument();
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#2')).toBeInTheDocument();
  });
});
