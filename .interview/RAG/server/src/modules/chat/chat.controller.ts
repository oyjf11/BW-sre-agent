import {
  Controller, Get, Post, Patch, Delete,
  Param, Body, Req, Res, Query,
} from '@nestjs/common';
import type { Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { ChatService } from './chat.service';
import { AiService } from '../ai/ai.service';
import { UserService } from '../user/user.service';
import { TicketService, analyzeEmotion } from '../ticket/ticket.service';
import { RetrievalService } from '../knowledge/retrieval.service';
import { Public } from '../auth/jwt.guard';
import { getWebDesignSystemPrompt, getCareerSystemPrompt } from './design-prompts';

@Controller('api')
export class ChatController {
  constructor(
    private chatService: ChatService,
    private aiService: AiService,
    private userService: UserService,
    private ticketService: TicketService,
    private retrievalService: RetrievalService,
  ) {}

  // ──────── 对话管理 ────────

  @Get('conversations')
  getConversations(@Req() req: any) {
    return this.chatService.getConversations(req.user.sub);
  }

  @Post('conversations')
  createConversation(@Req() req: any, @Body() body: any) {
    return this.chatService.createConversation(
      req.user.sub,
      body.model_id,
      body.mode || 'fast',
      body.title || '新对话',
    );
  }

  @Patch('conversations/:id')
  updateConversation(@Req() req: any, @Param('id') id: string, @Body() body: any) {
    return this.chatService.updateConversation(id, req.user.sub, body);
  }

  @Delete('conversations/:id')
  deleteConversation(@Req() req: any, @Param('id') id: string) {
    this.chatService.deleteConversation(id, req.user.sub);
    return { ok: true };
  }

  @Get('conversations/:id/messages')
  getMessages(@Req() req: any, @Param('id') id: string) {
    const conv = this.chatService.getConversationById(id, req.user.sub);
    if (!conv) return { error: '对话不存在' };
    return this.chatService.getMessages(id);
  }

  // ──────── AI 模型 ────────

  @Public()
  @Get('models')
  getModels() {
    return this.aiService.getEnabledModels();
  }

  @Get('admin/models')
  getAdminModels(@Req() req: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.aiService.getAllModels();
  }

  @Post('admin/models')
  createModel(@Req() req: any, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.aiService.createModel(body);
  }

  @Patch('admin/models/:id')
  updateModel(@Req() req: any, @Param('id') id: string, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.aiService.updateModel(Number(id), body);
  }

  @Delete('admin/models/:id')
  deleteModel(@Req() req: any, @Param('id') id: string) {
    if (!req.user.isAdmin) return { error: '无权限' };
    this.aiService.deleteModel(Number(id));
    return { ok: true };
  }

  // ──────── SSE 流式对话 ────────

  @Post('chat/completions')
  async chatCompletions(@Req() req: any, @Res() res: Response, @Body() body: any) {
    const userId: number = req.user.sub;
    const { conversation_id, model_id, mode = 'fast', message, attachment_content,
      user_api_key, user_base_url, user_model_id, content_type = 'text',
      regenerate = false, kb_ids = [] } = body;

    if (!conversation_id || (!message && !regenerate)) {
      return res.status(400).json({ error: '缺少必要参数' });
    }

    // 获取对话
    const conv = this.chatService.getConversationById(conversation_id, userId);
    if (!conv) return res.status(404).json({ error: '对话不存在' });

    if (regenerate) {
      // 重新生成：删除最后一条 assistant 消息，不保存新的用户消息
      this.chatService.deleteLastAssistantMessage(conversation_id);
    } else {
      // 如果有附件内容，拼接到用户消息
      const fullUserMessage = attachment_content
        ? `${message}\n\n[附件内容]\n${attachment_content}`
        : message;
      // 保存用户消息
      this.chatService.addMessage(conversation_id, 'user', fullUserMessage);
    }

    // 自动更新标题
    const messages = this.chatService.getMessages(conversation_id) as any[];
    if (!regenerate && messages.length <= 1) {
      this.chatService.autoGenerateTitle(conversation_id);
    }

    // 构建历史消息（最多取最近20条）
    const historyMessages = messages.slice(-20).map((m: any) => ({
      role: m.role as 'user' | 'assistant' | 'system',
      content: m.content,
    }));

    // RAG：若指定了知识库，检索相关内容并注入系统提示
    let ragSources: Array<{ filename: string }> = [];
    if (Array.isArray(kb_ids) && kb_ids.length > 0 && message) {
      try {
        const chunks = await this.retrievalService.retrieve(
          message,
          kb_ids.map(Number).filter((n: number) => !isNaN(n)),
          5,
        );
        if (chunks.length > 0) {
          ragSources = [...new Map(
            chunks.filter((c) => c.filename).map((c) => [c.filename, { filename: c.filename! }])
          ).values()];
          const refs = chunks
            .map((c, i) => {
              const src = c.filename ? ` (来源: ${c.filename})` : '';
              return `[${i + 1}]${src}\n${c.content}`;
            })
            .join('\n\n');
          const ragPrompt = `## 知识库参考资料\n\n${refs}\n\n请优先参考以上内容回答用户问题。如果参考资料中没有相关信息，可基于自身知识回答，并说明信息来源。`;
          historyMessages.unshift({ role: 'system' as const, content: ragPrompt });
        }
      } catch (err: any) {
        // RAG 失败不阻断对话，记录日志即可
        console.warn(`[RAG] 检索失败: ${err.message}`);
      }
    }

    // 特殊功能：注入系统提示词
    if (content_type === 'webdesign') {
      historyMessages.unshift({ role: 'system' as const, content: getWebDesignSystemPrompt() });
    } else if (content_type === 'career') {
      historyMessages.unshift({ role: 'system' as const, content: getCareerSystemPrompt() });
    }

    // 网页设计模式强制使用 expert 档位（max_tokens=16384），避免 HTML 被截断
    const effectiveMode = content_type === 'webdesign' ? 'expert' : mode;

    // 设置 SSE 响应头
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders();

    const writeEvent = (event: string, data: any) => {
      res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
    };

    // RAG 命中时先推送来源信息
    if (ragSources.length > 0) {
      writeEvent('rag_sources', { sources: ragSources });
    }

    const targetModelId = model_id || (conv as any).model_id || 1;

    await this.aiService.streamChat({
      modelId: Number(targetModelId),
      messages: historyMessages,
      mode: effectiveMode,
      userApiKey: user_api_key,
      userBaseUrl: user_base_url,
      userModelId: user_model_id,
      onChunk: (chunk) => {
        writeEvent('chunk', { content: chunk });
      },
      onReasoning: (reasoning) => {
        writeEvent('reasoning', { content: reasoning });
      },
      onDone: (fullText, reasoningText, tokensUsed) => {
        // 保存 AI 消息
        const model = this.aiService.getModelById(Number(targetModelId)) as any;
        this.chatService.addMessage(conversation_id, 'assistant', fullText, {
          reasoning_content: reasoningText || undefined,
          model_used: model?.name,
          tokens_used: tokensUsed,
          rag_sources: ragSources.length > 0 ? JSON.stringify(ragSources) : undefined,
        });
        // 扣减 token
        this.userService.deductTokens(userId, tokensUsed);

        // 情绪识别：分析用户最后一条消息
        const allMsgs = this.chatService.getMessages(conversation_id) as any[];
        const lastUserMsg = [...allMsgs].reverse().find((m: any) => m.role === 'user');
        const emotion = analyzeEmotion(lastUserMsg?.content || '');
        let needsHuman = emotion.needsHuman;

        // 负面情绪或人工需求：自动生成工单
        if (emotion.negative) {
          try {
            this.ticketService.createTicket({
              userId,
              conversationId: conversation_id,
              lastUserMessage: lastUserMsg?.content?.slice(0, 500),
              emotion: emotion.emotion,
              needsHuman: emotion.needsHuman,
            });
          } catch { /* 工单创建失败不阻断主流程 */ }
        }

        writeEvent('done', { fullText, reasoningText, tokensUsed, needsHuman });
        res.end();
      },
      onError: (err) => {
        writeEvent('error', { message: err.message });
        res.end();
      },
    });
  }

  // ──────── 图片生成 ────────

  @Post('images/generate')
  async generateImage(@Req() req: any, @Body() body: any) {
    const { prompt, model_id } = body;
    if (!prompt?.trim()) return { error: '请输入图片描述' };

    // 图片生成次数限制：管理员无限制，免费=0张，体验券=4张，源码版=4张
    const userId = req.user.sub;
    const user = this.userService.findById(userId) as any;
    const isAdmin = !!user?.is_admin;
    const planLimits: Record<string, number> = { experience: 4, source: 4 };
    const planType = user?.plan_type || '';
    const imageLimit = isAdmin ? 99 : (planLimits[planType] ?? 0);
    const imagesUsed = user?.images_used ?? 0;

    if (!isAdmin && imageLimit === 0) {
      return {
        error: '图片生成为付费功能：体验券（¥9.9）可免费4张，源码版（¥499）可免费4张',
        error_code: 'IMAGE_LIMIT_EXCEEDED',
        need_upgrade: true,
      };
    }

    if (!isAdmin && imagesUsed >= imageLimit) {
      const canUpgrade = planType === 'experience';
      return {
        error: `图片生成次数已用完（${imagesUsed}/${imageLimit}）${
          canUpgrade ? '，可联系作者或在左侧配置自己的模型 AK 使用' : '，如需更多请联系作者'
        }`,
        error_code: 'IMAGE_LIMIT_EXCEEDED',
        need_upgrade: canUpgrade,
      };
    }

    try {
      const imageUrl = await this.aiService.generateImage(prompt.trim(), model_id ? Number(model_id) : undefined);
      if (!isAdmin) this.userService.incrementImagesUsed(userId);
      return { imageUrl, images_used: isAdmin ? 0 : imagesUsed + 1, image_limit: imageLimit };
    } catch (err: any) {
      return { error: err.message || '图片生成失败' };
    }
  }
}
