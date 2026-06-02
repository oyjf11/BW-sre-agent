import { useEffect, useRef, useState } from 'react';
import type { RunEvent } from '../types';
import { formatTime } from '../utils/time';
import { useI18n } from '../i18n';

interface EventTimelineProps {
  events: RunEvent[];
  onReconnect?: () => void;
}

type FilterType = 'ALL' | 'ERROR' | 'WARNING' | 'INFO';

function getEventLevelClass(level: string): string {
  switch (level) {
    case 'ERROR':
      return 'status-critical';
    case 'WARNING':
      return 'status-warning';
    default:
      return 'status-info';
  }
}

function getEventBorderClass(level: string): string {
  switch (level) {
    case 'ERROR':
      return 'border-l-status-critical';
    case 'WARNING':
      return 'border-l-status-warning';
    default:
      return 'border-l-border';
  }
}

export function EventTimeline({ events, onReconnect }: EventTimelineProps) {
  const { t } = useI18n();
  const [filter, setFilter] = useState<FilterType>('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  const filteredEvents = filter === 'ALL' 
    ? events 
    : events.filter(e => e.level === filter);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [filteredEvents, autoScroll]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value as FilterType)}
            className="input text-sm py-1.5"
          >
            <option value="ALL">{t('event.filterAll')}</option>
            <option value="ERROR">{t('event.filterError')}</option>
            <option value="WARNING">{t('event.filterWarning')}</option>
            <option value="INFO">{t('event.filterInfo')}</option>
          </select>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-content-secondary cursor-pointer">
            <input 
              type="checkbox" 
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-border bg-surface-secondary text-accent focus:ring-accent"
            />
            {t('event.autoScroll')}
          </label>
          {onReconnect && (
            <button onClick={onReconnect} className="p-1.5 hover:bg-surface-tertiary rounded transition-fast cursor-pointer">
              <svg className="w-4 h-4 text-content-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          )}
        </div>
      </div>

      <div ref={containerRef} className="max-h-96 overflow-y-auto space-y-2 pr-2">
        {filteredEvents.length === 0 ? (
          <p className="text-content-muted text-center py-8">{t('event.noEvents')}</p>
        ) : (
          filteredEvents.map((event) => (
            <div 
              key={event.event_id} 
              className={`border-l-4 pl-4 py-3 rounded-r transition-fast hover:bg-surface-tertiary cursor-pointer ${getEventBorderClass(event.level)}`}
            >
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs px-2 py-0.5 rounded font-medium ${getEventLevelClass(event.level)}`}>
                  {event.level}
                </span>
                <span className="text-xs text-content-muted mono">
                  {formatTime(event.timestamp)}
                </span>
                {event.node_name && (
                  <span className="text-xs text-content-muted">@{event.node_name}</span>
                )}
              </div>
              <p className="mt-2 break-words text-sm text-content-primary">{event.message}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
