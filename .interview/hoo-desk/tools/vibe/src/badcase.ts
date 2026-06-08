import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import { BadCase, BadCaseSchema } from './contracts';

export function compound(dir: string, bc: BadCase): string {
  const safe = BadCaseSchema.parse(bc);
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${safe.id}.yaml`);
  fs.writeFileSync(file, `---\n${yaml.dump(safe)}---\n`);
  return file;
}

export interface ResearchQuery {
  feature: string;
  keywords: string[];
}

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
