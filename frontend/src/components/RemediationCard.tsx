import type { RemediationPlan } from '../types';

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
  if (!plan) {
    return <p className="text-content-muted">No remediation plan yet</p>;
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
            Waiting for human approval
          </span>
        </div>
      )}

      {plan.actions.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-content-secondary">Actions</h4>
          {plan.actions.map((action, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-surface-tertiary rounded-lg hover:bg-border transition-fast">
              <div className="text-sm">
                <span className="font-medium text-content-primary">{action.action_type}</span>
                <span className="text-content-muted mx-2">on</span>
                <code className="text-accent">{action.service}</code>
                <span className="text-content-muted mx-2">in</span>
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
          <strong>Rollback:</strong> {plan.rollback_plan}
        </div>
      )}
    </div>
  );
}
