"""
SOAR Platform - Playbook Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PlaybookStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class PlaybookStepType(str, Enum):
    TASK = "task"
    IF = "if"
    PARALLEL = "parallel"
    FOR_EACH = "for_each"
    WAIT = "wait"
    APPROVAL = "approval"
    ERROR_HANDLER = "error_handler"
    END = "end"


class PlaybookStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class PlaybookTrigger(str, Enum):
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    SEVERITY_THRESHOLD = "severity_threshold"
    TAG_MATCH = "tag_match"
    OBSERVABLE_MATCH = "observable_match"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class PlaybookResponse(BaseModel):
    """Playbook response model."""
    id: int
    name: str
    version: str
    version_hash: Optional[str]
    definition: Optional[str]
    trigger: Optional[PlaybookTrigger]
    trigger_config: Optional[str]
    status: PlaybookStatus
    description: Optional[str]
    tags: Optional[str]
    metadata: Optional[str]
    author: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlaybookVersionResponse(BaseModel):
    """Playbook version response model."""
    id: int
    playbook_id: int
    version: str
    version_hash: Optional[str]
    definition: Optional[str]
    notes: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlaybookRunResponse(BaseModel):
    """Playbook run response model."""
    id: int
    playbook_version_id: int
    incident_id: Optional[int]
    trigger: Optional[str]
    input_data: Optional[str]
    status: str
    output_data: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    metadata: Optional[str]
    
    class Config:
        from_attributes = True


class PlaybookStepRunResponse(BaseModel):
    """Playbook step run response model."""
    id: int
    playbook_run_id: int
    step_id: Optional[int]
    step_type: Optional[str]
    name: Optional[str]
    status: PlaybookStepStatus
    output_data: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    retry_count: int
    max_retries: Optional[int]
    requires_approval: bool
    approval_id: Optional[int]
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlaybookApprovalResponse(BaseModel):
    """Playbook approval response model."""
    id: int
    playbook_run_id: int
    approval_id: str
    action_type: str
    action_target: Optional[str]
    risk_level: str
    status: PlaybookStatus
    requested_at: datetime
    approved_at: Optional[datetime]
    expires_at: Optional[datetime]
    approved_by: Optional[str]
    rejected_by: Optional[str]
    rejection_reason: Optional[str]
    ai_recommendation: Optional[str]
    ai_reasoning: Optional[str]
    
    class Config:
        from_attributes = True
