import { Injectable, Logger, BadRequestException, ServiceUnavailableException, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { DatabaseService } from '../../database/database.service';
import { UserService } from '../user/user.service';
import axios, { AxiosError } from 'axios';

const SSO_BASE = 'https://aibook.mvtable.com';

/** 提取 aibook 返回的错误消息 */
function extractSsoError(err: any): string {
  if (err instanceof AxiosError) {
    const data = err.response?.data;
    if (typeof data === 'object' && data?.error) return data.error as string;
    if (typeof data === 'string') return data;
    if (err.code === 'ECONNABORTED') return 'aibook SSO 服务超时，请稍后重试';
    if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED') return 'aibook SSO 服务无法连接';
  }
  return err?.message || 'SSO 服务异常';
}

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private config: ConfigService,
    private jwtService: JwtService,
    private db: DatabaseService,
    private userService: UserService,
  ) {}

  /** PC 端：获取微信扫码二维码 */
  async getSsoQrCode(redirectUri: string): Promise<{ state: string; qrDataUrl: string; expiresIn: number }> {
    const appId = this.config.get('AIBOOK_APP_ID');
    const state = `sso_${Date.now()}_${Math.random().toString(36).slice(2)}`;

    try {
      const res = await axios.get(`${SSO_BASE}/api/sso/login`, {
        params: { app_id: appId, redirect_uri: redirectUri, state, mode: 'qr' },
        timeout: 10000,
      });
      return {
        state: res.data.state || state,
        qrDataUrl: res.data.qrDataUrl,
        expiresIn: res.data.expires_in || 600,
      };
    } catch (err: any) {
      const msg = extractSsoError(err);
      this.logger.error(`[SSO] 获取二维码失败: ${msg}`);
      throw new BadRequestException(`无法获取登录二维码：${msg}`);
    }
  }

  /** PC 端：轮询扫码结果 */
  async pollSsoState(state: string): Promise<{ done: boolean; expired?: boolean; token?: string }> {
    try {
      const res = await axios.get(`${SSO_BASE}/api/sso/poll`, {
        params: { state },
        timeout: 5000,
      });
      return res.data;
    } catch (err: any) {
      const msg = extractSsoError(err);
      this.logger.warn(`[SSO] 轮询状态失败: ${msg}`);
      // 轮询错误不报 500，返回 expired 防止前端死循环
      return { done: false, expired: true };
    }
  }

  /** 验证 aibook SSO token，获取或创建用户，返回本地 JWT */
  async verifySsoToken(token: string): Promise<{ accessToken: string; user: any }> {
    const appId = this.config.get('AIBOOK_APP_ID');
    const appSecret = this.config.get('AIBOOK_APP_SECRET');

    // 调用 aibook verify 接口
    let verifyRes: any;
    try {
      verifyRes = await axios.post(`${SSO_BASE}/api/sso/verify`, {
        app_id: appId,
        app_secret: appSecret,
        token,
      });
    } catch (err: any) {
      const msg = extractSsoError(err);
      this.logger.error(`[SSO] 验证 token 失败: ${msg}`);
      throw new BadRequestException(`SSO Token 验证失败：${msg}`);
    }

    if (!verifyRes.data.ok) {
      throw new BadRequestException(verifyRes.data.error || '验证失败');
    }

    const { openid, nickname, avatar, plan_type, is_member } = verifyRes.data.user;

    // 按会员等级确定初始 token 额度（仅新用户建档时赋予）
    const initialTokens =
      plan_type === 'pro'  ? 30000 :
      plan_type === 'plus' ? 10000 : 1000;

    // 查找或创建本地用户
    let user = this.db.get('SELECT * FROM users WHERE openid = ?', [openid]);
    if (!user) {
      this.db.run(
        'INSERT INTO users (openid, nickname, avatar, plan_type, is_member, tokens_remaining) VALUES (?, ?, ?, ?, ?, ?)',
        [openid, nickname, avatar, plan_type, is_member ? 1 : 0, initialTokens],
      );
      user = this.db.get('SELECT * FROM users WHERE openid = ?', [openid]);
    } else {
      // 同步昵称和头像（is_member 不同步，只由本应用内购买行为改变）
      this.db.run(
        'UPDATE users SET nickname=?, avatar=?, plan_type=?, updated_at=CURRENT_TIMESTAMP WHERE openid=?',
        [nickname, avatar, plan_type, openid],
      );
      user = this.db.get('SELECT * FROM users WHERE openid = ?', [openid]);
    }

    const accessToken = this.jwtService.sign({
      sub: user.id,
      openid: user.openid,
      nickname: user.nickname,
      avatar: user.avatar,
      isAdmin: user.is_admin === 1,
    });

    return { accessToken, user };
  }

  /** 移动端 SSO 跳转 URL */
  getMobileSsoUrl(redirectUri: string): string {
    const appId = this.config.get('AIBOOK_APP_ID');
    const state = `sso_mob_${Date.now()}`;
    return (
      `${SSO_BASE}/api/sso/login` +
      `?app_id=${appId}` +
      `&redirect_uri=${encodeURIComponent(redirectUri)}` +
      `&state=${state}` +
      `&mode=redirect`
    );
  }

  /** 本地管理员登录（跳过 SSO） */
  async loginAsAdmin(username: string, password: string): Promise<{ accessToken: string; user: any }> {
    const cfgUser = this.config.get('ADMIN_USERNAME', 'admin');
    const cfgPass = this.config.get('ADMIN_PASSWORD', '');

    if (!cfgPass) throw new Error('管理员本地登录未启用，请在 .env 中配置 ADMIN_PASSWORD');
    if (username !== cfgUser || password !== cfgPass) throw new Error('账号或密码错误');

    // 获取或创建本地管理员虚拟账号
    const ADMIN_OPENID = '__admin_local__';
    let user: any = this.db.get('SELECT * FROM users WHERE openid=?', [ADMIN_OPENID]);
    if (!user) {
      this.db.run(
        'INSERT INTO users (openid, nickname, is_admin, tokens_remaining) VALUES (?,?,1,999999999)',
        [ADMIN_OPENID, '本地管理员'],
      );
      user = this.db.get('SELECT * FROM users WHERE openid=?', [ADMIN_OPENID]);
    } else if (!user.is_admin) {
      // 确保 is_admin = 1
      this.db.run('UPDATE users SET is_admin=1 WHERE openid=?', [ADMIN_OPENID]);
      user = this.db.get('SELECT * FROM users WHERE openid=?', [ADMIN_OPENID]);
    }

    const accessToken = this.jwtService.sign({
      sub: user.id,
      openid: user.openid,
      nickname: user.nickname,
      avatar: null,
      isAdmin: true,
    });

    return { accessToken, user };
  }

  /** 本地用户登录（账号密码） */
  async loginLocalUser(username: string, password: string): Promise<{
    accessToken: string;
    user: any;
    mustChangePassword: boolean;
  }> {
    const user = await this.userService.verifyPassword(username, password);
    if (!user) {
      throw new UnauthorizedException('账号或密码错误');
    }

    const accessToken = this.jwtService.sign({
      sub: user.id,
      openid: `local_${user.username}`,
      nickname: user.nickname,
      avatar: user.avatar,
      isAdmin: user.is_admin === 1,
    });

    return {
      accessToken,
      user: {
        id: user.id,
        nickname: user.nickname,
        avatar: user.avatar,
        is_admin: user.is_admin,
        plan_type: user.plan_type,
        tokens_remaining: user.tokens_remaining,
      },
      mustChangePassword: user.must_change_password === 1,
    };
  }

  /** 本地用户修改密码 */
  async changeLocalPassword(userId: number, oldPassword: string, newPassword: string) {
    // 验证旧密码
    const user = this.db.get('SELECT * FROM users WHERE id = ?', [userId]) as any;
    if (!user || user.user_type !== 'local') {
      throw new BadRequestException('用户不存在或非本地用户');
    }

    const valid = await this.userService.verifyPassword(user.username, oldPassword);
    if (!valid) {
      throw new BadRequestException('旧密码错误');
    }

    // 更新密码
    await this.userService.updatePassword(userId, newPassword);
  }
}
