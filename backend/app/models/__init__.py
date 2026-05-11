"""Domain Models package. 领域模型包。"""
from app.models.incident import IncidentTicket  # 事件工单模型
from app.models.triage import TriageResult  # 分诊结果模型
from app.models.evidence import EvidenceItem  # 证据条目模型
from app.models.root_cause import RootCauseCandidate  # 根因候选模型
from app.models.action import ActionSpec  # 运维动作规格模型
from app.models.remediation import RemediationPlan  # 修复方案模型
from app.models.approval import ApprovalRequest, ApprovalResult  # 审批请求与结果模型
from app.models.rca import RcaReport  # 根因分析报告模型
from app.models.event import RunEvent  # 运行事件模型

__all__ = [  # 对外暴露的领域模型名称
    "IncidentTicket",  # 事件工单
    "TriageResult",  # 分诊结果
    "EvidenceItem",  # 证据条目
    "RootCauseCandidate",  # 根因候选
    "ActionSpec",  # 运维动作规格
    "RemediationPlan",  # 修复方案
    "ApprovalRequest",  # 审批请求
    "ApprovalResult",  # 审批结果
    "RcaReport",  # 根因分析报告
    "RunEvent",  # 运行事件
]