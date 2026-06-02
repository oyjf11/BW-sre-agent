# OpsPilot Incident Reliability Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make OpsPilot stop honestly when evidence or automation capability is insufficient, persist the reason, avoid doomed approvals, and render the actual halt stage in the run-detail UI.

**Architecture:** Keep the existing LangGraph node set and introduce a reliability layer around it: structured evidence collection outcomes, a terminal `NEEDS_HUMAN` state, read-only capability preflight, durable sanitized tool audits, and downgraded RCA output. Persist terminal metadata on `incident_runs`, keep detailed collection outcomes in checkpoints, expose both through additive API fields, and map backend nodes to ten explicit frontend display stages.

**Tech Stack:** Python 3, FastAPI, LangGraph, Pydantic v2, SQLAlchemy, Alembic, SQLite, React 19, TypeScript, Vitest, Testing Library, Tailwind CSS v4.

---

## Workspace Safety

The current worktree contains user edits in files this plan will touch. Before implementation, inspect:

```bash
git status --short
git diff -- backend/app frontend/src
```

Preserve existing edits. Do not reset, checkout, stash, or overwrite them. In particular, build on the uncommitted realtime refresh work in:

- `backend/app/services/event_bus.py`
- `backend/app/services/graph_runner.py`
- `frontend/src/pages/RunDetailPage.tsx`
- `frontend/src/services/runDetailSync.ts`
- `frontend/src/components/EvidencePanel.tsx`
- `frontend/src/i18n/en.json`
- `frontend/src/i18n/zh-CN.json`

Reference design:

```text
docs/superpowers/specs/2026-06-02-incident-reliability-closure-design.md
```

Reference production-like sample:

```text
878ae18a-25c0-49ed-9f96-7f16150ddf64
```

## File Structure

### Backend Contracts And Persistence

- Create: `backend/alembic/versions/007_incident_reliability_fields.py`
  - Add halt metadata and downgraded RCA columns.
- Create: `backend/app/models/evidence_collection.py`
  - Define structured collection statuses and results.
- Modify: `backend/app/models/action.py`
  - Require automatic actions to carry supporting evidence IDs.
- Modify: `backend/app/models/rca.py`
  - Add certainty, candidate, automation outcome, and manual next-step fields.
- Modify: `backend/app/models/db_models.py`
  - Add `NEEDS_HUMAN` and ORM columns.
- Modify: `backend/app/models/__init__.py`
  - Export the new collection models.
- Modify: `backend/app/graph/state.py`
  - Add workflow state fields.
- Modify: `backend/app/graph/serde.py`
  - Deserialize collection results after checkpoint restore.
- Modify: `backend/app/repositories/__init__.py`
  - Add legacy SQLite fallback patches and export tool audits.
- Modify: `backend/app/repositories/rca_repo.py`
  - Persist extended RCA fields.
- Create: `backend/app/repositories/tool_audits_repo.py`
  - Persist sanitized tool invocation records.

### Backend Reliability Logic

- Create: `backend/app/graph/evidence_quality.py`
  - Centralize payload usability, failure classification, and aggregate helpers.
- Modify: `backend/app/tools/gateway.py`
  - Add read-only capability descriptions and durable sanitized auditing on every path.
- Modify: `backend/app/graph/nodes/__init__.py`
  - Record evidence outcomes, stop on exhausted evidence, gate remediation by evidence, preflight capability, and downgrade RCA.
- Modify: `backend/app/graph/builder.py`
  - Route `NEEDS_HUMAN` directly to RCA.
- Modify: `backend/app/services/approval_runtime.py`
  - Resume from the pause checkpoint without regressing state.
- Modify: `backend/app/services/event_bus.py`
  - Add `RUN_PAUSED`.
- Modify: `backend/app/services/graph_runner.py`
  - Separate pause from terminal completion and persist halt metadata.
- Modify: `backend/app/i18n/__init__.py`
  - Translate pause and human-handoff lifecycle events.

### Backend API

- Modify: `backend/app/api/incidents.py`
  - Return halt metadata, expose collection outcomes, and return extended RCA fields.

### Frontend

- Modify: `frontend/src/index.css`
  - Load Tailwind v4 compatibility config so custom stepper utilities are generated.
- Modify: `frontend/src/types/index.ts`
  - Add terminal reason, collection result, action support, and RCA fields.
- Modify: `frontend/src/services/runs.ts`
  - Fetch collection outcomes.
- Modify: `frontend/src/services/runDetailSync.ts`
  - Treat `NEEDS_HUMAN` as terminal.
- Modify: `frontend/src/components/RunStepper.tsx`
  - Render ten mapped display stages and halt markers.
- Create: `frontend/src/components/EvidenceCollectionStatusPanel.tsx`
  - Render usable, empty, configuration-failed, and runtime-failed collection attempts.
- Modify: `frontend/src/pages/RunDetailPage.tsx`
  - Display terminal reason and collection outcomes.
- Modify: `frontend/src/pages/RcaPage.tsx`
  - Display downgraded RCA fields.
- Modify: `frontend/src/i18n/en.json`
  - Add English labels.
- Modify: `frontend/src/i18n/zh-CN.json`
  - Add Chinese labels.

### Tests

- Modify: `backend/app/tests/test_models.py`
- Modify: `backend/app/tests/test_repositories.py`
- Create: `backend/app/tests/test_evidence_quality.py`
- Modify: `backend/app/tests/test_tool_gateway.py`
- Modify: `backend/app/tests/test_resume_and_evidence.py`
- Modify: `backend/app/tests/test_graph_integration.py`
- Modify: `backend/app/tests/test_incidents_api.py`
- Modify: `frontend/src/components/RunStepper.test.tsx`
- Create: `frontend/src/components/EvidenceCollectionStatusPanel.test.tsx`
- Modify: `frontend/src/services/runs.test.ts`
- Modify: `frontend/src/services/runDetailSync.test.ts`
- Modify: `frontend/src/pages/RunDetailPage.test.tsx`
- Create: `frontend/src/pages/RcaPage.test.tsx`

---

### Task 1: Add Reliability Domain Contracts And Database Columns

**Files:**
- Create: `backend/alembic/versions/007_incident_reliability_fields.py`
- Create: `backend/app/models/evidence_collection.py`
- Modify: `backend/app/models/action.py`
- Modify: `backend/app/models/rca.py`
- Modify: `backend/app/models/db_models.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/graph/state.py`
- Modify: `backend/app/graph/serde.py`
- Modify: `backend/app/repositories/__init__.py`
- Modify: `backend/app/tests/test_models.py`
- Modify: `backend/app/tests/test_repositories.py`

- [ ] **Step 1: Write failing model and legacy-schema tests**

Append to `backend/app/tests/test_models.py`:

```python
from app.models import EvidenceCollectionResult, EvidenceCollectionStatus


class TestEvidenceCollectionResult:
    def test_create_empty_result(self):
        result = EvidenceCollectionResult(
            tool_name="query_metrics",
            category="metrics",
            params={"service": "api", "env": "prod"},
            status=EvidenceCollectionStatus.SUCCESS_EMPTY,
            latency_ms=12,
        )

        assert result.status == EvidenceCollectionStatus.SUCCESS_EMPTY
        assert result.evidence_id is None


def test_action_spec_defaults_supporting_evidence_ids_to_empty_list():
    action = ActionSpec(
        action_type="restart",
        service="api",
        env="prod",
        params={},
        risk_level="LOW",
    )

    assert action.supporting_evidence_ids == []


def test_rca_report_accepts_downgrade_fields():
    report = RcaReport(
        run_id="run-1",
        report_markdown="# RCA",
        root_cause="尚未确认",
        resolution="需要人工接管",
        root_cause_status="UNKNOWN",
        candidate_hypotheses=[{"hypothesis": "配置异常", "confidence": 0.4}],
        automation_outcome={"status": "NEEDS_HUMAN"},
        manual_next_steps=["检查生产配置"],
    )

    assert report.root_cause_status == "UNKNOWN"
    assert report.manual_next_steps == ["检查生产配置"]
```

Extend `test_ensure_sqlite_schema_upgrades_legacy_tables` in
`backend/app/tests/test_repositories.py`:

```python
        assert {
            "halted_at_node",
            "terminal_reason_json",
        }.issubset(run_columns)
        assert {
            "root_cause_status",
            "candidate_hypotheses_json",
            "automation_outcome_json",
            "manual_next_steps_json",
        }.issubset(rca_columns)
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_models.py app/tests/test_repositories.py -q
```

Expected: FAIL because the collection model, action support field, RCA fields, and SQLite fallback columns do not exist.

- [ ] **Step 3: Add the collection result model**

Create `backend/app/models/evidence_collection.py`:

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EvidenceCollectionStatus(str, Enum):
    SUCCESS_USABLE = "SUCCESS_USABLE"
    SUCCESS_EMPTY = "SUCCESS_EMPTY"
    FAILED_CONFIG = "FAILED_CONFIG"
    FAILED_RUNTIME = "FAILED_RUNTIME"


class EvidenceCollectionResult(BaseModel):
    tool_name: str
    category: str
    params: Dict[str, Any] = Field(default_factory=dict)
    status: EvidenceCollectionStatus
    evidence_id: Optional[str] = None
    error: Optional[str] = None
    latency_ms: int = 0
    collected_at: datetime = Field(default_factory=datetime.utcnow)
```

Export `EvidenceCollectionResult` and `EvidenceCollectionStatus` from
`backend/app/models/__init__.py`.

- [ ] **Step 4: Extend workflow and domain models**

Add to `ActionSpec` in `backend/app/models/action.py`:

```python
    supporting_evidence_ids: List[str] = Field(
        default_factory=list,
        description="Usable evidence IDs supporting automated execution",
    )
```

Update imports and add to `RcaReport` in `backend/app/models/rca.py`:

```python
from typing import Any, Dict, List, Optional

    root_cause_status: str = Field(
        default="UNKNOWN",
        description="Root-cause certainty: CONFIRMED, SUSPECTED, or UNKNOWN",
    )
    candidate_hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    automation_outcome: Optional[Dict[str, Any]] = None
    manual_next_steps: List[str] = Field(default_factory=list)
```

Add `NEEDS_HUMAN = "NEEDS_HUMAN"` to both `RunStatus` in
`backend/app/graph/state.py` and `RunStatusEnum` in
`backend/app/models/db_models.py`.

Add to `IncidentAgentState`:

```python
    evidence_collection_results: List[EvidenceCollectionResult]
    failed_evidence_tools: List[str]
    terminal_reason: Optional[Dict[str, Any]]
    halted_at_node: Optional[str]
```

Import `EvidenceCollectionResult` in `backend/app/graph/state.py` and
`backend/app/graph/serde.py`, then add to `_LIST_MODEL_FIELDS`:

```python
    "evidence_collection_results": EvidenceCollectionResult,
```

- [ ] **Step 5: Add ORM columns and migration**

Add to `IncidentRun` in `backend/app/models/db_models.py`:

```python
    halted_at_node = Column(String, nullable=True)
    terminal_reason_json = Column(JSON, nullable=True)
```

Add to `IncidentRcaReport`:

```python
    root_cause_status = Column(String, nullable=True)
    candidate_hypotheses_json = Column(JSON, nullable=True)
    automation_outcome_json = Column(JSON, nullable=True)
    manual_next_steps_json = Column(JSON, nullable=True)
