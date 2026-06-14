import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { DatabaseService } from '../../database/database.service';
import * as crypto from 'crypto';
import axios from 'axios';

const JITPAY_BASE = 'https://pay.pxcharts.com';

// 套餐配置（单位：分）
export const PLANS = {
  experience: { name: '体验券', amount: 990, tokens: 50000, plan_type: 'experience' },
  source: { name: '整套源码解决方案', amount: 49900, tokens: 0, plan_type: 'source' },
};

@Injectable()
export class PaymentService {
  private readonly logger = new Logger(PaymentService.name);

  constructor(
    private config: ConfigService,
    private db: DatabaseService,
  ) {}

  private jitpay(method: string, path: string, body?: any) {
    const appKey = this.config.get('JITPAY_APP_KEY');
    const appSecret = this.config.get('JITPAY_APP_SECRET');
    const timestamp = String(Math.floor(Date.now() / 1000));
    const nonce = crypto.randomBytes(16).toString('hex');
    const bodyStr = body ? JSON.stringify(body) : '';
    const bodyHash = crypto.createHash('sha256').update(bodyStr, 'utf8').digest('hex');
    const signStr = `${method}\n${path}\n${timestamp}\n${nonce}\n${bodyHash}\n`;
    const signature = crypto.createHmac('sha256', appSecret).update(signStr).digest('hex');
    return axios({
      method,
      url: JITPAY_BASE + path,
      data: body,
      headers: {
        'Content-Type': 'application/json',
        'X-App-Key': appKey,
        'X-Timestamp': timestamp,
        'X-Nonce': nonce,
        'X-Signature': signature,
      },
      timeout: 15000,
    });
  }

  private generateOutTradeNo(): string {
    return `AI${Date.now()}${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
  }

  /** PC 端 NATIVE 扫码支付 */
  async createNativeOrder(userId: number, planKey: string) {
    const plan = PLANS[planKey as keyof typeof PLANS];
    if (!plan) throw new Error('套餐不存在');

    const outTradeNo = this.generateOutTradeNo();

    const result = await this.jitpay('POST', '/v1/pay/create', {
      pay_type: 'NATIVE',
      out_trade_no: outTradeNo,
      amount: plan.amount,
      description: `AI Chat ${plan.name}`,
    });

    // 保存订单
    this.db.run(
      'INSERT INTO orders (user_id, out_trade_no, order_no, amount, plan_type, status) VALUES (?,?,?,?,?,?)',
      [userId, outTradeNo, result.data.order_no, plan.amount, plan.plan_type, 'pending'],
    );

    return {
      codeUrl: result.data.code_url,
      orderNo: result.data.order_no,
      outTradeNo,
      amount: plan.amount,
      planName: plan.name,
    };
  }

  /** 移动端 JSAPI 支付 */
  async createJsapiOrder(userId: number, planKey: string, openid: string) {
    const plan = PLANS[planKey as keyof typeof PLANS];
    if (!plan) throw new Error('套餐不存在');

    const outTradeNo = this.generateOutTradeNo();

    const result = await this.jitpay('POST', '/v1/pay/create', {
      pay_type: 'JSAPI',
      openid,
      out_trade_no: outTradeNo,
      amount: plan.amount,
      description: `AI Chat ${plan.name}`,
    });

    this.db.run(
      'INSERT INTO orders (user_id, out_trade_no, order_no, amount, plan_type, status) VALUES (?,?,?,?,?,?)',
      [userId, outTradeNo, result.data.order_no, plan.amount, plan.plan_type, 'pending'],
    );

    return {
      jsapiParams: result.data.jsapi_params,
      orderNo: result.data.order_no,
      outTradeNo,
    };
  }

  /** 查询支付状态
   *
   * 设计要点：先查本地 orders 表而不是直接透传 JitPay API。
   * 原因：JitPay 的状态 API 可能在回调尚未送达本服务器时已返回 "paid"，
   * 若前端据此立刻 fetchProfile，会拿到尚未升级的旧用户数据（竞态条件）。
   * 只有本地 DB 确认 paid（= handleCallback 已执行、用户权益已升级），
   * 前端才应触发 fetchProfile。
   */
  async queryStatus(orderNo: string) {
    // ① 查本地订单表
    const order = this.db.get(
      'SELECT status, out_trade_no, user_id, plan_type FROM orders WHERE order_no=?',
      [orderNo],
    ) as any;

    // 本地已 paid → callback 已处理、用户权益已升级，直接返回
    if (order?.status === 'paid') return { status: 'paid' };

    // ② 本地未 paid，查 JitPay 获取最新状态
    try {
      const result = await this.jitpay('GET', `/v1/pay/status/${orderNo}`);
      const jitStatus = result.data?.status;

      // JitPay 已 paid 但本地回调尚未到达（或丢失）→ 主动补偿处理
      if (jitStatus === 'paid' && order) {
        await this.handleCallback({
          order_no: orderNo,
          out_trade_no: order.out_trade_no,
          status: 'paid',
          transaction_id: result.data?.transaction_id ?? `manual_${Date.now()}`,
        });
        return { status: 'paid' };
      }

      return { status: jitStatus || 'pending' };
    } catch {
      // JitPay 查询失败时回退到本地状态
      return { status: order?.status || 'pending' };
    }
  }

  /** JitPay 回调处理 */
  async handleCallback(body: any) {
    const { order_no, out_trade_no, status, transaction_id } = body;
    if (status !== 'paid') return { code: 0 };

    const order = this.db.get('SELECT * FROM orders WHERE out_trade_no=?', [out_trade_no]) as any;
    if (!order || order.status === 'paid') return { code: 0 };

    this.db.run(
      'UPDATE orders SET status=?, transaction_id=?, paid_at=CURRENT_TIMESTAMP WHERE out_trade_no=?',
      ['paid', transaction_id, out_trade_no],
    );

    // 升级用户权益
    const plan = Object.values(PLANS).find(p => p.plan_type === order.plan_type);
    if (plan) {
      this.db.run(
        'UPDATE users SET plan_type=?, is_member=1, tokens_remaining=tokens_remaining+?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        [plan.plan_type, plan.tokens, order.user_id],
      );
    }

    this.logger.log(`支付成功: ${out_trade_no}, 用户: ${order.user_id}`);
    return { code: 0 };
  }

  /** 获取订单列表（管理员） */
  getOrders(page = 1, pageSize = 20) {
    const offset = (page - 1) * pageSize;
    const total = (this.db.get('SELECT COUNT(*) as c FROM orders') as any).c;
    const list = this.db.all(
      `SELECT o.*, u.nickname, u.openid FROM orders o
       LEFT JOIN users u ON o.user_id = u.id
       ORDER BY o.created_at DESC LIMIT ? OFFSET ?`,
      [pageSize, offset],
    );
    return { list, total, page, pageSize };
  }

  getUserOrders(userId: number) {
    return this.db.all('SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 20', [userId]);
  }
}
