import { Injectable, Logger, NotFoundException, ForbiddenException } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import { EmbeddingService } from './embedding.service';
import { ChunkerService } from './chunker.service';

@Injectable()
export class KnowledgeService {
  private readonly logger = new Logger(KnowledgeService.name);

  constructor(
    private db: DatabaseService,
    private chunker: ChunkerService,
    private embedding: EmbeddingService,
  ) {}

  // ────────────────────────────────────────────────────────────
  //  知识库 CRUD
  // ────────────────────────────────────────────────────────────

  createKnowledgeBase(
    userId: number | null,
    name: string,
    description = '',
    isPublic = false,
  ) {
    const result = this.db.run(
      'INSERT INTO knowledge_bases (user_id, name, description, is_public) VALUES (?,?,?,?)',
      [userId, name, description, isPublic ? 1 : 0],
    );
    return this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [result.lastInsertRowid]);
  }

  /** 普通用户：公共知识库 + 自己的；管理员：全部 */
  listKnowledgeBases(userId: number, isAdmin = false) {
    if (isAdmin) {
      return this.db.all('SELECT * FROM knowledge_bases ORDER BY created_at DESC');
    }
    return this.db.all(
      'SELECT * FROM knowledge_bases WHERE is_public=1 OR user_id=? ORDER BY created_at DESC',
      [userId],
    );
  }

  getKnowledgeBase(id: number) {
    return this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [id]);
  }

  updateKnowledgeBase(
    id: number,
    userId: number,
    isAdmin: boolean,
    data: { name?: string; description?: string; is_public?: boolean },
  ) {
    const kb = this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [id]) as any;
    if (!kb) throw new NotFoundException('知识库不存在');
    if (!isAdmin && kb.user_id !== userId) throw new ForbiddenException('无权限修改');

    const sets: string[] = [];
    const vals: any[] = [];
    if (data.name !== undefined) { sets.push('name=?'); vals.push(data.name); }
    if (data.description !== undefined) { sets.push('description=?'); vals.push(data.description); }
    if (data.is_public !== undefined) { sets.push('is_public=?'); vals.push(data.is_public ? 1 : 0); }
    sets.push('updated_at=CURRENT_TIMESTAMP');
    if (!sets.length) return kb;

    this.db.run(`UPDATE knowledge_bases SET ${sets.join(',')} WHERE id=?`, [...vals, id]);
    return this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [id]);
  }

  deleteKnowledgeBase(id: number, userId: number, isAdmin = false) {
    const kb = this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [id]) as any;
    if (!kb) throw new NotFoundException('知识库不存在');
    if (!isAdmin && kb.user_id !== userId) throw new ForbiddenException('无权限删除');

    // 删除 FTS5 中对应条目
    this.db.run('DELETE FROM kb_chunks_fts WHERE kb_id=?', [id]);
    this.db.run('DELETE FROM knowledge_bases WHERE id=?', [id]);
    return { success: true };
  }

  // ────────────────────────────────────────────────────────────
  //  文档管理
  // ────────────────────────────────────────────────────────────

  listDocuments(kbId: number) {
    return this.db.all(
      `SELECT id, kb_id, filename, file_type, file_size, status,
              error_msg, chunk_count, created_at
       FROM kb_documents WHERE kb_id=? ORDER BY created_at DESC`,
      [kbId],
    );
  }

  deleteDocument(docId: number, kbId: number, userId: number, isAdmin = false) {
    const kb = this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [kbId]) as any;
    if (!kb) throw new NotFoundException('知识库不存在');
    if (!isAdmin && kb.user_id !== userId) throw new ForbiddenException('无权限操作');

    const doc = this.db.get('SELECT * FROM kb_documents WHERE id=? AND kb_id=?', [docId, kbId]) as any;
    if (!doc) throw new NotFoundException('文档不存在');

    // 清理 FTS5
    const chunks = this.db.all('SELECT id FROM kb_chunks WHERE doc_id=?', [docId]) as any[];
    for (const c of chunks) {
      this.db.run('DELETE FROM kb_chunks_fts WHERE chunk_id=?', [c.id]);
    }

    this.db.run('DELETE FROM kb_documents WHERE id=?', [docId]);
    this.db.run(
      'UPDATE knowledge_bases SET doc_count=MAX(0,doc_count-1), chunk_count=MAX(0,chunk_count-?), updated_at=CURRENT_TIMESTAMP WHERE id=?',
      [doc.chunk_count ?? 0, kbId],
    );
    return { success: true };
  }

  // ────────────────────────────────────────────────────────────
  //  文档上传 & 异步索引
  // ────────────────────────────────────────────────────────────

  async indexDocument(
    kbId: number,
    filename: string,
    buffer: Buffer,
    userId: number,
    isAdmin = false,
  ): Promise<{ docId: number; message: string }> {
    const kb = this.db.get('SELECT * FROM knowledge_bases WHERE id=?', [kbId]) as any;
    if (!kb) throw new NotFoundException('知识库不存在');
    if (!isAdmin && kb.user_id !== userId) throw new ForbiddenException('无权限上传');

    // 修复 Latin-1 文件名乱码
    const safeName = Buffer.from(filename, 'latin1').toString('utf8');
    const ext = (safeName.match(/\.[^.]+$/)?.[0] ?? '').toLowerCase().slice(1);

    const r = this.db.run(
      'INSERT INTO kb_documents (kb_id, filename, file_type, file_size, status) VALUES (?,?,?,?,?)',
      [kbId, safeName, ext, buffer.length, 'indexing'],
    );
    const docId = r.lastInsertRowid as number;

    this.db.run(
      'UPDATE knowledge_bases SET doc_count=doc_count+1, updated_at=CURRENT_TIMESTAMP WHERE id=?',
      [kbId],
    );

    // 异步处理，不阻塞响应
    this.processDocument(kbId, docId, safeName, buffer).catch((err) => {
      this.logger.error(`文档 ${docId} 索引失败: ${err.message}`);
    });

    return { docId, message: '上传成功，后台正在索引中' };
  }

  private async processDocument(
    kbId: number,
    docId: number,
    filename: string,
    buffer: Buffer,
  ) {
    try {
      const text = await this.chunker.parseFile(buffer, filename);
      if (!text.trim()) throw new Error('文件内容为空');

      // 存储解析后的纲文（限制 500KB），供预览使用
      this.db.run(
        'UPDATE kb_documents SET parsed_content=? WHERE id=?',
        [text.slice(0, 500000), docId],
      );

      const chunks = this.chunker.chunkText(text);
      if (chunks.length === 0) throw new Error('无法从文档中提取有效内容块');

      this.logger.log(`文档 ${docId} 解析完成，共 ${chunks.length} 块，开始 Embedding...`);
      const embeddings = await this.embedding.embedTexts(chunks);

      // 事务写入
      this.db.transaction(() => {
        for (let i = 0; i < chunks.length; i++) {
          const cr = this.db.run(
            'INSERT INTO kb_chunks (kb_id, doc_id, chunk_index, content, embedding, token_count) VALUES (?,?,?,?,?,?)',
            [kbId, docId, i, chunks[i], JSON.stringify(embeddings[i]), chunks[i].length],
          );
          this.db.run(
            'INSERT INTO kb_chunks_fts (chunk_id, kb_id, content) VALUES (?,?,?)',
            [cr.lastInsertRowid, kbId, chunks[i]],
          );
        }
        this.db.run(
          'UPDATE kb_documents SET status=?, chunk_count=? WHERE id=?',
          ['ready', chunks.length, docId],
        );
        this.db.run(
          'UPDATE knowledge_bases SET chunk_count=chunk_count+?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
          [chunks.length, kbId],
        );
      });

      this.logger.log(`文档 ${docId} 索引完成，共 ${chunks.length} 块`);
    } catch (err: any) {
      this.db.run(
        'UPDATE kb_documents SET status=?, error_msg=? WHERE id=?',
        ['failed', err.message, docId],
      );
      throw err;
    }
  }

  getDocumentPreview(docId: number, kbId: number) {
    const doc = this.db.get(
      'SELECT id, filename, file_type, parsed_content FROM kb_documents WHERE id=? AND kb_id=?',
      [docId, kbId],
    ) as any;
    if (!doc) return null;

    // 降级回退：老文档 parsed_content 为空时，从分块拼接重建预览
    if (!doc.parsed_content) {
      const chunks = this.db.all(
        'SELECT content FROM kb_chunks WHERE doc_id=? AND kb_id=? ORDER BY chunk_index ASC',
        [docId, kbId],
      ) as any[];
      if (chunks.length > 0) {
        const OVERLAP = 80;
        let assembled = chunks[0].content as string;
        for (let i = 1; i < chunks.length; i++) {
          const curr = chunks[i].content as string;
          const suffix = assembled.slice(-OVERLAP);
          // 当前块首部与上一块尾部重叠时，去重
          if (curr.startsWith(suffix) && suffix.trim().length > 0) {
            assembled += '\n\n' + curr.slice(suffix.length);
          } else {
            assembled += '\n\n' + curr;
          }
        }
        doc.parsed_content = assembled;
      }
    }

    return doc;
  }

  getDocumentStatus(kbId: number) {
    const docs = this.db.all('SELECT status FROM kb_documents WHERE kb_id=?', [kbId]) as any[];
    return {
      total: docs.length,
      ready: docs.filter((d) => d.status === 'ready').length,
      indexing: docs.filter((d) => d.status === 'indexing').length,
      failed: docs.filter((d) => d.status === 'failed').length,
    };
  }

  /** 获取文档分块列表（不返回向量） */
  listChunks(docId: number, kbId: number) {
    return this.db.all(
      `SELECT id, chunk_index, content, token_count FROM kb_chunks
       WHERE doc_id=? AND kb_id=? ORDER BY chunk_index ASC`,
      [docId, kbId],
    );
  }

  // ────────────────────────────────────────────────────────────
  //  数据统计分析
  // ────────────────────────────────────────────────────────────

  getAnalytics(userId: number, isAdmin: boolean) {
    // 1. 获取可访问的知识库列表
    const accessibleKbs = (isAdmin
      ? this.db.all('SELECT id, is_public FROM knowledge_bases')
      : this.db.all(
          'SELECT id, is_public FROM knowledge_bases WHERE user_id=? OR is_public=1',
          [userId],
        )
    ) as any[];

    const totalBases = accessibleKbs.length;
    const publicBases = accessibleKbs.filter((k) => k.is_public === 1).length;
    const privateBases = totalBases - publicBases;
    const kbIds = accessibleKbs.map((k) => k.id);

    if (kbIds.length === 0) {
      return {
        overview: { totalBases: 0, publicBases: 0, privateBases: 0, totalDocs: 0, totalChunks: 0 },
        health: { byStatus: [], byType: [], successRate: 100, failedReasons: [] },
        ragUsage: { totalAiMsgs: 0, ragMsgs: 0, hitRate: 0, trend: [] },
      };
    }

    const ph = kbIds.map(() => '?').join(',');

    // 2. 文档状态分布
    const byStatus = this.db.all(
      `SELECT status, COUNT(*) as count FROM kb_documents WHERE kb_id IN (${ph}) GROUP BY status ORDER BY count DESC`,
      kbIds,
    ) as any[];

    // 3. 文档格式分布
    const byType = this.db.all(
      `SELECT COALESCE(NULLIF(file_type,''), 'unknown') as file_type, COUNT(*) as count
       FROM kb_documents WHERE kb_id IN (${ph}) GROUP BY file_type ORDER BY count DESC`,
      kbIds,
    ) as any[];

    const totalDocs = byStatus.reduce((s: number, r: any) => s + r.count, 0);
    const readyCount = (byStatus.find((r: any) => r.status === 'ready')?.count as number) || 0;
    const failedCount = (byStatus.find((r: any) => r.status === 'failed')?.count as number) || 0;
    const successRate =
      readyCount + failedCount > 0
        ? Math.round((readyCount / (readyCount + failedCount)) * 100)
        : 100;

    // 4. 分块总数
    const chunksRow = this.db.get(
      `SELECT COUNT(*) as total FROM kb_chunks WHERE kb_id IN (${ph})`,
      kbIds,
    ) as any;

    // 5. 失败原因分布
    const failedReasons = this.db.all(
      `SELECT COALESCE(NULLIF(TRIM(error_msg),''), '未知错误') as reason, COUNT(*) as count
       FROM kb_documents WHERE status='failed' AND kb_id IN (${ph})
       GROUP BY reason ORDER BY count DESC LIMIT 5`,
      kbIds,
    ) as any[];

    // 6. RAG 使用统计（全局，不按知识库过滤）
    const ragStats = this.db.get(
      `SELECT COUNT(*) as total,
              SUM(CASE WHEN rag_sources IS NOT NULL THEN 1 ELSE 0 END) as withRag
       FROM messages WHERE role='assistant'`,
    ) as any;

    // 7. 近 7 天 RAG 趋势
    const trend = this.db.all(
      `SELECT DATE(created_at) as date,
              COUNT(*) as total,
              SUM(CASE WHEN rag_sources IS NOT NULL THEN 1 ELSE 0 END) as rag
       FROM messages
       WHERE role='assistant' AND DATE(created_at) >= DATE('now', '-6 days')
       GROUP BY DATE(created_at)
       ORDER BY date ASC`,
    ) as any[];

    return {
      overview: {
        totalBases,
        publicBases,
        privateBases,
        totalDocs,
        totalChunks: chunksRow?.total || 0,
      },
      health: {
        byStatus,
        byType,
        successRate,
        failedReasons,
      },
      ragUsage: {
        totalAiMsgs: ragStats?.total || 0,
        ragMsgs: ragStats?.withRag || 0,
        hitRate:
          ragStats?.total > 0
            ? Math.round((ragStats.withRag / ragStats.total) * 100)
            : 0,
        trend,
      },
    };
  }
}
