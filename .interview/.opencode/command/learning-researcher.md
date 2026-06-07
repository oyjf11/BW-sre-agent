---
description: Retrieve prior Bad Cases for a feature before generating tests
agent: test-orchestrator
---

Before generating tests, retrieve relevant Bad Cases so the generator avoids past mistakes.

Feature / keywords: $ARGUMENTS

Run this exact one-liner from the project root, then inject the returned `fix_hint`s into the
generator's context:

```bash
npx tsx -e "import('./tools/vibe/src/badcase.ts').then(m => console.log(JSON.stringify(m.research('.vibe/badcases', { feature:'login', keywords:[] }), null, 2)))"
```
