import { Controller, Post, Get, Param, Body, Req, Query } from '@nestjs/common';
import { PaymentService, PLANS } from './payment.service';
import { Public } from '../auth/jwt.guard';

@Controller('api/pay')
export class PaymentController {
  constructor(private paymentService: PaymentService) {}

  /** 获取套餐列表 */
  @Public()
  @Get('plans')
  getPlans() {
    return Object.entries(PLANS).map(([key, plan]) => ({ key, ...plan }));
  }

  /** PC 端创建 NATIVE 扫码订单 */
  @Post('native')
  async createNative(@Req() req: any, @Body('plan') plan: string) {
    return this.paymentService.createNativeOrder(req.user.sub, plan);
  }

  /** 移动端创建 JSAPI 订单 */
  @Post('jsapi')
  async createJsapi(@Req() req: any, @Body('plan') plan: string) {
    const openid = req.user.openid;
    return this.paymentService.createJsapiOrder(req.user.sub, plan, openid);
  }

  /** 查询支付状态 */
  @Get('status/:orderNo')
  async queryStatus(@Param('orderNo') orderNo: string) {
    return this.paymentService.queryStatus(orderNo);
  }

  /** 支付回调（JitPay 主动推送） */
  @Public()
  @Post('callback')
  async handleCallback(@Body() body: any) {
    return this.paymentService.handleCallback(body);
  }

  /** 用户订单历史 */
  @Get('orders/mine')
  getUserOrders(@Req() req: any) {
    return this.paymentService.getUserOrders(req.user.sub);
  }

  /** 管理员获取所有订单 */
  @Get('orders/admin')
  getAdminOrders(@Req() req: any, @Query('page') page = '1') {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.paymentService.getOrders(Number(page));
  }
}
