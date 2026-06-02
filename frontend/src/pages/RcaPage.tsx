import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { runs } from '../services/runs';
import { useI18n } from '../i18n';
import type { RcaReport } from '../types';

export function RcaPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useI18n();
  const [rca, setRca] = useState<RcaReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    
    runs.getRunRca(id)
      .then(setRca)
      .catch(err => setError(err instanceof Error ? err.message : t('rca.loadFailed')))
      .finally(() => setLoading(false));
  }, [id, t]);

  const downloadRca = () => {
    if (!rca) return;
    const blob = new Blob([rca.report_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rca-${id}.md`;
    a.click();
    URL.revokeObjectURL(url);
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
  
  if (error) return <div className="p-4 rounded-lg status-critical">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Link to={`/runs/${id}`} className="text-accent hover:text-accent-hover transition-fast">
          &larr; {t('common.back')}
        </Link>
        {rca && (
          <button
            onClick={downloadRca}
            className="btn btn-secondary cursor-pointer"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            {t('rca.exportMarkdown')}
          </button>
        )}
      </div>
      
      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-6 font-heading">
          {t('rca.title')}
        </h2>
        
        {rca ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium text-content-muted uppercase tracking-wider mb-2">
                {t('rca.rootCause')}
              </h3>
              <p className="text-content-primary">{rca.root_cause}</p>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-content-muted uppercase tracking-wider mb-2">
                {t('rca.resolution')}
              </h3>
              <p className="text-content-primary">{rca.resolution}</p>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-content-muted uppercase tracking-wider mb-2">
                {t('rca.prevention')}
              </h3>
              <ul className="list-disc list-inside space-y-1">
                {rca.prevention_items?.map((item, i) => (
                  <li key={i} className="text-content-primary">{item}</li>
                ))}
              </ul>
            </div>
            
            <div className="pt-4 border-t border-border-subtle">
              <span className="text-sm text-content-muted">
                {t('rca.confirmedByHuman')}: 
                <span className={`ml-2 px-2 py-0.5 rounded text-xs ${rca.confirmed_by_human ? 'status-success' : 'status-warning'}`}>
                  {rca.confirmed_by_human ? t('rca.yes') : t('rca.no')}
                </span>
              </span>
            </div>
          </div>
        ) : (
          <p className="text-content-muted">{t('rca.pending')}</p>
        )}
      </div>
    </div>
  );
}
