import type { Page, Route } from '@playwright/test';

type RunStatus = 'NEW' | 'WAITING_HUMAN' | 'COMPLETED';

interface MockOptions {
  runId?: string;
  approvalId?: string;
  service?: string;
  env?: string;
  severity?: string;
  initialRunStatus?: RunStatus;
}

interface MockState {
  runId: string;
  approvalId: string;
  service: string;
  env: string;
  severity: string;
  runStatus: RunStatus;
  approvalStatus: 'PENDING' | 'APPROVED';
}

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}

function buildRun(state: MockState) {
  return {
    run_id: state.runId,
    ticket_id: `INC-${state.runId}`,
    thread_id: `thread-${state.runId}`,
    status: state.runStatus,
    severity: state.severity,
    service: state.service,
    env: state.env,
    current_node: state.runStatus === 'WAITING_HUMAN' ? 'node_approval_interrupt' : null,
    step_count: state.runStatus === 'COMPLETED' ? 13 : 11,
    created_at: '2026-04-08T13:07:08.885200',
    updated_at: '2026-04-08T13:08:07.194831',
    completed_at: state.runStatus === 'COMPLETED' ? '2026-04-08T13:08:07.194541' : null,
  };
}

function buildEvents(state: MockState) {
  return [
    {
      event_id: 'evt-created',
      run_id: state.runId,
      level: 'INFO',
      type: 'RUN_CREATED',
      node_name: null,
      message: 'Run started',
      timestamp: '2026-04-08T13:07:08.899062',
    },
    {
      event_id: 'evt-diagnose',
      run_id: state.runId,
      level: 'INFO',
      type: 'NODE_COMPLETED',
      node_name: 'node_diagnose',
      message: 'Node node_diagnose completed',
      timestamp: '2026-04-08T13:07:41.536212',
    },
    {
      event_id: 'evt-status',
      run_id: state.runId,
      level: 'INFO',
      type: 'RUN_COMPLETED',
      node_name: null,
      message:
        state.runStatus === 'WAITING_HUMAN'
          ? 'Run finished with status WAITING_HUMAN'
          : 'Run finished with status COMPLETED',
      timestamp: '2026-04-08T13:08:07.195640',
    },
  ];
}

function buildEvidence(state: MockState) {
  return [
    {
      evidence_id: 'ev-logs-1',
      run_id: state.runId,
      tool_name: 'query_logs',
      category: 'logs',
      source_ref: 'logs-source',
      summary: `Retrieved logs data for ${state.service}`,
      raw_payload: { count: 3 },
      created_at: '2026-04-08T13:07:25.263608',
    },
    {
      evidence_id: 'ev-k8s-1',
      run_id: state.runId,
      tool_name: 'query_k8s_deployment_status',
      category: 'k8s',
      source_ref: 'k8s-source',
      summary: `Retrieved k8s data for ${state.service}`,
      raw_payload: { status: 'running' },
      created_at: '2026-04-08T13:07:25.265899',
    },
  ];
}

function buildDiagnosis(state: MockState) {
  return {
    run_id: state.runId,
    confidence: 0.7,
    root_cause_candidates: [
      {
        candidate_id: 'cand-1',
        hypothesis: '近期部署变更导致依赖不兼容',
        confidence: 0.7,
        supporting_evidence_ids: ['ev-logs-1'],
        contradicting_evidence_ids: [],
        next_checks: ['检查最近一次发布变更'],
      },
    ],
  };
}

function buildRemediation(state: MockState) {
  return {
    run_id: state.runId,
    remediation_plan: {
      summary: 'Proposed 1 remediation actions',
      actions: [
        {
          action_type: state.runStatus === 'WAITING_HUMAN' ? 'rollback' : 'restart',
          service: state.service,
          env: state.env,
          params: state.runStatus === 'WAITING_HUMAN' ? { version: 'previous' } : {},
          risk_level: state.runStatus === 'WAITING_HUMAN' ? 'HIGH' : 'LOW',
          requires_approval: state.runStatus === 'WAITING_HUMAN',
        },
      ],
      expected_outcome: 'Service should recover',
      rollback_plan: 'Rollback to previous version if needed',
      risk_notes: null,
      human_checkpoints: [],
    },
  };
}

