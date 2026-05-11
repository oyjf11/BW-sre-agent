from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class ToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to call")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters for the tool"
    )
    run_id: Optional[str] = Field(
        default=None, description="Associated run ID for tracking"
    )


class ToolResponse(BaseModel):
    tool_name: str = Field(..., description="Name of the tool that was called")
    success: bool = Field(..., description="Whether the tool call succeeded")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Tool execution result"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    latency_ms: int = Field(..., description="Execution time in milliseconds")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class ToolMetadata(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    risk_level: str = Field(default="LOW", description="Risk level")
    requires_approval: bool = Field(default=False)
    timeout_ms: int = Field(default=30000)
    retries: int = Field(default=1)


TOOL_REGISTRY: Dict[str, ToolMetadata] = {}


def register_tool(metadata: ToolMetadata):
    TOOL_REGISTRY[metadata.name] = metadata
