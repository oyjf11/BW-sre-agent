import { useState } from 'react';

interface JsonViewerProps {
  data: unknown;
  defaultExpanded?: boolean;
}

function JsonValue({ value, depth = 0 }: { value: unknown; depth?: number }) {
  const [expanded, setExpanded] = useState(depth < 2);

  if (value === null) return <span className="text-content-muted">null</span>;
  if (value === undefined) return <span className="text-content-muted">undefined</span>;
  if (typeof value === 'boolean') return <span className="text-status-info">{value.toString()}</span>;
  if (typeof value === 'number') return <span className="text-status-success">{value}</span>;
  if (typeof value === 'string') return <span className="text-status-warning">"{value}"</span>;

  if (Array.isArray(value)) {
    if (value.length === 0) return <span>[]</span>;
    return (
      <span>
        <button onClick={() => setExpanded(!expanded)} className="flex items-center gap-1 hover:bg-surface-tertiary px-1 rounded transition-fast cursor-pointer">
          {expanded ? (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          ) : (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          [{value.length}]
        </button>
        {expanded && (
          <div className="ml-4">
            {value.map((item, i) => (
              <div key={i}><JsonValue value={item} depth={depth + 1} /></div>
            ))}
          </div>
        )}
      </span>
    );
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) return <span>{'{}'}</span>;
    return (
      <span>
        <button onClick={() => setExpanded(!expanded)} className="flex items-center gap-1 hover:bg-surface-tertiary px-1 rounded transition-fast cursor-pointer">
          {expanded ? (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          ) : (
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {'{'}...{'}'}
        </button>
        {expanded && (
          <div className="ml-4">
            {entries.map(([k, v]) => (
              <div key={k}>
                <span className="text-status-pending">"{k}"</span>: <JsonValue value={v} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
      </span>
    );
  }

  return <span>{String(value)}</span>;
}

export function JsonViewer({ data, defaultExpanded = false }: JsonViewerProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
  };

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative">
      <div className="absolute top-2 right-2 flex gap-1">
        <button onClick={copyToClipboard} className="p-1.5 hover:bg-surface-tertiary rounded transition-fast cursor-pointer" title="Copy">
          <svg className="w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
        <button onClick={downloadJson} className="p-1.5 hover:bg-surface-tertiary rounded transition-fast cursor-pointer" title="Download">
          <svg className="w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
      </div>
      <button onClick={() => setExpanded(!expanded)} className="flex items-center gap-1 mb-2 hover:bg-surface-tertiary px-2 py-1 rounded transition-fast cursor-pointer">
        {expanded ? (
          <svg className="w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        )}
        <span className="text-sm text-content-secondary">Toggle JSON</span>
      </button>
      {expanded && (
        <pre className="bg-surface-secondary p-4 rounded-lg overflow-x-auto text-sm font-mono border border-border-subtle">
          <JsonValue value={data} />
        </pre>
      )}
    </div>
  );
}
