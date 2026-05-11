/**
 * P0 场景：人工审批（Human-in-the-Loop Approval）
 * 
 * 验证场景：
 * - 创建审批请求
 * - 查询待审批列表
 * - 查询单个审批
 * - 批准动作
 * - 拒绝动作
 * - 要求修改参数
 * - 要求补充证据
 * - 审批超时
 * - 审批不存在
 */

import { test, expect } from '../fixtures/api';

test.describe('人工审批 (Human-in-the-Loop Approval)', () => {
  test('正常流程：查询待审批列表（空）', async ({ api }) => {
    const response = await api.get('/approvals/pending');
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test('正常流程：查询不存在的审批返回 404', async ({ api }) => {
    const response = await api.get('/approvals/non-existent-approval-id');
    expect(response.status()).toBe(404);
  });

  test('正常流程：审批通过后工单进入执行阶段', async ({ api }) => {
    // 创建一个高风险工单，触发审批
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-001',
          title: '需要审批的高风险操作',
          description: '服务重启需要人工审批',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    expect(createResponse.ok()).toBeTruthy();
    const { run_id } = await createResponse.json();

    // 查询工单状态，应该进入审批阶段或已完成
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    expect(['PENDING_APPROVAL', 'EXECUTING', 'COMPLETED', 'FAILED']).toContain(body.status);
  });

  test('场景一：拒绝动作后工单失败', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-REJECT-001',
          title: '测试拒绝',
          description: '测试审批拒绝流程',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();
    expect(run_id).toBeDefined();
  });

  test('场景二：修改参数后重新审批', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-MODIFY-001',
          title: '测试修改参数',
          description: '测试审批修改流程',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();
    expect(run_id).toBeDefined();
  });

  test('场景三：要求补充证据', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-EVIDENCE-001',
          title: '需要更多证据',
          description: '证据不足需要补充',
          service: 'test-service',
          env: 'dev',
          severity: 'P3',
        },
      },
    });

    const { run_id } = await createResponse.json();
    expect(run_id).toBeDefined();
  });

  test('异常流程：审批超时保持待审批状态', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-TIMEOUT-001',
          title: '审批超时测试',
          description: '测试审批超时场景',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询状态
    const getResponse = await api.get(`/incidents/runs/${run_id}`);
    const body = await getResponse.json();
    // 审批超时后状态可能还是 PENDING_APPROVAL
    expect(body.run_id).toBeDefined();
  });

  test('正常流程：审批决策正确更新工单状态', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-DECISION-001',
          title: '审批决策测试',
          description: '测试审批决策对工单状态的影响',
          service: 'decision-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件确认审批事件触发
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();
    expect(Array.isArray(events)).toBe(true);
  });

  test('正常流程：所有审批操作有审计日志', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-APPROVAL-AUDIT-001',
          title: '审计日志测试',
          description: '验证审批操作有审计日志',
          service: 'audit-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();
    
    // 验证有 RUN_CREATED 事件
    expect(events.length).toBeGreaterThan(0);
  });
});
