# Vibe Dev Toolkit (Phase 1: A+B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a framework-agnostic AI test harness that turns structured acceptance criteria (AC) into real Playwright runs and deterministically catches three classes of LLM testing hallucination (execution / assertion / coverage), plus a Bad Case learning loop — validated on the real Vue2 project hoo-desk's login page.

**Architecture:** A deterministic TypeScript "spine" (state machine + task-selection algorithm + zod contracts + coverage-checker) exposed as a CLI, called by OpenCode LLM agents (generator/analyst) via shell — mirroring hoo-desk's existing `task-management/router.sh` pattern. The spine has ZERO business knowledge; it adapts to projects via a framework detector (vue2/vue3/react16±) and pluggable selector adapters. The LLM generates Playwright specs; the deterministic checker — not the LLM — decides pass/fail.

**Tech Stack:** TypeScript + Node 22, Vitest (unit tests), zod (contracts), js-yaml (Bad Case store), Playwright (E2E execution). Toolchain is ESM, run via `tsx`. Target app hoo-desk stays Vue2+JS, untouched.

---

## Base Directory & Git

- **Toolchain + config + AC live inside hoo-desk** (its own git repo): `/Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/`
- All `tools/vibe` commands run from: `/Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/tools/vibe`
- **Before Task 1**, create a feature branch in the hoo-desk repo:
  ```bash
  cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
  git checkout -b feat/vibe-test-toolkit
  ```
- The design spec stays in the sre-agent repo (`docs/superpowers/specs/2026-06-07-vibe-dev-toolkit-design.md`) and is NOT part of these commits.

## File Structure (locked decomposition)

All paths relative to `/Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/`:

```
tools/vibe/
├── package.json                 # ESM toolchain deps (vitest/zod/js-yaml/@playwright/test/tsx)
├── tsconfig.json
├── src/
│   ├── contracts.ts             # ALL zod schemas + inferred types (the shared vocabulary)
│   ├── detect.ts                # package.json → Framework enum (vue2/vue3/react16±)
│   ├── profile.ts               # Framework → Profile defaults (buildProfile)
│   ├── state.ts                 # task.json load/save + selectNext + transition
│   ├── events.ts                # events.jsonl append/read
│   ├── adapters/
│   │   ├── types.ts             # SelectorAdapter interface
│   │   ├── vue2.ts              # SOLID (target is vue2)
│   │   ├── vue3.ts             # skeleton (throws notImplemented)
│   │   ├── react16-minus.ts    # skeleton
│   │   ├── react16-plus.ts     # skeleton
│   │   └── index.ts            # getAdapter(framework) registry
│   ├── coverage-checker.ts      # ★ extractTests + checkCoverage → 5 verdicts (防线②③)
│   ├── badcase.ts               # compound (write yaml) + research (retrieve)
│   └── cli.ts                   # wires spine into a CLI: init/next/complete/check/detect/hints
│   └── *.test.ts                # Vitest unit tests colocated
.opencode/
├── command/
│   ├── vibe-test.md             # entry: AC → three defenses
│   ├── learning-compound.md     # Bad Case sink
│   └── learning-researcher.md   # Bad Case retrieval
└── agent/
    ├── test-orchestrator.md     # deterministic-ish driver (calls vibe CLI)
    ├── test-generator.md        # AC → Playwright spec.ts
    └── test-analyst.md          # failure → Bad Case
.vibe/
├── profile.json                 # detector output (committed for hoo-desk)
├── specs/acceptance/login.ac.json
playwright.config.ts             # at hoo-desk root, points at e2e/
e2e/                             # generated specs land here
```

**Responsibility boundaries:** `contracts.ts` is the single source of types — every other file imports from it. `coverage-checker.ts` is the deterministic heart (proves the three defenses). `cli.ts` is the only file that touches process args / orchestration. Adapters are the ONLY place framework-level words (`element-ui`) may appear.

---

### Task 1: Scaffold the toolchain

**Files:**
- Create: `tools/vibe/package.json`
- Create: `tools/vibe/tsconfig.json`
- Create: `tools/vibe/src/smoke.test.ts`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "vibe-test-toolkit",
  "version": "0.1.0",
  "type": "module",
  "private": true,
  "scripts": {
    "test": "vitest run",
    "vibe": "tsx src/cli.ts"
  },
  "dependencies": {
    "js-yaml": "^4.1.0",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@playwright/test": "^1.48.0",
    "@types/js-yaml": "^4.0.9",
    "@types/node": "^22.0.0",
    "tsx": "^4.19.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "types": ["node"],
    "noEmit": true
  },
  "include": ["src"]
}
```

- [ ] **Step 3: Write a smoke test**

Create `tools/vibe/src/smoke.test.ts`:

```ts
import { describe, it, expect } from 'vitest';

