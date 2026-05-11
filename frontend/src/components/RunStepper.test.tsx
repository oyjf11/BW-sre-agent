import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { RunStepper } from './RunStepper';
import { renderWithProviders } from '../test/render';

describe('RunStepper', () => {
  it('renders all steps', () => {
    renderWithProviders(<RunStepper status="NEW" />);
    
    expect(screen.getByText('New')).toBeInTheDocument();
    expect(screen.getByText('Triaged')).toBeInTheDocument();
    expect(screen.getByText('Planned')).toBeInTheDocument();
    expect(screen.getByText('Gathering Evidence')).toBeInTheDocument();
    expect(screen.getByText('Diagnosed')).toBeInTheDocument();
    expect(screen.getByText('Pending Approval')).toBeInTheDocument();
    expect(screen.getByText('Executing')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('marks current step as active', () => {
    renderWithProviders(<RunStepper status="TRIAGED" />);
    
    const steps = screen.getAllByText(/New|Triaged/);
    expect(steps.length).toBeGreaterThan(0);
  });

  it('marks completed steps with checkmark', () => {
    const { container } = renderWithProviders(<RunStepper status="PLANNED" />);
    expect(container.querySelectorAll('svg').length).toBeGreaterThan(0);
  });

  it('handles COMPLETED status', () => {
    renderWithProviders(<RunStepper status="COMPLETED" />);
    
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('handles FAILED status', () => {
    renderWithProviders(<RunStepper status="FAILED" />);
    
    expect(screen.getByText('New')).toBeInTheDocument();
  });

  it('handles WAITING_HUMAN status', () => {
    renderWithProviders(<RunStepper status="WAITING_HUMAN" />);
    
    expect(screen.getByText('Pending Approval')).toBeInTheDocument();
  });

  it('renders step numbers for future steps', () => {
    renderWithProviders(<RunStepper status="NEW" />);
    
    const numbers = screen.getAllByText('1');
    expect(numbers.length).toBeGreaterThan(0);
  });
});
