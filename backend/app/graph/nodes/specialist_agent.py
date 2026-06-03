"""Specialist Agent with ReAct loop for evidence analysis.

Each SpecialistAgent runs a managed ReAct loop: rounds of LLM tool-calling
followed by a structured final analysis. The agent has a 4-level degradation
path and per-category rule-based fallback extraction.
"""

import asyncio
import json
import logging
import re
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import yaml

from app.core.config import get_settings
from app.llm_client import llm_client
from app.models.planning import (
    AgentRunStatus,
    AgentTask,
    AnomalySignal,
    CorrelationHint,
    SpecialistAnalysis,
    SpecialistEvidence,
)
from app.tools.gateway import ToolRequest, gateway
from app.tracing import tracer

logger = logging.getLogger(__name__)

FORBIDDEN_TOOLS = {"execute_action"}

CATEGORY_PREFIX_MAP: Dict[str, str] = {
    "k8s": "query_k8s_",
    "db": "query_db_",
    "logs": "query_logs",
    "metrics": "query_metrics",
    "deployments": "query_deployments",
}


class SpecialistAgentConfig:
    def __init__(
        self,
        agent_id: str,
        category: str,
        description: str,
        enabled: bool,
        max_tool_rounds: int,
        system_prompt_version: str,
        tool_names: List[str],
        system_prompt: str,
    ):
        self.agent_id = agent_id
        self.category = category
        self.description = description
        self.enabled = enabled
        self.max_tool_rounds = max_tool_rounds
        self.system_prompt_version = system_prompt_version
        self.tool_names = tool_names
        self.system_prompt = system_prompt


def load_agent_configs(path: str = "") -> Dict[str, SpecialistAgentConfig]:
    if not path:
        import os as _os
        path = _os.path.join(_os.path.dirname(__file__), "agent_configs.yaml")
    try:
        with open(path) as f:
            raw = yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"agent_configs.yaml not found at {path}, all agents disabled")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"agent_configs.yaml parse error: {e}, all agents disabled")
        return {}

    configs: Dict[str, SpecialistAgentConfig] = {}
    agents = raw.get("agents", []) if raw else []
    for a in agents:
        agent_id = a.get("agent_id", "")
        category = a.get("category", "")
        description = a.get("description", "")
        enabled = a.get("enabled", True)
        max_tool_rounds = a.get("max_tool_rounds", 3)
        version = a.get("system_prompt_version", "1.0.0")
        tool_names = a.get("tool_names", [])
        prompt = a.get("system_prompt", "")

        if not validate_agent_config(agent_id, category, tool_names):
            enabled = False
            logger.warning(f"Agent {agent_id} failed validation, disabling")

        configs[agent_id] = SpecialistAgentConfig(
            agent_id=agent_id,
            category=category,
            description=description,
            enabled=enabled,
            max_tool_rounds=max_tool_rounds,
            system_prompt_version=version,
            tool_names=tool_names,
            system_prompt=prompt,
        )
    return configs


def validate_agent_config(agent_id: str, category: str, tool_names: List[str]) -> bool:
    forbidden = FORBIDDEN_TOOLS & set(tool_names)
    if forbidden:
        logger.error(f"Agent {agent_id}: forbidden tools in tool_names: {forbidden}")
        return False

    prefix = CATEGORY_PREFIX_MAP.get(category)
    if prefix:
        for tn in tool_names:
            if not tn.startswith(prefix):
                logger.error(
                    f"Agent {agent_id}: tool '{tn}' does not match category prefix '{prefix}'"
                )
                return False

    for tn in tool_names:
        cap = gateway.describe_capability(tn)
        if not cap.get("available"):
            logger.warning(
                f"Agent {agent_id}: tool '{tn}' not available in gateway: {cap.get('reason')}"
            )

    return True


