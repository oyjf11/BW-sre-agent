from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import asyncio
import logging

from app.graph.state import IncidentAgentState, RunStatus
from app.models.incident import IncidentTicket
from app.models.triage import TriageResult
from app.models.evidence import EvidenceItem
from app.models.root_cause import RootCauseCandidate
from app.models.incident_type import IncidentType
from app.models.remediation import RemediationPlan, ActionSpec
from app.models.approval import ApprovalRequest
from app.models.rca import RcaReport
from app.models.planning import AgentTask, SpecialistAnalysis
from app.tools import gateway, ToolRequest
from app.llm_client import llm_client
from app.core.config import get_settings
from app.graph.evidence_utils import (
    EvidenceCollectionResult,
    classify_result,
    compute_quality_from_results,
)

logger = logging.getLogger(__name__)


MAX_STEPS = 30


def _has_deployment_evidence(items: List[EvidenceItem]) -> bool:
    for item in items:
        category = item.category if hasattr(item, "category") else item.get("category", "")
        if category == "deployments":
            return True
    return False


def intake_node(state: IncidentAgentState) -> IncidentAgentState:
    from app.normalizers import normalize_env, normalize_service, normalize_time_range

    ticket = state.get("ticket")
    if not ticket:
        raise ValueError("Ticket is required")

    if isinstance(ticket, dict):
        ticket = IncidentTicket(**ticket)

    # Normalize fields (idempotent if already normalized by IntakeService)
    try:
        ticket = ticket.model_copy(
            update={
                "env": normalize_env(ticket.env),
                "service": normalize_service(ticket.service),
                "time_range": normalize_time_range(ticket.time_range),
            }
        )
    except ValueError:
        pass  # Keep original if normalization fails (e.g. unknown env)

    state["ticket"] = ticket
    state["status"] = RunStatus.NEW
    state["step_count"] = state.get("step_count", 0) + 1
    state["evidence_items"] = []
    state["root_cause_candidates"] = []
    state["evidence_collection_results"] = []
    state["failed_evidence_tools"] = []

    return state


def _triage_by_rules(title: str, description: str, severity: str, service: str, env: str):
    """Stage 1: Rule-based triage for known patterns. Returns TriageResult or None."""
    text = f"{title} {description}".lower()

    # Deployment regression pattern
    if any(kw in text for kw in ["deploy", "rollback", "release", "版本", "发布", "回滚"]):
        return TriageResult(
            incident_type=IncidentType.deployment_regression.value,
            severity=severity or "P1",
            suspected_services=[service] if service else [],
            suggested_time_window={"start": "2h ago", "end": "now"},
            requires_immediate_human=env == "prod" and severity in ("P0", "P1"),
            rationale=f"Rule match: deployment/release keywords detected in '{title}'",
        )

    # Resource exhaustion pattern
    if any(kw in text for kw in ["cpu", "memory", "oom", "disk", "内存", "磁盘"]):
        return TriageResult(
            incident_type=IncidentType.resource_exhaustion.value,
            severity=severity or "P2",
            suspected_services=[service] if service else [],
            suggested_time_window={"start": "1h ago", "end": "now"},
            requires_immediate_human=False,
            rationale=f"Rule match: resource exhaustion keywords detected in '{title}'",
        )

    # Dependency failure pattern
    if any(
        kw in text
        for kw in ["timeout", "connection refused", "downstream", "依赖", "超时", "503", "502"]
    ):
        return TriageResult(
            incident_type=IncidentType.dependency_failure.value,
            severity=severity or "P2",
            suspected_services=[service] if service else [],
            suggested_time_window={"start": "1h ago", "end": "now"},
            requires_immediate_human=False,
            rationale=f"Rule match: dependency failure keywords detected in '{title}'",
        )

    return None


def _triage_by_llm(title: str, description: str, severity: str, service: str, env: str):
    """Stage 2: LLM-enhanced triage. Returns TriageResult or None."""
    triage_prompt = f"""Analyze this incident ticket and provide triage information:

Title: {title}
Description: {description}
Service: {service}
Environment: {env}
Original Severity: {severity}

Provide:
1. incident_type: (e.g., service_degradation, deployment_regression, resource_exhaustion, dependency_failure, security_incident)
2. severity: (P0, P1, P2, P3, P4)
3. suspected_services: list of service names that might be related
4. suggested_time_window: time range to look for evidence
5. requires_immediate_human: true/false
6. rationale: brief explanation of your triage decision

Respond in JSON format."""

    import json, re

    try:
        llm_response = llm_client.complete_sync(
            triage_prompt, system_prompt="你是一个SRE故障处理助手。请始终使用简体中文回复。"
        )
    except Exception:
        return None

    if not llm_response or llm_response == "fallback_response":
        return None

    try:
        json_match = re.search(r"\{.*\}", llm_response, re.DOTALL)
        if not json_match:
            return None
        llm_data = json.loads(json_match.group())

        tw = llm_data.get("suggested_time_window", {"start": "1h ago", "end": "now"})
        if isinstance(tw, str):
            tw = {"start": tw, "end": "now"}

        return TriageResult(
            incident_type=llm_data.get("incident_type", IncidentType.service_degradation.value),
            severity=llm_data.get("severity", severity or "P2"),
            suspected_services=llm_data.get("suspected_services", [service] if service else []),
            suggested_time_window=tw,
            requires_immediate_human=llm_data.get("requires_immediate_human", False),
            rationale=llm_data.get("rationale", f"LLM triage for: {title}"),
        )
    except Exception:
        return None


def _triage_fallback(title: str, severity: str, service: str):
    """Stage 3: Fallback triage when rules and LLM both fail."""
    return TriageResult(
        incident_type=IncidentType.service_degradation.value,
        severity=severity or "P2",
        suspected_services=[service] if service else [],
        suggested_time_window={"start": "1h ago", "end": "now"},
        requires_immediate_human=False,
        rationale=f"Fallback triage for: {title}",
    )


def triage_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    if not ticket:
        raise ValueError("Ticket is required for triage")

    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "")
    severity = ticket.severity if hasattr(ticket, "severity") else ticket.get("severity", "")
    title = ticket.title if hasattr(ticket, "title") else ticket.get("title", "unknown")
    description = (
        ticket.description if hasattr(ticket, "description") else ticket.get("description", "")
    )

    # Preserve original severity snapshot
    original_severity = severity

    # 3-stage triage: rules → LLM → fallback
    triage_result = _triage_by_rules(title, description, severity, service, env)
    if not triage_result:
        triage_result = _triage_by_llm(title, description, severity, service, env)
    if not triage_result:
        triage_result = _triage_fallback(title, severity, service)

    state["triage"] = triage_result
    state["status"] = RunStatus.TRIAGED
    state["step_count"] = state.get("step_count", 0) + 1

    # Mark run for human if requires_immediate_human
    if triage_result.requires_immediate_human:
        state["user_context"] = state.get("user_context") or {}
        state["user_context"]["requires_immediate_human"] = True
        state["user_context"]["original_severity"] = original_severity

    return state


