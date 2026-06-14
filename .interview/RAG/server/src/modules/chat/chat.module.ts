import { Module } from '@nestjs/common';
import { ChatService } from './chat.service';
import { ChatController } from './chat.controller';
import { AiService } from '../ai/ai.service';
import { UserModule } from '../user/user.module';
import { TicketModule } from '../ticket/ticket.module';
import { KnowledgeModule } from '../knowledge/knowledge.module';

@Module({
  imports: [UserModule, TicketModule, KnowledgeModule],
  providers: [ChatService, AiService],
  controllers: [ChatController],
  exports: [ChatService, AiService],
})
export class ChatModule {}
