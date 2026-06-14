import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { DatabaseService } from '../../database/database.service';
import * as fs from 'fs';
import * as path from 'path';
import * as mammoth from 'mammoth';

@Injectable()
export class FileService {
  private readonly logger = new Logger(FileService.name);
  private readonly uploadDir: string;

  constructor(
    private db: DatabaseService,
    private config: ConfigService,
  ) {
    this.uploadDir = config.get('UPLOAD_DIR', './uploads');
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  async parseAndSave(userId: number, file: Express.Multer.File): Promise<any> {
    let parsedContent = '';

    try {
      const ext = path.extname(file.originalname).toLowerCase();
      if (ext === '.docx') {
        const result = await mammoth.extractRawText({ buffer: file.buffer });
        parsedContent = result.value;
      } else {
        // .md / .txt
        parsedContent = file.buffer.toString('utf-8');
      }
    } catch (err: any) {
      this.logger.error(`文件解析失败: ${err.message}`);
      parsedContent = file.buffer.toString('utf-8');
    }

    // 限制文件内容长度（防止超过模型上下文）
    if (parsedContent.length > 50000) {
      parsedContent = parsedContent.slice(0, 50000) + '\n...[内容过长已截断]';
    }

    // 保存文件到本地
    const filename = `${Date.now()}_${file.originalname}`;
    const filepath = path.join(this.uploadDir, filename);
    fs.writeFileSync(filepath, file.buffer);

    const r = this.db.run(
      'INSERT INTO attachments (user_id, filename, filepath, mimetype, size, parsed_content) VALUES (?,?,?,?,?,?)',
      [userId, file.originalname, filepath, file.mimetype, file.size, parsedContent],
    );

    return this.db.get('SELECT id, user_id, filename, mimetype, size, created_at FROM attachments WHERE id=?', [r.lastInsertRowid]);
  }

  getAttachment(id: number, userId: number) {
    return this.db.get('SELECT * FROM attachments WHERE id=? AND user_id=?', [id, userId]);
  }

  listFiles(userId: number) {
    return this.db.all(
      'SELECT id, user_id, filename, mimetype, size, created_at FROM attachments WHERE user_id=? ORDER BY created_at DESC',
      [userId],
    );
  }

  deleteFile(id: number, userId: number) {
    const file = this.db.get(
      'SELECT filepath FROM attachments WHERE id=? AND user_id=?',
      [id, userId],
    ) as any;
    if (file?.filepath && fs.existsSync(file.filepath)) {
      try { fs.unlinkSync(file.filepath); } catch { /* 就算磁盘文件不存在也正常删库 */ }
    }
    this.db.run('DELETE FROM attachments WHERE id=? AND user_id=?', [id, userId]);
    return { success: true };
  }

  /** 下载文件：返回原始二进制 Buffer + 文件名 + MIME 类型 */
  downloadFile(id: number, userId: number): { buffer: Buffer; filename: string; mimetype: string } {
    const file = this.db.get(
      'SELECT * FROM attachments WHERE id=? AND user_id=?',
      [id, userId],
    ) as any;
    if (!file) throw new Error('文件不存在或无权访问');
    if (!file.filepath || !fs.existsSync(file.filepath)) {
      throw new Error('文件已被删除或无法访问');
    }
    const buffer = fs.readFileSync(file.filepath);
    return { buffer, filename: file.filename, mimetype: file.mimetype || 'application/octet-stream' };
  }
}
