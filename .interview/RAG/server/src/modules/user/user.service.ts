import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';
import * as bcrypt from 'bcrypt';

@Injectable()
export class UserService {
  constructor(private db: DatabaseService) {}

  findById(id: number) {
    return this.db.get('SELECT * FROM users WHERE id = ?', [id]);
  }

  findAll(page = 1, pageSize = 20) {
    const offset = (page - 1) * pageSize;
    const total = (this.db.get('SELECT COUNT(*) as c FROM users') as any).c;
    const list = this.db.all('SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?', [pageSize, offset]);
    return { list, total, page, pageSize };
  }

  update(id: number, data: { plan_type?: string; is_member?: number; tokens_remaining?: number; is_admin?: number }) {
    const fields: string[] = [];
    const values: any[] = [];
    if (data.plan_type !== undefined) { fields.push('plan_type=?'); values.push(data.plan_type); }
    if (data.is_member !== undefined) { fields.push('is_member=?'); values.push(data.is_member); }
    if (data.tokens_remaining !== undefined) { fields.push('tokens_remaining=?'); values.push(data.tokens_remaining); }
    if (data.is_admin !== undefined) { fields.push('is_admin=?'); values.push(data.is_admin); }
    if (fields.length === 0) return this.findById(id);
    fields.push('updated_at=CURRENT_TIMESTAMP');
    values.push(id);
    this.db.run(`UPDATE users SET ${fields.join(',')} WHERE id=?`, values);
    return this.findById(id);
  }

  deductTokens(userId: number, tokens: number) {
    this.db.run('UPDATE users SET tokens_remaining = MAX(0, tokens_remaining - ?) WHERE id = ?', [tokens, userId]);
  }

  addTokens(userId: number, tokens: number) {
    this.db.run('UPDATE users SET tokens_remaining = tokens_remaining + ? WHERE id = ?', [tokens, userId]);
  }

  incrementImagesUsed(userId: number) {
    this.db.run('UPDATE users SET images_used = COALESCE(images_used, 0) + 1 WHERE id = ?', [userId]);
  }

  // ──── 本地用户认证 ────

  /** 根据 username 查找用户 */
  findByUsername(username: string) {
    return this.db.get('SELECT * FROM users WHERE username = ? AND user_type = ?', [username, 'local']) as any;
  }

  /** 创建本地用户（账号密码登录） */
  async createLocalUser(data: {
    username: string;
    password: string;
    nickname?: string;
    plan_type?: string;
    tokens_remaining?: number;
    is_admin?: number;
  }) {
    // 检查 username 是否已存在
    const existing = this.db.get('SELECT id FROM users WHERE username = ?', [data.username]);
    if (existing) {
      throw new ConflictException('账号已存在');
    }

    // 密码加密
    const saltRounds = 10;
    const passwordHash = await bcrypt.hash(data.password, saltRounds);

    // 插入数据库
    const result = this.db.run(
      `INSERT INTO users (openid, username, password_hash, nickname, user_type, plan_type, tokens_remaining, is_admin, must_change_password)
       VALUES (?, ?, ?, ?, 'local', ?, ?, ?, 1)`,
      [
        `local_${data.username}_${Date.now()}`,  // 生成唯一的虚拟 openid
        data.username,
        passwordHash,
        data.nickname || data.username,
        data.plan_type || null,
        data.tokens_remaining ?? 100000,
        data.is_admin ?? 0,
      ],
    );

    return this.db.get('SELECT * FROM users WHERE id = ?', [result.lastInsertRowid]);
  }

  /** 验证本地用户密码 */
  async verifyPassword(username: string, password: string) {
    const user = this.findByUsername(username);
    if (!user) return null;
    if (user.is_disabled) return null; // 禁用账号

    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) return null;

    return user;
  }

  /** 更新密码 */
  async updatePassword(userId: number, newPassword: string) {
    const saltRounds = 10;
    const passwordHash = await bcrypt.hash(newPassword, saltRounds);
    this.db.run(
      'UPDATE users SET password_hash = ?, must_change_password = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [passwordHash, userId],
    );
  }

  /** 重置密码（管理员操作） */
  async resetPassword(userId: number, newPassword: string) {
    const saltRounds = 10;
    const passwordHash = await bcrypt.hash(newPassword, saltRounds);
    this.db.run(
      'UPDATE users SET password_hash = ?, must_change_password = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [passwordHash, userId],
    );
  }

  /** 禁用/启用用户 */
  toggleDisabled(userId: number, isDisabled: boolean) {
    this.db.run(
      'UPDATE users SET is_disabled = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [isDisabled ? 1 : 0, userId],
    );
    return this.db.get('SELECT * FROM users WHERE id = ?', [userId]);
  }
}
