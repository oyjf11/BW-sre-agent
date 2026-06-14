import { Injectable, Logger } from '@nestjs/common';
import { AiService } from '../ai/ai.service';

export interface ChartSpec {
  title: string;
  type: 'flowchart' | 'pie' | 'sequence' | 'gantt' | 'mindmap' | string;
  description: string;
}

export interface IntentPlan {
  summary: string;
  imagePrompts: string[];
  chartSpecs: ChartSpec[];
}

@Injectable()
export class MultimodalService {
  private readonly logger = new Logger(MultimodalService.name);

  constructor(private readonly aiService: AiService) {}

  // ─── Agent 1: 意图分析 ─────────────────────────────────────────────────────
  // 分析用户意图，返回结构化生成计划（非流式，需要JSON）
  async analyzeIntent(
    message: string,
    modelId: number,
    attachmentContent?: string,
  ): Promise<IntentPlan> {
    const userContent = attachmentContent
      ? `${message}\n\n[附件内容]\n${attachmentContent}`
      : message;

    const systemPrompt = `你是一个多模态内容生成意图分析器。分析用户需求后，严格返回一个JSON对象（不含markdown代码块，不含其他文字）。

JSON格式如下：
{"summary":"中文简短描述将生成的内容","imagePrompts":["英文图片提示词1"],"chartSpecs":[{"title":"中文图表标题","type":"flowchart","description":"图表内容描述"}]}

规则：
- summary: 简短中文描述（20字以内）
- imagePrompts: 最多2个英文提示词。**如果用户希望内容视觉化、需要配图或提到了图片/插图/配图/当景图/展示图等，必须生成至少1个图片提示词**；纯文字分析或流程类需求可以设为[]
- chartSpecs: 1到3个图表，type只能是以下之一: flowchart / pie / sequence / gantt / mindmap`;

    return new Promise<IntentPlan>((resolve) => {
      let fullText = '';

      this.aiService.streamChat({
        modelId,
        messages: [{ role: 'user', content: userContent }],
        mode: 'fast',
        customSystemPrompt: systemPrompt,
        onChunk: (chunk) => { fullText += chunk; },
        onDone: () => {
          try {
            const jsonMatch = fullText.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              const plan = JSON.parse(jsonMatch[0]) as IntentPlan;
              resolve({
                summary: plan.summary || '正在生成多模态内容',
                imagePrompts: (Array.isArray(plan.imagePrompts) ? plan.imagePrompts : []).slice(0, 2),
                chartSpecs: (Array.isArray(plan.chartSpecs) ? plan.chartSpecs : []).slice(0, 3),
              });
              return;
            }
          } catch (e) {
            this.logger.warn('Intent JSON parse failed, using fallback', e);
          }
          resolve({ summary: '正在生成多模态内容', imagePrompts: [], chartSpecs: [{ title: '内容概览', type: 'flowchart', description: '主要内容流程' }] });
        },
        onError: (err) => {
          this.logger.warn('Intent agent error', err);
          resolve({ summary: '正在生成多模态内容', imagePrompts: [], chartSpecs: [] });
        },
      });
    });
  }

  // ─── Agent 2: 内容生成（流式Markdown） ─────────────────────────────────────
  // 生成含 ```mermaid 代码块和 [IMAGE_N] 占位符的完整Markdown（流式输出）
  async generateContent(
    plan: IntentPlan,
    userMessage: string,
    modelId: number,
    handlers: {
      onChunk: (chunk: string) => void;
      onDone: (fullText: string) => void;
      onError: (err: Error) => void;
    },
  ): Promise<void> {
    const chartInstructions = plan.chartSpecs.length > 0
      ? plan.chartSpecs.map((s, i) =>
          `图表${i + 1}：标题="${s.title}"，类型=${s.type}，内容=${s.description}`,
        ).join('\n')
      : '无需专门图表';

    const imageInstructions = plan.imagePrompts.length > 0
      ? `在合适位置分别独占一行插入以下占位符：${plan.imagePrompts.map((_, i) => `[IMAGE_${i}]`).join('、')}`
      : '不需要图片，请勿插入任何[IMAGE_N]占位符';

    const mermaidExamples = `
mermaid语法示例（必须严格遵守）：
flowchart:
\`\`\`mermaid
flowchart TD
  A[开始] --> B{判断}
  B -->|是| C[执行]
  B -->|否| D[结束]
\`\`\`
pie:
\`\`\`mermaid
pie title 数据分布
  "类别A" : 40
  "类别B" : 35
  "类别C" : 25
\`\`\`
sequence:
\`\`\`mermaid
sequenceDiagram
  participant A as 用户
  participant B as 系统
  A->>B: 发送请求
  B-->>A: 返回结果
\`\`\`
gantt:
\`\`\`mermaid
gantt
  title 项目计划
  dateFormat YYYY-MM-DD
  section 阶段1
  任务A :a1, 2024-01-01, 30d
\`\`\`
mindmap:
\`\`\`mermaid
mindmap
  root((主题))
    分支1
      子节点A
      子节点B
    分支2
      子节点C
\`\`\``;

    const systemPrompt = `你是专业的多模态内容生成器，生成结构清晰、图文并茂的Markdown报告。

本次任务：${plan.summary}

【图表要求】
${chartInstructions}

【图片要求】
${imageInstructions}

【输出要求】
1. 使用标题层级(# ## ###)合理划分章节，内容丰富有实际价值，总字数不少于800字
2. 按要求嵌入Mermaid图表，数量必须满足要求，语法严格参照示例
3. mermaid代码阶叇选择规则（按优先级尽量遵守）：
   a) 节点ID只用英文字母+数字（A B C1 D2等），不要用中文或特殊符号
   b) 节点标签内容第一选择：英文描述；如必须用中文，用方括号[]包裹，绝对不用()括号
   c) 不要在mermaid代码中使用任何引号（包括中英文单引号/双引号）
   d) flowchart路径标签用管道语法：-->｜文字｜，文字不需要引号
   e) pie图表每行格式严格：用英文双引号包裹标签，如: "CategoryA" : 40
   f) mindmap中用空格缩进表示层级，展开节点不需要[]
4. 如需图片，在相关章节末尾独占一行插入占位符
5. 生成完整可读的报告，不要输出"占位符说明"等元信息

${mermaidExamples}`;

    return new Promise<void>((resolve) => {
      this.aiService.streamChat({
        modelId,
        messages: [{ role: 'user', content: userMessage }],
        mode: 'expert',
        customSystemPrompt: systemPrompt,
        onChunk: handlers.onChunk,
        onDone: (fullText) => { handlers.onDone(fullText); resolve(); },
        onError: (err) => { handlers.onError(err); resolve(); },
      });
    });
  }

  // ─── Agent 3: 图片生成 ─────────────────────────────────────────────────────
  // 复用现有 AiService.generateImage，无需额外实现
  async generateImage(prompt: string): Promise<string> {
    return this.aiService.generateImage(prompt);
  }
}
