"""
SOAR Platform - Audit Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AuditEventResponse(BaseModel):
    """Audit event response model."""
    id: int
    incident_id: Optional[int]
    actor_id: Optional[int]
    actor_type: Optional[str]
    action: str
    action_type: Optional[str]
    risk_level: Optional[str]
    category: Optional[str]
    details: Optional[str]
    success: bool
    error_message: Optional[str]
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
