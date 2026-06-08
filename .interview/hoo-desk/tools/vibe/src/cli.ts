import * as fs from 'fs';
import * as path from 'path';
import { AcFileSchema, TaskFile } from './contracts';
import { loadTaskFile, saveTaskFile, selectNext, transition } from './state';
import { appendEvent } from './events';
import { detectFromProject } from './detect';
import { buildProfile } from './profile';
import { extractTests, checkCoverage, PlaywrightResult } from './coverage-checker';

export interface CliCtx {
  cwd: string;
  now: string;                 // injected timestamp (no Date.now in core)
  log?: (s: string) => void;
}

function out(ctx: CliCtx, s: string): void {
  (ctx.log ?? ((x: string) => process.stdout.write(x + '\n')))(s);
}
const p = (ctx: CliCtx, ...segs: string[]) => path.join(ctx.cwd, ...segs);
const TASK_PATH = ['.vibe', 'runtime', 'task.json'];
const EVENTS_PATH = ['.vibe', 'runtime', 'events.jsonl'];

function normalizeResults(raw: any): PlaywrightResult[] {
  const rows: PlaywrightResult[] = [];
  const walk = (suite: any) => {
    for (const spec of suite.specs ?? []) {
      const status = spec.tests?.[0]?.results?.[0]?.status ?? 'skipped';
      rows.push({ title: spec.title, status });
    }
    for (const child of suite.suites ?? []) walk(child);
  };
  for (const s of raw.suites ?? []) walk(s);
  return rows;
}

export function runCli(argv: string[], ctx: CliCtx): number {
  const [cmd, ...rest] = argv;

  if (cmd === 'detect') {
    const fw = detectFromProject(ctx.cwd);
    const project = path.basename(ctx.cwd);
    const profile = buildProfile(fw, project);
    fs.mkdirSync(p(ctx, '.vibe'), { recursive: true });
    fs.writeFileSync(p(ctx, '.vibe', 'profile.json'), JSON.stringify(profile, null, 2));
    out(ctx, fw);
    return 0;
  }

  if (cmd === 'init') {
    const acFile = path.resolve(ctx.cwd, rest[0]);
    const acRaw = JSON.parse(fs.readFileSync(acFile, 'utf-8'));
    const ac = AcFileSchema.parse(acRaw);
    const tf: TaskFile = {
      run_id: `run-${ac.feature}`,
      created_at: ctx.now,
      tasks: [{
        id: 'T1', type: 'test', ac_refs: ac.criteria.map((c) => c.id),
        priority: 1, seq: 1, status: 'pending', attempts: 0, max_attempts: 3,
      }],
    };
    fs.mkdirSync(p(ctx, '.vibe', 'runtime'), { recursive: true });
    saveTaskFile(p(ctx, ...TASK_PATH), tf);
    appendEvent(p(ctx, ...EVENTS_PATH), { ts: ctx.now, type: 'init', detail: ac.feature });
    return 0;
  }

  if (cmd === 'next') {
    const tf = loadTaskFile(p(ctx, ...TASK_PATH));
    const task = selectNext(tf.tasks);
    out(ctx, task ? JSON.stringify(task) : 'DONE');
    return 0;
  }

  if (cmd === 'complete') {
    const [id, to] = rest;
    const tf = loadTaskFile(p(ctx, ...TASK_PATH));
    const idx = tf.tasks.findIndex((t) => t.id === id);
    if (idx < 0) { out(ctx, `unknown task ${id}`); return 1; }
    const from = tf.tasks[idx].status;
    try {
      tf.tasks[idx] = transition(tf.tasks[idx], to as any);
    } catch (e: any) {
      out(ctx, `transition error: ${e.message}`);
      return 1;
    }
    saveTaskFile(p(ctx, ...TASK_PATH), tf);
    appendEvent(p(ctx, ...EVENTS_PATH), { ts: ctx.now, type: 'transition', task_id: id, from, to });
    return 0;
  }

  if (cmd === 'check') {
    const [rawAc, rawE2e, rawResults] = rest;
    const acPath = path.resolve(ctx.cwd, rawAc);
    const e2eDir = path.resolve(ctx.cwd, rawE2e);
    const resultsPath = path.resolve(ctx.cwd, rawResults);
    const ac = AcFileSchema.parse(JSON.parse(fs.readFileSync(acPath, 'utf-8')));
    const specFiles = fs.existsSync(e2eDir)
      ? fs.readdirSync(e2eDir).filter((f) => f.endsWith('.spec.ts'))
      : [];
    const tests = specFiles.flatMap((f) => extractTests(fs.readFileSync(path.join(e2eDir, f), 'utf-8')));
    const results = normalizeResults(JSON.parse(fs.readFileSync(resultsPath, 'utf-8')));
    const report = checkCoverage(ac, tests, results);
    fs.mkdirSync(p(ctx, '.vibe', 'reports'), { recursive: true });
    fs.writeFileSync(p(ctx, '.vibe', 'reports', 'coverage.json'), JSON.stringify(report, null, 2));
    appendEvent(p(ctx, ...EVENTS_PATH), { ts: ctx.now, type: 'check', detail: report.passed ? 'PASS' : 'FAIL' });
    return report.passed ? 0 : 1;
  }

  out(ctx, `unknown command: ${cmd}`);
  return 2;
}

// Entry point when run via `tsx src/cli.ts ...`
if (import.meta.url === `file://${process.argv[1]}`) {
  const code = runCli(process.argv.slice(2), { cwd: process.cwd(), now: new Date().toISOString() });
  process.exit(code);
}
