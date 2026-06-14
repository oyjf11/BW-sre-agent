import axios from 'axios';
import { API_BASE } from '../constants';

const http = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// 请求拦截：自动加 Token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 响应拦截：统一错误处理
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.dispatchEvent(new Event('auth:logout'));
    }
    return Promise.reject(err.response?.data || err);
  },
);

export default http;

// ──────── Auth ────────
export const authApi = {
  getSsoQr: (redirectUri?: string) =>
    http.get('/api/auth/sso/qr', { params: { redirect_uri: redirectUri } }),
  pollSso: (state: string) =>
    http.get('/api/auth/sso/poll', { params: { state } }),
  verifySsoToken: (token: string) =>
    http.post('/api/auth/verify', { token }),
  getMe: () => http.get('/api/auth/me'),
  adminLogin: (username: string, password: string) =>
    http.post('/api/auth/admin/login', { username, password }),
};

// ──────── User ────────
export const userApi = {
  getProfile: () => http.get('/api/user/profile'),
  getUsers: (page = 1) => http.get('/api/admin/users', { params: { page } }),
  updateUser: (id: number, data: any) => http.patch(`/api/admin/users/${id}`, data),
};

// ──────── Conversations ────────
export const convApi = {
  list: () => http.get('/api/conversations'),
  create: (data: any) => http.post('/api/conversations', data),
  update: (id: string, data: any) => http.patch(`/api/conversations/${id}`, data),
  delete: (id: string) => http.delete(`/api/conversations/${id}`),
  getMessages: (id: string) => http.get(`/api/conversations/${id}/messages`),
};

// ──────── Models ────────
export const modelApi = {
  list: () => http.get('/api/models'),
  adminList: () => http.get('/api/admin/models'),
  create: (data: any) => http.post('/api/admin/models', data),
  update: (id: number, data: any) => http.patch(`/api/admin/models/${id}`, data),
  delete: (id: number) => http.delete(`/api/admin/models/${id}`),
};

