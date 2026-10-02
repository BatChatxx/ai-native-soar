"""
SOAR Platform - AI Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AIIntent(str, Enum):
    ANALYZE_INCIDENT = "analyze_incident"
    CLASSIFY_THREAT = "classify_threat"
    GENERATE_FINDINGS = "generate_findings"
    RECOMMEND_ACTIONS = "recommend_actions"
    SUMMARIZE = "summarize"
    EXPLAIN = "explain"
    QUERY = "query"


class AISessionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolRisk(str, Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ToolType(str, Enum):
    EVIDENCE = "evidence"
    INCIDENT = "incident"
    INTEGRATION = "integration"
    SEARCH = "search"
    LOOKUP = "lookup"
    PLAYBOOK = "playbook"
    SYSTEM = "system"


class AIIntentEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LLMSessionResponse(BaseModel):
    """LLM session response model."""
    id: int
    session_id: str
    incident_id: Optional[int]
    session_type: Optional[str]
    intent: Optional[AIIntent]
    system_prompt: Optional[str]
    status: AISessionStatus
    model: Optional[str]
    model_version: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_tokens: Optional[int]
    final_response: Optional[str]
    error_message: Optional[str]
    metadata: Optional[str]
    
    class Config:
        from_attributes = True


class LLMMessageResponse(BaseModel):
    """LLM message response model."""
    id: int
    session_id: int
    role: str
    content: str
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LLMToolCallResponse(BaseModel):
    """LLM tool call response model."""
    id: int
    session_id: int
    tool_name: str
    tool_path: Optional[str]
    tool_type: Optional[ToolType]
    risk_level: ToolRisk
    arguments: Optional[str]
    status: str
    output: Optional[str]
    error: Optional[str]
    duration_ms: Optional[int]
    requires_approval: bool
    approval_id: Optional[int]
    metadata: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LLMFindingResponse(BaseModel):
    """LLM finding response model."""
    id: int
    session_id: int
    finding_type: Optional[str]
    title: Optional[str]
    content: Optional[str]
    confidence: Optional[int]
    evidence_ids: Optional[str]
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LLMToolResponse(BaseModel):
    """LLM tool response model."""
    id: int
    name: str
    path: Optional[str]
    description: Optional[str]
    input_schema: Optional[str]
    output_schema: Optional[str]
    risk_level: ToolRisk
    requires_approval: bool
    ai_callable: bool
    enabled: bool
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
