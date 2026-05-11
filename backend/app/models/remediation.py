from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional  # 引入列表和可选类型
from app.models.action import ActionSpec  # 引入运维动作规格模型


class RemediationPlan(BaseModel):
    """
    修复方案模型，描述针对当前事件的具体处置计划，
    包含要执行的动作列表、预期效果、回滚方案等。
    """

    summary: str = Field(
        ..., description="Overall remediation summary"
    )  # 修复方案整体概述
    actions: List[ActionSpec] = Field(
        default_factory=list, description="List of actions to take"
    )  # 计划执行的动作列表
    expected_outcome: str = Field(
        ..., description="Expected result after remediation"
    )  # 期望通过修复达到的效果
    rollback_plan: Optional[str] = Field(
        default=None, description="Steps to rollback if needed"
    )  # 如修复失败时的回滚步骤
    risk_notes: Optional[str] = Field(
        default=None, description="Risk considerations"
    )  # 与该修复方案相关的风险说明
    human_checkpoints: List[str] = Field(
        default_factory=list, description="Points where human review is required"
    )  # 需要人工确认的关键检查点列表