// ──────── Files ────────
export const fileApi = {
  upload: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return http.post('/api/files/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => http.get('/api/files'),
  delete: (id: number) => http.delete(`/api/files/${id}`),
  /** 下载文件：带鉴权获取原始文件并触发浏览器下载 */
  download: async (id: number, filename: string): Promise<void> => {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE}/api/files/${id}/download`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('下载失败');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};

// ──────── Image Generation ────────
export const imageApi = {
  // 图片生成耗时60-120s，录用独立超时（视为覆盖默认30s）
  generate: (prompt: string, modelId?: number) =>
    http.post('/api/images/generate', { prompt, model_id: modelId }, { timeout: 130000 }),
};

// ──────── Payment ────────
export const payApi = {
  getPlans: () => http.get('/api/pay/plans'),
  createNative: (plan: string) => http.post('/api/pay/native', { plan }),
  createJsapi: (plan: string) => http.post('/api/pay/jsapi', { plan }),
  queryStatus: (orderNo: string) => http.get(`/api/pay/status/${orderNo}`),
  getMyOrders: () => http.get('/api/pay/orders/mine'),
  getAdminOrders: (page = 1) => http.get('/api/pay/orders/admin', { params: { page } }),
};

// ──────── 工单 (Tickets) ────────
export const ticketApi = {
  /** 管理员获取所有工单 */
  getAdminTickets: (page = 1) => http.get('/api/admin/tickets', { params: { page } }),
  /** 管理员更新工单状态或备注 */
  updateTicket: (id: number, data: { status?: string; admin_notes?: string }) =>
    http.patch(`/api/admin/tickets/${id}`, data),
};

// ──────── RAG 知识库 ────────
export const knowledgeApi = {
  /** 知识库列表（公共 + 用户自己的） */
  listBases: () => http.get('/api/knowledge/bases'),
  /** 创建知识库 */
  createBase: (data: { name: string; description?: string; is_public?: boolean }) =>
    http.post('/api/knowledge/bases', data),
  /** 更新知识库 */
  updateBase: (id: number, data: { name?: string; description?: string; is_public?: boolean }) =>
    http.put(`/api/knowledge/bases/${id}`, data),
  /** 删除知识库 */
  deleteBase: (id: number) => http.delete(`/api/knowledge/bases/${id}`),
  /** 文档列表 */
  listDocuments: (kbId: number) => http.get(`/api/knowledge/bases/${kbId}/documents`),
  /** 索引状态（pending/indexing/ready/failed 数量） */
  getStatus: (kbId: number) => http.get(`/api/knowledge/bases/${kbId}/status`),
  /** 上传并索引文档 */
  uploadDocument: (kbId: number, file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return http.post(`/api/knowledge/bases/${kbId}/documents`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 0, // 大文件上传不限时
    });
  },
  /** 删除文档 */
  deleteDocument: (kbId: number, docId: number) =>
    http.delete(`/api/knowledge/bases/${kbId}/documents/${docId}`),
  /** 获取文档分块列表 */
  listChunks: (kbId: number, docId: number) =>
    http.get(`/api/knowledge/bases/${kbId}/documents/${docId}/chunks`),
  /** 获取文档预览内容 */
  getPreview: (kbId: number, docId: number) =>
    http.get(`/api/knowledge/bases/${kbId}/documents/${docId}/preview`),
  /** 获取数据分析概览 */
  getAnalytics: () => http.get('/api/knowledge/analytics'),
};

// ──────── SSE 流式对话 ────────
export function streamChat(
  body: {
    conversation_id: string;
    model_id?: number;
    mode?: string;
    message: string;
    content_type?: string;
    attachment_content?: string;
    // 用户自定义模型覆盖
    user_model_id?: string;
    user_base_url?: string;
    user_api_key?: string;
    /** 重新生成：跳过保存用户消息，删除上一条 assistant 消息 */
    regenerate?: boolean;
    /** RAG：要检索的知识库 id 列表 */
    kb_ids?: number[];
  },
  handlers: {
    onChunk: (text: string) => void;
    onReasoning?: (text: string) => void;
    onSources?: (sources: Array<{ filename: string }>) => void;
    onDone?: (data: any) => void;
    onError?: (err: string) => void;
  },
): () => void {
  const token = localStorage.getItem('access_token');
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}/api/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!res.ok) {
        handlers.onError?.(`请求失败: ${res.status}`);
        return;
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = 'chunk';
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) { currentEvent = 'chunk'; continue; }
          if (trimmed.startsWith('event: ')) {
            currentEvent = trimmed.slice(7).trim();
            continue;
          }
          if (!trimmed.startsWith('data: ')) continue;

          try {
            const data = JSON.parse(trimmed.slice(6));
            if (currentEvent === 'chunk') {
              handlers.onChunk(data.content || '');
            } else if (currentEvent === 'reasoning') {
              handlers.onReasoning?.(data.content || '');
            } else if (currentEvent === 'rag_sources') {
              handlers.onSources?.(data.sources || []);
            } else if (currentEvent === 'done') {
              handlers.onDone?.(data);
            } else if (currentEvent === 'error') {
              handlers.onError?.(data.message || '');
            }
            currentEvent = 'chunk';
          } catch {
            // ignore
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        handlers.onError?.(err.message || '连接失败');
      }
    }
  })();

  return () => controller.abort();
}

// ──────── 多模态AI 流式生成 ────────
export interface MultimodalPlan {
  summary: string;
  imageCount: number;
  chartCount: number;
  canGenerateImages: boolean;
}

export function streamMultimodal(
  body: {
    conversation_id: string;
    message: string;
    model_id?: number;
    attachment_content?: string;
  },
  handlers: {
    onPlan: (plan: MultimodalPlan) => void;
    onChunk: (text: string) => void;
    onImageStart: (index: number, prompt: string) => void;
    onImage: (index: number, url: string) => void;
    onDone: () => void;
    onError: (err: string) => void;
  },
): () => void {
  const token = localStorage.getItem('access_token');
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}/api/multimodal/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      if (!res.ok) {
        handlers.onError(`请求失败: ${res.status}`);
        return;
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let currentEvent = 'chunk';
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) { currentEvent = 'chunk'; continue; }
          if (trimmed.startsWith('event: ')) {
            currentEvent = trimmed.slice(7).trim();
            continue;
          }
          if (!trimmed.startsWith('data: ')) continue;

          try {
            const data = JSON.parse(trimmed.slice(6));
            switch (currentEvent) {
              case 'plan':
                handlers.onPlan(data as MultimodalPlan);
                break;
              case 'chunk':
                handlers.onChunk(data.content || '');
                break;
              case 'image_start':
                handlers.onImageStart(data.index ?? 0, data.prompt || '');
                break;
              case 'image':
                handlers.onImage(data.index ?? 0, data.url || '');
                break;
              case 'done':
                handlers.onDone();
                break;
              case 'error':
                handlers.onError(data.message || '生成失败');
                break;
            }
            currentEvent = 'chunk';
          } catch {
            // ignore JSON parse errors
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        handlers.onError(err.message || '连接失败');
      }
    }
  })();

  return () => controller.abort();
}