def planner_node(state: IncidentAgentState) -> IncidentAgentState:
    from app.models.planning import InvestigationTask, InvestigationPlan

    triage = state.get("triage")
    if not triage:
        raise ValueError("Triage is required for planning")

    services = (
        triage.suspected_services
        if hasattr(triage, "suspected_services")
        else triage.get("suspected_services", [])
    )
    incident_type = (
        triage.incident_type
        if hasattr(triage, "incident_type")
        else triage.get("incident_type", "unknown")
    )
    env = ""
    ticket = state.get("ticket")
    if ticket:
        env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "")

    tasks = []
    task_idx = 0

    def _add(category, tool, priority, svc, extra_params=None):
        nonlocal task_idx
        task_idx += 1
        params = {"service": svc, "env": env}
        if extra_params:
            params.update(extra_params)
        tasks.append(
            InvestigationTask(
                task_id=f"task_{task_idx:03d}",
                category=category,
                tool_name=tool,
                priority=priority,
                params=params,
            )
        )

    def _add_db_tasks(svc: str, incident: str):
        if incident == IncidentType.resource_exhaustion.value:
            _add("db", "query_db_variables", 2, svc)
            _add("db", "query_db_processlist", 2, svc)
            _add("db", "query_db_slow_queries", 3, svc, {"threshold_seconds": 5})
        elif incident == IncidentType.dependency_failure.value:
            _add("db", "query_db_processlist", 2, svc)
            _add("db", "query_db_slow_queries", 2, svc, {"threshold_seconds": 5})
        elif incident == IncidentType.deployment_regression.value:
            _add("db", "query_db_slow_queries", 4, svc, {"threshold_seconds": 5})
        else:
            _add("db", "query_db_processlist", 3, svc)
            _add("db", "query_db_variables", 3, svc)

    def _add_k8s_tasks(svc: str, incident: str):
        if incident == IncidentType.resource_exhaustion.value:
            _add("k8s", "query_k8s_nodes", 1, svc)
            _add("k8s", "query_k8s_deployment_status", 2, svc)
            _add("k8s", "query_k8s_pods", 2, svc)
            _add("k8s", "query_k8s_hpa", 2, svc)
            _add("k8s", "query_k8s_events", 3, svc, {"limit": 20})
            _add("k8s", "query_k8s_resource_quotas", 3, svc)
            _add("k8s", "query_k8s_pod_logs_summary", 4, svc, {"tail_lines": 100})
            _add("k8s", "query_k8s_pvc", 4, svc)
        elif incident == IncidentType.dependency_failure.value:
            _add("k8s", "query_k8s_deployment_status", 2, svc)
            _add("k8s", "query_k8s_events", 2, svc, {"limit": 20})
            _add("k8s", "query_k8s_services", 2, svc)
            _add("k8s", "query_k8s_pod_logs_summary", 3, svc, {"tail_lines": 100})
            _add("k8s", "query_k8s_ingresses", 3, svc)
        elif incident == IncidentType.deployment_regression.value:
            _add("k8s", "query_k8s_deployment_status", 2, svc)
            _add("k8s", "query_k8s_pods", 3, svc)
            _add("k8s", "query_k8s_events", 3, svc, {"limit": 20})
            _add("k8s", "query_k8s_replicasets", 3, svc)
            _add("k8s", "query_k8s_configmaps", 4, svc)
        else:
            _add("k8s", "query_k8s_deployment_status", 3, svc)
            _add("k8s", "query_k8s_pods", 3, svc)
            _add("k8s", "query_k8s_nodes", 4, svc)
            _add("k8s", "query_k8s_services", 4, svc)
            _add("k8s", "query_k8s_hpa", 4, svc)
            _add("k8s", "query_k8s_statefulsets", 5, svc)
            _add("k8s", "query_k8s_daemonsets", 5, svc)
            _add("k8s", "query_k8s_jobs", 5, svc)

    if incident_type == IncidentType.deployment_regression.value:
        # Deployments + logs first
        for s in services:
            _add("deployments", "query_deployments", 1, s)
            _add("logs", "query_logs", 2, s)
            _add_k8s_tasks(s, incident_type)
            _add("metrics", "query_metrics", 3, s)
            _add_db_tasks(s, incident_type)
            _add("runbook", "query_runbook", 4, s, {"incident_type": incident_type})
        rationale = "Deployment regression: prioritize deployment history, K8s rollout state, logs, and DB slow query evidence"

    elif incident_type == IncidentType.resource_exhaustion.value:
        # Metrics + k8s first
        for s in services:
            _add("metrics", "query_metrics", 1, s)
            _add_k8s_tasks(s, incident_type)
            _add_db_tasks(s, incident_type)
            _add("logs", "query_logs", 3, s)
            _add("deployments", "query_deployments", 4, s)
            _add("runbook", "query_runbook", 5, s, {"incident_type": incident_type})
        rationale = "Resource exhaustion: prioritize metrics, K8s saturation signals, and DB capacity evidence"

    elif incident_type == IncidentType.dependency_failure.value:
        # Logs + history + lb first
        for s in services:
            _add("logs", "query_logs", 1, s)
            _add("metrics", "query_metrics", 2, s)
            _add_k8s_tasks(s, incident_type)
            _add_db_tasks(s, incident_type)
            _add("deployments", "query_deployments", 4, s)
            _add("runbook", "query_runbook", 3, s, {"incident_type": incident_type})
        rationale = "Dependency failure: prioritize logs, K8s events, DB waits, and service dependencies"

    else:
        # Unknown / generic: multi-path parallel
        for s in services:
            _add("logs", "query_logs", 2, s)
            _add("metrics", "query_metrics", 2, s)
            _add_k8s_tasks(s, incident_type)
            _add_db_tasks(s, incident_type)
            _add("deployments", "query_deployments", 3, s)
            _add("runbook", "query_runbook", 3, s, {"incident_type": incident_type})
        rationale = f"Generic investigation for incident type: {incident_type}, including K8s and DB diagnostics"

    investigation_plan = InvestigationPlan(tasks=tasks, rationale=rationale)
    state["investigation_plan"] = investigation_plan

    # Keep backward-compatible plan dict
    state["plan"] = {
        "tasks": [t.model_dump() for t in tasks],
        "rationale": rationale,
    }

    # --- Specialist Agent Pool (v2): generate AgentTask list ---
    settings = get_settings()
    if settings.agent_feature_specialist_pool:
        agent_tasks = _generate_agent_tasks(state)
        state["agent_tasks"] = [t.model_dump() for t in agent_tasks]

    state["status"] = RunStatus.PLANNED
    state["step_count"] = state.get("step_count", 0) + 1

    return state


def _generate_agent_tasks(state: IncidentAgentState) -> List:
    from app.models.planning import AgentTask
    from app.graph.nodes.specialist_agent import agent_id_for_category

    ticket = state.get("ticket")
    triage = state.get("triage")

    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "unknown")
    incident_type = (
        triage.incident_type if hasattr(triage, "incident_type")
        else triage.get("incident_type", "unknown")
    )

    categories = ["k8s", "db", "logs", "metrics", "deployments"]
    tasks = []
    for cat in categories:
        tasks.append(AgentTask(
            agent_id=agent_id_for_category(cat),
            category=cat,
            service=service,
            env=env,
            incident_type=incident_type,
        ))
    return tasks


async def evidence_fanout_node(state: IncidentAgentState) -> IncidentAgentState:
    settings = get_settings()

    if not settings.agent_feature_specialist_pool:
        return await _original_evidence_fanout(state)

    return await _evidence_fanout_v2(state)


async def _original_evidence_fanout(state: IncidentAgentState) -> IncidentAgentState:
    """Dynamic evidence fanout: dispatch tasks from InvestigationPlan in parallel."""
    investigation_plan = state.get("investigation_plan")
    plan = state.get("plan")
    run_id = state.get("run_id", "unknown")

    if not investigation_plan and not plan:
        raise ValueError("Plan is required for evidence gathering")

    state["status"] = RunStatus.GATHERING_EVIDENCE

    tasks_to_run = []
    if investigation_plan:
        for task in investigation_plan.tasks:
            tasks_to_run.append(
                (task.tool_name, task.params, task.category, task.degrade_on_failure)
            )
    elif plan:
        for t in plan.get("tasks", []):
            tasks_to_run.append(
                (
                    t["tool"],
                    t.get("params", {"service": t.get("service", ""), "env": ""}),
                    t.get("category", ""),
                    True,
                )
            )

    async def _collect_one(tool_name, params, category, degrade):
        try:
            req = ToolRequest(tool_name=tool_name, params=params, run_id=run_id)
            result = await gateway.call_tool(req)
            collected_at = datetime.utcnow().isoformat()
            latency = result.latency_ms

            if result.success and result.result:
                classification = classify_result(
                    tool_name, category, True, result.result, None, latency, collected_at
                )
                if classification.status == "SUCCESS_USABLE":
                    evidence = EvidenceItem(
                        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                        tool_name=tool_name,
                        category=category,
                        source_ref=f"{category}-{run_id}",
                        summary=classification.summary,
                        raw_payload=result.result,
                        confidence=0.8,
                        freshness_score=0.9,
                        completeness_score=0.7,
                    )
                    return (evidence, classification)
                else:
                    return (None, classification)
            else:
                classification = classify_result(
                    tool_name,
                    category,
                    False,
                    result.result if result else None,
                    result.error if result else "no response",
                    result.latency_ms if result else 0,
                    datetime.utcnow().isoformat(),
                )
                if not degrade:
                    raise RuntimeError(
                        f"Non-degradable task {tool_name} failed: {classification.error_summary}"
                    )
                return (None, classification)
        except Exception as e:
            if not degrade:
                raise
            classification = EvidenceCollectionResult(
                status="FAILED_RUNTIME",
                tool_name=tool_name,
                category=category,
                error_summary=str(e),
                latency_ms=0,
                collected_at=datetime.utcnow().isoformat(),
            )
            return (None, classification)

    results = await asyncio.gather(
        *[_collect_one(t, p, c, d) for t, p, c, d in tasks_to_run],
        return_exceptions=True,
    )

    evidence_items = state.get("evidence_items", [])
    collection_results: List[Dict[str, Any]] = state.get("evidence_collection_results", [])

    for r in results:
        if isinstance(r, Exception):
            continue
        if isinstance(r, tuple) and len(r) == 2:
            evidence, result_obj = r
            if evidence is not None:
                evidence_items.append(evidence)
            collection_results.append(result_obj.model_dump())

    state["evidence_items"] = evidence_items
    state["evidence_collection_results"] = collection_results
    state["step_count"] = state.get("step_count", 0) + 1

    return state


