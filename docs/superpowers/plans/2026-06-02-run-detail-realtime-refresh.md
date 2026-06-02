# Run Detail Realtime Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the run detail page update events, run status, evidence, diagnosis, remediation, and trace metadata without manual browser refreshes, with SSE-first delivery, REST fallback polling, automatic recovery, and responsive progressive loading states.

**Architecture:** Persisted REST events remain the source of truth. The backend emits default SSE `message` events and wakes subscribers safely across event-loop boundaries. The frontend replaces the process-wide SSE singleton with one `RunDetailSyncController` instance per mounted run-detail page; the controller owns SSE, incremental polling, compensation fetches, timers, and cleanup while the page owns artifact rendering state.

**Tech Stack:** FastAPI, `sse-starlette`, SQLAlchemy, `asyncio`, React 19, TypeScript, Vitest, Testing Library, Playwright, Tailwind CSS utility classes.

---

## Workspace Safety

The current workspace already contains user edits in files this plan will touch, including:

- `frontend/src/pages/RunDetailPage.tsx`
- `frontend/src/components/EventTimeline.tsx`
- `frontend/src/components/EvidencePanel.tsx`
- `frontend/src/components/DiagnosisCard.tsx`
- `frontend/src/components/RemediationCard.tsx`
- `frontend/src/i18n/en.json`
- `frontend/src/i18n/zh-CN.json`

Before implementation, inspect `git status --short` and `git diff -- <affected-files>`. Preserve those edits. Do not reset, checkout, stash, or overwrite them. If implementation moves to a dedicated worktree, first transfer the user's existing edits by committing them with the user's approval or by applying an explicit patch in the new worktree.

Reference design: `docs/superpowers/specs/2026-06-02-run-detail-realtime-refresh-design.md`.

## File Structure

### Backend

- Modify: `backend/app/services/event_bus.py`
  - Store subscriber queue and event loop together.
  - Publish with `loop.call_soon_threadsafe`.
  - Normalize pushed event shape to the frontend `RunEvent` contract.
- Modify: `backend/app/api/incidents.py`
  - Emit default SSE `message` payloads.
- Modify: `backend/app/tests/test_event_bus.py`
  - Cover same-loop and cross-thread subscriber delivery.
- Modify: `backend/app/tests/test_incidents_api.py`
  - Cover default SSE formatting and incremental `last_event_id` retrieval.

### Frontend Data Flow

- Modify: `frontend/src/services/runs.ts`
  - Use `last_event_id` for incremental event requests.
- Modify: `frontend/src/services/runs.test.ts`
  - Lock the updated REST cursor contract.
- Create: `frontend/src/services/runDetailSync.ts`
  - Implement the page-scoped synchronization controller.
- Create: `frontend/src/services/runDetailSync.test.ts`
  - Cover live delivery, fallback, recovery, deduplication, terminal states, approval resume, and cleanup.
- Delete: `frontend/src/services/sse.ts`
  - Remove the obsolete process-wide SSE singleton after the detail page stops importing it.

### Frontend Presentation

- Create: `frontend/src/components/RunDetailStates.tsx`
  - Provide skeleton, fallback notice, and reusable artifact pending/error/refresh states.
- Create: `frontend/src/components/RunDetailStates.test.tsx`
  - Cover visible loading, fallback, refresh, and retry states.
- Modify: `frontend/src/pages/RunDetailPage.tsx`
  - Integrate the controller and progressive artifact rendering.
  - Add responsive wrapping and no-overlap layout constraints.
- Modify: `frontend/src/pages/RunDetailPage.test.tsx`
  - Mock the controller factory and cover page-level state transitions.
- Modify: `frontend/src/components/EventTimeline.tsx`
  - Allow long event content to wrap.
- Modify: `frontend/src/components/EvidencePanel.tsx`
  - Allow summaries to wrap without colliding with disclosure controls.
- Modify: `frontend/src/components/DiagnosisCard.tsx`
  - Allow long hypotheses and evidence IDs to wrap.
- Modify: `frontend/src/components/RemediationCard.tsx`
  - Wrap long action rows on narrow screens.
- Modify: `frontend/src/i18n/en.json`
  - Add realtime, loading, retry, and updated-time labels.
- Modify: `frontend/src/i18n/zh-CN.json`
  - Add matching Chinese labels.

### Browser Regression

- Modify: `frontend/e2e/fixtures/mockApi.ts`
  - Expose mock `EventSource` instances so Playwright can trigger messages and disconnects.
- Create: `frontend/e2e/smoke-run-detail-realtime.spec.ts`
  - Cover SSE append, fallback notice, automatic recovery, deduplication, and responsive overflow.

---

### Task 1: Make Backend Subscriber Delivery Thread-Safe

**Files:**
- Modify: `backend/app/services/event_bus.py:1-124`
- Modify: `backend/app/tests/test_event_bus.py:1-67`

- [ ] **Step 1: Write failing event-bus tests**

Replace the existing synchronous subscriber notification test with async tests that exercise the actual iterator path and add a cross-thread publish case:

```python
@pytest.mark.asyncio
async def test_publish_notifies_subscriber(self, db_session):
    bus = EventBus()
    iterator = bus.iter_events("run-1")
    pending = asyncio.create_task(anext(iterator))
    await asyncio.sleep(0)

    bus.publish(
        db=db_session,
        run_id="run-1",
        event_type=EventType.RUN_CREATED,
        message="created",
    )

    event = await asyncio.wait_for(pending, timeout=1)
    assert event["type"] == "RUN_CREATED"
    assert event["message"] == "created"
    assert "timestamp" in event
    await iterator.aclose()


@pytest.mark.asyncio
async def test_publish_notifies_subscriber_from_worker_thread(self, db_session):
    bus = EventBus()
    iterator = bus.iter_events("run-1")
    pending = asyncio.create_task(anext(iterator))
    await asyncio.sleep(0)

    await asyncio.to_thread(
        bus.publish,
        db_session,
        "run-1",
        EventType.NODE_STARTED,
        "node_intake",
        "started",
    )

    event = await asyncio.wait_for(pending, timeout=1)
    assert event["node_name"] == "node_intake"
    assert event["message"] == "started"
    await iterator.aclose()
```

Update the unsubscribe test so it subscribes inside a running loop:

