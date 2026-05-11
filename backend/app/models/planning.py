"""Planning models for memory retrieval and investigation.
用于记忆检索和排查规划的模型定义。
"""

from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import Any, Dict, List, Optional  # 引入通用类型注解


class MemoryHit(BaseModel):
    """
    记忆命中模型，表示从知识库/历史数据中检索到的一条结果，
    例如历史 RCA、服务文档、运行手册等。
    """

    source: str = Field(
        ..., description="Memory source (runbook/rca_history/service_doc/alert_experience)"
    )  # 记忆来源类型（运行手册/历史 RCA/服务文档/告警经验等）
    content: str = Field(
        ..., description="Retrieved content"
    )  # 检索到的具体内容（文本）
    relevance_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Relevance to current incident"
    )  # 与当前事件相关度评分（0~1）
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )  # 额外元数据（如文档 ID、URL、标签等）


class InvestigationTask(BaseModel):
    """
    排查任务模型，描述一次具体的证据采集或检查动作，
    例如拉日志、查指标、检查 K8s 状态等。
    """

    task_id: str = Field(
        ..., description="Unique task identifier"
    )  # 任务唯一标识
    category: str = Field(
        ..., description="Evidence category (logs/metrics/deployments/runbook/k8s/lb/db)"
    )  # 任务类别（日志/指标/部署/文档/K8s/LB/DB 等）
    tool_name: str = Field(
        ..., description="Tool to call"
    )  # 执行该任务要调用的工具名称
    priority: int = Field(
        default=5, ge=1, le=10, description="Priority 1-10 (1=highest)"
    )  # 优先级，1 为最高
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters"
    )  # 调用工具所需的参数
    depends_on: List[str] = Field(
        default_factory=list, description="Task IDs this depends on"
    )  # 依赖的其他任务 ID 列表（需先完成）
    degrade_on_failure: bool = Field(
        default=True, description="If true, failure degrades but doesn't terminate run"
    )  # 失败时是否仅降级而不终止整个流程
    timeout_ms: int = Field(
        default=30000, description="Timeout in milliseconds"
    )  # 任务超时时间（毫秒）


class InvestigationPlan(BaseModel):
    """
    排查计划模型，由多个排查任务构成，
    并包含整体的策略说明与时间预估。
    """

    tasks: List[InvestigationTask] = Field(
        default_factory=list, description="Investigation tasks"
    )  # 排查任务列表
    rationale: str = Field(
        default="", description="Rationale for this investigation plan"
    )  # 制定该排查计划的总体思路说明
    estimated_duration: Optional[str] = Field(
        default=None, description="Estimated total duration"
    )  # 预计整体耗时（字符串表示，如 '15m'）
