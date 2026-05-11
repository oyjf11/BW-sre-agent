import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { RcaPage } from './RcaPage';
import * as runsModule from '../services/runs';
import { renderWithProviders } from '../test/render';

vi.mock('../services/runs', () => ({
  runs: {
    getRunRca: vi.fn(),
  },
}));

describe('RcaPage', () => {
  const mockRca = {
    run_id: 'run-123',
    report_markdown: '# Root Cause Analysis\n\n## Root Cause\nDatabase connection pool exhausted',
    root_cause: 'Database connection pool exhausted',
    resolution: 'Increased pool size',
    prevention_items: ['Add monitoring', 'Set alerts'],
    confirmed_by_human: false,
  };

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders loading state', () => {
    vi.mocked(runsModule.runs.getRunRca).mockImplementation(
      () => new Promise(() => {})
    );

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123/rca']}>
        <Routes>
          <Route path="/runs/:id/rca" element={<RcaPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders RCA report', async () => {
    vi.mocked(runsModule.runs.getRunRca).mockResolvedValue(mockRca as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123/rca']}>
        <Routes>
          <Route path="/runs/:id/rca" element={<RcaPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Root Cause Analysis')).toBeInTheDocument();
    });

    expect(screen.getByText('Database connection pool exhausted')).toBeInTheDocument();
    expect(screen.getByText('Increased pool size')).toBeInTheDocument();
  });

  it('renders error state', async () => {
    vi.mocked(runsModule.runs.getRunRca).mockRejectedValue(new Error('Not found'));

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123/rca']}>
        <Routes>
          <Route path="/runs/:id/rca" element={<RcaPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Not found')).toBeInTheDocument();
    });
  });

  it('renders empty state when RCA not available', async () => {
    vi.mocked(runsModule.runs.getRunRca).mockResolvedValue(null as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123/rca']}>
        <Routes>
          <Route path="/runs/:id/rca" element={<RcaPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Root cause analysis pending')).toBeInTheDocument();
    });
  });

  it('has download button', async () => {
    vi.mocked(runsModule.runs.getRunRca).mockResolvedValue(mockRca as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123/rca']}>
        <Routes>
          <Route path="/runs/:id/rca" element={<RcaPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /export markdown/i })).toBeInTheDocument();
    });
  });
});
