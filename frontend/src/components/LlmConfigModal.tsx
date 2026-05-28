import { useState, useEffect } from 'react';
import { settings } from '../services/settings';
import type { LlmConfig } from '../types';

interface Props {
  open: boolean;
  onClose: () => void;
}

export function LlmConfigModal({ open, onClose }: Props) {
  const [provider, setProvider] = useState('minimax');
  const [openaiKey, setOpenaiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-4o');
  const [minimaxKey, setMinimaxKey] = useState('');
  const [minimaxGroupId, setMinimaxGroupId] = useState('');
  const [minimaxModel, setMinimaxModel] = useState('abab6.5s-chat');
  const [deepseekKey, setDeepseekKey] = useState('');
  const [deepseekModel, setDeepseekModel] = useState('deepseek-chat');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!open) return;
    const loadConfig = async () => {
      try {
        const config = await settings.getLlmConfig();
        setProvider(config.provider || 'minimax');
        setOpenaiKey(config.openai_api_key || '');
        setOpenaiModel(config.openai_model || 'gpt-4o');
        setMinimaxKey(config.minimax_api_key || '');
        setMinimaxGroupId(config.minimax_group_id || '');
        setMinimaxModel(config.minimax_model || 'abab6.5s-chat');
        setDeepseekKey(config.deepseek_api_key || '');
        setDeepseekModel(config.deepseek_model || 'deepseek-chat');
      } catch (e) {
        console.error('Failed to load LLM config:', e);
      }
    };
    loadConfig();
  }, [open]);

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    try {
      const config: LlmConfig = {
        provider,
        openai_api_key: openaiKey,
        openai_model: openaiModel,
        minimax_api_key: minimaxKey,
        minimax_group_id: minimaxGroupId,
        minimax_model: minimaxModel,
        deepseek_api_key: deepseekKey,
        deepseek_model: deepseekModel,
      };
      const result = await settings.updateLlmConfig(config);
      localStorage.setItem('opspilot_llm_configured', '1');
      setMessage(result.message || '配置已保存，热更新生效');
      setTimeout(() => {
        setMessage('');
        onClose();
      }, 1500);
    } catch (e: any) {
      setMessage(e.detail || e.message || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0,0,0,0.4)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="rounded-xl shadow-xl w-full max-w-lg mx-4"
        style={{
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-xl)',
        }}
      >
        <div
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: '1px solid var(--border-subtle)' }}
        >
          <h2 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
            LLM 大模型配置
          </h2>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-md transition-fast cursor-pointer"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
              大模型平台
            </label>
            <div className="flex gap-3">
              {[
                { value: 'minimax', label: 'MiniMax' },
                { value: 'deepseek', label: 'DeepSeek' },
                { value: 'openai', label: 'OpenAI' },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setProvider(opt.value)}
                  className="flex-1 px-4 py-2.5 text-sm rounded-lg border font-medium transition-fast cursor-pointer"
                  style={{
                    borderColor: provider === opt.value ? 'var(--accent-primary)' : 'var(--border-default)',
                    backgroundColor: provider === opt.value ? 'var(--accent-muted)' : 'transparent',
                    color: provider === opt.value ? 'var(--text-primary)' : 'var(--text-secondary)',
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {provider === 'openai' && (
            <>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  className="input w-full"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  Model
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={openaiModel}
                  onChange={(e) => setOpenaiModel(e.target.value)}
                  placeholder="gpt-4o"
                />
              </div>
            </>
          )}

          {provider === 'minimax' && (
            <>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  MiniMax API Key
                </label>
                <input
                  type="password"
                  className="input w-full"
                  value={minimaxKey}
                  onChange={(e) => setMinimaxKey(e.target.value)}
                  placeholder="sk-api-..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  Group ID
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={minimaxGroupId}
                  onChange={(e) => setMinimaxGroupId(e.target.value)}
                  placeholder="agent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  Model
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={minimaxModel}
                  onChange={(e) => setMinimaxModel(e.target.value)}
                  placeholder="MiniMax-M2.5"
                />
              </div>
            </>
          )}

          {provider === 'deepseek' && (
            <>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  DeepSeek API Key
                </label>
                <input
                  type="password"
                  className="input w-full"
                  value={deepseekKey}
                  onChange={(e) => setDeepseekKey(e.target.value)}
                  placeholder="sk-..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  Model
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={deepseekModel}
                  onChange={(e) => setDeepseekModel(e.target.value)}
                  placeholder="deepseek-chat"
                />
              </div>
            </>
          )}

          {message && (
            <div
              className="px-4 py-2.5 rounded-lg text-sm"
              style={{
                backgroundColor: message.includes('失败') ? 'var(--status-critical-bg)' : 'var(--status-success-bg)',
                color: message.includes('失败') ? 'var(--status-critical)' : 'var(--status-success)',
              }}
            >
              {message}
            </div>
          )}
        </div>

        <div
          className="flex justify-end gap-3 px-6 py-4"
          style={{ borderTop: '1px solid var(--border-subtle)' }}
        >
          <button onClick={onClose} className="btn btn-secondary" disabled={saving}>
            取消
          </button>
          <button onClick={handleSave} className="btn btn-primary" disabled={saving}>
            {saving ? '保存中...' : '保存并生效'}
          </button>
        </div>
      </div>
    </div>
  );
}
