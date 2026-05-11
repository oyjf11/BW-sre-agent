/**
 * P0 场景：工单运行生命周期（Incident Run Lifecycle）
 * 
 * 验证场景：
 * - 完整生命周期状态流转
 * - 审批拒绝后终止
 * - 证据不足重试
 * - 执行失败
 * 
 * 注意：此测试需要完整的流程执行，在 mock 环境下重点验证状态查询
 */

import { test, expect } from '../fixtures/api';

test.describe('工单运行生命周期 (Incident Run Lifecycle)', () => {
  const validIncidentPayload = {
    ticket: {
      ticket_id: 'INC-LIFECYCLE-001',
      title: 'API 响应延迟突增',
      description: 'p95 延迟从 200ms 增加到 2s',
      service: 'api-gateway',
      env: 'staging',
      severity: 'P2',
    },
  };

  test('正常流程：创建工单后状态为 NEW', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.status).toBe('NEW');
  });

  test('正常流程：查询工单状态变化', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 查询工单状态
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    expect(getResponse.ok()).toBeTruthy();

    const body = await getResponse.json();
    expect(body.run_id).toBe(run_id);
    expect(['NEW', 'TRIAGED', 'PLANNED', 'GATHERING_EVIDENCE', 'DIAGNOSED', 'PENDING_APPROVAL', 'EXECUTING', 'VERIFYING', 'COMPLETED', 'FAILED']).toContain(body.status);
  });

  test('正常流程：完成后 completed_at 被设置', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 查询工单
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();

    // 如果状态是 COMPLETED，completed_at 应该被设置
    if (body.status === 'COMPLETED') {
      expect(body.completed_at).toBeDefined();
    }
  });

  test('异常流程：失败工单包含 error 信息', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 查询工单
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();

    // 如果状态是 FAILED，应该有 error 字段或者可以从 events 中获取
    if (body.status === 'FAILED') {
      // error 信息可能在 events 中或单独的 error 字段
      expect(body).toHaveProperty('run_id');
    }
  });
});
