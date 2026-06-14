import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { DatabaseService } from '../../database/database.service';
import axios from 'axios';

export type ChatMode = 'fast' | 'think' | 'expert';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface StreamOptions {
  modelId: number;
  messages: ChatMessage[];
  mode: ChatMode;
  onChunk: (chunk: string) => void;
  onReasoning?: (reasoning: string) => void;
  onDone: (fullText: string, reasoningText: string, tokensUsed: number) => void;
  onError: (err: Error) => void;
  // 用户自定义模型覆盖（优先级高于 DB 配置）
  userApiKey?: string;
  userBaseUrl?: string;
  userModelId?: string;
  /** 自定义系统提示词（覆盖 buildSystemPrompt(mode)，用于多模态等特殊场景） */
  customSystemPrompt?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// 提供商适配层
// ─────────────────────────────────────────────────────────────────────────────

interface BuildRequestOptions {
  messages: ChatMessage[];
  mode: ChatMode;
  model: any;         // DB 中的模型行
  userModelId?: string;
}

interface ParsedChunk {
  content?: string;
  reasoning?: string;
  tokens?: number;
}

interface ProviderAdapter {
  /** 构建发送给 AI 的请求体 */
  buildRequestBody(opts: BuildRequestOptions): Record<string, any>;
  /** 解析 SSE 流中的一个 JSON 块 */
  parseChunk(parsed: any): ParsedChunk;
}

/** 根据模式获取通用温度 & max_tokens */
function modeParams(mode: ChatMode) {
  return {
    temperature: mode === 'fast' ? 0.7 : mode === 'think' ? 0.3 : 0.5,
    max_tokens:  mode === 'fast' ? 2048 : mode === 'think' ? 8192 : 16384,
  };
}

// ── DeepSeek 适配器 ───────────────────────────────────────────────────────────
const deepseekAdapter: ProviderAdapter = {
  buildRequestBody({ messages, mode, model, userModelId }) {
    const isThink = mode === 'think';
    // 思考模式强制使用 deepseek-reasoner
    const finalModelId = userModelId || (isThink ? 'deepseek-reasoner' : model.model_id);
    return {
      model: finalModelId,
      messages,
      stream: true,
      ...modeParams(mode),
    };
  },
  parseChunk(parsed) {
    const delta = parsed.choices?.[0]?.delta || {};
    return {
      content:   delta.content,
      reasoning: delta.reasoning_content,
      tokens:    parsed.usage?.total_tokens,
    };
  },
};

// ── MiniMax 适配器 ────────────────────────────────────────────────────────────
const minimaxAdapter: ProviderAdapter = {
  buildRequestBody({ messages, mode, model, userModelId }) {
    return {
      model: userModelId || model.model_id,
      messages,
      stream: true,
      mask_sensitive_info: true,   // MiniMax 必填
      ...modeParams(mode),
    };
  },
  parseChunk(parsed) {
    const delta = parsed.choices?.[0]?.delta || {};
    return { content: delta.content, tokens: parsed.usage?.total_tokens };
  },
};

// ── Qwen(千问) 适配器 ─────────────────────────────────────────────────────────
const qwenAdapter: ProviderAdapter = {
  buildRequestBody({ messages, mode, model, userModelId }) {
    return {
      model: userModelId || model.model_id,
      messages,
      stream: true,
      stream_options: { include_usage: true },  // 千问需要此参数以返回 token 统计
      ...modeParams(mode),
    };
  },
  parseChunk(parsed) {
    const delta = parsed.choices?.[0]?.delta || {};
    return { content: delta.content, tokens: parsed.usage?.total_tokens };
  },
};

// ── 通用 OpenAI 兼容适配器（doubao / moonshot / openai / 自定义）────────────
const doubaoAdapter: ProviderAdapter = {
  buildRequestBody({ messages, mode, model, userModelId }) {
    return {
      model: userModelId || model.model_id,
      messages,
      stream: true,
      stream_options: { include_usage: true },
      ...modeParams(mode),
    };
  },
  parseChunk(parsed) {
    const delta = parsed.choices?.[0]?.delta || {};
    return { content: delta.content, tokens: parsed.usage?.total_tokens };
  },
};

const defaultAdapter: ProviderAdapter = {
  buildRequestBody({ messages, mode, model, userModelId }) {
    return {
      model: userModelId || model.model_id,
      messages,
      stream: true,
      ...modeParams(mode),
    };
  },
  parseChunk(parsed) {
    const delta = parsed.choices?.[0]?.delta || {};
    return { content: delta.content, tokens: parsed.usage?.total_tokens };
  },
};

/** 根据 provider 字符串选择适配器 */
function getAdapter(provider: string): ProviderAdapter {
  const map: Record<string, ProviderAdapter> = {
    deepseek: deepseekAdapter,
    minimax:  minimaxAdapter,
    qwen:     qwenAdapter,
    doubao:   doubaoAdapter,
  };
  return map[provider] ?? defaultAdapter;
}

// ─────────────────────────────────────────────────────────────────────────────
// AiService
// ─────────────────────────────────────────────────────────────────────────────

@Injectable()
export class AiService {
  private readonly logger = new Logger(AiService.name);

  constructor(
    private db: DatabaseService,
    private config: ConfigService,
  ) {}

  /** 从环境变量中获取 provider 对应的 API Key（兜底方案） */
  private getEnvApiKey(provider: string): string {
    const keyMap: Record<string, string> = {
      deepseek: 'DEEPSEEK_API_KEY',
      moonshot: 'MOONSHOT_API_KEY',
      doubao:   'DOUBAO_API_KEY',
      minimax:  'MINIMAX_API_KEY',
      qwen:     'QWEN_API_KEY',
    };
    const envKey = keyMap[provider];
    return envKey ? this.config.get(envKey, '') : '';
  }

  getAllModels() {
    return this.db.all('SELECT id, name, provider, model_id, base_url, enabled, supports_vision, supports_image_gen, supports_voice, supports_video, sort_order FROM ai_models ORDER BY sort_order ASC');
  }

  getEnabledModels() {
    return this.db.all('SELECT id, name, provider, model_id, base_url, enabled, supports_vision, supports_image_gen, supports_voice, supports_video, sort_order FROM ai_models WHERE enabled=1 ORDER BY sort_order ASC');
  }

  getModelById(id: number) {
    return this.db.get('SELECT * FROM ai_models WHERE id=?', [id]);
  }

  updateModel(id: number, data: any) {
    const fields: string[] = [];
    const values: any[] = [];
    const allowed = ['name', 'provider', 'model_id', 'api_key', 'base_url', 'enabled',
      'supports_vision', 'supports_image_gen', 'supports_voice', 'supports_video', 'sort_order'];
    for (const key of allowed) {
      if (data[key] !== undefined) {
        fields.push(`${key}=?`);
        values.push(data[key]);
      }
    }
    if (!fields.length) return this.getModelById(id);
    values.push(id);
    this.db.run(`UPDATE ai_models SET ${fields.join(',')} WHERE id=?`, values);
    return this.getModelById(id);
  }

  createModel(data: any) {
    const r = this.db.run(
      'INSERT INTO ai_models (name, provider, model_id, api_key, base_url, enabled, sort_order) VALUES (?,?,?,?,?,?,?)',
      [data.name, data.provider, data.model_id, data.api_key || null, data.base_url || null, data.enabled ?? 1, data.sort_order ?? 99],
    );
    return this.getModelById(r.lastInsertRowid as number);
  }

  deleteModel(id: number) {
    this.db.run('DELETE FROM ai_models WHERE id=?', [id]);
  }

  /** 图片生成（豆包 SeedDream 文生图 API） */
  async generateImage(prompt: string, modelId?: number): Promise<string> {
    let apiKey = '';
    let baseUrl = 'https://ark.cn-beijing.volces.com/api/v3';

    // 1. 优先：调用方明确传入 modelId
    if (modelId) {
      const m = this.getModelById(modelId) as any;
      if (m) {
        apiKey = m.api_key || this.getEnvApiKey(m.provider);
        if (m.base_url) baseUrl = m.base_url;
      }
    }

    // 2. 从 DB 找 supports_image_gen=1 的模型（获取 apiKey + model_id）
    const imgModel = this.db.get(
      "SELECT * FROM ai_models WHERE supports_image_gen=1 AND enabled=1 ORDER BY sort_order ASC LIMIT 1",
    ) as any;

    // imageModelId 优先级：环境变量 > DB 中 image_gen 专属模型 > 硬编码默认值
    const envImageModelId = this.config.get('DOUBAO_IMAGE_MODEL', '');
    let imageModelId: string;
    if (envImageModelId) {
      imageModelId = envImageModelId;
    } else if (imgModel) {
      imageModelId = imgModel.model_id;
      if (!apiKey) {
        apiKey = imgModel.api_key || this.getEnvApiKey(imgModel.provider);
        if (imgModel.base_url) baseUrl = imgModel.base_url;
      }
    } else {
      // 保底默认，如果没有任何配置则报配置错误
      imageModelId = 'doubao-seedream-3-0-t2i-250415';
    }

    // 3. apiKey 兜底：找任意 doubao 模型
    if (!apiKey) {
      const doubaoModel = this.db.get(
        "SELECT * FROM ai_models WHERE provider='doubao' AND enabled=1 ORDER BY sort_order ASC LIMIT 1",
      ) as any;
      if (doubaoModel) {
        apiKey = doubaoModel.api_key || this.getEnvApiKey('doubao');
        if (doubaoModel.base_url) baseUrl = doubaoModel.base_url;
      }
    }
    if (!apiKey) apiKey = this.getEnvApiKey('doubao');

    if (!apiKey) {
      throw new Error('未找到豆包 API Key，请在管理后台配置豆包模型或设置 DOUBAO_API_KEY 环境变量');
    }

    if (!imgModel && !envImageModelId) {
      throw new Error(
        `图片生成模型未配置，请选择以下任一方式：\n` +
        `① 在管理后台 → 模型管理，为文生图模型（如 doubao-seedream-4-5-t2i-xxxxxx 或 ep-xxx 端点）勾选「支持图片生成」\n` +
        `② 在 .env 中设置 DOUBAO_IMAGE_MODEL=你的模型ID\n\n` +
        `当前使用了旧默认值 ${imageModelId}，可能导致 404 错误`,
      );
    }

    this.logger.log(`图片生成请求 model=${imageModelId} prompt=${prompt.slice(0, 50)}`);

    try {
      const result = await axios.post(
        `${baseUrl}/images/generations`,
        // 注意：不传 response_format，火山引擎不支持该参数，会导致 400
        // size 使用 2048x2048（SeedDream-4.5 最小要求 3686400 像素，即 ≥1920×1920）
        { model: imageModelId, prompt, n: 1, size: '2048x2048' },
        {
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
          timeout: 120000,
        },
      );

      const imageData = result.data?.data?.[0];
      if (!imageData) throw new Error('图片生成失败，返回数据为空');

      // 如果已是 base64 直接返回
      if (imageData.b64_json) return `data:image/png;base64,${imageData.b64_json}`;

      if (imageData.url) {
        // 代理下载并转为 base64，避免客户端因 CORS 无法内联预览
        try {
          const imgRes = await axios.get(imageData.url, {
            responseType: 'arraybuffer',
            timeout: 60000,
            headers: { Accept: 'image/*' },
          });
          const mimeType = (imgRes.headers['content-type'] as string || '').split(';')[0].trim() || 'image/png';
          const base64 = Buffer.from(imgRes.data as Buffer).toString('base64');
          return `data:${mimeType};base64,${base64}`;
        } catch {
          // 代理失败则直接返回 URL（作为允尺）
          return imageData.url;
        }
      }

      throw new Error('图片生成失败，未返回图片 URL 或 base64 数据');
    } catch (err: any) {
      // 提取火山引擎返回的具体错误信息
      const apiErrMsg = err.response?.data?.error?.message
        || err.response?.data?.message
        || err.response?.data?.error
        || '';
      const status = err.response?.status;

      if (status === 404) {
        throw new Error(
          `图片生成模型不存在（404）：当前模型 ID 为 "${imageModelId}"\n` +
          `请在管理后台 → 模型管理配置正确的文生图模型，或在 .env 设置 DOUBAO_IMAGE_MODEL=正确模型ID`,
        );
      }
      if (status === 400) {
        throw new Error(
          `图片生成请求异常（400）${apiErrMsg ? '：' + apiErrMsg : ''}，模型 ID="${imageModelId}"`,
        );
      }
      throw err;
    }
  }

  /** 构建系统提示词，根据模式调整 */
  private buildSystemPrompt(mode: ChatMode): string {
    const prompts: Record<ChatMode, string> = {
      fast:   '你是一个高效的 AI 助手，请简洁、准确地回答问题。',
      think:  '你是一个深度思考的 AI 助手，请先分析问题，然后给出详细、有逻辑的回答。对于复杂问题，请展示你的推理过程。',
      expert: '你是一个各领域的专家 AI 助手，具备深厚的专业知识。请给出专业、全面、深度的回答，包含相关技术细节和最佳实践。',
    };
    return prompts[mode];
  }

  /** 流式调用 AI 接口（兼容 OpenAI 格式，通过适配器支持多提供商） */
  async streamChat(options: StreamOptions): Promise<void> {
    const { modelId, messages, mode, onChunk, onReasoning, onDone, onError,
      userApiKey, userBaseUrl, userModelId, customSystemPrompt } = options;

    // 优先使用用户自定义凭据；否则从 DB 读取模型配置
    let model: any = null;
    if (!userApiKey) {
      model = this.getModelById(modelId) as any;
      if (!model) { onError(new Error('模型不存在')); return; }

      // DB 中 api_key 为空时，从环境变量兜底读取
      if (!model.api_key) {
        const envKey = this.getEnvApiKey(model.provider);
        if (envKey) {
          model = { ...model, api_key: envKey };
          this.logger.log(`模型 "${model.name}" 使用环境变量中的 API Key`);
        } else {
          onError(new Error(`模型 "${model.name}" 未配置 API Key，请在管理后台或 .env 中填写`));
          return;
        }
      }
    }

    const systemPrompt = customSystemPrompt ?? this.buildSystemPrompt(mode);
    const allMessages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      ...messages,
    ];

    // 选择适配器并构建请求体
    const provider = model?.provider ?? 'default';
    const adapter  = getAdapter(provider);
    const requestBody = adapter.buildRequestBody({ messages: allMessages, mode, model, userModelId });

    const baseUrl = userBaseUrl || model?.base_url || 'https://api.openai.com/v1';
    const apiKey  = userApiKey  || model?.api_key;

    // 请求前输出调试信息，方便排查
    this.logger.log(`发起 AI 请求 [${provider}] model=${requestBody.model} url=${baseUrl}/chat/completions`);

    try {
      const response = await axios.post(
        `${baseUrl}/chat/completions`,
        requestBody,
        {
          headers: {
            'Content-Type':  'application/json',
            Authorization:   `Bearer ${apiKey}`,
          },
          responseType: 'stream',
          timeout: 120000,
        },
      );

      let fullText     = '';
      let reasoningText = '';
      let tokensUsed   = 0;
      let buffer       = '';

      // 不活跃超时：60s 无数据则触发错误（防止豆包等模型沉默无响应）
      let inactivityTimer: ReturnType<typeof setTimeout> | null = null;
      const INACTIVITY_TIMEOUT = 90_000; // 90s
      const resetTimer = () => {
        if (inactivityTimer) clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(() => {
          response.data.destroy();
          onError(new Error(`AI 服务超时（90s 无数据），请重试或检查网络`));
        }, INACTIVITY_TIMEOUT);
      };
      resetTimer();

      response.data.on('data', (chunk: Buffer) => {
        resetTimer(); // 每收到数据就重置超时
        buffer += chunk.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data: ')) continue;
          const data = trimmed.slice(6);
          if (data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            const { content, reasoning, tokens } = adapter.parseChunk(parsed);

            if (reasoning) {
              reasoningText += reasoning;
              onReasoning?.(reasoning);
            }
            if (content) {
              fullText += content;
              onChunk(content);
            }
            if (tokens) tokensUsed = tokens;
          } catch {
            // 忽略 JSON 解析错误
          }
        }
      });

      response.data.on('end', () => {
        if (inactivityTimer) clearTimeout(inactivityTimer);
        if (!fullText && !reasoningText) {
          // 流结束但无内容：可能被模型内部错误拦截，不应默默显示空气泡
          onError(new Error('模型返回了空响应，请重试（可能是订阅配额不足或模型内部错误）'));
        } else {
          onDone(fullText, reasoningText, tokensUsed);
        }
      });
      response.data.on('error', (err: Error) => {
        if (inactivityTimer) clearTimeout(inactivityTimer);
        onError(err);
      });

    } catch (err: any) {
      const status = err.response?.status;
      let msg = err.message;

      // 尝试读取火山引擎返回的具体错误信息
      let apiErrorDetail = '';
      if (err.response?.data) {
        try {
          const chunks: Buffer[] = [];
          for await (const chunk of err.response.data) {
            chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
          }
          const body = Buffer.concat(chunks).toString();
          const json = JSON.parse(body);
          apiErrorDetail = json?.error?.message || json?.message || '';
        } catch { /* 忽略解析错误 */ }
      }

      if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED' || err.code === 'ETIMEDOUT') {
        msg = `无法连接到 ${provider} API 服务（${err.code}）\n请检查：服务器是否能访问外网、是否需要配置 HTTP 代理。目标域名：${(err as any).hostname || '未知'}`;
      } else if (status === 401 || status === 403) {
        msg = `API Key 无效或无权限 (${status})，请检查 API Key 配置`;
      } else if (status === 404) {
        if (provider === 'doubao') {
          msg = apiErrorDetail
            ? `豆包 API 错误 (404): ${apiErrorDetail}`
            : `模型 ID "${requestBody.model}" 不存在\n火山引擎支持的格式示例：\n  • 直接模型：doubao-pro-32k、doubao-seed-1-6-251015、doubao-1-5-pro-32k\n  • 配置的推理接入点：ep-xxxxxxxxxx（在火山引擎控制台创建）\n请到管理后台更新模型的 model_id 字段`;
        } else {
          msg = apiErrorDetail || `API 端点不存在 (404)，请检查 base_url 和模型 ID 配置`;
        }
      } else if (status === 429) {
        msg = `API 请求过于频繁 (429)，请稍后重试`;
      } else if (status >= 500) {
        msg = apiErrorDetail || `AI 服务端错误 (${status})，请稍后重试`;
      } else if (apiErrorDetail) {
        msg = apiErrorDetail;
      }

      this.logger.error(`AI 请求失败 [${provider}] model=${requestBody.model}: ${err.message}`);
      onError(new Error(msg));
    }
  }
}
