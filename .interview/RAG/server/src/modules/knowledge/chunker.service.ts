import { Injectable } from '@nestjs/common';
import * as mammoth from 'mammoth';

@Injectable()
export class ChunkerService {
  private readonly CHUNK_SIZE = 600;
  private readonly OVERLAP = 80;
  private readonly MIN_CHUNK_LENGTH = 20;

  async parseFile(buffer: Buffer, filename: string): Promise<string> {
    const ext = (filename.match(/\.[^.]+$/)?.[0] ?? '').toLowerCase();
    if (ext === '.txt' || ext === '.md') {
      return buffer.toString('utf-8');
    }
    if (ext === '.docx') {
      const result = await mammoth.extractRawText({ buffer });
      return result.value;
    }
    throw new Error(`不支持的文件类型: ${ext}，请上传 .txt / .md / .docx`);
  }

  chunkText(text: string): string[] {
    const normalized = text
      .split('\r\n').join('\n')
      .split('\r').join('\n');

    const parts = normalized.split('\n\n');
    const paragraphs: string[] = [];
    let prev = '';
    for (const p of parts) {
      const t = p.trim();
      if (!t) {
        if (prev) {
          paragraphs.push(prev);
          prev = '';
        }
      } else {
        prev = prev ? prev + '\n\n' + t : t;
      }
    }
    if (prev) paragraphs.push(prev);

    const validParagraphs = paragraphs.filter((p) => p.length >= this.MIN_CHUNK_LENGTH);

    const chunks: string[] = [];
    let current = '';

    for (const para of validParagraphs) {
      if (para.length > this.CHUNK_SIZE) {
        if (current) {
          chunks.push(current);
          current = '';
        }
        let i = 0;
        while (i < para.length) {
          const slice = para.slice(i, i + this.CHUNK_SIZE);
          if (slice.trim().length >= this.MIN_CHUNK_LENGTH) {
            chunks.push(slice.trim());
          }
          i += this.CHUNK_SIZE - this.OVERLAP;
        }
        continue;
      }

      const candidate = current ? current + '\n\n' + para : para;
      if (candidate.length <= this.CHUNK_SIZE) {
        current = candidate;
      } else {
        if (current) chunks.push(current);
        const overlap = current.slice(-this.OVERLAP);
        current = overlap ? overlap + '\n\n' + para : para;
      }
    }

    if (current.trim().length >= this.MIN_CHUNK_LENGTH) {
      chunks.push(current.trim());
    }

    return chunks;
  }
}
