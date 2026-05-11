import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { runs } from '../services/runs';
import { useI18n } from '../i18n';
import type { IncidentTicket } from '../types';

type CreateMode = 'ticket' | 'ticket_id' | 'alert_event';

const MODES: CreateMode[] = ['ticket', 'ticket_id', 'alert_event'];

const MODE_LABELS: Record<CreateMode, { en: string; zh: string }> = {
  ticket:      { en: 'Manual Ticket',  zh: '手动工单' },
  ticket_id:   { en: 'Ticket ID',      zh: '工单 ID 查询' },
  alert_event: { en: 'Alert Event',    zh: '告警事件' },
};

export function RunCreatePage() {
  const navigate = useNavigate();
  const { t, locale } = useI18n();
  const isCN = locale === 'zh-CN';

  const [mode, setMode] = useState<CreateMode>('ticket');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ticket mode fields
  const [ticketForm, setTicketForm] = useState({
    ticket_id: '',
    title: '',
    description: '',
    service: '',
    env: 'prod',
    severity: 'P2',
  });

  // ticket_id mode fields
  const [lookupTicketId, setLookupTicketId] = useState('');

  // alert_event mode fields
  const [alertForm, setAlertForm] = useState({
    alert_name: '',
    service: '',
    env: 'prod',
    severity: 'P2',
    description: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let payload;

      if (mode === 'ticket') {
        const ticket: IncidentTicket = {
          ticket_id: ticketForm.ticket_id || `INC-${Date.now()}`,
          title: ticketForm.title,
          description: ticketForm.description,
          service: ticketForm.service,
          env: ticketForm.env,
          severity: ticketForm.severity,
          source: 'manual',
        };
        payload = { ticket };
      } else if (mode === 'ticket_id') {
        if (!lookupTicketId.trim()) {
          setError(isCN ? '请输入工单 ID' : 'Ticket ID is required');
          setLoading(false);
          return;
        }
        payload = { ticket_id: lookupTicketId.trim() };
      } else {
        if (!alertForm.alert_name.trim() || !alertForm.service.trim()) {
          setError(isCN ? '告警名称和服务名称为必填项' : 'Alert name and service are required');
          setLoading(false);
          return;
        }
        payload = {
          alert_event: {
            alert_name: alertForm.alert_name,
            service: alertForm.service,
            env: alertForm.env,
            severity: alertForm.severity,
            description: alertForm.description || undefined,
          },
        };
      }

      const result = await runs.createRun(payload);
      navigate(`/runs/${result.run_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('run.createFailed'));
    } finally {
      setLoading(false);
    }
  };

  const envOptions = (
    <>
      <option value="prod">{t('run.environments.prod')}</option>
      <option value="staging">{t('run.environments.staging')}</option>
      <option value="dev">{t('run.environments.dev')}</option>
    </>
  );

  const severityOptions = (
    <>
      <option value="P1">{t('run.severities.P1')}</option>
      <option value="P2">{t('run.severities.P2')}</option>
      <option value="P3">{t('run.severities.P3')}</option>
      <option value="P4">{t('run.severities.P4')}</option>
    </>
  );

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-6 font-heading">{t('run.create')}</h2>

      {/* Mode switcher */}
      <div className="flex gap-2 mb-6">
        {MODES.map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => { setMode(m); setError(null); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-fast cursor-pointer ${
              mode === m
                ? 'btn btn-primary'
                : 'btn btn-secondary'
            }`}
          >
            {isCN ? MODE_LABELS[m].zh : MODE_LABELS[m].en}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 p-4 rounded-lg status-critical">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="card p-6 space-y-6">

        {/* ── ticket mode ── */}
        {mode === 'ticket' && (
          <>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {t('run.ticketId')}
              </label>
              <input
                type="text"
                value={ticketForm.ticket_id}
                onChange={(e) => setTicketForm({ ...ticketForm, ticket_id: e.target.value })}
                className="input w-full"
                placeholder="INC-001"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {t('run.titleRequired')}
              </label>
              <input
                type="text"
                value={ticketForm.title}
                onChange={(e) => setTicketForm({ ...ticketForm, title: e.target.value })}
                className="input w-full"
                placeholder={isCN ? '服务降级' : 'Service degraded'}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {t('run.description')}
              </label>
              <textarea
                value={ticketForm.description}
                onChange={(e) => setTicketForm({ ...ticketForm, description: e.target.value })}
                rows={3}
                className="input w-full resize-none"
                placeholder={isCN ? '描述事件...' : 'Describe the incident...'}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-content-secondary mb-2">
                  {t('run.serviceRequired')}
                </label>
                <input
                  type="text"
                  value={ticketForm.service}
                  onChange={(e) => setTicketForm({ ...ticketForm, service: e.target.value })}
                  className="input w-full"
                  placeholder="api-gateway"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-content-secondary mb-2">
                  {t('run.environmentRequired')}
                </label>
                <select
                  value={ticketForm.env}
                  onChange={(e) => setTicketForm({ ...ticketForm, env: e.target.value })}
                  className="input w-full"
                >
                  {envOptions}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {t('run.severityRequired')}
              </label>
              <select
                value={ticketForm.severity}
                onChange={(e) => setTicketForm({ ...ticketForm, severity: e.target.value })}
                className="input w-full"
              >
                {severityOptions}
              </select>
            </div>
          </>
        )}

        {/* ── ticket_id mode ── */}
        {mode === 'ticket_id' && (
          <div>
            <label className="block text-sm font-medium text-content-secondary mb-2">
              {isCN ? '工单 ID' : 'Ticket ID'}
            </label>
            <input
              type="text"
              value={lookupTicketId}
              onChange={(e) => setLookupTicketId(e.target.value)}
              className="input w-full"
              placeholder="INC-001"
              required
            />
            <p className="mt-2 text-xs text-content-muted">
              {isCN
                ? '系统将自动从工单系统查询工单详情并创建处置流程'
                : 'The system will look up the ticket from the ticketing system and start a run'}
            </p>
          </div>
        )}

        {/* ── alert_event mode ── */}
        {mode === 'alert_event' && (
          <>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {isCN ? '告警名称 *' : 'Alert Name *'}
              </label>
              <input
                type="text"
                value={alertForm.alert_name}
                onChange={(e) => setAlertForm({ ...alertForm, alert_name: e.target.value })}
                className="input w-full"
                placeholder={isCN ? 'HighErrorRate' : 'HighErrorRate'}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {t('run.description')}
              </label>
              <textarea
                value={alertForm.description}
                onChange={(e) => setAlertForm({ ...alertForm, description: e.target.value })}
                rows={2}
                className="input w-full resize-none"
                placeholder={isCN ? '告警描述...' : 'Alert description...'}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-content-secondary mb-2">
                  {t('run.serviceRequired')}
                </label>
                <input
                  type="text"
                  value={alertForm.service}
                  onChange={(e) => setAlertForm({ ...alertForm, service: e.target.value })}
                  className="input w-full"
                  placeholder="api-gateway"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-content-secondary mb-2">
                  {t('run.environmentRequired')}
                </label>
                <select
                  value={alertForm.env}
                  onChange={(e) => setAlertForm({ ...alertForm, env: e.target.value })}
                  className="input w-full"
                >
                  {envOptions}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-content-secondary mb-2">
                {t('run.severityRequired')}
              </label>
              <select
                value={alertForm.severity}
                onChange={(e) => setAlertForm({ ...alertForm, severity: e.target.value })}
                className="input w-full"
              >
                {severityOptions}
              </select>
            </div>
          </>
        )}

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary w-full py-3 shadow-glow hover:shadow-lg cursor-pointer"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {t('run.creating')}
            </>
          ) : (
            t('run.create')
          )}
        </button>
      </form>
    </div>
  );
}
