import { useState } from 'react';
import type { EvidenceItem } from '../types';
import { JsonViewer } from './JsonViewer';
import { useI18n } from '../i18n';

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  logs: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  metrics: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  ),
  deployments: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
    </svg>
  ),
  runbook: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
};

interface EvidencePanelProps {
  evidence: EvidenceItem[];
}

export function EvidencePanel({ evidence }: EvidencePanelProps) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const grouped = evidence.reduce((acc, item) => {
    const cat = item.category || 'other';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, EvidenceItem[]>);

  const toggle = (id: string) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([category, items]) => (
        <div key={category} className="card overflow-hidden">
          <div className="bg-surface-tertiary px-4 py-2.5 flex items-center gap-2 font-medium">
            {CATEGORY_ICONS[category] || (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            )}
            <span className="capitalize text-content-primary font-heading">{category}</span>
            <span className="text-content-muted text-sm">({items.length})</span>
          </div>
          <div className="divide-y divide-border-subtle">
            {items.map((item) => (
              <div key={item.evidence_id}>
                <button 
                  onClick={() => toggle(item.evidence_id)}
                  className="flex w-full min-w-0 items-center justify-between gap-3 px-4 py-3 text-left hover:bg-surface-tertiary transition-fast cursor-pointer"
                >
                  <span className="min-w-0 break-words text-sm text-content-primary">{item.summary}</span>
                  {expanded[item.evidence_id] ? (
                    <svg className="w-4 h-4 text-content-muted flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 text-content-muted flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                </button>
                {expanded[item.evidence_id] && (
                    <div className="px-4 pb-4 bg-surface-tertiary">
                    <div className="flex gap-4 text-xs text-content-muted mb-3">
                  <span>{t('evidence.confidence')}: {Math.round((item.confidence ?? 0) * 100)}%</span>
                  <span>{t('evidence.freshness')}: {Math.round((item.freshness_score ?? 0) * 100)}%</span>
                    </div>
                    {item.raw_payload && (
                      <JsonViewer data={item.raw_payload} defaultExpanded={false} />
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
      {evidence.length === 0 && (
        <p className="text-content-muted text-center py-8">{t('evidence.noEvidence')}</p>
      )}
    </div>
  );
}
