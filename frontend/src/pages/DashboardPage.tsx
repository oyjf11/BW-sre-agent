import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { runs } from '../services/runs';
import { useI18n } from '../i18n';
import type { RunSummary } from '../types';

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
    case 'NEW':
    case 'TRIAGED':
    case 'DIAGNOSED':
      return 'status-info';
    default:
      return 'status-pending';
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function DashboardPage() {
  const { t } = useI18n();
  const [runsList, setRunsList] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        const data = await runs.listRuns(20, 0);
        setRunsList(data);
      } catch (err) {
        console.error('Failed to load runs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRuns();
  }, []);

  const recentRuns = runsList.slice(0, 10);
  const activeRuns = runsList.filter(r => 
    ['NEW', 'TRIAGED', 'DIAGNOSED', 'RUNNING', 'PENDING', 'WAITING_HUMAN'].includes(r.status)
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-5 hover:border-zinc-300 transition-fast">
          <div className="text-3xl font-bold text-zinc-900 font-heading">{runsList.length}</div>
          <div className="text-sm text-zinc-500 mt-1">总工单</div>
        </div>
        <div className="card p-5 hover:border-zinc-300 transition-fast">
          <div className="text-3xl font-bold text-amber-600 font-heading">{activeRuns.length}</div>
          <div className="text-sm text-zinc-500 mt-1">进行中</div>
        </div>
        <div className="card p-5 hover:border-zinc-300 transition-fast">
          <div className="text-3xl font-bold text-emerald-600 font-heading">
            {runsList.filter(r => r.status === 'COMPLETED').length}
          </div>
          <div className="text-sm text-zinc-500 mt-1">已完成</div>
        </div>
        <div className="card p-5 hover:border-zinc-300 transition-fast">
          <div className="text-3xl font-bold text-red-600 font-heading">
            {runsList.filter(r => r.status === 'FAILED').length}
          </div>
          <div className="text-sm text-zinc-500 mt-1">失败</div>
        </div>
      </div>

      <div className="flex gap-4">
        <Link
          to="/runs/new"
          className="btn btn-primary"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('run.createNew')}
        </Link>
      </div>

      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-zinc-100">
          <h2 className="font-semibold text-zinc-900 font-heading">最近工单</h2>
        </div>
        
        {loading ? (
          <div className="p-8 text-center text-zinc-500">加载中...</div>
        ) : recentRuns.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-zinc-500 mb-4">暂无工单</div>
            <Link
              to="/runs/new"
              className="text-blue-600 hover:text-blue-700 transition-fast"
            >
              创建第一个工单
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-zinc-100">
            {recentRuns.map((run) => (
              <Link
                key={run.run_id}
                to={`/runs/${run.run_id}`}
                className="block px-5 py-4 hover:bg-zinc-50 transition-fast cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`status-dot ${getStatusClass(run.status)}`} />
                    <div>
                      <div className="font-medium text-zinc-900 font-heading">
                        {run.ticket_id || run.run_id.slice(0, 8)}
                      </div>
                      <div className="text-sm text-zinc-500">
                        {run.service} · {run.env} · {run.severity}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`inline-block px-2.5 py-1 text-xs rounded-md font-medium ${getStatusClass(run.status)}`}>
                      {run.status}
                    </span>
                    <div className="text-xs text-zinc-400 mt-1.5 mono">
                      {formatDate(run.created_at)}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
