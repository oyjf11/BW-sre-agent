import { useI18n } from '../i18n';

const DISPLAY_STEPS = [
  { key: 'NEW', i18n: 'run.status.NEW' },
  { key: 'TRIAGED', i18n: 'run.status.TRIAGED' },
  { key: 'PLANNED', i18n: 'run.status.PLANNED' },
  { key: 'GATHERING_EVIDENCE', i18n: 'run.status.GATHERING_EVIDENCE' },
  { key: 'DIAGNOSED', i18n: 'run.status.DIAGNOSED' },
  { key: 'RISK_GATE', i18n: 'run.status.RISK_GATE' },
  { key: 'PENDING_APPROVAL', i18n: 'run.status.PENDING_APPROVAL' },
  { key: 'EXECUTING', i18n: 'run.status.EXECUTING' },
  { key: 'VERIFYING', i18n: 'run.status.VERIFYING' },
  { key: 'COMPLETED', i18n: 'run.status.COMPLETED' },
];

const NODE_TO_STEP: Record<string, number> = {
  node_intake: DISPLAY_STEPS.findIndex((s) => s.key === 'NEW'),
  node_triage: DISPLAY_STEPS.findIndex((s) => s.key === 'TRIAGED'),
  node_planner: DISPLAY_STEPS.findIndex((s) => s.key === 'PLANNED'),
  node_evidence_fanout: DISPLAY_STEPS.findIndex((s) => s.key === 'GATHERING_EVIDENCE'),
  node_evidence_aggregate: DISPLAY_STEPS.findIndex((s) => s.key === 'GATHERING_EVIDENCE'),
  node_diagnose: DISPLAY_STEPS.findIndex((s) => s.key === 'DIAGNOSED'),
  node_critic: DISPLAY_STEPS.findIndex((s) => s.key === 'DIAGNOSED'),
  node_remediation: DISPLAY_STEPS.findIndex((s) => s.key === 'PENDING_APPROVAL'),
  node_risk_gate: DISPLAY_STEPS.findIndex((s) => s.key === 'RISK_GATE'),
  node_approval_interrupt: DISPLAY_STEPS.findIndex((s) => s.key === 'PENDING_APPROVAL'),
  node_executor: DISPLAY_STEPS.findIndex((s) => s.key === 'EXECUTING'),
  node_verify_outcome: DISPLAY_STEPS.findIndex((s) => s.key === 'VERIFYING'),
  node_rca: DISPLAY_STEPS.findIndex((s) => s.key === 'COMPLETED'),
};

const STATUS_TO_STEP: Record<string, number> = {
  NEW: 0,
  TRIAGED: 1,
  PLANNED: 2,
  GATHERING_EVIDENCE: 3,
  DIAGNOSED: 4,
  PENDING_APPROVAL: 6,
  WAITING_HUMAN: 6,
  EXECUTING: 7,
  VERIFYING: 8,
  COMPLETED: 9,
};

interface RunStepperProps {
  status: string;
  currentNode?: string;
  haltedAtNode?: string;
}

export function RunStepper({ status, currentNode, haltedAtNode }: RunStepperProps) {
  const { t } = useI18n();

  let currentIndex = STATUS_TO_STEP[status] ?? -1;
  if (currentIndex < 0 && currentNode) {
    currentIndex = NODE_TO_STEP[currentNode] ?? -1;
  }
  if (currentIndex < 0) {
    currentIndex = 0;
  }

  let haltedIndex = -1;
  if (haltedAtNode) {
    haltedIndex = NODE_TO_STEP[haltedAtNode] ?? -1;
  }

  const isNeedsHuman = status === 'NEEDS_HUMAN';
  const isFailed = status === 'FAILED';

  return (
    <div className="flex items-center justify-between overflow-x-auto pb-2">
      {DISPLAY_STEPS.map((step, index) => {
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;
        const isHaltedHere = isNeedsHuman && haltedIndex === index;
        const isFailedHere = isFailed && haltedIndex === index;

        return (
          <div key={step.key} className="flex items-center flex-shrink-0">
            <div className="flex flex-col items-center">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium transition-fast ${
                  isHaltedHere
                    ? 'bg-status-warning text-surface-primary'
                    : isFailedHere
                    ? 'bg-status-critical text-surface-primary'
                    : isCompleted
                    ? 'bg-status-success text-surface-primary'
                    : isCurrent
                    ? 'bg-accent text-surface-primary shadow-glow'
                    : 'bg-surface-tertiary text-content-muted'
                }`}
              >
                {isCompleted ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : isHaltedHere ? (
                  <span className="text-sm font-bold">!</span>
                ) : isFailedHere ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>
              <span
                className={`text-[10px] mt-1.5 whitespace-nowrap ${
                  isHaltedHere
                    ? 'text-status-warning font-medium'
                    : isFailedHere
                    ? 'text-status-critical font-medium'
                    : isCurrent
                    ? 'text-accent font-medium'
                    : 'text-content-muted'
                }`}
              >
                {t(step.i18n)}
              </span>
            </div>
            {index < DISPLAY_STEPS.length - 1 && (
              <div
                className={`w-6 h-0.5 mx-0.5 ${isCompleted ? 'bg-status-success' : 'bg-border-subtle'}`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
