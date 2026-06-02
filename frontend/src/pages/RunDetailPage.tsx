import { useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { runs } from '../services/runs';
import { useI18n } from '../i18n';
import {
  createRunDetailSyncController,
  type SyncConnectionState,
} from '../services/runDetailSync';
import {
  ArtifactPanelState,
  RealtimeFallbackNotice,
  RunDetailSkeleton,
} from '../components/RunDetailStates';
import { RunStepper } from '../components/RunStepper';
import { EventTimeline } from '../components/EventTimeline';
import { EvidencePanel } from '../components/EvidencePanel';
import { DiagnosisCard } from '../components/DiagnosisCard';
import { RemediationCard } from '../components/RemediationCard';
import type {
  RunDetail,
  RunEvent,
  EvidenceItem,
  RootCauseCandidate,
  RemediationPlan,
  RunTrace,
} from '../types';

type RunTab = 'events' | 'evidence' | 'diagnosis' | 'remediation';

type ArtifactKey = 'evidence' | 'diagnosis' | 'remediation';
interface ArtifactMeta {
  pending: boolean;
  refreshing: boolean;
  error?: string;
  updatedAt?: string;
}
const EMPTY_ARTIFACT_META: Record<ArtifactKey, ArtifactMeta> = {
  evidence: { pending: true, refreshing: false },
  diagnosis: { pending: true, refreshing: false },
  remediation: { pending: true, refreshing: false },
};

function getStatusClass(status: string): string {
  switch (status) {
    case 'COMPLETED':
      return 'status-success';
    case 'FAILED':
      return 'status-critical';
    case 'WAITING_HUMAN':
    case 'NEEDS_HUMAN':
      return 'status-warning';
    case 'RUNNING':
    case 'PENDING':
      return 'status-info';
    default:
      return 'status-pending';
  }
}

function mergeEvents(current: RunEvent[], incoming: RunEvent[]): RunEvent[] {
  const byId = new Map(current.map((event) => [event.event_id, event]));
  for (const event of incoming) byId.set(event.event_id, event);
  return [...byId.values()].sort(
    (left, right) => Date.parse(left.timestamp) - Date.parse(right.timestamp),
  );
}

function isPendingArtifactError(reason: unknown): boolean {
  return (
    typeof reason === 'object' &&
    reason !== null &&
    'status' in reason &&
    (reason as { status: unknown }).status === 404
  );
}

export function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useI18n();
  const [run, setRun] = useState<RunDetail | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [diagnosis, setDiagnosis] = useState<RootCauseCandidate[]>([]);
  const [remediationPlan, setRemediationPlan] = useState<RemediationPlan | undefined>();
  const [runTrace, setRunTrace] = useState<RunTrace | null>(null);
  const [activeTab, setActiveTab] = useState<RunTab>('events');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<SyncConnectionState>('connecting');
  const [artifactMeta, setArtifactMeta] = useState(EMPTY_ARTIFACT_META);
  const [retryVersion, setRetryVersion] = useState(0);
  const retryArtifactsRef = useRef<() => Promise<void>>(async () => undefined);

  const traceHref = runTrace?.external_trace_url || runTrace?.trace_url;

  useEffect(() => {
    if (!id) return;
    let active = true;
    let artifactSequence = 0;
    setLoading(true);
    setError(null);
    setRun(null);
    setEvents([]);
    setEvidence([]);
    setDiagnosis([]);
    setRemediationPlan(undefined);
    setRunTrace(null);
    setConnectionState('connecting');
    setArtifactMeta(EMPTY_ARTIFACT_META);

    const updateMeta = (key: ArtifactKey, patch: Partial<ArtifactMeta>) => {
      if (!active) return;
      setArtifactMeta((current) => ({
        ...current,
        [key]: { ...current[key], ...patch },
      }));
    };

    const markFailure = (key: ArtifactKey, reason: unknown) => {
      if (isPendingArtifactError(reason)) {
        updateMeta(key, { pending: true, refreshing: false, error: undefined });
        return;
      }
      updateMeta(key, {
        pending: false,
        refreshing: false,
        error: reason instanceof Error ? reason.message : t('run.loadFailed'),
      });
    };

    const refreshArtifacts = async () => {
      const sequence = ++artifactSequence;
      setArtifactMeta((current) => ({
        evidence: { ...current.evidence, refreshing: !current.evidence.pending },
        diagnosis: { ...current.diagnosis, refreshing: !current.diagnosis.pending },
        remediation: { ...current.remediation, refreshing: !current.remediation.pending },
      }));
      const [evidenceResult, diagnosisResult, remediationResult, traceResult] =
        await Promise.allSettled([
          runs.getRunEvidence(id),
          runs.getRunDiagnosis(id),
          runs.getRunRemediation(id),
          runs.getRunTrace(id),
        ]);
      if (!active || sequence !== artifactSequence) return;
      const updatedAt = new Date().toLocaleTimeString();

      if (evidenceResult.status === 'fulfilled') {
        setEvidence(evidenceResult.value);
        updateMeta('evidence', { pending: false, refreshing: false, error: undefined, updatedAt });
      } else {
        markFailure('evidence', evidenceResult.reason);
      }
      if (diagnosisResult.status === 'fulfilled') {
        setDiagnosis(diagnosisResult.value.root_cause_candidates ?? []);
        updateMeta('diagnosis', { pending: false, refreshing: false, error: undefined, updatedAt });
      } else {
        markFailure('diagnosis', diagnosisResult.reason);
      }
      if (remediationResult.status === 'fulfilled') {
        setRemediationPlan(remediationResult.value.remediation_plan);
        updateMeta('remediation', { pending: false, refreshing: false, error: undefined, updatedAt });
      } else {
        markFailure('remediation', remediationResult.reason);
      }
      if (traceResult.status === 'fulfilled') setRunTrace(traceResult.value);
    };

    const controller = createRunDetailSyncController({
      runId: id,
      getRun: runs.getRun,
      getRunEvents: runs.getRunEvents,
      refreshArtifacts,
      onRun: (nextRun) => active && setRun(nextRun),
      onEvents: (incoming) => active && setEvents((current) => mergeEvents(current, incoming)),
      onConnectionState: (state) => active && setConnectionState(state),
    });
    retryArtifactsRef.current = refreshArtifacts;

    const fetchInitial = async () => {
      try {
        const artifacts = refreshArtifacts();
        const [runData, eventsData] = await Promise.all([
          runs.getRun(id),
          runs.getRunEvents(id),
        ]);
        if (!active) return;
        controller.observeRun(runData);
        setEvents((current) => mergeEvents(current, eventsData));
        controller.seedEvents(eventsData);
        await artifacts;
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : t('run.loadFailed'));
      } finally {
        if (active) setLoading(false);
      }
    };

    controller.start();
    void fetchInitial();
    return () => {
      active = false;
      retryArtifactsRef.current = async () => undefined;
      controller.dispose();
    };
  }, [id, retryVersion, t]);

  if (loading) return <RunDetailSkeleton />;

  if (error || !run) {
    return (
      <div className="space-y-3 rounded-lg p-4 status-critical">
        <p>{t('common.error')}: {error || t('run.notFound')}</p>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setRetryVersion((version) => version + 1)}
        >
          {t('run.retry')}
        </button>
      </div>
    );
  }

  const statusLabel = t(`run.status.${run.status}`) || run.status;
  const tabs: Array<{ id: RunTab; label: string }> = [
    { id: 'events', label: t('run.tabs.events') },
    { id: 'evidence', label: t('run.tabs.evidence') },
    { id: 'diagnosis', label: t('run.tabs.diagnosis') },
    { id: 'remediation', label: t('run.tabs.remediation') },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {(connectionState === 'polling' || connectionState === 'reconnecting') && (
        <RealtimeFallbackNotice />
      )}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <h2 className="break-words text-xl font-semibold tracking-tight font-heading">
            {run.service || t('run.incident')}
          </h2>
          <p className="flex flex-wrap gap-x-2 gap-y-1 text-sm text-content-secondary mt-1">
            <span className="mono text-xs">{run.env}</span>
            <span className="text-content-muted">|</span>
            <span className="mono text-xs">{run.severity}</span>
            <span className="text-content-muted">|</span>
            <span className="text-content-muted">{t('common.created')}: {new Date(run.created_at).toLocaleString()}</span>
            {run.updated_at && (
              <>
                <span className="text-content-muted">|</span>
                <span className="text-content-muted">{t('common.updated')}: {new Date(run.updated_at).toLocaleString()}</span>
              </>
            )}
          </p>
        </div>
        <span className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ${getStatusClass(run.status)}`}>
          {run.status === 'RUNNING' && <span className="pulse-live h-2 w-2 rounded-full bg-current"></span>}
          {statusLabel}
        </span>
      </div>

      <div className="card p-5">
        <RunStepper
          status={run.status}
          currentNode={run.current_node}
          haltedAtNode={run.halted_at_node}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="card p-4 sm:p-6">
            <div className="mb-5 flex flex-wrap gap-2 border-b border-border-subtle pb-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`rounded-md px-3 py-1.5 text-sm font-medium transition-fast cursor-pointer ${
                    activeTab === tab.id ? 'btn btn-primary' : 'btn btn-secondary'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === 'events' && <EventTimeline events={events} />}
            {activeTab === 'evidence' && (
              <ArtifactPanelState
                empty={evidence.length === 0}
                pending={artifactMeta.evidence.pending}
                refreshing={artifactMeta.evidence.refreshing}
                error={artifactMeta.evidence.error}
                pendingLabel={t('run.collectingEvidence')}
                updatedAt={artifactMeta.evidence.updatedAt}
                onRetry={() => void retryArtifactsRef.current()}
              >
                <EvidencePanel evidence={evidence} />
              </ArtifactPanelState>
            )}
            {activeTab === 'diagnosis' && (
              <ArtifactPanelState
                empty={diagnosis.length === 0}
                pending={artifactMeta.diagnosis.pending}
                refreshing={artifactMeta.diagnosis.refreshing}
                error={artifactMeta.diagnosis.error}
                pendingLabel={t('run.generatingDiagnosis')}
                updatedAt={artifactMeta.diagnosis.updatedAt}
                onRetry={() => void retryArtifactsRef.current()}
              >
                <DiagnosisCard candidates={diagnosis} />
              </ArtifactPanelState>
            )}
            {activeTab === 'remediation' && (
              <ArtifactPanelState
                empty={!remediationPlan}
                pending={artifactMeta.remediation.pending}
                refreshing={artifactMeta.remediation.refreshing}
                error={artifactMeta.remediation.error}
                pendingLabel={t('run.generatingRemediation')}
                updatedAt={artifactMeta.remediation.updatedAt}
                onRetry={() => void retryArtifactsRef.current()}
              >
                <RemediationCard plan={remediationPlan} approvalStatus={run.status} />
              </ArtifactPanelState>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-4 sm:p-6">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <svg className="h-5 w-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {t('run.quickActions')}
            </h3>
            <div className="space-y-2">
              <Link
                to={`/runs/${id}/rca`}
                className="btn btn-secondary w-full justify-start cursor-pointer"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {t('run.viewRca')}
              </Link>
              {traceHref && (
                <a
                  href={traceHref}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary w-full justify-start cursor-pointer"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4m-4-8h6m0 0v6m0-6L10 16" />
                  </svg>
                  {t('run.viewTrace')}
                </a>
              )}
            </div>
          </div>

          {run.status === 'WAITING_HUMAN' && (
            <div className="card p-4 sm:p-6 status-warning">
              <h3 className="font-heading mb-2 text-lg font-semibold">
                {t('approval.title')}
              </h3>
              <p className="mb-4 text-sm">{t('run.approvalPending')}</p>
              <Link to="/approvals" className="btn btn-secondary w-full justify-center cursor-pointer">
                {t('run.viewApprovals')}
              </Link>
            </div>
          )}

          {run.status === 'NEEDS_HUMAN' && run.terminal_reason && (
            <div className="card p-4 sm:p-6 status-warning">
              <h3 className="font-heading mb-2 text-lg font-semibold">
                {t('run.needsHuman') || 'Needs Human'}
              </h3>
              <p className="mb-1 text-sm font-medium">{run.terminal_reason.code}</p>
              <p className="mb-2 text-xs text-content-secondary">{run.terminal_reason.message}</p>
              {run.terminal_reason.failed_tools && run.terminal_reason.failed_tools.length > 0 && (
                <p className="text-xs text-content-muted">
                  Failed: {run.terminal_reason.failed_tools.join(', ')}
                </p>
              )}
            </div>
          )}

          <div className="card p-4 sm:p-6">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <svg className="h-5 w-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {t('run.runId')}
            </h3>
            <code className="block break-all whitespace-pre-wrap rounded bg-surface-tertiary px-3 py-2 text-xs text-content-secondary">
              {id}
            </code>
            {run.current_node && (
              <div className="mt-4">
                <p className="mb-1 text-xs uppercase tracking-wide text-content-muted">
                  {t('run.currentNode')}
                </p>
                <code className="block break-all whitespace-pre-wrap rounded bg-surface-tertiary px-3 py-2 text-xs text-content-secondary">
                  {run.current_node}
                </code>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
