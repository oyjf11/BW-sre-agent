# OpsPilot Phase 8 离线评测 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 OpsPilot 建立离线评测能力——先让 diagnose 节点输出封闭枚举 `incident_type`（生产改动），再搭建用 fixture 固定证据、打真实 DeepSeek 的两层评测框架，量化诊断质量。

**Architecture:** 分两阶段交付。Phase 8.0 收敛根因标签空间到 `IncidentType` 枚举并改造 diagnose 输出结构化字段（地基）。Phase 8.1 在其上搭评测框架：复刻项目已有的 `ContextVar` 模式注入 fixture（gateway 短路）、`GraphExecutor` 双实现（Direct 扎实 / Runner 骨架）、确定性 scorer + stdlib 指标聚合 + JSON/Markdown 报告 + CLI 三模式。

**Tech Stack:** Python 3 / Pydantic v2 / LangGraph / pytest（框架单测 mock LLM 进 CI）/ argparse CLI（真实 DeepSeek 评测手动离线跑）。

---

## 关键约定（实现前必读）

- **运行测试**：`cd backend && source venv/bin/activate && python -m pytest app/tests/<file>::<test> -v`
- **全量测试**：`cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q`
- **commit 格式**：`backend: xxx`，结尾附 `Co-Authored-By` 行
- **Pydantic/dict 二义性**：graph state 中对象可能是 Pydantic 模型也可能是 dict（checkpoint 反序列化后）。所有读取必须 `x.attr if hasattr(x, "attr") else x.get("attr", default)` 兼容。
- **autouse mock adapter**：`app/tests/conftest.py` 强制 `TOOL_ADAPTER_MODE=mock`，所有单测继承。
- **fixture 缺失策略（已决策）**：评测时未在 `tool_fixtures` 提供的**只读工具**返回受控空结果 `{}`（`success=True`），graph 照常推进，**不** fail-loud。写类工具（`write_*`）和 `execute_action` 返回成功桩。证据仍 100% 确定（空就是空，绝不回退 mock 随机数据）。

---

## 文件结构

**Phase 8.0（生产改动）**

| 文件 | 责任 |
|------|------|
| `backend/app/models/incident_type.py`（新） | `IncidentType` 枚举（11 个一级类型，唯一标签空间来源） |
| `backend/app/models/root_cause.py`（改） | `RootCauseCandidate` 新增 `incident_type` 字段（默认 `unknown`，向后兼容） |
| `backend/app/graph/nodes/__init__.py`（改） | diagnose 输出/解析/排序/fallback 改造；triage/planner magic-string 引用收敛 |

**Phase 8.1（评测框架，新目录 `backend/app/evals/`）**

| 文件 | 责任 |
|------|------|
| `backend/app/graph/builder.py`（改） | `create_incident_graph(checkpointer=None)`，默认 None 行为不变 |
| `backend/app/tools/gateway.py`（改） | `call_tool` 开头加 fixture 短路读取点 |
| `backend/app/evals/__init__.py`（新） | 包标记 |
| `backend/app/evals/fixture_context.py`（新） | `ContextVar` + `fixture_scope()` 注入 |
| `backend/app/evals/case_loader.py`（新） | 读取 + 校验 dataset JSON |
| `backend/app/evals/scorer.py`（新） | 单 case 确定性评分 → `CaseResult` |
| `backend/app/evals/metrics.py`（新） | 聚合指标（纯 stdlib） |
| `backend/app/evals/report.py`（新） | JSON + Markdown 报告 |
| `backend/app/evals/executors.py`（新） | `GraphExecutor` Protocol + `DirectGraphExecutor`（扎实）+ `RunnerGraphExecutor`（骨架） |
| `backend/app/evals/runner.py`（新） | 编排：加载 → fixture_scope → execute → score → repeat → 聚合 |
| `backend/app/evals/replay_runner.py`（新） | CLI 入口（`--mode/--repeat/--dataset/--output`） |
| `backend/app/evals/datasets/*.json`（新） | 10-12 个 case，每类至少 1 个 + 风险/审批场景 |

**测试文件（mock LLM，进 CI）**

| 文件 | 覆盖 |
|------|------|
| `backend/app/tests/test_incident_type.py` | 枚举完整性 + `RootCauseCandidate.incident_type` 默认值/兼容 |
| `backend/app/tests/test_diagnose_structured.py` | diagnose 枚举内/非法降级/降序/fallback unknown |
| `backend/app/tests/test_eval_fixture_context.py` | `fixture_scope` 短路、退出恢复、并发隔离、空结果回退 |
| `backend/app/tests/test_eval_case_loader.py` | 合法/非法 schema 加载 |
| `backend/app/tests/test_eval_scorer.py` | Top1/Top3/risk/status 匹配 |
| `backend/app/tests/test_eval_metrics.py` | accuracy/macro-F1/混淆矩阵/per-class recall/unknown rate |
| `backend/app/tests/test_eval_executors.py` | `DirectGraphExecutor` mock LLM 端到端 + fixture 注入链路 |

---

# Phase 8.0：结构化根因输出

## Task 1: IncidentType 枚举

**Files:**
- Create: `backend/app/models/incident_type.py`
- Test: `backend/app/tests/test_incident_type.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_incident_type.py`：

```python
"""Tests for IncidentType enum (closed label space for eval)."""
from app.models.incident_type import IncidentType


class TestIncidentType:
    def test_has_eleven_types(self):
        assert len(list(IncidentType)) == 11

    def test_str_enum_values_match_names(self):
        # str-Enum: value equals the snake_case string used everywhere
        assert IncidentType.deployment_regression.value == "deployment_regression"
        assert IncidentType.unknown.value == "unknown"
        assert IncidentType.other.value == "other"

    def test_is_str_subclass(self):
        # Must be a str subclass so `== "deployment_regression"` works directly
        assert isinstance(IncidentType.deployment_regression, str)
        assert IncidentType.resource_exhaustion == "resource_exhaustion"

    def test_triage_legacy_values_all_present(self):
        # The 5 magic-strings triage already emits must round-trip with zero loss
        for legacy in (
            "deployment_regression",
            "resource_exhaustion",
            "dependency_failure",
            "security_incident",
            "service_degradation",
        ):
            assert IncidentType(legacy).value == legacy

    def test_membership_check_by_value(self):
        values = {t.value for t in IncidentType}
        assert "database_failure" in values
        assert "network_failure" in values
        assert "traffic_anomaly" in values
        assert "configuration_error" in values
        assert "made_up_type" not in values
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_incident_type.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app.models.incident_type'`）

- [ ] **Step 3: 实现枚举**

创建 `backend/app/models/incident_type.py`：

```python
"""Closed incident-type label space shared by triage, diagnose, and offline eval.

This enum is the single source of truth for root-cause classification. The eval
scorer compares against these values by enum equality (no keyword/LLM guessing),
so the label space must stay closed and mutually exclusive.

Extending: add one line here + at least one dataset case for the new type.
The scorer/metrics compare dynamically by value and need no code change.
"""
from enum import Enum


class IncidentType(str, Enum):
    deployment_regression = "deployment_regression"  # 发布变更(代码/配置/镜像/依赖版本)直接引入
    configuration_error = "configuration_error"      # 非发布的配置错误(手工改动/环境漂移/配置中心)
    resource_exhaustion = "resource_exhaustion"      # CPU/内存/连接池/磁盘耗尽
    dependency_failure = "dependency_failure"        # 下游/第三方依赖不可用
    database_failure = "database_failure"            # DB 层故障(慢查询/锁/连接/主从)
    network_failure = "network_failure"              # 网络/DNS/LB 链路
    traffic_anomaly = "traffic_anomaly"              # 流量突增/异常请求模式
    security_incident = "security_incident"          # 安全事件(入侵/漏洞利用/异常访问)
    service_degradation = "service_degradation"      # 服务自身退化(非以上明确归因)
    unknown = "unknown"                              # 证据不足，无法判断
    other = "other"                                  # 已判因但超出标签体系
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_incident_type.py -v`
Expected: PASS（5 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/models/incident_type.py backend/app/tests/test_incident_type.py
git commit -m "backend: add IncidentType closed enum for root-cause label space

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: RootCauseCandidate 新增 incident_type 字段

**Files:**
- Modify: `backend/app/models/root_cause.py`
- Test: `backend/app/tests/test_incident_type.py`（追加）

- [ ] **Step 1: 追加失败测试**

在 `backend/app/tests/test_incident_type.py` 末尾追加：

```python
class TestRootCauseCandidateIncidentType:
    def test_defaults_to_unknown(self):
        from app.models.root_cause import RootCauseCandidate

        c = RootCauseCandidate(
            candidate_id="c1", hypothesis="something", confidence=0.5
        )
        assert c.incident_type == IncidentType.unknown

    def test_accepts_explicit_type(self):
        from app.models.root_cause import RootCauseCandidate

        c = RootCauseCandidate(
            candidate_id="c1",
            hypothesis="bad deploy",
            confidence=0.9,
            incident_type=IncidentType.deployment_regression,
        )
        assert c.incident_type == IncidentType.deployment_regression

    def test_backward_compat_old_dict_without_field(self):
        # Old checkpoints serialized before this field existed must still load
        from app.models.root_cause import RootCauseCandidate

        old = {"candidate_id": "c1", "hypothesis": "x", "confidence": 0.3}
        c = RootCauseCandidate(**old)
        assert c.incident_type == IncidentType.unknown

    def test_accepts_string_value(self):
        # LLM-parsed string should coerce into the enum
        from app.models.root_cause import RootCauseCandidate

        c = RootCauseCandidate(
            candidate_id="c1",
            hypothesis="db lock",
            confidence=0.7,
            incident_type="database_failure",
        )
        assert c.incident_type == IncidentType.database_failure
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_incident_type.py::TestRootCauseCandidateIncidentType -v`
Expected: FAIL（`incident_type` 字段不存在 → AttributeError / ValidationError）

- [ ] **Step 3: 加字段**

修改 `backend/app/models/root_cause.py`，在 import 区和 `next_checks` 字段后增加：

```python
from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional  # 引入列表和可选类型

from app.models.incident_type import IncidentType


class RootCauseCandidate(BaseModel):
    """
    根因候选模型，表示某个可能的根因假设，
    用于在诊断过程中进行打分和筛选。
    """

    candidate_id: str = Field(
        ..., description="Unique candidate identifier"
    )  # 根因候选唯一标识
    hypothesis: str = Field(
        ..., description="Root cause hypothesis"
    )  # 根因假设内容
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score"
    )  # 对该根因假设的置信度（0~1）
    incident_type: IncidentType = Field(
        default=IncidentType.unknown,
        description="Closed-enum incident classification (primary eval metric)",
    )  # 封闭枚举根因分类（评测主指标，默认 unknown 向后兼容）
    supporting_evidence_ids: List[str] = Field(
        default_factory=list, description="Evidence supporting this hypothesis"
    )  # 支持该假设的证据 ID 列表
    contradicting_evidence_ids: List[str] = Field(
        default_factory=list, description="Evidence contradicting this hypothesis"
    )  # 与该假设相矛盾的证据 ID 列表
    next_checks: List[str] = Field(
        default_factory=list, description="Suggested verification steps"
    )  # 用于验证该假设的后续检查建议
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_incident_type.py -v`
Expected: PASS（全部）

并跑 serde 回归（确认序列化不报错）：
Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_serde.py -q`
Expected: PASS

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/models/root_cause.py backend/app/tests/test_incident_type.py
git commit -m "backend: add incident_type field to RootCauseCandidate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: 改造 diagnose（输出/解析/排序/fallback）

**Files:**
- Modify: `backend/app/graph/nodes/__init__.py:864-1001`（`diagnose_node`）
- Test: `backend/app/tests/test_diagnose_structured.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_diagnose_structured.py`：

```python
"""Tests for structured incident_type output from diagnose_node (mock LLM)."""
import pytest