```python
@pytest.mark.asyncio
async def test_unsubscribe(self, db_session):
    bus = EventBus()
    subscriber = bus.subscribe("run-1")
    bus.unsubscribe("run-1", subscriber)

    bus.publish(db=db_session, run_id="run-1", event_type=EventType.RUN_CREATED)

    assert subscriber.queue.empty()
```

- [ ] **Step 2: Run the focused backend test and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_event_bus.py -q
```

Expected: FAIL because `subscribe()` currently returns a plain queue and `publish()` calls `queue.put_nowait()` directly.

- [ ] **Step 3: Implement loop-aware subscribers**

In `backend/app/services/event_bus.py`, add a subscriber record and update subscription delivery:

```python
from dataclasses import dataclass


@dataclass
class Subscriber:
    queue: asyncio.Queue
    loop: asyncio.AbstractEventLoop
```

Replace the subscriber storage and methods with:

```python
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, list[Subscriber]] = {}

    def _notify(self, run_id: str, event: Dict[str, Any]) -> None:
        for subscriber in list(self._subscribers.get(run_id, [])):
            subscriber.loop.call_soon_threadsafe(subscriber.queue.put_nowait, event)

    def subscribe(self, run_id: str) -> Subscriber:
        subscriber = Subscriber(queue=asyncio.Queue(), loop=asyncio.get_running_loop())
        self._subscribers.setdefault(run_id, []).append(subscriber)
        return subscriber

    def unsubscribe(self, run_id: str, subscriber: Subscriber) -> None:
        subscribers = self._subscribers.get(run_id, [])
        if subscriber in subscribers:
            subscribers.remove(subscriber)
        if not subscribers and run_id in self._subscribers:
            del self._subscribers[run_id]

    async def iter_events(self, run_id: str) -> AsyncIterator[Dict[str, Any]]:
        subscriber = self.subscribe(run_id)
        try:
            while True:
                yield await subscriber.queue.get()
        finally:
            self.unsubscribe(run_id, subscriber)
```

Inside `publish()`, emit the frontend contract and call `_notify()`:

```python
event_dict = {
    "event_id": event.event_id,
    "run_id": event.run_id,
    "timestamp": event.ts.isoformat(),
    "level": event.level,
    "type": event.type,
    "node_name": event.node_name,
    "message": event.message,
    "data": event.data_json,
}
self._notify(run_id, event_dict)
```

- [ ] **Step 4: Re-run the focused backend test**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_event_bus.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the backend delivery fix**

```bash
git add backend/app/services/event_bus.py backend/app/tests/test_event_bus.py
git commit -m "backend: make SSE event delivery thread safe"
```

---

### Task 2: Normalize The Backend SSE And Incremental Event Contracts

**Files:**
- Modify: `backend/app/api/incidents.py:254-302`
- Modify: `backend/app/tests/test_incidents_api.py`

- [ ] **Step 1: Write failing API contract tests**

Import `_format_sse_event`, `IncidentRunEvent`, and `EventType` in `backend/app/tests/test_incidents_api.py`, then add:

```python
from app.api.incidents import _format_sse_event, get_db, router
from app.models.db_models import (
    Base,
    IncidentCheckpoint,
    IncidentRun,
    IncidentRunEvent,
    RunStatusEnum,
)


def test_format_sse_event_uses_default_message_event():
    payload = {
        "event_id": "evt-1",
        "run_id": "run-123",
        "timestamp": "2026-06-02T10:00:00",
        "level": "INFO",
        "type": "NODE_STARTED",
        "node_name": "node_intake",
        "message": "started",
        "data": None,
    }

    formatted = _format_sse_event(payload)

    assert formatted == {"data": json.dumps(payload, default=str)}


