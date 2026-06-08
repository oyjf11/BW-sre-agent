import { describe, it, expect, afterEach } from 'vitest';
import { existsSync, unlinkSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { selectNext, transition, loadTaskFile, saveTaskFile } from './state';
import { Task } from './contracts';
import type { TaskFile } from './contracts';

function task(p: Partial<Task>): Task {
  return {
    id: 'T', type: 'test', ac_refs: [], priority: 1, seq: 1,
    status: 'pending', attempts: 0, max_attempts: 3, ...p,
  };
}

describe('selectNext (recovery-aware task selection)', () => {
  it('prefers doing with highest priority (recovery path)', () => {
    const next = selectNext([
      task({ id: 'A', status: 'pending', priority: 1 }),
      task({ id: 'B', status: 'doing', priority: 2 }),
      task({ id: 'C', status: 'doing', priority: 1 }),
    ]);
    expect(next?.id).toBe('C');
  });
  it('with no doing, picks highest-priority pending', () => {
    const next = selectNext([
      task({ id: 'A', status: 'pending', priority: 2, seq: 1 }),
      task({ id: 'B', status: 'pending', priority: 1, seq: 5 }),
    ]);
    expect(next?.id).toBe('B');
  });
  it('breaks priority ties by seq', () => {
    const next = selectNext([
      task({ id: 'A', status: 'pending', priority: 1, seq: 2 }),
      task({ id: 'B', status: 'pending', priority: 1, seq: 1 }),
    ]);
    expect(next?.id).toBe('B');
  });
  it('returns null when all terminal', () => {
    expect(selectNext([
      task({ id: 'A', status: 'passing' }),
      task({ id: 'B', status: 'failing' }),
    ])).toBeNull();
  });
});

describe('transition', () => {
  it('allows pending → doing', () => {
    expect(transition(task({ status: 'pending' }), 'doing').status).toBe('doing');
  });
  it('allows doing → passing', () => {
    expect(transition(task({ status: 'doing' }), 'passing').status).toBe('passing');
  });
  it('allows failing → doing (retry)', () => {
    expect(transition(task({ status: 'failing' }), 'doing').status).toBe('doing');
  });
  it('rejects pending → passing (must go through doing)', () => {
    expect(() => transition(task({ status: 'pending' }), 'passing')).toThrow();
  });
  it('rejects any transition out of passing (terminal)', () => {
    expect(() => transition(task({ status: 'passing' }), 'doing')).toThrow();
  });
});

describe('loadTaskFile / saveTaskFile', () => {
  let tmp: string | null = null;
  afterEach(() => { if (tmp && existsSync(tmp)) unlinkSync(tmp); tmp = null; });

  it('round-trips a TaskFile', () => {
    tmp = join(tmpdir(), `vibe-state-${process.pid}.json`);
    const tf: TaskFile = {
      run_id: 'r1',
      created_at: '2026-06-07T00:00:00Z',
      tasks: [{
        id: 'T1', type: 'test', ac_refs: ['AC-1'],
        priority: 1, seq: 1, status: 'pending', attempts: 0, max_attempts: 3,
      }],
    };
    saveTaskFile(tmp, tf);
    const loaded = loadTaskFile(tmp);
    expect(loaded.run_id).toBe('r1');
    expect(loaded.tasks[0].id).toBe('T1');
  });

  it('throws with context on missing file', () => {
    const missing = join(tmpdir(), 'vibe-state-missing-xyz.json');
    expect(() => loadTaskFile(missing)).toThrow(/failed to load task file/);
  });
});
