from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import List, Optional, Dict, Any  # 引入列表、可选与字典类型
from datetime import datetime  # 引入时间类型


class EvidenceItem(BaseModel):
    """
    证据条目模型，表示从各类工具（日志、监控、部署、文档等）
    收集到的单条证据，用于辅助诊断和决策。
    """

    evidence_id: str = Field(
        ..., description="Unique evidence identifier"
    )  # 证据唯一标识
    tool_name: str = Field(
        ..., description="Tool that generated this evidence"
    )  # 产生该证据的工具名称
    category: str = Field(
        ..., description="Evidence category (logs/metrics/deployments/runbook/history)"
    )  # 证据类别（日志/指标/发布信息/文档等）
    source_ref: str = Field(
        ..., description="Reference to source (query ID, URL, etc.)"
    )  # 证据来源引用（如查询 ID、URL 等）
    source_timestamp: Optional[datetime] = Field(
        default=None, description="Timestamp of evidence source"
    )  # 证据源对应的时间（例如日志时间）
    summary: str = Field(
        ..., description="Brief summary of evidence"
    )  # 证据的摘要说明
    raw_payload: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw data from the tool"
    )  # 工具返回的原始数据（结构化）
    confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Confidence score"
    )  # 证据对当前推断的可信度评分（0~1）
    freshness_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="How fresh is this evidence"
    )  # 证据的新鲜度评分（0~1，越新越高）
    completeness_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="How complete is this evidence"
    )  # 证据的完整度评分（0~1）
    tags: List[str] = Field(
        default_factory=list, description="Tags for classification"
    )  # 用于分类和检索的标签列表
    error_hint: Optional[str] = Field(
        default=None, description="Hint if evidence collection had issues"
    )  # 若采集证据过程中出现异常，可在此给出错误提示