def test_get_run_events_filters_by_last_event_id():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)
    db = session_factory()
    try:
        db.add_all(
            [
                IncidentRunEvent(
                    event_id="evt-1",
                    run_id="run-123",
                    ts=datetime(2026, 6, 2, 10, 0, 0),
                    level="INFO",
                    type="RUN_CREATED",
                    message="created",
                ),
                IncidentRunEvent(
                    event_id="evt-2",
                    run_id="run-123",
                    ts=datetime(2026, 6, 2, 10, 0, 1),
                    level="INFO",
                    type="NODE_STARTED",
                    message="started",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/events?last_event_id=evt-1")

    assert response.status_code == 200
    assert [event["event_id"] for event in response.json()] == ["evt-2"]
```

Add `import json` at the top of the test file.

- [ ] **Step 2: Run the focused API tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_incidents_api.py -q
```

Expected: FAIL because `_format_sse_event()` does not exist.

- [ ] **Step 3: Emit default SSE messages**

Add this helper above the routes in `backend/app/api/incidents.py`:

```python
def _format_sse_event(event: Dict[str, Any]) -> Dict[str, str]:
    return {"data": json.dumps(event, default=str)}
```

Update the stream generator:

```python
async def generate():
    async for event in event_bus.iter_events(run_id):
        yield _format_sse_event(event)
```

Do not set the SSE `event` field. `EventSource.onmessage` must receive every pushed run event.

- [ ] **Step 4: Run the API and event-bus tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_incidents_api.py app/tests/test_event_bus.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit the backend protocol fix**

```bash
git add backend/app/api/incidents.py backend/app/tests/test_incidents_api.py
git commit -m "backend: normalize run event SSE protocol"
```

---

### Task 3: Switch The Frontend REST Cursor To `last_event_id`

**Files:**
- Modify: `frontend/src/services/runs.ts:48-53`
- Modify: `frontend/src/services/runs.test.ts:91-117`

- [ ] **Step 1: Replace the timestamp cursor test with an ID cursor test**

In `frontend/src/services/runs.test.ts`, replace the `lastEventTs` test with:

```typescript
it('fetches events after the last event ID', async () => {
  const mockEvents = [
    {
      event_id: 'evt-2',
      run_id: 'run-123',
      level: 'INFO',
      message: 'Updated',
      timestamp: '2026-06-02T10:00:01Z',
    },
  ];
  vi.mocked(mockApi.get).mockResolvedValue(mockEvents);

  const result = await runs.getRunEvents('run-123', 'evt-1');

  expect(mockApi.get).toHaveBeenCalledWith(
    '/incidents/runs/run-123/events?last_event_id=evt-1',
  );
  expect(result).toEqual(mockEvents);
});
```

- [ ] **Step 2: Run the frontend service test and verify failure**

Run:

```bash
cd frontend
npx vitest run src/services/runs.test.ts
```

Expected: FAIL because `runs.getRunEvents()` still sends `last_event_ts`.

- [ ] **Step 3: Update the REST client**

Replace `getRunEvents` in `frontend/src/services/runs.ts` with:

```typescript
getRunEvents: (runId: string, lastEventId?: string) => {
  const url = lastEventId
    ? `/incidents/runs/${runId}/events?last_event_id=${encodeURIComponent(lastEventId)}`
    : `/incidents/runs/${runId}/events`;
  return api.get<RunEvent[]>(url);
},
```

- [ ] **Step 4: Re-run the frontend service test**

Run:

```bash
cd frontend
npx vitest run src/services/runs.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit the frontend REST contract**

```bash
git add frontend/src/services/runs.ts frontend/src/services/runs.test.ts
git commit -m "frontend: use event ids for incremental run polling"
```

---

### Task 4: Add A Page-Scoped Run Detail Synchronization Controller

**Files:**
- Create: `frontend/src/services/runDetailSync.ts`
- Create: `frontend/src/services/runDetailSync.test.ts`
- Delete after Task 6 integration: `frontend/src/services/sse.ts`

- [ ] **Step 1: Write the controller test harness**

Create `frontend/src/services/runDetailSync.test.ts` with a fake `EventSource`, fake timers, and dependency mocks:

```typescript
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
```

- [ ] **Step 2: Add failing behavior tests**

Add these tests below the harness:

```typescript
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
```

- [ ] **Step 3: Run the controller tests and verify failure**

Run:

```bash
cd frontend
npx vitest run src/services/runDetailSync.test.ts
```

Expected: FAIL because `runDetailSync.ts` does not exist.

- [ ] **Step 4: Implement the controller**

Create `frontend/src/services/runDetailSync.ts`. Use these public types and behavior:

```typescript
import type { RunDetail, RunEvent } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const POLL_INTERVAL = 3000;
const RECONNECT_INTERVAL = 5000;
const STATUS_INTERVAL = 5000;
const ARTIFACT_REFRESH_DELAY = 750;
const STOPPED_STATUSES = new Set(['COMPLETED', 'FAILED']);

export type SyncConnectionState =
  | 'connecting'
  | 'live'
  | 'polling'
  | 'reconnecting'
  | 'stopped';

export interface RunDetailSyncOptions {
  runId: string;
  getRun: (runId: string) => Promise<RunDetail>;
  getRunEvents: (runId: string, lastEventId?: string) => Promise<RunEvent[]>;
  refreshArtifacts: () => Promise<void>;
  onRun: (run: RunDetail) => void;
  onEvents: (events: RunEvent[]) => void;
  onConnectionState: (state: SyncConnectionState) => void;
  eventSourceFactory?: (url: string) => EventSource;
}

class RunDetailSyncController {
  private eventSource: EventSource | null = null;
  private pollTimer: number | null = null;
  private reconnectTimer: number | null = null;
  private statusTimer: number | null = null;
  private artifactTimer: number | null = null;
  private seenEventIds = new Set<string>();
  private lastEventId: string | undefined;
  private disposed = false;
  private connectionState: SyncConnectionState = 'stopped';

  constructor(private options: RunDetailSyncOptions) {}

  seedEvents(events: RunEvent[]) {
    for (const event of events) this.recordEvent(event);
  }

  observeRun(run: RunDetail) {
    if (this.disposed) return;
    this.options.onRun(run);
    this.applyRunStatus(run);
  }

  start() {
    this.disposed = false;
    this.openSse(false);
    this.ensureStatusTimer();
  }

  dispose() {
    this.disposed = true;
    this.closeEventSource();
    this.clearTimer('pollTimer');
    this.clearTimer('reconnectTimer');
    this.clearTimer('statusTimer');
    this.clearTimer('artifactTimer');
    this.setConnectionState('stopped');
  }

  private setConnectionState(state: SyncConnectionState) {
    if (this.connectionState === state) return;
    this.connectionState = state;
    this.options.onConnectionState(state);
  }

  private recordEvent(event: RunEvent): boolean {
    if (!event?.event_id || this.seenEventIds.has(event.event_id)) return false;
    this.seenEventIds.add(event.event_id);
    this.lastEventId = event.event_id;
    return true;
  }

  private acceptEvents(events: RunEvent[]) {
    if (this.disposed) return;
    const fresh = events.filter((event) => this.recordEvent(event));
    if (fresh.length > 0) this.options.onEvents(fresh);
  }

  private openSse(reconnecting: boolean) {
    if (this.disposed) return;
    this.closeEventSource();
    this.setConnectionState(reconnecting ? 'reconnecting' : 'connecting');
    try {
      const factory = this.options.eventSourceFactory ?? ((url) => new EventSource(url));
      const source = factory(`${API_BASE}/incidents/runs/${this.options.runId}/stream`);
      this.eventSource = source;
      source.onopen = () => void this.handleOpen();
      source.onmessage = (message) => this.handleMessage(message);
      source.onerror = () => this.startFallback();
    } catch {
      this.startFallback();
    }
  }

  private async handleOpen() {
    if (this.disposed) return;
    if (this.pollTimer !== null || this.reconnectTimer !== null) {
      try {
        await this.pollEvents();
      } catch {
        this.closeEventSource();
        this.setConnectionState('polling');
        return;
      }
      if (this.disposed) return;
      this.clearTimer('pollTimer');
      this.clearTimer('reconnectTimer');
    }
    this.setConnectionState('live');
    this.scheduleArtifacts();
  }

  private handleMessage(message: MessageEvent) {
    try {
      const event = JSON.parse(message.data) as RunEvent;
      this.acceptEvents([event]);
      void this.refreshRun();
      this.scheduleArtifacts();
    } catch {
      console.error('Ignoring malformed SSE run event');
    }
  }

  private startFallback() {
    if (this.disposed) return;
    this.closeEventSource();
    this.setConnectionState('polling');
    if (this.pollTimer === null) {
      void this.pollOnce();
      this.pollTimer = window.setInterval(() => void this.pollOnce(), POLL_INTERVAL);
    }
    if (this.reconnectTimer === null) {
      this.reconnectTimer = window.setInterval(
        () => this.openSse(true),
        RECONNECT_INTERVAL,
      );
    }
  }

  private async pollEvents() {
    const events = await this.options.getRunEvents(this.options.runId, this.lastEventId);
    this.acceptEvents(events);
  }

  private async pollOnce() {
    try {
      await Promise.all([this.pollEvents(), this.refreshRun()]);
      this.scheduleArtifacts();
    } catch {
      this.setConnectionState('polling');
    }
  }

  private async refreshRun() {
    const run = await this.options.getRun(this.options.runId);
    if (this.disposed) return;
    this.observeRun(run);
  }

  private applyRunStatus(run: RunDetail) {
    if (STOPPED_STATUSES.has(run.status)) {
      this.dispose();
      return;
    }
    if (run.status === 'WAITING_HUMAN') {
      this.closeEventSource();
      this.clearTimer('pollTimer');
      this.clearTimer('reconnectTimer');
      this.setConnectionState('stopped');
      return;
    }
    if (this.connectionState === 'stopped') this.openSse(false);
  }

  private ensureStatusTimer() {
    if (this.statusTimer !== null) return;
    this.statusTimer = window.setInterval(() => void this.refreshRun(), STATUS_INTERVAL);
  }

  private scheduleArtifacts() {
    if (this.disposed) return;
    this.clearTimer('artifactTimer');
    this.artifactTimer = window.setTimeout(() => {
      this.artifactTimer = null;
      void this.options.refreshArtifacts();
    }, ARTIFACT_REFRESH_DELAY);
  }

  private closeEventSource() {
    this.eventSource?.close();
    this.eventSource = null;
  }

  private clearTimer(
    key: 'pollTimer' | 'reconnectTimer' | 'statusTimer' | 'artifactTimer',
  ) {
    const timer = this[key];
    if (timer === null) return;
    window.clearTimeout(timer);
    this[key] = null;
  }
}

export function createRunDetailSyncController(options: RunDetailSyncOptions) {
  return new RunDetailSyncController(options);
}
```

During implementation, keep the controller focused. Artifact rendering state belongs to the page, not this class.

- [ ] **Step 5: Run the controller tests**

Run:

```bash
cd frontend
npx vitest run src/services/runDetailSync.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit the isolated controller**

```bash
git add frontend/src/services/runDetailSync.ts frontend/src/services/runDetailSync.test.ts
git commit -m "frontend: add run detail sync controller"
```

---

### Task 5: Add Reusable Progressive Loading And Error States

**Files:**
- Create: `frontend/src/components/RunDetailStates.tsx`
- Create: `frontend/src/components/RunDetailStates.test.tsx`
- Modify: `frontend/src/i18n/en.json`
- Modify: `frontend/src/i18n/zh-CN.json`

- [ ] **Step 1: Write failing state-component tests**

Create `frontend/src/components/RunDetailStates.test.tsx`:

```typescript
import { fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '../test/render';
import {
  ArtifactPanelState,
  RealtimeFallbackNotice,
  RunDetailSkeleton,
} from './RunDetailStates';

describe('RunDetailStates', () => {
  beforeEach(() => localStorage.setItem('opspilot-locale', 'en'));

  it('renders the detail skeleton without an overlay', () => {
    renderWithProviders(<RunDetailSkeleton />);
    expect(screen.getByTestId('run-detail-skeleton')).toBeInTheDocument();
  });

  it('renders the fallback notice while polling', () => {
    renderWithProviders(<RealtimeFallbackNotice />);
    expect(screen.getByText(/Switched to automatic refresh/)).toBeInTheDocument();
  });

  it('shows local pending text when an artifact has no content yet', () => {
    renderWithProviders(
      <ArtifactPanelState empty pending pendingLabel="Collecting evidence">
        <p>content</p>
      </ArtifactPanelState>,
    );
    expect(screen.getByText('Collecting evidence')).toBeInTheDocument();
    expect(screen.queryByText('content')).not.toBeInTheDocument();
  });

  it('preserves content and exposes retry after a refresh error', () => {
    const retry = vi.fn();
    renderWithProviders(
      <ArtifactPanelState empty={false} error="Refresh failed" onRetry={retry}>
        <p>existing content</p>
      </ArtifactPanelState>,
    );
    expect(screen.getByText('existing content')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    expect(retry).toHaveBeenCalledOnce();
  });
});
```

- [ ] **Step 2: Run the component test and verify failure**

Run:

```bash
cd frontend
npx vitest run src/components/RunDetailStates.test.tsx
```

Expected: FAIL because `RunDetailStates.tsx` does not exist.

- [ ] **Step 3: Add translations**

Merge these keys into the existing `run` object in `frontend/src/i18n/en.json`:

```json
"realtimeFallback": "Realtime connection interrupted. Switched to automatic refresh and attempting to reconnect.",
"retry": "Retry",
"updatedAt": "Updated {{time}}",
"collectingEvidence": "Collecting evidence...",
"generatingDiagnosis": "Generating diagnosis...",
"generatingRemediation": "Generating remediation...",
"refreshing": "Refreshing..."
```

Merge the matching keys into `frontend/src/i18n/zh-CN.json`:

```json
"realtimeFallback": "实时连接中断，已切换为自动刷新，正在尝试恢复连接。",
"retry": "重试",
"updatedAt": "更新于 {{time}}",
"collectingEvidence": "正在收集证据...",
"generatingDiagnosis": "正在生成诊断...",
"generatingRemediation": "正在生成修复方案...",
"refreshing": "正在刷新..."
```

The existing i18n helper does not interpolate placeholders. Replace `{{time}}` in
the translated string inside JSX as shown below.

- [ ] **Step 4: Implement the state components**

Create `frontend/src/components/RunDetailStates.tsx`:

```typescript
import type { ReactNode } from 'react';
import { useI18n } from '../i18n';

function Spinner() {
  return (
    <span
      aria-hidden="true"
      className="inline-block h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-current border-r-transparent"
    />
  );
}

export function RunDetailSkeleton() {
  return (
    <div
      data-testid="run-detail-skeleton"
      className="mx-auto max-w-6xl animate-pulse space-y-6"
    >
      <div className="flex flex-wrap justify-between gap-4">
        <div className="space-y-2">
          <div className="h-6 w-52 rounded bg-surface-tertiary" />
          <div className="h-4 w-72 max-w-full rounded bg-surface-tertiary" />
        </div>
        <div className="h-9 w-28 rounded-full bg-surface-tertiary" />
      </div>
      <div className="card h-20 p-5" />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card min-h-80 p-4 sm:p-6 lg:col-span-2" />
        <div className="space-y-6">
          <div className="card h-36 p-4 sm:p-6" />
          <div className="card h-32 p-4 sm:p-6" />
        </div>
      </div>
    </div>
  );
}

export function RealtimeFallbackNotice() {
  const { t } = useI18n();
  return (
    <div role="status" className="status-warning flex flex-wrap items-center gap-2 rounded-lg p-3 text-sm">
      <Spinner />
      <span className="min-w-0 break-words">{t('run.realtimeFallback')}</span>
    </div>
  );
}

interface ArtifactPanelStateProps {
  children: ReactNode;
  empty: boolean;
  pending?: boolean;
  refreshing?: boolean;
  error?: string;
  pendingLabel: string;
  updatedAt?: string;
  onRetry?: () => void;
}

export function ArtifactPanelState({
  children,
  empty,
  pending = false,
  refreshing = false,
  error,
  pendingLabel,
  updatedAt,
  onRetry,
}: ArtifactPanelStateProps) {
  const { t } = useI18n();
  if (empty && pending) {
    return <div className="flex flex-wrap items-center gap-2 py-8 text-sm text-content-muted"><Spinner /><span>{pendingLabel}</span>{updatedAt && <span>{t('run.updatedAt').replace('{{time}}', updatedAt)}</span>}</div>;
  }
  if (empty && error) {
    return <div className="space-y-3 py-6 text-sm text-status-critical"><p>{error}</p>{onRetry && <button className="btn btn-secondary" onClick={onRetry}>{t('run.retry')}</button>}</div>;
  }
  return (
    <div className="space-y-3">
      {(refreshing || error || updatedAt) && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-content-muted">
          {refreshing && <><Spinner /><span>{t('run.refreshing')}</span></>}
          {error && <span className="text-status-critical">{error}</span>}
          {updatedAt && <span>{t('run.updatedAt').replace('{{time}}', updatedAt)}</span>}
          {error && onRetry && <button className="btn btn-secondary px-2 py-1 text-xs" onClick={onRetry}>{t('run.retry')}</button>}
        </div>
      )}
      {children}
    </div>
  );
}
```

- [ ] **Step 5: Run state-component tests**

Run:

```bash
cd frontend
npx vitest run src/components/RunDetailStates.test.tsx
```

Expected: PASS.

- [ ] **Step 6: Commit progressive state components**

```bash
git add frontend/src/components/RunDetailStates.tsx frontend/src/components/RunDetailStates.test.tsx frontend/src/i18n/en.json frontend/src/i18n/zh-CN.json
git commit -m "frontend: add progressive run detail states"
```

---

### Task 6: Integrate Live Synchronization Into The Run Detail Page

**Files:**
- Modify: `frontend/src/pages/RunDetailPage.tsx:1-312`
- Modify: `frontend/src/pages/RunDetailPage.test.tsx`
- Modify: `frontend/src/components/EventTimeline.tsx:89-112`
- Modify: `frontend/src/components/EvidencePanel.tsx:64-68`
- Modify: `frontend/src/components/DiagnosisCard.tsx:34-45`
- Modify: `frontend/src/components/RemediationCard.tsx:41-53`
- Delete: `frontend/src/services/sse.ts`

- [ ] **Step 1: Replace the old SSE mock with a controller factory mock**

In `frontend/src/pages/RunDetailPage.test.tsx`, replace the `../services/sse` mock with:

```typescript
const sync = vi.hoisted(() => ({
  options: null as any,
  controller: {
    seedEvents: vi.fn(),
    observeRun: vi.fn(),
    start: vi.fn(),
    dispose: vi.fn(),
  },
}));

vi.mock('../services/runDetailSync', () => ({
  createRunDetailSyncController: vi.fn((options) => {
    sync.options = options;
    return sync.controller;
  }),
}));
```

Reset `sync.options` and controller mocks in `beforeEach()`.

- [ ] **Step 2: Add failing page transition tests**

Add:

```typescript
it('shows a skeleton during initial loading', () => {
  vi.mocked(runsModule.runs.getRun).mockImplementation(() => new Promise(() => {}));
  vi.mocked(runsModule.runs.getRunEvents).mockImplementation(() => new Promise(() => {}));

  renderPage();

  expect(screen.getByTestId('run-detail-skeleton')).toBeInTheDocument();
});

it('shows and clears the fallback notice from controller state', async () => {
  vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
  vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
  renderPage();
  await screen.findByText('api-gateway');

  act(() => sync.options.onConnectionState('polling'));
  expect(screen.getByText(/Switched to automatic refresh/)).toBeInTheDocument();

  act(() => sync.options.onConnectionState('live'));
  expect(screen.queryByText(/Switched to automatic refresh/)).not.toBeInTheDocument();
});

it('keeps existing evidence visible while artifacts refresh', async () => {
  vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
  vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
  vi.mocked(runsModule.runs.getRunEvidence).mockResolvedValue([
    {
      evidence_id: 'evd-1',
      tool_name: 'prometheus',
      category: 'metrics',
      source_ref: 'prometheus://5xx',
      summary: '5xx elevated',
    },
  ] as any);
  renderPage();
  await screen.findByText('api-gateway');
  await userEvent.setup().click(screen.getByRole('button', { name: 'Evidence' }));

  let resolveRefresh!: () => void;
  vi.mocked(runsModule.runs.getRunEvidence).mockImplementation(
    () => new Promise((resolve) => {
      resolveRefresh = () => resolve([]);
    }),
  );
  act(() => void sync.options.refreshArtifacts());

  expect(screen.getByText('5xx elevated')).toBeInTheDocument();
  expect(screen.getByText('Refreshing...')).toBeInTheDocument();
  resolveRefresh();
});

it('shows local waiting text while diagnosis has not been generated', async () => {
  vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
  vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
  vi.mocked(runsModule.runs.getRunDiagnosis).mockRejectedValue(
    Object.assign(new Error('No checkpoint found'), { status: 404 }),
  );
  renderPage();
  await screen.findByText('api-gateway');

  await userEvent.setup().click(screen.getByRole('button', { name: 'Diagnosis' }));

  expect(screen.getByText('Generating diagnosis...')).toBeInTheDocument();
});

it('ignores an older artifact response that resolves after a newer refresh', async () => {
  vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
  vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
  vi.mocked(runsModule.runs.getRunEvidence).mockResolvedValueOnce([] as any);
  renderPage();
  await screen.findByText('api-gateway');

  let resolveOlder!: (value: any[]) => void;
  let resolveNewer!: (value: any[]) => void;
  vi.mocked(runsModule.runs.getRunEvidence)
    .mockImplementationOnce(() => new Promise((resolve) => { resolveOlder = resolve; }))
    .mockImplementationOnce(() => new Promise((resolve) => { resolveNewer = resolve; }));
  const older = sync.options.refreshArtifacts();
  const newer = sync.options.refreshArtifacts();
  resolveNewer([{ evidence_id: 'new', tool_name: 'logs', category: 'logs', source_ref: 'new', summary: 'new evidence' }]);
  await newer;
  resolveOlder([{ evidence_id: 'old', tool_name: 'logs', category: 'logs', source_ref: 'old', summary: 'old evidence' }]);
  await older;

  await userEvent.setup().click(screen.getByRole('button', { name: 'Evidence' }));
  expect(screen.getByText('new evidence')).toBeInTheDocument();
  expect(screen.queryByText('old evidence')).not.toBeInTheDocument();
});

it('retries the initial request after a page load failure', async () => {
  vi.mocked(runsModule.runs.getRun)
    .mockRejectedValueOnce(new Error('Network error'))
    .mockResolvedValueOnce(mockRun as any);
  vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
  renderPage();
  await screen.findByText(/Network error/);

  await userEvent.setup().click(screen.getByRole('button', { name: 'Retry' }));

  expect(await screen.findByText('api-gateway')).toBeInTheDocument();
});

it('disposes the page-scoped controller on unmount', async () => {
  vi.mocked(runsModule.runs.getRun).mockResolvedValue(mockRun as any);
  vi.mocked(runsModule.runs.getRunEvents).mockResolvedValue(mockEvents);
  const view = renderPage();
  await screen.findByText('api-gateway');

  view.unmount();

  expect(sync.controller.dispose).toHaveBeenCalledOnce();
});
```

Add this helper inside the test suite to reduce repeated router setup:

```typescript
function renderPage() {
  return renderWithProviders(
    <MemoryRouter initialEntries={['/runs/run-123']}>
      <Routes>
        <Route path="/runs/:id" element={<RunDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}
```

Import `act` from `@testing-library/react`.

- [ ] **Step 3: Run the page tests and verify failure**

Run:

```bash
cd frontend
npx vitest run src/pages/RunDetailPage.test.tsx
```

Expected: FAIL because the page still imports `sseClient`, renders the old spinner, and does not expose progressive refresh state.

- [ ] **Step 4: Integrate the page-scoped controller**

In `frontend/src/pages/RunDetailPage.tsx`:

1. Replace the `sseClient` import with:

```typescript
import {
  createRunDetailSyncController,
  type SyncConnectionState,
} from '../services/runDetailSync';
import {
  ArtifactPanelState,
  RealtimeFallbackNotice,
  RunDetailSkeleton,
} from '../components/RunDetailStates';
```

2. Add artifact state:

```typescript
type ArtifactKey = 'evidence' | 'diagnosis' | 'remediation';
interface ArtifactMeta {
  pending: boolean;
  refreshing: boolean;
  error?: string;
  updatedAt?: string;
}
const EMPTY_ARTIFACT_META: Record<ArtifactKey, ArtifactMeta> = {
  evidence: { pending: true, refreshing: false },
  diagnosis: { pending: true, refreshing: false },
  remediation: { pending: true, refreshing: false },
};
```

3. In the component, add:

```typescript
const [connectionState, setConnectionState] = useState<SyncConnectionState>('connecting');
const [artifactMeta, setArtifactMeta] = useState(EMPTY_ARTIFACT_META);
const [retryVersion, setRetryVersion] = useState(0);
const retryArtifactsRef = useRef<() => Promise<void>>(async () => undefined);
```

4. Replace the current effect with one that:

- Creates one controller instance.
- Starts SSE immediately.
- Merges all events by `event_id`.
- Uses `Promise.allSettled()` for artifacts.
- Keeps previous successful artifact values while marking refreshes.
- Uses a monotonically increasing request sequence and an `active` boolean so stale requests cannot overwrite newer state or update an unmounted page.
- Calls `controller.seedEvents(eventsData)` after the initial REST response.
- Calls `controller.dispose()` on cleanup.
- Includes `retryVersion` in the effect dependency list so the full-page retry
  button restarts initial loading with a fresh page-scoped controller.

Use this merge helper:

```typescript
function mergeEvents(current: RunEvent[], incoming: RunEvent[]): RunEvent[] {
  const byId = new Map(current.map((event) => [event.event_id, event]));
  for (const event of incoming) byId.set(event.event_id, event);
  return [...byId.values()].sort(
    (left, right) => Date.parse(left.timestamp) - Date.parse(right.timestamp),
  );
}
```

Use this pending check:

```typescript
function isPendingArtifactError(reason: unknown): boolean {
  return typeof reason === 'object' && reason !== null
    && 'status' in reason && reason.status === 404;
}
```

For each artifact result:

- Evidence fulfilled: update `evidence`, set evidence meta to ready with `updatedAt`.
- Diagnosis fulfilled: update candidates, set diagnosis meta to ready with `updatedAt`.
- Diagnosis `404`: keep old candidates and leave diagnosis pending only when candidates are empty.
- Remediation fulfilled: update plan, set remediation meta to ready with `updatedAt`.
- Remediation `404`: keep old plan and leave remediation pending only when no plan exists.
- Non-404 failures: preserve old content, set that artifact meta error, and do not fail the entire page after initial run and events have loaded.
- Trace fulfilled: update `runTrace`; trace failures preserve the previous trace link.

Use this effect skeleton so stale requests cannot overwrite newer state:

```typescript
useEffect(() => {
  if (!id) return;
  let active = true;
  let artifactSequence = 0;
  setLoading(true);
  setError(null);
  setRun(null);
  setEvents([]);
  setEvidence([]);
  setDiagnosis([]);
  setRemediationPlan(undefined);
  setRunTrace(null);
  setConnectionState('connecting');
  setArtifactMeta(EMPTY_ARTIFACT_META);

  const updateMeta = (key: ArtifactKey, patch: Partial<ArtifactMeta>) => {
    if (!active) return;
    setArtifactMeta((current) => ({
      ...current,
      [key]: { ...current[key], ...patch },
    }));
  };

  const markFailure = (key: ArtifactKey, reason: unknown) => {
    if (isPendingArtifactError(reason)) {
      updateMeta(key, { pending: true, refreshing: false, error: undefined });
      return;
    }
    updateMeta(key, {
      pending: false,
      refreshing: false,
      error: reason instanceof Error ? reason.message : t('run.loadFailed'),
    });
  };

  const refreshArtifacts = async () => {
    const sequence = ++artifactSequence;
    setArtifactMeta((current) => ({
      evidence: { ...current.evidence, refreshing: !current.evidence.pending },
      diagnosis: { ...current.diagnosis, refreshing: !current.diagnosis.pending },
      remediation: { ...current.remediation, refreshing: !current.remediation.pending },
    }));
    const [evidenceResult, diagnosisResult, remediationResult, traceResult] =
      await Promise.allSettled([
        runs.getRunEvidence(id),
        runs.getRunDiagnosis(id),
        runs.getRunRemediation(id),
        runs.getRunTrace(id),
      ]);
    if (!active || sequence !== artifactSequence) return;
    const updatedAt = new Date().toLocaleTimeString();

    if (evidenceResult.status === 'fulfilled') {
      setEvidence(evidenceResult.value);
      updateMeta('evidence', { pending: false, refreshing: false, error: undefined, updatedAt });
    } else {
      markFailure('evidence', evidenceResult.reason);
    }
    if (diagnosisResult.status === 'fulfilled') {
      setDiagnosis(diagnosisResult.value.root_cause_candidates ?? []);
      updateMeta('diagnosis', { pending: false, refreshing: false, error: undefined, updatedAt });
    } else {
      markFailure('diagnosis', diagnosisResult.reason);
    }
    if (remediationResult.status === 'fulfilled') {
      setRemediationPlan(remediationResult.value.remediation_plan);
      updateMeta('remediation', { pending: false, refreshing: false, error: undefined, updatedAt });
    } else {
      markFailure('remediation', remediationResult.reason);
    }
    if (traceResult.status === 'fulfilled') setRunTrace(traceResult.value);
  };

  const controller = createRunDetailSyncController({
    runId: id,
    getRun: runs.getRun,
    getRunEvents: runs.getRunEvents,
    refreshArtifacts,
    onRun: (nextRun) => active && setRun(nextRun),
    onEvents: (incoming) => active && setEvents((current) => mergeEvents(current, incoming)),
    onConnectionState: (state) => active && setConnectionState(state),
  });
  retryArtifactsRef.current = refreshArtifacts;

  const fetchInitial = async () => {
    try {
      const artifacts = refreshArtifacts();
      const [runData, eventsData] = await Promise.all([
        runs.getRun(id),
        runs.getRunEvents(id),
      ]);
      if (!active) return;
      controller.observeRun(runData);
      setEvents((current) => mergeEvents(current, eventsData));
      controller.seedEvents(eventsData);
      await artifacts;
    } catch (reason) {
      if (active) setError(reason instanceof Error ? reason.message : t('run.loadFailed'));
    } finally {
      if (active) setLoading(false);
    }
  };

  controller.start();
  void fetchInitial();
  return () => {
    active = false;
    retryArtifactsRef.current = async () => undefined;
    controller.dispose();
  };
}, [id, retryVersion, t]);
```

5. Replace the initial spinner with:

```typescript
if (loading) return <RunDetailSkeleton />;
```

6. Replace the full-page error block with a retryable state:

```typescript
if (error || !run) {
  return (
    <div className="space-y-3 rounded-lg p-4 status-critical">
      <p>{t('common.error')}: {error || t('run.notFound')}</p>
      <button
        type="button"
        className="btn btn-secondary"
        onClick={() => setRetryVersion((version) => version + 1)}
      >
        {t('run.retry')}
      </button>
    </div>
  );
}
```

7. Render the fallback notice above the header:

```typescript
{(connectionState === 'polling' || connectionState === 'reconnecting') && (
  <RealtimeFallbackNotice />
)}
```

8. Wrap each artifact tab in `ArtifactPanelState`:

```typescript
<ArtifactPanelState
  empty={evidence.length === 0}
  pending={artifactMeta.evidence.pending}
  refreshing={artifactMeta.evidence.refreshing}
  error={artifactMeta.evidence.error}
  pendingLabel={t('run.collectingEvidence')}
  updatedAt={artifactMeta.evidence.updatedAt}
  onRetry={() => void retryArtifactsRef.current()}
>
  <EvidencePanel evidence={evidence} />
</ArtifactPanelState>
```

Use equivalent wrappers for diagnosis and remediation with `run.generatingDiagnosis` and `run.generatingRemediation`.

- [ ] **Step 5: Add responsive no-overlap classes**

Apply these layout changes while preserving existing translated text:

```typescript
<div className="mx-auto max-w-6xl space-y-6">
  <div className="flex flex-wrap items-start justify-between gap-4">
    <div className="min-w-0">
      <h2 className="break-words text-xl font-semibold tracking-tight font-heading">
```

Use `flex flex-wrap gap-x-2 gap-y-1` for header metadata. Change the main tab card and sidebar cards to `p-4 sm:p-6`. Use `break-all whitespace-pre-wrap` for run IDs instead of horizontal scrolling.

When `run.updated_at` exists, include `{t('common.updated')}: {new Date(run.updated_at).toLocaleString()}` in the wrapping header metadata so a long-running wait always exposes the latest persisted run update time.

In `EventTimeline.tsx`, render event text with:

```typescript
<p className="mt-2 break-words text-sm text-content-primary">{event.message}</p>
```

In `EvidencePanel.tsx`, update the disclosure button and summary:

```typescript
className="flex w-full min-w-0 items-center justify-between gap-3 px-4 py-3 text-left hover:bg-surface-tertiary transition-fast cursor-pointer"
```

```typescript
<span className="min-w-0 break-words text-sm text-content-primary">{item.summary}</span>
```

In `DiagnosisCard.tsx`, add `break-words` to hypothesis text and `break-all` to evidence buttons.

In `RemediationCard.tsx`, update each action row and text wrapper:

```typescript
<div key={idx} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-surface-tertiary p-3 hover:bg-border transition-fast">
  <div className="min-w-0 break-words text-sm">
```

- [ ] **Step 6: Delete the obsolete singleton and run frontend tests**

Delete `frontend/src/services/sse.ts`, then run:

```bash
cd frontend
npx vitest run src/services/runs.test.ts src/services/runDetailSync.test.ts src/components/RunDetailStates.test.tsx src/pages/RunDetailPage.test.tsx src/components/EventTimeline.test.tsx src/components/EvidencePanel.test.tsx src/components/DiagnosisCard.test.tsx src/components/RemediationCard.test.tsx
npm run build
```

Expected: PASS.

- [ ] **Step 7: Commit page integration**

```bash
git add frontend/src/pages/RunDetailPage.tsx frontend/src/pages/RunDetailPage.test.tsx frontend/src/components/EventTimeline.tsx frontend/src/components/EvidencePanel.tsx frontend/src/components/DiagnosisCard.tsx frontend/src/components/RemediationCard.tsx frontend/src/services/sse.ts
git commit -m "frontend: refresh run details without manual reloads"
```

---

### Task 7: Add Playwright Realtime And Responsive Regression Coverage

**Files:**
- Modify: `frontend/e2e/fixtures/mockApi.ts`
- Create: `frontend/e2e/smoke-run-detail-realtime.spec.ts`

- [ ] **Step 1: Expose controllable mock EventSource instances**

In the `page.addInitScript()` block in `frontend/e2e/fixtures/mockApi.ts`, expose instances:

```typescript
class MockEventSource {
  static instances: MockEventSource[] = [];
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
    window.setTimeout(() => this.open(), 0);
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
}

Object.defineProperty(window, '__opspilotEventSources', {
  configurable: true,
  value: MockEventSource.instances,
});
```

Keep the existing `EventSource` replacement. Add a local TypeScript declaration at the top of the new spec rather than modifying global application types.

- [ ] **Step 2: Write the Playwright regression spec**

Create `frontend/e2e/smoke-run-detail-realtime.spec.ts`:

```typescript
import { expect, test } from '@playwright/test';
import { installOpsPilotMocks } from './fixtures/mockApi';

test.describe('OpsPilot run detail realtime refresh', () => {
  test('appends SSE events, falls back to polling, and recovers automatically', async ({ page }) => {
    await installOpsPilotMocks(page, {
      runId: 'run-realtime-001',
      initialRunStatus: 'NEW',
    });
    await page.goto('/runs/run-realtime-001');

    await page.evaluate(() => {
      const sources = (window as any).__opspilotEventSources;
      sources[0].emit({
        event_id: 'evt-live',
        run_id: 'run-realtime-001',
        level: 'INFO',
        type: 'NODE_STARTED',
        message: 'Realtime event arrived',
        timestamp: '2026-06-02T10:00:02Z',
      });
    });
    await expect(page.getByText('Realtime event arrived')).toHaveCount(1);

    await page.evaluate(() => (window as any).__opspilotEventSources[0].fail());
    await expect(page.getByText(/已切换为自动刷新/)).toBeVisible();

    await page.waitForTimeout(5200);
    await page.evaluate(() => {
      const sources = (window as any).__opspilotEventSources;
      sources.at(-1).open();
    });
    await expect(page.getByText(/已切换为自动刷新/)).toHaveCount(0);
    await expect(page.getByText('Realtime event arrived')).toHaveCount(1);
  });

  for (const width of [1440, 1024, 768, 375]) {
    test(`does not overflow horizontally at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await installOpsPilotMocks(page, {
        runId: `run-responsive-${width}`,
        service: 'payment-service-with-an-intentionally-long-name',
        initialRunStatus: 'COMPLETED',
      });
      await page.goto(`/runs/run-responsive-${width}`);
      await expect(page.getByRole('button', { name: '事件流' })).toBeVisible();

      const overflow = await page.evaluate(() => ({
        documentWidth: document.documentElement.scrollWidth,
        viewportWidth: window.innerWidth,
      }));
      expect(overflow.documentWidth).toBeLessThanOrEqual(overflow.viewportWidth);
    });
  }
});
```

- [ ] **Step 3: Run Playwright smoke tests**

Run:

```bash
cd frontend
npm run test:e2e:smoke
```

Expected: PASS, including the new realtime and four responsive viewport checks.

- [ ] **Step 4: Commit browser regressions**

```bash
git add frontend/e2e/fixtures/mockApi.ts frontend/e2e/smoke-run-detail-realtime.spec.ts
git commit -m "frontend: cover realtime run detail browser states"
```

---

### Task 8: Run Full Verification And Manual Browser QA

**Files:**
- Verify only; do not modify unrelated files.

- [ ] **Step 1: Run the backend regression suite**

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/ -x -q
```