from app.graph.nodes import diagnose_node
from app.graph.state import RunStatus
from app.models.incident import IncidentTicket
from app.models.incident_type import IncidentType
from app.llm_client import llm_client


def _state():
    ticket = IncidentTicket(
        ticket_id="t1",
        title="5xx after release",
        description="errors spiked post deploy",
        service="payment-service",
        env="staging",
        severity="P2",
        source="manual",
    )
    return {
        "run_id": "diag-1",
        "ticket": ticket,
        "evidence_items": [],
        "root_cause_candidates": [],
    }


def test_incident_type_always_in_enum(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          {"incident_type": "deployment_regression", "hypothesis": "bad deploy",
           "confidence": 0.8, "next_checks": ["rollback"]}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    cands = out["root_cause_candidates"]
    assert len(cands) >= 1
    for c in cands:
        assert isinstance(c.incident_type, IncidentType)
    assert cands[0].incident_type == IncidentType.deployment_regression


def test_illegal_type_downgrades_to_other(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          {"incident_type": "aliens_did_it", "hypothesis": "ufo",
           "confidence": 0.9, "next_checks": []}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    assert out["root_cause_candidates"][0].incident_type == IncidentType.other


def test_candidates_sorted_by_confidence_desc(monkeypatch):
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[
          {"incident_type": "resource_exhaustion", "hypothesis": "low", "confidence": 0.3, "next_checks": []},
          {"incident_type": "deployment_regression", "hypothesis": "high", "confidence": 0.9, "next_checks": []},
          {"incident_type": "dependency_failure", "hypothesis": "mid", "confidence": 0.6, "next_checks": []}
        ]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    confs = [c.confidence for c in out["root_cause_candidates"]]
    assert confs == sorted(confs, reverse=True)
    assert out["root_cause_candidates"][0].incident_type == IncidentType.deployment_regression


def test_llm_failure_falls_back_to_unknown(monkeypatch):
    def boom(prompt, system_prompt=None, temperature=0.7):
        raise RuntimeError("LLM down")

    monkeypatch.setattr(llm_client, "complete_sync", boom)
    out = diagnose_node(_state())
    cands = out["root_cause_candidates"]
    assert len(cands) >= 1
    assert all(c.incident_type == IncidentType.unknown for c in cands)
    assert out["status"] == RunStatus.DIAGNOSED


def test_missing_type_defaults_to_unknown(monkeypatch):
    # LLM returns candidate WITHOUT incident_type key
    def fake(prompt, system_prompt=None, temperature=0.7):
        return """[{"hypothesis": "no type given", "confidence": 0.5, "next_checks": []}]"""

    monkeypatch.setattr(llm_client, "complete_sync", fake)
    out = diagnose_node(_state())
    assert out["root_cause_candidates"][0].incident_type == IncidentType.unknown
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_diagnose_structured.py -v`
Expected: FAIL（diagnose 尚未解析 `incident_type`，candidates 默认全 unknown → 多条用例不通过；排序未实现）

- [ ] **Step 3: 改造 diagnose_node**

修改 `backend/app/graph/nodes/__init__.py` 的 `diagnose_node`。

3a. 在文件顶部 import 区（约第 11 行，`from app.models.root_cause import RootCauseCandidate` 下方）增加：

```python
from app.models.incident_type import IncidentType
```

3b. 把 `diagnose_node` 内的 LLM prompt（约 911-933 行）替换为要求枚举输出的版本：

```python
    # LLM prompt for root cause analysis
    incident_type_values = ", ".join(t.value for t in IncidentType)
    diagnose_prompt = f"""Analyze this incident and provide root cause candidates.

## Incident
- Title: {ticket_title}
- Description: {ticket_desc}
- Service: {service}
- Environment: {env}
- Incident Type (from triage, may be revised): {incident_type}

## Collected Evidence
{evidence_text}

Classify each candidate's root cause into EXACTLY ONE of these incident_type values:
{incident_type_values}

Rules for incident_type:
- Pick the single most specific matching type.
- Use "unknown" ONLY when evidence is insufficient to classify.
- Use "other" when you DID determine a cause but it fits none of the listed types.

Provide 2-3 root cause candidates in JSON format:
[
  {{
    "incident_type": "one value from the list above",
    "hypothesis": "brief description of possible root cause",
    "confidence": 0.0-1.0,
    "next_checks": ["action to verify", "another check"]
  }}
]

Respond in JSON format only."""
```

3c. 把 LLM 解析块（约 951-973 行，`candidates = []` 到第一个 `except Exception: pass`）替换为带枚举校验的版本：

```python
    candidates = []

    # Parse LLM response
    if llm_response and llm_response != "fallback_response":
        try:
            import re

            json_match = re.search(r"\[[\s\S]*\]", llm_response)
            if json_match:
                llm_candidates = json.loads(json_match.group())
                if isinstance(llm_candidates, list):
                    for c in llm_candidates[:3]:
                        raw_type = c.get("incident_type")
                        incident_type = _coerce_incident_type(raw_type)
                        candidate = RootCauseCandidate(
                            candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
                            hypothesis=c.get("hypothesis", "Unknown"),
                            confidence=c.get("confidence", 0.5),
                            incident_type=incident_type,
                            supporting_evidence_ids=[],
                            contradicting_evidence_ids=[],
                            next_checks=c.get("next_checks", []),
                        )
                        candidates.append(candidate)
        except Exception:
            pass
```

3d. 把 fallback 块（约 976-995 行，两个硬编码候选）替换为带 `incident_type=IncidentType.unknown` 的版本：

```python
    # Fallback if LLM failed → unknown (reflects degraded quality, not a fake hit)
    if not candidates:
        candidate = RootCauseCandidate(
            candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
            hypothesis="High resource usage causing degradation",
            confidence=0.7,
            incident_type=IncidentType.unknown,
            supporting_evidence_ids=[],
            contradicting_evidence_ids=[],
            next_checks=["Check metric thresholds", "Review scaling policies"],
        )
        candidates.append(candidate)

        candidate = RootCauseCandidate(
            candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
            hypothesis="Recent deployment may have introduced the issue",
            confidence=0.5,
            incident_type=IncidentType.unknown,
            supporting_evidence_ids=[],
            contradicting_evidence_ids=[],
            next_checks=["Check deployment logs", "Verify rollback"],
        )
        candidates.append(candidate)
```

3e. 在 `state["root_cause_candidates"] = candidates`（约 997 行）**之前**插入降序排序：

```python
    # Sort candidates by confidence DESC so [0] is the most-trusted candidate.
    # Eval Top1 metric, critic, and remediation all read [0].
    candidates.sort(
        key=lambda c: c.confidence if hasattr(c, "confidence") else 0.0,
        reverse=True,
    )

    state["root_cause_candidates"] = candidates
```

3f. 在 `diagnose_node` 函数**之前**（约 863 行，`def diagnose_node` 上方）新增枚举校验 helper：

```python
def _coerce_incident_type(raw: Any) -> "IncidentType":
    """Validate an LLM-provided incident_type into the closed enum.

    - Valid enum value → that member.
    - Missing / None → unknown (insufficient signal).
    - Non-empty but illegal → other (model decided a cause outside the taxonomy).
    """
    if raw is None or raw == "":
        return IncidentType.unknown
    try:
        return IncidentType(str(raw).strip())
    except ValueError:
        logger.warning("diagnose: illegal incident_type %r → downgraded to 'other'", raw)
        return IncidentType.other
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_diagnose_structured.py -v`
Expected: PASS（5 passed）

回归现有图集成测试（确认 diagnose 改造没破坏整图）：
Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_graph_integration.py -q`
Expected: PASS

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/graph/nodes/__init__.py backend/app/tests/test_diagnose_structured.py
git commit -m "backend: diagnose outputs structured incident_type with validation and sorting

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: triage / planner magic-string 引用收敛

**Files:**
- Modify: `backend/app/graph/nodes/__init__.py`（`_triage_by_rules`、`_triage_by_llm`、`_triage_fallback`、`planner_node`）
- Test: `backend/app/tests/test_diagnose_structured.py`（追加 triage 引用对齐回归）

> 仅做引用对齐（magic string → `IncidentType.X.value`），**不重写判断逻辑**，行为零变化。

- [ ] **Step 1: 追加回归测试**

在 `backend/app/tests/test_diagnose_structured.py` 末尾追加：

```python
class TestTriageReferenceAlignment:
    """triage still emits the same string values, now sourced from the enum."""

    def test_deploy_rule_emits_enum_value(self):
        from app.graph.nodes import _triage_by_rules

        r = _triage_by_rules("Release rollback failed", "", "P1", "svc", "prod")
        assert r is not None
        assert r.incident_type == IncidentType.deployment_regression.value

    def test_resource_rule_emits_enum_value(self):
        from app.graph.nodes import _triage_by_rules

        r = _triage_by_rules("OOM killed pod", "memory leak", "P2", "svc", "staging")
        assert r is not None
        assert r.incident_type == IncidentType.resource_exhaustion.value

    def test_dependency_rule_emits_enum_value(self):
        from app.graph.nodes import _triage_by_rules

        r = _triage_by_rules("downstream timeout 503", "", "P2", "svc", "staging")
        assert r is not None
        assert r.incident_type == IncidentType.dependency_failure.value

    def test_fallback_emits_enum_value(self):
        from app.graph.nodes import _triage_fallback

        r = _triage_fallback("weird thing", "P3", "svc")
        assert r.incident_type == IncidentType.service_degradation.value
```

- [ ] **Step 2: 跑测试确认失败（或已偶然通过）**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_diagnose_structured.py::TestTriageReferenceAlignment -v`
Expected: PASS（值未变，测试此刻就通过）—— 该测试作为**引用收敛后的防回归锁**，确认收敛不改变输出值。继续 Step 3 完成引用替换。

- [ ] **Step 3: 替换 magic string 为枚举引用**

在 `backend/app/graph/nodes/__init__.py` 中做如下精确替换（`IncidentType` 已在 Task 3 import）：

3a. `_triage_by_rules` 内三处 `incident_type="..."`：
- `incident_type="deployment_regression"` → `incident_type=IncidentType.deployment_regression.value`
- `incident_type="resource_exhaustion"` → `incident_type=IncidentType.resource_exhaustion.value`
- `incident_type="dependency_failure"` → `incident_type=IncidentType.dependency_failure.value`

3b. `_triage_by_llm` 内 fallback 默认值：
- `incident_type=llm_data.get("incident_type", "service_degradation")` → `incident_type=llm_data.get("incident_type", IncidentType.service_degradation.value)`

3c. `_triage_fallback` 内：
- `incident_type="service_degradation"` → `incident_type=IncidentType.service_degradation.value`

3d. `planner_node` 内分支比较（约 304、315、326 行）：
- `if incident_type == "deployment_regression":` → `if incident_type == IncidentType.deployment_regression.value:`
- `elif incident_type == "resource_exhaustion":` → `elif incident_type == IncidentType.resource_exhaustion.value:`
- `elif incident_type == "dependency_failure":` → `elif incident_type == IncidentType.dependency_failure.value:`

3e. `_add_db_tasks` 与 `_add_k8s_tasks` 内的 `if incident == "...":` 比较同样替换为 `IncidentType.X.value`（`resource_exhaustion` / `dependency_failure` / `deployment_regression` 各处）。

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_diagnose_structured.py -v`
Expected: PASS（全部）

回归 triage/planner 相关测试：
Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_graph_integration.py app/tests/test_mysql_planning.py -q`
Expected: PASS

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/graph/nodes/__init__.py backend/app/tests/test_diagnose_structured.py
git commit -m "backend: converge triage/planner incident_type magic-strings to IncidentType enum

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 6: Phase 8.0 全量回归（地基验收）**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q`
Expected: PASS（全绿后方可进入 Phase 8.1）

---

# Phase 8.1：评测框架

> 仅在 Phase 8.0 全量回归通过后启动。

## Task 5: create_incident_graph 支持注入 checkpointer

**Files:**
- Modify: `backend/app/graph/builder.py:161-272`（`create_incident_graph`）
- Test: `backend/app/tests/test_graph_integration.py`（追加）

> 唯一为评测动的 graph 构建改动。默认 `None` → 生产行为完全不变。

- [ ] **Step 1: 追加失败测试**

在 `backend/app/tests/test_graph_integration.py` 的 `TestIncidentGraph` 类内追加：

```python
    def test_graph_accepts_checkpointer_kwarg(self):
        """create_incident_graph(checkpointer=...) compiles; default None unchanged."""
        from langgraph.checkpoint.memory import MemorySaver

        default_graph = create_incident_graph()
        assert default_graph is not None

        cp_graph = create_incident_graph(checkpointer=MemorySaver())
        assert cp_graph is not None
        assert hasattr(cp_graph, "ainvoke")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_graph_integration.py::TestIncidentGraph::test_graph_accepts_checkpointer_kwarg -v`
Expected: FAIL（`create_incident_graph() got an unexpected keyword argument 'checkpointer'`）

- [ ] **Step 3: 改签名透传**

修改 `backend/app/graph/builder.py`：

3a. 函数签名（第 161 行）：

```python
def create_incident_graph(checkpointer=None) -> StateGraph:
```

3b. 末尾 return（第 272 行）：

```python
    return graph.compile(checkpointer=checkpointer)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_graph_integration.py -q`
Expected: PASS（全部，含原有用例）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/graph/builder.py backend/app/tests/test_graph_integration.py
git commit -m "backend: create_incident_graph accepts optional checkpointer (default None)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: fixture_context + gateway 短路读取点

**Files:**
- Create: `backend/app/evals/__init__.py`
- Create: `backend/app/evals/fixture_context.py`
- Modify: `backend/app/tools/gateway.py`（import + `call_tool` 开头 + helper）
- Test: `backend/app/tests/test_eval_fixture_context.py`

- [ ] **Step 1: 建空包标记**

创建 `backend/app/evals/__init__.py`（空文件）：

```python
```

- [ ] **Step 2: 写失败测试**

创建 `backend/app/tests/test_eval_fixture_context.py`：

```python
"""Tests for eval fixture injection via ContextVar + gateway short-circuit."""
import asyncio

import pytest

from app.tools import gateway, ToolRequest
from app.evals.fixture_context import fixture_scope, get_active_fixtures


def _req(tool_name):
    return ToolRequest(
        tool_name=tool_name, params={"service": "s", "env": "e"}, run_id="r"
    )


def test_no_scope_returns_none():
    assert get_active_fixtures() is None


@pytest.mark.asyncio
async def test_scope_short_circuits_to_fixture():
    with fixture_scope({"query_logs": {"logs": [], "count": 7}}):
        resp = await gateway.call_tool(_req("query_logs"))
    assert resp.success is True
    assert resp.result["count"] == 7
    assert resp.result["_adapter_info"] == "eval_fixture"


@pytest.mark.asyncio
async def test_unprovided_readonly_tool_returns_controlled_empty():
    # query_k8s_pods not provided → controlled empty, NOT fail-loud, NOT mock data
    with fixture_scope({"query_logs": {"count": 1}}):
        resp = await gateway.call_tool(_req("query_k8s_pods"))
    assert resp.success is True
    assert resp.result.get("_adapter_info") == "eval_fixture"
    # No payload keys other than the adapter marker
    assert set(resp.result.keys()) == {"_adapter_info"}


@pytest.mark.asyncio
async def test_write_tool_returns_success_stub():
    with fixture_scope({"query_logs": {"count": 1}}):
        resp = await gateway.call_tool(
            ToolRequest(
                tool_name="write_rca_to_oss",
                params={"run_id": "r", "content": "x"},
                run_id="r",
            )
        )
    assert resp.success is True
    assert resp.result.get("_eval_stub") is True


@pytest.mark.asyncio
async def test_scope_exit_restores_normal_path():
    with fixture_scope({"query_logs": {"count": 1}}):
        pass
    resp = await gateway.call_tool(_req("query_logs"))
    # Back to mock adapter — not the eval marker
    assert resp.result.get("_adapter_info") != "eval_fixture"


@pytest.mark.asyncio
async def test_concurrent_cases_are_isolated():
    async def run_case(count):
        with fixture_scope({"query_logs": {"count": count}}):
            await asyncio.sleep(0.01)
            resp = await gateway.call_tool(_req("query_logs"))
            return resp.result["count"]

    results = await asyncio.gather(run_case(1), run_case(2), run_case(3))
    assert sorted(results) == [1, 2, 3]
```

- [ ] **Step 3: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_fixture_context.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.fixture_context`）

- [ ] **Step 4: 实现 fixture_context**

创建 `backend/app/evals/fixture_context.py`：

```python
"""Scoped fixture injection for offline eval.

Mirrors the project's existing ContextVar pattern (app/graph/context.py,
app/tracing.py run_id_var): a ContextVar carries per-case tool fixtures so the
gateway can short-circuit tool calls to fixed evidence. ContextVar follows the
async task automatically, so concurrent eval cases never cross-contaminate and
the gateway stays stateless. Outside a fixture_scope the var is None and the
gateway behaves exactly as in production.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Dict, Optional

# {tool_name: result_dict}; None means "not in an eval scope".
_fixture_var: ContextVar[Optional[Dict[str, dict]]] = ContextVar(
    "eval_fixtures", default=None
)


def get_active_fixtures() -> Optional[Dict[str, dict]]:
    """Return the active fixture map, or None when not inside a fixture_scope."""
    return _fixture_var.get()


@contextmanager
def fixture_scope(fixtures: Dict[str, dict]):
    """Activate a per-case fixture map for the duration of the block.

    Args:
        fixtures: mapping of tool_name -> result dict the gateway should return.
    """
    token = _fixture_var.set(fixtures or {})
    try:
        yield
    finally:
        _fixture_var.reset(token)
```

- [ ] **Step 5: 加 gateway 短路读取点**

修改 `backend/app/tools/gateway.py`：

5a. 第 1 行 import 增加 `Optional`：

```python
from typing import Dict, Any, List, Optional
```

5b. 在 `class ToolGateway:` 定义**之前**（约第 854 行，`_sanitize_for_audit` 之后）新增 helper：

```python
EVAL_WRITE_LIKE_TOOLS = {"execute_action"}


def _maybe_eval_fixture_response(
    request: ToolRequest, start_time: float
) -> Optional[ToolResponse]:
    """Short-circuit tool calls to fixed fixtures when inside an eval fixture_scope.

    Returns None outside any scope (production / normal tests) so the gateway
    proceeds with its mock/real adapter logic unchanged. Inside a scope:
      - tool provided in fixtures   → wrapped fixture result
      - write_* / execute_action    → success stub (not required as fixtures)
      - other read-only tool        → controlled empty {} (NOT mock data)
    """
    from app.evals.fixture_context import get_active_fixtures

    fixtures = get_active_fixtures()
    if fixtures is None:
        return None

    tool_name = request.tool_name
    if tool_name in fixtures:
        raw = fixtures[tool_name]
        result = dict(raw) if isinstance(raw, dict) else {"value": raw}
    elif tool_name.startswith("write_") or tool_name in EVAL_WRITE_LIKE_TOOLS:
        result = {"success": True, "_eval_stub": True}
    else:
        result = {}

    result["_adapter_info"] = "eval_fixture"
    latency = int((time.time() - start_time) * 1000)
    return ToolResponse(
        tool_name=tool_name,
        success=True,
        result=result,
        latency_ms=latency,
    )
```

5c. 在 `call_tool` 开头（约第 891-892 行，`start_time = time.time()` **之后**、`span_id = tracer.start_span(...)` **之前**）插入短路：

```python
    async def call_tool(self, request: ToolRequest) -> ToolResponse:
        start_time = time.time()

        # Eval fixture short-circuit (active only inside fixture_scope). Happens
        # before mock/real selection, so it composes with the autouse mock conftest.
        fixture_resp = _maybe_eval_fixture_response(request, start_time)
        if fixture_resp is not None:
            return fixture_resp

        span_id = tracer.start_span(
```

- [ ] **Step 6: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_fixture_context.py -v`
Expected: PASS（6 passed）

回归 gateway 相关（确认生产路径零影响）：
Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_graph_integration.py -q`
Expected: PASS

- [ ] **Step 7: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/__init__.py backend/app/evals/fixture_context.py backend/app/tools/gateway.py backend/app/tests/test_eval_fixture_context.py
git commit -m "backend: scoped fixture injection via ContextVar with gateway short-circuit

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: case_loader（加载 + 校验）

**Files:**
- Create: `backend/app/evals/case_loader.py`
- Test: `backend/app/tests/test_eval_case_loader.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_case_loader.py`：

```python
"""Tests for dataset case loading + schema validation."""
import json

import pytest

from app.evals.case_loader import load_cases, EvalDatasetError


def _valid_case(case_id="c1", incident_type="deployment_regression"):
    return {
        "case_id": case_id,
        "description": "human-readable scenario",
        "ticket": {
            "ticket_id": "INC-1",
            "title": "5xx spike",
            "description": "errors",
            "service": "payment-service",
            "env": "staging",
            "severity": "P2",
            "source": "manual",
        },
        "tool_fixtures": {"query_logs": {"count": 3}},
        "expected": {"incident_type": incident_type},
    }


def _write(tmp_path, name, data):
    f = tmp_path / name
    f.write_text(json.dumps(data), encoding="utf-8")
    return f


def test_loads_valid_directory(tmp_path):
    _write(tmp_path, "a.json", _valid_case("c1"))
    _write(tmp_path, "b.json", _valid_case("c2", "resource_exhaustion"))
    cases = load_cases(str(tmp_path))
    assert {c["case_id"] for c in cases} == {"c1", "c2"}


def test_loads_single_file(tmp_path):
    f = _write(tmp_path, "a.json", _valid_case("solo"))
    cases = load_cases(str(f))
    assert len(cases) == 1
    assert cases[0]["case_id"] == "solo"


def test_missing_case_id_fails(tmp_path):
    bad = _valid_case()
    del bad["case_id"]
    _write(tmp_path, "bad.json", bad)
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "case_id" in str(exc.value)


def test_missing_ticket_field_fails(tmp_path):
    bad = _valid_case()
    del bad["ticket"]["service"]
    _write(tmp_path, "bad.json", bad)
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "service" in str(exc.value)


def test_illegal_expected_incident_type_fails(tmp_path):
    bad = _valid_case(incident_type="aliens")
    _write(tmp_path, "bad.json", bad)
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "incident_type" in str(exc.value)


def test_duplicate_case_id_fails(tmp_path):
    _write(tmp_path, "a.json", _valid_case("dup"))
    _write(tmp_path, "b.json", _valid_case("dup"))
    with pytest.raises(EvalDatasetError) as exc:
        load_cases(str(tmp_path))
    assert "dup" in str(exc.value)


def test_empty_directory_fails(tmp_path):
    with pytest.raises(EvalDatasetError):
        load_cases(str(tmp_path))
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_case_loader.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.case_loader`）

- [ ] **Step 3: 实现 case_loader**

创建 `backend/app/evals/case_loader.py`：

```python
"""Load and validate eval dataset case JSON files.

Schema is intentionally minimal and fail-fast: a malformed case aborts loading
with a message naming the offending case + field, so the dataset can never run a
half-broken case silently.
"""
import json
from pathlib import Path
from typing import Dict, List

from app.models.incident_type import IncidentType

REQUIRED_TOP = ("case_id", "ticket")
REQUIRED_TICKET = (
    "ticket_id",
    "title",
    "description",
    "service",
    "env",
    "severity",
    "source",
)
_VALID_TYPES = {t.value for t in IncidentType}


class EvalDatasetError(Exception):
    """Raised when a dataset case fails schema validation."""


def load_cases(path: str) -> List[Dict]:
    """Load all case dicts from a directory of *.json or a single file.

    Raises EvalDatasetError on any schema violation, duplicate case_id, or empty
    dataset.
    """
    p = Path(path)
    if p.is_dir():
        files = sorted(p.glob("*.json"))
    elif p.is_file():
        files = [p]
    else:
        raise EvalDatasetError(f"Dataset path not found: {path}")

    cases: List[Dict] = []
    seen = set()
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise EvalDatasetError(f"{f.name}: invalid JSON ({exc})") from exc
        _validate_case(data, f.name)
        cid = data["case_id"]
        if cid in seen:
            raise EvalDatasetError(f"Duplicate case_id '{cid}' in {f.name}")
        seen.add(cid)
        cases.append(data)

    if not cases:
        raise EvalDatasetError(f"No case JSON files found under {path}")
    return cases


def _validate_case(data: Dict, fname: str) -> None:
    if not isinstance(data, dict):
        raise EvalDatasetError(f"{fname}: top-level JSON must be an object")

    for key in REQUIRED_TOP:
        if key not in data:
            raise EvalDatasetError(f"{fname}: missing required field '{key}'")

    ticket = data["ticket"]
    if not isinstance(ticket, dict):
        raise EvalDatasetError(f"{fname}: 'ticket' must be an object")
    for key in REQUIRED_TICKET:
        if key not in ticket:
            raise EvalDatasetError(f"{fname}: ticket missing required field '{key}'")

    fixtures = data.get("tool_fixtures", {})
    if not isinstance(fixtures, dict):
        raise EvalDatasetError(f"{fname}: 'tool_fixtures' must be an object")

    expected = data.get("expected", {})
    if not isinstance(expected, dict):
        raise EvalDatasetError(f"{fname}: 'expected' must be an object")

    exp_type = expected.get("incident_type")
    if exp_type is not None and exp_type not in _VALID_TYPES:
        raise EvalDatasetError(
            f"{fname}: expected.incident_type '{exp_type}' is not a valid IncidentType"
        )
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_case_loader.py -v`
Expected: PASS（7 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/case_loader.py backend/app/tests/test_eval_case_loader.py
git commit -m "backend: eval dataset case loader with fail-fast schema validation

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: scorer（单 case 确定性评分）

**Files:**
- Create: `backend/app/evals/scorer.py`
- Test: `backend/app/tests/test_eval_scorer.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_scorer.py`：

```python
"""Tests for deterministic per-case scoring."""
from app.evals.scorer import CaseResult, score_case
from app.models.incident_type import IncidentType
from app.models.root_cause import RootCauseCandidate
from app.graph.state import RunStatus


def _case(expected):
    return {"case_id": "c1", "ticket": {}, "expected": expected}


def _cand(incident_type, conf):
    return RootCauseCandidate(
        candidate_id="x", hypothesis="h", confidence=conf, incident_type=incident_type
    )


def test_top1_hit_and_miss():
    state = {
        "root_cause_candidates": [
            _cand(IncidentType.deployment_regression, 0.9),
            _cand(IncidentType.resource_exhaustion, 0.4),
        ],
        "risk_decision": "NEEDS_APPROVAL",
        "status": RunStatus.WAITING_HUMAN,
    }
    r = score_case(_case({"incident_type": "deployment_regression"}), state, 120)
    assert r.hit_top1 is True
    assert r.actual_type == "deployment_regression"
    assert r.confidence == 0.9
    assert r.latency_ms == 120

    r2 = score_case(_case({"incident_type": "resource_exhaustion"}), state, 120)
    assert r2.hit_top1 is False
    assert r2.hit_top3 is True  # present at index 1


def test_top3_miss():
    state = {"root_cause_candidates": [_cand(IncidentType.deployment_regression, 0.9)]}
    r = score_case(_case({"incident_type": "database_failure"}), state, 50)
    assert r.hit_top1 is False
    assert r.hit_top3 is False


def test_risk_and_status_match():
    state = {
        "root_cause_candidates": [_cand(IncidentType.deployment_regression, 0.8)],
        "risk_decision": "NEEDS_APPROVAL",
        "status": RunStatus.WAITING_HUMAN,
    }
    r = score_case(
        _case(
            {
                "incident_type": "deployment_regression",
                "risk_decision": "NEEDS_APPROVAL",
                "final_status": "WAITING_HUMAN",
            }
        ),
        state,
        10,
    )
    assert r.risk_match is True
    assert r.status_match is True


def test_unset_expected_fields_are_skipped_as_none():
    state = {
        "root_cause_candidates": [_cand(IncidentType.deployment_regression, 0.8)],
        "risk_decision": "LOW_ONLY",
        "status": RunStatus.COMPLETED,
    }
    r = score_case(_case({"incident_type": "deployment_regression"}), state, 10)
    assert r.risk_match is None  # expected.risk_decision absent → skipped
    assert r.status_match is None


def test_handles_dict_candidates_from_checkpoint():
    # candidates may be plain dicts after checkpoint round-trip
    state = {
        "root_cause_candidates": [
            {"candidate_id": "x", "hypothesis": "h", "confidence": 0.7,
             "incident_type": "network_failure"}
        ],
    }
    r = score_case(_case({"incident_type": "network_failure"}), state, 5)
    assert r.hit_top1 is True
    assert r.actual_type == "network_failure"


def test_no_candidates_gives_none_actual():
    state = {"root_cause_candidates": []}
    r = score_case(_case({"incident_type": "deployment_regression"}), state, 5)
    assert r.actual_type is None
    assert r.hit_top1 is False


def test_error_result_factory():
    r = CaseResult.error_result("c9", "BoomError: x", 33)
    assert r.case_id == "c9"
    assert r.error == "BoomError: x"
    assert r.hit_top1 is None
    assert r.latency_ms == 33
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_scorer.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.scorer`）

- [ ] **Step 3: 实现 scorer**

创建 `backend/app/evals/scorer.py`：

```python
"""Deterministic per-case scoring (no LLM).

The primary metric is enum equality on incident_type: actual[0] vs expected.
Every comparison is exact-match and reproducible; the only non-determinism in
the whole eval lives upstream in the real LLM, never here.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CaseResult:
    case_id: str
    hit_top1: Optional[bool]
    hit_top3: Optional[bool]
    risk_match: Optional[bool]
    status_match: Optional[bool]
    actual_type: Optional[str]
    expected_type: Optional[str]
    confidence: Optional[float]
    latency_ms: Optional[int]
    hypothesis: Optional[str]
    error: Optional[str] = None

    @classmethod
    def error_result(cls, case_id: str, error: str, latency_ms: int) -> "CaseResult":
        return cls(
            case_id=case_id,
            hit_top1=None,
            hit_top3=None,
            risk_match=None,
            status_match=None,
            actual_type=None,
            expected_type=None,
            confidence=None,
            latency_ms=latency_ms,
            hypothesis=None,
            error=error,
        )


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, dict):
        return obj.get(name, default)
    return default


def _type_value(candidate: Any) -> Optional[str]:
    it = _attr(candidate, "incident_type")
    if it is None:
        return None
    return it.value if hasattr(it, "value") else str(it)


def _status_value(status: Any) -> Optional[str]:
    if status is None:
        return None
    return status.value if hasattr(status, "value") else str(status)


def score_case(
    case: Dict[str, Any], final_state: Dict[str, Any], latency_ms: int
) -> CaseResult:
    case_id = case["case_id"]
    expected = case.get("expected", {}) or {}

    candidates = final_state.get("root_cause_candidates") or []
    types: List[str] = [t for t in (_type_value(c) for c in candidates if c is not None) if t]
    top_type = types[0] if types else None
    top_conf = _attr(candidates[0], "confidence") if candidates else None
    top_hyp = _attr(candidates[0], "hypothesis") if candidates else None

    exp_type = expected.get("incident_type")
    hit_top1 = (top_type == exp_type) if exp_type is not None else None
    hit_top3 = (exp_type in types[:3]) if exp_type is not None else None

    exp_risk = expected.get("risk_decision")
    risk_match = (
        final_state.get("risk_decision") == exp_risk if exp_risk is not None else None
    )

    exp_status = expected.get("final_status")
    actual_status = _status_value(final_state.get("status"))
    status_match = (actual_status == exp_status) if exp_status is not None else None

    return CaseResult(
        case_id=case_id,
        hit_top1=hit_top1,
        hit_top3=hit_top3,
        risk_match=risk_match,
        status_match=status_match,
        actual_type=top_type,
        expected_type=exp_type,
        confidence=top_conf,
        latency_ms=latency_ms,
        hypothesis=top_hyp,
        error=None,
    )
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_scorer.py -v`
Expected: PASS（7 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/scorer.py backend/app/tests/test_eval_scorer.py
git commit -m "backend: deterministic per-case eval scorer

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: metrics（聚合指标，纯 stdlib）

**Files:**
- Create: `backend/app/evals/metrics.py`
- Test: `backend/app/tests/test_eval_metrics.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_metrics.py`：

```python
"""Tests for metric aggregation (pure stdlib, deterministic)."""
import math

from app.evals.scorer import CaseResult
from app.evals.metrics import compute_metrics, aggregate_rounds


def _r(case_id, exp, act, conf=0.8, risk=None, status=None, error=None):
    hit1 = (exp == act) if (exp is not None and error is None) else (None if error else False)
    return CaseResult(
        case_id=case_id,
        hit_top1=hit1,
        hit_top3=hit1,
        risk_match=risk,
        status_match=status,
        actual_type=act,
        expected_type=exp,
        confidence=conf,
        latency_ms=100,
        hypothesis="h",
        error=error,
    )


def test_top1_accuracy():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", "resource_exhaustion", "deployment_regression"),
        _r("c3", "database_failure", "database_failure"),
    ]
    m = compute_metrics(results)
    assert m["top1_accuracy"] == round(2 / 3, 4)
    assert m["case_count"] == 3
    assert m["scored_count"] == 3
    assert m["error_count"] == 0


