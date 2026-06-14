import { Controller, Get, Post, Patch, Delete, Param, Body, Req, Query } from '@nestjs/common';
import { UserService } from './user.service';
import { Public } from '../auth/jwt.guard';

@Controller('api')
export class UserController {
  constructor(private userService: UserService) {}

  @Get('user/profile')
  getProfile(@Req() req: any) {
    const user = this.userService.findById(req.user.sub);
    if (!user) return { error: '用户不存在' };
    const { /* api_key: _, */ ...safeUser } = user as any;
    return safeUser;
  }

  @Get('admin/users')
  getUsers(@Req() req: any, @Query('page') page = '1', @Query('pageSize') pageSize = '20') {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.userService.findAll(Number(page), Number(pageSize));
  }

  @Patch('admin/users/:id')
  updateUser(@Req() req: any, @Param('id') id: string, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    return this.userService.update(Number(id), body);
  }

  @Post('admin/users')
  async createLocalUser(@Req() req: any, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    const { username, password, nickname, plan_type, tokens_remaining, is_admin } = body;
    if (!username || !password) {
      return { error: '账号和密码不能为空' };
    }
    try {
      const user = await this.userService.createLocalUser({
        username,
        password,
        nickname,
        plan_type,
        tokens_remaining,
        is_admin,
      });
      const { password_hash: _, ...safeUser } = user as any;
      return safeUser;
    } catch (err: any) {
      return { error: err.message || '创建失败' };
    }
  }

  @Post('admin/users/:id/reset-password')
  async resetPassword(@Req() req: any, @Param('id') id: string, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    const { new_password } = body;
    if (!new_password) {
      return { error: '新密码不能为空' };
    }
    try {
      await this.userService.resetPassword(Number(id), new_password);
      return { ok: true, message: '密码重置成功，用户下次登录需修改密码' };
    } catch (err: any) {
      return { error: err.message || '重置失败' };
    }
  }

  @Patch('admin/users/:id/toggle-disabled')
  toggleDisabled(@Req() req: any, @Param('id') id: string, @Body() body: any) {
    if (!req.user.isAdmin) return { error: '无权限' };
    const { is_disabled } = body;
    if (typeof is_disabled !== 'boolean') {
      return { error: 'is_disabled 必须为布尔值' };
    }
    try {
      const user = this.userService.toggleDisabled(Number(id), is_disabled);
      const { password_hash: _, ...safeUser } = user as any;
      return safeUser;
    } catch (err: any) {
      return { error: err.message || '操作失败' };
    }
  }
}
