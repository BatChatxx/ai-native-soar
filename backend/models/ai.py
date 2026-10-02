"""
AI Models for LLM Integration

These models define the structure for LLM tool calls and messages.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime


class LLMMessage(BaseModel):
    """LLM message for chat completion"""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class LLMTool(BaseModel):
    """Registered AI tool"""
    id: Optional[int] = None
    name: str = Field(..., description="Unique tool name")
    path: str = Field(default="", description="Tool path (optional)")
    description: str = Field(default="", description="Tool description")
    input_schema: Dict[str, Any] = Field(default={}, description="Input schema (JSON)")
    output_schema: Dict[str, Any] = Field(default={}, description="Output schema (JSON)")
    risk_level: str = Field(..., description="Risk level: READ, ENRICH, MODIFY, CONTAIN, EXECUTE, DESTRUCTIVE")
    requires_approval: bool = Field(default=False, description="Whether action requires approval")
    ai_callable: bool = Field(default=True, description="Whether tool is callable by AI")
    enabled: bool = Field(default=True, description="Whether tool is enabled")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None


class LLMToolCreate(BaseModel):
    """Create new AI tool request"""
    name: str = Field(..., description="Unique tool name")
    path: str = Field(default="", description="Tool path")
    description: str = Field(default="", description="Tool description")
    input_schema: Dict[str, Any] = Field(default={}, description="Input schema")
    output_schema: Dict[str, Any] = Field(default={}, description="Output schema")
    risk_level: str = Field(..., description="Risk level")
    requires_approval: bool = Field(default=False, description="Requires approval")
    ai_callable: bool = Field(default=True, description="AI can call this")
    enabled: bool = Field(default=True, description="Enabled by default")
    metadata: Dict[str, Any] = Field(default={}, description="Metadata")


class LLMToolCall(BaseModel):
    """LLM tool call"""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique tool call ID")
    tool_id: str = Field(..., description="Tool ID/name")
    arguments: Any = Field(default={}, description="Tool arguments")
    approval_id: Optional[str] = Field(None, description="Approval ID if required")


class LLMToolCallRequest(BaseModel):
    """LLM tool call request"""
    tool_name: str = Field(..., description="Tool name")
    arguments: Any = Field(default={}, description="Tool arguments")
    approval_id: Optional[str] = Field(None, description="Approval ID for high-risk actions")


class LLMToolCallResponse(BaseModel):
    """LLM tool call response"""
    tool_call_id: str = Field(..., description="Tool call ID")
    status: str = Field(..., description="Status: completed, error, pending_approval")
    type: str = Field(default="tool_call", description="Response type")
    name: Optional[str] = Field(None, description="Tool name")
    output: Any = Field(default=None, description="Tool output")
    content: Optional[str] = Field(None, description="Error/content message")


class LLMSession(BaseModel):
    """LLM investigation session"""
    id: Optional[int] = None
    incident_id: int = Field(..., description="Associated incident")
    session_id: str = Field(..., description="Unique session ID")
    status: str = Field(default="in_progress", description="Session status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None


class LLMMessageSession(BaseModel):
    """LLM message in session"""
    id: Optional[int] = None
    session_id: int = Field(..., description="Session ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LLMToolCallSession(BaseModel):
    """LLM tool call in session"""
    id: Optional[int] = None
    session_id: int = Field(..., description="Session ID")
    tool_name: str = Field(..., description="Tool name")
    arguments: Any = Field(default={}, description="Tool arguments")
    status: str = Field(..., description="Call status")
    output: Any = Field(default=None, description="Call output")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LLMFinding(BaseModel):
    """LLM investigation finding"""
    id: Optional[int] = None
    session_id: int = Field(..., description="Session ID")
    evidence_ids: List[int] = Field(default=[], description="Related evidence IDs")
    finding_type: str = Field(..., description="Finding type: observed, inference, hypothesis, recommendation")
    title: str = Field(..., description="Finding title")
    description: str = Field(..., description="Finding description")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LLMSessionCreate(BaseModel):
    """Create new LLM session"""
    incident_id: int = Field(..., description="Associated incident")
    initial_prompt: str = Field(..., description="Initial investigation prompt")
    tools_enabled: bool = Field(default=True, description="Enable tool calling")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Temperature for creativity")
    max_tokens: int = Field(default=4096, ge=100, le=8192, description="Max tokens")
