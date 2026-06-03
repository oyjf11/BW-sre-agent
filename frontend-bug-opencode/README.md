# frontend-bug-opencode

Controlled multi-agent frontend bug repair workflow for OpenCode.

## Install
Copy these files into your repository root:

```bash
cp -R .opencode opencode.json /path/to/your/repo/
```

Then open OpenCode in that repo. The default primary agent is `frontend-bug-orchestrator`.

## Usage

```text
/frontend-bug 登录页点击提交后按钮一直 loading，预期失败后恢复按钮可点击，实际一直禁用
```

Or manually select/switch to `frontend-bug-orchestrator` and describe the bug.

## Agents
- `frontend-bug-orchestrator`: primary orchestrator, task-only dispatch.
- `frontend-bug-reproducer`: hidden read/test reproduction specialist.
- `frontend-bug-rootcasuse`: hidden root cause specialist. Name intentionally matches the user-provided spelling.
- `frontend-bug-fixer`: hidden minimal fix specialist, edit/write ask-only.
- `frontend-bug-reviewer`: hidden read-only reviewer.

## Notes
- The workflow assumes Superpowers skills are installed.
- Hidden agents are not shown in autocomplete, but can still be invoked by the orchestrator through Task permissions.
- Bash command filtering follows OpenCode glob-style permission matching. Put `*` first and specific allow rules after it.
