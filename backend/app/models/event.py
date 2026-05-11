from pydantic import BaseModel, Field  # 引入 Pydantic 基类和字段声明工具
from typing import Optional, Dict, Any  # 引入可选类型与字典类型
from datetime import datetime  # 引入时间类型


class RunEvent(BaseModel):
    """
    运行事件模型，记录一次诊断运行过程中的关键事件，
    例如节点进入/退出、错误、重要日志等。
    """

    ts: datetime = Field(..., description="Event timestamp")  # 事件发生时间
    run_id: str = Field(..., description="Associated run ID")  # 关联的诊断运行 ID
    level: str = Field(
        ..., description="Event level (INFO/WARNING/ERROR)"
    )  # 事件级别（INFO/WARNING/ERROR）
    type: str = Field(..., description="Event type")  # 事件类型（自定义分类）
    node_name: Optional[str] = Field(
        default=None, description="Node that generated this event"
    )  # 产生该事件的节点名称（可选）
    message: str = Field(..., description="Event message")  # 事件的主提示信息
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional event data"
    )  # 附加的结构化数据（如上下文、参数等）