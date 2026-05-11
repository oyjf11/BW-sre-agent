const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const POLL_INTERVAL = 3000;

type EventCallback = (data: unknown) => void;

class SseClient {
  private eventSource: EventSource | null = null;
  private pollingTimer: number | null = null;
  private fallbackMode = false;
  private callbacks: Map<string, EventCallback[]> = new Map();
  private lastEventId: string | null = null;

  connect(endpoint: string) {
    const url = `${API_BASE}${endpoint}`;
    
    try {
      this.eventSource = new EventSource(url);
      
      this.eventSource.onopen = () => {
        this.fallbackMode = false;
        console.log('SSE connected');
      };

      this.eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.notify('message', data);
      };

      this.eventSource.onerror = () => {
        if (!this.fallbackMode) {
          this.fallbackMode = true;
          this.eventSource?.close();
          this.startPolling(endpoint);
        }
      };
    } catch {
      this.fallbackMode = true;
      this.startPolling(endpoint);
    }
  }

  private startPolling(endpoint: string) {
    console.log('Falling back to polling mode');
    const poll = async () => {
      try {
        const url = this.lastEventId 
          ? `${API_BASE}${endpoint}?last_event_ts=${encodeURIComponent(this.lastEventId)}`
          : `${API_BASE}${endpoint}`;
        
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          if (Array.isArray(data)) {
            data.forEach(item => this.notify('message', item));
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    poll();
    this.pollingTimer = window.setInterval(poll, POLL_INTERVAL);
  }

  on(event: string, callback: EventCallback) {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, []);
    }
    this.callbacks.get(event)!.push(callback);
  }

  off(event: string, callback: EventCallback) {
    const cbs = this.callbacks.get(event);
    if (cbs) {
      const idx = cbs.indexOf(callback);
      if (idx >= 0) cbs.splice(idx, 1);
    }
  }

  private notify(event: string, data: unknown) {
    const cbs = this.callbacks.get(event);
    if (cbs) {
      cbs.forEach(cb => cb(data));
    }
  }

  disconnect() {
    this.eventSource?.close();
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
    }
  }
}

export const sseClient = new SseClient();