```

Create `backend/alembic/versions/007_incident_reliability_fields.py`:

```python
"""Add incident reliability closure fields.

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incident_runs") as batch_op:
        batch_op.add_column(sa.Column("halted_at_node", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("terminal_reason_json", sa.JSON(), nullable=True))

    with op.batch_alter_table("incident_rca_reports") as batch_op:
        batch_op.add_column(sa.Column("root_cause_status", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("candidate_hypotheses_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("automation_outcome_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("manual_next_steps_json", sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table("incident_rca_reports") as batch_op:
        batch_op.drop_column("manual_next_steps_json")
        batch_op.drop_column("automation_outcome_json")
        batch_op.drop_column("candidate_hypotheses_json")
        batch_op.drop_column("root_cause_status")

    with op.batch_alter_table("incident_runs") as batch_op:
        batch_op.drop_column("terminal_reason_json")
        batch_op.drop_column("halted_at_node")
```

Add to the `incident_runs` legacy patches in `backend/app/repositories/__init__.py`:

```python
        ("halted_at_node", "ALTER TABLE incident_runs ADD COLUMN halted_at_node VARCHAR"),
        (
            "terminal_reason_json",
            "ALTER TABLE incident_runs ADD COLUMN terminal_reason_json JSON",
        ),
```

Add to the `incident_rca_reports` patches:

```python
        (
            "root_cause_status",
            "ALTER TABLE incident_rca_reports ADD COLUMN root_cause_status VARCHAR",
        ),
        (
            "candidate_hypotheses_json",
            "ALTER TABLE incident_rca_reports ADD COLUMN candidate_hypotheses_json JSON",
        ),
        (
            "automation_outcome_json",
            "ALTER TABLE incident_rca_reports ADD COLUMN automation_outcome_json JSON",
        ),
        (
            "manual_next_steps_json",
            "ALTER TABLE incident_rca_reports ADD COLUMN manual_next_steps_json JSON",
        ),
```

- [ ] **Step 6: Run migration and focused tests**

Run:

```bash
cd backend && source venv/bin/activate
alembic upgrade head
python -m pytest app/tests/test_models.py app/tests/test_repositories.py -q
```

Expected: Alembic upgrades to `007`; focused tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/alembic/versions/007_incident_reliability_fields.py \
  backend/app/models/evidence_collection.py \
  backend/app/models/action.py backend/app/models/rca.py \
  backend/app/models/db_models.py backend/app/models/__init__.py \
  backend/app/graph/state.py backend/app/graph/serde.py \
  backend/app/repositories/__init__.py \
  backend/app/tests/test_models.py backend/app/tests/test_repositories.py
git commit -m "backend: add reliability closure contracts"
```

---

### Task 2: Centralize Evidence Usability And Quality Rules

**Files:**
- Create: `backend/app/graph/evidence_quality.py`
- Create: `backend/app/tests/test_evidence_quality.py`

- [ ] **Step 1: Write failing evidence-quality tests**

Create `backend/app/tests/test_evidence_quality.py`:

```python
from app.graph.evidence_quality import (
    classify_collection_result,
    compute_evidence_quality,
)
from app.models.evidence import EvidenceItem
from app.models.evidence_collection import EvidenceCollectionStatus
from app.tools.schemas import ToolResponse


def response(tool_name, result=None, error=None):
    return ToolResponse(
        tool_name=tool_name,
        success=error is None,
        result=result,
        error=error,
        latency_ms=5,
    )


def test_empty_logs_are_not_usable():
    outcome = classify_collection_result(
        "query_logs", "logs", {"service": "api"}, response("query_logs", {"logs": []})
    )

    assert outcome.status == EvidenceCollectionStatus.SUCCESS_EMPTY


def test_metrics_need_at_least_one_value():
    outcome = classify_collection_result(
        "query_metrics",
        "metrics",
        {"service": "api"},
        response("query_metrics", {"metrics": {"cpu_usage": {"values": []}}}),
    )

    assert outcome.status == EvidenceCollectionStatus.SUCCESS_EMPTY


def test_adapter_configuration_error_is_preserved():
    outcome = classify_collection_result(
        "query_runbook",
        "runbook",
        {"service": "api"},
        response("query_runbook", error="Real adapter 'query_runbook' is not configured"),
    )

    assert outcome.status == EvidenceCollectionStatus.FAILED_CONFIG
    assert "not configured" in outcome.error


def test_runtime_error_is_preserved():
    outcome = classify_collection_result(
        "query_db_processlist",
        "db",
        {},
        response("query_db_processlist", error="Lost connection to MySQL server"),
    )

    assert outcome.status == EvidenceCollectionStatus.FAILED_RUNTIME


def test_repeated_empty_metrics_do_not_raise_quality():
    empty = classify_collection_result(
        "query_metrics",
        "metrics",
        {"service": "api"},
        response("query_metrics", {"metrics": {"cpu_usage": {"values": []}}}),
    )

    score, missing, failed = compute_evidence_quality([], [empty, empty])

    assert score == 0.0
    assert missing == ["deployments", "logs", "metrics", "runbook"]
    assert failed == []


def test_usable_logs_raise_quality():
    item = EvidenceItem(
        evidence_id="ev-1",
        tool_name="query_logs",
        category="logs",
        source_ref="logs-run-1",
        summary="Retrieved logs",
        confidence=0.8,
    )
    usable = classify_collection_result(
        "query_logs",
        "logs",
        {"service": "api"},
        response("query_logs", {"logs": [{"message": "500"}]}),
        evidence_id="ev-1",
    )

    score, missing, failed = compute_evidence_quality([item], [usable])

    assert score == 0.47
    assert missing == ["deployments", "metrics", "runbook"]
    assert failed == []
```

- [ ] **Step 2: Run the focused test and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_evidence_quality.py -q
```

Expected: FAIL because `app.graph.evidence_quality` does not exist.

- [ ] **Step 3: Implement the reliability helper**

Create `backend/app/graph/evidence_quality.py`:

```python
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.models.evidence import EvidenceItem
from app.models.evidence_collection import (
    EvidenceCollectionResult,
    EvidenceCollectionStatus,
)
from app.tools.schemas import ToolResponse

EXPECTED_CATEGORIES = {"logs", "metrics", "deployments", "runbook"}
CONFIG_ERROR_MARKERS = (
    "not configured",
    "missing configuration",
    "invalid kube-config",
    "kubeconfig",
    "credential",
    "api key",
    "access key",
)
LIST_FIELDS = {
    "query_logs": ("logs",),
    "query_deployments": ("deployments",),
    "query_runbook": ("runbooks",),
    "query_k8s_pods": ("pods",),
    "query_k8s_events": ("events",),
    "query_k8s_pod_logs_summary": ("sample_logs", "patterns"),
    "query_db_processlist": ("processlist",),
    "query_db_slow_queries": ("slow_queries",),
    "query_db_table_status": ("table_status",),
}


def _has_non_empty_list(payload: Dict[str, Any], fields: Iterable[str]) -> bool:
    return any(isinstance(payload.get(field), list) and bool(payload[field]) for field in fields)


def payload_is_usable(tool_name: str, payload: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(payload, dict):
        return False
    if tool_name == "query_metrics":
        metrics = payload.get("metrics")
        return isinstance(metrics, dict) and any(
            isinstance(metric, dict) and bool(metric.get("values"))
            for metric in metrics.values()
        )
    if tool_name == "query_db_variables":
        return bool(payload.get("variables"))
    if tool_name == "query_k8s_deployment_status":
        return payload.get("status") not in (None, "", "unknown", "unavailable")
    if tool_name == "query_lb_health_status":
        return payload.get("status") not in (None, "", "unknown", "unavailable")
    if tool_name == "query_lb_traffic_metrics":
        return payload.get("metrics_available") is not False and "qps" in payload
    fields = LIST_FIELDS.get(tool_name)
    if fields:
        return _has_non_empty_list(payload, fields)
    return bool({key: value for key, value in payload.items() if key != "_adapter_info"})


def classify_failure(error: Optional[str]) -> EvidenceCollectionStatus:
    normalized = (error or "").lower()
    if any(marker in normalized for marker in CONFIG_ERROR_MARKERS):
        return EvidenceCollectionStatus.FAILED_CONFIG
    return EvidenceCollectionStatus.FAILED_RUNTIME


def classify_collection_result(
    tool_name: str,
    category: str,
    params: Dict[str, Any],
    response: ToolResponse,
    evidence_id: Optional[str] = None,
) -> EvidenceCollectionResult:
    if not response.success:
        status = classify_failure(response.error)
    elif payload_is_usable(tool_name, response.result):
        status = EvidenceCollectionStatus.SUCCESS_USABLE
    else:
        status = EvidenceCollectionStatus.SUCCESS_EMPTY
    return EvidenceCollectionResult(
        tool_name=tool_name,
        category=category,
        params=params,
        status=status,
        evidence_id=evidence_id if status == EvidenceCollectionStatus.SUCCESS_USABLE else None,
        error=response.error,
        latency_ms=response.latency_ms,
    )


def usable_evidence_ids(results: Iterable[EvidenceCollectionResult]) -> List[str]:
    return sorted(
        {
            item.evidence_id
            for item in results
            if item.status == EvidenceCollectionStatus.SUCCESS_USABLE and item.evidence_id
        }
    )


def compute_evidence_quality(
    evidence_items: Iterable[EvidenceItem],
    results: Iterable[EvidenceCollectionResult],
) -> Tuple[float, List[str], List[str]]:
    usable_ids = set(usable_evidence_ids(results))
    usable_items = [
        item
        for item in evidence_items
        if (item.evidence_id if hasattr(item, "evidence_id") else item.get("evidence_id"))
        in usable_ids
    ]
    categories = {
        item.category if hasattr(item, "category") else item.get("category", "unknown")
        for item in usable_items
    }
    confidence = sum(
        item.confidence if hasattr(item, "confidence") else item.get("confidence", 0.5)
        for item in usable_items
    )
    coverage = len(categories & EXPECTED_CATEGORIES) / len(EXPECTED_CATEGORIES)
    average = confidence / len(usable_items) if usable_items else 0.0
    score = round(coverage * 0.6 + average * 0.4, 2)
    failed = sorted(
        {
            item.tool_name
            for item in results
            if item.status
            in (EvidenceCollectionStatus.FAILED_CONFIG, EvidenceCollectionStatus.FAILED_RUNTIME)
        }
    )
    return score, sorted(EXPECTED_CATEGORIES - categories), failed
```

- [ ] **Step 4: Run the focused test**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_evidence_quality.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/graph/evidence_quality.py backend/app/tests/test_evidence_quality.py
git commit -m "backend: classify usable evidence outcomes"
```

---

### Task 3: Record Collection Outcomes And Stop Evidence Loops Honestly

**Files:**
- Modify: `backend/app/graph/nodes/__init__.py`
- Modify: `backend/app/graph/builder.py`
- Modify: `backend/app/tests/test_resume_and_evidence.py`
- Modify: `backend/app/tests/test_graph_integration.py`

- [ ] **Step 1: Write failing node tests**

Append to `backend/app/tests/test_resume_and_evidence.py`:

```python
from app.graph.nodes import critic_node, evidence_aggregate_node, remediation_node, verify_outcome_node
from app.models.evidence_collection import (
    EvidenceCollectionResult,
    EvidenceCollectionStatus,
)


def test_aggregate_ignores_empty_collection_results():
    state = {
        "evidence_items": [],
        "evidence_collection_results": [
            EvidenceCollectionResult(
                tool_name="query_metrics",
                category="metrics",
                params={"service": "api"},
                status=EvidenceCollectionStatus.SUCCESS_EMPTY,
            )
        ],
        "step_count": 0,
    }

    result = evidence_aggregate_node(state)

    assert result["evidence_quality_score"] == 0.0
    assert result["missing_evidence_categories"] == [
        "deployments",
        "logs",
        "metrics",
        "runbook",
    ]


def test_critic_hands_off_after_evidence_loop_limit():
    state = {
        "loop_count": 2,
        "max_loop_count": 2,
        "missing_evidence_categories": ["deployments", "runbook"],
        "failed_evidence_tools": ["query_runbook"],
        "root_cause_candidates": [],
        "step_count": 0,
    }

    result = critic_node(state)

    assert result["critic_decision"] == "NEEDS_HUMAN"
    assert result["status"] == RunStatus.NEEDS_HUMAN
    assert result["halted_at_node"] == "node_critic"
    assert result["terminal_reason"]["code"] == "EVIDENCE_EXHAUSTED"


def test_remediation_refuses_action_without_usable_evidence():
    state = {
        "ticket": {"service": "api", "env": "prod"},
        "root_cause_candidates": [
            {
                "hypothesis": "resource pressure",
                "confidence": 0.7,
                "supporting_evidence_ids": [],
            }
        ],
        "evidence_items": [],
        "evidence_collection_results": [],
        "step_count": 0,
    }

    result = remediation_node(state)

    assert result["status"] == RunStatus.NEEDS_HUMAN
    assert result["remediation_plan"].actions == []
    assert result["terminal_reason"]["code"] == "NO_SUPPORTED_AUTOMATION_ACTION"


@pytest.mark.asyncio
async def test_verify_preserves_executor_halt_for_failed_actions():
    result = await verify_outcome_node(
        {
            "run_id": "run-action-failed",
            "ticket": {"service": "api", "env": "prod"},
            "action_results": [{"action_type": "restart", "success": False}],
            "step_count": 0,
        }
    )

    assert result["status"] == RunStatus.FAILED
    assert result["halted_at_node"] == "node_executor"
    assert result["terminal_reason"]["code"] == "ACTION_EXECUTION_FAILED"
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py -q
```

Expected: FAIL because aggregate counts persisted evidence indiscriminately, critic force-passes, and remediation emits an unsupported restart.

- [ ] **Step 3: Replace fanout drop-on-failure behavior**

Import the reliability helper and collection model in
`backend/app/graph/nodes/__init__.py`:

```python
from app.graph.evidence_quality import (
    classify_collection_result,
    compute_evidence_quality,
    usable_evidence_ids,
)
from app.models.evidence_collection import EvidenceCollectionStatus
```

Inside `evidence_fanout_node`, replace `_collect_one` with:

```python
    async def _collect_one(tool_name, params, category, degrade):
        req = ToolRequest(tool_name=tool_name, params=params, run_id=run_id)
        try:
            response = await gateway.call_tool(req)
        except Exception as exc:
            response = ToolResponse(
                tool_name=tool_name,
                success=False,
                error=str(exc),
                latency_ms=0,
            )
        evidence = None
        outcome = classify_collection_result(tool_name, category, params, response)
        if outcome.status == EvidenceCollectionStatus.SUCCESS_USABLE:
            evidence = EvidenceItem(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                tool_name=tool_name,
                category=category,
                source_ref=f"{category}-{run_id}",
                summary=f"Retrieved usable {category} data for {params.get('service', 'unknown')}",
                raw_payload=response.result,
                confidence=0.8,
                freshness_score=0.9,
                completeness_score=0.7,
            )
            outcome.evidence_id = evidence.evidence_id
        if not degrade and outcome.status != EvidenceCollectionStatus.SUCCESS_USABLE:
            state["status"] = RunStatus.NEEDS_HUMAN
            state["halted_at_node"] = "node_evidence_fanout"
            state["terminal_reason"] = {
                "code": "NON_DEGRADABLE_EVIDENCE_FAILED",
                "stage": "evidence_fanout",
                "message": f"{tool_name} did not return usable evidence",
                "failed_tools": [tool_name],
            }
        return evidence, outcome
```

Replace result accumulation with:

```python
    evidence_items = state.get("evidence_items", [])
    collection_results = state.get("evidence_collection_results", [])
    for result in results:
        if isinstance(result, Exception):
            continue
        evidence, outcome = result
        collection_results.append(outcome)
        if evidence is not None:
            evidence_items.append(evidence)

    state["evidence_items"] = evidence_items
    state["evidence_collection_results"] = collection_results
```

Import `ToolResponse` alongside `ToolRequest`.

- [ ] **Step 4: Replace aggregate scoring and exhausted-loop behavior**

Replace the score section of `evidence_aggregate_node` with:

```python
    collection_results = state.get("evidence_collection_results", [])
    quality_score, missing, failed_tools = compute_evidence_quality(items, collection_results)
    usable_ids = set(usable_evidence_ids(collection_results))
    usable_items = [
        item
        for item in items
        if (item.evidence_id if hasattr(item, "evidence_id") else item.get("evidence_id"))
        in usable_ids
    ]
    categories = {}
    for item in usable_items:
        category = item.category if hasattr(item, "category") else item.get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1
    summary = f"Collected {len(usable_items)} usable evidence items."
    if categories:
        summary += " Categories: " + ", ".join(f"{key}: {value}" for key, value in categories.items())
```

Preserve contradiction detection, but run it against `usable_items`. Store:

```python
    state["evidence_summary"] = summary
    state["evidence_quality_score"] = quality_score
    state["missing_evidence_categories"] = missing
    state["failed_evidence_tools"] = failed_tools
```

Replace the loop-guard branch in `critic_node` with:

```python
    if loop_count >= max_loop:
        state["critic_decision"] = "NEEDS_HUMAN"
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_critic"
        state["terminal_reason"] = {
            "code": "EVIDENCE_EXHAUSTED",
            "stage": "critic",
            "message": "Evidence remained insufficient after the configured collection loops",
            "failed_tools": state.get("failed_evidence_tools", []),
            "missing_evidence_categories": state.get("missing_evidence_categories", []),
        }
        state["step_count"] = state.get("step_count", 0) + 1
        return state
```

- [ ] **Step 5: Restrict remediation to supported actions**

At the start of `remediation_node`, calculate:

```python
    usable_ids = set(usable_evidence_ids(state.get("evidence_collection_results", [])))
```

For each top candidate, calculate its evidence intersection:

```python
        candidate_ids = (
            top_candidate.supporting_evidence_ids
            if hasattr(top_candidate, "supporting_evidence_ids")
            else top_candidate.get("supporting_evidence_ids", [])
        )
        supporting_ids = sorted(usable_ids & set(candidate_ids))
```

Only build rollback or restart when `supporting_ids` is non-empty, and pass:

```python
                supporting_evidence_ids=supporting_ids,
```

After building the plan, hand off when no supported action exists:

```python
    if not actions:
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_remediation"
        state["terminal_reason"] = {
            "code": "NO_SUPPORTED_AUTOMATION_ACTION",
            "stage": "remediation",
            "message": "No automation action has usable supporting evidence",
            "failed_tools": state.get("failed_evidence_tools", []),
            "missing_evidence_categories": state.get("missing_evidence_categories", []),
        }
    else:
        state["status"] = RunStatus.PLANNED
```

In `diagnose_node`, bind generated candidates to currently usable evidence:

```python
    supporting_ids = usable_evidence_ids(state.get("evidence_collection_results", []))
```

Use `supporting_evidence_ids=supporting_ids` for parsed and fallback candidates.

- [ ] **Step 6: Route human handoff directly to RCA**

In `backend/app/graph/builder.py`, import `RunStatus` alongside `IncidentAgentState`, then add:

```python
def _route_human_handoff_or(state: IncidentAgentState, next_node: str) -> str:
    if state.get("status") == RunStatus.NEEDS_HUMAN:
        return "node_rca"
    return next_node


def _route_after_evidence_aggregate(state: IncidentAgentState) -> str:
    return _route_human_handoff_or(state, "node_diagnose")


def _route_after_remediation(state: IncidentAgentState) -> str:
    return _route_human_handoff_or(state, "node_risk_gate")
```

At the top of `_route_after_critic` and `_route_after_risk_gate`, add:

```python
    if state.get("status") == RunStatus.NEEDS_HUMAN:
        return "node_rca"
```

Replace static edges after aggregate and remediation with conditional edges:

```python
    graph.add_conditional_edges(
        "node_evidence_aggregate",
        _route_after_evidence_aggregate,
        {"node_diagnose": "node_diagnose", "node_rca": "node_rca"},
    )
    graph.add_conditional_edges(
        "node_remediation",
        _route_after_remediation,
        {"node_risk_gate": "node_risk_gate", "node_rca": "node_rca"},
    )
```

- [ ] **Step 7: Persist the actual execution or verification halt stage**

In `executor_node`, directly after setting `state["status"]`, add:

```python
    if has_failure:
        state["halted_at_node"] = "node_executor"
        state["terminal_reason"] = {
            "code": "ACTION_EXECUTION_FAILED",
            "stage": "executor",
            "message": "At least one automation action failed during execution",
        }
```

In the early fatal branch of `verify_outcome_node`, add:

```python
        state.setdefault("halted_at_node", "node_executor")
        state.setdefault(
            "terminal_reason",
            {
                "code": "ACTION_EXECUTION_FAILED",
                "stage": "executor",
                "message": "No automation action completed successfully",
            },
        )
```

In the majority-failed verification branch, add:

```python
        state["halted_at_node"] = "node_verify_outcome"
        state["terminal_reason"] = {
            "code": "VERIFICATION_FAILED",
            "stage": "verify",
            "message": "Most post-remediation verification checks failed",
        }
```

In `_route_after_verify` in `backend/app/graph/builder.py`, mark exhausted retries before routing to
RCA:

```python
        state["status"] = RunStatus.FAILED
        state["halted_at_node"] = "node_verify_outcome"
        state["terminal_reason"] = {
            "code": "VERIFICATION_RETRIES_EXHAUSTED",
            "stage": "verify",
            "message": "Post-remediation verification retries were exhausted",
        }
        return "node_rca"
```

- [ ] **Step 8: Run focused graph tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py app/tests/test_graph_integration.py -q
```

Expected: PASS after updating graph integration fixtures to include collection outcomes where they expect automatic execution.

- [ ] **Step 9: Commit**

```bash
git add backend/app/graph/nodes/__init__.py backend/app/graph/builder.py \
  backend/app/tests/test_resume_and_evidence.py backend/app/tests/test_graph_integration.py
git commit -m "backend: stop unsupported evidence loops"
```

---

### Task 4: Persist Sanitized Tool Audits And Describe Capabilities

**Files:**
- Create: `backend/app/repositories/tool_audits_repo.py`
- Modify: `backend/app/repositories/__init__.py`
- Modify: `backend/app/tools/gateway.py`
- Modify: `backend/app/tests/test_tool_gateway.py`

- [ ] **Step 1: Write failing gateway tests**

Append to `backend/app/tests/test_tool_gateway.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.db_models import Base, IncidentRun, IncidentToolAudit, RunStatusEnum


def create_audit_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_factory()
    db.add(IncidentRun(run_id="run-audit", thread_id="thread-audit", status=RunStatusEnum.NEW))
    db.commit()
    db.close()
    return session_factory


def test_describe_capability_reports_missing_real_execute_adapter(monkeypatch):
    gateway_module = importlib.import_module("app.tools.gateway")
    monkeypatch.setattr(gateway_module, "ADAPTER_MODE", "real")
    gateway = ToolGateway()

    capability = gateway.describe_capability("execute_action")

    assert capability == {
        "available": False,
        "adapter_mode": "real",
        "reason": "real adapter is not configured",
    }


@pytest.mark.asyncio
async def test_tool_audit_is_persisted_and_sanitized(monkeypatch):
    session_factory = create_audit_session_factory()
    gateway = ToolGateway(audit_session_factory=session_factory)
    request = ToolRequest(
        tool_name="query_logs",
        params={"service": "api", "env": "prod", "token": "secret-value"},
        run_id="run-audit",
    )

    response = await gateway.call_tool(request)

    assert response.success is True
    db = session_factory()
    try:
        audits = db.query(IncidentToolAudit).all()
        assert len(audits) == 1
        assert audits[0].request_json["token"] == "[REDACTED]"
    finally:
        db.close()


@pytest.mark.asyncio
async def test_validation_failure_is_audited():
    session_factory = create_audit_session_factory()
    gateway = ToolGateway(audit_session_factory=session_factory)

    await gateway.call_tool(
        ToolRequest(
            tool_name="query_db_slow_queries",
            params={"threshold_seconds": "bad"},
            run_id="run-audit",
        )
    )

    db = session_factory()
    try:
        audit = db.query(IncidentToolAudit).one()
        assert audit.success == 0
        assert "expected integer" in audit.error_message
    finally:
        db.close()
```

- [ ] **Step 2: Run gateway tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_tool_gateway.py -q
```

Expected: FAIL because `ToolGateway` has no capability API, injected session factory, or database audit persistence.

- [ ] **Step 3: Add the audit repository**

Create `backend/app/repositories/tool_audits_repo.py`:

```python
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.db_models import IncidentToolAudit


class ToolAuditsRepo:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        run_id: str,
        tool_name: str,
        adapter_mode: str,
        request_json: Optional[Dict[str, Any]],
        response_json: Optional[Dict[str, Any]],
        success: bool,
        error_message: Optional[str],
        latency_ms: int,
    ) -> IncidentToolAudit:
        audit = IncidentToolAudit(
            audit_id=f"audit_{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            tool_name=tool_name,
            adapter_mode=adapter_mode,
            request_json=request_json,
            response_json=response_json,
            success=1 if success else 0,
            error_message=error_message,
            latency_ms=latency_ms,
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit
```

Export `ToolAuditsRepo` from `backend/app/repositories/__init__.py`.

- [ ] **Step 4: Add capability descriptions and recursive redaction**

In `backend/app/tools/gateway.py`, add:

```python
REAL_UNAVAILABLE_TOOLS = {
    "query_runbook": "real adapter is not configured",
    "execute_action": "real adapter is not configured",
    "query_ticket_by_id": "real adapter is not configured",
    "query_service_metadata": "real adapter is not configured",
}
SENSITIVE_KEY_MARKERS = (
    "password",
    "secret",
    "token",
    "api_key",
    "access_key",
    "authorization",
    "cookie",
)


def _default_audit_session_factory():
    from app.repositories import SessionLocal

    return SessionLocal()


def _redact_sensitive(value: Any, key: str = "") -> Any:
    if any(marker in key.lower() for marker in SENSITIVE_KEY_MARKERS):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {item_key: _redact_sensitive(item, item_key) for item_key, item in value.items()}
    if isinstance(value, list):
        return [_redact_sensitive(item) for item in value]
    return value
```

Change the constructor and add:

```python
    def __init__(self, audit_session_factory=None):
        self.handlers = tool_handlers
        self.registry = TOOL_REGISTRY
        self.audit_log = audit_log
        self.adapter_mode = ADAPTER_MODE
        self.audit_session_factory = audit_session_factory or _default_audit_session_factory

    def describe_capability(self, tool_name: str) -> Dict[str, Any]:
        if tool_name not in self.handlers:
            return {
                "available": False,
                "adapter_mode": ADAPTER_MODE,
                "reason": "tool is not registered",
            }
        if ADAPTER_MODE != "real":
            return {"available": True, "adapter_mode": ADAPTER_MODE, "reason": "mock adapter"}
        reason = REAL_UNAVAILABLE_TOOLS.get(tool_name)
        if reason:
            return {"available": False, "adapter_mode": ADAPTER_MODE, "reason": reason}
        if select_adapter(tool_name) is None:
            return {
                "available": False,
                "adapter_mode": ADAPTER_MODE,
                "reason": "real adapter is not configured",
            }
        return {"available": True, "adapter_mode": ADAPTER_MODE, "reason": "real adapter"}
```

- [ ] **Step 5: Persist every audit path**

Replace `_log_audit` with:

```python
    def _log_audit(
        self,
        request: ToolRequest,
        latency_ms: int,
        success: bool,
        result: Dict[str, Any],
        adapter_info: str = "unknown",
    ):
        safe_params = _redact_sensitive(request.params)
        safe_result = _redact_sensitive(result)
        entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": request.run_id,
            "tool_name": request.tool_name,
            "params": safe_params,
            "adapter": adapter_info,
            "latency_ms": latency_ms,
            "success": success,
            "result": safe_result if success else None,
            "error": safe_result.get("error") if not success else None,
        }
        self.audit_log.append(entry)
        if not request.run_id:
            logger.warning("Skipping durable tool audit without run_id: %s", request.tool_name)
            return
        db = None
        try:
            from app.repositories.tool_audits_repo import ToolAuditsRepo

            db = self.audit_session_factory()
            ToolAuditsRepo(db).insert(
                run_id=request.run_id,
                tool_name=request.tool_name,
                adapter_mode=adapter_info,
                request_json=safe_params,
                response_json=safe_result if success else None,
                success=success,
                error_message=entry["error"],
                latency_ms=latency_ms,
            )
        except Exception:
            logger.warning("Failed to persist tool audit for %s", request.tool_name, exc_info=True)
        finally:
            if db is not None:
                db.close()
```

Add this method to `ToolGateway`:

```python
    def _failure_response(
        self,
        request: ToolRequest,
        start_time: float,
        span_id: str,
        error: str,
        adapter_info: str,
    ) -> ToolResponse:
        latency = int((time.time() - start_time) * 1000)
        self._log_audit(
            request,
            latency,
            False,
            {"error": error},
            adapter_info=adapter_info,
        )
        tracer.end_span(span_id, status="error", error=error)
        return ToolResponse(
            tool_name=request.tool_name,
            success=False,
            error=error,
            latency_ms=latency,
        )
```

Sanitize trace payloads too. Replace:

```python
        tracer.add_event(span_id, "tool_called", {"params": request.params})
```

with:

```python
        tracer.add_event(span_id, "tool_called", {"params": _redact_sensitive(request.params)})
```

Replace the three early-return branches in `call_tool` with:

```python
        if request.tool_name not in self.handlers:
            return self._failure_response(
                request,
                start_time,
                span_id,
                f"Tool '{request.tool_name}' not found",
                "unknown",
            )

        metadata = self.registry.get(request.tool_name)
        validation_error = self._validate_params(request.params, metadata)
        if validation_error:
            return self._failure_response(
                request,
                start_time,
                span_id,
                validation_error,
                ADAPTER_MODE,
            )

        real_handler = select_adapter(request.tool_name)
        if real_handler and ADAPTER_MODE == "real":
            handler = real_handler
            adapter_info = "real"
        elif ADAPTER_MODE == "real":
            return self._failure_response(
                request,
                start_time,
                span_id,
                f"Tool '{request.tool_name}' has no real adapter configured",
                "real",
            )
        else:
            handler = self.handlers[request.tool_name]
            adapter_info = "mock"
```

- [ ] **Step 6: Run gateway tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_tool_gateway.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/repositories/tool_audits_repo.py backend/app/repositories/__init__.py \
  backend/app/tools/gateway.py backend/app/tests/test_tool_gateway.py
git commit -m "backend: persist sanitized tool audits"
```

---

### Task 5: Preflight Automation And Resume From The Pause Checkpoint

**Files:**
- Modify: `backend/app/graph/nodes/__init__.py`
- Modify: `backend/app/services/approval_runtime.py`
- Modify: `backend/app/tests/test_resume_and_evidence.py`
- Modify: `backend/app/tests/test_graph_integration.py`

- [ ] **Step 1: Write failing preflight and resume tests**

Append to `backend/app/tests/test_resume_and_evidence.py`:

```python
def test_risk_gate_hands_off_when_execute_capability_is_missing(monkeypatch):
    monkeypatch.setattr(
        "app.graph.nodes.gateway.describe_capability",
        lambda _tool_name: {
            "available": False,
            "adapter_mode": "real",
            "reason": "real adapter is not configured",
        },
    )
    state = {
        "ticket": {"env": "prod", "severity": "P2"},
        "remediation_plan": RemediationPlan(
            summary="restart service",
            actions=[
                ActionSpec(
                    action_type="restart",
                    service="api",
                    env="prod",
                    params={},
                    risk_level="LOW",
                    supporting_evidence_ids=["ev-1"],
                )
            ],
            expected_outcome="recover",
        ),
        "root_cause_candidates": [{"confidence": 0.9}],
        "step_count": 0,
    }

    result = risk_gate_node(state)

    assert result["risk_decision"] == "NEEDS_HUMAN"
    assert result["status"] == RunStatus.NEEDS_HUMAN
    assert result["halted_at_node"] == "node_risk_gate"
    assert result["terminal_reason"]["code"] == "AUTOMATION_CAPABILITY_UNAVAILABLE"


def test_risk_gate_rejects_action_without_usable_support(monkeypatch):
    monkeypatch.setattr(
        "app.graph.nodes.gateway.describe_capability",
        lambda _tool_name: {
            "available": True,
            "adapter_mode": "mock",
            "reason": "mock adapter",
        },
    )
    state = {
        "ticket": {"env": "prod", "severity": "P2"},
        "remediation_plan": RemediationPlan(
            summary="restart service",
            actions=[
                ActionSpec(
                    action_type="restart",
                    service="api",
                    env="prod",
                    params={},
                    risk_level="LOW",
                    supporting_evidence_ids=["ev-missing"],
                )
            ],
            expected_outcome="recover",
        ),
        "evidence_collection_results": [],
        "root_cause_candidates": [{"confidence": 0.9}],
        "step_count": 0,
    }

    result = risk_gate_node(state)

    assert result["risk_decision"] == "NEEDS_HUMAN"
    assert result["status"] == RunStatus.NEEDS_HUMAN
    assert result["terminal_reason"]["code"] == "AUTOMATION_ACTION_UNSUPPORTED"


def test_risk_gate_rejects_unavailable_precondition_capability(monkeypatch):
    def capability(tool_name):
        if tool_name == "query_service_metadata":
            return {
                "available": False,
                "adapter_mode": "real",
                "reason": "real adapter is not configured",
            }
        return {"available": True, "adapter_mode": "real", "reason": "real adapter"}

    monkeypatch.setattr("app.graph.nodes.gateway.describe_capability", capability)
    state = {
        "ticket": {"env": "prod", "severity": "P2"},
        "remediation_plan": RemediationPlan(
            summary="restart service",
            actions=[
                ActionSpec(
                    action_type="restart",
                    service="api",
                    env="prod",
                    params={},
                    risk_level="LOW",
                    preconditions=["service_exists"],
                    supporting_evidence_ids=["ev-1"],
                )
            ],
            expected_outcome="recover",
        ),
        "evidence_collection_results": [
            EvidenceCollectionResult(
                tool_name="query_logs",
                category="logs",
                params={"service": "api"},
                status=EvidenceCollectionStatus.SUCCESS_USABLE,
                evidence_id="ev-1",
            )
        ],
        "root_cause_candidates": [{"confidence": 0.9}],
        "step_count": 0,
    }

    result = risk_gate_node(state)

    assert result["status"] == RunStatus.NEEDS_HUMAN
    assert result["terminal_reason"]["code"] == "PRECONDITION_CAPABILITY_UNAVAILABLE"
    assert result["terminal_reason"]["failed_tools"] == ["query_service_metadata"]


def test_approval_runtime_uses_pause_checkpoint_without_step_regression(monkeypatch):
    session_factory = create_session_factory()
    db = session_factory()
    try:
        db.add(
            IncidentRun(
                run_id="run-pause",
                thread_id="thread-pause",
                status=RunStatusEnum.WAITING_HUMAN,
            )
        )
        db.add_all(
            [
                IncidentCheckpoint(
                    checkpoint_id="cp-risk",
                    run_id="run-pause",
                    node_name="node_risk_gate",
                    state_json={"step_count": 18, "risk_decision": "NEEDS_APPROVAL"},
                ),
                IncidentCheckpoint(
                    checkpoint_id="cp-pause",
                    run_id="run-pause",
                    node_name="node_approval_interrupt",
                    state_json={"step_count": 19, "risk_decision": "NEEDS_APPROVAL"},
                ),
            ]
        )
        db.commit()
        monkeypatch.setattr("app.services.approval_runtime.event_bus.publish", lambda **_kwargs: None)

        state, node_name = ApprovalRuntime(db).prepare_resume_state(
            run_id="run-pause",
            approval_id="apr-1",
            decision="approved",
        )

        assert node_name == "node_approval_interrupt"
        assert state["step_count"] == 19
        assert state["risk_decision"] == "NEEDS_APPROVAL"
        assert state["_resume_from_node"] == "node_executor"
    finally:
        db.close()
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py -q
```

Expected: FAIL because risk gate does not preflight and resume loads `node_risk_gate`.

- [ ] **Step 3: Add risk-gate capability preflight**

In `risk_gate_node`, after obtaining `actions`, add:

```python
    capability = gateway.describe_capability("execute_action")
    if not capability["available"]:
        state["risk_decision"] = "NEEDS_HUMAN"
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_risk_gate"
        state["terminal_reason"] = {
            "code": "AUTOMATION_CAPABILITY_UNAVAILABLE",
            "stage": "risk_gate",
            "message": f"execute_action {capability['reason']}",
            "failed_tools": ["execute_action"],
            "missing_evidence_categories": state.get("missing_evidence_categories", []),
        }
        state["step_count"] = state.get("step_count", 0) + 1
        return state
```

Immediately after capability preflight, validate action support again so human modifications and
restored checkpoints cannot bypass remediation:

```python
    usable_ids = set(usable_evidence_ids(state.get("evidence_collection_results", [])))
    unsupported_actions = []
    for action in actions:
        support_ids = (
            action.supporting_evidence_ids
            if hasattr(action, "supporting_evidence_ids")
            else action.get("supporting_evidence_ids", [])
        )
        if not usable_ids.intersection(support_ids):
            unsupported_actions.append(
                action.action_type
                if hasattr(action, "action_type")
                else action.get("action_type", "unknown")
            )
    if unsupported_actions:
        state["risk_decision"] = "NEEDS_HUMAN"
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_risk_gate"
        state["terminal_reason"] = {
            "code": "AUTOMATION_ACTION_UNSUPPORTED",
            "stage": "risk_gate",
            "message": "Automation actions lack usable supporting evidence",
            "actions": unsupported_actions,
        }
        state["step_count"] = state.get("step_count", 0) + 1
        return state
```

Then validate that each declared precondition can be evaluated without invoking external systems:

```python
    precondition_tools = {
        "service_exists": "query_service_metadata",
        "deployment_healthy": "query_k8s_deployment_status",
    }
    failed_precondition_tools = set()
    for action in actions:
        preconditions = (
            action.preconditions
            if hasattr(action, "preconditions")
            else action.get("preconditions", [])
        ) or []
        for precondition in preconditions:
            tool_name = precondition_tools.get(precondition)
            if tool_name and not gateway.describe_capability(tool_name)["available"]:
                failed_precondition_tools.add(tool_name)
    if failed_precondition_tools:
        state["risk_decision"] = "NEEDS_HUMAN"
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_risk_gate"
        state["terminal_reason"] = {
            "code": "PRECONDITION_CAPABILITY_UNAVAILABLE",
            "stage": "risk_gate",
            "message": "Automation preconditions cannot be evaluated",
            "failed_tools": sorted(failed_precondition_tools),
        }
        state["step_count"] = state.get("step_count", 0) + 1
        return state
```

Update the existing `test_risk_gate_keeps_low_risk_action_out_of_approval` fixture so its action
contains:

```python
                    supporting_evidence_ids=["ev-1"],
```

and its state contains:

```python
        "evidence_collection_results": [
            EvidenceCollectionResult(
                tool_name="query_logs",
                category="logs",
                params={"service": "mysql"},
                status=EvidenceCollectionStatus.SUCCESS_USABLE,
                evidence_id="ev-1",
            )
        ],
```

In `approval_interrupt_node`, replace `evidence_refs=[]` with:

```python
            evidence_refs=(
                action.supporting_evidence_ids
                if hasattr(action, "supporting_evidence_ids")
                else action.get("supporting_evidence_ids", [])
            ),
```

- [ ] **Step 4: Load the latest pause checkpoint during resume**

In `ApprovalRuntime.prepare_resume_state`, replace the risk-gate-specific checkpoint load with:

```python
        checkpoint = self.checkpoints_repo.load_latest(
            run_id,
            node_name="node_approval_interrupt",
        )
        if not checkpoint:
            checkpoint = self.checkpoints_repo.load_latest(run_id)
```

Remove the approved-branch assignment:

```python
            state["risk_decision"] = "LOW_ONLY"
```

Update the method docstring to state that the dispatcher uses `_resume_from_node`, so the full
pause checkpoint is safe to restore.

- [ ] **Step 5: Run focused tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py app/tests/test_graph_integration.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/graph/nodes/__init__.py backend/app/services/approval_runtime.py \
  backend/app/tests/test_resume_and_evidence.py backend/app/tests/test_graph_integration.py
git commit -m "backend: preflight automation before approval"
```

---

### Task 6: Separate Paused Runs From Terminal Runs

**Files:**
- Modify: `backend/app/services/event_bus.py`
- Modify: `backend/app/services/graph_runner.py`
- Modify: `backend/app/i18n/__init__.py`
- Modify: `backend/app/tests/test_resume_and_evidence.py`

- [ ] **Step 1: Write failing GraphRunner lifecycle tests**

Append to `backend/app/tests/test_resume_and_evidence.py`:

```python
@pytest.mark.asyncio
async def test_graph_runner_marks_waiting_human_as_paused(monkeypatch):
    session_factory = create_session_factory()
    db = session_factory()
    try:
        db.add(
            IncidentRun(
                run_id="run-waiting",
                thread_id="thread-waiting",
                status=RunStatusEnum.NEW,
            )
        )
        db.commit()

        class FakeGraph:
            async def astream(self, initial_state, config=None):
                yield {
                    "node_approval_interrupt": {
                        **initial_state,
                        "status": RunStatus.WAITING_HUMAN,
                        "step_count": 1,
                    }
                }

        monkeypatch.setattr("app.services.graph_runner.create_incident_graph", lambda: FakeGraph())
        runner = GraphRunner(db)
        emitted = []
        monkeypatch.setattr(runner, "_emit", lambda *args, **kwargs: emitted.append((args, kwargs)))

        await runner.run("run-waiting", {"evidence_items": [], "step_count": 0})

        saved = RunsRepo(db).get("run-waiting")
        assert saved.completed_at is None
        assert any(args[1] == EventType.RUN_PAUSED for args, _kwargs in emitted)
        assert not any(args[1] == EventType.RUN_COMPLETED for args, _kwargs in emitted)
    finally:
        db.close()


@pytest.mark.asyncio
async def test_graph_runner_persists_human_handoff_reason(monkeypatch):
    session_factory = create_session_factory()
    db = session_factory()
    try:
        db.add(
            IncidentRun(
                run_id="run-human",
                thread_id="thread-human",
                status=RunStatusEnum.NEW,
            )
        )
        db.commit()

        class FakeGraph:
            async def astream(self, initial_state, config=None):
                yield {
                    "node_rca": {
                        **initial_state,
                        "status": RunStatus.NEEDS_HUMAN,
                        "halted_at_node": "node_risk_gate",
                        "terminal_reason": {"code": "AUTOMATION_CAPABILITY_UNAVAILABLE"},
                        "step_count": 1,
                    }
                }

        monkeypatch.setattr("app.services.graph_runner.create_incident_graph", lambda: FakeGraph())

        await GraphRunner(db).run("run-human", {"evidence_items": [], "step_count": 0})

        saved = RunsRepo(db).get("run-human")
        assert saved.status == RunStatusEnum.NEEDS_HUMAN
        assert saved.halted_at_node == "node_risk_gate"
        assert saved.terminal_reason_json == {"code": "AUTOMATION_CAPABILITY_UNAVAILABLE"}
        assert saved.completed_at is not None
    finally:
        db.close()
```

- [ ] **Step 2: Run lifecycle tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py -q
```

Expected: FAIL because all graph exits currently set `completed_at` and emit `RUN_COMPLETED`.

- [ ] **Step 3: Add pause event and translated messages**

Add to `EventType` in `backend/app/services/event_bus.py`:

```python
    RUN_PAUSED = "RUN_PAUSED"
```

In `backend/app/i18n/__init__.py`, add `needs_human` status labels and `run_paused` messages:

```python
        "needs_human": "Needs Human Intervention",
```

```python
        "needs_human": "需要人工接管",
```

```python
        "run_paused": "Run paused | status: {status}",
```

```python
        "run_paused": "运行已暂停｜状态：{status}",
```

Normalize status keys in `get_status_name`:

```python
    return STATUS_NAMES.get(lang, {}).get(status.lower(), status)
```

- [ ] **Step 4: Persist halt metadata and pause semantics**

Extend `_sync_run_progress` in `backend/app/services/graph_runner.py`:

```python
        if "halted_at_node" in state:
            update_fields["halted_at_node"] = state.get("halted_at_node")
        if "terminal_reason" in state:
            update_fields["terminal_reason_json"] = state.get("terminal_reason")
        if status_enum in (RunStatusEnum.WAITING_HUMAN, RunStatusEnum.NEEDS_HUMAN):
            update_fields["requires_human"] = 1
```

Replace the unconditional final `_update_run` and event emission with:

```python
            from app.i18n import get_status_name, t

            status_value = status_enum.value
            if status_enum == RunStatusEnum.WAITING_HUMAN:
                self._update_run(run_id, status=status_enum, completed_at=None, current_node=None)
                self._emit(
                    run_id,
                    EventType.RUN_PAUSED,
                    message=t("run_paused", status=get_status_name(status_value)),
                )
            else:
                self._update_run(
                    run_id,
                    status=status_enum,
                    completed_at=datetime.utcnow(),
                    current_node=None,
                )
                self._emit(
                    run_id,
                    EventType.RUN_COMPLETED,
                    message=t("run_completed", status=get_status_name(status_value)),
                )
```

In the exception branch, also persist:

```python
                halted_at_node=next(iter(active_node_spans), None),
                terminal_reason_json={
                    "code": "GRAPH_EXECUTION_ERROR",
                    "stage": "graph_runner",
                    "message": error_msg[:1000],
                },
```

- [ ] **Step 5: Run focused lifecycle tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/event_bus.py backend/app/services/graph_runner.py \
  backend/app/i18n/__init__.py backend/app/tests/test_resume_and_evidence.py
git commit -m "backend: distinguish paused and terminal runs"
```

---

### Task 7: Generate Downgraded RCA And Persist Certainty

**Files:**
- Modify: `backend/app/graph/nodes/__init__.py`
- Modify: `backend/app/repositories/rca_repo.py`
- Modify: `backend/app/services/graph_runner.py`
- Modify: `backend/app/tests/test_resume_and_evidence.py`

- [ ] **Step 1: Write failing RCA downgrade test**

Append to `backend/app/tests/test_resume_and_evidence.py`:

```python
from app.graph.nodes import rca_node


def test_rca_downgrades_human_handoff_without_confirmed_root_cause(monkeypatch):
    async def no_archive(_request):
        return ToolResponse(
            tool_name="write_rca_to_oss",
            success=False,
            error="disabled",
            latency_ms=0,
        )

    monkeypatch.setattr("app.graph.nodes.gateway.call_tool", no_archive)
    state = {
        "run_id": "run-human-rca",
        "ticket": {
            "title": "api errors",
            "description": "5xx increased",
            "service": "api",
            "env": "prod",
            "severity": "P2",
        },
        "status": RunStatus.NEEDS_HUMAN,
        "terminal_reason": {
            "code": "EVIDENCE_EXHAUSTED",
            "message": "Evidence remained insufficient",
        },
        "missing_evidence_categories": ["deployments", "runbook"],
        "failed_evidence_tools": ["query_runbook"],
        "root_cause_candidates": [
            {"hypothesis": "recent deployment", "confidence": 0.5}
        ],
        "evidence_items": [],
        "evidence_collection_results": [],
        "step_count": 0,
    }

    result = rca_node(state)

    assert result["status"] == RunStatus.NEEDS_HUMAN
    assert result["rca_report"].root_cause_status == "UNKNOWN"
    assert result["rca_report"].root_cause == "根因尚未确认"
    assert "人工" in result["rca_report"].resolution
    assert result["rca_report"].manual_next_steps
```

Import `ToolResponse` at the top of `backend/app/tests/test_resume_and_evidence.py`:

```python
from app.tools.schemas import ToolResponse
```

- [ ] **Step 2: Run the focused RCA test and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py -q
```

Expected: FAIL because RCA currently uses the first hypothesis as the root cause and lacks certainty fields.

- [ ] **Step 3: Add deterministic downgraded RCA output**

In `rca_node`, calculate:

```python
    needs_human = state.get("status") == RunStatus.NEEDS_HUMAN
    collection_results = state.get("evidence_collection_results", [])
    usable_ids = usable_evidence_ids(collection_results)
    root_cause_status = "UNKNOWN" if not usable_ids else "SUSPECTED"
    candidate_hypotheses = [
        {
            "hypothesis": c.hypothesis if hasattr(c, "hypothesis") else c.get("hypothesis", ""),
            "confidence": c.confidence if hasattr(c, "confidence") else c.get("confidence", 0.0),
        }
        for c in candidates
    ]
    terminal_reason = state.get("terminal_reason") or {}
    manual_next_steps = [
        f"检查缺失证据类别：{category}"
        for category in state.get("missing_evidence_categories", [])
    ]
    manual_next_steps.extend(
        f"修复工具后重新采集：{tool_name}"
        for tool_name in state.get("failed_evidence_tools", [])
    )
    if not manual_next_steps:
        manual_next_steps.append("由值班工程师复核诊断候选并选择处置动作")
```

Set the run outcome before rendering the prompt:

```python
    run_outcome = "NEEDS_HUMAN" if needs_human else ("FAILED" if is_failure else "SUCCESS")
```

When `needs_human` is true, bypass LLM certainty promotion and force these values after parsing any
LLM response:

```python
    final_root_cause = "根因尚未确认"
    final_resolution = "自动化流程已停止，需要人工接管"
```

Build:

```python
    automation_outcome = {
        "status": "NEEDS_HUMAN" if needs_human else run_outcome,
        "reason": terminal_reason,
        "executed_action_ids": executed_action_ids,
    }
```

Pass the new values to `RcaReport`. Preserve `NEEDS_HUMAN` at node exit:

```python
    if state.get("status") not in {
        RunStatus.FAILED,
        RunStatus.WAITING_HUMAN,
        RunStatus.NEEDS_HUMAN,
    }:
        state["status"] = RunStatus.COMPLETED
```

Fix evidence archive serialization by replacing nonexistent `source` and `content` fields:

```python
                "source_ref": (
                    ev.source_ref if hasattr(ev, "source_ref") else ev.get("source_ref")
                ),
                "summary": ev.summary if hasattr(ev, "summary") else ev.get("summary"),
                "raw_payload": (
                    ev.raw_payload if hasattr(ev, "raw_payload") else ev.get("raw_payload")
                ),
```

- [ ] **Step 4: Persist certainty fields**

Extend `RcaRepo.upsert` parameters and assignments in `backend/app/repositories/rca_repo.py`:

```python
        root_cause_status: Optional[str] = None,
        candidate_hypotheses: Optional[List[dict]] = None,
        automation_outcome: Optional[dict] = None,
        manual_next_steps: Optional[List[str]] = None,
```

Map them to:

```python
            existing.root_cause_status = root_cause_status
            existing.candidate_hypotheses_json = candidate_hypotheses
            existing.automation_outcome_json = automation_outcome
            existing.manual_next_steps_json = manual_next_steps
```

For new rows, add these constructor arguments to `IncidentRcaReport(...)`:

```python
                root_cause_status=root_cause_status,
                candidate_hypotheses_json=candidate_hypotheses,
                automation_outcome_json=automation_outcome,
                manual_next_steps_json=manual_next_steps,
```

Pass these fields from `GraphRunner._persist_rca`.

In `RcaRepo.confirm`, add:

```python
        rca.root_cause_status = "CONFIRMED"
```

- [ ] **Step 5: Run focused backend tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_resume_and_evidence.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/graph/nodes/__init__.py backend/app/repositories/rca_repo.py \
  backend/app/services/graph_runner.py backend/app/tests/test_resume_and_evidence.py
git commit -m "backend: downgrade unconfirmed rca reports"
```

---

### Task 8: Expose Halt Metadata And Collection Outcomes Through The API

**Files:**
- Modify: `backend/app/api/incidents.py`
- Modify: `backend/app/tests/test_incidents_api.py`

- [ ] **Step 1: Write failing API tests**

Append to `backend/app/tests/test_incidents_api.py`:

```python
def test_get_run_returns_halt_metadata():
    app, session_factory = create_test_client()
    db = session_factory()
    try:
        db.add(
            IncidentRun(
                run_id="run-human",
                thread_id="thread-human",
                status=RunStatusEnum.NEEDS_HUMAN,
                halted_at_node="node_risk_gate",
                terminal_reason_json={"code": "AUTOMATION_CAPABILITY_UNAVAILABLE"},
            )
        )
        db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-human")

    assert response.status_code == 200
    assert response.json()["halted_at_node"] == "node_risk_gate"
    assert response.json()["terminal_reason"]["code"] == "AUTOMATION_CAPABILITY_UNAVAILABLE"


def test_get_evidence_collection_results_returns_checkpoint_state():
    app, session_factory = create_test_client()
    seed_run_with_checkpoint(session_factory)
    db = session_factory()
    try:
        checkpoint = db.query(IncidentCheckpoint).filter_by(checkpoint_id="cp-123").one()
        checkpoint.state_json = {
            **checkpoint.state_json,
            "evidence_collection_results": [
                {
                    "tool_name": "query_metrics",
                    "category": "metrics",
                    "params": {"service": "payment-service"},
                    "status": "SUCCESS_EMPTY",
                    "latency_ms": 4,
                    "collected_at": "2026-06-02T10:00:00",
                }
            ],
        }
        db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.get("/incidents/runs/run-123/evidence/collection-results")

    assert response.status_code == 200
    assert response.json()[0]["status"] == "SUCCESS_EMPTY"


def test_resume_rejects_terminal_human_handoff():
    app, session_factory = create_test_client()
    db = session_factory()
    try:
        db.add(
            IncidentRun(
                run_id="run-human-terminal",
                thread_id="thread-human-terminal",
                status=RunStatusEnum.NEEDS_HUMAN,
            )
        )
        db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.post("/incidents/runs/run-human-terminal/resume")

    assert response.status_code == 409
    assert response.json()["detail"] == "NEEDS_HUMAN is terminal and cannot be resumed"
```

Extend the RCA API test fixture and assertion with:

```python
    assert payload["root_cause_status"] in ("CONFIRMED", "SUSPECTED", "UNKNOWN", None)
```

- [ ] **Step 2: Run API tests and verify failure**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_incidents_api.py -q
```

Expected: FAIL because run halt fields and the collection-results endpoint are missing.

- [ ] **Step 3: Extend API responses**

Add to `IncidentRunResponse`:

```python
    halted_at_node: Optional[str] = None
    terminal_reason: Optional[Dict[str, Any]] = None
```

Map in `_run_to_response`:

```python
        halted_at_node=getattr(run, "halted_at_node", None),
        terminal_reason=getattr(run, "terminal_reason_json", None),
```

Initialize new state in `create_run`:

```python
        "evidence_collection_results": [],
        "failed_evidence_tools": [],
```

Add:

```python
@router.get("/runs/{run_id}/evidence/collection-results")
async def get_evidence_collection_results(run_id: str, db=Depends(get_db)):
    state = _load_latest_checkpoint_state(run_id, db)
    return state.get("evidence_collection_results", [])
```

In `resume_run`, immediately after loading `run`, reject terminal human handoff:

```python
    if run.status == RunStatusEnum.NEEDS_HUMAN:
        raise HTTPException(
            status_code=409,
            detail="NEEDS_HUMAN is terminal and cannot be resumed",
        )
```

Import `RunStatusEnum` from `app.models.db_models`.

Return RCA fields:

```python
        "root_cause_status": rca.root_cause_status,
        "candidate_hypotheses": rca.candidate_hypotheses_json or [],
        "automation_outcome": rca.automation_outcome_json,
        "manual_next_steps": rca.manual_next_steps_json or [],
```

- [ ] **Step 4: Run API tests**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_incidents_api.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/incidents.py backend/app/tests/test_incidents_api.py
git commit -m "backend: expose reliability halt metadata"
```

---

### Task 9: Render Ten Explicit Stepper Stages And Restore Tailwind Tokens

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/components/RunStepper.tsx`
- Modify: `frontend/src/components/RunStepper.test.tsx`
- Modify: `frontend/src/i18n/en.json`
- Modify: `frontend/src/i18n/zh-CN.json`

- [ ] **Step 1: Write failing stepper tests**

Replace `frontend/src/components/RunStepper.test.tsx` with:

```tsx
import { describe, expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { RunStepper } from './RunStepper';
import { renderWithProviders } from '../test/render';

describe('RunStepper', () => {
  it('renders all ten display stages', () => {
    renderWithProviders(<RunStepper status="NEW" />);

    expect(screen.getByText('New')).toBeInTheDocument();
    expect(screen.getByText('Triaged')).toBeInTheDocument();
    expect(screen.getByText('Planned')).toBeInTheDocument();
    expect(screen.getByText('Gathering Evidence')).toBeInTheDocument();
    expect(screen.getByText('Diagnosed')).toBeInTheDocument();
    expect(screen.getByText('Risk Assessment')).toBeInTheDocument();
    expect(screen.getByText('Pending Approval')).toBeInTheDocument();
    expect(screen.getByText('Executing')).toBeInTheDocument();
    expect(screen.getByText('Verifying')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('maps waiting human to pending approval', () => {
    renderWithProviders(<RunStepper status="WAITING_HUMAN" />);
    expect(screen.getByTestId('step-PENDING_APPROVAL')).toHaveAttribute('data-current', 'true');
  });

  it('maps verifying to its own display stage', () => {
    renderWithProviders(<RunStepper status="VERIFYING" />);
    expect(screen.getByTestId('step-VERIFYING')).toHaveAttribute('data-current', 'true');
  });

  it('shows human handoff at the halted node', () => {
    renderWithProviders(
      <RunStepper
        status="NEEDS_HUMAN"
        haltedAtNode="node_risk_gate"
      />,
    );
    expect(screen.getByLabelText('Needs human intervention at Risk Assessment')).toHaveTextContent('!');
  });

  it('shows failure at the halted node', () => {
    renderWithProviders(
      <RunStepper
        status="FAILED"
        haltedAtNode="node_executor"
      />,
    );
    expect(screen.getByLabelText('Failed at Executing')).toHaveTextContent('×');
  });

  it('uses a conservative diagnosed fallback for an unknown status', () => {
    renderWithProviders(<RunStepper status="UNRECOGNIZED" />);
    expect(screen.getByTestId('step-DIAGNOSED')).toHaveAttribute('data-current', 'true');
  });
});
```

- [ ] **Step 2: Run stepper tests and verify failure**

Run:

```bash
cd frontend
npx vitest run src/components/RunStepper.test.tsx
```

Expected: FAIL because risk assessment, verifying mapping, and halt markers are missing.

- [ ] **Step 3: Load Tailwind v4 compatibility config**

In `frontend/src/index.css`, directly after `@import "tailwindcss";`, add:

```css
@config "../tailwind.config.js";
```

This restores generation of custom utilities such as `bg-status-success`, `bg-accent`,
`text-surface-primary`, and `bg-border-subtle`.

- [ ] **Step 4: Replace direct status indexing with explicit mappings**

Replace `frontend/src/components/RunStepper.tsx` with:

```tsx
import { useI18n } from '../i18n';

const STEPS = [
  'NEW',
  'TRIAGED',
  'PLANNED',
  'GATHERING_EVIDENCE',
  'DIAGNOSED',
  'RISK_ASSESSMENT',
  'PENDING_APPROVAL',
  'EXECUTING',
  'VERIFYING',
  'COMPLETED',
] as const;

const STATUS_TO_STEP: Record<string, string> = {
  NEW: 'NEW',
  TRIAGED: 'TRIAGED',
  PLANNED: 'PLANNED',
  GATHERING_EVIDENCE: 'GATHERING_EVIDENCE',
  DIAGNOSED: 'DIAGNOSED',
  PENDING_APPROVAL: 'PENDING_APPROVAL',
  WAITING_HUMAN: 'PENDING_APPROVAL',
  EXECUTING: 'EXECUTING',
  VERIFYING: 'VERIFYING',
  COMPLETED: 'COMPLETED',
};

const NODE_TO_STEP: Record<string, string> = {
  node_intake: 'NEW',
  node_triage: 'TRIAGED',
  node_retrieve_memory: 'TRIAGED',
  node_planner: 'PLANNED',
  node_evidence_fanout: 'GATHERING_EVIDENCE',
  node_evidence_aggregate: 'GATHERING_EVIDENCE',
  node_diagnose: 'DIAGNOSED',
  node_critic: 'DIAGNOSED',
  node_remediation: 'DIAGNOSED',
  node_risk_gate: 'RISK_ASSESSMENT',
  node_approval_interrupt: 'PENDING_APPROVAL',
  node_executor: 'EXECUTING',
  node_verify_outcome: 'VERIFYING',
  node_rca: 'COMPLETED',
};

interface RunStepperProps {
  status: string;
  currentNode?: string;
  haltedAtNode?: string;
}

export function RunStepper({ status, currentNode, haltedAtNode }: RunStepperProps) {
  const { t } = useI18n();
  const mappedNode = NODE_TO_STEP[haltedAtNode || currentNode || ''];
  const activeStep = mappedNode || STATUS_TO_STEP[status] || 'DIAGNOSED';
  const currentIndex = STEPS.indexOf(activeStep as (typeof STEPS)[number]);
  const abnormal = status === 'FAILED' || status === 'NEEDS_HUMAN';

  return (
    <div className="flex items-center justify-between overflow-x-auto pb-2">
      {STEPS.map((step, index) => {
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;
        const isAbnormal = abnormal && isCurrent;
        const label = t(`run.status.${step}`);
        const marker = status === 'FAILED' ? '×' : '!';
        const markerLabel = status === 'FAILED'
          ? t('run.failedAt', { stage: label })
          : t('run.needsHumanAt', { stage: label });

        return (
          <div key={step} className="flex shrink-0 items-center">
            <div
              data-testid={`step-${step}`}
              data-current={isCurrent ? 'true' : 'false'}
              className="flex flex-col items-center"
            >
              <div
                aria-label={isAbnormal ? markerLabel : undefined}
                className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium transition-fast ${
                  isAbnormal && status === 'FAILED' ? 'bg-status-critical text-white' :
                  isAbnormal ? 'bg-status-warning text-white' :
                  isCompleted ? 'bg-status-success text-white' :
                  isCurrent ? 'bg-accent text-white shadow-glow' :
                  'bg-surface-tertiary text-content-muted'
                }`}
              >
                {isAbnormal ? marker : isCompleted ? '✓' : index + 1}
              </div>
              <span className={`mt-1.5 whitespace-nowrap text-[10px] ${
                isCurrent ? 'font-medium text-accent' : 'text-content-muted'
              }`}>
                {label}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div className={`mx-0.5 h-0.5 w-6 ${
                isCompleted ? 'bg-status-success' : 'bg-border-subtle'
              }`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 5: Add stepper translations**

Add under `run.status` in `frontend/src/i18n/en.json`:

```json
"RISK_ASSESSMENT": "Risk Assessment",
"NEEDS_HUMAN": "Needs Human Intervention"
```

Add under `run`:

```json
"failedAt": "Failed at {{stage}}",
"needsHumanAt": "Needs human intervention at {{stage}}"
```

Add equivalent Chinese labels:

```json
"RISK_ASSESSMENT": "风险评估",
"NEEDS_HUMAN": "需要人工接管"
```

```json
"failedAt": "在{{stage}}失败",
"needsHumanAt": "在{{stage}}需要人工接管"
```

- [ ] **Step 6: Run stepper tests and frontend build**

Run:

```bash
cd frontend
npx vitest run src/components/RunStepper.test.tsx
npm run build
```

Expected: test PASS; build PASS and generated CSS includes the restored custom utilities.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/index.css frontend/src/components/RunStepper.tsx \
  frontend/src/components/RunStepper.test.tsx frontend/src/i18n/en.json \
  frontend/src/i18n/zh-CN.json
git commit -m "frontend: render reliable run stepper stages"
```

---

### Task 10: Show Collection Outcomes And Terminal Reasons In Run Detail

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/services/runs.ts`
- Modify: `frontend/src/services/runs.test.ts`
- Modify: `frontend/src/services/runDetailSync.ts`
- Modify: `frontend/src/services/runDetailSync.test.ts`
- Create: `frontend/src/components/EvidenceCollectionStatusPanel.tsx`
- Create: `frontend/src/components/EvidenceCollectionStatusPanel.test.tsx`
- Modify: `frontend/src/pages/RunDetailPage.tsx`
- Modify: `frontend/src/pages/RunDetailPage.test.tsx`
- Modify: `frontend/src/i18n/en.json`
- Modify: `frontend/src/i18n/zh-CN.json`

- [ ] **Step 1: Extend frontend contracts**

Add to `frontend/src/types/index.ts`:

```ts
export interface TerminalReason {
  code: string;
  stage?: string;
  message?: string;
  failed_tools?: string[];
  missing_evidence_categories?: string[];
}

export type EvidenceCollectionStatus =
  | 'SUCCESS_USABLE'
  | 'SUCCESS_EMPTY'
  | 'FAILED_CONFIG'
  | 'FAILED_RUNTIME';

export interface EvidenceCollectionResult {
  tool_name: string;
  category: string;
  params: Record<string, unknown>;
  status: EvidenceCollectionStatus;
  evidence_id?: string;
  error?: string;
  latency_ms: number;
  collected_at: string;
}
```

Extend `RunDetail`:

```ts
  halted_at_node?: string;
  terminal_reason?: TerminalReason;
```

Extend `ActionSpec`:

```ts
  supporting_evidence_ids?: string[];
```

- [ ] **Step 2: Write failing service and sync tests**

Append to `frontend/src/services/runs.test.ts`:

```ts
it('fetches evidence collection outcomes', async () => {
  vi.mocked(api.get).mockResolvedValue([]);

  await runs.getRunEvidenceCollectionResults('run-1');

  expect(api.get).toHaveBeenCalledWith('/incidents/runs/run-1/evidence/collection-results');
});
```

Append to `frontend/src/services/runDetailSync.test.ts`:

```ts
it('stops immediately when human intervention is terminal', () => {
  const { controller, states } = setup();
  controller.start();

  controller.observeRun({ ...baseRun, status: 'NEEDS_HUMAN' });

  expect(FakeEventSource.instances[0].closed).toBe(true);
  expect(states.at(-1)).toBe('stopped');
  expect(vi.getTimerCount()).toBe(0);
});
```

- [ ] **Step 3: Add service method and terminal sync state**

Import `EvidenceCollectionResult` in `frontend/src/services/runs.ts`, then add:

```ts
  getRunEvidenceCollectionResults: (runId: string) =>
    api.get<EvidenceCollectionResult[]>(`/incidents/runs/${runId}/evidence/collection-results`),
```

In `frontend/src/services/runDetailSync.ts`, change:

```ts
const STOPPED_STATUSES = new Set(['COMPLETED', 'FAILED', 'NEEDS_HUMAN']);
```

- [ ] **Step 4: Create collection status panel and tests**

Create `frontend/src/components/EvidenceCollectionStatusPanel.tsx`:

```tsx
import type { EvidenceCollectionResult } from '../types';
import { useI18n } from '../i18n';

interface Props {
  results: EvidenceCollectionResult[];
}

export function EvidenceCollectionStatusPanel({ results }: Props) {
  const { t } = useI18n();
  if (results.length === 0) return null;

  return (
    <div className="card mb-4 overflow-hidden">
      <div className="bg-surface-tertiary px-4 py-2.5 font-medium">
        {t('evidence.collectionResults')}
      </div>
      <ul className="divide-y divide-border-subtle">
        {results.map((result, index) => (
          <li key={`${result.tool_name}-${result.collected_at}-${index}`} className="px-4 py-3 text-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <code>{result.tool_name}</code>
              <span className={`rounded px-2 py-0.5 text-xs ${
                result.status === 'SUCCESS_USABLE' ? 'status-success' :
                result.status === 'SUCCESS_EMPTY' ? 'status-warning' :
                'status-critical'
              }`}>
                {t(`evidence.status.${result.status}`)}
              </span>
            </div>
            {result.error && <p className="mt-2 break-words text-content-muted">{result.error}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

Create `frontend/src/components/EvidenceCollectionStatusPanel.test.tsx`:

```tsx
import { expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import { EvidenceCollectionStatusPanel } from './EvidenceCollectionStatusPanel';
import { renderWithProviders } from '../test/render';

it('renders empty and failed collection outcomes', () => {
  renderWithProviders(
    <EvidenceCollectionStatusPanel
      results={[
        {
          tool_name: 'query_metrics',
          category: 'metrics',
          params: {},
          status: 'SUCCESS_EMPTY',
          latency_ms: 5,
          collected_at: '2026-06-02T10:00:00',
        },
        {
          tool_name: 'query_runbook',
          category: 'runbook',
          params: {},
          status: 'FAILED_CONFIG',
          error: 'real adapter is not configured',
          latency_ms: 6,
          collected_at: '2026-06-02T10:00:01',
        },
      ]}
    />,
  );

  expect(screen.getByText('query_metrics')).toBeInTheDocument();
  expect(screen.getByText('Empty result')).toBeInTheDocument();
  expect(screen.getByText('Configuration failed')).toBeInTheDocument();
});
```

- [ ] **Step 5: Integrate run-detail presentation**

In `frontend/src/pages/RunDetailPage.tsx`:

1. Treat human handoff as a warning in `getStatusClass`:

```tsx
    case 'WAITING_HUMAN':
    case 'NEEDS_HUMAN':
      return 'status-warning';
```

2. Add `EvidenceCollectionResult` import and state:

```tsx
  const [collectionResults, setCollectionResults] = useState<EvidenceCollectionResult[]>([]);
```

3. Reset it during run change:

```tsx
    setCollectionResults([]);
```

4. Fetch it with evidence artifacts and update the destructuring assignment:

```tsx
      const [evidenceResult, collectionResult, diagnosisResult, remediationResult, traceResult] =
        await Promise.allSettled([
          runs.getRunEvidence(id),
          runs.getRunEvidenceCollectionResults(id),
          runs.getRunDiagnosis(id),
          runs.getRunRemediation(id),
          runs.getRunTrace(id),
        ]);
```

5. Store fulfilled results:

```tsx
      if (collectionResult.status === 'fulfilled') {
        setCollectionResults(collectionResult.value);
      }
```

6. Pass node context:

```tsx
        <RunStepper
          status={run.status}
          currentNode={run.current_node}
          haltedAtNode={run.halted_at_node}
        />
```

7. Before `<EvidencePanel evidence={evidence} />`, render:

```tsx
                <EvidenceCollectionStatusPanel results={collectionResults} />
```

8. In the right column, render a handoff card:

```tsx
          {run.status === 'NEEDS_HUMAN' && run.terminal_reason && (
            <div className="card p-4 sm:p-6 status-warning">
              <h3 className="mb-2 text-lg font-semibold">{t('run.needsHuman')}</h3>
              <p className="break-words text-sm">
                {run.terminal_reason.message || run.terminal_reason.code}
              </p>
            </div>
          )}
```

- [ ] **Step 6: Add translations**

Add:

```json
"needsHuman": "Needs human intervention"
```

and:

```json
"needsHuman": "需要人工接管"
```

Under `evidence`, add English:

```json
"collectionResults": "Collection results",
"status": {
  "SUCCESS_USABLE": "Usable",
  "SUCCESS_EMPTY": "Empty result",
  "FAILED_CONFIG": "Configuration failed",
  "FAILED_RUNTIME": "Runtime failed"
}
```

Add equivalent Chinese:

```json
"collectionResults": "采集结果",
"status": {
  "SUCCESS_USABLE": "有效",
  "SUCCESS_EMPTY": "结果为空",
  "FAILED_CONFIG": "配置失败",
  "FAILED_RUNTIME": "运行失败"
}
```

- [ ] **Step 7: Update page mocks and run focused frontend tests**

Add `getRunEvidenceCollectionResults: vi.fn()` to the mocked `runs` service in
`frontend/src/pages/RunDetailPage.test.tsx`, default it in `beforeEach`:

```tsx
    vi.mocked(runsModule.runs.getRunEvidenceCollectionResults).mockResolvedValue([]);
```

Add this page test:

```tsx
  it('shows the terminal reason when automation needs a human', async () => {
    vi.mocked(runsModule.runs.getRun).mockResolvedValue({
      ...mockRun,
      status: 'NEEDS_HUMAN',
      halted_at_node: 'node_risk_gate',
      terminal_reason: {
        code: 'AUTOMATION_CAPABILITY_UNAVAILABLE',
        message: 'execute_action real adapter is not configured',
      },
    } as any);

    renderPage();

    expect(await screen.findByText('execute_action real adapter is not configured')).toBeInTheDocument();
  });
```

Run:

```bash
cd frontend
npx vitest run src/services/runs.test.ts src/services/runDetailSync.test.ts \
  src/components/EvidenceCollectionStatusPanel.test.tsx src/pages/RunDetailPage.test.tsx
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/services/runs.ts \
  frontend/src/services/runs.test.ts frontend/src/services/runDetailSync.ts \
  frontend/src/services/runDetailSync.test.ts \
  frontend/src/components/EvidenceCollectionStatusPanel.tsx \
  frontend/src/components/EvidenceCollectionStatusPanel.test.tsx \
  frontend/src/pages/RunDetailPage.tsx frontend/src/pages/RunDetailPage.test.tsx \
  frontend/src/i18n/en.json frontend/src/i18n/zh-CN.json
git commit -m "frontend: display human handoff evidence context"
```

---

### Task 11: Render Downgraded RCA Details

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/pages/RcaPage.tsx`
- Create: `frontend/src/pages/RcaPage.test.tsx`
- Modify: `frontend/src/i18n/en.json`
- Modify: `frontend/src/i18n/zh-CN.json`

- [ ] **Step 1: Extend RCA type**

Extend `RcaReport` in `frontend/src/types/index.ts`:

```ts
  root_cause_status?: 'CONFIRMED' | 'SUSPECTED' | 'UNKNOWN';
  candidate_hypotheses?: Array<{ hypothesis: string; confidence: number }>;
  automation_outcome?: {
    status: string;
    reason?: TerminalReason;
    executed_action_ids?: string[];
  };
  manual_next_steps?: string[];
```

- [ ] **Step 2: Write failing RCA-page test**

Create `frontend/src/pages/RcaPage.test.tsx`:

```tsx
import { describe, expect, it, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { RcaPage } from './RcaPage';
import { renderWithProviders } from '../test/render';

vi.mock('../services/runs', () => ({
  runs: {
    getRunRca: vi.fn().mockResolvedValue({
      run_id: 'run-1',
      report_markdown: '# RCA',
      root_cause: '根因尚未确认',
      resolution: '自动化流程已停止，需要人工接管',
      prevention_items: [],
      confirmed_by_human: false,
      root_cause_status: 'UNKNOWN',
      candidate_hypotheses: [{ hypothesis: 'recent deployment', confidence: 0.5 }],
      automation_outcome: {
        status: 'NEEDS_HUMAN',
        reason: { code: 'EVIDENCE_EXHAUSTED', message: 'Evidence remained insufficient' },
      },
      manual_next_steps: ['检查缺失证据类别：deployments'],
    }),
  },
}));

describe('RcaPage', () => {
  it('renders downgraded certainty and manual next steps', async () => {
    renderWithProviders(
      <MemoryRouter initialEntries={['/runs/run-1/rca']}>
        <Routes>
          <Route path="/runs/:id/rca" element={<RcaPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Unknown')).toBeInTheDocument();
    expect(screen.getByText('recent deployment')).toBeInTheDocument();
    expect(screen.getByText('检查缺失证据类别：deployments')).toBeInTheDocument();
    expect(screen.getByText('Evidence remained insufficient')).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Render RCA reliability sections**

In `frontend/src/pages/RcaPage.tsx`, after root cause, add:

```tsx
            {rca.root_cause_status && (
              <div>
                <h3 className="mb-2 text-sm font-medium uppercase tracking-wider text-content-muted">
                  {t('rca.rootCauseStatus')}
                </h3>
                <span className="rounded px-2 py-0.5 text-xs status-warning">
                  {t(`rca.status.${rca.root_cause_status}`)}
                </span>
              </div>
            )}
```

After resolution, add:

```tsx
            {rca.candidate_hypotheses?.length ? (
              <div>
                <h3 className="mb-2 text-sm font-medium uppercase tracking-wider text-content-muted">
                  {t('rca.candidates')}
                </h3>
                <ul className="list-inside list-disc space-y-1">
                  {rca.candidate_hypotheses.map((candidate) => (
                    <li key={candidate.hypothesis} className="break-words text-content-primary">
                      {candidate.hypothesis} ({Math.round(candidate.confidence * 100)}%)
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {rca.automation_outcome?.reason?.message && (
              <div>
                <h3 className="mb-2 text-sm font-medium uppercase tracking-wider text-content-muted">
                  {t('rca.automationOutcome')}
                </h3>
                <p className="break-words text-content-primary">
                  {rca.automation_outcome.reason.message}
                </p>
              </div>
            )}

            {rca.manual_next_steps?.length ? (
              <div>
                <h3 className="mb-2 text-sm font-medium uppercase tracking-wider text-content-muted">
                  {t('rca.manualNextSteps')}
                </h3>
                <ul className="list-inside list-disc space-y-1">
                  {rca.manual_next_steps.map((item) => (
                    <li key={item} className="break-words text-content-primary">{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}
```

- [ ] **Step 4: Add RCA translations**

Add English:

```json
"rootCauseStatus": "Root cause status",
"candidates": "Candidate hypotheses",
"automationOutcome": "Automation outcome",
"manualNextSteps": "Manual next steps",
"status": {
  "CONFIRMED": "Confirmed",
  "SUSPECTED": "Suspected",
  "UNKNOWN": "Unknown"
}
```

Add Chinese:

```json
"rootCauseStatus": "根因状态",
"candidates": "候选假设",
"automationOutcome": "自动化结果",
"manualNextSteps": "人工下一步",
"status": {
  "CONFIRMED": "已确认",
  "SUSPECTED": "疑似",
  "UNKNOWN": "未知"
}
```

- [ ] **Step 5: Run RCA page test**

Run:

```bash
cd frontend
npx vitest run src/pages/RcaPage.test.tsx
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/pages/RcaPage.tsx \
  frontend/src/pages/RcaPage.test.tsx frontend/src/i18n/en.json frontend/src/i18n/zh-CN.json
git commit -m "frontend: render downgraded rca details"
```

---

### Task 12: Run Full Regression And Verify Acceptance Scenarios

**Files:**
- Modify only when a regression exposes a defect in the files above.

- [ ] **Step 1: Run backend regression**

Run:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/ -x -q
```

Expected: PASS.

- [ ] **Step 2: Run frontend regression and build**

Run:

```bash
cd frontend
npx vitest run
npm run build
```

Expected: PASS.

- [ ] **Step 3: Verify the local API is healthy**

Run:

```bash
curl -s http://127.0.0.1:8000/healthz
```

Expected: HTTP 200 health payload. If the backend is not running, start it with:

```bash
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

- [ ] **Step 4: Verify real-mode missing capability handoff**

With `TOOL_ADAPTER_MODE=real`, create a manual run and inspect it after background processing:

```bash
RUN_ID="$(
  curl -s -X POST http://127.0.0.1:8000/incidents/runs \
    -H 'Content-Type: application/json' \
    -d '{"ticket":{"ticket_id":"INC-RELIABILITY-REAL","title":"api 5xx elevated","description":"verify fail-closed capability handoff","service":"api","env":"prod","severity":"P2","source":"manual"}}' |
    python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'
)"
sleep 5
for _ in {1..30}; do
  STATUS="$(curl -s "http://127.0.0.1:8000/incidents/runs/$RUN_ID" |
    python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])')"
  case "$STATUS" in
    COMPLETED|FAILED|NEEDS_HUMAN|WAITING_HUMAN) break ;;
  esac
  sleep 2
done
curl -s "http://127.0.0.1:8000/incidents/runs/$RUN_ID" | python3 -m json.tool
curl -s http://127.0.0.1:8000/approvals/pending | python3 -m json.tool
curl -s "http://127.0.0.1:8000/incidents/runs/$RUN_ID/rca" | python3 -m json.tool
```

Expected:

```text
status = NEEDS_HUMAN
halted_at_node = node_risk_gate
terminal_reason.code = AUTOMATION_CAPABILITY_UNAVAILABLE
no pending approval for this run
rca.root_cause_status is UNKNOWN or SUSPECTED
```

- [ ] **Step 5: Verify evidence exhaustion handoff**

Run the focused evidence-exhaustion tests:

```bash
cd backend && source venv/bin/activate
python -m pytest app/tests/test_evidence_quality.py \
  app/tests/test_resume_and_evidence.py::test_critic_hands_off_after_evidence_loop_limit -q
```

Expected:

```text
empty payloads are SUCCESS_EMPTY
configuration failures are FAILED_CONFIG
status = NEEDS_HUMAN after max evidence loops
terminal_reason.code = EVIDENCE_EXHAUSTED
```

- [ ] **Step 6: Verify approval pause and resume continuity**

Run the focused pause and resume tests:

```bash
cd backend && source venv/bin/activate
python -m pytest \
  app/tests/test_resume_and_evidence.py::test_graph_runner_marks_waiting_human_as_paused \
  app/tests/test_resume_and_evidence.py::test_approval_runtime_uses_pause_checkpoint_without_step_regression \
  -q
```

Expected:

```text
WAITING_HUMAN has completed_at = null
event stream contains RUN_PAUSED
resumed step_count is greater than or equal to paused step_count
```

- [ ] **Step 7: Verify tool audits**

Run:

```bash
cd backend
sqlite3 opspilot.db "
SELECT tool_name, adapter_mode, success, error_message
FROM incident_tool_audits
ORDER BY created_at DESC
LIMIT 20;
"
```

Expected: successful, empty-result, validation-failed, and missing-adapter calls are represented.

- [ ] **Step 8: Verify the frontend visually**

Run:

```bash
cd frontend
npm run dev
```

Open the affected run detail page in the Browser plugin and inspect:

```text
ten colored step circles and connectors are visible
risk assessment and verifying stages exist
NEEDS_HUMAN stops at risk assessment or the actual halt node with an orange !
FAILED stops at the actual halt node with a red ×
terminal reason is visible
evidence collection outcomes list empty and failed tools
RCA shows certainty and manual next steps
```

- [ ] **Step 9: Check the diff and commit regression-only fixes**

Run:

```bash
git status --short
git diff --stat
```

Expected: only intentional reliability-closure files are modified by this implementation. If a
regression required an adjustment, stage exactly the files changed for that adjustment and commit
them with `git commit -m "test: close incident reliability regressions"`.

---

## Coverage Matrix

| Requirement | Task |
| --- | --- |
| `NEEDS_HUMAN` terminal status | Task 1 |
| Halt node and terminal reason persistence | Tasks 1, 6, 8 |
| Structured evidence outcomes | Tasks 1, 2, 3 |
| Empty evidence excluded from quality | Tasks 2, 3 |
| Collection failures retained | Tasks 2, 3, 10 |
| Loop exhaustion hands off to humans | Task 3 |
| Remediation requires usable evidence IDs | Task 3 |
| Read-only capability preflight | Tasks 4, 5 |
| Missing execute adapter prevents approval | Task 5 |
| Missing precondition-tool capability prevents approval | Task 5 |
| Pause checkpoint resume continuity | Task 5 |
| Terminal `NEEDS_HUMAN` cannot use the manual resume endpoint | Task 8 |
| `WAITING_HUMAN` emits `RUN_PAUSED` without completion timestamp | Task 6 |
| Durable sanitized audits | Task 4 |
| Downgraded RCA certainty and manual steps | Tasks 7, 8, 11 |
| Ten frontend display stages | Task 9 |
| Tailwind v4 custom token generation | Task 9 |
| Actual halt marker for handoff and failure | Task 9 |
| Existing realtime controller stops on `NEEDS_HUMAN` | Task 10 |
| Full regression and browser verification | Task 12 |
