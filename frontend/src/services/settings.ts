import { api } from './api';
import type { LlmConfig } from '../types';

export const settings = {
  getLlmConfig: () =>
    api.get<LlmConfig>('/settings/llm'),

  updateLlmConfig: (config: LlmConfig) =>
    api.put<{ status: string; message: string; provider: string }>('/settings/llm', config),
};
