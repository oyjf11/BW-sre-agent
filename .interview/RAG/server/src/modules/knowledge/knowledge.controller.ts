import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Param,
  Body,
  Req,
  UseInterceptors,
  UploadedFile,
  ParseIntPipe,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { memoryStorage } from 'multer';
import { KnowledgeService } from './knowledge.service';

@Controller('api/knowledge')
export class KnowledgeController {
  constructor(private ks: KnowledgeService) {}

  // ── 知识库 ──

  @Post('bases')
  createBase(@Req() req: any, @Body() body: any) {
    const { name, description, is_public } = body;
    if (!name?.trim()) throw new HttpException('知识库名称不能为空', HttpStatus.BAD_REQUEST);
    const isAdmin = req.user?.isAdmin === true;
    return this.ks.createKnowledgeBase(
      is_public && isAdmin ? null : req.user.sub,
      name.trim(),
      description ?? '',
      isAdmin && !!is_public,
    );
  }

  @Get('bases')
  listBases(@Req() req: any) {
    const isAdmin = req.user?.isAdmin === true;
    return this.ks.listKnowledgeBases(req.user.sub, isAdmin);
  }

  @Get('analytics')
  getAnalytics(@Req() req: any) {
    return this.ks.getAnalytics(req.user.sub, req.user?.isAdmin === true);
  }

  @Get('bases/:id')
  getBase(@Param('id', ParseIntPipe) id: number) {
    const kb = this.ks.getKnowledgeBase(id);
    if (!kb) throw new HttpException('知识库不存在', HttpStatus.NOT_FOUND);
    return kb;
  }

  @Put('bases/:id')
  updateBase(
    @Req() req: any,
    @Param('id', ParseIntPipe) id: number,
    @Body() body: any,
  ) {
    return this.ks.updateKnowledgeBase(id, req.user.sub, req.user?.isAdmin === true, body);
  }

  @Delete('bases/:id')
  deleteBase(@Req() req: any, @Param('id', ParseIntPipe) id: number) {
    return this.ks.deleteKnowledgeBase(id, req.user.sub, req.user?.isAdmin === true);
  }

  // ── 文档 ──

  @Get('bases/:id/documents')
  listDocuments(@Param('id', ParseIntPipe) id: number) {
    return this.ks.listDocuments(id);
  }

  @Get('bases/:id/status')
  getStatus(@Param('id', ParseIntPipe) id: number) {
    return this.ks.getDocumentStatus(id);
  }

  @Post('bases/:id/documents')
  @UseInterceptors(
    FileInterceptor('file', {
      storage: memoryStorage(),
      limits: { fileSize: 20 * 1024 * 1024 }, // 20 MB
      fileFilter: (_, file, cb) => {
        const allowed = ['.md', '.txt', '.docx'];
        const ext = file.originalname.match(/\.[^.]+$/)?.[0]?.toLowerCase();
        cb(null, allowed.includes(ext ?? ''));
      },
    }),
  )
  async uploadDocument(
    @Req() req: any,
    @Param('id', ParseIntPipe) kbId: number,
    @UploadedFile() file: Express.Multer.File,
  ) {
    if (!file) {
      throw new HttpException(
        '不支持的文件类型，请上传 .txt / .md / .docx',
        HttpStatus.BAD_REQUEST,
      );
    }
    return this.ks.indexDocument(
      kbId,
      file.originalname,
      file.buffer,
      req.user.sub,
      req.user?.isAdmin === true,
    );
  }

  @Delete('bases/:kbId/documents/:docId')
  deleteDocument(
    @Req() req: any,
    @Param('kbId', ParseIntPipe) kbId: number,
    @Param('docId', ParseIntPipe) docId: number,
  ) {
    return this.ks.deleteDocument(docId, kbId, req.user.sub, req.user?.isAdmin === true);
  }

  @Get('bases/:kbId/documents/:docId/chunks')
  listChunks(
    @Param('kbId', ParseIntPipe) kbId: number,
    @Param('docId', ParseIntPipe) docId: number,
  ) {
    return this.ks.listChunks(docId, kbId);
  }

  @Get('bases/:kbId/documents/:docId/preview')
  getDocumentPreview(
    @Param('kbId', ParseIntPipe) kbId: number,
    @Param('docId', ParseIntPipe) docId: number,
  ) {
    return this.ks.getDocumentPreview(docId, kbId);
  }
}
