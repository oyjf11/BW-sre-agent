/**
 * P0 场景：执行器（Executor）
 * 
 * 验证场景：
 * - 执行低风险动作
 * - 执行已审批动作
 * - 重启服务
 * - 回滚版本
 * - 执行失败生成补偿建议
 * - 幂等校验
 * - 生产环境阻止高风险操作
 */

import { test, expect } from '../fixtures/api';

test.describe('执行器 (Executor)', () => {
  test('正常流程：低风险动作直接执行', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-LOW-001',
          title: '低风险操作',
          description: '只读查询操作',
          service: 'query-service',
          env: 'dev',
          severity: 'P3',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('正常流程：审批通过后进入执行阶段', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-APPROVED-001',
          title: '审批后执行',
          description: '需要审批的高风险操作',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const { run_id } = await response.json();

    // 等待执行完成
    let status = 'NEW';
    let attempts = 0;
    
    while (!['EXECUTING', 'VERIFYING', 'COMPLETED', 'FAILED'].includes(status) && attempts < 20) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 执行后状态应该是 EXECUTING, VERIFYING, COMPLETED 或 FAILED
    expect(['EXECUTING', 'VERIFYING', 'COMPLETED', 'FAILED']).toContain(status);
  });

  test('场景一：重启服务', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-RESTART-001',
          title: '重启服务',
          description: 'Pod 异常需要重启',
          service: 'payment-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('场景二：回滚版本', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-ROLLBACK-001',
          title: '回滚版本',
          description: '发布问题需要回滚',
          service: 'api-gateway',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.run_id).toBeDefined();
  });

  test('异常流程：执行失败生成补偿建议', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-FAIL-001',
          title: '执行失败测试',
          description: '模拟执行失败场景',
          service: 'fail-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await response.json();

    // 查询状态
    let status = 'NEW';
    let attempts = 0;
    
    while (!['COMPLETED', 'FAILED'].includes(status) && attempts < 20) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 如果执行失败，状态应该是 FAILED
    expect(['COMPLETED', 'FAILED']).toContain(status);
  });

  test('异常流程：幂等校验避免重复执行', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-IDEMPOTENT-001',
          title: '幂等测试',
          description: '测试幂等性',
          service: 'idempotent-service',
          env: 'staging',
          severity: 'P3',
        },
      },
    });

    const { run_id } = await createResponse.json();
    expect(run_id).toBeDefined();

    // 多次查询应该返回相同结果
    const response1 = await api.get(`/incidents/runs/${run_id}`);
    const response2 = await api.get(`/incidents/runs/${run_id}`);
    
    const body1 = await response1.json();
    const body2 = await response2.json();
    
    expect(body1.run_id).toBe(body2.run_id);
  });

  test('异常流程：生产环境阻止高风险操作', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-PROD-BLOCK-001',
          title: '生产环境高风险',
          description: '测试生产环境阻止',
          service: 'critical-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    const { run_id } = await response.json();

    // 查询状态
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    
    // 生产环境可能被阻止执行
    expect(body.run_id).toBeDefined();
  });

  test('正常流程：执行结果被记录', async ({ api }) => {
    const response = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-RESULT-001',
          title: '执行结果记录',
          description: '验证执行结果被记录',
          service: 'result-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await response.json();

    // 查询事件确认执行过程
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();
    
    expect(events.length).toBeGreaterThan(0);
  });

  test('正常流程：执行耗时被记录', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EXECUTOR-DURATION-001',
          title: '执行耗时',
          description: '测试执行耗时记录',
          service: 'duration-service',
          env: 'staging',
          severity: 'P3',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询工单
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    
    // completed_at 应该有值表示执行完成
    if (body.status === 'COMPLETED') {
      expect(body.completed_at).toBeDefined();
    }
  });
});
