import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class ChatService {
  constructor(private db: DatabaseService) {}

  getConversations(userId: number) {
    return this.db.all(
      `SELECT c.*, m.name as model_name
       FROM conversations c
       LEFT JOIN ai_models m ON c.model_id = m.id
       WHERE c.user_id = ?
       ORDER BY c.updated_at DESC
       LIMIT 100`,
      [userId],
    );
  }

  getConversationById(id: string, userId: number) {
    return this.db.get(
      'SELECT * FROM conversations WHERE id=? AND user_id=?',
      [id, userId],
    );
  }

  createConversation(userId: number, modelId?: number, mode = 'fast', title = '新对话') {
    const id = uuidv4();
    this.db.run(
      'INSERT INTO conversations (id, user_id, model_id, mode, title) VALUES (?,?,?,?,?)',
      [id, userId, modelId || null, mode, title],
    );
    return this.db.get('SELECT * FROM conversations WHERE id=?', [id]);
  }

  updateConversation(id: string, userId: number, data: { title?: string; model_id?: number; mode?: string }) {
    const fields: string[] = ['updated_at=CURRENT_TIMESTAMP'];
    const values: any[] = [];
    if (data.title !== undefined) { fields.push('title=?'); values.push(data.title); }
    if (data.model_id !== undefined) { fields.push('model_id=?'); values.push(data.model_id); }
    if (data.mode !== undefined) { fields.push('mode=?'); values.push(data.mode); }
    values.push(id, userId);
    this.db.run(`UPDATE conversations SET ${fields.join(',')} WHERE id=? AND user_id=?`, values);
    return this.db.get('SELECT * FROM conversations WHERE id=?', [id]);
  }

  deleteConversation(id: string, userId: number) {
    this.db.run('DELETE FROM conversations WHERE id=? AND user_id=?', [id, userId]);
  }

  getMessages(conversationId: string) {
    const rows = this.db.all(
      'SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at ASC',
      [conversationId],
    ) as any[];
    return rows.map((m) => ({
      ...m,
      rag_sources: m.rag_sources ? JSON.parse(m.rag_sources) : undefined,
    }));
  }

  addMessage(conversationId: string, role: string, content: string, options?: {
    content_type?: string;
    attachment_id?: number;
    reasoning_content?: string;
    model_used?: string;
    tokens_used?: number;
    rag_sources?: string;
  }) {
    const id = uuidv4();
    this.db.run(
      `INSERT INTO messages (id, conversation_id, role, content, content_type, attachment_id, reasoning_content, model_used, tokens_used, rag_sources)
       VALUES (?,?,?,?,?,?,?,?,?,?)`,
      [
        id, conversationId, role, content,
        options?.content_type || 'text',
        options?.attachment_id || null,
        options?.reasoning_content || null,
        options?.model_used || null,
        options?.tokens_used || 0,
        options?.rag_sources || null,
      ],
    );
    // 更新对话时间
    this.db.run('UPDATE conversations SET updated_at=CURRENT_TIMESTAMP WHERE id=?', [conversationId]);
    return this.db.get('SELECT * FROM messages WHERE id=?', [id]);
  }

  /** 删除最后一条 assistant 消息（重新生成时调用） */
  deleteLastAssistantMessage(conversationId: string) {
    const lastMsg = this.db.get(
      'SELECT id FROM messages WHERE conversation_id=? AND role=? ORDER BY created_at DESC LIMIT 1',
      [conversationId, 'assistant'],
    ) as any;
    if (lastMsg) {
      this.db.run('DELETE FROM messages WHERE id=?', [lastMsg.id]);
    }
  }

  /** 自动生成对话标题（取用户第一条消息前20字符） */
  autoGenerateTitle(conversationId: string) {
    const firstMsg = this.db.get(
      'SELECT content FROM messages WHERE conversation_id=? AND role=? ORDER BY created_at ASC LIMIT 1',
      [conversationId, 'user'],
    ) as any;
    if (firstMsg) {
      const title = firstMsg.content.slice(0, 20).replace(/\n/g, ' ');
      this.db.run('UPDATE conversations SET title=? WHERE id=?', [title, conversationId]);
    }
  }
}