async def _evidence_fanout_v2(state: IncidentAgentState) -> IncidentAgentState:
    """v2 evidence fanout: dispatch Specialist Agents in parallel with ReAct loop."""
    from app.graph.nodes.specialist_agent import (
        load_agent_configs,
        SpecialistAgent,
        _build_default_agent_tasks,
        _build_llm_failed_shell_static,
    )

    run_id = state.get("run_id", "unknown")
    state["status"] = RunStatus.GATHERING_EVIDENCE

    ticket = state.get("ticket")
    agent_tasks_raw = state.get("agent_tasks") or []

    agent_configs = load_agent_configs()

    # Fallback level 2: convert plan tasks to agent tasks
    if not agent_tasks_raw:
        plan = state.get("plan") or {}
        plan_tasks = plan.get("tasks", [])
        if plan_tasks:
            agent_tasks_raw = _fallback_from_plan_to_agent_tasks(plan_tasks, ticket)

    # Fallback level 3: generate default agent tasks
    if not agent_tasks_raw:
        agent_tasks_raw = [
            t.model_dump() for t in _build_default_agent_tasks(ticket)
        ]

    agent_tasks = [
        AgentTask(**t) if isinstance(t, dict) else t
        for t in agent_tasks_raw
    ]

    results: List[SpecialistAnalysis] = []
    specialist_results: List[Dict[str, Any]] = []

    # Filter enabled agent tasks
    enabled_tasks = []
    for task in agent_tasks:
        config = agent_configs.get(task.agent_id)
        if config and config.enabled:
            enabled_tasks.append(task)
        else:
            specialist_results.append(_build_llm_failed_shell_static(
                task.agent_id, task.category
            ).model_dump())

    if enabled_tasks:
        try:
            gathered = await asyncio.wait_for(
                asyncio.gather(*[
                    SpecialistAgent(agent_configs[t.agent_id]).run(t, run_id)
                    for t in enabled_tasks
                ], return_exceptions=True),
                timeout=150.0,
            )
        except asyncio.TimeoutError:
            gathered = [TimeoutError("fanout total timeout") for _ in enabled_tasks]

        evidence_items = state.get("evidence_items", [])

        for task, result in zip(enabled_tasks, gathered):
            if isinstance(result, Exception):
                result = _build_llm_failed_shell_static(task.agent_id, task.category)

            # Atomic agent-level write
            agent_evidence: List[EvidenceItem] = []
            for tool_name, raw_data in result.raw_tool_results.items():
                agent_evidence.append(_build_raw_evidence_item(
                    tool_name, raw_data, result, run_id
                ))

            try:
                evidence_items.extend(agent_evidence)
                specialist_results.append(result.model_dump())
            except Exception:
                evidence_set = set(id(e) for e in agent_evidence)
                evidence_items = [e for e in evidence_items if id(e) not in evidence_set]
                specialist_results.append(_build_llm_failed_shell_static(
                    task.agent_id, task.category
                ).model_dump())

        state["evidence_items"] = evidence_items

    state["specialist_analyses"] = specialist_results
    state["step_count"] = state.get("step_count", 0) + 1
    return state


def _fallback_from_plan_to_agent_tasks(plan_tasks: List[Dict], ticket: Any) -> List[Dict[str, Any]]:
    from app.graph.nodes.specialist_agent import agent_id_for_category

    category_map = {
        "k8s": "k8s", "db": "db", "logs": "logs",
        "metrics": "metrics", "deployments": "deployments",
    }
    seen_categories = set()
    agent_tasks = []

    for pt in plan_tasks:
        cat = pt.get("category", "")
        mapped = category_map.get(cat)
        if mapped and mapped not in seen_categories:
            seen_categories.add(mapped)
            service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
            env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "unknown")
            agent_tasks.append(AgentTask(
                agent_id=agent_id_for_category(mapped),
                category=mapped,
                service=service,
                env=env,
            ).model_dump())

    return agent_tasks


def _build_raw_evidence_item(
    tool_name: str,
    raw_data: Any,
    analysis: SpecialistAnalysis,
    run_id: str,
) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=f"ev_{tool_name}_{analysis.agent_id}_{uuid.uuid4().hex[:8]}",
        tool_name=tool_name,
        category=analysis.agent_category,
        source_ref=f"{analysis.agent_category}-{run_id}",
        summary=f"Raw data from {tool_name} (Agent: {analysis.agent_id})",
        raw_payload=raw_data,
        confidence=0.7,
        freshness_score=0.8,
        completeness_score=0.6,
    )


async def _call_tool_async(tool_name: str, params: Dict[str, Any], run_id: str):
    req = ToolRequest(tool_name=tool_name, params=params, run_id=run_id)
    return await gateway.call_tool(req)


async def logs_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod")
    run_id = state.get("run_id", "unknown")

    result = await _call_tool_async("query_logs", {"service": service, "env": env}, run_id)

    if result.success:
        evidence = EvidenceItem(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            tool_name="query_logs",
            category="logs",
            source_ref=f"query-{run_id}",
            summary=f"Retrieved {result.result.get('count', 0)} logs for {service}",
            raw_payload=result.result,
            confidence=0.8,
            freshness_score=0.9,
            completeness_score=0.7,
        )
        items = state.get("evidence_items", [])
        items.append(evidence)
        state["evidence_items"] = items

    state["step_count"] = state.get("step_count", 0) + 1
    return state


async def metrics_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod")
    run_id = state.get("run_id", "unknown")

    result = await _call_tool_async("query_metrics", {"service": service, "env": env}, run_id)

    if result.success:
        evidence = EvidenceItem(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            tool_name="query_metrics",
            category="metrics",
            source_ref=f"metrics-{run_id}",
            summary=f"Retrieved metrics for {service}",
            raw_payload=result.result,
            confidence=0.9,
            freshness_score=0.9,
            completeness_score=0.8,
        )
        items = state.get("evidence_items", [])
        items.append(evidence)
        state["evidence_items"] = items

    state["step_count"] = state.get("step_count", 0) + 1
    return state


async def deployments_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod")
    run_id = state.get("run_id", "unknown")

    result = await _call_tool_async("query_deployments", {"service": service, "env": env}, run_id)

    if result.success:
        evidence = EvidenceItem(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            tool_name="query_deployments",
            category="deployments",
            source_ref=f"deployments-{run_id}",
            summary=f"Retrieved {result.result.get('count', 0)} deployments for {service}",
            raw_payload=result.result,
            confidence=0.85,
            freshness_score=0.8,
            completeness_score=0.7,
        )
        items = state.get("evidence_items", [])
        items.append(evidence)
        state["evidence_items"] = items

    state["step_count"] = state.get("step_count", 0) + 1
    return state


async def runbook_node(state: IncidentAgentState) -> IncidentAgentState:
    ticket = state.get("ticket")
    triage = state.get("triage")
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod")
    incident_type = (
        triage.incident_type
        if hasattr(triage, "incident_type")
        else triage.get("incident_type", "general")
    )
    run_id = state.get("run_id", "unknown")

    result = await _call_tool_async(
        "query_runbook", {"service": service, "env": env, "incident_type": incident_type}, run_id
    )

    if result.success:
        evidence = EvidenceItem(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            tool_name="query_runbook",
            category="runbook",
            source_ref=f"runbook-{run_id}",
            summary=f"Retrieved runbooks for {service}",
            raw_payload=result.result,
            confidence=0.9,
            freshness_score=0.95,
            completeness_score=0.9,
        )
        items = state.get("evidence_items", [])
        items.append(evidence)
        state["evidence_items"] = items

    state["step_count"] = state.get("step_count", 0) + 1
    return state


def evidence_aggregate_node(state: IncidentAgentState) -> IncidentAgentState:
    settings = get_settings()

    if settings.agent_feature_specialist_pool and state.get("specialist_analyses"):
        return _evidence_aggregate_v2(state)

    return _original_evidence_aggregate(state)
