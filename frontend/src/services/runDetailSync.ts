import type { RunDetail, RunEvent } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const POLL_INTERVAL = 3000;
const RECONNECT_INTERVAL = 5000;
const STATUS_INTERVAL = 5000;
const ARTIFACT_REFRESH_DELAY = 750;
const STOPPED_STATUSES = new Set(['COMPLETED', 'FAILED', 'NEEDS_HUMAN']);

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
  private options: RunDetailSyncOptions;

  constructor(options: RunDetailSyncOptions) {
    this.options = options;
  }

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
