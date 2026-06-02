import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { approvals } from '../services/approvals';
import { useI18n } from '../i18n';
import type { ApprovalDetail } from '../types';

function getRiskClass(risk: string | undefined): string {
  switch (risk) {
    case 'CRITICAL':
      return 'status-critical';
    case 'HIGH':
      return 'status-warning';
    case 'MEDIUM':
      return 'status-info';
    default:
      return 'status-success';
  }
}

export function ApprovalDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useI18n();
  const [approval, setApproval] = useState<ApprovalDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showModify, setShowModify] = useState(false);
  const [modifiedParams, setModifiedParams] = useState('');

  useEffect(() => {
    if (!id) return;
    
    approvals.getApproval(id)
      .then(setApproval)
      .catch(err => setError(err instanceof Error ? err.message : t('approval.loadFailed')))
      .finally(() => setLoading(false));
  }, [id, t]);

  const handleDecision = async (decision: string) => {
    if (!id) return;
    setSubmitting(true);
    try {
      await approvals.postDecision(id, { decision });
      navigate('/approvals');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('approval.submitFailed'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleModify = async () => {
    if (!id) return;
    setSubmitting(true);
    try {
      const params = JSON.parse(modifiedParams);
      await approvals.postDecision(id, { decision: 'modify', comment: JSON.stringify(params) });
      navigate('/approvals');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('approval.submitFailed'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
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
  
  if (error || !approval) return <div className="p-4 rounded-lg status-critical">{error || t('run.notFound')}</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link to="/approvals" className="text-accent hover:text-accent-hover transition-fast inline-block">
        &larr; {t('common.back')}
      </Link>
      
      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-6 font-heading">
          {t('approval.requestTitle')}
        </h2>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="text-sm text-content-muted">ID</label>
            <p className="font-mono text-content-secondary">{approval.approval_id}</p>
          </div>
          <div>
            <label className="text-sm text-content-muted">{t('common.actions')}</label>
            <p className="text-content-primary">
              <span className="mono">{approval.action?.action_type}</span>
              <span className="text-content-muted"> on </span>
              <code className="text-accent">{approval.action?.service}</code>
              <span className="text-content-muted"> ({approval.action?.env})</span>
            </p>
          </div>
          <div>
            <label className="text-sm text-content-muted">{t('approval.riskLevel')}</label>
            <p className="mt-1">
              <span className={`px-2 py-1 text-xs rounded font-medium ${getRiskClass(approval.risk_level)}`}>
                {approval.risk_level}
              </span>
            </p>
          </div>
          <div>
            <label className="text-sm text-content-muted">{t('approval.reason')}</label>
            <p className="text-content-primary mt-1">{approval.reason}</p>
          </div>
        </div>

        {showModify ? (
          <div className="space-y-4 mb-6">
            <div>
              <label className="text-sm text-content-muted">{t('approval.modifiedParams')}</label>
              <textarea
                value={modifiedParams}
                onChange={(e) => setModifiedParams(e.target.value)}
                rows={4}
                className="input w-full mt-2 font-mono text-sm resize-none"
                placeholder='{"param1": "value1"}'
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleModify}
                disabled={submitting}
                className="btn btn-primary flex-1 cursor-pointer"
              >
                {t('common.submit')}
              </button>
              <button
                onClick={() => setShowModify(false)}
                className="btn btn-secondary flex-1 cursor-pointer"
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => handleDecision('approved')}
              disabled={submitting}
              className="btn btn-primary cursor-pointer"
            >
              {t('approval.approve')}
            </button>
            <button
              onClick={() => handleDecision('rejected')}
              disabled={submitting}
              className="btn status-critical cursor-pointer"
            >
              {t('approval.reject')}
            </button>
            <button
              onClick={() => setShowModify(true)}
              disabled={submitting}
              className="btn btn-secondary col-span-2 cursor-pointer"
            >
              {t('common.edit')}
            </button>
            <button
              onClick={() => handleDecision('more_evidence')}
              disabled={submitting}
              className="btn btn-ghost col-span-2 cursor-pointer"
            >
              {t('approval.needMoreInfo')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
