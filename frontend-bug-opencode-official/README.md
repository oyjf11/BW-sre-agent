# frontend-bug-opencode-official

This package uses the official OpenCode Markdown agent layout: `.opencode/agents/*.md`.

## Install

```bash
cp -R .opencode opencode.json /path/to/your/repo/
```

## Verify

```bash
opencode agent list
opencode --agent frontend-bug-orchestrator
```

## Usage

```text
/frontend-bug <bug description>
```

Notes:
- `.opencode/contracts/` is a custom reference document, not a native OpenCode contract runtime.
- The root-cause agent name intentionally keeps the original spelling: `frontend-bug-rootcasuse`.