def _original_evidence_aggregate(state: IncidentAgentState) -> IncidentAgentState:
    items = state.get("evidence_items", [])
    collection_results_raw = state.get("evidence_collection_results", [])

    collection_results = [
        EvidenceCollectionResult(**r) if isinstance(r, dict) else r
        for r in collection_results_raw
    ]

    quality_score, missing, failed_tools = compute_quality_from_results(collection_results)

    categories = {}
    total_confidence = 0.0
    for item in items:
        cat = item.category if hasattr(item, "category") else item.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        total_confidence += item.confidence if hasattr(item, "confidence") else 0.5

    summary = f"Collected {len(items)} usable evidence items from {len(collection_results)} tasks. "
    if categories:
        summary += "Categories: " + ", ".join(f"{k}: {v}" for k, v in categories.items())
    if failed_tools:
        summary += f" Failed tools: {', '.join(failed_tools)}."

    if not items:
        quality_score = 0.0

    contradiction_signals = []
    summaries_text = " ".join(
        (item.summary if hasattr(item, "summary") else item.get("summary", "")) for item in items
    ).lower()
    if "error" in summaries_text and "healthy" in summaries_text:
        contradiction_signals.append("mixed_health_signals")

    if contradiction_signals:
        summary += f" Contradictions: {', '.join(contradiction_signals)}"

    state["evidence_summary"] = summary
    state["evidence_quality_score"] = quality_score
    state["missing_evidence_categories"] = missing
    state["failed_evidence_tools"] = failed_tools
    state["step_count"] = state.get("step_count", 0) + 1

    return state


def _evidence_aggregate_v2(state: IncidentAgentState) -> IncidentAgentState:
    from app.graph.nodes.aggregator import (
        _build_correlation_graph,
        _infer_causal_chains,
        _detect_cross_agent_contradictions,
        _compute_weighted_quality,
        _format_global_summary,
    )

    analyses_raw: List[Dict[str, Any]] = state.get("specialist_analyses", [])

    analyses: List[SpecialistAnalysis] = []
    for a in analyses_raw:
        if isinstance(a, dict):
            try:
                analyses.append(SpecialistAnalysis(**a))
            except Exception:
                continue
        elif isinstance(a, SpecialistAnalysis):
            analyses.append(a)

    graph = _build_correlation_graph(analyses)
    causal_chains = _infer_causal_chains(graph, analyses)
    contradictions = _detect_cross_agent_contradictions(analyses)
    quality_score = _compute_weighted_quality(analyses)
    summary = _format_global_summary(analyses, quality_score, contradictions, causal_chains)

    state["evidence_summary"] = summary
    state["evidence_quality_score"] = quality_score
    state["cross_agent_causal_chains"] = causal_chains
    state["contradiction_signals"] = contradictions
    state["missing_evidence_categories"] = []
    state["failed_evidence_tools"] = []
    state["step_count"] = state.get("step_count", 0) + 1

    return state


def _coerce_incident_type(raw: Any) -> "IncidentType":
    """Validate an LLM-provided incident_type into the closed enum.

    - Valid enum value -> that member.
    - Missing / None -> unknown (insufficient signal).
    - Non-empty but illegal -> other (model decided a cause outside the taxonomy).
    """
    if isinstance(raw, IncidentType):
        return raw
    if raw is None:
        return IncidentType.unknown
    value = str(raw).strip()
    if value == "":
        return IncidentType.unknown
    try:
        return IncidentType(value)
    except ValueError:
        logger.warning("diagnose: illegal incident_type %r -> downgraded to 'other'", raw)
        return IncidentType.other


def diagnose_node(state: IncidentAgentState) -> IncidentAgentState:
    import logging

    logger = logging.getLogger(__name__)
    logger.info("DIAGNOSE_NODE: Starting execution")

    ticket = state.get("ticket")
    triage = state.get("triage")
    items = state.get("evidence_items", [])

    # Build evidence summary for LLM
    evidence_summary = []
    for item in items:
        cat = item.category if hasattr(item, "category") else item.get("category", "unknown")
        summary = item.summary if hasattr(item, "summary") else item.get("summary", "")
        raw = item.raw_payload if hasattr(item, "raw_payload") else item.get("raw_payload", {})

        if cat == "logs" and isinstance(raw, dict):
            log_count = raw.get("count", 0)
            evidence_summary.append(f"- Logs: {log_count} entries retrieved")
        elif cat == "metrics" and isinstance(raw, dict):
            metrics_names = list(raw.get("metrics", {}).keys())
            evidence_summary.append(
                f"- Metrics: {', '.join(metrics_names) if metrics_names else 'retrieved'}"
            )
        elif cat == "deployments" and isinstance(raw, dict):
            deploy_count = raw.get("count", 0)
            evidence_summary.append(f"- Deployments: {deploy_count} recent deployments")
        elif cat == "runbook" and isinstance(raw, dict):
            rb_count = raw.get("count", 0)
            evidence_summary.append(f"- Runbooks: {rb_count} available")

    evidence_text = "\n".join(evidence_summary) if evidence_summary else "No evidence collected"

    ticket_title = ticket.title if hasattr(ticket, "title") else ticket.get("title", "unknown")
    ticket_desc = (
        ticket.description if hasattr(ticket, "description") else ticket.get("description", "")
    )
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "unknown")
    incident_type = (
        triage.incident_type
        if hasattr(triage, "incident_type")
        else triage.get("incident_type", "unknown")
    )
    incident_type_values = ", ".join(t.value for t in IncidentType)

    # LLM prompt for root cause analysis
    diagnose_prompt = f"""Analyze this incident and provide root cause candidates.

## Incident
- Title: {ticket_title}
- Description: {ticket_desc}
- Service: {service}
- Environment: {env}
- Incident Type: {incident_type}

## Collected Evidence
{evidence_text}

Provide 2-3 root cause candidates in JSON format:
[
  {{
    "incident_type": "EXACTLY ONE of: {incident_type_values}",
    "hypothesis": "brief description of possible root cause",
    "confidence": 0.0-1.0,
    "next_checks": ["action to verify", "another check"]
  }}
]

incident_type rules:
- Use exactly one value from this closed enum: {incident_type_values}.
- Use "unknown" when evidence is insufficient to choose a cause.
- Use "other" only when you have a concrete cause outside this taxonomy.

Respond in JSON format only."""

    # Call LLM
    import json
    import logging

    logger = logging.getLogger(__name__)
    logger.info("DIAGNOSE_NODE: Calling LLM...")
    llm_response = ""
    try:
        llm_response = llm_client.complete_sync(
            diagnose_prompt, system_prompt="你是一个SRE故障诊断助手。请始终使用简体中文回复。"
        )
        logger.info(f"DIAGNOSE_NODE: LLM response: {llm_response[:100]}...")
    except Exception as e:
        logger.error(f"DIAGNOSE_NODE: LLM call failed: {e}")
        llm_response = ""

    candidates = []

    # Parse LLM response
    if llm_response and llm_response != "fallback_response":
        try:
            import re

            json_match = re.search(r"\[[\s\S]*\]", llm_response)
            if json_match:
                llm_candidates = json.loads(json_match.group())
                if isinstance(llm_candidates, list):
                    for index, c in enumerate(llm_candidates[:3]):
                        if not isinstance(c, dict):
                            logger.warning(
                                "diagnose: skipping invalid candidate at index %s: "
                                "expected object, got %s",
                                index,
                                type(c).__name__,
                            )
                            continue
                        try:
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
                        except Exception as e:
                            logger.warning(
                                "diagnose: skipping invalid candidate at index %s: %s",
                                index,
                                e,
                            )
                            continue
                        candidates.append(candidate)
                else:
                    logger.warning(
                        "diagnose: expected LLM candidates array, got %s",
                        type(llm_candidates).__name__,
                    )
            else:
                logger.warning("diagnose: LLM response did not contain a candidate array")
        except Exception as e:
            logger.warning("diagnose: failed to parse LLM candidates: %s", e)

    # Fallback if LLM failed
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

    candidates.sort(
        key=lambda c: c.confidence if hasattr(c, "confidence") else 0.0,
        reverse=True,
    )

    state["root_cause_candidates"] = candidates
    state["status"] = RunStatus.DIAGNOSED
    state["step_count"] = state.get("step_count", 0) + 1

    return state


