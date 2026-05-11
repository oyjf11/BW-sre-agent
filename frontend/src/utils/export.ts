export function exportJson(data: unknown, filename: string): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function exportEventsJson(events: unknown[]): void {
  exportJson(events, `events-${Date.now()}.json`);
}

export function exportEvidenceJson(evidence: unknown[]): void {
  exportJson(evidence, `evidence-${Date.now()}.json`);
}