def test_macro_f1_and_confusion_and_recall():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", "deployment_regression", "resource_exhaustion"),
        _r("c3", "resource_exhaustion", "resource_exhaustion"),
    ]
    m = compute_metrics(results)

    # confusion[expected][actual]
    cm = m["confusion_matrix"]
    assert cm["deployment_regression"]["deployment_regression"] == 1
    assert cm["deployment_regression"]["resource_exhaustion"] == 1
    assert cm["resource_exhaustion"]["resource_exhaustion"] == 1

    # per-class recall
    assert m["per_class"]["deployment_regression"]["recall"] == 0.5
    assert m["per_class"]["resource_exhaustion"]["recall"] == 1.0

    # both classes have f1 = 2/3 → macro 2/3
    assert math.isclose(m["macro_f1"], round(2 / 3, 4), abs_tol=1e-4)


def test_unknown_rate():
    results = [
        _r("c1", "deployment_regression", "unknown"),
        _r("c2", "resource_exhaustion", "resource_exhaustion"),
    ]
    m = compute_metrics(results)
    assert m["unknown_rate"] == 0.5


def test_risk_and_status_accuracy_skip_none():
    results = [
        _r("c1", "deployment_regression", "deployment_regression", risk=True, status=True),
        _r("c2", "resource_exhaustion", "resource_exhaustion", risk=False, status=None),
    ]
    m = compute_metrics(results)
    assert m["risk_accuracy"] == 0.5  # 1 of 2 graded
    assert m["status_accuracy"] == 1.0  # only c1 graded → 1/1


