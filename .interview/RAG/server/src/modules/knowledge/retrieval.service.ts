import { Injectable, Logger } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import { EmbeddingService } from './embedding.service';

export interface RetrievedChunk {
  id: number;
  kb_id: number;
  doc_id: number;
  content: string;
  score: number;
  filename?: string;
}

/** 余弦相似度（向量点积 / 模长之积） */
function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}

@Injectable()
export class RetrievalService {
  private readonly logger = new Logger(RetrievalService.name);
  /** 向量检索最低相似度阈值 */
  private readonly VEC_THRESHOLD = 0.3;

  constructor(
    private db: DatabaseService,
    private embedding: EmbeddingService,
  ) {}

  /**
   * 混合检索：向量相似度 + FTS5 关键词，RRF 融合重排序
   * @param query  用户查询
   * @param kbIds  要检索的知识库 id 列表
   * @param topK   返回最多 topK 条
   */
  async retrieve(query: string, kbIds: number[], topK = 5): Promise<RetrievedChunk[]> {
    if (!kbIds.length) return [];

    const queryVec = await this.embedding.embedText(query);

    const vecResults = this.vectorSearch(queryVec, kbIds, topK * 3);
    const ftsResults = this.ftsSearch(query, kbIds, topK * 3);

    const merged = this.rrfMerge(vecResults, ftsResults, topK);

    // 拼上文件名
    for (const chunk of merged) {
      const doc = this.db.get(
        'SELECT filename FROM kb_documents WHERE id=?',
        [chunk.doc_id],
      ) as any;
      if (doc) chunk.filename = doc.filename;
    }

    return merged;
  }

  private vectorSearch(
    queryVec: number[],
    kbIds: number[],
    limit: number,
  ): RetrievedChunk[] {
    const ph = kbIds.map(() => '?').join(',');
    const rows = this.db.all(
      `SELECT id, kb_id, doc_id, content, embedding FROM kb_chunks
       WHERE kb_id IN (${ph}) AND embedding IS NOT NULL`,
      kbIds,
    ) as any[];

    return rows
      .map((r) => {
        let score = 0;
        try {
          score = cosineSimilarity(queryVec, JSON.parse(r.embedding) as number[]);
        } catch {
          score = 0;
        }
        return { ...r, score };
      })
      .filter((r) => r.score >= this.VEC_THRESHOLD)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  private ftsSearch(query: string, kbIds: number[], limit: number): RetrievedChunk[] {
    try {
      const ph = kbIds.map(() => '?').join(',');
      // FTS5 MATCH 使用安全的查询串（去除特殊字符）
      const safeQ = query
        .replace(/['"()*:^]/g, ' ')
        .trim()
        .split(/\s+/)
        .filter(Boolean)
        .join(' OR ');
      if (!safeQ) return [];

      return this.db.all(
        `SELECT c.id, c.kb_id, c.doc_id, c.content,
                (-f.rank) AS score
         FROM kb_chunks_fts f
         JOIN kb_chunks c ON c.id = f.chunk_id
         WHERE kb_chunks_fts MATCH ? AND f.kb_id IN (${ph})
         ORDER BY rank
         LIMIT ?`,
        [safeQ, ...kbIds, limit],
      ) as RetrievedChunk[];
    } catch (err: any) {
      this.logger.warn(`FTS5 search failed: ${err.message}`);
      return [];
    }
  }

  /** Reciprocal Rank Fusion 融合两个结果列表 */
  private rrfMerge(
    vecResults: RetrievedChunk[],
    ftsResults: RetrievedChunk[],
    topK: number,
  ): RetrievedChunk[] {
    const K = 60;
    const scores = new Map<number, number>();
    const chunkMap = new Map<number, RetrievedChunk>();

    vecResults.forEach((c, rank) => {
      scores.set(c.id, (scores.get(c.id) ?? 0) + 1 / (rank + K));
      chunkMap.set(c.id, c);
    });
    ftsResults.forEach((c, rank) => {
      scores.set(c.id, (scores.get(c.id) ?? 0) + 1 / (rank + K));
      if (!chunkMap.has(c.id)) chunkMap.set(c.id, c);
    });

    return Array.from(scores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, topK)
      .map(([id, score]) => ({ ...chunkMap.get(id)!, score }));
  }
}
