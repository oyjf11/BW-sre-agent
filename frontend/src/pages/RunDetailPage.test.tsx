import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { RunDetailPage } from './RunDetailPage';
import * as runsModule from '../services/runs';
import { renderWithProviders } from '../test/render';

vi.mock('../services/sse', () => ({
  sseClient: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
  },
}));

vi.mock('../services/runs', () => ({
  runs: {
    getRun: vi.fn(),
    getRunEvents: vi.fn(),
    getRunEvidence: vi.fn(),
    getRunDiagnosis: vi.fn(),
    getRunRemediation: vi.fn(),
    getRunTrace: vi.fn(),
  },
}));

describe('RunDetailPage', () => {
  const mockRun = {
      run_id: 'run-123',
      thread_id: 'thread-456',
      status: 'TRIAGED',
      severity: 'P1',
      service: 'api-gateway',
      env: 'prod',
      created_at: '2024-01-15T10:00:00Z',
    };

  const mockEvents = [
    {
      event_id: 'ev-1',
      run_id: 'run-123',
      level: 'INFO',
      type: 'started',
      message: 'Run started',
      timestamp: '2024-01-15T10:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(runsModule.runs.getRunEvidence).mockResolvedValue([]);
    vi.mocked(runsModule.runs.getRunDiagnosis).mockResolvedValue({
      run_id: 'run-123',
      root_cause_candidates: [],
    });
    vi.mocked(runsModule.runs.getRunRemediation).mockResolvedValue({
      run_id: 'run-123',
      remediation_plan: undefined,
    });
    vi.mocked(runsModule.runs.getRunTrace).mockResolvedValue({
      run_id: 'run-123',
      provider: 'local',
      trace_url: '/incidents/runs/run-123/trace',
      spans: [],
    } as any);
  });

  it('renders loading state', () => {
    vi.mocked(runsModule.runs.getRun).mockImplementation(
      () => new Promise(() => {})
    );

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders run details', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('api-gateway')).toBeInTheDocument();
    });

    expect(screen.getByText(/prod/)).toBeInTheDocument();
    expect(screen.getByText(/P1/)).toBeInTheDocument();
    expect(screen.getAllByText('Triaged').length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: 'Events' })).toBeInTheDocument();
  });

  it('switches tabs and renders evidence and diagnosis content', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
    vi.mocked(runsModule.runs.getRunEvidence).mockResolvedValue([
      {
        evidence_id: 'evd-1',
        tool_name: 'prometheus',
        category: 'metrics',
        source_ref: 'prometheus://5xx',
        summary: '5xx elevated',
      },
    ] as any);
    vi.mocked(runsModule.runs.getRunDiagnosis).mockResolvedValue({
      run_id: 'run-123',
      root_cause_candidates: [
        {
          candidate_id: 'cand-1',
          hypothesis: 'A recent deploy caused the issue',
          confidence: 0.8,
          supporting_evidence_ids: [],
          contradicting_evidence_ids: [],
          next_checks: [],
        },
      ],
    });

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText('Run started')).toBeInTheDocument());

    await userEvent.setup().click(screen.getByRole('button', { name: 'Evidence' }));
    expect(screen.getByText('5xx elevated')).toBeInTheDocument();

    await userEvent.setup().click(screen.getByRole('button', { name: 'Diagnosis' }));
    expect(screen.getByText('A recent deploy caused the issue')).toBeInTheDocument();
  });

  it('renders error state', async () => {
    vi.mocked(runsModule.runs.getRun).mockRejectedValue(new Error('Not found'));
    vi.mocked(runsModule.runs.getRunEvents).mockRejectedValue(new Error('Not found'));

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Error: Not found')).toBeInTheDocument();
    });
  });

  it('shows approval card when run is waiting for human input', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue({
      ...mockRun,
      status: 'WAITING_HUMAN',
    } as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText('Human approval required before execution')).toBeInTheDocument());
    expect(screen.getByRole('link', { name: 'Review approvals' })).toHaveAttribute('href', '/approvals');
  });

  it('renders trace link in quick actions', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText('api-gateway')).toBeInTheDocument());
    expect(screen.getByRole('link', { name: 'View Trace' })).toHaveAttribute(
      'href',
      '/incidents/runs/run-123/trace',
    );
  });

  it('uses external trace URL for the View Trace action when present', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
    vi.mocked(runsModule.runs.getRunTrace).mockResolvedValue({
      run_id: 'run-123',
      provider: 'langfuse',
      trace_url: '/incidents/runs/run-123/trace',
      external_trace_id: 'trace-run-123',
      external_root_span_id: 'span-root',
      external_trace_url: 'https://langfuse.example/project/opspilot/traces/trace-run-123',
      spans: [],
    } as any);

    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-123']}>
        <Routes>
          <Route path="/runs/:id" element={<RunDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('api-gateway')).toBeInTheDocument();
    });

    expect(screen.getByRole('link', { name: 'View Trace' })).toHaveAttribute(
      'href',
      'https://langfuse.example/project/opspilot/traces/trace-run-123',
    );
  });
});
