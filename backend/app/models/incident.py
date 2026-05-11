from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import Optional, Dict, Any  # 引入可选类型和字典类型
from datetime import datetime  # 引入时间类型


class IncidentTicket(BaseModel):
    """
    事件工单模型，表示一次告警/事故的基础信息。
    由上游告警系统或人工创建后，作为诊断流程的输入。
    """

    ticket_id: str = Field(..., description="Unique ticket identifier")  # 工单唯一标识
    title: str = Field(..., description="Incident title")  # 事件标题
    description: str = Field(..., description="Detailed incident description")  # 事件详细描述
    service: str = Field(..., description="Affected service name")  # 受影响服务名
    env: str = Field(..., description="Environment (prod/staging/dev)")  # 环境（prod/staging/dev）
    severity: str = Field(
        ..., description="Severity level (P1/P2/P3/P4)"
    )  # 严重级别（P1/P2/P3/P4）
    time_range: Optional[Dict[str, datetime]] = Field(
        default=None, description="Time window for investigation"
    )  # 建议排查的时间范围（起止时间）
    source: str = Field(
        ..., description="Ticket source (pagerduty/alertmanager/manual)"
    )  # 工单来源（如 pagerduty/alertmanager/人工）
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )  # 其他附加元数据（如标签、扩展字段）