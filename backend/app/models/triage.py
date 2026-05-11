from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional  # 引入列表和可选类型


class TriageResult(BaseModel):
    """
    分诊结果模型，表示系统对事件的初步分类和判断，
    包括事件类型、严重级别、可疑服务等信息。
    """

    incident_type: str = Field(
        ..., description="Classified incident type"
    )  # 分类后的事件类型
    severity: str = Field(
        ..., description="Confirmed/adjusted severity"
    )  # 确认或调整后的严重级别
    suspected_services: List[str] = Field(
        default_factory=list, description="Services potentially involved"
    )  # 潜在涉及的服务列表
    suggested_time_window: Optional[dict] = Field(
        default=None, description="Recommended time range for investigation"
    )  # 推荐的排查时间范围
    requires_immediate_human: bool = Field(
        default=False, description="Whether human intervention is immediately required"
    )  # 是否需要立即人工介入
    rationale: str = Field(
        ..., description="Explanation for triage decision"
    )  # 做出该分诊决策的原因说明