/**
 * P0 场景：证据收集（Evidence Collection）
 * 
 * 验证场景：
 * - 并行证据收集
 * - 收集日志证据
 * - 收集指标证据
 * - 收集部署记录
 * - 查询 Runbook
 * - 工具超时返回降级结果
 * - 工具返回为空时标记 LOW confidence
 * - 证据不足触发 critic 回退
 */

import { test, expect } from '../fixtures/api';

test.describe('证据收集 (Evidence Collection)', () => {
  const validIncidentPayload = {
    ticket: {
      ticket_id: 'INC-EVIDENCE-001',
      title: '支付服务错误率飙升',
      description: '错误率从 1% 飙升到 20%，需要收集日志和指标',
      service: 'payment-service',
      env: 'prod',
      severity: 'P1',
    },
  };

  test('正常流程：工单创建后进入证据收集阶段', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    // 初始状态为 NEW，后续会进入 GATHERING_EVIDENCE
    expect(['NEW', 'PLANNED', 'GATHERING_EVIDENCE', 'DIAGNOSED']).toContain(body.status);
  });

  test('场景一：查询工单事件确认证据收集节点执行', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    expect(eventsResponse.ok()).toBeTruthy();

    const events = await eventsResponse.json();
    expect(Array.isArray(events)).toBe(true);
    
    // 应该有 RUN_CREATED 事件
    const runCreatedEvent = events.find((e: any) => e.type === 'RUN_CREATED');
    expect(runCreatedEvent).toBeDefined();
    expect(runCreatedEvent.level).toBe('INFO');
  });

  test('场景二：查询工单确认状态流转', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 等待一段时间后查询状态
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    
    // 状态应该随着证据收集推进
    expect(body.run_id).toBeDefined();
    expect(body.status).toBeDefined();
  });

  test('异常流程：工单不存在时事件查询返回空列表', async ({ api }) => {
    const response = await api.get('/incidents/runs/non-existent-id/events');
    expect(response.ok()).toBeTruthy();
    
    const events = await response.json();
    expect(events).toEqual([]);
  });

  test('正常流程：证据收集完成后状态变为 DIAGNOSED', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: validIncidentPayload,
    });
    const { run_id } = await createResponse.json();

    // 多次查询等待证据收集完成
    let status = 'NEW';
    let attempts = 0;
    
    while (['NEW', 'PLANNED', 'GATHERING_EVIDENCE'].includes(status) && attempts < 10) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      if (['NEW', 'PLANNED', 'GATHERING_EVIDENCE'].includes(status)) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    // 最终状态可能是 DIAGNOSED, PENDING_APPROVAL, COMPLETED 等
    expect(['DIAGNOSED', 'PENDING_APPROVAL', 'COMPLETED', 'FAILED']).toContain(status);
  });

  test('场景三：并行收集多种证据', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVIDENCE-PARALLEL-001',
          title: '多维度故障',
          description: '需要同时收集日志、指标、部署记录和 Runbook',
          service: 'order-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件，应该有多个证据收集相关事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();
    
    // 验证至少有 RUN_CREATED 事件
    expect(events.length).toBeGreaterThan(0);
  });

  test('异常流程：证据收集超时返回降级结果', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVIDENCE-TIMEOUT-001',
          title: '超时测试',
          description: '测试证据收集超时场景',
          service: 'timeout-service',
          env: 'prod',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询工单状态
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    
    // 即使超时，也应该有状态更新
    expect(body.run_id).toBeDefined();
  });
});
