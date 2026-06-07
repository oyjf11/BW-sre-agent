# Frontend Bug Agent Contract

## Fixed todo list
- reproduce
- root-cause
- minimal-fix
- verify
- review

Allowed todo states: `pending`, `in_progress`, `done`, `blocked`, `skipped`.

## State machine
Forward path: `intake -> reproduce -> root_cause -> minimal_fix -> verify -> review -> done`.

Allowed fallback paths:
- `reproduce -> blocked`
- `root_cause -> reproduce`
- `minimal_fix -> root_cause`
- `verify -> minimal_fix`
- `review -> minimal_fix`

Forbidden jumps:
- `reproduce -> minimal_fix`
- `reproduce -> review`
- `root_cause -> verify`
- `root_cause(low confidence) -> minimal_fix`
- `verify=fail -> done`

Only one active stage is allowed at a time.

## Universal response envelope
Every subagent final response must end with a standalone JSON object or fenced JSON block:

```json
{
  "header": {
    "agent": "frontend-bug-reproducer",
    "stage": "reproduce",
    "status": "PASS | FAIL | PARTIAL",
    "retry_count": 0,
    "timestamp": "ISO 8601"
  },
  "ref": {
    "upstream_stage": "intake",
    "upstream_status": "PASS"
  },
  "payload": {},
  "meta": {
    "warnings": [],
    "assumptions": [],
    "needs_user_input": false
  }
}
```

Valid statuses: `PASS`, `FAIL`, `PARTIAL` only.

## Reproduce payload
```json
{
  "repro_steps": {"command": "...", "description": "..."},
  "output": {"actual": "...", "expected": "...", "diff": "..."},
  "env": {"node": "...", "browser": "...", "os": "..."},
  "code_locations": [{"file": "src/xxx.ts", "line": 42, "relevance": "..."}]
}
```
Required: `repro_steps.command`, `output.actual`, `output.expected`, non-empty `code_locations`.

## Root cause payload
```json
{
  "root_cause": {"summary": "问题根因是 X，因为 Y", "confidence": "high | medium | low"},
  "evidence_chain": [
    {"node": "复现输出", "file": "test/xxx.test.ts", "line": 15, "finding": "..."},
    {"node": "根因", "file": "src/yyy.ts", "line": 88, "finding": "..."}
  ],
  "impact_scope": {"modules": [], "components": [], "apis": []},
  "pending_hypotheses": []
}
```
Required: summary contains `根因` or `root cause`; confidence in `high|medium|low`; evidence_chain length >= 2; every evidence has file + line + finding. If confidence is low, `pending_hypotheses` must be non-empty.

## Fix confirmation request payload
Before editing, fixer must return this and stop:

```json
{
  "type": "fix_confirmation_request",
  "planned_changes": [
    {"file": "src/xxx.ts", "lines": "40-45", "reason": "...", "change_type": "modify"}
  ],
  "impact_summary": "..."
}
```

The orchestrator must approve/deny:

```json
{
  "type": "fix_confirmation_response",
  "decision": "approved | denied",
  "reason": "...",
  "allowed_files": ["src/xxx.ts"]
}
```

## Minimal fix completion payload
```json
{
  "changes": [
    {"file": "src/xxx.ts", "lines": "40-44", "description": "...", "type": "modify"}
  ],
  "verification": {
    "lint": {"status": "PASS", "output": "..."},
    "typecheck": {"status": "PASS", "output": "..."},
    "tests_added": [{"file": "src/xxx.test.ts", "test_name": "...", "result": "PASS"}],
    "tests_existing": "..."
  },
  "self_risk_assessment": "..."
}
```
Required: changes within approved files; lint PASS; typecheck PASS; at least one added/modified regression test.

## Review payload
```json
{
  "verdict": "approved | conditional_approved | rejected",
  "checklist": {
    "root_cause_addressed": {"result": true, "detail": "..."},
    "no_regression": {"result": true, "detail": "..."},
    "no_scope_creep": {"result": true, "detail": "..."},
    "code_quality": {"result": true, "detail": "..."},
    "test_coverage": {"result": true, "detail": "..."}
  },
  "must_fix": [],
  "suggestions": [],
  "acceptable_risks": []
}
```
If `rejected`, `must_fix` must be non-empty. If `conditional_approved`, both `must_fix` and `suggestions` must be non-empty.
