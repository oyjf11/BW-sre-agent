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
