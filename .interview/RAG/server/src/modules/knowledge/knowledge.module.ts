import { Module } from '@nestjs/common';
import { DatabaseModule } from '../../database/database.module';
import { EmbeddingService } from './embedding.service';
import { ChunkerService } from './chunker.service';
import { RetrievalService } from './retrieval.service';
import { KnowledgeService } from './knowledge.service';
import { KnowledgeController } from './knowledge.controller';

@Module({
  imports: [DatabaseModule],
  controllers: [KnowledgeController],
  providers: [EmbeddingService, ChunkerService, RetrievalService, KnowledgeService],
  exports: [RetrievalService],
})
export class KnowledgeModule {}
