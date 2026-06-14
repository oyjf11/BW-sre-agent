import { Controller, Get, Patch, Param, Body, Req, Query } from '@nestjs/common';
import { TicketService } from './ticket.service';

@Controller('api')
export class TicketController {
  constructor(private readonly ticketService: TicketService) {}

  /** GET /api/admin/tickets?page=1  管理员查看所有工单 */
  @Get('admin/tickets')
  getAdminTickets(@Req() req: any, @Query('page') page = '1') {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.ticketService.getAdminTickets(Number(page));
  }

  /** PATCH /api/admin/tickets/:id  管理员更新工单状态/备注 */
  @Patch('admin/tickets/:id')
  updateTicket(@Req() req: any, @Param('id') id: string, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.ticketService.updateTicket(Number(id), {
      status: body.status,
      admin_notes: body.admin_notes,
    });
  }

  /** GET /api/tickets/mine  用户查看自己的工单 */
  @Get('tickets/mine')
  getMyTickets(@Req() req: any) {
    return this.ticketService.getUserTickets(req.user.sub);
  }
}
