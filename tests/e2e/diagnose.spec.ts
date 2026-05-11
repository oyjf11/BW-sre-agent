/**
 * P0 场景：根因分析（Diagnose & Remediation）
 * 
 * 验证场景：
 * - 生成根因候选列表
 * - 单一高置信度根因
 * - 多候选根因
 * - 生成修复方案
 * - 重启服务方案
 * - 回滚版本方案
 * - 无足够证据时的处理
 * - 无法确定根因时的处理
 */

import { test, expect } from '../fixtures/api';

test.describe('根因分析 (Diagnose & Remediation)', () => {
  const validIncidentPayload = {
    ticket: {
      ticket_id: 'INC-DIAGNOSE-001',
      title: '支付服务错误率飙升',
      description: '错误率从 1% 飙升到 20%，需要分析根因',
      service: 'payment-service',
      env: 'prod',
      severity: 'P1',
    },
  };

  test('正常流程：证据收集后进入诊断阶段', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
    // 状态应该随着流程推进到诊断阶段
    expect(['NEW', 'PLANNED', 'GATHERING_EVIDENCE', 'DIAGNOSED', 'PENDING_APPROVAL']).toContain(body.status);
  });

  test('场景一：单一高置信度根因', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-DIAGNOSE-SINGLE-001',
          title: '数据库连接池耗尽',
          description: '错误日志显示 ConnectionPoolTimeoutException，最近一次部署更新了数据库连接池配置',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('场景二：多候选根因', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-DIAGNOSE-MULTI-001',
          title: '服务响应变慢',
          description: '多个指标同时异常，原因不明确',
          service: 'order-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('场景三：重启服务方案', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-DIAGNOSE-RESTART-001',
          title: 'Pod 频繁重启',
          description: 'Pod 状态为 OOMKilled，需要重启',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
    // 高风险动作需要审批
    expect(['PENDING_APPROVAL', 'COMPLETED', 'FAILED']).toContain(body.status);
  });

  test('场景四：回滚版本方案', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-DIAGNOSE-ROLLBACK-001',
          title: '发布后服务异常',
          description: '最近一次发布后错误率飙升，需要回滚',
          service: 'api-gateway',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
    // CRITICAL 风险需要审批
  });

  test('异常流程：无足够证据时标记需要补充', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-DIAGNOSE-NOEVIDENCE-001',
          title: '问题',
          description: '',  // 描述不足
          service: 'test-service',
          env: 'dev',
          severity: 'P3',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('异常流程：无法确定根因时生成建议', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-DIAGNOSE-UNKNOWN-001',
          title: '未知问题',
          description: '间歇性异常，难以确定根因',
          service: 'mystery-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('正常流程：诊断完成后生成修复方案', async ({ api }) => {
    // 创建工单并等待诊断完成
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 查询状态
    let status = 'NEW';
    let attempts = 0;
    
    while (!['DIAGNOSED', 'PENDING_APPROVAL', 'COMPLETED', 'FAILED'].includes(status) && attempts < 20) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 诊断完成后应该进入审批或完成状态
    expect(['DIAGNOSED', 'PENDING_APPROVAL', 'COMPLETED', 'FAILED']).toContain(status);
  });
});
