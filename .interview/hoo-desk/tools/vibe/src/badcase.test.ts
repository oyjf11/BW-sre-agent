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
  id: 'BC-20260607-001', feature: 'checkout', type: 'coverage_gap', ac_id: 'AC-CHECKOUT-04',
  symptom: 'coupon error path untested, generator only did happy path',
  root_cause: 'generator skipped isCoupon=3 branch',
  fix_hint: 'force-cover every AC then-branch including异常 observable',
  created_at: '2026-06-07T00:00:00Z',
};

describe('badcase compound/research', () => {
  it('writes a yaml-frontmatter file and reads it back', () => {
    const d = tmpDir();
    const file = compound(d, bc);
    expect(fs.existsSync(file)).toBe(true);
    expect(fs.readFileSync(file, 'utf-8')).toMatch(/^---\n/);
    const found = research(d, { feature: 'checkout', keywords: [] });
    expect(found).toHaveLength(1);
    expect(found[0].ac_id).toBe('AC-CHECKOUT-04');
  });
  it('filters by feature', () => {
    const d = tmpDir();
    compound(d, bc);
    expect(research(d, { feature: 'other-feature', keywords: [] })).toHaveLength(0);
  });
  it('matches keywords against symptom/root_cause/ac_id', () => {
    const d = tmpDir();
    compound(d, bc);
    expect(research(d, { feature: 'checkout', keywords: ['happy path'] })).toHaveLength(1);
    expect(research(d, { feature: 'checkout', keywords: ['nonexistent-token'] })).toHaveLength(0);
  });
  it('returns [] for a missing directory', () => {
    expect(research(path.join(os.tmpdir(), 'vibe-bc-nope-xyz'), { feature: 'checkout', keywords: [] })).toEqual([]);
  });
});
