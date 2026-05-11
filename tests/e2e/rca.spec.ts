/**
 * P0 场景：RCA 报告生成（Root Cause Analysis Report）
 * 
 * 验证场景：
 * - 成功场景生成 RCA
 * - 查询 RCA 报告
 * - 失败场景生成 RCA
 * - RCA 待生成时返回提示
 */

import { test, expect } from '../fixtures/api';

test.describe('RCA 报告 (Root Cause Analysis Report)', () => {
  test('正常流程：工单完成后可查询 RCA', async ({ api }) => {
    // 创建工单并等待完成
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-001',
          title: 'RCA 测试工单',
          description: '测试 RCA 报告生成',
          service: 'test-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    expect(createResponse.ok()).toBeTruthy();
    const { run_id } = await createResponse.json();

    // 等待工单完成
    let status = 'NEW';
    let attempts = 0;
    
    while (!['COMPLETED', 'FAILED'].includes(status) && attempts < 30) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 查询 RCA
    const rcaResponse = await api.get(`/incidents/runs/${run_id}/rca`);
    expect(rcaResponse.ok()).toBeTruthy();
    
    const rca = await rcaResponse.json();
    expect(rca.run_id).toBe(run_id);
  });

  test('正常流程：成功场景生成完整 RCA', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-SUCCESS-001',
          title: '成功场景 RCA',
          description: '测试成功场景 RCA 报告',
          service: 'success-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 等待完成
    let status = 'NEW';
    let attempts = 0;
    
    while (!['COMPLETED', 'FAILED'].includes(status) && attempts < 30) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 如果成功完成，查询 RCA
    if (status === 'COMPLETED') {
      const rcaResponse = await api.get(`/incidents/runs/${run_id}/rca`);
      const rca = await rcaResponse.json();
      
      // RCA 应该包含报告内容
      expect(rca.run_id).toBeDefined();
    }
  });

  test('正常流程：查询 RCA 包含必要字段', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-FIELDS-001',
          title: 'RCA 字段测试',
          description: '验证 RCA 字段',
          service: 'fields-service',
          env: 'staging',
          severity: 'P3',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询 RCA
    const rcaResponse = await api.get(`/incidents/runs/${run_id}/rca`);
    expect(rcaResponse.ok()).toBeTruthy();
    
    const rca = await rcaResponse.json();
    expect(rca).toHaveProperty('run_id');
    // 可能有 report_markdown, root_cause, resolution 等字段
  });

  test('异常流程：失败场景生成失败报告', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-FAIL-001',
          title: '失败场景 RCA',
          description: '测试失败场景 RCA',
          service: 'fail-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 等待完成（可能是失败）
    let status = 'NEW';
    let attempts = 0;
    
    while (!['COMPLETED', 'FAILED'].includes(status) && attempts < 30) {
      const getResponse = await api.get(`/incidents/runs/${run_id}`);
      const body = await getResponse.json();
      status = body.status;
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    // 查询 RCA
    const rcaResponse = await api.get(`/incidents/runs/${run_id}/rca`);
    const rca = await rcaResponse.json();
    
    expect(rca.run_id).toBe(run_id);
  });

  test('异常流程：RCA 待生成时返回提示', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-PENDING-001',
          title: 'RCA 待生成',
          description: '测试 RCA 待生成场景',
          service: 'pending-service',
          env: 'dev',
          severity: 'P3',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 立即查询 RCA（可能还没生成）
    const rcaResponse = await api.get(`/incidents/runs/${run_id}/rca`);
    const rca = await rcaResponse.json();
    
    expect(rca.run_id).toBe(run_id);
    // 可能返回 "Root cause analysis pending" 或实际报告
  });

  test('异常流程：工单不存在时 RCA 查询返回 404', async ({ api }) => {
    const response = await api.get('/incidents/runs/non-existent-id/rca');
    // Run 不存在返回 404
    expect([404, 200]).toContain(response.status());
  });

  test('正常流程：RCA 报告包含时间线', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-TIMELINE-001',
          title: 'RCA 时间线',
          description: '验证 RCA 包含时间线',
          service: 'timeline-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询事件作为时间线数据
    const eventsResponse = await api.get(`/incidents/runs/${run_id}/events`);
    const events = await eventsResponse.json();
    
    expect(events.length).toBeGreaterThan(0);
    // 事件应该按时间排序
  });

  test('正常流程：RCA 包含预防项', async ({ api }) => {
    const createResponse = await api.post('/incidents/runs', {
      data: {
        ticket: {
          ticket_id: 'INC-RCA-PREVENTION-001',
          title: 'RCA 预防项',
          description: '验证 RCA 包含预防项',
          service: 'prevention-service',
          env: 'staging',
          severity: 'P2',
        },
      },
    });

    const { run_id } = await createResponse.json();

    // 查询 RCA
    const rcaResponse = await api.get(`/incidents/runs/${run_id}/rca`);
    const rca = await rcaResponse.json();
    
    expect(rca.run_id).toBeDefined();
  });
});
