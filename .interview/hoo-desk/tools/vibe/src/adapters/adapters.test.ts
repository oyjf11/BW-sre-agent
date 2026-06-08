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
