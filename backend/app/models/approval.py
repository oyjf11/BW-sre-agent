from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional  # 引入列表和可选类型
from app.models.action import ActionSpec  # 引入运维动作规格模型


class ApprovalRequest(BaseModel):
    """
    审批请求模型，描述某个动作需要人工审批时的上下文信息。
    """

    approval_id: str = Field(
        ..., description="Unique approval identifier"
    )  # 审批请求唯一标识
    run_id: str = Field(..., description="Associated run ID")  # 关联的诊断运行 ID
    action: ActionSpec = Field(
        ..., description="Action requiring approval"
    )  # 需要审批的具体动作规格
    reason: str = Field(
        ..., description="Reason for the action"
    )  # 申请执行该动作的原因说明
    risk_level: str = Field(
        ..., description="Risk level assessment"
    )  # 风险等级评估结果
    evidence_refs: List[str] = Field(
        default_factory=list, description="References to supporting evidence"
    )  # 用于支撑审批决策的证据 ID 列表
    expected_impact: str = Field(
        ..., description="Expected impact of the action"
    )  # 动作预期产生的影响（正向/负向）
    rollback_plan: Optional[str] = Field(
        default=None, description="Rollback plan if approved"
    )  # 若出现问题时的回滚方案（可选）


class ApprovalResult(BaseModel):
    """
    审批结果模型，记录审批通过/拒绝/修改等决策及相关信息。
    """

    approval_id: str = Field(..., description="Approval identifier")  # 审批请求 ID
    decision: str = Field(
        ..., description="Decision (approved/rejected/modified)"
    )  # 审批决策（通过/拒绝/修改）
    approver: Optional[str] = Field(
        default=None, description="Who approved/rejected"
    )  # 审批人标识（账号、姓名等）
    comment: Optional[str] = Field(
        default=None, description="Approval comment"
    )  # 审批意见或说明
    created_at: str = Field(
        ..., description="Timestamp of decision"
    )  # 作出审批决策的时间戳（字符串格式）