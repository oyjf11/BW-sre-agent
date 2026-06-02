from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional, Dict, Any  # 引入列表和可选类型


class RcaReport(BaseModel):
    """
    根因分析报告模型，记录一次诊断运行最终的 RCA 结果，
    包含根因、处置方案、预防措施等内容。
    """

    run_id: str = Field(..., description="Associated run ID")  # 关联的诊断运行 ID
    report_markdown: str = Field(
        ..., description="Markdown formatted RCA report"
    )  # Markdown 格式的完整 RCA 报告
    root_cause: str = Field(
        ..., description="Identified root cause"
    )  # 识别出的根因描述
    root_cause_status: str = Field(
        default="UNKNOWN", description="CONFIRMED | SUSPECTED | UNKNOWN"
    )  # 根因确认状态
    resolution: str = Field(
        ..., description="Resolution steps taken"
    )  # 已采取的解决步骤
    prevention_items: List[str] = Field(
        default_factory=list, description="Steps to prevent recurrence"
    )  # 避免问题复发的预防措施列表
    confirmed_by_human: bool = Field(
        default=False, description="Whether human confirmed the RCA"
    )  # 是否已经由人工确认该 RCA
    timeline_summary: Optional[str] = Field(
        default=None, description="Brief timeline of incident events"
    )  # 事件关键时间线摘要
    impact_assessment: Optional[str] = Field(
        default=None, description="Assessment of incident impact"
    )  # 对事件影响范围和程度的评估
    supporting_evidence_ids: List[str] = Field(
        default_factory=list, description="IDs of evidence used in analysis"
    )  # 分析过程中使用到的证据 ID 列表
    executed_action_ids: List[str] = Field(
        default_factory=list, description="IDs of actions executed during remediation"
    )  # 修复过程中实际执行过的动作 ID 列表
    candidate_hypotheses: List[Dict[str, Any]] = Field(
        default_factory=list, description="Candidate hypotheses from diagnosis"
    )  # 诊断候选假设列表
    automation_outcome: Optional[Dict[str, Any]] = Field(
        default=None, description="Automation workflow outcome summary"
    )  # 自动化流程结果摘要
    manual_next_steps: List[str] = Field(
        default_factory=list, description="Manual intervention steps for human takeover"
    )  # 人工接管后续步骤
    archive_ref: Optional[str] = Field(
        default=None, description="Reference to archived report (e.g. OSS path)"
    )  # 报告归档位置引用（如 OSS 路径）