def critic_node(state: IncidentAgentState) -> IncidentAgentState:
    """Critic with 4-way routing: PASS / NEED_MORE_EVIDENCE / REPLAN / CONTRADICTION.
    Includes loop guard: max 2 loops, then NEEDS_HUMAN with terminal_reason."""
    items = state.get("evidence_items", [])
    candidates = state.get("root_cause_candidates", [])
    quality_score = state.get("evidence_quality_score") or 0.5
    missing = state.get("missing_evidence_categories") or []
    failed_tools = state.get("failed_evidence_tools") or []

    loop_count = state.get("loop_count") or 0
    max_loop = state.get("max_loop_count") or 2

    if loop_count >= max_loop:
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_critic"
        state["terminal_reason"] = {
            "code": "EVIDENCE_LOOP_EXHAUSTED",
            "stage": "critic",
            "message": (
                f"Evidence loop exhausted after {loop_count} rounds. "
                f"Quality: {quality_score}, missing: {missing}, failed tools: {failed_tools}"
            ),
            "missing_evidence_categories": missing,
            "failed_tools": failed_tools,
        }
        state["user_context"] = state.get("user_context") or {}
        state["user_context"]["loop_guard_triggered"] = True
        state["user_context"]["requires_immediate_human"] = True
        for c in candidates:
            if hasattr(c, "confidence"):
                c.confidence = min(c.confidence, 0.5)
        state["root_cause_candidates"] = candidates
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    has_contradiction = False
    for candidate in candidates:
        contradicting = (
            candidate.contradicting_evidence_ids
            if hasattr(candidate, "contradicting_evidence_ids")
            else []
        )
        if len(contradicting) > 0:
            has_contradiction = True
            break

    if has_contradiction:
        state["critic_decision"] = "CONTRADICTION"
        state["loop_count"] = loop_count + 1
    elif quality_score < 0.4 or len(missing) >= 2:
        state["critic_decision"] = "NEED_MORE_EVIDENCE"
        state["loop_count"] = loop_count + 1
    elif quality_score < 0.3 and len(items) < 2:
        state["critic_decision"] = "REPLAN"
        state["loop_count"] = loop_count + 1
    else:
        state["critic_decision"] = "PASS"

    state["step_count"] = state.get("step_count", 0) + 1
    return state


def remediation_node(state: IncidentAgentState) -> IncidentAgentState:
    candidates = state.get("root_cause_candidates", [])
    ticket = state.get("ticket")
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod")
    evidence_items = state.get("evidence_items", [])

    valid_evidence_ids = [
        ev.evidence_id if hasattr(ev, "evidence_id") else ev.get("evidence_id", "")
        for ev in evidence_items
        if ev is not None
    ]
    valid_evidence_ids = [eid for eid in valid_evidence_ids if eid]

    actions = []
    if candidates and valid_evidence_ids:
        top_candidate = candidates[0]
        has_deployment_signal = (
            "deployment" in top_candidate.hypothesis.lower()
            and _has_deployment_evidence(evidence_items)
        )
        if has_deployment_signal:
            action = ActionSpec(
                action_type="rollback",
                service=service,
                env=env,
                params={"version": "previous"},
                risk_level="HIGH",
                requires_approval=True,
                supporting_evidence_ids=valid_evidence_ids,
            )
            actions.append(action)
        else:
            action = ActionSpec(
                action_type="restart",
                service=service,
                env=env,
                params={},
                risk_level="LOW",
                requires_approval=False,
                supporting_evidence_ids=valid_evidence_ids,
            )
            actions.append(action)

    if not actions:
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_remediation"
        state["terminal_reason"] = {
            "code": "CANNOT_GENERATE_TRUSTED_ACTIONS",
            "stage": "remediation",
            "message": "No valid evidence to support any automated remediation action",
            "missing_evidence_categories": state.get("missing_evidence_categories", []),
            "failed_tools": state.get("failed_evidence_tools", []),
        }
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    plan = RemediationPlan(
        summary=f"Proposed {len(actions)} remediation actions",
        actions=actions,
        expected_outcome="Service should recover",
        rollback_plan="Rollback to previous version if needed",
    )

    state["remediation_plan"] = plan
    state["status"] = RunStatus.PLANNED
    state["step_count"] = state.get("step_count", 0) + 1

    return state


def risk_gate_node(state: IncidentAgentState) -> IncidentAgentState:
    """Risk decision: LOW_ONLY / NEEDS_APPROVAL / BLOCKED / NEEDS_HUMAN.
    Combines: action risk + severity + env + triage human-priority + diagnosis confidence
    + loop guard + capability preflight."""
    plan = state.get("remediation_plan")
    if not plan:
        state["risk_decision"] = "LOW_ONLY"
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    actions = plan.actions if hasattr(plan, "actions") else plan.get("actions", [])
    if not actions:
        state["risk_decision"] = "LOW_ONLY"
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    ticket = state.get("ticket")
    env = ""
    severity = "P3"
    if ticket:
        env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "")
        severity = ticket.severity if hasattr(ticket, "severity") else ticket.get("severity", "P3")

    user_ctx = state.get("user_context") or {}
    loop_guard_triggered = user_ctx.get("loop_guard_triggered", False)
    requires_human_from_triage = user_ctx.get("requires_immediate_human", False)

    candidates = state.get("root_cause_candidates", [])
    top_confidence = (
        candidates[0].confidence if candidates and hasattr(candidates[0], "confidence") else 0.5
    )

    high_risk_actions = [
        a
        for a in actions
        if (a.risk_level if hasattr(a, "risk_level") else a.get("risk_level", "LOW"))
        in ["HIGH", "CRITICAL"]
    ]

    actions_requiring_approval = [
        a
        for a in actions
        if (
            a.requires_approval if hasattr(a, "requires_approval") else a.get("requires_approval", False)
        )
    ]

    critical_actions = [
        a
        for a in actions
        if (a.risk_level if hasattr(a, "risk_level") else a.get("risk_level", "LOW")) == "CRITICAL"
    ]

    # Capability preflight: check if execute_action is available
    action_types = [
        a.action_type if hasattr(a, "action_type") else a.get("action_type", "")
        for a in actions
    ]
    unavailable_actions = []
    for at in action_types:
        if at and not _can_execute_action(action_type=at, env=env, service=(
            actions[0].service if hasattr(actions[0], "service") else actions[0].get("service", "")
        )):
            unavailable_actions.append(at)

    if unavailable_actions:
        state["status"] = RunStatus.NEEDS_HUMAN
        state["halted_at_node"] = "node_risk_gate"
        state["terminal_reason"] = {
            "code": "AUTOMATION_CAPABILITY_UNAVAILABLE",
            "stage": "risk_gate",
            "message": f"execute_action real adapter is not configured for: {', '.join(unavailable_actions)}",
            "failed_tools": ["execute_action"],
            "missing_evidence_categories": state.get("missing_evidence_categories", []),
        }
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    if critical_actions and env == "prod" and (top_confidence < 0.5 or loop_guard_triggered):
        state["risk_decision"] = "BLOCKED"
        state["status"] = RunStatus.FAILED
        state["error"] = {
            "code": "RISK_BLOCKED",
            "message": "Critical action blocked: low confidence in prod environment",
            "node_name": "risk_gate",
            "retryable": False,
            "details": None,
        }
    elif actions_requiring_approval or high_risk_actions or loop_guard_triggered:
        state["risk_decision"] = "NEEDS_APPROVAL"
    else:
        state["risk_decision"] = "LOW_ONLY"

    state["step_count"] = state.get("step_count", 0) + 1
    return state


def _can_execute_action(action_type: str, env: str, service: str) -> bool:
    try:
        descriptor = gateway.describe_capability("execute_action")
        return descriptor.get("available", False)
    except Exception:
        return False


