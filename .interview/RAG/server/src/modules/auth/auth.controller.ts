import { Controller, Get, Post, Query, Body, Res, Req } from '@nestjs/common';
import type { Response, Request } from 'express';
import { AuthService } from './auth.service';
import { Public } from './jwt.guard';
import { ConfigService } from '@nestjs/config';

@Controller('api/auth')
export class AuthController {
  constructor(
    private authService: AuthService,
    private config: ConfigService,
  ) {}

  /** PC 端：获取微信扫码二维码 */
  @Public()
  @Get('sso/qr')
  async getSsoQr(@Query('redirect_uri') redirectUri: string) {
    const clientUrl = this.config.get('CLIENT_URL', 'http://localhost:5173');
    const callbackUrl = redirectUri || `${clientUrl}/auth/callback`;
    return this.authService.getSsoQrCode(callbackUrl);
  }

  /** PC 端：轮询扫码状态 */
  @Public()
  @Get('sso/poll')
  async pollSso(@Query('state') state: string) {
    return this.authService.pollSsoState(state);
  }

  /** 验证 SSO token，返回本地 JWT */
  @Public()
  @Post('verify')
  async verifyToken(@Body('token') token: string) {
    return this.authService.verifySsoToken(token);
  }

  /** 移动端 SSO 跳转 */
  @Public()
  @Get('sso/mobile')
  mobileLogin(@Query('redirect_uri') redirectUri: string, @Res() res: Response) {
    const url = this.authService.getMobileSsoUrl(redirectUri);
    return res.redirect(url);
  }

  /** 本地管理员登录（跳过 SSO，适用于本地开发/运维） */
  @Public()
  @Post('admin/login')
  async adminLogin(
    @Body('username') username: string,
    @Body('password') password: string,
  ) {
    try {
      return await this.authService.loginAsAdmin(username, password);
    } catch (err: any) {
      return { error: err.message || '登录失败' };
    }
  }

  /** 本地用户登录（账号密码） */
  @Public()
  @Post('local/login')
  async localLogin(
    @Body('username') username: string,
    @Body('password') password: string,
  ) {
    try {
      return await this.authService.loginLocalUser(username, password);
    } catch (err: any) {
      return { error: err.message || '登录失败' };
    }
  }

  /** 本地用户首次登录修改密码 */
  @Post('local/change-password')
  async changePassword(
    @Req() req: any,
    @Body('old_password') oldPassword: string,
    @Body('new_password') newPassword: string,
  ) {
    try {
      await this.authService.changeLocalPassword(req.user.sub, oldPassword, newPassword);
      return { ok: true, message: '密码修改成功' };
    } catch (err: any) {
      return { error: err.message || '修改失败' };
    }
  }

  /** 获取当前登录用户信息 */
  @Get('me')
  getMe(@Req() req: Request & { user: any }) {
    return { user: req.user };
  }
}