def test_errors_excluded_from_accuracy():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", None, None, error="Boom"),
    ]
    m = compute_metrics(results)
    assert m["error_count"] == 1
    assert m["scored_count"] == 1
    assert m["top1_accuracy"] == 1.0


def test_aggregate_rounds_mean_min_max():
    m1 = compute_metrics([_r("c1", "deployment_regression", "deployment_regression")])
    m2 = compute_metrics([_r("c1", "deployment_regression", "resource_exhaustion")])
    agg = aggregate_rounds([m1, m2])
    assert agg["top1_accuracy"]["mean"] == 0.5
    assert agg["top1_accuracy"]["min"] == 0.0
    assert agg["top1_accuracy"]["max"] == 1.0
    assert agg["rounds"] == 2
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_metrics.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.metrics`）

- [ ] **Step 3: 实现 metrics**

创建 `backend/app/evals/metrics.py`：

```python
"""Aggregate CaseResults into eval metrics. Pure stdlib, no pandas.

Two metric layers never merge into one composite number: incident-type quality
(top1/top3/macro-F1/recall/confusion) is reported alongside, but separately from,
risk/status fidelity. Macro-F1 and per-class recall guard against a dominant
class masking failures on rare ones.
"""
from typing import Any, Dict, List, Optional

from app.evals.scorer import CaseResult


