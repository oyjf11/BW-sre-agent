import type { RemediationPlan } from '../types';
import { useI18n } from '../i18n';

const RISK_COLORS: Record<string, string> = {
  LOW: 'status-success',
  MEDIUM: 'status-warning',
  HIGH: 'status-warning',
  CRITICAL: 'status-critical',
};

interface RemediationCardProps {
  plan?: RemediationPlan;
  approvalStatus?: string;
}

export function RemediationCard({ plan, approvalStatus }: RemediationCardProps) {
  const { t } = useI18n();
  if (!plan) {
    return <p className="text-content-muted">{t('remediation.noPlan')}</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="font-semibold text-content-primary font-heading">{plan.summary}</h3>
        <p className="text-sm text-content-secondary mt-1">{plan.expected_outcome}</p>
      </div>

      {approvalStatus === 'WAITING_HUMAN' && (
        <div className="status-warning border rounded-lg p-3 text-sm">
          <span className="inline-flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-current pulse-live"></span>
            {t('remediation.waitingApproval')}
          </span>
        </div>
      )}

      {plan.actions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-content-secondary">{t('remediation.actions')}</h4>
          {plan.actions.map((action, idx) => (
            <div key={idx} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-surface-tertiary p-3 hover:bg-border transition-fast">
              <div className="min-w-0 break-words text-sm">
                <span className="font-medium text-content-primary">{action.action_type}</span>
                <span className="text-content-muted mx-2">{t('remediation.on')}</span>
                <code className="text-accent">{action.service}</code>
                <span className="text-content-muted mx-2">{t('remediation.in')}</span>
                <span className="text-content-secondary">{action.env}</span>
              </div>
              <span className={`px-2 py-1 text-xs rounded font-medium ${RISK_COLORS[action.risk_level] || 'status-info'}`}>
                {action.risk_level}
              </span>
            </div>
          ))}
        </div>
      )}

      {plan.rollback_plan && (
        <div className="text-sm text-content-muted">
          <strong>{t('remediation.rollback')}:</strong> {plan.rollback_plan}
        </div>
      )}
    </div>
  );
}
