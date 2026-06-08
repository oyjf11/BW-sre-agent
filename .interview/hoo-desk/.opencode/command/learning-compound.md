---
description: Persist a Bad Case to the local learning store (.vibe/badcases)
agent: test-analyst
---

Persist the provided Bad Case(s) to `.vibe/badcases/` as YAML via the vibe badcase API.

Input (verdict rows or a described failure): $ARGUMENTS

For each Bad Case, run this exact one-liner from the project root (fill the JSON fields per the
BadCase schema — id/feature/type/ac_id/symptom/root_cause/fix_hint/created_at):

```bash
npx tsx -e "import('./tools/vibe/src/badcase.ts').then(m => m.compound('.vibe/badcases', { id:'BC-<date>-001', feature:'login', type:'coverage_gap', ac_id:'AC-LOGIN-04', symptom:'...', root_cause:'...', fix_hint:'...', created_at:'<iso>' }))"
```

`type` must be one of: `coverage_gap` | `hollow_assertion` | `exec_fail` | `claimed_not_run`.