Expected: PASS.

- [ ] **Step 2: Run the frontend regression suite and build**

```bash
cd frontend
npx vitest run
npm run build
```

Expected: PASS.

- [ ] **Step 3: Run Playwright smoke coverage**

```bash
cd frontend
npm run test:e2e:smoke
```

Expected: PASS.

- [ ] **Step 4: Start the local app and verify the real data path**

Run:

```bash
./start-dev.sh
curl http://127.0.0.1:8000/healthz
```

Expected health response:

```json
{"status":"ok"}
```

Create a mock-mode manual incident:

```bash
curl -s -X POST http://127.0.0.1:8000/incidents/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "ticket": {
      "ticket_id": "INC-REALTIME-QA",
      "title": "Realtime detail QA",
      "description": "Verify run details update without a browser reload",
      "service": "payment-service",
      "env": "staging",
      "severity": "P2",
      "source": "manual"
    }
  }'
```

Open the returned `/runs/{run_id}` route with the Browser plugin and verify:

- Events append without manual browser refresh.
- Evidence, diagnosis, and remediation appear progressively.
- Existing content remains visible during later refreshes.
- DevTools network blocking or backend interruption surfaces the fallback notice.
- Recovery removes the fallback notice.

- [ ] **Step 5: Verify responsive spacing with Browser**

Using the Browser plugin, inspect the run detail page at:

- `1440x900`
- `1024x900`
- `768x900`
- `375x900`

Confirm:

- No overlapping cards or text.
- No horizontal page scrollbar.
- Header, status badge, warning notice, and tabs wrap cleanly.
- Long service names, run IDs, event messages, evidence summaries, and remediation rows remain readable.

- [ ] **Step 6: Confirm the final diff scope**

Run:

```bash
git status --short
git diff --check
git log --oneline --max-count=8
```

Expected:

- No whitespace errors.
- No `.env`, database, `node_modules`, or Playwright artifact files staged.
- Existing user edits outside this feature remain intact.
