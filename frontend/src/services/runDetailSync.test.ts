import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  createRunDetailSyncController,
  type RunDetailSyncOptions,
  type SyncConnectionState,
} from './runDetailSync';
import type { RunDetail, RunEvent } from '../types';

class FakeEventSource {
  static instances: FakeEventSource[] = [];
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  closed = false;

  constructor(public url: string) {
    FakeEventSource.instances.push(this);
  }

  open() {
    this.onopen?.(new Event('open'));
  }

  message(event: RunEvent) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(event) }));
  }

  fail() {
    this.onerror?.(new Event('error'));
  }

  close() {
    this.closed = true;
  }
}

const baseRun: RunDetail = {
  ticket_id: 'INC-1',
  run_id: 'run-1',
  thread_id: 'thread-1',
  status: 'GATHERING_EVIDENCE',
  created_at: '2026-06-02T10:00:00Z',
};

const event = (event_id: string): RunEvent => ({
  event_id,
  run_id: 'run-1',
  level: 'INFO',
  type: 'NODE_STARTED',
  message: event_id,
  timestamp: '2026-06-02T10:00:00Z',
});

function setup(overrides: Partial<RunDetailSyncOptions> = {}) {
  const states: SyncConnectionState[] = [];
  const received: RunEvent[][] = [];
  const options: RunDetailSyncOptions = {
    runId: 'run-1',
    getRun: vi.fn().mockResolvedValue(baseRun),
    getRunEvents: vi.fn().mockResolvedValue([]),
    refreshArtifacts: vi.fn().mockResolvedValue(undefined),
    onRun: vi.fn(),
    onEvents: (events) => received.push(events),
    onConnectionState: (state) => states.push(state),
    eventSourceFactory: (url) => new FakeEventSource(url) as unknown as EventSource,
    ...overrides,
  };
  return { controller: createRunDetailSyncController(options), options, states, received };
}

beforeEach(() => {
  vi.useFakeTimers();
  FakeEventSource.instances = [];
});

describe('RunDetailSyncController', () => {
  it('appends default SSE messages once and updates the cursor', async () => {
    const { controller, received, options } = setup();
    controller.start();
    FakeEventSource.instances[0].open();
    FakeEventSource.instances[0].message(event('evt-1'));
    FakeEventSource.instances[0].message(event('evt-1'));

    expect(received).toEqual([[event('evt-1')]]);

    FakeEventSource.instances[0].fail();
    await vi.advanceTimersByTimeAsync(0);
    expect(options.getRunEvents).toHaveBeenCalledWith('run-1', 'evt-1');
  });

  it('falls back to REST polling and reconnects SSE automatically', async () => {
    const { controller, options, states } = setup();
    controller.seedEvents([event('evt-1')]);
    controller.start();
    FakeEventSource.instances[0].fail();
    await vi.advanceTimersByTimeAsync(0);

    expect(states).toContain('polling');
    expect(options.getRunEvents).toHaveBeenCalledWith('run-1', 'evt-1');

    await vi.advanceTimersByTimeAsync(5000);
    expect(FakeEventSource.instances).toHaveLength(2);
    FakeEventSource.instances[1].open();
    await vi.advanceTimersByTimeAsync(0);

    expect(states.at(-1)).toBe('live');
    expect(options.getRunEvents).toHaveBeenLastCalledWith('run-1', 'evt-1');
  });

  it('stops live delivery while waiting for approval and resumes after status changes', async () => {
    const getRun = vi
      .fn()
      .mockResolvedValueOnce({ ...baseRun, status: 'WAITING_HUMAN' })
      .mockResolvedValueOnce({ ...baseRun, status: 'EXECUTING' });
    const { controller, states } = setup({ getRun });
    controller.start();

    await vi.advanceTimersByTimeAsync(5000);
    expect(states.at(-1)).toBe('stopped');

    await vi.advanceTimersByTimeAsync(5000);
    expect(FakeEventSource.instances).toHaveLength(2);
  });

  it('stops immediately when the initial REST status is terminal', () => {
    const { controller, states } = setup();
    controller.start();

    controller.observeRun({ ...baseRun, status: 'COMPLETED' });

    expect(FakeEventSource.instances[0].closed).toBe(true);
    expect(states.at(-1)).toBe('stopped');
    expect(vi.getTimerCount()).toBe(0);
  });

  it('throttles artifact refreshes after an SSE burst', async () => {
    const { controller, options } = setup();
    controller.start();
    FakeEventSource.instances[0].open();
    FakeEventSource.instances[0].message(event('evt-1'));
    FakeEventSource.instances[0].message(event('evt-2'));

    await vi.advanceTimersByTimeAsync(749);
    expect(options.refreshArtifacts).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1);
    expect(options.refreshArtifacts).toHaveBeenCalledOnce();
  });

  it('cleans up timers and EventSource on dispose', () => {
    const { controller, states } = setup();
    controller.start();
    controller.dispose();

    expect(FakeEventSource.instances[0].closed).toBe(true);
    expect(states.at(-1)).toBe('stopped');
    expect(vi.getTimerCount()).toBe(0);
  });
});