function buildRca(state: MockState) {
  return {
    run_id: state.runId,
    report_markdown: '# RCA Report',
    root_cause: '近期部署变更导致依赖不兼容',
    resolution: '回滚后恢复',
    prevention_items: ['补充发布前验证', '增加灰度检查'],
    confirmed_by_human: false,
  };
}

function buildApproval(state: MockState) {
  return {
    approval_id: state.approvalId,
    run_id: state.runId,
    action: {
      action_type: 'rollback',
      service: state.service,
      env: state.env,
      params: { version: 'previous' },
      risk_level: 'HIGH',
      requires_approval: true,
    },
    risk_level: 'HIGH',
    status: state.approvalStatus,
    reason: 'Rollback latest deployment',
    evidence_refs: ['ev-logs-1'],
    expected_impact: 'Error rate should return to baseline',
    rollback_plan: 'Redeploy current version if rollback fails',
    approver: state.approvalStatus === 'APPROVED' ? 'human' : null,
    comment: null,
    created_at: '2026-04-08T13:07:41.569311',
  };
}

export async function installOpsPilotMocks(page: Page, options: MockOptions = {}) {
  const state: MockState = {
    runId: options.runId ?? 'run-e2e-001',
    approvalId: options.approvalId ?? 'apr-e2e-001',
    service: options.service ?? 'mysql',
    env: options.env ?? 'prod',
    severity: options.severity ?? 'P2',
    runStatus: options.initialRunStatus ?? 'COMPLETED',
    approvalStatus: 'PENDING',
  };

  await page.addInitScript(() => {
    window.localStorage.setItem('opspilot-locale', 'zh-CN');

    class MockEventSource {
      static instances: MockEventSource[] = [];
      url: string;
      onopen: ((event: Event) => void) | null = null;
      onmessage: ((event: MessageEvent) => void) | null = null;
      onerror: ((event: Event) => void) | null = null;

      constructor(url: string) {
        this.url = url;
        MockEventSource.instances.push(this);
        window.setTimeout(() => {
          this.open();
        }, 0);
      }

      open() {
        this.onopen?.(new Event('open'));
      }

      emit(event: unknown) {
        this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(event) }));
      }

      fail() {
        this.onerror?.(new Event('error'));
      }

      close() {
        return undefined;
      }

      addEventListener() {
        return undefined;
      }

      removeEventListener() {
        return undefined;
      }
    }

    Object.defineProperty(window, 'EventSource', {
      configurable: true,
      writable: true,
      value: MockEventSource,
    });

    Object.defineProperty(window, '__opspilotEventSources', {
      configurable: true,
      value: MockEventSource.instances,
    });
  });

  await page.route('**/incidents/runs', async (route) => {
    if (route.request().method() !== 'POST') {
      return json(route, [buildRun(state)]);
    }

    state.runStatus = options.initialRunStatus ?? 'COMPLETED';
    return json(route, buildRun(state), 201);
  });

  await page.route('**/incidents/runs?**', async (route) => {
    return json(route, [buildRun(state)]);
  });

  await page.route('**/incidents/runs/*/stream', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: '',
    });
  });

  await page.route('**/incidents/runs/*/events**', async (route) => {
    return json(route, buildEvents(state));
  });

  await page.route('**/incidents/runs/*/evidence', async (route) => {
    return json(route, buildEvidence(state));
  });

  await page.route('**/incidents/runs/*/diagnosis', async (route) => {
    return json(route, buildDiagnosis(state));
  });

  await page.route('**/incidents/runs/*/remediation', async (route) => {
    return json(route, buildRemediation(state));
  });

  await page.route('**/incidents/runs/*/rca', async (route) => {
    return json(route, buildRca(state));
  });

  await page.route('**/incidents/runs/*', async (route) => {
    return json(route, buildRun(state));
  });

  await page.route('**/approvals/pending', async (route) => {
    const body = state.approvalStatus === 'PENDING' ? [buildApproval(state)] : [];
    return json(route, body);
  });

  await page.route('**/approvals/*/decision', async (route) => {
    const request = route.request();
    const payload = request.postDataJSON() as { decision?: string } | null;
    if (payload?.decision === 'approved') {
      state.approvalStatus = 'APPROVED';
      state.runStatus = 'COMPLETED';
    }
    return json(route, {
      status: 'success',
      message: `Decision '${payload?.decision ?? 'unknown'}' recorded`,
    });
  });

  await page.route('**/approvals/*', async (route) => {
    return json(route, buildApproval(state));
  });

  return state;
}
