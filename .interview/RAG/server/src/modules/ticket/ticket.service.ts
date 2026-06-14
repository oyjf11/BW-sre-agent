import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';

export interface EmotionResult {
  negative: boolean;
  needsHuman: boolean;
  emotion: 'neutral' | 'negative' | 'needs_human';
}

/**
 * 轻量级情绪识别（关键词匹配）
 * - 无需调用外部 AI，响应极快
 * - 覆盖"投诉/不满意/要人工"三大场景
 */
export function analyzeEmotion(text: string): EmotionResult {
  const t = text || '';

  const humanKeywords = [
    '人工', '客服', '人工服务', '转人工', '人工客服',
    '联系客服', '需要人工', '找客服', '找人', '工作人员',
    '在线客服', '专员', '人工介入',
  ];
  const negativeKeywords = [
    '不满意', '不对', '错了', '说错', '回答错', '答错', '不对劲',
    '没用', '没效果', '垃圾', '差评', '不行', '太差', '很差', '非常差',
    '失望', '糟糕', '很糟', '太烂', '不靠谱', '不准确', '不正确',
    '解决不了', '帮不了', '帮不上', '这不是我想要的', '不是我要的',
    '完全不对', '答非所问', '牛头不对马嘴', '投诉', '举报',
  ];

  const needsHuman = humanKeywords.some((k) => t.includes(k));
  const isNegative = negativeKeywords.some((k) => t.includes(k));

  return {
    negative: isNegative || needsHuman,
    needsHuman,
    emotion: needsHuman ? 'needs_human' : isNegative ? 'negative' : 'neutral',
  };
}

@Injectable()
export class TicketService {
  constructor(private db: DatabaseService) {}

  createTicket(data: {
    userId: number;
    conversationId?: string;
    lastUserMessage?: string;
    emotion?: string;
    needsHuman?: boolean;
  }) {
    const result = this.db.run(
      `INSERT INTO tickets (user_id, conversation_id, last_user_message, emotion, needs_human)
       VALUES (?, ?, ?, ?, ?)`,
      [
        data.userId,
        data.conversationId ?? null,
        data.lastUserMessage ?? null,
        data.emotion ?? 'neutral',
        data.needsHuman ? 1 : 0,
      ],
    );
    return this.db.get('SELECT * FROM tickets WHERE id = ?', [(result as any).lastInsertRowid]);
  }

  /** 管理员获取所有工单（含用户昵称） */
  getAdminTickets(page = 1, pageSize = 50) {
    const offset = (page - 1) * pageSize;
    const list = this.db.all(
      `SELECT t.*, u.nickname, u.avatar
       FROM tickets t
       LEFT JOIN users u ON u.id = t.user_id
       ORDER BY t.created_at DESC
       LIMIT ? OFFSET ?`,
      [pageSize, offset],
    );
    const total = (this.db.get('SELECT COUNT(*) as c FROM tickets', []) as any)?.c ?? 0;
    return { list, total, page, pageSize };
  }

  /** 管理员更新工单状态/备注 */
  updateTicket(id: number, data: { status?: string; admin_notes?: string }) {
    const sets: string[] = [];
    const vals: any[] = [];
    if (data.status !== undefined) { sets.push('status = ?'); vals.push(data.status); }
    if (data.admin_notes !== undefined) { sets.push('admin_notes = ?'); vals.push(data.admin_notes); }
    if (sets.length === 0) return null;
    sets.push('updated_at = CURRENT_TIMESTAMP');
    vals.push(id);
    this.db.run(`UPDATE tickets SET ${sets.join(', ')} WHERE id = ?`, vals);
    return this.db.get('SELECT * FROM tickets WHERE id = ?', [id]);
  }

  /** 获取用户自己的工单 */
  getUserTickets(userId: number) {
    return this.db.all(
      'SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC LIMIT 20',
      [userId],
    );
  }
}