def approval_interrupt_node(state: IncidentAgentState) -> IncidentAgentState:
    plan = state.get("remediation_plan")
    ticket = state.get("ticket")

    if not plan or not ticket:
        raise ValueError("Remediation plan and ticket required")

    actions = plan.actions if hasattr(plan, "actions") else plan.get("actions", [])
    severity = ticket.severity if hasattr(ticket, "severity") else ticket.get("severity", "P3")
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod")

    if actions:
        action = actions[0]
        risk_level = (
            action.risk_level
            if hasattr(action, "risk_level")
            else action.get("risk_level", "MEDIUM")
        )

        approval_id = f"apr_{uuid.uuid4().hex[:8]}"
        reason = plan.summary if hasattr(plan, "summary") else plan.get("summary", "")
        expected_impact = (
            plan.expected_outcome
            if hasattr(plan, "expected_outcome")
            else plan.get("expected_outcome", "Service recovery expected")
        )
        rollback_plan = (
            plan.rollback_plan if hasattr(plan, "rollback_plan") else plan.get("rollback_plan")
        )

        approval = ApprovalRequest(
            approval_id=approval_id,
            run_id=state.get("run_id", "unknown"),
            action=action,
            reason=reason,
            risk_level=risk_level,
            evidence_refs=[],
            expected_impact=expected_impact,
            rollback_plan=rollback_plan,
        )
        state["pending_approval"] = approval

        # Persist to DB so the approval is queryable immediately
        try:
            from app.repositories import SessionLocal, ApprovalsRepo
            from datetime import datetime
            import logging
            import traceback

            _logger = logging.getLogger(__name__)
            _logger.info(
                f"approval_interrupt_node: persisting approval, action type={type(action).__name__}"
            )

            if hasattr(action, "model_dump"):
                action_dict = action.model_dump()
            elif isinstance(action, dict):
                action_dict = action
            else:
                action_dict = {
                    "action_type": getattr(action, "action_type", "unknown"),
                    "service": getattr(action, "service", "unknown"),
                    "env": getattr(action, "env", "unknown"),
                    "params": getattr(action, "params", {}),
                    "risk_level": getattr(action, "risk_level", "MEDIUM"),
                }

            _logger.info(f"approval_interrupt_node: action_dict={action_dict}")

            db = SessionLocal()
            try:
                approvals_repo = ApprovalsRepo(db)
                # Create approval record with explicit timestamps
                from app.models.db_models import IncidentApproval

                approval_record = IncidentApproval(
                    approval_id=approval_id,
                    run_id=state.get("run_id", "unknown"),
                    action_json=action_dict,
                    risk_level=risk_level,
                    status="PENDING",
                    reason=reason,
                    expected_impact=expected_impact,
                    rollback_plan=rollback_plan,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(approval_record)
                db.commit()
                db.refresh(approval_record)
                _logger.info(
                    f"approval_interrupt_node: approval {approval_id} persisted successfully"
                )
            except Exception as db_err:
                db.rollback()
                _logger.error(
                    f"approval_interrupt_node: DB error: {db_err}\n{traceback.format_exc()}"
                )
                raise
            finally:
                db.close()
        except Exception as _e:
            import logging
            import traceback

            logging.getLogger(__name__).warning(
                f"approval_interrupt_node: failed to persist approval: {_e}\n{traceback.format_exc()}"
            )

            if hasattr(action, "model_dump"):
                action_dict = action.model_dump()
            elif isinstance(action, dict):
                action_dict = action
            else:
                action_dict = {
                    "action_type": getattr(action, "action_type", "unknown"),
                    "service": getattr(action, "service", "unknown"),
                    "env": getattr(action, "env", "unknown"),
                    "params": getattr(action, "params", {}),
                    "risk_level": getattr(action, "risk_level", "MEDIUM"),
                }

            _logger.info(f"approval_interrupt_node: action_dict={action_dict}")

            db = SessionLocal()
            try:
                approvals_repo = ApprovalsRepo(db)
                approvals_repo.create(
                    run_id=state.get("run_id", "unknown"),
                    action=action_dict,
                    risk_level=risk_level,
                    approval_id=approval_id,
                    reason=reason,
                    expected_impact=expected_impact,
                    rollback_plan=rollback_plan,
                )
                _logger.info(
                    f"approval_interrupt_node: approval {approval_id} persisted successfully"
                )
            finally:
                db.close()
        except Exception as _e:
            import logging
            import traceback

            logging.getLogger(__name__).warning(
                f"approval_interrupt_node: failed to persist approval: {_e}\n{traceback.format_exc()}"
            )

    state["status"] = RunStatus.WAITING_HUMAN
    state["step_count"] = state.get("step_count", 0) + 1

    return state


async def executor_node(state: IncidentAgentState) -> IncidentAgentState:
    plan = state.get("remediation_plan")
    run_id = state.get("run_id", "unknown")

    if not plan:
        state["status"] = RunStatus.FAILED
        state["error"] = {
            "code": "NO_PLAN",
            "message": "No remediation plan",
            "node_name": "executor",
            "retryable": False,
            "details": None,
        }
        return state

    actions = plan.actions if hasattr(plan, "actions") else plan.get("actions", [])

    # Debug logging
    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        f"executor_node: plan type={type(plan).__name__}, actions type={type(actions).__name__}, len={len(actions) if actions else 0}"
    )
    for i, a in enumerate(actions):
        logger.info(f"  action[{i}]: type={type(a).__name__}, value={a}")

    # Normalize actions to dicts for ControlledExecutor
    action_dicts = []
    for a in actions:
        if a is None:
            logger.warning("Skipping None action")
            continue
        if hasattr(a, "model_dump"):
            action_dicts.append(a.model_dump())
        elif isinstance(a, dict):
            # Already a dict (e.g. deserialized from checkpoint)
            action_dicts.append(a)
        elif hasattr(a, "action_type"):
            action_dicts.append(
                {
                    "action_type": a.action_type,
                    "service": a.service,
                    "env": a.env,
                    "params": a.params,
                    "idempotency_key": getattr(a, "idempotency_key", None),
                    "preconditions": getattr(a, "preconditions", None),
                }
            )
        else:
            logger.warning(f"Unknown action type: {type(a).__name__}, appending as-is")
            action_dicts.append(a)

    logger.info(f"Normalized actions: {len(action_dicts)} actions")
    for i, a in enumerate(action_dicts):
        logger.info(
            f"  action_dict[{i}]: type={type(a).__name__}, keys={a.keys() if isinstance(a, dict) else 'N/A'}"
        )

    # Get approval_id if present
    approval_result = state.get("approval_result")
    approval_id = None
    if approval_result:
        approval_id = (
            approval_result.get("approval_id")
            if isinstance(approval_result, dict)
            else getattr(approval_result, "approval_id", None)
        )

    from app.services.executor import ControlledExecutor
    from app.repositories import SessionLocal

    db = SessionLocal()
    try:
        executor = ControlledExecutor(db)
        results = await executor.execute_plan(run_id, action_dicts, approval_id=approval_id)
    finally:
        db.close()

    # Debug logging for results - write to file for visibility
    import os

    debug_file = "/tmp/executor_debug.log"
    with open(debug_file, "a") as f:
        f.write(f"=== executor_node run_id={run_id} ===\n")
        f.write(f"execute_plan returned {len(results)} results\n")
        for i, r in enumerate(results):
            f.write(f"  result[{i}]: type={type(r).__name__}, is_none={r is None}\n")
            if r is not None:
                f.write(f"    success={r.success}, skipped={r.skipped}\n")
        f.write(f"action_dicts count: {len(action_dicts)}\n")
        for i, a in enumerate(action_dicts):
            f.write(f"  action_dict[{i}]: type={type(a).__name__}, is_none={a is None}\n")
        f.write("\n")

    # Filter out None results
    valid_results = [r for r in results if r is not None]
    action_results = [r.to_dict() for r in valid_results]
    execution_results = action_results  # structured execution tracking

    all_success = all(r.success for r in valid_results) if valid_results else False
    has_failure = (
        any(not r.success and not r.skipped for r in valid_results) if valid_results else True
    )

    # Track executor retry count
    retries = state.get("retries") or {}
    retries["executor"] = retries.get("executor", 0) + 1
    state["retries"] = retries

    state["action_results"] = action_results
    state["execution_results"] = execution_results
    state["status"] = RunStatus.EXECUTING if all_success else RunStatus.FAILED
    state["step_count"] = state.get("step_count", 0) + 1
    logger.info(f"executor_node completed: all_success={all_success}, has_failure={has_failure}")

    return state


