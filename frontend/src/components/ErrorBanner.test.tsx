import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBanner } from './ErrorBanner';

describe('ErrorBanner', () => {
  it('renders error message', () => {
    render(<ErrorBanner message="Something went wrong" />);
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('renders with correct styling', () => {
    const { container } = render(<ErrorBanner message="Error message" />);
    const banner = container.firstChild;
    expect(banner).toHaveClass('rounded-lg', 'status-critical');
  });

  it('does not render dismiss button when onDismiss is not provided', () => {
    render(<ErrorBanner message="Error message" />);
    const buttons = screen.queryByRole('button');
    expect(buttons).not.toBeInTheDocument();
  });

  it('renders dismiss button when onDismiss is provided', () => {
    render(<ErrorBanner message="Error message" onDismiss={() => {}} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onDismiss when dismiss button is clicked', async () => {
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    
    render(<ErrorBanner message="Error message" onDismiss={onDismiss} />);
    await user.click(screen.getByRole('button'));
    
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});
