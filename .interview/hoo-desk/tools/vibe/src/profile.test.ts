import { describe, it, expect } from 'vitest';
import { buildProfile } from './profile';
import { ProfileSchema } from './contracts';

describe('buildProfile', () => {
  it('produces a schema-valid vue2 profile with element-ui defaults', () => {
    const p = buildProfile('vue2', 'my-project');
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
