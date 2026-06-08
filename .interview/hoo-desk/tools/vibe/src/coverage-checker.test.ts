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
    feature: 'checkout',
    target: { page: 'p', route: '/checkout' },
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
