import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EmptyState } from './EmptyState';

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No items found" />);
    expect(screen.getByText('No items found')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<EmptyState title="No items" description="There are no items to display" />);
    expect(screen.getByText('There are no items to display')).toBeInTheDocument();
  });

  it('does not render description when not provided', () => {
    const { container } = render(<EmptyState title="No items" />);
    const description = container.querySelector('p');
    expect(description).not.toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    render(
      <EmptyState
        title="No data"
        action={<button>Create New</button>}
      />
    );
    expect(screen.getByRole('button', { name: 'Create New' })).toBeInTheDocument();
  });

  it('does not render action when not provided', () => {
    render(<EmptyState title="No items" />);
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('calls action onClick when clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    
    render(
      <EmptyState
        title="No items"
        action={<button onClick={onClick}>Add Item</button>}
      />
    );
    
    await user.click(screen.getByRole('button', { name: 'Add Item' }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
