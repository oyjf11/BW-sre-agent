import { describe, it, expect, afterEach } from 'vitest';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { appendEvent, readEvents } from './events';

let tmp: string | null = null;
function tmpFile(): string {
  tmp = path.join(os.tmpdir(), `vibe-events-${process.pid}-${Math.floor(performance.now())}.jsonl`);
  return tmp;
}
afterEach(() => { if (tmp && fs.existsSync(tmp)) fs.unlinkSync(tmp); tmp = null; });

describe('events.jsonl', () => {
  it('round-trips appended events in order', () => {
    const f = tmpFile();
    appendEvent(f, { ts: '2026-06-07T00:00:00Z', type: 'transition', task_id: 'T1', from: 'pending', to: 'doing' });
    appendEvent(f, { ts: '2026-06-07T00:00:01Z', type: 'dispatch', task_id: 'T1', detail: 'test-generator' });
    const evs = readEvents(f);
    expect(evs).toHaveLength(2);
    expect(evs[0].to).toBe('doing');
    expect(evs[1].detail).toBe('test-generator');
  });
  it('returns [] for a missing file', () => {
    expect(readEvents(path.join(os.tmpdir(), 'vibe-nope-xyz.jsonl'))).toEqual([]);
  });
});
