from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional  # 引入列表和可选类型


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
    supporting_evidence_ids: List[str] = Field(
        default_factory=list, description="Evidence supporting this hypothesis"
    )  # 支持该假设的证据 ID 列表
    contradicting_evidence_ids: List[str] = Field(
        default_factory=list, description="Evidence contradicting this hypothesis"
    )  # 与该假设相矛盾的证据 ID 列表
    next_checks: List[str] = Field(
        default_factory=list, description="Suggested verification steps"
    )  # 用于验证该假设的后续检查建议