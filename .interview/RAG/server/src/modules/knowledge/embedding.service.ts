import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

@Injectable()
export class EmbeddingService {
  private readonly logger = new Logger(EmbeddingService.name);
  private readonly BATCH_SIZE = 25;
  private readonly MODEL = 'BAAI/bge-m3';
  private readonly BASE_URL = 'https://api.siliconflow.cn/v1';

  constructor(private config: ConfigService) {}

  /** 批量文本 → embedding 向量数组，自动分批 + 限速 */
  async embedTexts(texts: string[]): Promise<number[][]> {
    const apiKey = this.config.get<string>('SILICONFLOW_API_KEY');
    if (!apiKey) throw new Error('SILICONFLOW_API_KEY 未配置');

    const results: number[][] = [];
    for (let i = 0; i < texts.length; i += this.BATCH_SIZE) {
      const batch = texts.slice(i, i + this.BATCH_SIZE);
      const batchResult = await this.embedBatch(batch, apiKey);
      results.push(...batchResult);
      // 批次间隔 200ms，避免触发频率限制
      if (i + this.BATCH_SIZE < texts.length) {
        await new Promise((r) => setTimeout(r, 200));
      }
    }
    return results;
  }

  /** 单条文本 → embedding 向量 */
  async embedText(text: string): Promise<number[]> {
    const results = await this.embedTexts([text]);
    return results[0];
  }

  private async embedBatch(texts: string[], apiKey: string): Promise<number[][]> {
    const res = await axios.post(
      `${this.BASE_URL}/embeddings`,
      { model: this.MODEL, input: texts, encoding_format: 'float' },
      {
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 60000,
      },
    );
    // 保序：按 index 排序后取 embedding
    return (res.data.data as any[])
      .sort((a, b) => a.index - b.index)
      .map((d) => d.embedding as number[]);
  }
}
