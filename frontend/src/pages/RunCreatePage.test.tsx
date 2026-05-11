import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { RunCreatePage } from './RunCreatePage';
import * as runsModule from '../services/runs';
import { renderWithProviders } from '../test/render';

vi.mock('../services/runs', () => ({
  runs: {
    createRun: vi.fn(),
  },
}));

describe('RunCreatePage', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders form fields', () => {
    renderWithProviders(
      <BrowserRouter>
        <RunCreatePage />
      </BrowserRouter>,
    );

    expect(screen.getByRole('heading', { name: 'Create Incident Run' })).toBeInTheDocument();
    expect(screen.getByPlaceholderText('INC-001')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Service degraded')).toBeInTheDocument();
  });

  it('shows validation error when neither title nor ticket_id is provided', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(
      <BrowserRouter>
        <RunCreatePage />
      </BrowserRouter>,
    );

    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    expect(runsModule.runs.createRun).not.toHaveBeenCalled();
  });

  it('calls createRun with form data', async () => {
    const user = userEvent.setup();
    vi.mocked(runsModule.runs.createRun).mockResolvedValue({
      run_id: 'run-123',
      thread_id: 'thread-456',
      status: 'NEW',
      created_at: '2024-01-15T10:00:00Z',
    });

    renderWithProviders(
      <BrowserRouter>
        <RunCreatePage />
      </BrowserRouter>,
    );

    await user.type(screen.getByPlaceholderText('Service degraded'), 'API Gateway down');
    await user.type(screen.getByPlaceholderText('api-gateway'), 'api-gateway');
    
    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(runsModule.runs.createRun).toHaveBeenCalled();
    });
  });

  it('disables button while loading', async () => {
    const user = userEvent.setup();
    vi.mocked(runsModule.runs.createRun).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ run_id: 'run-123', thread_id: 't', status: 'NEW', created_at: '' }), 100))
    );

    renderWithProviders(
      <BrowserRouter>
        <RunCreatePage />
      </BrowserRouter>,
    );

    const submitButton = screen.getByRole('button', { name: /create/i });
    
    await user.type(screen.getByPlaceholderText('Service degraded'), 'test');
    await user.type(screen.getByPlaceholderText('api-gateway'), 'api-gateway');
    await user.click(submitButton);

    await waitFor(() => expect(screen.getByRole('button', { name: /creating/i })).toBeDisabled());
  });
});
