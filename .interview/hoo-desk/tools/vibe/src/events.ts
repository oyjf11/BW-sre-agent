import * as fs from 'fs';

export interface VibeEvent {
  ts: string;
  type: string;
  task_id?: string;
  from?: string;
  to?: string;
  detail?: string;
}

export function appendEvent(path: string, ev: VibeEvent): void {
  fs.appendFileSync(path, JSON.stringify(ev) + '\n');
}

export function readEvents(path: string): VibeEvent[] {
  if (!fs.existsSync(path)) return [];
  return fs.readFileSync(path, 'utf-8').split('\n').filter(Boolean).map((l) => JSON.parse(l) as VibeEvent);
}
