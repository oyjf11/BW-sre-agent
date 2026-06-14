import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Database from 'better-sqlite3';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class DatabaseService implements OnModuleInit, OnModuleDestroy {
  private db: Database.Database;

  constructor(private config: ConfigService) {}

  onModuleInit() {
    const dbPath = this.config.get<string>('DATABASE_PATH', './data/aichat.db');
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('foreign_keys = ON');
    this.migrate();
  }

  onModuleDestroy() {
    if (this.db) this.db.close();
  }

  getDb(): Database.Database {
    return this.db;
  }

  private migrate() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        openid TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE,
        password_hash TEXT,
        user_type TEXT DEFAULT 'sso' CHECK(user_type IN ('sso', 'local')),
        nickname TEXT,
        avatar TEXT,
        plan_type TEXT DEFAULT NULL,
        is_member INTEGER DEFAULT 0,
        tokens_remaining INTEGER DEFAULT 100000,
        is_admin INTEGER DEFAULT 0,
        must_change_password INTEGER DEFAULT 0,
        is_disabled INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS ai_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider TEXT NOT NULL,
        model_id TEXT NOT NULL,
        api_key TEXT,
        base_url TEXT,
        enabled INTEGER DEFAULT 1,
        supports_vision INTEGER DEFAULT 0,
        supports_image_gen INTEGER DEFAULT 0,
        supports_voice INTEGER DEFAULT 0,
        supports_video INTEGER DEFAULT 0,
        sort_order INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT DEFAULT '新对话',
        model_id INTEGER,
        mode TEXT DEFAULT 'fast',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (model_id) REFERENCES ai_models(id) ON DELETE SET NULL
      );

      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        content_type TEXT DEFAULT 'text' CHECK(content_type IN ('text', 'image', 'audio', 'video', 'file')),
        attachment_id INTEGER,
        reasoning_content TEXT,
        model_used TEXT,
        tokens_used INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        mimetype TEXT,
        size INTEGER DEFAULT 0,
        parsed_content TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        out_trade_no TEXT UNIQUE NOT NULL,
        order_no TEXT,
        amount INTEGER NOT NULL,
        plan_type TEXT NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'paid', 'closed', 'failed')),
        transaction_id TEXT,
        paid_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      );

      CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
      CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
      CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
      CREATE INDEX IF NOT EXISTS idx_orders_trade ON orders(out_trade_no);
    `);

    // 存量迁移：为旧数据库自动添加新字段
    try { this.db.exec('ALTER TABLE users ADD COLUMN images_used INTEGER DEFAULT 0'); } catch { /* 已存在 */ }
    try { this.db.exec('ALTER TABLE messages ADD COLUMN rag_sources TEXT'); } catch { /* 已存在 */ }
    try { this.db.exec('ALTER TABLE kb_documents ADD COLUMN parsed_content TEXT'); } catch { /* 已存在 */ }

    // 存量迁移：本地用户认证字段（username/password_hash）
    // SQLite 不支持通过 ALTER TABLE ADD COLUMN 直接添加 UNIQUE 列，需先加普通列，再建唯一索引。
    try { this.db.exec('ALTER TABLE users ADD COLUMN username TEXT'); } catch { /* 已存在 */ }
    try { this.db.exec('ALTER TABLE users ADD COLUMN password_hash TEXT'); } catch { /* 已存在 */ }
    try { this.db.exec("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'sso' CHECK(user_type IN ('sso', 'local'))"); } catch { /* 已存在 */ }
    try { this.db.exec('ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0'); } catch { /* 已存在 */ }
    try { this.db.exec('ALTER TABLE users ADD COLUMN is_disabled INTEGER DEFAULT 0'); } catch { /* 已存在 */ }
    this.db.exec('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username) WHERE username IS NOT NULL');

    // 存量迁移：创建工单表（情绪识别 + 人工服务）
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id TEXT,
        last_user_message TEXT,
        emotion TEXT DEFAULT 'neutral',
        needs_human INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'handling', 'resolved', 'closed')),
        admin_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      );
      CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id);
      CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
    `);

    // 存量迁移：RAG 知识库相关表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS knowledge_bases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        is_public INTEGER DEFAULT 0,
        doc_count INTEGER DEFAULT 0,
        chunk_count INTEGER DEFAULT 0,
        embedding_model TEXT DEFAULT 'BAAI/bge-m3',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS kb_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kb_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_type TEXT,
        file_size INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'indexing', 'ready', 'failed')),
        error_msg TEXT,
        chunk_count INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS kb_chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kb_id INTEGER NOT NULL,
        doc_id INTEGER NOT NULL,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        embedding TEXT,
        token_count INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
        FOREIGN KEY (doc_id) REFERENCES kb_documents(id) ON DELETE CASCADE
      );

      CREATE INDEX IF NOT EXISTS idx_kb_docs_kb ON kb_documents(kb_id);
      CREATE INDEX IF NOT EXISTS idx_kb_chunks_kb ON kb_chunks(kb_id);
      CREATE INDEX IF NOT EXISTS idx_kb_chunks_doc ON kb_chunks(doc_id);
    `);

    // FTS5 全文检索表（与 kb_chunks 同步，用于关键词检索）
    try {
      this.db.exec(`
        CREATE VIRTUAL TABLE IF NOT EXISTS kb_chunks_fts USING fts5(
          content,
          chunk_id UNINDEXED,
          kb_id UNINDEXED,
          tokenize='unicode61 remove_diacritics 1'
        );
      `);
    } catch { /* FTS5 已存在 */ }


    // 存量迁移：扩展 content_type CHECK 约束，支持 'multimodal'
    try {
      const tbl = this.db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='messages'").get() as any;
      if (tbl?.sql && !tbl.sql.includes("'multimodal'")) {
        this.db.pragma('foreign_keys = OFF');
        this.db.exec(`
          CREATE TABLE messages_new (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            content_type TEXT DEFAULT 'text' CHECK(content_type IN ('text', 'image', 'audio', 'video', 'file', 'multimodal')),
            attachment_id INTEGER,
            reasoning_content TEXT,
            model_used TEXT,
            tokens_used INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
          );
          INSERT INTO messages_new SELECT * FROM messages;
          DROP TABLE messages;
          ALTER TABLE messages_new RENAME TO messages;
          CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
        `);
        this.db.pragma('foreign_keys = ON');
      }
    } catch { /* already migrated or no-op */ }

    // 插入默认模型配置（从 env 读取 api_key）
    const existingModels = this.db.prepare('SELECT COUNT(*) as c FROM ai_models').get() as { c: number };
    // DOUBAO_ENDPOINT 支持两种格式：推理接入点 ep-xxx 或直接模型名如 doubao-pro-32k
    const doubaoModelId = this.config.get('DOUBAO_ENDPOINT', '') || 'doubao-pro-32k';
    if (existingModels.c === 0) {
      const deepseekKey  = this.config.get('DEEPSEEK_API_KEY', '');
      const moonshotKey  = this.config.get('MOONSHOT_API_KEY', '');
      const doubaoKey    = this.config.get('DOUBAO_API_KEY', '');
      const minimaxKey   = this.config.get('MINIMAX_API_KEY', '');
      const qwenKey      = this.config.get('QWEN_API_KEY', '');
    
      const insertModel = this.db.prepare(
        'INSERT INTO ai_models (name, provider, model_id, api_key, base_url, enabled, sort_order) VALUES (?,?,?,?,?,?,?)',
      );
      insertModel.run('豆包 Pro', 'doubao', doubaoModelId, doubaoKey || null, 'https://ark.cn-beijing.volces.com/api/v3', 1, 1);
      insertModel.run('Kimi',     'moonshot', 'moonshot-v1-8k', moonshotKey || null, 'https://api.moonshot.cn/v1', 1, 2);
      insertModel.run('DeepSeek R1', 'deepseek', 'deepseek-reasoner', deepseekKey || null, 'https://api.deepseek.com', 1, 3);
      insertModel.run('MiniMax',  'minimax', 'abab6.5s-chat', minimaxKey || null, 'https://api.minimax.chat/v1', 1, 4);
      insertModel.run('千问 Max',  'qwen', 'qwen-max', qwenKey || null, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 1, 5);
    } else {
      // 已有模型配置：只更新空 api_key（防止重启覆盖已配置的密鑰）
      const updates: Array<[string, string]> = [
        [this.config.get('DEEPSEEK_API_KEY', ''), 'deepseek'],
        [this.config.get('MOONSHOT_API_KEY', ''), 'moonshot'],
        [this.config.get('DOUBAO_API_KEY', ''), 'doubao'],
        [this.config.get('MINIMAX_API_KEY', ''), 'minimax'],
        [this.config.get('QWEN_API_KEY', ''), 'qwen'],
      ];
      const updateStmt = this.db.prepare("UPDATE ai_models SET api_key=? WHERE provider=? AND (api_key IS NULL OR api_key='')");
      for (const [key, provider] of updates) {
        if (key) updateStmt.run(key, provider);
      }
      // 若豆包 model_id 仍是旧占位符或兑退默认山，且 env 已配置有效 endpoint，自动修正
      const doubaoEndpoint = this.config.get('DOUBAO_ENDPOINT', '');
      if (doubaoEndpoint) {
        this.db.prepare(
          "UPDATE ai_models SET model_id=? WHERE provider='doubao' AND (model_id='ep-xxxxxxxx' OR model_id='doubao-pro-32k')",
        ).run(doubaoEndpoint);
      }
    }
  }

  // 通用查询方法
  all<T = any>(sql: string, params: any[] = []): T[] {
    return this.db.prepare(sql).all(...params) as T[];
  }

  get<T = any>(sql: string, params: any[] = []): T | undefined {
    return this.db.prepare(sql).get(...params) as T | undefined;
  }

  run(sql: string, params: any[] = []): Database.RunResult {
    return this.db.prepare(sql).run(...params);
  }

  transaction<T>(fn: () => T): T {
    return this.db.transaction(fn)();
  }
}
