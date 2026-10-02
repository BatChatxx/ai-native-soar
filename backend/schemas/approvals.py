"""
SOAR Platform - Approval Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ActionRisk(str, Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    MODIFY_LOW = "MODIFY_LOW"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApproverType(str, Enum):
    USER = "user"
    ROLE = "role"
    GROUP = "group"
    AI_ASSIST = "ai_assist"


class ApprovalRequestResponse(BaseModel):
    """Approval request response model."""
    id: int
    approval_id: str
    request_type: str
    description: str
    incident_id: Optional[int]
    action_type: Optional[str]
    action_target: Optional[str]
    action_metadata: Optional[str]
    risk_level: ActionRisk
    status: ApprovalStatus
    requested_by: Optional[str]
    requested_at: datetime
    expires_at: Optional[datetime]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    rejected_by: Optional[str]
    rejected_at: Optional[datetime]
    approver_type: Optional[ApproverType]
    ai_recommendation: Optional[str]
    ai_reasoning: Optional[str]
    
    class Config:
        from_attributes = True


class ApprovalCommentCreate(BaseModel):
    """Create approval comment."""
    content: str
    comment_type: Optional[str] = "analyst"


class ApprovalResponse(BaseModel):
    """Approval response model."""
    id: int
    approval_id: str
    request_type: str
    description: str
    status: ApprovalStatus
    requested_at: datetime
    approved_at: Optional[datetime]
    ai_recommendation: Optional[str]
    
    class Config:
        from_attributes = True
