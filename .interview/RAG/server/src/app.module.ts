import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { DatabaseModule } from './database/database.module';
import { AuthModule } from './modules/auth/auth.module';
import { UserModule } from './modules/user/user.module';
import { ChatModule } from './modules/chat/chat.module';
import { FileModule } from './modules/file/file.module';
import { PaymentModule } from './modules/payment/payment.module';
import { MultimodalModule } from './modules/multimodal/multimodal.module';
import { TicketModule } from './modules/ticket/ticket.module';
import { KnowledgeModule } from './modules/knowledge/knowledge.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    DatabaseModule,
    AuthModule,
    UserModule,
    ChatModule,
    FileModule,
    PaymentModule,
    MultimodalModule,
    TicketModule,
    KnowledgeModule,
  ],
})
export class AppModule {}
