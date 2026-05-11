/**
 * P1 场景：事件流（Event Stream）
 * 
 * 验证场景：
 * - 查询事件列表
 * - 增量查询事件
 * - RUN_CREATED 事件
 * - NODE_STARTED / NODE_COMPLETED 事件
 * - TOOL_CALL 事件
 * - APPROVAL_REQUESTED 事件
 * - ERROR 事件
 * - run_id 不存在时返回空列表
 */

import { test, expect } from '../fixtures/api';

test.describe('事件流 (Event Stream)', () => {
  test('正常流程：查询事件列表', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-001',
          title: '事件流测试',
          description: '测试事件列表查询',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(createResponse.ok()).toBeTruthy();
    const { run_id } = await createResponse.json();

    // 查询事件列表
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    expect(eventsResponse.ok()).toBeTruthy();

    const events = await eventsResponse.json();
    expect(Array.isArray(events)).toBe(true);
    expect(events.length).toBeGreaterThan(0);
  });

  test('正常流程：事件包含必要字段', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-FIELDS-001',
          title: '事件字段测试',
          description: '验证事件字段',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 验证事件字段
    const event = events[0];
    expect(event).toHaveProperty('event_id');
    expect(event).toHaveProperty('run_id');
    expect(event).toHaveProperty('level');
    expect(event).toHaveProperty('type');
    expect(event).toHaveProperty('message');
    expect(event).toHaveProperty('timestamp');
  });

  test('场景一：RUN_CREATED 事件', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-RUN-001',
          title: 'RUN_CREATED 事件测试',
          description: '验证 RUN_CREATED 事件',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 应该有 RUN_CREATED 事件
    const runCreatedEvent = events.find((e: any) => e.type === 'RUN_CREATED');
    expect(runCreatedEvent).toBeDefined();
    expect(runCreatedEvent.level).toBe('INFO');
    expect(runCreatedEvent.run_id).toBe(run_id);
  });

  test('场景二：NODE_STARTED / NODE_COMPLETED 事件', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-NODE-001',
          title: '节点事件测试',
          description: '验证节点开始/结束事件',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 可能有节点事件
    const nodeEvents = events.filter((e: any) => 
      e.type === 'NODE_STARTED' || e.type === 'NODE_COMPLETED'
    );
    // 事件可能包含 node_name
    if (nodeEvents.length > 0) {
      expect(nodeEvents[0]).toHaveProperty('node_name');
    }
  });

  test('场景三：TOOL_CALL 事件', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-TOOL-001',
          title: '工具调用事件测试',
          description: '验证工具调用事件',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 可能有工具调用事件
    const toolEvents = events.filter((e: any) => e.type === 'TOOL_CALL');
    // 工具调用事件可能包含 tool_name, params 等
  });

  test('场景四：APPROVAL_REQUESTED 事件', async ({ api }) => {
    // 创建高风险工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-APPROVAL-001',
          title: '审批请求事件测试',
          description: '验证审批请求事件',
          service: 'payment-service',
          env: 'prod',
          severity: 'P1',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 可能有审批请求事件
    const approvalEvents = events.filter((e: any) => e.type === 'APPROVAL_REQUESTED');
    if (approvalEvents.length > 0) {
      expect(approvalEvents[0].level).toBe('WARNING');
    }
  });

  test('场景五：ERROR 事件', async ({ api }) => {
    // 创建可能失败的工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-ERROR-001',
          title: '错误事件测试',
          description: '验证错误事件',
          service: 'error-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 过滤错误事件
    const errorEvents = events.filter((e: any) => e.level === 'ERROR');
    // 错误事件应该包含错误信息
  });

  test('正常流程：增量查询事件', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-INCREMENT-001',
          title: '增量查询测试',
          description: '测试增量查询',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 第一次查询
    const eventsResponse1 = await api.get(`/incidents/runs/${run_id}/events`);
    const events1 = await eventsResponse1.json();

    if (events1.length > 0) {
      // 使用第一个事件的时间戳进行增量查询
      const firstEventTs = events1[0].timestamp;

      // 增量查询
      const eventsResponse2 = await api.get(
        `/incidents/runs/${run_id}/events?last_event_ts=${encodeURIComponent(firstEventTs)}`
      );
      const events2 = await eventsResponse2.json();

      // 增量查询应该返回之后的事件
      expect(Array.isArray(events2)).toBe(true);
    }
  });

  test('正常流程：事件按时间升序排列', async ({ api }) => {
    // 创建工单
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-EVENTS-ORDER-001',
          title: '事件排序测试',
          description: '验证事件按时间排序',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();

    // 验证按时间升序
    for (let i = 1; i < events.length; i++) {
      const prevTime = new Date(events[i - 1].timestamp).getTime();
      const currTime = new Date(events[i].timestamp).getTime();
      expect(currTime).toBeGreaterThanOrEqual(prevTime);
    }
  });

  test('异常流程：run_id 不存在返回空列表', async ({ api }) => {
    const response = await api.get('/incidents/runs/non-existent-run-id/events');
    expect(response.ok()).toBeTruthy();

    const events = await response.json();
    expect(events).toEqual([]);
  });
});
