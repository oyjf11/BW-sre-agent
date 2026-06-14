import { Controller, Post, Req, Res, Body } from '@nestjs/common';
import type { Response } from 'express';
import { MultimodalService } from './multimodal.service';
import { UserService } from '../user/user.service';
import { ChatService } from '../chat/chat.service';

@Controller('api')
export class MultimodalController {
  constructor(
    private readonly multimodalService: MultimodalService,
    private readonly userService: UserService,
    private readonly chatService: ChatService,
  ) {}

  /**
   * POST /api/multimodal/generate
   * SSE 端点：多Agent协作生成图文图表并茂的多模态内容
   *
   * 事件协议：
   *   event: plan        { summary, imageCount, chartCount }     // 意图分析结果
   *   event: chunk       { content }                             // 流式文字（含mermaid块）
   *   event: image_start { index, prompt }                       // 图片生成开始（占位）
   *   event: image       { index, url }                          // 图片生成完成
   *   event: done        {}                                      // 全部完成
   *   event: error       { message }                             // 错误
   */
  @Post('multimodal/generate')
  async generate(@Req() req: any, @Res() res: Response, @Body() body: any) {
    const userId: number = req.user.sub;
    const { message, conversation_id, attachment_content, model_id } = body;

    if (!message?.trim() || !conversation_id) {
      return res.status(400).json({ error: '缺少必要参数：message 和 conversation_id' });
    }

    // 验证对话归属
    const conv = this.chatService.getConversationById(conversation_id, userId);
    if (!conv) return res.status(404).json({ error: '对话不存在' });

    // 图片配额判断：管理员不受限制，其他用户按套餐
    const user = this.userService.findById(userId) as any;
    const isAdmin = !!user?.is_admin;
    const planLimits: Record<string, number> = { experience: 4, source: 4 };
    const planType = user?.plan_type || '';
    const imageLimit = isAdmin ? 99 : (planLimits[planType] ?? 0);
    const imagesUsed = user?.images_used ?? 0;
    const canGenerateImages = imageLimit > 0 && (isAdmin || imagesUsed < imageLimit);
    const remainingImages = isAdmin ? 99 : Math.max(0, imageLimit - imagesUsed);

    // 保存用户消息
    const fullUserMessage = attachment_content
      ? `${message}\n\n[附件内容]\n${attachment_content}`
      : message;
    this.chatService.addMessage(conversation_id, 'user', fullUserMessage);

    // 自动更新对话标题（首条消息时）
    const messages = this.chatService.getMessages(conversation_id) as any[];
    if (messages.length <= 1) {
      this.chatService.autoGenerateTitle(conversation_id);
    }

    const targetModelId = model_id || (conv as any).model_id || 1;

    // 建立 SSE 连接
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders();

    const writeEvent = (event: string, data: any) => {
      if (!res.writableEnded) {
        res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
      }
    };

    let fullContent = '';

    try {
      // ══════════════════════════════════════════════════════════════
      // Agent 1: 意图分析 — 分析用户意图，生成结构化执行计划
      // ══════════════════════════════════════════════════════════════
      const plan = await this.multimodalService.analyzeIntent(
        message,
        targetModelId,
        attachment_content,
      );

      // 无配额时不生成图片，保留图表和文字
      const effectiveImagePrompts = canGenerateImages
        ? plan.imagePrompts.slice(0, remainingImages)
        : [];
      const effectivePlan = { ...plan, imagePrompts: effectiveImagePrompts };

      writeEvent('plan', {
        summary: effectivePlan.summary,
        imageCount: effectiveImagePrompts.length,
        chartCount: effectivePlan.chartSpecs.length,
        canGenerateImages,
      });

      // ══════════════════════════════════════════════════════════════
      // Agent 2: 内容生成 — 流式输出含 Mermaid 图表 + 图片占位符的 Markdown
      // ══════════════════════════════════════════════════════════════
      await this.multimodalService.generateContent(
        effectivePlan,
        message,
        targetModelId,
        {
          onChunk: (chunk) => {
            fullContent += chunk;
            writeEvent('chunk', { content: chunk });
          },
          onDone: () => { /* 内容生成完毕，继续图片阶段 */ },
          onError: (err) => writeEvent('error', { message: err.message }),
        },
      );

      // ══════════════════════════════════════════════════════════════
      // Agent 3: 图片生成 — 扫描 fullContent 中实际存在的 [IMAGE_N] 占位符
      // 而不是仅依赖 Agent1 的计划，避免 Agent2 擅自写入占位符却永远不替换的问题
      // ══════════════════════════════════════════════════════════════

      // 扫描 fullContent 找出全部 [IMAGE_N] 占位符
      const foundPlaceholders = new Set<number>();
      const placeholderRe = /\[IMAGE_(\d+)\]/g;
      let phMatch: RegExpExecArray | null;
      // eslint-disable-next-line no-cond-assign
      while ((phMatch = placeholderRe.exec(fullContent)) !== null) {
        foundPlaceholders.add(parseInt(phMatch[1], 10));
      }

      // 图片结果映射： index => url（空字符串表示生成失败）
      const imageResults = new Map<number, string>();

      if (foundPlaceholders.size > 0) {
        const sortedIndices = Array.from(foundPlaceholders).sort((a, b) => a - b);

        const imagePromises = sortedIndices.map(async (index) => {
          // 使用 Agent1 规划的提示词；如果超出范围则用通用提示词
          const prompt = effectiveImagePrompts[index]
            ?? `high quality illustration for: ${plan.summary}`;

          if (canGenerateImages) {
            writeEvent('image_start', { index, prompt });
            try {
              const url = await this.multimodalService.generateImage(prompt);
              imageResults.set(index, url);
              writeEvent('image', { index, url });
              if (!isAdmin) this.userService.incrementImagesUsed(userId);
            } catch (err: any) {
              imageResults.set(index, '');
              writeEvent('image', { index, url: '', error: err.message });
            }
          } else {
            // 无配额：发送空 url，让前端移除占位符
            imageResults.set(index, '');
            writeEvent('image', { index, url: '' });
          }
        });

        await Promise.all(imagePromises);
      }

      // 存库前用真实 URL 替换占位符，避免刷新页面后再次出现 [IMAGE_N]
      let savedContent = fullContent;
      imageResults.forEach((url, index) => {
        const replacement = url
          ? `![\u751f\u6210\u56fe\u7247${index + 1}](${url})`
          : `> \u26a0\ufe0f \u56fe\u7247${index + 1}\u751f\u6210\u5931\u8d25`;
        savedContent = savedContent.replace(`[IMAGE_${index}]`, replacement);
      });
      // 删除其余未处理的占位符（防御）
      savedContent = savedContent.replace(/\[IMAGE_\d+\]/g, '');

      // 保存最终消息到数据库
      this.chatService.addMessage(conversation_id, 'assistant', savedContent, {
        content_type: 'multimodal',
      });

      writeEvent('done', {});
    } catch (err: any) {
      writeEvent('error', { message: err.message || '多模态生成失败，请重试' });
    } finally {
      res.end();
    }
  }
}
