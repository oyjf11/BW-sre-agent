import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { RunDetailPage } from './RunDetailPage';
import * as runsModule from '../services/runs';
import { renderWithProviders } from '../test/render';

const controllerMethods = vi.hoisted(() => ({
  seedEvents: vi.fn(),
  observeRun: vi.fn(),
  start: vi.fn(),
  dispose: vi.fn(),
}));

let capturedOptions: any = null;

vi.mock('../services/runDetailSync', () => ({
  createRunDetailSyncController: vi.fn((options) => {
    capturedOptions = options;
    controllerMethods.seedEvents = vi.fn();
    controllerMethods.observeRun = vi.fn((run) => { capturedOptions?.onRun(run); });
    controllerMethods.start = vi.fn(() => { capturedOptions?.onConnectionState('connecting'); });
    controllerMethods.dispose = vi.fn();
    return controllerMethods;
  }),
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

function renderPage() {
  return renderWithProviders(
    <MemoryRouter initialEntries={['/runs/run-123']}>
      <Routes>
        <Route path="/runs/:id" element={<RunDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RunDetailPage', () => {
  const mockRun = {
    ticket_id: 'INC-1',
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
    capturedOptions = null;
    vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
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

  it('shows a skeleton during initial loading', () => {
    vi.mocked(runsModule.runs.getRun).mockImplementation(() => new Promise(() => {}));
    vi.mocked(runsModule.runs.getRunEvents).mockImplementation(() => new Promise(() => {}));

    renderPage();

    expect(screen.getByTestId('run-detail-skeleton')).toBeInTheDocument();
  });

  it('renders run detail after loading', async () => {
    renderPage();
    await screen.findByText('api-gateway');
    expect(screen.getByText('api-gateway')).toBeInTheDocument();
  });

  it('shows and clears the fallback notice from controller state', async () => {
    renderPage();
    await screen.findByText('api-gateway');

    act(() => capturedOptions?.onConnectionState('polling'));
    expect(screen.getByText(/Switched to automatic refresh/)).toBeInTheDocument();

    act(() => capturedOptions?.onConnectionState('live'));
    expect(screen.queryByText(/Switched to automatic refresh/)).not.toBeInTheDocument();
  });

  it('keeps existing evidence visible while artifacts refresh', async () => {
    vi.mocked(runsModule.runs.getRunEvidence).mockResolvedValue([
      {
        evidence_id: 'evd-1',
        tool_name: 'prometheus',
        category: 'metrics',
        source_ref: 'prometheus://5xx',
        summary: '5xx elevated',
      },
    ] as any);
    renderPage();
    await screen.findByText('api-gateway');
    await userEvent.setup().click(screen.getByRole('button', { name: 'Evidence' }));

    let resolveRefresh!: () => void;
    vi.mocked(runsModule.runs.getRunEvidence).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveRefresh = () => resolve([]);
        }),
    );
    act(() => void capturedOptions?.refreshArtifacts());

    expect(screen.getByText('5xx elevated')).toBeInTheDocument();
    expect(screen.getByText('Refreshing...')).toBeInTheDocument();
    resolveRefresh();
  });

  it('shows local waiting text while diagnosis has not been generated', async () => {
    vi.mocked(runsModule.runs.getRunDiagnosis).mockRejectedValue(
      Object.assign(new Error('No checkpoint found'), { status: 404 }),
    );
    renderPage();
    await screen.findByText('api-gateway');

    await userEvent.setup().click(screen.getByRole('button', { name: 'Diagnosis' }));

    expect(screen.getByText('Generating diagnosis...')).toBeInTheDocument();
  });

  it('ignores an older artifact response that resolves after a newer refresh', async () => {
    vi.mocked(runsModule.runs.getRunEvidence).mockResolvedValueOnce([] as any);
    renderPage();
    await screen.findByText('api-gateway');

    let resolveOlder!: (value: any[]) => void;
    let resolveNewer!: (value: any[]) => void;
    vi.mocked(runsModule.runs.getRunEvidence)
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveOlder = resolve;
          }),
      )
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveNewer = resolve;
          }),
      );
    const older = capturedOptions?.refreshArtifacts();
    const newer = capturedOptions?.refreshArtifacts();
    resolveNewer([
      {
        evidence_id: 'new',
        tool_name: 'logs',
        category: 'logs',
        source_ref: 'new',
        summary: 'new evidence',
      },
    ]);
    await newer;
    resolveOlder([
      {
        evidence_id: 'old',
        tool_name: 'logs',
        category: 'logs',
        source_ref: 'old',
        summary: 'old evidence',
      },
    ]);
    await older;

    await userEvent.setup().click(screen.getByRole('button', { name: 'Evidence' }));
    expect(screen.getByText('new evidence')).toBeInTheDocument();
    expect(screen.queryByText('old evidence')).not.toBeInTheDocument();
  });

  it('retries the initial request after a page load failure', async () => {
    vi.mocked(runsModule.runs.getRun)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce(mockRun as any);
    vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
    renderPage();
    await screen.findByText(/Network error/);

    await userEvent.setup().click(screen.getByRole('button', { name: 'Retry' }));

    expect(await screen.findByText('api-gateway')).toBeInTheDocument();
  });

  it('disposes the page-scoped controller on unmount', async () => {
    const view = renderPage();
    await screen.findByText('api-gateway');

    view.unmount();

    expect(controllerMethods.dispose).toHaveBeenCalledOnce();
  });
});
