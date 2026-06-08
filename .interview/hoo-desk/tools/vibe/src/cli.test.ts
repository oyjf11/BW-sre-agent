import { describe, it, expect, afterEach } from 'vitest';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { runCli } from './cli';

let work: string | null = null;
function workdir(): string {
  work = fs.mkdtempSync(path.join(os.tmpdir(), 'vibe-cli-'));
  return work;
}
afterEach(() => { if (work && fs.existsSync(work)) fs.rmSync(work, { recursive: true, force: true }); work = null; });

function writeAc(dir: string): string {
  const acDir = path.join(dir, '.vibe/specs/acceptance');
  fs.mkdirSync(acDir, { recursive: true });
  const file = path.join(acDir, 'checkout.ac.json');
  fs.writeFileSync(file, JSON.stringify({
    feature: 'checkout',
    target: { page: 'p', route: '/checkout' },
    criteria: [
      { id: 'AC-1', priority: 1, desc: 'd', given: 'g', when: 'w', then: { observable: 'toast', expect_text: 'A' } },
    ],
  }));
  return file;
}

describe('vibe CLI', () => {
  it('init creates task.json with one test task referencing all AC ids', () => {
    const dir = workdir();
    const ac = writeAc(dir);
    const code = runCli(['init', ac], { cwd: dir, now: '2026-06-07T00:00:00Z' });
    expect(code).toBe(0);
    const tf = JSON.parse(fs.readFileSync(path.join(dir, '.vibe/runtime/task.json'), 'utf-8'));
    expect(tf.tasks).toHaveLength(1);
    expect(tf.tasks[0].ac_refs).toEqual(['AC-1']);
    expect(tf.tasks[0].status).toBe('pending');
  });

  it('next prints the selected task id, complete advances it', () => {
    const dir = workdir();
    const ac = writeAc(dir);
    runCli(['init', ac], { cwd: dir, now: '2026-06-07T00:00:00Z' });

    const lines: string[] = [];
    const log = (s: string) => lines.push(s);
    runCli(['next'], { cwd: dir, now: '2026-06-07T00:00:01Z', log });
    expect(lines.join('')).toContain('T1');

    // mark doing then passing
    runCli(['complete', 'T1', 'doing'], { cwd: dir, now: '2026-06-07T00:00:02Z' });
    runCli(['complete', 'T1', 'passing'], { cwd: dir, now: '2026-06-07T00:00:03Z' });

    const done: string[] = [];
    runCli(['next'], { cwd: dir, now: '2026-06-07T00:00:04Z', log: (s) => done.push(s) });
    expect(done.join('')).toContain('DONE');
  });

  it('check exits non-zero when coverage has a MISSING verdict', () => {
    const dir = workdir();
    const ac = writeAc(dir);          // AC-1 expects toast 'A'
    const e2e = path.join(dir, 'e2e');
    fs.mkdirSync(e2e, { recursive: true });
    // spec covers a different, orphan AC — AC-1 will be MISSING
    fs.writeFileSync(path.join(e2e, 'checkout.spec.ts'),
      `test('[AC-99] orphan', async ({ page }) => { await expect(page.locator('x')).toContainText('Z'); });`);
    const results = path.join(dir, '.vibe/runtime/pw-results.json');
    fs.mkdirSync(path.dirname(results), { recursive: true });
    fs.writeFileSync(results, JSON.stringify({ suites: [{ specs: [
      { title: '[AC-99] orphan', tests: [{ results: [{ status: 'passed' }] }] },
    ] }] }));

    const code = runCli(['check', ac, e2e, results], { cwd: dir, now: '2026-06-07T00:00:05Z' });
    expect(code).toBe(1);
    const report = JSON.parse(fs.readFileSync(path.join(dir, '.vibe/reports/coverage.json'), 'utf-8'));
    expect(report.passed).toBe(false);
    expect(report.rows.some((r: any) => r.verdict === 'MISSING')).toBe(true);
  });
});