async def verify_outcome_node(state: IncidentAgentState) -> IncidentAgentState:
    action_results = state.get("action_results", [])
    run_id = state.get("run_id", "unknown")
    ticket = state.get("ticket")
    state["status"] = RunStatus.VERIFYING

    service = (
        ticket.service
        if hasattr(ticket, "service")
        else ticket.get("service", "unknown")
        if ticket
        else "unknown"
    )
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "prod") if ticket else "prod"

    # If no actions or all failed, skip verification
    if not action_results or not any(r.get("success") for r in action_results if r is not None):
        state["verify_decision"] = "FATAL_FAILURE"
        state["status"] = RunStatus.FAILED
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    # Collect verification evidence
    verification_evidence_ids = []
    verification_checks = []

    # Check 1: K8s deployment status
    try:
        deploy_result = await _call_tool_async(
            "query_k8s_deployment_status",
            {
                "service": service,
                "env": env,
            },
            run_id,
        )
        if deploy_result.success:
            ev = EvidenceItem(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                tool_name="query_k8s_deployment_status",
                category="verification",
                source_ref=f"verify-deploy-{run_id}",
                summary=f"Deployment status for {service}: {deploy_result.result.get('status', 'unknown')}",
                raw_payload=deploy_result.result,
                confidence=0.8,
                freshness_score=1.0,
                completeness_score=0.7,
            )
            items = state.get("evidence_items", [])
            items.append(ev)
            state["evidence_items"] = items
            verification_evidence_ids.append(ev.evidence_id)
            deploy_status = deploy_result.result.get("status", "unknown")
            verification_checks.append(
                {
                    "check": "deployment_status",
                    "status": deploy_status,
                    "pass": deploy_status in ("running", "healthy", "available"),
                }
            )
    except Exception as e:
        verification_checks.append(
            {"check": "deployment_status", "status": "error", "pass": False, "error": str(e)}
        )

    # Check 2: Health check
    try:
        health_result = await _call_tool_async(
            "query_lb_health_status",
            {
                "service": service,
                "env": env,
            },
            run_id,
        )
        if health_result.success:
            ev = EvidenceItem(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                tool_name="query_lb_health_status",
                category="verification",
                source_ref=f"verify-health-{run_id}",
                summary=f"Health status for {service}: {health_result.result.get('status', 'unknown')}",
                raw_payload=health_result.result,
                confidence=0.8,
                freshness_score=1.0,
                completeness_score=0.7,
            )
            items = state.get("evidence_items", [])
            items.append(ev)
            state["evidence_items"] = items
            verification_evidence_ids.append(ev.evidence_id)
            health_status = health_result.result.get("status", "unknown")
            verification_checks.append(
                {
                    "check": "health",
                    "status": health_status,
                    "pass": health_status in ("healthy", "ok", "UP"),
                }
            )
    except Exception as e:
        verification_checks.append(
            {"check": "health", "status": "error", "pass": False, "error": str(e)}
        )

    # Check 3: Traffic metrics (5xx, QPS)
    try:
        traffic_result = await _call_tool_async(
            "query_lb_traffic_metrics",
            {
                "service": service,
                "env": env,
            },
            run_id,
        )
        if traffic_result.success:
            ev = EvidenceItem(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                tool_name="query_lb_traffic_metrics",
                category="verification",
                source_ref=f"verify-traffic-{run_id}",
                summary=f"Traffic metrics for {service}",
                raw_payload=traffic_result.result,
                confidence=0.7,
                freshness_score=1.0,
                completeness_score=0.6,
            )
            items = state.get("evidence_items", [])
            items.append(ev)
            state["evidence_items"] = items
            verification_evidence_ids.append(ev.evidence_id)
            error_rate = traffic_result.result.get("error_rate", 0)
            if error_rate is None:
                error_rate = 0.0
            metrics_available = traffic_result.result.get("metrics_available", True)
            # If CMS returned no real metrics, treat as unavailable — not a pass
            if not metrics_available:
                verification_checks.append(
                    {
                        "check": "traffic",
                        "status": "unavailable",
                        "pass": False,
                        "reason": "CMS metrics unavailable — cannot verify traffic health",
                    }
                )
            else:
                verification_checks.append(
                    {"check": "traffic", "error_rate": error_rate, "pass": error_rate < 0.05}
                )
    except Exception as e:
        verification_checks.append(
            {"check": "traffic", "status": "error", "pass": False, "error": str(e)}
        )

    state["verification_evidence_ids"] = verification_evidence_ids

    # Decision logic
    passed_checks = sum(1 for c in verification_checks if c.get("pass"))
    total_checks = len(verification_checks)

    if total_checks == 0:
        # No verification checks could run - treat as retryable
        state["verify_decision"] = "RETRYABLE_FAILURE"
    elif passed_checks == total_checks:
        state["verify_decision"] = "SUCCESS"
    elif passed_checks >= total_checks * 0.5:
        # Partial pass: retryable (might need more time to converge)
        state["verify_decision"] = "RETRYABLE_FAILURE"
    else:
        # Majority failed: fatal
        state["verify_decision"] = "FATAL_FAILURE"
        state["status"] = RunStatus.FAILED

    state["step_count"] = state.get("step_count", 0) + 1
    return state