class SpecialistAgent:
    def __init__(self, config: SpecialistAgentConfig):
        self.config = config
        self._reset()

    def _reset(self):
        self.messages: List[Dict[str, Any]] = []
        self.raw_tool_results: Dict[str, Any] = {}
        self.collected_tool_names: List[str] = []
        self.round_truncated = False
        self.llm_had_error = False

    async def run(
        self, agent_task: AgentTask, run_id: str, parent_span_id: str = ""
    ) -> SpecialistAnalysis:
        self._reset()

        span_id = tracer.start_span(
            f"specialist.{self.config.agent_id}", run_id=run_id, parent_id=parent_span_id
        )

        deadline = time.monotonic() + agent_task.timeout_ms / 1000.0

        self.messages = [
            {"role": "system", "content": self.config.system_prompt},
            {
                "role": "user",
                "content": self._build_task_prompt(agent_task),
            },
        ]

        tools = self._build_tool_definitions()

        for round_num in range(self.config.max_tool_rounds):
            remaining_ms = int((deadline - time.monotonic()) * 1000)
            if remaining_ms < 2000:
                self.round_truncated = True
                tracer.add_event(
                    span_id, "agent.timeout",
                    {"round": round_num, "remaining_ms": remaining_ms},
                )
                break

            tracer.set_step_context(span_id)
            round_echo = f"react.round.{round_num}"
            tracer.add_event(span_id, round_echo, {"remaining_ms": remaining_ms})

            try:
                llm_deadline = min(remaining_ms / 1000, 15.0)
                resp = await asyncio.wait_for(
                    llm_client.complete_async(
                        self.messages, tools=tools, temperature=0.7, max_tokens=2000,
                    ),
                    timeout=llm_deadline,
                )
            except asyncio.TimeoutError:
                logger.warning(f"[{self.config.agent_id}] LLM timeout round {round_num}")
                self.llm_had_error = True
                self.round_truncated = True
                break
            except Exception:
                logger.error(
                    f"[{self.config.agent_id}] LLM error round {round_num}:\n{traceback.format_exc()}"
                )
                self.llm_had_error = True
                self.round_truncated = True
                break

            tool_calls = resp.get("tool_calls")
            content = resp.get("content", "")

            if not tool_calls:
                self.messages.append({"role": "assistant", "content": content})
                break

            assistant_msg: Dict[str, Any] = {"role": "assistant", "content": content or ""}
            assistant_msg["tool_calls"] = tool_calls
            self.messages.append(assistant_msg)

            valid_calls = [tc for tc in tool_calls if self._tool_allowed(tc)]
            results = await asyncio.gather(
                *[self._execute_tool(tc, run_id, remaining_ms) for tc in valid_calls],
                return_exceptions=True,
            )
            for tc, res in zip(valid_calls, results):
                tool_name = tc["function"]["name"]
                self.collected_tool_names.append(tool_name)
                self.raw_tool_results[tool_name] = res if not isinstance(res, Exception) else {"error": str(res)}
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": tool_name,
                    "content": json.dumps(res if not isinstance(res, Exception) else {"error": str(res)}),
                })

            if round_num == self.config.max_tool_rounds - 1 and tool_calls:
                self.round_truncated = True

        tracer.add_event(
            span_id, "agent.final_analysis",
            {"truncated": self.round_truncated, "llm_error": self.llm_had_error},
        )
        analysis = await self._produce_final_analysis(
            agent_task, run_id, span_id
        )
        tracer.end_span(span_id, status="ok")
        return analysis

    def _build_task_prompt(self, task: AgentTask) -> str:
        parts = [
            f"服务: {task.service}",
            f"环境: {task.env}",
        ]
        if task.incident_type:
            parts.append(f"故障类型: {task.incident_type}")
        if task.time_window_start:
            parts.append(f"时间窗开始: {task.time_window_start}")
        if task.time_window_end:
            parts.append(f"时间窗结束: {task.time_window_end}")
        if task.extra_context:
            ctx_text = ", ".join(f"{k}={v}" for k, v in task.extra_context.items())
            parts.append(f"上下文: {ctx_text}")
        parts.append("请调用可用工具收集数据，并在最终响应中输出结构化JSON分析结论。")
        return "\n".join(parts)

    def _build_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            gateway.get_tool_schema(tn) for tn in self.config.tool_names
            if gateway.get_tool_schema(tn)
        ]

    def _tool_allowed(self, tool_call: Dict[str, Any]) -> bool:
        func = tool_call.get("function", {})
        name = func.get("name", "")
        if name not in self.config.tool_names:
            logger.warning(
                f"[{self.config.agent_id}] LLM hallucinated tool '{name}', injecting error"
            )
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "name": name,
                "content": json.dumps({"error": f"Tool '{name}' is not available. Use: {self.config.tool_names}"}),
            })
            return False
        return True

    async def _execute_tool(
        self, tool_call: Dict[str, Any], run_id: str, remaining_ms: int
    ) -> Dict[str, Any]:
        func = tool_call.get("function", {})
        name = func.get("name", "")
        args_str = func.get("arguments", "{}")
        try:
            params = json.loads(args_str) if isinstance(args_str, str) else args_str
        except json.JSONDecodeError:
            params = {}

        request = ToolRequest(tool_name=name, params=params, run_id=run_id)
        tool_timeout = min(30, max(1, int(remaining_ms / 1000) // len(self.config.tool_names)))

        try:
            resp = await asyncio.wait_for(gateway.call_tool(request), timeout=tool_timeout)
            if resp.success:
                return resp.result or {}
            return {"error": resp.error}
        except asyncio.TimeoutError:
            return {"error": f"Tool '{name}' timed out after {tool_timeout}s"}
        except Exception as e:
            return {"error": str(e)}

    async def _produce_final_analysis(
        self, task: AgentTask, run_id: str, span_id: str
    ) -> SpecialistAnalysis:
        has_raw_data = bool(self.raw_tool_results)

        if self.llm_had_error:
            if has_raw_data:
                return self._build_degraded_analysis(task, AgentRunStatus.PARTIAL)
            return self._build_llm_failed_shell(task)

        try:
            final_resp = await asyncio.wait_for(
                llm_client.complete_async(
                    self.messages + [{
                        "role": "user",
                        "content": "请现在输出最终的结构化JSON分析结论（不要调用工具）。",
                    }],
                    tools=None,
                    temperature=0.3,
                    max_tokens=2000,
                ),
                timeout=min((self.config.max_tool_rounds + 2) * 5, 30.0),
            )
        except Exception:
            logger.error(f"[{self.config.agent_id}] Final LLM call failed")
            if has_raw_data:
                return self._build_degraded_analysis(task, AgentRunStatus.PARTIAL)
            return self._build_llm_failed_shell(task)

        content = final_resp.get("content", "")
        llm_confidence = 0.0

        try:
            parsed = self._extract_json(content)
            conclusion = parsed.get("conclusion", "异常: 分析结果缺失")
            severity = parsed.get("severity", "warning")

            anomalies = []
            for a in parsed.get("anomalies", []):
                anomalies.append(AnomalySignal(
                    signal_type=a.get("signal_type", "unknown"),
                    evidence_ref=a.get("evidence_ref", ""),
                    description=a.get("description", ""),
                    timestamp_hint=a.get("timestamp_hint"),
                ))

            correlation_hints = []
            for h in parsed.get("correlation_hints", []):
                hl_confidence = min(float(h.get("confidence", 0.5)), 0.6)
                correlation_hints.append(CorrelationHint(
                    source_category=self.config.category,
                    target_category=h.get("target_category", ""),
                    reason=h.get("reason", ""),
                    confidence=hl_confidence,
                    source="llm",
                ))

            llm_confidence_raw = float(parsed.get("confidence", 0.5))
            llm_confidence = min(llm_confidence_raw, 0.9)  # 代码层封顶

            self._extraact_signals_by_rules()
            rule_hints = self._extraact_correlation_hints_by_rules(task)
            correlation_hints.extend(rule_hints)

            evidence = SpecialistEvidence(
                evidence_id=f"ev_{self.config.agent_id}_{run_id}",
                category=self.config.category,
                conclusion=conclusion,
                severity=severity,
                anomalies=anomalies,
                correlation_hints=correlation_hints,
            )

            return SpecialistAnalysis(
                agent_id=self.config.agent_id,
                agent_category=self.config.category,
                evidence_items=[evidence],
                collected_tool_names=list(self.collected_tool_names),
                raw_tool_results=dict(self.raw_tool_results),
                execution_summary=(
                    f"L0_COMPLETED v{self.config.system_prompt_version} "
                    f"truncated={self.round_truncated} tools={self.collected_tool_names}"
                ),
                confidence=llm_confidence,
                run_status=AgentRunStatus.COMPLETED,
                partial=False,
                truncated=self.round_truncated,
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"[{self.config.agent_id}] L1 JSON parse/validation failed: {e}")
            return self._build_degraded_analysis(task, AgentRunStatus.PARTIAL)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            match = re.search(pattern, text)
            if match:
                return json.loads(match.group())
        raise json.JSONDecodeError("No JSON found", text, 0)

    def _build_degraded_analysis(
        self, task: AgentTask, status: AgentRunStatus
    ) -> SpecialistAnalysis:
        self._extraact_signals_by_rules()
        rule_hints = self._extraact_correlation_hints_by_rules(task)

        anomalies = self._collect_rule_anomalies()
        conclusion = "部分: 规则兜底分析（LLM失效）" if anomalies else "失败: 无法完成分析（LLM失效且无异常信号）"

        evidence = SpecialistEvidence(
            evidence_id=f"ev_{self.config.agent_id}_degraded_{task.service}",
            category=self.config.category,
            conclusion=conclusion,
            severity="warning" if anomalies else "info",
            anomalies=anomalies,
            correlation_hints=rule_hints,
        )

        return SpecialistAnalysis(
            agent_id=self.config.agent_id,
            agent_category=self.config.category,
            evidence_items=[evidence],
            collected_tool_names=list(self.collected_tool_names),
            raw_tool_results=dict(self.raw_tool_results),
            execution_summary=(
                f"L{2 if bool(self.raw_tool_results) else 1}_DEGRADED "
                f"v{self.config.system_prompt_version} status={status.value}"
            ),
            confidence=0.25 if anomalies else 0.0,
            run_status=status,
            partial=True,
            truncated=self.round_truncated,
        )

    def _build_llm_failed_shell(self, task: AgentTask) -> SpecialistAnalysis:
        return SpecialistAnalysis(
            agent_id=self.config.agent_id,
            agent_category=self.config.category,
            evidence_items=[],
            collected_tool_names=[],
            raw_tool_results={},
            execution_summary=f"L3_LLM_FAILED v{self.config.system_prompt_version}",
            confidence=0.0,
            run_status=AgentRunStatus.LLM_FAILED,
            partial=True,
            truncated=self.round_truncated,
        )

    _rule_anomalies: List[AnomalySignal] = []

    def _extraact_signals_by_rules(self):
        self._rule_anomalies = []
        raw = self.raw_tool_results

        if self.config.category == "k8s":
            self._extraact_k8s_signals(raw)
        elif self.config.category == "db":
            self._extraact_db_signals(raw)
        elif self.config.category == "logs":
            self._extraact_log_signals(raw)
        elif self.config.category == "metrics":
            self._extraact_metrics_signals(raw)
        elif self.config.category == "deployments":
            self._extraact_deployment_signals(raw)

    def _extraact_k8s_signals(self, raw: Dict[str, Any]):
        for tn, result in raw.items():
            if isinstance(result, dict):
                pods = result.get("pods", [])
                for pod in pods:
                    if isinstance(pod, dict):
                        for cs in pod.get("container_statuses", []):
                            if isinstance(cs, dict):
                                state = cs.get("state", {})
                                for sk, sv in state.items():
                                    reason = sv.get("reason", "") if isinstance(sv, dict) else ""
                                    if reason in {"CrashLoopBackOff", "ErrImagePull", "OOMKilled"}:
                                        self._rule_anomalies.append(AnomalySignal(
                                            signal_type=reason,
                                            evidence_ref=tn,
                                            description=f"Pod {pod.get('name', '?')}: {reason}",
                                        ))
                ready = result.get("ready_replicas", 0)
                desired = result.get("desired_replicas", 0)
                if desired > 0 and ready < desired:
                    self._rule_anomalies.append(AnomalySignal(
                        signal_type="replicas_mismatch",
                        evidence_ref=tn,
                        description=f"Ready replicas {ready} < desired {desired}",
                    ))

    def _extraact_db_signals(self, raw: Dict[str, Any]):
        for tn, result in raw.items():
            if isinstance(result, dict):
                if tn == "query_db_processlist":
                    pl = result.get("processlist", [])
                    active = sum(
                        1 for p in pl
                        if isinstance(p, dict) and p.get("COMMAND", "Sleep") != "Sleep"
                    )
                    if active > 50:
                        self._rule_anomalies.append(AnomalySignal(
                            signal_type="high_connections",
                            evidence_ref=tn,
                            description=f"Active connections: {active} (>50)",
                        ))
                if tn == "query_db_slow_queries":
                    sq = result.get("slow_queries", [])
                    if len(sq) > 10:
                        self._rule_anomalies.append(AnomalySignal(
                            signal_type="slow_queries",
                            evidence_ref=tn,
                            description=f"Slow queries: {len(sq)} (>10)",
                        ))

    def _extraact_log_signals(self, raw: Dict[str, Any]):
        for tn, result in raw.items():
            if isinstance(result, dict):
                log_text = json.dumps(result)
                count = len(re.findall(r'ERROR|FATAL|Exception', log_text, re.IGNORECASE))
                if count > 10:
                    self._rule_anomalies.append(AnomalySignal(
                        signal_type="high_error_logs",
                        evidence_ref=tn,
                        description=f"ERROR/FATAL/Exception count: {count} (>10)",
                    ))

    def _extraact_metrics_signals(self, raw: Dict[str, Any]):
        for tn, result in raw.items():
            if isinstance(result, dict):
                metrics = result.get("metrics", {})
                for mname, data in metrics.items():
                    values = data.get("values", []) if isinstance(data, dict) else []
                    if len(values) >= 2:
                        try:
                            v1, v2 = float(values[0]), float(values[-1])
                            if v1 > 0 and abs((v2 - v1) / v1) > 0.5:
                                self._rule_anomalies.append(AnomalySignal(
                                    signal_type=f"{mname}_spike",
                                    evidence_ref=tn,
                                    description=f"{mname}: {v1} → {v2} ({abs((v2 - v1) / v1) * 100:.0f}% change)",
                                ))
                        except (ValueError, TypeError, ZeroDivisionError):
                            pass

    def _extraact_deployment_signals(self, raw: Dict[str, Any]):
        pass

    def _extraact_correlation_hints_by_rules(self, task: AgentTask) -> List[CorrelationHint]:
        hints: List[CorrelationHint] = []
        if self.config.category == "deployments":
            raw = self.raw_tool_results
            for tn, result in raw.items():
                if isinstance(result, dict) and result.get("deployments"):
                    deployments = result["deployments"]
                    if isinstance(deployments, list) and deployments:
                        hints.append(CorrelationHint(
                            source_category=self.config.category,
                            target_category="k8s",
                            reason="检测到最近部署，可能与 K8s 变化相关",
                            confidence=0.6,
                            source="rule",
                        ))
                        hints.append(CorrelationHint(
                            source_category=self.config.category,
                            target_category="logs",
                            reason="检测到最近部署，可能与日志异常相关",
                            confidence=0.6,
                            source="rule",
                        ))
        return hints

    def _collect_rule_anomalies(self) -> List[AnomalySignal]:
        return list(self._rule_anomalies)


def _build_llm_failed_shell_static(agent_id: str, category: str) -> SpecialistAnalysis:
    return SpecialistAnalysis(
        agent_id=agent_id,
        agent_category=category,
        evidence_items=[],
        collected_tool_names=[],
        raw_tool_results={},
        execution_summary="L3_LLM_FAILED (disabled)",
        confidence=0.0,
        run_status=AgentRunStatus.LLM_FAILED,
        partial=True,
        truncated=False,
    )


def _build_default_agent_tasks(ticket: Any) -> List[AgentTask]:
    service = getattr(ticket, "service", "") or (
        ticket.get("service", "unknown") if isinstance(ticket, dict) else "unknown"
    )
    env = getattr(ticket, "env", "") or (
        ticket.get("env", "unknown") if isinstance(ticket, dict) else "unknown"
    )
    categories = ["k8s", "db", "logs", "metrics", "deployments"]
    tasks: List[AgentTask] = []
    for cat in categories:
        tasks.append(AgentTask(
            agent_id=f"{cat}_specialist",
            category=cat,
            service=service,
            env=env,
            incident_type="",
            timeout_ms=30000,
        ))
    return tasks
