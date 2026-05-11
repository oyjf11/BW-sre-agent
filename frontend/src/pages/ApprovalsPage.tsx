import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { approvals } from '../services/approvals';
import { useI18n } from '../i18n';
import type { ApprovalSummary } from '../types';

function getRiskClass(risk: string): string {
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

export function ApprovalsPage() {
  const { t } = useI18n();
  const [list, setList] = useState<ApprovalSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState({ env: '', risk: '', service: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await approvals.listPendingApprovals();
        setList(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : t('approval.loadFailed'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [t]);

  const filteredList = list.filter(item => {
    if (filter.env && item.action?.env !== filter.env) return false;
    if (filter.risk && item.risk_level !== filter.risk) return false;
    if (filter.service && !item.action?.service?.toLowerCase().includes(filter.service.toLowerCase())) return false;
    return true;
  });

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
  
  if (error) return <div className="p-4 rounded-lg status-critical">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <h2 className="text-xl font-semibold font-heading">
        {t('approval.title')}
      </h2>
      
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder={t('run.service') === '服务' ? '搜索服务...' : 'Search by service...'}
            value={filter.service}
            onChange={(e) => setFilter({ ...filter, service: e.target.value })}
            className="input w-full pl-10"
          />
        </div>
        <select
          value={filter.env}
          onChange={(e) => setFilter({ ...filter, env: e.target.value })}
          className="input px-4 py-2"
        >
          <option value="">{t('run.environment') === '环境' ? '全部环境' : 'All Envs'}</option>
          <option value="prod">{t('run.environments.prod')}</option>
          <option value="staging">{t('run.environments.staging')}</option>
          <option value="dev">{t('run.environments.dev')}</option>
        </select>
        <select
          value={filter.risk}
          onChange={(e) => setFilter({ ...filter, risk: e.target.value })}
          className="input px-4 py-2"
        >
          <option value="">{t('approval.riskLevel') === '风险等级' ? '全部风险' : 'All Risks'}</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>
      
      {filteredList.length === 0 ? (
        <div className="card p-12 text-center">
          <svg className="w-12 h-12 mx-auto text-content-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-content-muted">{t('common.noData')}</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-border-subtle">
                <th className="px-6 py-4 text-left text-xs font-medium text-content-muted uppercase tracking-wider">ID</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-content-muted uppercase tracking-wider">{t('run.service')}/{t('run.environment')}</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-content-muted uppercase tracking-wider">{t('approval.riskLevel')}</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-content-muted uppercase tracking-wider">{t('common.created')}</th>
                <th className="px-6 py-4 text-left text-xs font-medium text-content-muted uppercase tracking-wider">{t('common.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {filteredList.map((item) => (
                <tr key={item.approval_id} className="border-b border-border-subtle hover:bg-surface-tertiary transition-fast">
                  <td className="px-6 py-4">
                    <Link to={`/approvals/${item.approval_id}`} className="text-accent hover:text-accent-hover transition-fast">
                      {item.approval_id.slice(0, 8)}...
                    </Link>
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-sm mono text-content-secondary">{item.action?.service}</code>
                    <span className="text-content-muted mx-1">/</span>
                    <span className="text-sm text-content-muted">{item.action?.env}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded font-medium ${getRiskClass(item.risk_level || '')}`}>
                      {item.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-content-muted">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <Link to={`/approvals/${item.approval_id}`} className="text-sm text-accent hover:text-accent-hover transition-fast">
                      {t('common.view')}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
