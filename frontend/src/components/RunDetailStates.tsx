import type { ReactNode } from 'react';
import { useI18n } from '../i18n';

function Spinner() {
  return (
    <span
      aria-hidden="true"
      className="inline-block h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-current border-r-transparent"
    />
  );
}

export function RunDetailSkeleton() {
  return (
    <div
      data-testid="run-detail-skeleton"
      className="mx-auto max-w-6xl animate-pulse space-y-6"
    >
      <div className="flex flex-wrap justify-between gap-4">
        <div className="space-y-2">
          <div className="h-6 w-52 rounded bg-surface-tertiary" />
          <div className="h-4 w-72 max-w-full rounded bg-surface-tertiary" />
        </div>
        <div className="h-9 w-28 rounded-full bg-surface-tertiary" />
      </div>
      <div className="card h-20 p-5" />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card min-h-80 p-4 sm:p-6 lg:col-span-2" />
        <div className="space-y-6">
          <div className="card h-36 p-4 sm:p-6" />
          <div className="card h-32 p-4 sm:p-6" />
        </div>
      </div>
    </div>
  );
}

export function RealtimeFallbackNotice() {
  const { t } = useI18n();
  return (
    <div role="status" className="status-warning flex flex-wrap items-center gap-2 rounded-lg p-3 text-sm">
      <Spinner />
      <span className="min-w-0 break-words">{t('run.realtimeFallback')}</span>
    </div>
  );
}

interface ArtifactPanelStateProps {
  children: ReactNode;
  empty: boolean;
  pending?: boolean;
  refreshing?: boolean;
  error?: string;
  pendingLabel: string;
  updatedAt?: string;
  onRetry?: () => void;
}

export function ArtifactPanelState({
  children,
  empty,
  pending = false,
  refreshing = false,
  error,
  pendingLabel,
  updatedAt,
  onRetry,
}: ArtifactPanelStateProps) {
  const { t } = useI18n();
  if (empty && pending) {
    return (
      <div className="flex flex-wrap items-center gap-2 py-8 text-sm text-content-muted">
        <Spinner />
        <span>{pendingLabel}</span>
        {updatedAt && <span>{t('run.updatedAt').replace('{{time}}', updatedAt)}</span>}
      </div>
    );
  }
  if (empty && error) {
    return (
      <div className="space-y-3 py-6 text-sm text-status-critical">
        <p>{error}</p>
        {onRetry && (
          <button className="btn btn-secondary" onClick={onRetry}>
            {t('run.retry')}
          </button>
        )}
      </div>
    );
  }
  return (
    <div className="space-y-3">
      {(refreshing || error || updatedAt) && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-content-muted">
          {refreshing && (
            <>
              <Spinner />
              <span>{t('run.refreshing')}</span>
            </>
          )}
          {error && <span className="text-status-critical">{error}</span>}
          {updatedAt && <span>{t('run.updatedAt').replace('{{time}}', updatedAt)}</span>}
          {error && onRetry && (
            <button className="btn btn-secondary px-2 py-1 text-xs" onClick={onRetry}>
              {t('run.retry')}
            </button>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
