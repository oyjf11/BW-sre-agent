import { Controller, Post, Get, Delete, Param, Req, Res, UseInterceptors, UploadedFile } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { FileService } from './file.service';
import { memoryStorage } from 'multer';

@Controller('api/files')
export class FileController {
  constructor(private fileService: FileService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file', {
    storage: memoryStorage(),
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
    fileFilter: (_, file, cb) => {
      const allowed = ['.md', '.txt', '.docx'];
      const ext = file.originalname.match(/\.[^.]+$/)?.[0]?.toLowerCase();
      cb(null, allowed.includes(ext || ''));
    },
  }))
  async upload(@Req() req: any, @UploadedFile() file: Express.Multer.File) {
    if (!file) return { error: '不支持的文件类型，请上传 .md/.txt/.docx 文件' };
    // multer 默认用 Latin-1 解码 HTTP 头中的文件名，中文会乱码，需要转回 UTF-8
    file.originalname = Buffer.from(file.originalname, 'latin1').toString('utf8');
    return this.fileService.parseAndSave(req.user.sub, file);
  }

  @Get(':id')
  getAttachment(@Req() req: any, @Param('id') id: string) {
    return this.fileService.getAttachment(Number(id), req.user.sub);
  }

  @Get()
  listFiles(@Req() req: any) {
    return this.fileService.listFiles(req.user.sub);
  }

  @Delete(':id')
  deleteFile(@Req() req: any, @Param('id') id: string) {
    return this.fileService.deleteFile(Number(id), req.user.sub);
  }

  /** 下载文件方式：返回原始文件内容 */
  @Get(':id/download')
  async downloadFile(@Req() req: any, @Param('id') id: string, @Res() res: any) {
    try {
      const { buffer, filename, mimetype } = this.fileService.downloadFile(Number(id), req.user.sub);
      res.set({
        'Content-Type': mimetype,
        'Content-Disposition': `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`,
        'Content-Length': buffer.length,
      });
      res.end(buffer);
    } catch (err: any) {
      res.status(404).json({ error: err.message || '文件不存在' });
    }
  }
}
