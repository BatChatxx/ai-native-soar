"""
SOAR Platform - Automation Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AutomationType(str, Enum):
    SCRIPT = "script"
    FUNCTION = "function"
    WORKFLOW = "workflow"


class AutomationTrigger(str, Enum):
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    INCIDENT_TAG_CHANGE = "incident_tag_change"
    OBSERVABLE_DETECTED = "observable_detected"
    SCHEDULED = "scheduled"
    EVENT_MATCH = "event_match"
    MANUAL = "manual"


class AutomationStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class AutomationRisk(str, Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class AutomationStatusEnum(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AutomationScriptResponse(BaseModel):
    """Automation script response model."""
    id: int
    name: str
    description: Optional[str]
    definition: Optional[str]
    script_type: Optional[AutomationType]
    trigger: Optional[AutomationTrigger]
    trigger_config: Optional[str]
    status: AutomationStatus
    risk_level: AutomationRisk
    requires_approval: bool
    author: Optional[str]
    tags: Optional[str]
    input_schema: Optional[str]
    output_schema: Optional[str]
    timeout: int
    max_retries: int
    retry_delay: int
    metadata: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AutomationVersionResponse(BaseModel):
    """Automation version response model."""
    id: int
    script_id: int
    version: str
    version_hash: Optional[str]
    definition: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AutomationRunResponse(BaseModel):
    """Automation run response model."""
    id: int
    version_id: int
    script_id: Optional[int]
    incident_id: Optional[int]
    input_data: Optional[str]
    status: AutomationStatusEnum
    output_data: Optional[str]
    error_message: Optional[str]
    risk_level: AutomationRisk
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    requires_approval: bool
    approval_id: Optional[int]
    audit_event_id: Optional[int]
    metadata: Optional[str]
    
    class Config:
        from_attributes = True
