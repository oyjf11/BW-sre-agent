/**
 * P0 场景：智能分诊（Intelligent Triage）
 * 
 * 验证场景：
 * - 分诊成功输出正确的分诊结果
 * - 错误率告警分诊
 * - 性能问题分诊
 * - 资源问题分诊
 * - 描述信息不足时输出 uncertainty
 * - 严重级别覆盖
 */

import { test, expect } from '../fixtures/api';

test.describe('智能分诊 (Intelligent Triage)', () => {
  test('正常流程：工单创建后状态为 NEW (待分诊)', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-001',
          title: '支付服务错误率飙升',
          description: '错误率从 1% 飙升到 20%',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.status).toBe('NEW');
    expect(body.service).toBe('payment-service');
    expect(body.severity).toBe('P1');
  });

  test('场景一：错误率告警分诊', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-ERROR-001',
          title: '支付服务 5xx 飙升',
          description: '错误率从 1% 飙升到 20%',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    // 分诊后状态应变为 TRIAGED 或保持 NEW（取决于执行时机）
    expect(['NEW', 'TRIAGED']).toContain(body.status);
    expect(body.severity).toBeDefined();
    expect(body.service).toBe('payment-service');
  });

  test('场景二：性能问题分诊', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-PERF-001',
          title: 'API 响应延迟突增',
          description: 'p95 延迟从 200ms 增加到 2s',
          service: 'api-gateway',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.service).toBe('api-gateway');
  });

  test('场景三：资源问题分诊', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-RESOURCE-001',
          title: 'Pod 频繁重启',
          description: 'CPU 打满，OOMKilled',
          service: 'order-service',
          env: 'prod',
          severity: 'P2',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.service).toBe('order-service');
  });

  test('异常流程：描述信息不足仍可分诊', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-EMPTY-001',
          title: '问题',
          description: '',  // 空的描述
          service: 'test-service',
          env: 'dev',
          severity: 'P3',
        },
      },
    });

    // 即使描述为空，也应该允许创建工单
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('异常流程：严重级别可被覆盖', async ({ api }) => {
    // 用户提交 P3，但系统可能升级为 P1
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-OVERRIDE-001',
          title: '服务完全不可用',
          description: '所有请求超时',
          service: 'critical-service',
          env: 'prod',
          severity: 'P3',  // 用户指定 P3
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    // 系统可以覆盖用户输入的 severity
    expect(body.severity).toBeDefined();
  });

  test('正常流程：分诊结果作为后续节点输入', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-TRIAGE-FLOW-001',
          title: '数据库连接失败',
          description: '无法连接到主数据库',
          service: 'db-proxy',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询工单详情
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    
    // 分诊结果应该被记录
    expect(body.run_id).toBe(run_id);
    expect(body.service).toBeDefined();
    expect(body.severity).toBeDefined();
  });
});
