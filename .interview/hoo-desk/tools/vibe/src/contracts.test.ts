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
      feature: 'checkout', target: { page: 'p', route: '/checkout' }, criteria: [],
    });
    expect(bad.success).toBe(false);
  });
  it('accepts a well-formed AC', () => {
    const ok = AcFileSchema.safeParse({
      feature: 'checkout',
      target: { page: 'src/views/shop/checkout.vue', route: '/checkout' },
      criteria: [{
        id: 'AC-CHECKOUT-01', priority: 1, desc: 'd', given: 'g', when: 'w',
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
      id: 'BC-1', feature: 'checkout', type: 'coverage_gap',
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