def rca_node(state: IncidentAgentState) -> IncidentAgentState:
    candidates = state.get("root_cause_candidates", [])
    ticket = state.get("ticket")
    triage = state.get("triage")
    remediation = state.get("remediation_plan")
    action_results = state.get("action_results", [])
    execution_results = state.get("execution_results", [])
    verify_decision = state.get("verify_decision")
    evidence_items = state.get("evidence_items", [])
    current_status = state.get("status")
    terminal_reason = state.get("terminal_reason")

    ticket_title = ticket.title if hasattr(ticket, "title") else ticket.get("title", "unknown")
    ticket_desc = (
        ticket.description if hasattr(ticket, "description") else ticket.get("description", "")
    )
    service = ticket.service if hasattr(ticket, "service") else ticket.get("service", "unknown")
    env = ticket.env if hasattr(ticket, "env") else ticket.get("env", "unknown")
    severity = ticket.severity if hasattr(ticket, "severity") else ticket.get("severity", "P3")

    is_needs_human = current_status == RunStatus.NEEDS_HUMAN
    is_failure = current_status == RunStatus.FAILED or verify_decision in (
        "FATAL_FAILURE",
        "RETRYABLE_FAILURE",
    )
    run_outcome = (
        "NEEDS_HUMAN" if is_needs_human else ("FAILED" if is_failure else "SUCCESS")
    )

    root_cause = "Unknown"
    root_cause_status = "UNKNOWN"
    confidence = 0.0
    if candidates:
        top = candidates[0]
        root_cause = top.hypothesis if hasattr(top, "hypothesis") else top.get("hypothesis")
        confidence = top.confidence if hasattr(top, "confidence") else top.get("confidence", 0.5)
        if is_needs_human:
            root_cause_status = "UNKNOWN"
        elif confidence >= 0.7:
            root_cause_status = "CONFIRMED"
        else:
            root_cause_status = "SUSPECTED"

    all_candidates = []
    candidate_hypotheses = []
    for c in candidates:
        hyp = c.hypothesis if hasattr(c, "hypothesis") else c.get("hypothesis")
        conf = c.confidence if hasattr(c, "confidence") else c.get("confidence", 0.5)
        all_candidates.append(f"- {hyp} (confidence: {conf})")
        candidate_hypotheses.append({"hypothesis": hyp, "confidence": conf})
    candidates_text = "\n".join(all_candidates) if all_candidates else "No candidates"

    remediation_text = ""
    if remediation:
        actions = (
            remediation.actions
            if hasattr(remediation, "actions")
            else remediation.get("actions", [])
        )
        for a in actions:
            at = a.action_type if hasattr(a, "action_type") else a.get("action_type", "unknown")
            remediation_text += f"- {at}\n"

    execution_text = ""
    for r in (execution_results or []) + (action_results or []):
        if r is None:
            continue
        at = r.get("action_type", "unknown") if isinstance(r, dict) else "unknown"
        success = r.get("success", False) if isinstance(r, dict) else False
        err = r.get("error", "") if isinstance(r, dict) else ""
        execution_text += f"- {at}: {'SUCCESS' if success else 'FAILED'}"
        if err:
            execution_text += f" ({err})"
        execution_text += "\n"

    supporting_evidence_ids = []
    for ev in evidence_items:
        eid = ev.evidence_id if hasattr(ev, "evidence_id") else ev.get("evidence_id", "")
        if eid:
            supporting_evidence_ids.append(eid)

    executed_action_ids = []
    for r in (execution_results or []):
        if r is None:
            continue
        aid = r.get("action_id", "") if isinstance(r, dict) else ""
        if aid:
            executed_action_ids.append(aid)

    automation_outcome = {
        "outcome": run_outcome,
        "step_count": state.get("step_count", 0),
        "loop_count": state.get("loop_count", 0),
    }
    if terminal_reason:
        automation_outcome["terminal_reason"] = terminal_reason

    manual_next_steps: List[str] = []

    if is_needs_human:
        failed_tools = state.get("failed_evidence_tools") or []
        missing_cats = state.get("missing_evidence_categories") or []
        manual_next_steps = [
            f"Review the following failed tool calls: {', '.join(failed_tools)}"
            if failed_tools
            else "Investigate why evidence collection returned empty results",
            f"Manually collect data for missing categories: {', '.join(missing_cats)}"
            if missing_cats
            else "",
            "Perform manual root cause investigation",
            "Re-assess whether automated remediation is feasible",
            f"Terminal reason: {terminal_reason.get('code', 'unknown') if terminal_reason else 'loop exhaustion'} — {terminal_reason.get('message', '') if terminal_reason else ''}",
        ]
        manual_next_steps = [s for s in manual_next_steps if s]

        degraded_rca_markdown = f"""# RCA Report [NEEDS_HUMAN]

## Status
**Automation could not complete this incident.** Root cause has NOT been confirmed.

## Root Cause Status
**UNKNOWN** — The automated workflow was unable to gather sufficient evidence to determine
the root cause. The hypotheses below are candidate explanations, NOT confirmed findings.

## Incident Summary
- **Title**: {ticket_title}
- **Service**: {service}
- **Environment**: {env}
- **Severity**: {severity}
- **Outcome**: {run_outcome}

## Candidate Hypotheses (UNCONFIRMED)
{candidates_text if candidates_text else "No hypotheses generated — insufficient evidence."}

## Automation Stop Reason
{terminal_reason.get('code', 'EVIDENCE_LOOP_EXHAUSTED') if terminal_reason else 'EVIDENCE_LOOP_EXHAUSTED'}
{terminal_reason.get('message', 'Evidence collection loop exhausted without sufficient results') if terminal_reason else ''}

## Evidence Quality
- Quality score: {state.get('evidence_quality_score', 0)}
- Missing categories: {state.get('missing_evidence_categories', [])}
- Failed tools: {state.get('failed_evidence_tools', [])}

## Manual Next Steps
"""
        for step in manual_next_steps:
            degraded_rca_markdown += f"- {step}\n"

        report = RcaReport(
            run_id=state.get("run_id", "unknown"),
            report_markdown=degraded_rca_markdown,
            root_cause=root_cause if root_cause != "Unknown" else "Root cause not confirmed",
            root_cause_status=root_cause_status,
            resolution="Automated resolution not possible — requires manual intervention",
            prevention_items=["Improve evidence collection reliability"],
            timeline_summary="Automated workflow stopped — manual investigation needed",
            impact_assessment="Impact could not be fully assessed — manual review required",
            supporting_evidence_ids=supporting_evidence_ids,
            executed_action_ids=executed_action_ids,
            candidate_hypotheses=candidate_hypotheses,
            automation_outcome=automation_outcome,
            manual_next_steps=manual_next_steps,
        )

        state["rca_report"] = report
        state["final_outcome"] = run_outcome
        if current_status != RunStatus.FAILED:
            state["status"] = RunStatus.NEEDS_HUMAN
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    rca_prompt = f"""Generate a comprehensive Root Cause Analysis (RCA) report.

## Incident Details
- Title: {ticket_title}
- Description: {ticket_desc}
- Service: {service}
- Environment: {env}
- Severity: {severity}
- Outcome: {run_outcome}

## Root Cause Candidates
{candidates_text}

## Remediation Actions Planned
{remediation_text if remediation_text else "None"}

## Execution Results
{execution_text if execution_text else "No actions executed"}

## Verification
{verify_decision or "Not performed"}

Generate a detailed RCA report in JSON format:
{{
  "root_cause": "primary root cause identified",
  "confidence": 0.0-1.0,
  "resolution": "what was done to resolve",
  "prevention_items": ["item 1", "item 2", "item 3"],
  "timeline_summary": "brief timeline of what happened",
  "impact_assessment": "what was the impact"
}}

Respond in JSON format only."""

    llm_response = ""
    try:
        llm_response = llm_client.complete_sync(
            rca_prompt, system_prompt="你是一个SRE根因分析助手。请始终使用简体中文回复。"
        )
    except Exception:
        llm_response = ""

    import json

    final_root_cause = root_cause
    final_resolution = (
        "Remediation actions executed"
        if not is_failure
        else "Remediation incomplete - manual intervention required"
    )
    final_prevention = [
        "Implement better monitoring",
        "Add automated rollback",
        "Improve deployment process",
    ]
    timeline_summary = ""
    impact_assessment = ""

    if llm_response and llm_response != "fallback_response":
        try:
            import re

            json_match = re.search(r"\{[\s\S]*\}", llm_response)
            if json_match:
                rca_data = json.loads(json_match.group())
                final_root_cause = rca_data.get("root_cause", final_root_cause)
                final_resolution = rca_data.get("resolution", final_resolution)
                final_prevention = rca_data.get("prevention_items", final_prevention)
                timeline_summary = rca_data.get("timeline_summary", "")
                impact_assessment = rca_data.get("impact_assessment", "")
        except Exception:
            pass

    outcome_emoji = "SUCCESS" if not is_failure else "FAILED"
    markdown_report = f"""# RCA Report [{outcome_emoji}]

## Root Cause
**{final_root_cause}** (confidence: {confidence:.0%})

## Root Cause Status
{root_cause_status}

## Incident Summary
- **Title**: {ticket_title}
- **Service**: {service}
- **Environment**: {env}
- **Severity**: {severity}
- **Outcome**: {run_outcome}

## Analysis
{candidates_text}

## Timeline
{timeline_summary if timeline_summary else "Incident analyzed and root cause identified through automated diagnosis."}

## Impact
{impact_assessment if impact_assessment else "Analysis completed - remediation actions proposed."}

## Execution Results
{execution_text if execution_text else "No actions executed."}

## Resolution
{final_resolution}

## Prevention
"""
    for item in final_prevention:
        markdown_report += f"- {item}\n"

    report = RcaReport(
        run_id=state.get("run_id", "unknown"),
        report_markdown=markdown_report,
        root_cause=final_root_cause,
        root_cause_status=root_cause_status,
        resolution=final_resolution,
        prevention_items=final_prevention,
        timeline_summary=timeline_summary or None,
        impact_assessment=impact_assessment or None,
        supporting_evidence_ids=supporting_evidence_ids,
        executed_action_ids=executed_action_ids,
        candidate_hypotheses=candidate_hypotheses,
        automation_outcome=automation_outcome,
        manual_next_steps=manual_next_steps,
    )

    archive_ref = ""
    try:
        rca_response = asyncio.run(
            gateway.call_tool(
                ToolRequest(
                    tool_name="write_rca_to_oss",
                    params={
                        "run_id": state.get("run_id", "unknown"),
                        "service": service,
                        "env": env,
                        "content": markdown_report,
                        "content_type": "markdown",
                    },
                    run_id=state.get("run_id", ""),
                )
            )
        )
        if rca_response.success and rca_response.result:
            archive_ref = rca_response.result.get("oss_url", "")
    except Exception:
        logger.warning(f"Failed to write RCA to OSS for run {state.get('run_id')}")

    evidence_json = ""
    try:
        evidence_data = [
            {
                "evidence_id": ev.evidence_id if hasattr(ev, "evidence_id") else ev.get("evidence_id"),
                "source": ev.source if hasattr(ev, "source") else ev.get("source"),
                "category": ev.category if hasattr(ev, "category") else ev.get("category"),
                "content": ev.content if hasattr(ev, "content") else ev.get("content"),
            }
            for ev in evidence_items
            if ev is not None
        ]
        evidence_json = json.dumps(evidence_data, ensure_ascii=False, default=str)
    except Exception:
        logger.warning(f"Failed to serialize evidence for run {state.get('run_id')}")

    if evidence_json:
        try:
            asyncio.run(
                gateway.call_tool(
                    ToolRequest(
                        tool_name="write_evidence_to_oss",
                        params={
                            "run_id": state.get("run_id", "unknown"),
                            "service": service,
                            "env": env,
                            "content": evidence_json,
                        },
                        run_id=state.get("run_id", ""),
                    )
                )
            )
        except Exception:
            logger.warning(f"Failed to write evidence to OSS for run {state.get('run_id')}")

    report.archive_ref = archive_ref

    state["rca_report"] = report
    state["final_outcome"] = run_outcome
    if current_status not in {RunStatus.FAILED, RunStatus.NEEDS_HUMAN, RunStatus.WAITING_HUMAN}:
        state["status"] = RunStatus.COMPLETED
    state["step_count"] = state.get("step_count", 0) + 1

    return state