def _safe_mean(values: List[float]) -> Optional[float]:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return round(sum(vals) / len(vals), 4)


def _accuracy(flags: List[Optional[bool]]) -> Optional[float]:
    graded = [f for f in flags if f is not None]
    if not graded:
        return None
    return round(sum(1 for f in graded if f) / len(graded), 4)


def compute_metrics(results: List[CaseResult]) -> Dict[str, Any]:
    scored = [r for r in results if r.error is None]
    errored = [r for r in results if r.error is not None]

    # incident-type quality
    top1_accuracy = _accuracy([r.hit_top1 for r in scored])
    top3_accuracy = _accuracy([r.hit_top3 for r in scored])

    # confusion matrix expected -> actual -> count (only cases with an expected label)
    pairs = [
        (r.expected_type, r.actual_type)
        for r in scored
        if r.expected_type is not None
    ]
    confusion: Dict[str, Dict[str, int]] = {}
    for exp, act in pairs:
        act_key = act if act is not None else "<none>"
        confusion.setdefault(exp, {})
        confusion[exp][act_key] = confusion[exp].get(act_key, 0) + 1

    classes = sorted(
        {e for e, _ in pairs} | {a for _, a in pairs if a is not None}
    )
    per_class: Dict[str, Dict[str, float]] = {}
    for c in classes:
        tp = sum(1 for e, a in pairs if e == c and a == c)
        fp = sum(1 for e, a in pairs if e != c and a == c)
        fn = sum(1 for e, a in pairs if e == c and a != c)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_class[c] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": sum(1 for e, _ in pairs if e == c),
        }

    expected_classes = [c for c in classes if any(e == c for e, _ in pairs)]
    macro_f1 = (
        round(sum(per_class[c]["f1"] for c in expected_classes) / len(expected_classes), 4)
        if expected_classes
        else None
    )

    actual_types = [r.actual_type for r in scored if r.actual_type is not None]
    unknown_rate = (
        round(sum(1 for t in actual_types if t == "unknown") / len(actual_types), 4)
        if actual_types
        else None
    )

    return {
        "case_count": len(results),
        "scored_count": len(scored),
        "error_count": len(errored),
        "error_cases": [r.case_id for r in errored],
        "top1_accuracy": top1_accuracy,
        "top3_accuracy": top3_accuracy,
        "risk_accuracy": _accuracy([r.risk_match for r in scored]),
        "status_accuracy": _accuracy([r.status_match for r in scored]),
        "macro_f1": macro_f1,
        "per_class": per_class,
        "confusion_matrix": confusion,
        "unknown_rate": unknown_rate,
        "avg_confidence": _safe_mean([r.confidence for r in scored]),
        "avg_latency_ms": _safe_mean([float(r.latency_ms) for r in scored if r.latency_ms is not None]),
    }


_SCALAR_KEYS = (
    "top1_accuracy",
    "top3_accuracy",
    "risk_accuracy",
    "status_accuracy",
    "macro_f1",
    "unknown_rate",
    "avg_confidence",
    "avg_latency_ms",
)


