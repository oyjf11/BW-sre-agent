/**
 * P0 场景：工单创建（Incident Create）
 * 
 * 验证场景：
 * - 正常流程：创建工单
 * - 查询工单列表
 * - 查询单个工单
 * - 异常流程：必填字段缺失
 * - 异常流程：工单 ID 重复
 */

import { test, expect } from '../fixtures/api';

test.describe('工单创建 (Incident Create)', () => {
  const validIncidentPayload = {
    ticket: {
      ticket_id: 'INC-2024-001',
      title: '支付服务 5xx 飙升',
      description: '错误率从 1% 飙升到 20%',
      service: 'payment-service',
      env: 'prod',
      severity: 'P1',
      source: 'manual',
    },
  };

  test('正常流程：创建工单成功', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body).toHaveProperty('run_id');
    expect(body).toHaveProperty('thread_id');
    expect(body.status).toBe('NEW');
    expect(body.severity).toBe('P1');
    expect(body.service).toBe('payment-service');
    expect(body.env).toBe('prod');
    expect(body).toHaveProperty('created_at');
  });

  test('正常流程：查询工单列表', async ({ api }) => {
    // 先创建一个工单
    await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    // 查询列表
    const response = await api.get('/incidents/runs');
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
    expect(body[0]).toHaveProperty('run_id');
    expect(body[0]).toHaveProperty('status');
  });

  test('正常流程：查询单个工单', async ({ api }) => {
    // 先创建一个工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 查询单个工单
    const response = await api.get(`/incidents/runs/${run_id}`);
    expect(response.ok()).toBeTruthy();

    const body = await response.json();
    expect(body.run_id).toBe(run_id);
    expect(body.status).toBe('NEW');
  });

  test('异常流程：查询不存在的工单返回 404', async ({ api }) => {
    const response = await api.get('/incidents/runs/non-existent-run-id');
    expect(response.status()).toBe(404);
  });

  test('异常流程：必填字段缺失返回 422', async ({ api }) => {
    const invalidPayload = {
      ticket: {
        // 缺少 ticket_id, title, description 等必填字段
        service: 'payment-service',
        env: 'prod',
        severity: 'P1',
      },
    };

    const response = await api.post('/incidents/runs', {
      data: invalidPayload,
    });

    // Pydantic 会返回 422 而不是 200
    expect([400, 422]).toContain(response.status());
  });

  test('异常流程：工单 ID 重复允许创建', async ({ api }) => {
    // 创建第一个工单
    await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    // 使用相同 ticket_id 创建第二个工单
    const response = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body).toHaveProperty('run_id');
    // 两个工单的 run_id 应该不同
  });
});
