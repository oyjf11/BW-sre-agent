import type { RootCauseCandidate } from '../types';
import { useI18n } from '../i18n';

interface DiagnosisCardProps {
  candidates: RootCauseCandidate[];
  onEvidenceClick?: (evidenceId: string) => void;
}

export function DiagnosisCard({ candidates, onEvidenceClick }: DiagnosisCardProps) {
  const { t } = useI18n();
  if (candidates.length === 0) {
    return <p className="text-content-muted">{t('diagnosis.noCandidates')}</p>;
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-content-primary font-heading">{t('diagnosis.rootCauseCandidates')}</h3>
      {candidates.map((candidate, idx) => (
        <div key={candidate.candidate_id} className="card p-4 hover:border-border transition-fast">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-accent font-heading">#{idx + 1}</span>
            <div className="flex items-center gap-2">
              <div className="w-20 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-accent rounded-full" 
                  style={{ width: `${candidate.confidence * 100}%` }}
                />
              </div>
              <span className="text-xs text-content-secondary mono">
                {Math.round(candidate.confidence * 100)}%
              </span>
            </div>
          </div>
          <p className="text-sm break-words text-content-primary mb-3">{candidate.hypothesis}</p>
          {candidate.supporting_evidence_ids.length > 0 && (
            <div className="text-xs text-content-muted">
              {t('diagnosis.supportingEvidence')}:{' '}
              {candidate.supporting_evidence_ids.map((id) => (
                <button
                  key={id}
                  onClick={() => onEvidenceClick?.(id)}
                  className="text-accent break-all hover:text-accent-hover transition-fast mx-1 cursor-pointer"
                >
                  {id}
                </button>
              ))}
            </div>
          )}
          {candidate.next_checks.length > 0 && (
            <div className="mt-2 text-xs text-content-muted">
              {t('diagnosis.nextChecks')}: {candidate.next_checks.join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
