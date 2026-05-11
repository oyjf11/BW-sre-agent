import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { RunEvent } from '../types';
import { EventTimeline } from './EventTimeline';

describe('EventTimeline', () => {
  const mockEvents: RunEvent[] = [
    {
      event_id: 'ev-1',
      run_id: 'run-123',
      level: 'INFO',
      type: 'node_completed',
      node_name: 'triage',
      message: 'Triage completed',
      timestamp: '2024-01-15T10:00:00Z',
    },
    {
      event_id: 'ev-2',
      run_id: 'run-123',
      level: 'WARNING',
      type: 'evidence_collected',
      message: 'Logs collected',
      timestamp: '2024-01-15T10:05:00Z',
    },
    {
      event_id: 'ev-3',
      run_id: 'run-123',
      level: 'ERROR',
      type: 'execution_failed',
      message: 'Failed to restart service',
      timestamp: '2024-01-15T10:10:00Z',
    },
  ];

  it('renders all events by default', () => {
    render(<EventTimeline events={mockEvents} />);
    expect(screen.getByText('Triage completed')).toBeInTheDocument();
    expect(screen.getByText('Logs collected')).toBeInTheDocument();
    expect(screen.getByText('Failed to restart service')).toBeInTheDocument();
  });

  it('shows no events message when empty', () => {
    render(<EventTimeline events={[]} />);
    expect(screen.getByText('No events')).toBeInTheDocument();
  });

  it('filters events by level', async () => {
    const user = userEvent.setup();
    render(<EventTimeline events={mockEvents} />);
    
    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'ERROR');
    
    expect(screen.queryByText('Triage completed')).not.toBeInTheDocument();
    expect(screen.getByText('Failed to restart service')).toBeInTheDocument();
  });

  it('shows level badges', () => {
    render(<EventTimeline events={mockEvents} />);
    
    const infoBadge = screen.getAllByText('INFO')[0];
    const warningBadge = screen.getAllByText('WARNING')[0];
    const errorBadge = screen.getAllByText('ERROR')[0];
    
    expect(infoBadge).toBeInTheDocument();
    expect(warningBadge).toBeInTheDocument();
    expect(errorBadge).toBeInTheDocument();
  });

  it('shows node name when present', () => {
    render(<EventTimeline events={mockEvents} />);
    expect(screen.getByText('@triage')).toBeInTheDocument();
  });

  it('has auto-scroll checkbox', () => {
    render(<EventTimeline events={mockEvents} />);
    expect(screen.getByLabelText('Auto-scroll')).toBeInTheDocument();
  });

  it('shows reconnect button when onReconnect is provided', () => {
    render(<EventTimeline events={mockEvents} onReconnect={() => {}} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