def aggregate_rounds(round_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate N per-round metric dicts into mean/min/max per scalar metric.

    Real-LLM eval is non-deterministic, so --repeat N reports a distribution,
    not a single point. Non-scalar fields (confusion, per_class) are taken from
    the last round for reference.
    """
    agg: Dict[str, Any] = {"rounds": len(round_metrics)}
    for key in _SCALAR_KEYS:
        vals = [m[key] for m in round_metrics if m.get(key) is not None]
        if vals:
            agg[key] = {
                "mean": round(sum(vals) / len(vals), 4),
                "min": round(min(vals), 4),
                "max": round(max(vals), 4),
            }
        else:
            agg[key] = {"mean": None, "min": None, "max": None}
    if round_metrics:
        agg["last_round_confusion_matrix"] = round_metrics[-1]["confusion_matrix"]
        agg["last_round_per_class"] = round_metrics[-1]["per_class"]
    return agg
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_metrics.py -v`
Expected: PASS（6 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/metrics.py backend/app/tests/test_eval_metrics.py
git commit -m "backend: eval metric aggregation (accuracy, macro-F1, confusion, recall)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: report（JSON + Markdown 生成）

**Files:**
- Create: `backend/app/evals/report.py`
- Test: `backend/app/tests/test_eval_report.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_report.py`：

```python
"""Tests for report assembly + markdown rendering."""
import json

from app.evals.scorer import CaseResult
from app.evals.metrics import compute_metrics, aggregate_rounds
from app.evals.report import build_report, render_markdown, write_report


def _r(case_id, exp, act):
    return CaseResult(
        case_id=case_id,
        hit_top1=(exp == act),
        hit_top3=(exp == act),
        risk_match=None,
        status_match=None,
        actual_type=act,
        expected_type=exp,
        confidence=0.8,
        latency_ms=100,
        hypothesis="some hypothesis text",
    )


def _round():
    results = [
        _r("c1", "deployment_regression", "deployment_regression"),
        _r("c2", "resource_exhaustion", "unknown"),
    ]
    return results, compute_metrics(results)


def test_build_report_structure():
    r1, m1 = _round()
    report = build_report(
        mode="direct",
        rounds_results=[r1],
        rounds_metrics=[m1],
        aggregate=aggregate_rounds([m1]),
    )
    assert report["mode"] == "direct"
    assert report["meta"]["real_llm"] is True
    assert report["meta"]["ci_metric"] is False
    assert "aggregate" in report
    assert len(report["rounds"]) == 1
    # hypothesis collected for human inspection
    assert report["rounds"][0]["cases"][0]["hypothesis"] == "some hypothesis text"


def test_render_markdown_contains_disclaimer_and_metrics():
    r1, m1 = _round()
    report = build_report(
        mode="direct",
        rounds_results=[r1],
        rounds_metrics=[m1],
        aggregate=aggregate_rounds([m1]),
    )
    md = render_markdown(report)
    assert "真实 LLM" in md
    assert "非 CI 指标" in md
    assert "Top1" in md
    assert "Confusion" in md or "混淆" in md


def test_write_report_emits_json(tmp_path):
    r1, m1 = _round()
    report = build_report(
        mode="direct",
        rounds_results=[r1],
        rounds_metrics=[m1],
        aggregate=aggregate_rounds([m1]),
    )
    out = tmp_path / "report.json"
    write_report(report, str(out))
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["mode"] == "direct"
    # markdown sibling written next to json
    assert (tmp_path / "report.md").exists()
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_report.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.report`）

- [ ] **Step 3: 实现 report**

创建 `backend/app/evals/report.py`：

```python
"""Assemble eval results into a JSON report + human-readable Markdown.

Every report is explicitly stamped real_llm=True / ci_metric=False: these numbers
come from a non-deterministic real-LLM run and must never be treated as a CI gate.
"""
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.evals.scorer import CaseResult

_DISCLAIMER = (
    "> ⚠️ 本报告由**真实 LLM**（DeepSeek）生成，结果存在波动，属**非 CI 指标**。"
    "请结合 --repeat N 的均值/波动范围解读，勿作为单点门禁。"
)


def build_report(
    mode: str,
    rounds_results: List[List[CaseResult]],
    rounds_metrics: List[Dict[str, Any]],
    aggregate: Dict[str, Any],
    extra_meta: Dict[str, Any] = None,
) -> Dict[str, Any]:
    meta = {
        "generated_at": datetime.utcnow().isoformat(),
        "real_llm": True,
        "ci_metric": False,
        "repeat": len(rounds_results),
    }
    if extra_meta:
        meta.update(extra_meta)

    rounds = []
    for idx, (results, metrics) in enumerate(zip(rounds_results, rounds_metrics)):
        rounds.append(
            {
                "round": idx + 1,
                "metrics": metrics,
                "cases": [asdict(r) for r in results],
            }
        )

    return {
        "mode": mode,
        "meta": meta,
        "aggregate": aggregate,
        "rounds": rounds,
    }


def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _fmt_band(band: Dict[str, Any]) -> str:
    if not band or band.get("mean") is None:
        return "—"
    return f"{_fmt(band['mean'])} (min {_fmt(band['min'])} / max {_fmt(band['max'])})"


def render_markdown(report: Dict[str, Any]) -> str:
    agg = report["aggregate"]
    lines: List[str] = []
    lines.append(f"# OpsPilot 离线评测报告 — mode={report['mode']}")
    lines.append("")
    lines.append(_DISCLAIMER)
    lines.append("")
    lines.append(f"- 生成时间: {report['meta']['generated_at']}")
    lines.append(f"- 轮数 (repeat): {report['meta']['repeat']}")
    lines.append("")
    lines.append("## 聚合指标（N 轮均值 + 波动）")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    lines.append(f"| Incident Type Top1 | {_fmt_band(agg.get('top1_accuracy'))} |")
    lines.append(f"| Incident Type Top3 | {_fmt_band(agg.get('top3_accuracy'))} |")
    lines.append(f"| Macro F1 | {_fmt_band(agg.get('macro_f1'))} |")
    lines.append(f"| Unknown Rate | {_fmt_band(agg.get('unknown_rate'))} |")
    lines.append(f"| 风险准确率 | {_fmt_band(agg.get('risk_accuracy'))} |")
    lines.append(f"| 终态准确率 | {_fmt_band(agg.get('status_accuracy'))} |")
    lines.append(f"| 平均 confidence | {_fmt_band(agg.get('avg_confidence'))} |")
    lines.append(f"| 平均 latency(ms) | {_fmt_band(agg.get('avg_latency_ms'))} |")
    lines.append("")

    per_class = agg.get("last_round_per_class", {})
    if per_class:
        lines.append("## Per-class Recall（末轮）")
        lines.append("")
        lines.append("| 类别 | recall | precision | f1 | support |")
        lines.append("|------|--------|-----------|----|---------|")
        for cls, pc in sorted(per_class.items()):
            lines.append(
                f"| {cls} | {_fmt(pc['recall'])} | {_fmt(pc['precision'])} "
                f"| {_fmt(pc['f1'])} | {pc['support']} |"
            )
        lines.append("")

    confusion = agg.get("last_round_confusion_matrix", {})
    if confusion:
        lines.append("## Confusion Matrix / 混淆矩阵（末轮，行=expected 列=actual）")
        lines.append("")
        lines.append("```")
        lines.append(json.dumps(confusion, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    # Hypothesis quality: collect-only, for human spot-check
    lines.append("## Hypothesis 抽查（首期只采集不评分）")
    lines.append("")
    last_round = report["rounds"][-1] if report["rounds"] else {"cases": []}
    for case in last_round["cases"]:
        err = case.get("error")
        if err:
            lines.append(f"- **{case['case_id']}** [ERROR] {err}")
        else:
            lines.append(
                f"- **{case['case_id']}** expected=`{_fmt(case['expected_type'])}` "
                f"actual=`{_fmt(case['actual_type'])}` conf={_fmt(case['confidence'])}: "
                f"{case.get('hypothesis') or '—'}"
            )
    lines.append("")
    return "\n".join(lines)


def write_report(report: Dict[str, Any], output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    md_path = out.with_suffix(".md")
    md_path.write_text(render_markdown(report), encoding="utf-8")
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_report.py -v`
Expected: PASS（3 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/report.py backend/app/tests/test_eval_report.py
git commit -m "backend: eval JSON + Markdown report with non-CI disclaimer

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: executors（Direct 扎实 / Runner 骨架）

**Files:**
- Create: `backend/app/evals/executors.py`
- Test: `backend/app/tests/test_eval_executors.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_executors.py`：

```python
"""Tests for DirectGraphExecutor end-to-end with mock LLM + fixture injection."""
import pytest

from app.evals.executors import DirectGraphExecutor, GraphExecutor
from app.evals.fixture_context import fixture_scope
from app.models.incident import IncidentTicket
from app.models.incident_type import IncidentType
from app.llm_client import llm_client


def _initial_state(case_id="exec-1"):
    ticket = IncidentTicket(
        ticket_id="INC-X",
        title="5xx after release",
        description="errors spiked post deploy",
        service="payment-service",
        env="staging",
        severity="P2",
        source="manual",
    )
    return {
        "run_id": f"eval-{case_id}",
        "thread_id": f"eval-{case_id}",
        "ticket": ticket,
        "evidence_items": [],
        "root_cause_candidates": [],
        "evidence_collection_results": [],
        "evidence_quality_score": 0.0,
        "step_count": 0,
    }


def _install_mock_llm(monkeypatch):
    def fake_complete_sync(prompt, system_prompt=None, temperature=0.7):
        if "incident_type" in prompt and "root cause candidates" in prompt:
            return """[
              {"incident_type": "deployment_regression",
               "hypothesis": "release introduced regression",
               "confidence": 0.85, "next_checks": ["rollback"]}
            ]"""
        if "triage information" in prompt:
            return """{"incident_type": "deployment_regression", "severity": "P2",
                       "suspected_services": ["payment-service"],
                       "suggested_time_window": {"start": "2h ago", "end": "now"},
                       "requires_immediate_human": false, "rationale": "deploy"}"""
        return "fallback_response"

    monkeypatch.setattr(llm_client, "complete_sync", fake_complete_sync)


@pytest.mark.asyncio
async def test_direct_executor_runs_end_to_end(monkeypatch):
    _install_mock_llm(monkeypatch)

    executor = DirectGraphExecutor()
    fixtures = {
        "query_logs": {"logs": [{"msg": "500"}], "count": 12},
        "query_deployments": {"deployments": [{"version": "v2"}], "count": 1},
    }
    with fixture_scope(fixtures):
        final_state = await executor.execute("exec-1", _initial_state())

    assert final_state is not None
    cands = final_state.get("root_cause_candidates") or []
    assert len(cands) >= 1
    top = cands[0]
    top_type = top.incident_type if hasattr(top, "incident_type") else top.get("incident_type")
    type_value = top_type.value if hasattr(top_type, "value") else top_type
    assert type_value == IncidentType.deployment_regression.value


@pytest.mark.asyncio
async def test_direct_executor_fixture_controls_evidence(monkeypatch):
    _install_mock_llm(monkeypatch)
    executor = DirectGraphExecutor()

    # Provide a query_logs fixture with a sentinel count; assert it flows into evidence
    with fixture_scope({"query_logs": {"logs": [{"m": "x"}], "count": 99}}):
        final_state = await executor.execute("exec-2", _initial_state("exec-2"))

    log_items = [
        e for e in final_state.get("evidence_items", [])
        if (e.tool_name if hasattr(e, "tool_name") else e.get("tool_name")) == "query_logs"
    ]
    assert log_items, "expected query_logs evidence from fixture"
    raw = log_items[0].raw_payload if hasattr(log_items[0], "raw_payload") else log_items[0].get("raw_payload")
    assert raw.get("count") == 99


def test_direct_executor_satisfies_protocol():
    executor = DirectGraphExecutor()
    assert isinstance(executor, GraphExecutor)
    assert executor.mode == "direct"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_executors.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.executors`）

- [ ] **Step 3: 实现 executors**

创建 `backend/app/evals/executors.py`：

```python
"""Graph execution strategies for eval.

Two layers share everything (fixtures, scoring, dataset) and diverge ONLY in how
the graph runs:
  - DirectGraphExecutor : compiled graph.ainvoke, no DB / no events. Layer-1
    Graph Quality across the full dataset. Done solid.
  - RunnerGraphExecutor : full GraphRunner production chain (events, checkpoints,
    persistence). Layer-2 Runtime Fidelity on a representative subset. Skeleton.

Layer-1 and Layer-2 metrics are reported separately and never merged.
"""
from typing import Any, Dict, Protocol, runtime_checkable

from app.graph.builder import create_incident_graph


@runtime_checkable
class GraphExecutor(Protocol):
    mode: str

    async def execute(self, case_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        ...


class DirectGraphExecutor:
    """Layer-1: run the compiled graph directly, no side effects."""

    mode = "direct"

    def __init__(self, checkpointer=None):
        self._checkpointer = checkpointer

    async def execute(self, case_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        graph = create_incident_graph(checkpointer=self._checkpointer)
        config = {
            "recursion_limit": 50,
            "configurable": {"thread_id": f"eval-{case_id}"},
        }
        return await graph.ainvoke(initial_state, config=config)


class RunnerGraphExecutor:
    """Layer-2 skeleton: run through the full GraphRunner production chain.

    Exercises events + checkpoints + persistence against the configured DB. Used
    for a representative smoke subset, not the full dataset. compare mode diffs
    its final state against DirectGraphExecutor to catch GraphRunner changing
    graph semantics or dropping fields across serialization.
    """

    mode = "runner"

    async def execute(self, case_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        from app.repositories import SessionLocal
        from app.services.graph_runner import GraphRunner

        run_id = f"eval-{case_id}"
        db = SessionLocal()
        try:
            self._ensure_run_row(db, run_id)
            runner = GraphRunner(db)
            state = {**initial_state, "run_id": run_id, "thread_id": run_id}
            final_state = await runner.run(run_id=run_id, initial_state=state)
            return final_state
        finally:
            db.close()

    @staticmethod
    def _ensure_run_row(db, run_id: str) -> None:
        """Insert a run row with this exact run_id so checkpoint FK writes succeed."""
        from app.models.db_models import IncidentRun, RunStatusEnum

        existing = (
            db.query(IncidentRun).filter(IncidentRun.run_id == run_id).first()
        )
        if existing:
            return
        db.add(IncidentRun(run_id=run_id, thread_id=run_id, status=RunStatusEnum.NEW))
        db.commit()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_executors.py -v`
Expected: PASS（3 passed）

> 注：`RunnerGraphExecutor` 为骨架，命中真实 DB，不在 pytest 中验证；由 CLI runner 模式手动冒烟（Task 14 验收）。

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/executors.py backend/app/tests/test_eval_executors.py
git commit -m "backend: GraphExecutor protocol + DirectGraphExecutor + RunnerGraphExecutor skeleton

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: runner（编排：加载 → fixture_scope → execute → score → repeat → 聚合）

**Files:**
- Create: `backend/app/evals/runner.py`
- Test: `backend/app/tests/test_eval_runner.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_runner.py`：

```python
"""Tests for eval orchestration: state build, single-case isolation, repeat."""
import pytest

from app.evals.runner import build_initial_state, run_one_case, run_dataset
from app.evals.scorer import CaseResult


class _StubExecutor:
    mode = "stub"

    def __init__(self, type_by_case):
        self._type_by_case = type_by_case
        self.seen_fixtures = []

    async def execute(self, case_id, initial_state):
        # Capture whatever fixture is active to prove scoping works
        from app.evals.fixture_context import get_active_fixtures

        self.seen_fixtures.append((case_id, get_active_fixtures()))
        return {
            "root_cause_candidates": [
                {
                    "candidate_id": "x",
                    "hypothesis": "h",
                    "confidence": 0.8,
                    "incident_type": self._type_by_case[case_id],
                }
            ],
            "risk_decision": "LOW_ONLY",
            "status": "COMPLETED",
        }


def _case(case_id, expected_type, fixtures=None):
    return {
        "case_id": case_id,
        "ticket": {
            "ticket_id": "INC-1",
            "title": "t",
            "description": "d",
            "service": "svc",
            "env": "staging",
            "severity": "P2",
            "source": "manual",
        },
        "tool_fixtures": fixtures or {},
        "expected": {"incident_type": expected_type},
    }


def test_build_initial_state_from_case():
    state = build_initial_state(_case("c1", "deployment_regression"))
    assert state["run_id"] == "eval-c1"
    ticket = state["ticket"]
    assert ticket.service == "svc"
    assert state["evidence_items"] == []
    assert state["step_count"] == 0


@pytest.mark.asyncio
async def test_run_one_case_scores_hit():
    ex = _StubExecutor({"c1": "deployment_regression"})
    result = await run_one_case(_case("c1", "deployment_regression"), ex)
    assert isinstance(result, CaseResult)
    assert result.hit_top1 is True


@pytest.mark.asyncio
async def test_run_one_case_injects_fixture_scope():
    ex = _StubExecutor({"c1": "deployment_regression"})
    await run_one_case(
        _case("c1", "deployment_regression", {"query_logs": {"count": 5}}), ex
    )
    case_id, fixtures = ex.seen_fixtures[0]
    assert fixtures == {"query_logs": {"count": 5}}


@pytest.mark.asyncio
async def test_run_one_case_captures_executor_error():
    class _Boom:
        mode = "boom"

        async def execute(self, case_id, initial_state):
            raise RuntimeError("kaboom")

    result = await run_one_case(_case("c1", "deployment_regression"), _Boom())
    assert result.error is not None
    assert "kaboom" in result.error


@pytest.mark.asyncio
async def test_run_dataset_repeats(tmp_path):
    import json

    for cid, typ in [("c1", "deployment_regression"), ("c2", "resource_exhaustion")]:
        (tmp_path / f"{cid}.json").write_text(json.dumps(_case(cid, typ)), encoding="utf-8")

    ex = _StubExecutor({"c1": "deployment_regression", "c2": "resource_exhaustion"})
    rounds_results, rounds_metrics, aggregate = await run_dataset(
        str(tmp_path), ex, repeat=3
    )
    assert len(rounds_results) == 3
    assert len(rounds_metrics) == 3
    assert aggregate["rounds"] == 3
    assert aggregate["top1_accuracy"]["mean"] == 1.0
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_runner.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.runner`）

- [ ] **Step 3: 实现 runner**

创建 `backend/app/evals/runner.py`：

```python
"""Orchestrate an eval run: load → per-case fixture_scope → execute → score → repeat.

Single-case isolation: an exception in one case becomes that case's error result;
the batch continues. Fixtures are injected per-case via fixture_scope so the
gateway returns fixed evidence and concurrent graph fan-out inherits the scope.
"""
import time
from typing import Any, Dict, List, Tuple

from app.evals.case_loader import load_cases
from app.evals.fixture_context import fixture_scope
from app.evals.metrics import aggregate_rounds, compute_metrics
from app.evals.scorer import CaseResult, score_case
from app.models.incident import IncidentTicket


def build_initial_state(case: Dict[str, Any]) -> Dict[str, Any]:
    case_id = case["case_id"]
    ticket = IncidentTicket(**case["ticket"])
    return {
        "run_id": f"eval-{case_id}",
        "thread_id": f"eval-{case_id}",
        "ticket": ticket,
        "evidence_items": [],
        "root_cause_candidates": [],
        "evidence_collection_results": [],
        "evidence_quality_score": 0.0,
        "step_count": 0,
    }


async def run_one_case(case: Dict[str, Any], executor) -> CaseResult:
    case_id = case["case_id"]
    fixtures = case.get("tool_fixtures", {}) or {}
    initial_state = build_initial_state(case)

    start = time.perf_counter()
    try:
        with fixture_scope(fixtures):
            final_state = await executor.execute(case_id, initial_state)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return score_case(case, final_state, latency_ms)
    except Exception as exc:  # single-case isolation
        latency_ms = int((time.perf_counter() - start) * 1000)
        return CaseResult.error_result(case_id, f"{type(exc).__name__}: {exc}", latency_ms)


async def run_dataset(
    dataset_path: str, executor, repeat: int = 1
) -> Tuple[List[List[CaseResult]], List[Dict[str, Any]], Dict[str, Any]]:
    cases = load_cases(dataset_path)
    rounds_results: List[List[CaseResult]] = []
    rounds_metrics: List[Dict[str, Any]] = []

    for _ in range(max(1, repeat)):
        case_results = [await run_one_case(case, executor) for case in cases]
        rounds_results.append(case_results)
        rounds_metrics.append(compute_metrics(case_results))

    aggregate = aggregate_rounds(rounds_metrics)
    return rounds_results, rounds_metrics, aggregate
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_runner.py -v`
Expected: PASS（5 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/runner.py backend/app/tests/test_eval_runner.py
git commit -m "backend: eval orchestration with per-case fixture scope and repeat rounds

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: replay_runner CLI（--mode / --repeat / --dataset / --output）

**Files:**
- Create: `backend/app/evals/replay_runner.py`
- Test: `backend/app/tests/test_eval_replay_cli.py`

- [ ] **Step 1: 写失败测试**

创建 `backend/app/tests/test_eval_replay_cli.py`：

```python
"""Tests for CLI wiring (arg parsing, executor selection, compare diff)."""
import pytest

from app.evals.replay_runner import build_arg_parser, make_executor, diff_compare
from app.evals.executors import DirectGraphExecutor, RunnerGraphExecutor


def test_parser_defaults():
    parser = build_arg_parser()
    args = parser.parse_args([])
    assert args.mode == "direct"
    assert args.repeat == 1
    assert args.dataset.endswith("datasets/")


def test_parser_custom():
    parser = build_arg_parser()
    args = parser.parse_args(
        ["--mode", "runner", "--repeat", "3", "--dataset", "d/", "--output", "o.json"]
    )
    assert args.mode == "runner"
    assert args.repeat == 3
    assert args.dataset == "d/"
    assert args.output == "o.json"


def test_make_executor_direct():
    assert isinstance(make_executor("direct"), DirectGraphExecutor)


def test_make_executor_runner():
    assert isinstance(make_executor("runner"), RunnerGraphExecutor)


def test_diff_compare_flags_mismatch():
    direct_state = {
        "root_cause_candidates": [{"incident_type": "deployment_regression"}],
        "status": "COMPLETED",
    }
    runner_state = {
        "root_cause_candidates": [{"incident_type": "resource_exhaustion"}],
        "status": "WAITING_HUMAN",
    }
    diff = diff_compare("c1", direct_state, runner_state)
    assert diff["case_id"] == "c1"
    assert diff["incident_type_match"] is False
    assert diff["status_match"] is False
    assert diff["direct_incident_type"] == "deployment_regression"
    assert diff["runner_incident_type"] == "resource_exhaustion"


def test_diff_compare_agrees():
    state = {
        "root_cause_candidates": [{"incident_type": "deployment_regression"}],
        "status": "COMPLETED",
    }
    diff = diff_compare("c1", state, dict(state))
    assert diff["incident_type_match"] is True
    assert diff["status_match"] is True
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_replay_cli.py -v`
Expected: FAIL（`ModuleNotFoundError: app.evals.replay_runner`）

- [ ] **Step 3: 实现 CLI**

创建 `backend/app/evals/replay_runner.py`：

```python
"""CLI entry: replay eval dataset through the graph with fixed fixtures.

Modes:
  direct  (default) full Graph-Quality eval, graph only.
  runner            subset Runtime-Fidelity eval, full GraphRunner chain.
  compare           run both paths per case, diff final incident_type / status to
                    catch GraphRunner changing semantics or dropping fields.

Real-LLM eval is manual/offline (never CI). Usage:
  python -m app.evals.replay_runner --mode direct --dataset app/evals/datasets/ --repeat 3
"""
import argparse
import asyncio
import os
import sys
from typing import Any, Dict, Optional

from app.evals.executors import DirectGraphExecutor, RunnerGraphExecutor
from app.evals.report import build_report, render_markdown, write_report
from app.evals.runner import run_dataset
from app.evals.case_loader import load_cases

_DEFAULT_DATASET = "app/evals/datasets/"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="replay_runner", description="OpsPilot offline eval")
    parser.add_argument("--mode", choices=["direct", "runner", "compare"], default="direct")
    parser.add_argument("--dataset", default=_DEFAULT_DATASET)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--output", default=None, help="JSON report path (md sibling auto-written)")
    return parser


def make_executor(mode: str):
    if mode == "runner":
        return RunnerGraphExecutor()
    return DirectGraphExecutor()


def _preflight_api_key() -> None:
    """Real-LLM eval needs a key for the active provider; fail fast if missing."""
    provider = os.getenv("LLM_PROVIDER", "minimax").lower()
    key_env = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "minimax": "MINIMAX_API_KEY",
    }.get(provider)
    if key_env and not os.getenv(key_env):
        print(
            f"[replay_runner] ERROR: LLM_PROVIDER={provider} requires {key_env}. "
            "Real-LLM eval cannot run without it.",
            file=sys.stderr,
        )
        sys.exit(2)


def _incident_type_of(state: Dict[str, Any]) -> Optional[str]:
    cands = state.get("root_cause_candidates") or []
    if not cands:
        return None
    top = cands[0]
    it = top.incident_type if hasattr(top, "incident_type") else top.get("incident_type")
    if it is None:
        return None
    return it.value if hasattr(it, "value") else str(it)


def _status_of(state: Dict[str, Any]) -> Optional[str]:
    s = state.get("status")
    if s is None:
        return None
    return s.value if hasattr(s, "value") else str(s)


def diff_compare(case_id: str, direct_state: Dict[str, Any], runner_state: Dict[str, Any]) -> Dict[str, Any]:
    d_type, r_type = _incident_type_of(direct_state), _incident_type_of(runner_state)
    d_status, r_status = _status_of(direct_state), _status_of(runner_state)
    return {
        "case_id": case_id,
        "direct_incident_type": d_type,
        "runner_incident_type": r_type,
        "incident_type_match": d_type == r_type,
        "direct_status": d_status,
        "runner_status": r_status,
        "status_match": d_status == r_status,
    }


async def _run_compare(dataset_path: str) -> Dict[str, Any]:
    cases = load_cases(dataset_path)
    direct, runner = DirectGraphExecutor(), RunnerGraphExecutor()
    diffs = []
    from app.evals.runner import build_initial_state
    from app.evals.fixture_context import fixture_scope

    for case in cases:
        fixtures = case.get("tool_fixtures", {}) or {}
        with fixture_scope(fixtures):
            d_state = await direct.execute(case["case_id"], build_initial_state(case))
        with fixture_scope(fixtures):
            r_state = await runner.execute(case["case_id"], build_initial_state(case))
        diffs.append(diff_compare(case["case_id"], d_state, r_state))

    return {
        "mode": "compare",
        "meta": {"real_llm": True, "ci_metric": False},
        "diffs": diffs,
        "mismatch_count": sum(
            1 for d in diffs if not (d["incident_type_match"] and d["status_match"])
        ),
    }


async def _run_async(args) -> int:
    if args.mode == "compare":
        report = await _run_compare(args.dataset)
        print(f"[compare] {report['mismatch_count']} mismatched case(s) of {len(report['diffs'])}")
        if args.output:
            write_report(report, args.output)
        return 0

    executor = make_executor(args.mode)
    rounds_results, rounds_metrics, aggregate = await run_dataset(
        args.dataset, executor, repeat=args.repeat
    )
    report = build_report(
        mode=args.mode,
        rounds_results=rounds_results,
        rounds_metrics=rounds_metrics,
        aggregate=aggregate,
    )
    print(render_markdown(report))
    if args.output:
        write_report(report, args.output)
        print(f"\n[replay_runner] report written to {args.output} (+ .md)")
    return 0


def main(argv=None) -> int:
    args = build_arg_parser().parse_args(argv)
    _preflight_api_key()
    return asyncio.run(_run_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_replay_cli.py -v`
Expected: PASS（6 passed）

- [ ] **Step 5: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/replay_runner.py backend/app/tests/test_eval_replay_cli.py
git commit -m "backend: replay_runner CLI with direct/runner/compare modes

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: 首期数据集（10-12 个 case）+ 端到端验收

**Files:**
- Create: `backend/app/evals/datasets/*.json`（每文件一个 case）
- Test: `backend/app/tests/test_eval_dataset_integrity.py`

> Fixture 写法采用 **minimal-fixture** 策略（已决策）：每个 case 只写「关心的」证据工具；未提供的只读工具由 gateway 返回受控空结果，graph 照常推进。

- [ ] **Step 1: 写数据集完整性测试**

创建 `backend/app/tests/test_eval_dataset_integrity.py`：

```python
"""The shipped dataset must load cleanly and cover every non-trivial IncidentType."""
from pathlib import Path

from app.evals.case_loader import load_cases
from app.models.incident_type import IncidentType

_DATASET_DIR = Path(__file__).resolve().parents[1] / "evals" / "datasets"

# unknown/other are degraded/edge labels, not required to have a dedicated case
_NOT_REQUIRED = {IncidentType.unknown.value, IncidentType.other.value}


def test_dataset_loads():
    cases = load_cases(str(_DATASET_DIR))
    assert len(cases) >= 10


def test_every_core_incident_type_has_a_case():
    cases = load_cases(str(_DATASET_DIR))
    covered = {c.get("expected", {}).get("incident_type") for c in cases}
    required = {t.value for t in IncidentType} - _NOT_REQUIRED
    missing = required - covered
    assert not missing, f"dataset missing cases for: {sorted(missing)}"


def test_has_approval_scenario():
    cases = load_cases(str(_DATASET_DIR))
    risks = {c.get("expected", {}).get("risk_decision") for c in cases}
    assert "NEEDS_APPROVAL" in risks
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_dataset_integrity.py -v`
Expected: FAIL（datasets 目录为空 → `EvalDatasetError: No case JSON files`）

- [ ] **Step 3: 创建数据集文件**

逐一创建以下 11 个文件（覆盖 9 个核心类型 + 1 个审批场景 + 1 个低风险终态）。

`backend/app/evals/datasets/case_01_deployment_regression.json`：

```json
{
  "case_id": "case_01_deployment_regression",
  "description": "发布后 5xx 升高，部署历史显示刚上线新版本",
  "ticket": {
    "ticket_id": "INC-EVAL-01",
    "title": "支付服务发布后 5xx 升高",
    "description": "发布 v2.3.1 后部分用户下单失败，错误率从 0.2% 升至 8%",
    "service": "payment-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_logs": {"logs": [{"level": "ERROR", "msg": "NullPointer in OrderHandler"}], "count": 42},
    "query_deployments": {"deployments": [{"version": "v2.3.1", "at": "30m ago"}], "count": 1},
    "query_metrics": {"metrics": {"error_rate": {"values": [0.08]}}}
  },
  "expected": {
    "incident_type": "deployment_regression",
    "risk_decision": "NEEDS_APPROVAL",
    "final_status": "WAITING_HUMAN"
  }
}
```

`backend/app/evals/datasets/case_02_resource_exhaustion.json`：

```json
{
  "case_id": "case_02_resource_exhaustion",
  "description": "内存耗尽 OOM，节点 MemoryPressure",
  "ticket": {
    "ticket_id": "INC-EVAL-02",
    "title": "订单服务 OOM 频繁重启",
    "description": "Pod 反复 OOMKilled，内存使用率持续 95% 以上",
    "service": "order-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_metrics": {"metrics": {"memory_usage": {"values": [0.96]}}},
    "query_k8s_nodes": {"status": "MemoryPressure", "summary": "node mem 96%"},
    "query_k8s_pods": {"pods": [{"name": "order-1", "restarts": 7, "lastState": "OOMKilled"}]}
  },
  "expected": {
    "incident_type": "resource_exhaustion"
  }
}
```

`backend/app/evals/datasets/case_03_dependency_failure.json`：

```json
{
  "case_id": "case_03_dependency_failure",
  "description": "下游依赖超时 503",
  "ticket": {
    "ticket_id": "INC-EVAL-03",
    "title": "网关大量 503 下游超时",
    "description": "调用 inventory-service 大量 timeout，503 比例升高",
    "service": "gateway-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_logs": {"logs": [{"level": "ERROR", "msg": "upstream timeout calling inventory-service"}], "count": 88},
    "query_metrics": {"metrics": {"error_rate": {"values": [0.12]}}}
  },
  "expected": {
    "incident_type": "dependency_failure"
  }
}
```

`backend/app/evals/datasets/case_04_database_failure.json`：

```json
{
  "case_id": "case_04_database_failure",
  "description": "DB 慢查询 + 锁等待",
  "ticket": {
    "ticket_id": "INC-EVAL-04",
    "title": "用户服务响应缓慢疑似 DB 慢查询",
    "description": "接口 P99 从 80ms 升至 4s，DB 连接数接近上限",
    "service": "user-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_db_slow_queries": {"queries": [{"sql": "SELECT * FROM users WHERE ...", "seconds": 12}]},
    "query_db_processlist": {"processes": [{"state": "Lock wait", "time": 30}]},
    "query_metrics": {"metrics": {"latency_p99": {"values": [4000]}}}
  },
  "expected": {
    "incident_type": "database_failure"
  }
}
```

`backend/app/evals/datasets/case_05_network_failure.json`：

```json
{
  "case_id": "case_05_network_failure",
  "description": "LB/DNS 链路异常",
  "ticket": {
    "ticket_id": "INC-EVAL-05",
    "title": "服务间歇性连接失败疑似网络",
    "description": "跨可用区调用间歇性 connection reset，DNS 解析偶发失败",
    "service": "checkout-service",
    "env": "staging",
    "severity": "P3",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_logs": {"logs": [{"level": "WARN", "msg": "connection reset by peer"}], "count": 25},
    "query_lb_health_status": {"status": "degraded", "summary": "2/5 backends unhealthy"}
  },
  "expected": {
    "incident_type": "network_failure"
  }
}
```

`backend/app/evals/datasets/case_06_traffic_anomaly.json`：

```json
{
  "case_id": "case_06_traffic_anomaly",
  "description": "流量突增导致过载",
  "ticket": {
    "ticket_id": "INC-EVAL-06",
    "title": "促销活动流量突增服务过载",
    "description": "QPS 从 2k 突增至 18k，无近期发布，资源被流量打满",
    "service": "catalog-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_metrics": {"metrics": {"qps": {"values": [18000]}, "error_rate": {"values": [0.06]}}},
    "query_deployments": {"deployments": [], "count": 0},
    "query_lb_traffic_metrics": {"status": "ok", "error_rate": 0.06, "summary": "qps 9x baseline"}
  },
  "expected": {
    "incident_type": "traffic_anomaly"
  }
}
```

`backend/app/evals/datasets/case_07_security_incident.json`：

```json
{
  "case_id": "case_07_security_incident",
  "description": "异常访问疑似入侵",
  "ticket": {
    "ticket_id": "INC-EVAL-07",
    "title": "管理接口异常高频访问疑似攻击",
    "description": "来自单一 IP 的 /admin 高频探测，伴随大量 401/403",
    "service": "admin-service",
    "env": "staging",
    "severity": "P1",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_logs": {"logs": [{"level": "WARN", "msg": "401 unauthorized /admin from 1.2.3.4 x3000"}], "count": 3000}
  },
  "expected": {
    "incident_type": "security_incident"
  }
}
```

`backend/app/evals/datasets/case_08_configuration_error.json`：

```json
{
  "case_id": "case_08_configuration_error",
  "description": "非发布的配置漂移",
  "ticket": {
    "ticket_id": "INC-EVAL-08",
    "title": "服务启动失败疑似配置错误",
    "description": "无代码发布，运维手工改了 ConfigMap 后服务无法连接缓存",
    "service": "session-service",
    "env": "staging",
    "severity": "P2",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_logs": {"logs": [{"level": "ERROR", "msg": "redis connection refused: wrong host in config"}], "count": 15},
    "query_deployments": {"deployments": [], "count": 0},
    "query_k8s_configmaps": {"status": "present", "summary": "redis.host changed 1h ago"}
  },
  "expected": {
    "incident_type": "configuration_error"
  }
}
```

`backend/app/evals/datasets/case_09_service_degradation.json`：

```json
{
  "case_id": "case_09_service_degradation",
  "description": "无明确归因的自身退化",
  "ticket": {
    "ticket_id": "INC-EVAL-09",
    "title": "服务整体变慢无明显单一原因",
    "description": "延迟缓慢上升，无发布、无明显资源瓶颈、无下游异常",
    "service": "search-service",
    "env": "staging",
    "severity": "P3",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_metrics": {"metrics": {"latency_p99": {"values": [900]}}},
    "query_deployments": {"deployments": [], "count": 0}
  },
  "expected": {
    "incident_type": "service_degradation"
  }
}
```

`backend/app/evals/datasets/case_10_deploy_prod_approval.json`：

```json
{
  "case_id": "case_10_deploy_prod_approval",
  "description": "生产发布回归，应进入审批门",
  "ticket": {
    "ticket_id": "INC-EVAL-10",
    "title": "生产支付发布回归需回滚审批",
    "description": "prod 环境发布后错误率飙升，回滚动作需人工审批",
    "service": "payment-service",
    "env": "prod",
    "severity": "P1",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_logs": {"logs": [{"level": "ERROR", "msg": "500 after release v9"}], "count": 120},
    "query_deployments": {"deployments": [{"version": "v9", "at": "15m ago"}], "count": 1}
  },
  "expected": {
    "incident_type": "deployment_regression",
    "risk_decision": "NEEDS_APPROVAL",
    "final_status": "WAITING_HUMAN"
  }
}
```

`backend/app/evals/datasets/case_11_low_risk_complete.json`：

```json
{
  "case_id": "case_11_low_risk_complete",
  "description": "低风险自愈路径，终态 COMPLETED",
  "ticket": {
    "ticket_id": "INC-EVAL-11",
    "title": "staging 单 Pod 假死可重启自愈",
    "description": "staging 环境单 Pod 无响应，重启即可恢复，低风险",
    "service": "notify-service",
    "env": "staging",
    "severity": "P3",
    "source": "manual"
  },
  "tool_fixtures": {
    "query_k8s_pods": {"pods": [{"name": "notify-3", "status": "NotReady"}], "status": "1 pod not ready"},
    "query_logs": {"logs": [{"level": "WARN", "msg": "healthcheck timeout"}], "count": 6}
  },
  "expected": {
    "incident_type": "service_degradation"
  }
}
```

- [ ] **Step 4: 跑数据集完整性测试确认通过**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_dataset_integrity.py -v`
Expected: PASS（3 passed）

- [ ] **Step 5: 评测框架全量单测（mock LLM，进 CI）**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/test_eval_*.py app/tests/test_incident_type.py app/tests/test_diagnose_structured.py -q`
Expected: PASS（全部）

- [ ] **Step 6: 后端全量回归（确认零破坏）**

Run: `cd backend && source venv/bin/activate && python -m pytest app/tests/ -x -q`
Expected: PASS（全绿）

- [ ] **Step 7: commit**

```bash
cd /Users/ouyangjinfeng/sre-agent
git add backend/app/evals/datasets/ backend/app/tests/test_eval_dataset_integrity.py
git commit -m "backend: seed offline eval dataset (11 cases covering core incident types)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: 真实 DeepSeek 端到端验收（手动，非 CI）

> 此步**不写测试**，是设计文档「验收」清单的人工执行。需要真实 `DEEPSEEK_API_KEY`。

**Files:** 无新增（运行既有 CLI）

- [ ] **Step 1: 确认 LLM 配置**

确认 `backend/.env` 设置 `LLM_PROVIDER=deepseek` 且 `DEEPSEEK_API_KEY` 已配置。

Run: `cd backend && source venv/bin/activate && python -c "import os; print('provider=', os.getenv('LLM_PROVIDER')); print('key set=', bool(os.getenv('DEEPSEEK_API_KEY')))"`
Expected: `provider= deepseek` / `key set= True`

- [ ] **Step 2: 跑 direct 模式 3 轮，输出报告**

Run:
```bash
cd backend && source venv/bin/activate && \
python -m app.evals.replay_runner --mode direct \
  --dataset app/evals/datasets/ --repeat 3 \
  --output /tmp/opspilot_eval_report.json
```
Expected:
- stdout 打印 Markdown 报告，含 Top1/Top3、Macro F1、混淆矩阵、per-class recall、unknown rate、风险/终态准确率，以及 3 轮均值 + min/max 波动。
- 报告顶部含「真实 LLM、非 CI 指标」声明。
- `/tmp/opspilot_eval_report.json` 与 `/tmp/opspilot_eval_report.md` 均生成。

- [ ] **Step 3: 验证 fixture 缺失/异常隔离（人工抽查）**

确认报告中：单个 case 若 executor 抛错被记为 error 并单列、不影响其余 case 评分（`error_count` 字段与 `error_cases` 列表）。

- [ ] **Step 4: 跑 compare 模式骨架（冒烟）**

Run:
```bash
cd backend && source venv/bin/activate && \
python -m app.evals.replay_runner --mode compare \
  --dataset app/evals/datasets/ \
  --output /tmp/opspilot_eval_compare.json
```
Expected: 打印 `[compare] N mismatched case(s) of M`，生成 compare JSON（direct vs runner 终态 incident_type/status diff）。

> 注：runner 模式命中真实 DB，需后端 DB 可用。此步验证骨架可运行，不要求 mismatch=0。

- [ ] **Step 5: 更新 ACTION_PLAN 进度**

将 `ACTION_PLAN.md` 中 Phase 8 / Task 8.1 标记为已完成，并记录评测命令与报告位置。

```bash
cd /Users/ouyangjinfeng/sre-agent
git add ACTION_PLAN.md
git commit -m "backend: mark Phase 8 Task 8.1 offline eval complete

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## 完成标准（对照设计文档「验收」）

- [x] `python -m app.evals.replay_runner --mode direct --dataset app/evals/datasets/ --repeat 3` 输出 JSON + Markdown，含 Top1/Top3、Macro F1、混淆矩阵、per-class recall、unknown rate、风险/终态准确率，及 N 轮均值 + 波动 → Task 13/15
- [x] 报告显式标注「真实 LLM、非 CI 指标」→ Task 10
- [x] 某 case 异常时单 case 隔离、不污染整批 → Task 12/15
- [x] 评测框架单元测试全部通过（mock LLM，确定）→ Task 6-13
- [x] 8.0 结构化根因单测通过，生产 graph 行为不变（checkpointer 默认 None）→ Task 1-5
- [x] compare 模式可运行（骨架），diff 终态业务字段 → Task 13/15

