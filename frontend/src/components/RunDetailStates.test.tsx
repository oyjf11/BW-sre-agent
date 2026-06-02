import { fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '../test/render';
import {
  ArtifactPanelState,
  RealtimeFallbackNotice,
  RunDetailSkeleton,
} from './RunDetailStates';

describe('RunDetailStates', () => {
  beforeEach(() => localStorage.setItem('opspilot-locale', 'en'));

  it('renders the detail skeleton without an overlay', () => {
    renderWithProviders(<RunDetailSkeleton />);
    expect(screen.getByTestId('run-detail-skeleton')).toBeInTheDocument();
  });

  it('renders the fallback notice while polling', () => {
    renderWithProviders(<RealtimeFallbackNotice />);
    expect(screen.getByText(/Switched to automatic refresh/)).toBeInTheDocument();
  });

  it('shows local pending text when an artifact has no content yet', () => {
    renderWithProviders(
      <ArtifactPanelState empty pending pendingLabel="Collecting evidence">
        <p>content</p>
      </ArtifactPanelState>,
    );
    expect(screen.getByText('Collecting evidence')).toBeInTheDocument();
    expect(screen.queryByText('content')).not.toBeInTheDocument();
  });

  it('preserves content and exposes retry after a refresh error', () => {
    const retry = vi.fn();
    renderWithProviders(
      <ArtifactPanelState empty={false} error="Refresh failed" onRetry={retry}>
        <p>existing content</p>
      </ArtifactPanelState>,
    );
    expect(screen.getByText('existing content')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    expect(retry).toHaveBeenCalledOnce();
  });
});
