"""Internationalization support for run event messages.

Usage:
    from app.i18n import t, set_language, get_node_name

    # Default language (controlled by I18N_LANGUAGE env var)
    msg = t("node_started", node_name=get_node_name("node_intake"))

    # Override per-call
    msg = t("node_started", lang="en", node_name="Intake")
"""

from contextvars import ContextVar
from typing import Optional

_current_lang: ContextVar[str] = ContextVar("i18n_lang", default="zh")


def set_language(lang: str) -> None:
    _current_lang.set(lang)


def get_language() -> str:
    return _current_lang.get()


NODE_NAMES = {
    "en": {
        "node_dispatcher": "Dispatcher",
        "node_intake": "Intake",
        "node_triage": "Triage",
        "node_retrieve_memory": "Memory Retrieval",
        "node_planner": "Planner",
        "node_evidence_fanout": "Evidence Collection",
        "node_evidence_aggregate": "Evidence Aggregation",
        "node_diagnose": "Diagnosis",
        "node_critic": "Review",
        "node_remediation": "Remediation",
        "node_risk_gate": "Risk Gate",
        "node_approval_interrupt": "Approval",
        "node_executor": "Executor",
        "node_verify_outcome": "Verification",
        "node_rca": "Root Cause Analysis",
    },
    "zh": {
        "node_dispatcher": "调度器",
        "node_intake": "信息接入",
        "node_triage": "分类分诊",
        "node_retrieve_memory": "记忆检索",
        "node_planner": "规划器",
        "node_evidence_fanout": "证据采集",
        "node_evidence_aggregate": "证据汇总",
        "node_diagnose": "诊断分析",
        "node_critic": "评审",
        "node_remediation": "修复方案",
        "node_risk_gate": "风险门禁",
        "node_approval_interrupt": "审批中断",
        "node_executor": "执行器",
        "node_verify_outcome": "结果验证",
        "node_rca": "根因分析",
    },
}

ACTION_NAMES = {
    "en": {
        "restart": "Restart",
        "scale_up": "Scale Up",
        "scale_down": "Scale Down",
        "rollback": "Rollback",
        "execute_sql": "Execute SQL",
        "execute_command": "Execute Command",
        "mysql_restart": "Restart MySQL",
        "k8s_rollback": "K8s Rollback",
    },
    "zh": {
        "restart": "重启",
        "scale_up": "扩容",
        "scale_down": "缩容",
        "rollback": "回滚",
        "execute_sql": "SQL执行",
        "execute_command": "命令执行",
        "mysql_restart": "MySQL重启",
        "k8s_rollback": "K8s回滚",
    },
}

STATUS_NAMES = {
    "en": {
        "completed": "Completed",
        "failed": "Failed",
        "waiting_human": "Waiting for Approval",
        "needs_human": "Needs Human Takeover",
        "running": "Running",
    },
    "zh": {
        "completed": "已完成",
        "failed": "已失败",
        "waiting_human": "等待审批",
        "needs_human": "需人工接管",
        "running": "运行中",
    },
}

MESSAGES = {
    "en": {
        "node_started": "{node_name} started",
        "node_completed": "{node_name} completed | step {step_count}",
        "node_failed": "{node_name} failed | {error}",
        "checkpoint_saved": "Checkpoint saved | {node_name}",
        "run_created": "Run started",
        "run_completed": "Run finished | status: {status}",
        "run_failed": "Run failed | {error}",
        "run_paused": "Run paused | status: {status} (waiting for human)",
        "action_started": "Executing {action_name} on {service}/{env} | attempt {attempt_no}",
        "action_completed": "Completed {action_name} on {service}/{env}",
        "action_failed": "Failed {action_name} on {service}/{env} | {error}",
        "action_skipped": "Skipped (idempotent) {action_name} on {service}/{env}",
        "precondition_failed": "Precondition check failed for {action_name} | {reasons}",
    },
    "zh": {
        "node_started": "节点「{node_name}」开始执行",
        "node_completed": "节点「{node_name}」执行完成（第 {step_count} 步）",
        "node_failed": "节点「{node_name}」执行失败：{error}",
        "checkpoint_saved": "已保存检查点｜{node_name}",
        "run_created": "开始运行",
        "run_completed": "运行完成｜状态：{status}",
        "run_failed": "运行失败：{error}",
        "run_paused": "运行已暂停｜状态：{status}（等待人工处理）",
        "action_started": "正在对 {service}/{env} 执行「{action_name}」（第 {attempt_no} 次）",
        "action_completed": "已完成对 {service}/{env} 的「{action_name}」",
        "action_failed": "对 {service}/{env} 执行「{action_name}」失败：{error}",
        "action_skipped": "已跳过（幂等）：对 {service}/{env} 的「{action_name}」",
        "precondition_failed": "前置检查失败（{action_name}）：{reasons}",
    },
}


def get_node_name(node_name: str, lang: Optional[str] = None) -> str:
    lang = lang or _current_lang.get()
    return NODE_NAMES.get(lang, {}).get(node_name, node_name)


def get_action_name(action_type: str, lang: Optional[str] = None) -> str:
    lang = lang or _current_lang.get()
    return ACTION_NAMES.get(lang, {}).get(action_type, action_type)


def get_status_name(status: str, lang: Optional[str] = None) -> str:
    lang = lang or _current_lang.get()
    return STATUS_NAMES.get(lang, {}).get(status, status)


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    lang = lang or _current_lang.get()
    templates = MESSAGES.get(lang, MESSAGES.get("en", {}))
    template = templates.get(key, MESSAGES.get("en", {}).get(key, key))
    return template.format(**kwargs)
