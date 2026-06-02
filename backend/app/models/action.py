from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import Dict, Any, List, Optional  # 引入字典、列表、可选等类型


class ActionSpec(BaseModel):
    """
    运维动作规格模型，描述一次可执行动作的详细信息，
    例如重启、回滚、扩容等。
    """

    action_id: Optional[str] = Field(
        default=None, description="Unique action identifier"
    )  # 动作唯一标识（可选）
    action_type: str = Field(
        ..., description="Type of action (restart/revert/scale/rollback/etc)"
    )  # 动作类型（如重启/回滚/扩容等）
    service: str = Field(..., description="Target service")  # 目标服务名称
    env: str = Field(..., description="Target environment")  # 目标环境（prod/staging/dev 等）
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Action parameters"
    )  # 动作参数（根据不同类型传入不同字段）
    risk_level: str = Field(
        ..., description="Risk level (LOW/MEDIUM/HIGH/CRITICAL)"
    )  # 风险等级（LOW/MEDIUM/HIGH/CRITICAL）
    requires_approval: bool = Field(
        default=False, description="Whether this action requires approval"
    )  # 是否需要人工审批
    idempotency_key: Optional[str] = Field(
        default=None, description="Key for idempotency checks"
    )  # 幂等性 Key，用于防止重复执行
    supporting_evidence_ids: List[str] = Field(
        default_factory=list, description="Evidence IDs supporting this action"
    )  # 支持此动作的证据 ID 列表
    preconditions: Optional[List[str]] = Field(
        default=None, description="Conditions that must be true before execution"
    )  # 执行前置条件列表（必须满足的条件描述）
    verification_plan: Optional[str] = Field(
        default=None, description="How to verify the action succeeded"
    )  # 执行完成后的验证方案描述