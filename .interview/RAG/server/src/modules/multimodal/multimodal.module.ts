import { Module } from '@nestjs/common';
import { MultimodalController } from './multimodal.controller';
import { MultimodalService } from './multimodal.service';
import { ChatModule } from '../chat/chat.module';   // 提供 ChatService + AiService
import { UserModule } from '../user/user.module';   // 提供 UserService

@Module({
  imports: [ChatModule, UserModule],
  controllers: [MultimodalController],
  providers: [MultimodalService],
})
export class MultimodalModule {}
