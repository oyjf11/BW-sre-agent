import { useI18n } from '../i18n';

const STEPS = [
  'NEW',
  'TRIAGED',
  'PLANNED',
  'GATHERING_EVIDENCE',
  'DIAGNOSED',
  'PENDING_APPROVAL',
  'EXECUTING',
  'COMPLETED',
];

interface RunStepperProps {
  status: string;
}

export function RunStepper({ status }: RunStepperProps) {
  const { t } = useI18n();
  const normalizedStatus = status === 'WAITING_HUMAN' ? 'PENDING_APPROVAL' : status;
  const currentIndex = STEPS.indexOf(normalizedStatus);
  
  return (
    <div className="flex items-center justify-between overflow-x-auto pb-2">
      {STEPS.map((step, index) => {
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;
        
        return (
          <div key={step} className="flex items-center flex-shrink-0">
            <div className="flex flex-col items-center">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium transition-fast ${
                isCompleted ? 'bg-status-success text-surface-primary' :
                isCurrent ? 'bg-accent text-surface-primary shadow-glow' :
                'bg-surface-tertiary text-content-muted'
              }`}>
                {isCompleted ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : index + 1}
              </div>
              <span className={`text-[10px] mt-1.5 whitespace-nowrap ${isCurrent ? 'text-accent font-medium' : 'text-content-muted'}`}>
                {t(`run.status.${step}`)}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div className={`w-6 h-0.5 mx-0.5 ${isCompleted ? 'bg-status-success' : 'bg-border-subtle'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
