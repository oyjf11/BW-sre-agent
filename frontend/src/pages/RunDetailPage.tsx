import { useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { runs } from '../services/runs';
import { useI18n } from '../i18n';
import { sseClient } from '../services/sse';
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

const TERMINAL_STATUSES = new Set(['COMPLETED', 'FAILED', 'WAITING_HUMAN']);
const ARTIFACT_PENDING_STATUSES = new Set([404]);

type RunTab = 'events' | 'evidence' | 'diagnosis' | 'remediation';

function getStatusClass(status: string): string {
  switch (status) {
    case 'COMPLETED':
      return 'status-success';
    case 'FAILED':
      return 'status-critical';
    case 'WAITING_HUMAN':
      return 'status-warning';
    case 'RUNNING':
    case 'PENDING':
      return 'status-info';
    default:
      return 'status-pending';
  }
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
  const seenEventIds = useRef<Set<string>>(new Set());

  const traceHref = runTrace?.external_trace_url || runTrace?.trace_url;

  useEffect(() => {
    if (!id) return;

    const loadArtifactData = async () => {
      const [evidenceResult, diagnosisResult, remediationResult, traceResult] = await Promise.allSettled([
        runs.getRunEvidence(id),
        runs.getRunDiagnosis(id),
        runs.getRunRemediation(id),
        runs.getRunTrace(id),
      ]);

      if (evidenceResult.status === 'fulfilled') {
        setEvidence(evidenceResult.value);
      }

      if (diagnosisResult.status === 'fulfilled') {
        setDiagnosis(diagnosisResult.value.root_cause_candidates ?? []);
      } else if (
        !('status' in diagnosisResult.reason) ||
        !ARTIFACT_PENDING_STATUSES.has(diagnosisResult.reason.status)
      ) {
        throw diagnosisResult.reason;
      } else {
        setDiagnosis([]);
      }

      if (remediationResult.status === 'fulfilled') {
        setRemediationPlan(remediationResult.value.remediation_plan);
      } else if (
        !('status' in remediationResult.reason) ||
        !ARTIFACT_PENDING_STATUSES.has(remediationResult.reason.status)
      ) {
        throw remediationResult.reason;
      } else {
        setRemediationPlan(undefined);
      }

      if (traceResult.status === 'fulfilled') {
        setRunTrace(traceResult.value);
      }
    };

    const fetchInitial = async () => {
      try {
        const [runData, eventsData] = await Promise.all([
          runs.getRun(id),
          runs.getRunEvents(id),
        ]);
        setRun(runData);
        seenEventIds.current = new Set(eventsData.map((ev) => ev.event_id));
        setEvents(eventsData);
        await loadArtifactData();
      } catch (err) {
        setError(err instanceof Error ? err.message : t('run.loadFailed'));
      } finally {
        setLoading(false);
      }
    };

    const refreshArtifacts = () => {
      loadArtifactData().catch(() => {
        // Ignore artifact refresh errors while the run is still progressing.
      });
    };

    fetchInitial();

    // SSE connection: append new events and refresh run status on each message
    const handleSseMessage = (data: unknown) => {
      const ev = data as RunEvent;
      if (!ev?.event_id || seenEventIds.current.has(ev.event_id)) return;
      seenEventIds.current.add(ev.event_id);
      setEvents(prev => [...prev, ev]);

      // Refresh run status after each SSE event (SSE carries events, not run state)
      runs.getRun(id).then(setRun).catch(() => {/* ignore */});
      refreshArtifacts();
    };

    sseClient.connect(`/incidents/runs/${id}/stream`);
    sseClient.on('message', handleSseMessage);

    // Slow poll for run status in case SSE misses terminal state transitions
    const statusPoll = setInterval(async () => {
      try {
        const runData = await runs.getRun(id);
        setRun(runData);
        refreshArtifacts();
        if (TERMINAL_STATUSES.has(runData.status)) {
          clearInterval(statusPoll);
          sseClient.disconnect();
        }
      } catch {/* ignore */}
    }, 5000);

    return () => {
      sseClient.off('message', handleSseMessage);
      sseClient.disconnect();
      clearInterval(statusPoll);
    };
  }, [id, t]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center gap-3 text-content-secondary">
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{t('common.loading')}</span>
        </div>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="p-4 rounded-lg status-critical">
        {t('common.error')}: {error || t('run.notFound')}
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
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight font-heading">
            {run.service || t('run.incident')}
          </h2>
          <p className="text-sm text-content-secondary mt-1">
            <span className="mono text-xs">{run.env}</span>
            <span className="mx-2 text-content-muted">|</span>
            <span className="mono text-xs">{run.severity}</span>
            <span className="mx-2 text-content-muted">|</span>
            <span className="text-content-muted">{t('common.created')}: {new Date(run.created_at).toLocaleString()}</span>
          </p>
        </div>
        <span className={`px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 ${getStatusClass(run.status)}`}>
          {run.status === 'RUNNING' && <span className="w-2 h-2 rounded-full bg-current pulse-live"></span>}
          {statusLabel}
        </span>
      </div>

      <div className="card p-5">
        <RunStepper status={run.status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <div className="flex flex-wrap gap-2 border-b border-border-subtle mb-5 pb-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-fast cursor-pointer ${
                    activeTab === tab.id ? 'btn btn-primary' : 'btn btn-secondary'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {activeTab === 'events' && <EventTimeline events={events} />}
            {activeTab === 'evidence' && <EvidencePanel evidence={evidence} />}
            {activeTab === 'diagnosis' && <DiagnosisCard candidates={diagnosis} />}
            {activeTab === 'remediation' && (
              <RemediationCard plan={remediationPlan} approvalStatus={run.status} />
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {t('run.quickActions')}
            </h3>
            <div className="space-y-2">
              <Link
                to={`/runs/${id}/rca`}
                className="btn btn-secondary w-full justify-start cursor-pointer"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4m-4-8h6m0 0v6m0-6L10 16" />
                  </svg>
                  {t('run.viewTrace')}
                </a>
              )}
            </div>
          </div>

          {run.status === 'WAITING_HUMAN' && (
            <div className="card p-6 status-warning">
              <h3 className="text-lg font-semibold mb-2 font-heading">
                {t('approval.title')}
              </h3>
              <p className="text-sm mb-4">{t('run.approvalPending')}</p>
              <Link to="/approvals" className="btn btn-secondary w-full justify-center cursor-pointer">
                {t('run.viewApprovals')}
              </Link>
            </div>
          )}

          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Run ID
            </h3>
            <code className="text-xs text-content-secondary bg-surface-tertiary px-3 py-2 rounded block overflow-x-auto">
              {id}
            </code>
            {run.current_node && (
              <div className="mt-4">
                <p className="text-xs uppercase tracking-wide text-content-muted mb-1">
                  {t('run.currentNode')}
                </p>
                <code className="text-xs text-content-secondary bg-surface-tertiary px-3 py-2 rounded block overflow-x-auto">
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