describe('toolchain', () => {
  it('runs vitest', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] **Step 4: Install deps and run the smoke test**

Run:
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/tools/vibe
npm install
npx vitest run
```
Expected: 1 passed. (npm install also pulls Playwright's npm package; browser binaries are installed later in Task 12.)

- [ ] **Step 5: Add a toolchain-scoped gitignore and commit**

Create `tools/vibe/.gitignore`:
```
node_modules/
```

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/package.json tools/vibe/tsconfig.json tools/vibe/src/smoke.test.ts tools/vibe/.gitignore
git commit -m "vibe: scaffold test toolchain (vitest+zod+tsx)"
```

---

### Task 2: Contracts (all zod schemas)

**Files:**
- Create: `tools/vibe/src/contracts.ts`
- Test: `tools/vibe/src/contracts.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/contracts.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import {
  EnvelopeSchema, AcFileSchema, ProfileSchema, BadCaseSchema, TaskFileSchema,
} from './contracts';

describe('EnvelopeSchema', () => {
  it('accepts a valid envelope', () => {
    const ok = EnvelopeSchema.safeParse({
      header: { agent: 'test-generator', stage: 'generate', status: 'PASS', attempt: 0 },
      payload: { any: 'thing' },
      meta: { warnings: [], needs_user_input: false },
    });
    expect(ok.success).toBe(true);
  });
  it('rejects an illegal status', () => {
    const bad = EnvelopeSchema.safeParse({
      header: { agent: 'x', stage: 'y', status: 'OK', attempt: 0 },
      payload: {}, meta: {},
    });
    expect(bad.success).toBe(false);
  });
});

describe('AcFileSchema', () => {
  it('requires at least one criterion', () => {
    const bad = AcFileSchema.safeParse({
      feature: 'login', target: { page: 'p', route: '/login' }, criteria: [],
    });
    expect(bad.success).toBe(false);
  });
  it('accepts a well-formed AC', () => {
    const ok = AcFileSchema.safeParse({
      feature: 'login',
      target: { page: 'src/views/public/login.vue', route: '/login' },
      criteria: [{
        id: 'AC-LOGIN-01', priority: 1, desc: 'd', given: 'g', when: 'w',
        then: { observable: 'toast', expect_text: 'x' },
      }],
    });
    expect(ok.success).toBe(true);
  });
});

describe('ProfileSchema', () => {
  it('rejects an unknown framework', () => {
    const bad = ProfileSchema.safeParse({
      project: 'p', framework: 'svelte',
      dev: { command: 'c', ready_log: 'r', base_url: 'u', timeout_ms: 1 },
      ui: { adapter: 'a', toast_selector: 't', input_strategy: 'i' },
      acceptance_dir: 'a', e2e_out_dir: 'e',
    });
    expect(bad.success).toBe(false);
  });
});

describe('BadCaseSchema + TaskFileSchema', () => {
  it('validates a badcase', () => {
    const ok = BadCaseSchema.safeParse({
      id: 'BC-1', feature: 'login', type: 'coverage_gap',
      symptom: 's', root_cause: 'r', fix_hint: 'f', created_at: '2026-06-07',
    });
    expect(ok.success).toBe(true);
  });
  it('validates a task file with status enum', () => {
    const bad = TaskFileSchema.safeParse({
      run_id: 'r', created_at: 't',
      tasks: [{ id: 'T1', type: 'test', ac_refs: [], priority: 1, seq: 1,
                status: 'WRONG', attempts: 0, max_attempts: 3 }],
    });
    expect(bad.success).toBe(false);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/tools/vibe && npx vitest run src/contracts.test.ts`
Expected: FAIL — `Cannot find module './contracts'`.

- [ ] **Step 3: Implement contracts.ts**

Create `tools/vibe/src/contracts.ts`:

```ts
import { z } from 'zod';

// ── Framework enum (shared by detect/profile/adapters) ──
export const FrameworkSchema = z.enum(['vue2', 'vue3', 'react16-minus', 'react16-plus']);
export type Framework = z.infer<typeof FrameworkSchema>;

// ── Agent response envelope ──
export const EnvelopeSchema = z.object({
  header: z.object({
    agent: z.string(),
    stage: z.string(),
    status: z.enum(['PASS', 'FAIL', 'PARTIAL']),
    attempt: z.number().int().min(0),
  }),
  payload: z.unknown(),
  meta: z.object({
    warnings: z.array(z.string()).default([]),
    needs_user_input: z.boolean().default(false),
  }),
});
export type Envelope = z.infer<typeof EnvelopeSchema>;

// ── Acceptance Criteria ──
export const AcThenSchema = z.object({
  observable: z.string(),               // 'toast' | 'url' | 'text' ...
  expect_text: z.string().optional(),
  expect_value: z.string().optional(),
});
export const AcCriterionSchema = z.object({
  id: z.string(),
  priority: z.number().int(),
  desc: z.string(),
  given: z.string(),
  when: z.string(),
  then: AcThenSchema,
});
export type AcCriterion = z.infer<typeof AcCriterionSchema>;

export const AcFileSchema = z.object({
  feature: z.string(),
  target: z.object({ page: z.string(), route: z.string() }),
  criteria: z.array(AcCriterionSchema).min(1),
});
export type AcFile = z.infer<typeof AcFileSchema>;

// ── Project profile (detector output) ──
export const ProfileSchema = z.object({
  project: z.string(),
  framework: FrameworkSchema,
  dev: z.object({
    command: z.string(),
    ready_log: z.string(),
    base_url: z.string(),
    timeout_ms: z.number().int(),
  }),
  ui: z.object({
    adapter: z.string(),
    toast_selector: z.string(),
    input_strategy: z.string(),
  }),
  acceptance_dir: z.string(),
  e2e_out_dir: z.string(),
});
export type Profile = z.infer<typeof ProfileSchema>;

// ── Coverage report (the three-defense verdicts) ──
export const VerdictSchema = z.enum(['COVERED', 'MISSING', 'CLAIMED_NOT_RUN', 'HOLLOW', 'ORPHAN']);
export type Verdict = z.infer<typeof VerdictSchema>;

export const CoverageRowSchema = z.object({
  ac_id: z.string().nullable(),
  test_title: z.string().nullable(),
  verdict: VerdictSchema,
  detail: z.string(),
});
export type CoverageRow = z.infer<typeof CoverageRowSchema>;

export const CoverageReportSchema = z.object({
  feature: z.string(),
  rows: z.array(CoverageRowSchema),
  passed: z.boolean(),
});
export type CoverageReport = z.infer<typeof CoverageReportSchema>;

// ── Bad Case ──
export const BadCaseSchema = z.object({
  id: z.string(),
  feature: z.string(),
  type: z.enum(['coverage_gap', 'hollow_assertion', 'exec_fail', 'claimed_not_run']),
  ac_id: z.string().optional(),
  symptom: z.string(),
  root_cause: z.string(),
  fix_hint: z.string(),
  created_at: z.string(),
});
export type BadCase = z.infer<typeof BadCaseSchema>;

// ── Task state machine ──
export const TaskSchema = z.object({
  id: z.string(),
  type: z.string(),                     // Phase 1: only 'test'
  ac_refs: z.array(z.string()),
  priority: z.number().int(),
  seq: z.number().int(),
  status: z.enum(['pending', 'doing', 'passing', 'failing']),
  attempts: z.number().int(),
  max_attempts: z.number().int(),
});
export type Task = z.infer<typeof TaskSchema>;

export const TaskFileSchema = z.object({
  run_id: z.string(),
  created_at: z.string(),
  tasks: z.array(TaskSchema),
});
export type TaskFile = z.infer<typeof TaskFileSchema>;
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/contracts.test.ts`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/contracts.ts tools/vibe/src/contracts.test.ts
git commit -m "vibe: add zod contracts (envelope/AC/profile/coverage/badcase/task)"
```

---

### Task 3: Framework detector

**Files:**
- Create: `tools/vibe/src/detect.ts`
- Test: `tools/vibe/src/detect.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/detect.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { detectFramework } from './detect';

describe('detectFramework', () => {
  it('vue ^2.5.2 → vue2', () => {
    expect(detectFramework({ dependencies: { vue: '^2.5.2' } })).toBe('vue2');
  });
  it('vue ^3.4.0 → vue3', () => {
    expect(detectFramework({ dependencies: { vue: '^3.4.0' } })).toBe('vue3');
  });
  it('react 16.8.0 → react16-plus (hooks boundary inclusive)', () => {
    expect(detectFramework({ dependencies: { react: '16.8.0' } })).toBe('react16-plus');
  });
  it('react 16.3.0 → react16-minus', () => {
    expect(detectFramework({ dependencies: { react: '16.3.0' } })).toBe('react16-minus');
  });
  it('react ^17.0.2 → react16-plus', () => {
    expect(detectFramework({ dependencies: { react: '^17.0.2' } })).toBe('react16-plus');
  });
  it('reads devDependencies too', () => {
    expect(detectFramework({ devDependencies: { vue: '~2.6.0' } })).toBe('vue2');
  });
  it('throws when no vue/react', () => {
    expect(() => detectFramework({ dependencies: { lodash: '^4' } })).toThrow();
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/detect.test.ts`
Expected: FAIL — `Cannot find module './detect'`.

- [ ] **Step 3: Implement detect.ts**

Create `tools/vibe/src/detect.ts`:

```ts
import * as fs from 'fs';
import * as path from 'path';
import { Framework } from './contracts';

interface PkgJson {
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
}

function cleanVer(v: string): string {
  return v.replace(/^[\^~>=<\s]+/, '');
}
function majorMinor(v: string): { major: number; minor: number } {
  const parts = cleanVer(v).split('.');
  return { major: parseInt(parts[0], 10), minor: parseInt(parts[1] || '0', 10) };
}

export function detectFramework(pkg: PkgJson): Framework {
  const deps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
  if (deps.vue) {
    const { major } = majorMinor(deps.vue);
    if (major === 2) return 'vue2';
    if (major >= 3) return 'vue3';
  }
  if (deps.react) {
    const { major, minor } = majorMinor(deps.react);
    if (major > 16 || (major === 16 && minor >= 8)) return 'react16-plus';
    return 'react16-minus';
  }
  throw new Error('unsupported framework: no vue/react dependency found');
}

export function detectFromProject(root: string): Framework {
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf-8'));
  return detectFramework(pkg);
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/detect.test.ts`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/detect.ts tools/vibe/src/detect.test.ts
git commit -m "vibe: framework detector (vue2/vue3/react16 boundary)"
```

---

### Task 4: Profile builder

**Files:**
- Create: `tools/vibe/src/profile.ts`
- Test: `tools/vibe/src/profile.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/profile.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { buildProfile } from './profile';
import { ProfileSchema } from './contracts';

describe('buildProfile', () => {
  it('produces a schema-valid vue2 profile with element-ui defaults', () => {
    const p = buildProfile('vue2', 'hoo-desk');
    expect(ProfileSchema.safeParse(p).success).toBe(true);
    expect(p.framework).toBe('vue2');
    expect(p.ui.adapter).toBe('vue2');
    expect(p.ui.toast_selector).toBe('.el-message');
    expect(p.dev.ready_log).toBe('Compiled successfully');
  });
  it('uses a generic default base_url (not project-specific)', () => {
    const p = buildProfile('vue2', 'anything');
    expect(p.dev.base_url).toBe('http://localhost:8080');
  });
  it('still builds a valid profile for non-vue2 (generic defaults)', () => {
    const p = buildProfile('react16-plus', 'demo');
    expect(ProfileSchema.safeParse(p).success).toBe(true);
    expect(p.ui.adapter).toBe('react16-plus');
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/profile.test.ts`
Expected: FAIL — `Cannot find module './profile'`.

- [ ] **Step 3: Implement profile.ts**

Create `tools/vibe/src/profile.ts`:

```ts
import { Framework, Profile, ProfileSchema } from './contracts';

// Framework-level UI defaults. These are generic (framework-scoped), NOT project-specific.
// Per-project overrides live in .vibe/profile.json, never in code.
const UI_DEFAULTS: Record<Framework, { toast_selector: string; ready_log: string }> = {
  vue2: { toast_selector: '.el-message', ready_log: 'Compiled successfully' },
  vue3: { toast_selector: '.el-message', ready_log: 'ready in' },
  'react16-minus': { toast_selector: '.ant-message', ready_log: 'Compiled successfully' },
  'react16-plus': { toast_selector: '.ant-message', ready_log: 'Compiled successfully' },
};

export function buildProfile(framework: Framework, project: string): Profile {
  const ui = UI_DEFAULTS[framework];
  const profile: Profile = {
    project,
    framework,
    dev: {
      command: 'npm run dev',
      ready_log: ui.ready_log,
      base_url: 'http://localhost:8080',
      timeout_ms: 180000,
    },
    ui: {
      adapter: framework,
      toast_selector: ui.toast_selector,
      input_strategy: 'placeholder',
    },
    acceptance_dir: '.vibe/specs/acceptance',
    e2e_out_dir: 'e2e',
  };
  return ProfileSchema.parse(profile);
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/profile.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/profile.ts tools/vibe/src/profile.test.ts
git commit -m "vibe: profile builder with framework-scoped UI defaults"
```

---

### Task 5: Task state machine + selection algorithm

**Files:**
- Create: `tools/vibe/src/state.ts`
- Test: `tools/vibe/src/state.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/state.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { selectNext, transition } from './state';
import { Task } from './contracts';

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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/state.test.ts`
Expected: FAIL — `Cannot find module './state'`.

- [ ] **Step 3: Implement state.ts**

Create `tools/vibe/src/state.ts`:

```ts
import * as fs from 'fs';
import { Task, TaskFile, TaskFileSchema } from './contracts';

const byPrioritySeq = (a: Task, b: Task) => a.priority - b.priority || a.seq - b.seq;

// Deterministic next-task selection (control stays with code, never the LLM).
// Recovery: if any task is mid-flight ('doing'), resume the highest-priority one.
export function selectNext(tasks: Task[]): Task | null {
  const doing = tasks.filter((t) => t.status === 'doing').sort(byPrioritySeq);
  if (doing.length > 0) return doing[0];
  const pending = tasks.filter((t) => t.status === 'pending').sort(byPrioritySeq);
  if (pending.length > 0) return pending[0];
  return null;
}

const ALLOWED: Record<Task['status'], Task['status'][]> = {
  pending: ['doing'],
  doing: ['passing', 'failing', 'pending'], // pending = requeue
  passing: [],                              // terminal
  failing: ['doing'],                       // retry
};

export function transition(task: Task, to: Task['status']): Task {
  if (!ALLOWED[task.status].includes(to)) {
    throw new Error(`illegal transition ${task.status} -> ${to}`);
  }
  return { ...task, status: to };
}

export function loadTaskFile(path: string): TaskFile {
  return TaskFileSchema.parse(JSON.parse(fs.readFileSync(path, 'utf-8')));
}

export function saveTaskFile(path: string, tf: TaskFile): void {
  fs.writeFileSync(path, JSON.stringify(tf, null, 2));
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/state.test.ts`
Expected: PASS (9 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/state.ts tools/vibe/src/state.test.ts
git commit -m "vibe: task state machine + recovery-aware selectNext"
```

---

### Task 6: Event log

**Files:**
- Create: `tools/vibe/src/events.ts`
- Test: `tools/vibe/src/events.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/events.test.ts`:

```ts
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/events.test.ts`
Expected: FAIL — `Cannot find module './events'`.

- [ ] **Step 3: Implement events.ts**

Create `tools/vibe/src/events.ts`:

```ts
import * as fs from 'fs';

export interface VibeEvent {
  ts: string;              // ISO timestamp, injected by caller (never Date.now in this module)
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/events.test.ts`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/events.ts tools/vibe/src/events.test.ts
git commit -m "vibe: append-only events.jsonl log"
```

---

### Task 7: Selector adapters (vue2 solid, others skeleton)

**Files:**
- Create: `tools/vibe/src/adapters/types.ts`
- Create: `tools/vibe/src/adapters/vue2.ts`
- Create: `tools/vibe/src/adapters/vue3.ts`
- Create: `tools/vibe/src/adapters/react16-minus.ts`
- Create: `tools/vibe/src/adapters/react16-plus.ts`
- Create: `tools/vibe/src/adapters/index.ts`
- Test: `tools/vibe/src/adapters/adapters.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/adapters/adapters.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { getAdapter } from './index';
import { buildProfile } from '../profile';
import { AcCriterion } from '../contracts';

const profile = buildProfile('vue2', 'demo');
const toastAc: AcCriterion = {
  id: 'AC-1', priority: 1, desc: 'd', given: 'g', when: 'w',
  then: { observable: 'toast', expect_text: '请输入账号' },
};

describe('vue2 adapter', () => {
  const a = getAdapter('vue2');
  it('maps toast observable to the profile toast selector', () => {
    expect(a.toastSelector(profile)).toBe('.el-message');
  });
  it('builds a placeholder-based input selector', () => {
    expect(a.inputSelector('手机号', profile)).toBe("input[placeholder=\"手机号\"]");
  });
  it('emits an assertion snippet that embeds the AC expect_text', () => {
    const snip = a.assertionSnippet(toastAc, profile);
    expect(snip).toContain('请输入账号');
    expect(snip).toContain('.el-message');
  });
});

describe('skeleton adapters', () => {
  it('vue3 is registered but not implemented', () => {
    expect(() => getAdapter('vue3').toastSelector(profile)).toThrow(/not implemented/i);
  });
  it('react16-plus is registered but not implemented', () => {
    expect(() => getAdapter('react16-plus').toastSelector(profile)).toThrow(/not implemented/i);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/adapters/adapters.test.ts`
Expected: FAIL — `Cannot find module './index'`.

- [ ] **Step 3: Implement the adapter interface and implementations**

Create `tools/vibe/src/adapters/types.ts`:

```ts
import { AcCriterion, Framework, Profile } from '../contracts';

// A SelectorAdapter turns AC *semantic* anchors into framework/UI-specific
// Playwright selectors and assertion style. It may contain framework-level
// knowledge (element-ui, antd) — but NEVER project-specific knowledge.
export interface SelectorAdapter {
  framework: Framework;
  toastSelector(profile: Profile): string;
  inputSelector(label: string, profile: Profile): string;
  assertionSnippet(ac: AcCriterion, profile: Profile): string;
}

export function notImplemented(framework: Framework): never {
  throw new Error(`selector adapter for "${framework}" is not implemented yet`);
}
```

Create `tools/vibe/src/adapters/vue2.ts`:

```ts
import { SelectorAdapter } from './types';

export const vue2Adapter: SelectorAdapter = {
  framework: 'vue2',
  toastSelector(profile) {
    return profile.ui.toast_selector;
  },
  inputSelector(label, _profile) {
    return `input[placeholder="${label}"]`;
  },
  assertionSnippet(ac, profile) {
    if (ac.then.observable === 'toast' && ac.then.expect_text) {
      return `await expect(page.locator('${profile.ui.toast_selector}'))`
        + `.toContainText('${ac.then.expect_text}');`;
    }
    if (ac.then.observable === 'url' && ac.then.expect_value) {
      return `await expect(page).toHaveURL(/${ac.then.expect_value}/);`;
    }
    return `await expect(page.locator('body')).toContainText('${ac.then.expect_text ?? ''}');`;
  },
};
```

Create `tools/vibe/src/adapters/vue3.ts`:

```ts
import { SelectorAdapter, notImplemented } from './types';

// Skeleton: registered so detect() can route here, but strategy not yet built.
export const vue3Adapter: SelectorAdapter = {
  framework: 'vue3',
  toastSelector: () => notImplemented('vue3'),
  inputSelector: () => notImplemented('vue3'),
  assertionSnippet: () => notImplemented('vue3'),
};
```

Create `tools/vibe/src/adapters/react16-minus.ts`:

```ts
import { SelectorAdapter, notImplemented } from './types';

export const react16MinusAdapter: SelectorAdapter = {
  framework: 'react16-minus',
  toastSelector: () => notImplemented('react16-minus'),
  inputSelector: () => notImplemented('react16-minus'),
  assertionSnippet: () => notImplemented('react16-minus'),
};
```

Create `tools/vibe/src/adapters/react16-plus.ts`:

```ts
import { SelectorAdapter, notImplemented } from './types';

export const react16PlusAdapter: SelectorAdapter = {
  framework: 'react16-plus',
  toastSelector: () => notImplemented('react16-plus'),
  inputSelector: () => notImplemented('react16-plus'),
  assertionSnippet: () => notImplemented('react16-plus'),
};
```

Create `tools/vibe/src/adapters/index.ts`:

```ts
import { Framework } from '../contracts';
import { SelectorAdapter } from './types';
import { vue2Adapter } from './vue2';
import { vue3Adapter } from './vue3';
import { react16MinusAdapter } from './react16-minus';
import { react16PlusAdapter } from './react16-plus';

const REGISTRY: Record<Framework, SelectorAdapter> = {
  vue2: vue2Adapter,
  vue3: vue3Adapter,
  'react16-minus': react16MinusAdapter,
  'react16-plus': react16PlusAdapter,
};

export function getAdapter(framework: Framework): SelectorAdapter {
  return REGISTRY[framework];
}

export type { SelectorAdapter } from './types';
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/adapters/adapters.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/adapters
git commit -m "vibe: selector adapters (vue2 solid, vue3/react16 skeletons)"
```

---

### Task 8: Coverage checker (★ the three defenses)

**Files:**
- Create: `tools/vibe/src/coverage-checker.ts`
- Test: `tools/vibe/src/coverage-checker.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/coverage-checker.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { extractTests, checkCoverage, PlaywrightResult } from './coverage-checker';
import { AcFile } from './contracts';

describe('extractTests (static spec parsing)', () => {
  const source = `
    import { test, expect } from '@playwright/test';
    test('[AC-1] good', async ({ page }) => {
      await expect(page.locator('.el-message')).toContainText('A');
    });
    test('[AC-2] hollow', async ({ page }) => {
      expect(true).toBe(true);
    });
    test('no ac tag here', async ({ page }) => {
      await expect(page.locator('x')).toHaveText('Z');
    });
  `;
  it('parses ac_id from [AC-x] titles', () => {
    const tests = extractTests(source);
    expect(tests.map((t) => t.ac_id)).toEqual(['AC-1', 'AC-2', null]);
  });
  it('collects assertion texts per test', () => {
    const tests = extractTests(source);
    expect(tests[0].assertionTexts).toEqual(['A']);
    expect(tests[0].hasAssertion).toBe(true);
  });
  it('flags a test with no real assertion text', () => {
    const tests = extractTests(source);
    expect(tests[1].assertionTexts).toEqual([]);
  });
});

describe('checkCoverage (5 verdicts)', () => {
  const ac: AcFile = {
    feature: 'login',
    target: { page: 'p', route: '/login' },
    criteria: [
      { id: 'AC-1', priority: 1, desc: 'd', given: 'g', when: 'w', then: { observable: 'toast', expect_text: 'A' } },
      { id: 'AC-2', priority: 1, desc: 'd', given: 'g', when: 'w', then: { observable: 'toast', expect_text: 'B' } },
      { id: 'AC-3', priority: 1, desc: 'd', given: 'g', when: 'w', then: { observable: 'toast', expect_text: 'C' } },
      { id: 'AC-4', priority: 1, desc: 'd', given: 'g', when: 'w', then: { observable: 'toast', expect_text: 'D' } },
    ],
  };
  const tests = [
    { title: '[AC-1] good', ac_id: 'AC-1', hasAssertion: true, assertionTexts: ['A'] },
    { title: '[AC-2] hollow', ac_id: 'AC-2', hasAssertion: true, assertionTexts: ['wrong'] },
    { title: '[AC-3] notrun', ac_id: 'AC-3', hasAssertion: true, assertionTexts: ['C'] },
    { title: '[AC-9] orphan', ac_id: 'AC-9', hasAssertion: true, assertionTexts: ['Z'] },
  ];
  const results: PlaywrightResult[] = [
    { title: '[AC-1] good', status: 'passed' },
    { title: '[AC-2] hollow', status: 'passed' },
    { title: '[AC-9] orphan', status: 'passed' },
    // '[AC-3] notrun' deliberately absent → CLAIMED_NOT_RUN
  ];

  it('assigns all five verdict types correctly', () => {
    const report = checkCoverage(ac, tests, results);
    const v = (id: string) => report.rows.find((r) => r.ac_id === id)?.verdict;
    expect(v('AC-1')).toBe('COVERED');
    expect(v('AC-2')).toBe('HOLLOW');
    expect(v('AC-3')).toBe('CLAIMED_NOT_RUN');
    expect(v('AC-4')).toBe('MISSING');
    expect(v('AC-9')).toBe('ORPHAN');
  });
  it('fails the run when any verdict is not COVERED', () => {
    expect(checkCoverage(ac, tests, results).passed).toBe(false);
  });
  it('passes only when every AC is COVERED and no orphans', () => {
    const cleanTests = [{ title: '[AC-1] good', ac_id: 'AC-1', hasAssertion: true, assertionTexts: ['A'] }];
    const cleanResults: PlaywrightResult[] = [{ title: '[AC-1] good', status: 'passed' }];
    const cleanAc: AcFile = { ...ac, criteria: [ac.criteria[0]] };
    expect(checkCoverage(cleanAc, cleanTests, cleanResults).passed).toBe(true);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/coverage-checker.test.ts`
Expected: FAIL — `Cannot find module './coverage-checker'`.

- [ ] **Step 3: Implement coverage-checker.ts**

Create `tools/vibe/src/coverage-checker.ts`:

```ts
import { AcFile, CoverageReport, CoverageRow } from './contracts';

// A test extracted statically from a generated spec file.
export interface ExtractedTest {
  title: string;
  ac_id: string | null;
  hasAssertion: boolean;
  assertionTexts: string[];
}

// One result row from Playwright's JSON reporter (normalized).
export interface PlaywrightResult {
  title: string;
  status: 'passed' | 'failed' | 'skipped' | 'timedOut';
}

// Static, deterministic extraction (no AST dep). Splits on `test(` boundaries
// and pulls the title, the [AC-xxx] tag, and any toHaveText/toContainText args.
export function extractTests(specSource: string): ExtractedTest[] {
  const chunks = specSource.split(/\btest\s*\(/).slice(1);
  return chunks.map((chunk) => {
    const titleMatch = chunk.match(/^\s*['"`](.+?)['"`]/);
    const title = titleMatch ? titleMatch[1] : '';
    const acMatch = title.match(/\[(AC-[A-Za-z0-9-]+)\]/);
    const ac_id = acMatch ? acMatch[1] : null;

    const assertionTexts: string[] = [];
    const assertRe = /to(?:Have|Contain)Text\(\s*['"`](.+?)['"`]/g;
    let m: RegExpExecArray | null;
    while ((m = assertRe.exec(chunk)) !== null) assertionTexts.push(m[1]);

    const hasAssertion = /\bexpect\s*\(/.test(chunk);
    return { title, ac_id, hasAssertion, assertionTexts };
  });
}

// The deterministic verdict engine — proves defenses ② (assertion) and ③ (coverage).
// None of this trusts the LLM's self-report; it cross-checks AC ↔ spec ↔ real results.
export function checkCoverage(
  ac: AcFile,
  tests: ExtractedTest[],
  results: PlaywrightResult[],
): CoverageReport {
  const rows: CoverageRow[] = [];
  const resultByTitle = new Map(results.map((r) => [r.title, r]));
  const acIds = new Set(ac.criteria.map((c) => c.id));

  const testsByAc = new Map<string, ExtractedTest[]>();
  for (const t of tests) {
    if (!t.ac_id) continue;
    const arr = testsByAc.get(t.ac_id) ?? [];
    arr.push(t);
    testsByAc.set(t.ac_id, arr);
  }

  // Forward: each AC must trace to an executed, asserting test.
  for (const c of ac.criteria) {
    const matched = testsByAc.get(c.id) ?? [];
    if (matched.length === 0) {
      rows.push({ ac_id: c.id, test_title: null, verdict: 'MISSING', detail: `AC ${c.id} has no test` });
      continue;
    }
    for (const t of matched) {
      const res = resultByTitle.get(t.title);
      if (!res || res.status === 'skipped') {
        rows.push({ ac_id: c.id, test_title: t.title, verdict: 'CLAIMED_NOT_RUN', detail: 'test exists but did not execute' });
        continue;
      }
      const want = c.then.expect_text;
      const assertionMatches = want ? t.assertionTexts.some((a) => a.includes(want)) : t.hasAssertion;
      if (!t.hasAssertion || !assertionMatches) {
        rows.push({ ac_id: c.id, test_title: t.title, verdict: 'HOLLOW', detail: `assertion does not match expect_text='${want ?? ''}'` });
        continue;
      }
      if (res.status !== 'passed') {
        rows.push({ ac_id: c.id, test_title: t.title, verdict: 'HOLLOW', detail: `test ran but status=${res.status}` });
        continue;
      }
      rows.push({ ac_id: c.id, test_title: t.title, verdict: 'COVERED', detail: 'ok' });
    }
  }

  // Reverse: any test claiming an AC id that doesn't exist is an orphan.
  for (const t of tests) {
    if (t.ac_id && !acIds.has(t.ac_id)) {
      rows.push({ ac_id: t.ac_id, test_title: t.title, verdict: 'ORPHAN', detail: 'ac_id not in AC set' });
    }
  }

  const passed = rows.length > 0 && rows.every((r) => r.verdict === 'COVERED');
  return { feature: ac.feature, rows, passed };
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/coverage-checker.test.ts`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/coverage-checker.ts tools/vibe/src/coverage-checker.test.ts
git commit -m "vibe: coverage-checker — deterministic 5-verdict engine (defenses 2+3)"
```

---

### Task 9: Bad Case loop (compound + research)

**Files:**
- Create: `tools/vibe/src/badcase.ts`
- Test: `tools/vibe/src/badcase.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/badcase.test.ts`:

```ts
import { describe, it, expect, afterEach } from 'vitest';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { compound, research } from './badcase';
import { BadCase } from './contracts';

let dir: string | null = null;
function tmpDir(): string {
  dir = path.join(os.tmpdir(), `vibe-bc-${process.pid}-${Math.floor(performance.now())}`);
  return dir;
}
afterEach(() => { if (dir && fs.existsSync(dir)) fs.rmSync(dir, { recursive: true, force: true }); dir = null; });

const bc: BadCase = {
  id: 'BC-20260607-001', feature: 'login', type: 'coverage_gap', ac_id: 'AC-LOGIN-04',
  symptom: 'mismatched password path untested, generator only did happy path',
  root_cause: 'generator skipped isForget=3 branch',
  fix_hint: 'force-cover every AC then-branch including异常 observable',
  created_at: '2026-06-07T00:00:00Z',
};

describe('badcase compound/research', () => {
  it('writes a yaml-frontmatter file and reads it back', () => {
    const d = tmpDir();
    const file = compound(d, bc);
    expect(fs.existsSync(file)).toBe(true);
    expect(fs.readFileSync(file, 'utf-8')).toMatch(/^---\n/);
    const found = research(d, { feature: 'login', keywords: [] });
    expect(found).toHaveLength(1);
    expect(found[0].ac_id).toBe('AC-LOGIN-04');
  });
  it('filters by feature', () => {
    const d = tmpDir();
    compound(d, bc);
    expect(research(d, { feature: 'checkout', keywords: [] })).toHaveLength(0);
  });
  it('matches keywords against symptom/root_cause/ac_id', () => {
    const d = tmpDir();
    compound(d, bc);
    expect(research(d, { feature: 'login', keywords: ['happy path'] })).toHaveLength(1);
    expect(research(d, { feature: 'login', keywords: ['nonexistent-token'] })).toHaveLength(0);
  });
  it('returns [] for a missing directory', () => {
    expect(research(path.join(os.tmpdir(), 'vibe-bc-nope-xyz'), { feature: 'login', keywords: [] })).toEqual([]);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/badcase.test.ts`
Expected: FAIL — `Cannot find module './badcase'`.

- [ ] **Step 3: Implement badcase.ts**

Create `tools/vibe/src/badcase.ts`:

```ts
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { BadCase, BadCaseSchema } from './contracts';

// /learning-compound: sink a validated Bad Case as YAML frontmatter (local store).
export function compound(dir: string, bc: BadCase): string {
  BadCaseSchema.parse(bc);
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${bc.id}.yaml`);
  fs.writeFileSync(file, `---\n${yaml.dump(bc)}---\n`);
  return file;
}

export interface ResearchQuery {
  feature: string;
  keywords: string[];
}

// /learning-researcher: retrieve prior Bad Cases for a feature, optionally keyword-filtered.
export function research(dir: string, q: ResearchQuery): BadCase[] {
  if (!fs.existsSync(dir)) return [];
  const out: BadCase[] = [];
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.yaml'))) {
    const raw = fs.readFileSync(path.join(dir, f), 'utf-8');
    const fm = raw.replace(/^---\n/, '').replace(/\n---\n?$/, '');
    const parsed = BadCaseSchema.safeParse(yaml.load(fm));
    if (!parsed.success) continue;
    const bc = parsed.data;
    if (bc.feature !== q.feature) continue;
    const hay = `${bc.symptom} ${bc.root_cause} ${bc.ac_id ?? ''}`.toLowerCase();
    if (q.keywords.length === 0 || q.keywords.some((k) => hay.includes(k.toLowerCase()))) {
      out.push(bc);
    }
  }
  return out;
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/badcase.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/badcase.ts tools/vibe/src/badcase.test.ts
git commit -m "vibe: Bad Case compound/research (yaml local store)"
```

---

### Task 10: CLI wiring (the spine the agents call)

**Files:**
- Create: `tools/vibe/src/cli.ts`
- Test: `tools/vibe/src/cli.test.ts`

This CLI is the deterministic backbone the OpenCode agents invoke via shell (mirroring hoo-desk's existing `task-management/router.sh`). Commands: `detect`, `init`, `next`, `complete`, `check`.

- [ ] **Step 1: Write the failing test**

Create `tools/vibe/src/cli.test.ts`:

```ts
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
  const file = path.join(acDir, 'login.ac.json');
  fs.writeFileSync(file, JSON.stringify({
    feature: 'login',
    target: { page: 'p', route: '/login' },
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
    fs.writeFileSync(path.join(e2e, 'login.spec.ts'),
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `npx vitest run src/cli.test.ts`
Expected: FAIL — `Cannot find module './cli'`.

- [ ] **Step 3: Implement cli.ts**

Create `tools/vibe/src/cli.ts`:

```ts
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

// Normalize Playwright JSON reporter output to flat {title,status} rows.
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
    const acRaw = JSON.parse(fs.readFileSync(rest[0], 'utf-8'));
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
    tf.tasks[idx] = transition(tf.tasks[idx], to as any);
    saveTaskFile(p(ctx, ...TASK_PATH), tf);
    appendEvent(p(ctx, ...EVENTS_PATH), { ts: ctx.now, type: 'transition', task_id: id, from, to });
    return 0;
  }

  if (cmd === 'check') {
    const [acPath, e2eDir, resultsPath] = rest;
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
```

> Note: `new Date().toISOString()` appears ONLY in the CLI entry shim (the process boundary), never in the deterministic core modules — keeping unit tests reproducible.

- [ ] **Step 4: Run the test to verify it passes**

Run: `npx vitest run src/cli.test.ts`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the full suite + typecheck**

Run:
```bash
npx vitest run
npx tsc --noEmit
```
Expected: all tests PASS, no type errors.

- [ ] **Step 6: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/src/cli.ts tools/vibe/src/cli.test.ts
git commit -m "vibe: CLI spine (detect/init/next/complete/check)"
```

---

### Task 11: OpenCode agents & commands

**Files:**
- Create: `.opencode/agent/test-orchestrator.md`
- Create: `.opencode/agent/test-generator.md`
- Create: `.opencode/agent/test-analyst.md`
- Create: `.opencode/command/vibe-test.md`
- Create: `.opencode/command/learning-compound.md`
- Create: `.opencode/command/learning-researcher.md`

These are LLM-facing config (not unit-tested). They delegate all deterministic decisions to the `vibe` CLI. Note `.opencode/` uses **singular** `agent/` and `command/` (matching the existing `skill/`).

- [ ] **Step 1: Create the orchestrator agent**

Create `.opencode/agent/test-orchestrator.md`:

```markdown
---
description: Vibe test-domain orchestrator. Drives AC → generate → real run → coverage gate using the deterministic vibe CLI. Never decides pass/fail itself.
mode: primary
temperature: 0
permission:
  read: allow
  glob: allow
  grep: allow
  bash:
    "cd */tools/vibe && npx tsx src/cli.ts*": allow
    "npx playwright test*": allow
    "*": ask
  edit: deny
  task:
    "*": deny
    test-generator: allow
    test-analyst: allow
---

You are `test-orchestrator`. You ONLY orchestrate; you never write test code or judge results yourself.

## The deterministic spine
All control decisions come from the `vibe` CLI, never from your own judgment:
- Detect framework / write profile: `cd <ROOT>/tools/vibe && npx tsx src/cli.ts detect` (run with cwd = project root)
- Initialize tasks from AC: `... cli.ts init <abs path to *.ac.json>`
- Ask what to do next: `... cli.ts next`  → prints a task JSON or `DONE`
- Record progress: `... cli.ts complete <task_id> doing|passing|failing`
- Run the coverage gate: `... cli.ts check <ac> <e2e_dir> <pw_results.json>` (exit 0 = pass, 1 = fail)

> The CLI's working directory must be the **project root** (where `.vibe/` lives), not tools/vibe.
> Invoke as: `cd <PROJECT_ROOT> && npx tsx tools/vibe/src/cli.ts <cmd> ...`.

## Fixed flow
1. `detect` (ensures `.vibe/profile.json`).
2. `init` with the target AC file.
3. `next` → if a task is returned, mark it `doing`.
4. Dispatch `test-generator` with the AC file + profile path. It writes specs into the profile's `e2e_out_dir`.
5. Run Playwright for real: `npx playwright test --reporter=json > .vibe/runtime/pw-results.json` (cwd = project root). Capture the JSON even on failure.
6. Run `check`. Read `.vibe/reports/coverage.json`.
7. If `check` exits non-zero: dispatch `test-analyst` to turn each non-COVERED row into a Bad Case, mark the task `failing`, and STOP (report to user). Do not loop more than `max_attempts`.
8. If `check` passes: mark the task `passing`, `next` again until `DONE`, then summarize.

## Hard rules
- Never declare success unless `vibe check` exited 0.
- Never edit generated specs to make them pass.
- A test's own "it passed" claim is irrelevant — only `.vibe/reports/coverage.json` counts.
```

- [ ] **Step 2: Create the generator agent**

Create `.opencode/agent/test-generator.md`:

```markdown
---
description: Turns structured acceptance criteria into real Playwright specs. One test per AC, titled with its [AC-xxx] id, asserting the AC's expected observable.
mode: subagent
temperature: 0.1
permission:
  read: allow
  glob: allow
  grep: allow
  bash:
    "cd */tools/vibe && npx tsx src/cli.ts*": allow
    "*": ask
  edit: allow
  task: deny
---

You are `test-generator`. Input: an AC file (`*.ac.json`) and `.vibe/profile.json`.

## Rules
- Generate ONE Playwright `test(...)` per AC criterion.
- The test title MUST start with the AC id in brackets, e.g. `test('[AC-LOGIN-04] 两次密码不一致提示', ...)`.
- The assertion MUST verify the AC's `then.expect_text` / `then.expect_value`. Use the framework's
  selector conventions from the profile (`ui.toast_selector`, `ui.input_strategy`).
- COVER EVERY AC, including异常/edge paths (e.g. mismatched password, empty field). Do NOT only test the happy path.
- Before checking the AC for prior pitfalls, the orchestrator may have injected Bad Case hints — honor them.
- Write specs into the profile's `e2e_out_dir` (default `e2e/`), one file per feature: `<feature>.spec.ts`.
- Navigate using `profile.dev.base_url` + `target.route`.

## Output envelope (end your message with this JSON)
\`\`\`json
{ "header": { "agent": "test-generator", "stage": "generate", "status": "PASS", "attempt": 0 },
  "payload": { "spec_files": ["e2e/login.spec.ts"], "ac_ids_covered": ["AC-LOGIN-01","AC-LOGIN-04"] },
  "meta": { "warnings": [], "needs_user_input": false } }
\`\`\`

Do NOT claim a test passed — you only generate. Execution and judgment happen downstream.
```

- [ ] **Step 3: Create the analyst agent**

Create `.opencode/agent/test-analyst.md`:

```markdown
---
description: Turns coverage-checker verdicts (MISSING/HOLLOW/CLAIMED_NOT_RUN/ORPHAN) into structured Bad Cases via the learning-compound command.
mode: subagent
temperature: 0.1
permission:
  read: allow
  glob: allow
  grep: allow
  bash:
    "cd */tools/vibe && npx tsx src/cli.ts*": allow
    "*": ask
  edit: deny
  task: deny
---

You are `test-analyst`. Input: `.vibe/reports/coverage.json`.

For each row whose verdict is NOT `COVERED`, produce a Bad Case object and persist it via `/learning-compound`:
- `MISSING` → type `coverage_gap`
- `HOLLOW` → type `hollow_assertion`
- `CLAIMED_NOT_RUN` → type `claimed_not_run`
- `ORPHAN` → type `coverage_gap` (note: spec references an unknown AC)

Each Bad Case must name the `ac_id`, a one-line `symptom`, a `root_cause`, and a concrete `fix_hint`
(what the generator should do differently next time).

End with the standard JSON envelope (agent=`test-analyst`, stage=`analyze`).
```

- [ ] **Step 4: Create the commands**

Create `.opencode/command/vibe-test.md`:

```markdown
---
description: Run the AC-driven three-defense test flow on a feature
agent: test-orchestrator
---

Run the vibe test-domain flow for this acceptance file.

AC file: $ARGUMENTS

Follow the fixed flow in your agent definition. Report the final coverage.json verdicts and, if any
defense failed, the Bad Cases that were recorded.
```

Create `.opencode/command/learning-compound.md`:

```markdown
---
description: Persist a Bad Case to the local learning store (.vibe/badcases)
agent: test-analyst
---

Persist the provided Bad Case(s) to `.vibe/badcases/` as YAML via the vibe badcase API.

Input (verdict rows or a described failure): $ARGUMENTS

For each Bad Case, run this exact one-liner from the project root (fill the JSON fields per the
BadCase schema — id/feature/type/ac_id/symptom/root_cause/fix_hint/created_at):

\`\`\`bash
npx tsx -e "import('./tools/vibe/src/badcase.ts').then(m => m.compound('.vibe/badcases', { id:'BC-<date>-001', feature:'login', type:'coverage_gap', ac_id:'AC-LOGIN-04', symptom:'...', root_cause:'...', fix_hint:'...', created_at:'<iso>' }))"
\`\`\`

`type` must be one of: `coverage_gap` | `hollow_assertion` | `exec_fail` | `claimed_not_run`.
```

Create `.opencode/command/learning-researcher.md`:

```markdown
---
description: Retrieve prior Bad Cases for a feature before generating tests
agent: test-orchestrator
---

Before generating tests, retrieve relevant Bad Cases so the generator avoids past mistakes.

Feature / keywords: $ARGUMENTS

Run this exact one-liner from the project root, then inject the returned `fix_hint`s into the
generator's context:

\`\`\`bash
npx tsx -e "import('./tools/vibe/src/badcase.ts').then(m => console.log(JSON.stringify(m.research('.vibe/badcases', { feature:'login', keywords:[] }), null, 2)))"
\`\`\`
```

- [ ] **Step 5: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add .opencode/agent .opencode/command
git commit -m "vibe: OpenCode agents (orchestrator/generator/analyst) + commands"
```

---

### Task 12: hoo-desk AC fixture + Playwright config + profile

**Files:**
- Create: `.vibe/specs/acceptance/login.ac.json`
- Create: `playwright.config.ts`
- Create: `.vibe/profile.json` (via CLI, then port override)

- [ ] **Step 1: Generate the profile via the detector**

Run (cwd = hoo-desk root):
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
npx tsx tools/vibe/src/cli.ts detect
```
Expected: prints `vue2`, writes `.vibe/profile.json`.

- [ ] **Step 2: Override the dev port for hoo-desk (data, not code)**

Edit `.vibe/profile.json`: change `dev.base_url` from `http://localhost:8080` to `http://localhost:8081` (hoo-desk's dev port per `config/index.js`). This is a per-project value living in data, not in `tools/vibe/src`.

- [ ] **Step 3: Write the AC fixture (covers all three isForget states, incl. exception paths)**

Create `.vibe/specs/acceptance/login.ac.json`:

```json
{
  "feature": "login",
  "target": { "page": "src/views/public/login.vue", "route": "/login" },
  "criteria": [
    { "id": "AC-LOGIN-01", "priority": 1, "desc": "空手机号点击登录提示请输入账号",
      "given": "isForget=1 登录态, 手机号与密码为空", "when": "点击登录按钮",
      "then": { "observable": "toast", "expect_text": "请输入账号" } },
    { "id": "AC-LOGIN-02", "priority": 1, "desc": "有手机号但空密码点击登录提示请输入密码",
      "given": "isForget=1, 手机号已填, 密码为空", "when": "点击登录按钮",
      "then": { "observable": "toast", "expect_text": "请输入密码" } },
    { "id": "AC-LOGIN-03", "priority": 2, "desc": "忘记密码态未填手机号点获取验证码提示",
      "given": "isForget=2 忘记密码态, 手机号为空", "when": "点击获取验证码",
      "then": { "observable": "toast", "expect_text": "请输入手机号后，再获取验证码" } },
    { "id": "AC-LOGIN-04", "priority": 2, "desc": "设置密码态两次密码不一致提示",
      "given": "isForget=3 设置密码态, 两次新密码不同", "when": "点击确定",
      "then": { "observable": "toast", "expect_text": "两次密码输入不一致" } }
  ]
}
```

- [ ] **Step 4: Create Playwright config**

Create `playwright.config.ts` (at hoo-desk root):

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:8081',
    trace: 'on',
    screenshot: 'only-on-failure',
  },
  reporter: [['json', { outputFile: '.vibe/runtime/pw-results.json' }], ['list']],
});
```

- [ ] **Step 5: Install Playwright browsers**

Run (from tools/vibe, where @playwright/test is installed):
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/tools/vibe
npx playwright install chromium
```
Expected: Chromium downloaded.

- [ ] **Step 6: Add .vibe runtime artifacts to gitignore, keep fixtures**

Create `.vibe/.gitignore`:
```
runtime/
reports/
```
(We commit `profile.json`, `specs/`, and `badcases/`; we ignore transient `runtime/` and `reports/`.)

- [ ] **Step 7: Commit**

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add .vibe/profile.json .vibe/specs/acceptance/login.ac.json .vibe/.gitignore playwright.config.ts
git commit -m "vibe: hoo-desk login AC fixture + profile + playwright config"
```

---

### Task 13: End-to-end acceptance + guards

**Files:**
- Create: `tools/vibe/scripts/zero-coupling-guard.sh`
- Create: `e2e/login.spec.ts` (generated — committed as the acceptance artifact)

This task proves the spec's §8 acceptance criteria. Some steps are manual/observational (real LLM + real browser).

- [ ] **Step 1: Add the zero-coupling guard script**

Create `tools/vibe/scripts/zero-coupling-guard.sh`:

```bash
#!/usr/bin/env bash
# Fails if business-specific words leak into the toolchain core (adapters excluded).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HITS=$(grep -rniE 'hoo-desk|isForget|\blogin\b' "$ROOT/src" --include='*.ts' \
  | grep -v '/adapters/' || true)
if [ -n "$HITS" ]; then
  echo "❌ zero-coupling violation: business words found in tools/vibe/src:"
  echo "$HITS"
  exit 1
fi
echo "✅ zero-coupling guard passed"
```

- [ ] **Step 2: Run the guard (expect pass)**

Run:
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/tools/vibe
chmod +x scripts/zero-coupling-guard.sh && ./scripts/zero-coupling-guard.sh
```
Expected: `✅ zero-coupling guard passed`. (If it flags a real hit, rename the offending identifier; do not weaken the grep.)

- [ ] **Step 3: Start hoo-desk dev server**

Run in a separate terminal:
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
npm install   # if not already
npm run dev
```
Expected: server up on `http://localhost:8081`, login reachable at `/login`. Leave it running.

- [ ] **Step 4: Run the full flow via OpenCode**

In OpenCode (cwd = hoo-desk root), run:
```
/vibe-test .vibe/specs/acceptance/login.ac.json
```
Expected: orchestrator runs detect→init→next→generator→`npx playwright test`→check. It produces `e2e/login.spec.ts`, `.vibe/runtime/pw-results.json`, and `.vibe/reports/coverage.json`.

- [ ] **Step 5: Verify the happy outcome OR a real caught defect**

Inspect `.vibe/reports/coverage.json`:
- Ideal: every AC `COVERED`, `passed: true`.
- If the generator missed an exception-path AC (e.g. AC-LOGIN-04), the report shows `MISSING` and `passed: false`, and `test-analyst` wrote a Bad Case. **This is a successful demonstration of defense ③**, not a failure of the toolkit.

Document whichever happened in the commit message.

- [ ] **Step 6: Deliberate-defect demo (defense ③ proof)**

Manually delete the AC-LOGIN-04 test block from `e2e/login.spec.ts`, then re-run only the gate:
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
npx playwright test --reporter=json > .vibe/runtime/pw-results.json || true
npx tsx tools/vibe/src/cli.ts check \
  .vibe/specs/acceptance/login.ac.json e2e .vibe/runtime/pw-results.json; echo "exit=$?"
```
Expected: `exit=1`, and `.vibe/reports/coverage.json` has an `AC-LOGIN-04 → MISSING` row. This proves the checker catches "claimed coverage that isn't there" deterministically.

- [ ] **Step 7: Bad Case round-trip check**

Run:
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
ls .vibe/badcases/    # should contain at least one BC-*.yaml after Step 5/6
npx tsx -e "import('./tools/vibe/src/badcase.ts').then(m => console.log(JSON.stringify(m.research('.vibe/badcases', { feature: 'login', keywords: [] }), null, 2)))"
```
Expected: prints the recorded Bad Case(s) for `login`.

- [ ] **Step 8: Universality check (the通用性 acceptance)**

Add a second AC file for a different page (e.g. `course/creat_class.vue`) WITHOUT touching `tools/vibe/src/**`:

Create `.vibe/specs/acceptance/creat_class.ac.json`:

```json
{
  "feature": "creat_class",
  "target": { "page": "src/views/course/creat_class.vue", "route": "/creat_class" },
  "criteria": [
    { "id": "AC-CLASS-01", "priority": 1, "desc": "必填项为空时提交给出校验提示",
      "given": "表单关键必填项为空", "when": "点击提交",
      "then": { "observable": "toast", "expect_text": "请" } }
  ]
}
```

Run the gate wiring against it (generation may be manual if the route needs auth — the point is the toolchain needs zero code change):
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
npx tsx tools/vibe/src/cli.ts init .vibe/specs/acceptance/creat_class.ac.json
npx tsx tools/vibe/src/cli.ts next   # prints a task referencing AC-CLASS-01
```
Expected: works with no edits under `tools/vibe/src/`. Re-run the guard (Step 2) to confirm still clean.

- [ ] **Step 9: Final full-suite gate + commit**

Run:
```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk/tools/vibe
npx vitest run && npx tsc --noEmit && ./scripts/zero-coupling-guard.sh
```
Expected: all unit tests PASS, no type errors, guard passes.

```bash
cd /Users/ouyangjinfeng/sre-agent/.interview/hoo-desk
git add tools/vibe/scripts/zero-coupling-guard.sh e2e/login.spec.ts .vibe/specs/acceptance/creat_class.ac.json
git add -f .vibe/badcases/ 2>/dev/null || true
git commit -m "vibe: end-to-end acceptance on hoo-desk login + zero-coupling guard + universality check"
```

---

## Acceptance Criteria (Phase 1 done = all checked)

- [ ] L1 unit suite green: contracts, detect (4 enums), profile, state (selectNext 3 cases + transitions), events, adapters (vue2 + skeleton throws), coverage-checker (5 verdicts), badcase round-trip, cli.
- [ ] `npx tsc --noEmit` clean.
- [ ] Framework detector identifies hoo-desk as `vue2` and the 4 sample versions correctly.
- [ ] Handwritten `login.ac.json` covers isForget 1/2/3 with ≥2 exception-path ACs.
- [ ] End-to-end run produces real `trace` + `pw-results.json` + `coverage.json`.
- [ ] `coverage.json` deterministically catches at least one of MISSING / HOLLOW / CLAIMED_NOT_RUN (Step 6 forces MISSING).
- [ ] Caught defect persisted as `badcases/*.yaml`; `research` retrieves it.
- [ ] Universality: a second page's AC works with zero edits under `tools/vibe/src/`.
- [ ] Zero-coupling guard passes (no `hoo-desk`/`login`/`isForget` outside adapters).
- [ ] hoo-desk business source and build config unchanged.
```
