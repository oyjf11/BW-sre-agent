import { AcFile, CoverageReport, CoverageRow } from './contracts';

export interface ExtractedTest {
  title: string;
  ac_id: string | null;
  hasAssertion: boolean;
  assertionTexts: string[];
}

export interface PlaywrightResult {
  title: string;
  status: 'passed' | 'failed' | 'skipped' | 'timedOut';
}

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

  for (const t of tests) {
    if (t.ac_id && !acIds.has(t.ac_id)) {
      rows.push({ ac_id: t.ac_id, test_title: t.title, verdict: 'ORPHAN', detail: 'ac_id not in AC set' });
    }
  }

  const passed = rows.length > 0 && rows.every((r) => r.verdict === 'COVERED');
  return { feature: ac.feature, rows, passed };
}
