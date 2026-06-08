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
export type AcThen = z.infer<typeof AcThenSchema>;
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
