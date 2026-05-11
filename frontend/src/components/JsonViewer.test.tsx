import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { JsonViewer } from './JsonViewer';

describe('JsonViewer', () => {
  it('renders object data', () => {
    const data = { key: 'value', count: 42 };
    render(<JsonViewer data={data} defaultExpanded={true} />);
    
    expect(screen.getByText(/"key"/)).toBeInTheDocument();
    expect(screen.getByText(/"value"/)).toBeInTheDocument();
  });

  it('renders array data', () => {
    const data = [1, 2, 3];
    render(<JsonViewer data={data} defaultExpanded={true} />);
    
    expect(screen.getByText('[3]')).toBeInTheDocument();
  });

  it('renders null value', () => {
    const data = { value: null };
    render(<JsonViewer data={data} defaultExpanded={true} />);
    
    expect(screen.getByText('null')).toBeInTheDocument();
  });

  it('renders empty object', () => {
    render(<JsonViewer data={{}} defaultExpanded={true} />);
    expect(screen.getByText('{}')).toBeInTheDocument();
  });

  it('renders empty array', () => {
    render(<JsonViewer data={[]} defaultExpanded={true} />);
    expect(screen.getByText('[]')).toBeInTheDocument();
  });

  it('toggles expansion', async () => {
    const user = userEvent.setup();
    const data = { key: 'value' };
    
    render(<JsonViewer data={data} defaultExpanded={false} />);
    
    const toggleButton = screen.getByText('Toggle JSON');
    await user.click(toggleButton);
    
    expect(screen.getByText(/"key"/)).toBeInTheDocument();
  });

  it('has copy and download buttons', () => {
    const data = { key: 'value' };
    render(<JsonViewer data={data} defaultExpanded={true} />);
    
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBe(4);
  });
});
