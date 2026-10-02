"""
SOAR Platform - Incident Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    TRIAGE = "triage"
    ANALYSIS = "analysis"
    CONTAINMENT = "containment"
    RESOLUTION = "resolution"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ObservableType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH_MD5 = "hash_md5"
    HASH_SHA1 = "hash_sha1"
    HASH_SHA256 = "hash_sha256"
    FILE = "file"
    PROCESS = "process"
    COMMAND = "command"
    EMAIL = "email"


class IncidentCreate(BaseModel):
    """Create incident."""
    title: str
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = IncidentStatus.NEW
    source_type: Optional[str] = None
    detection_id: Optional[str] = None
    tags: Optional[str] = None
    metadata: Optional[str] = None
    
    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    """Incident response model."""
    id: int
    incident_number: str
    title: str
    description: Optional[str]
    severity: Optional[IncidentSeverity]
    status: Optional[IncidentStatus]
    source_type: Optional[str]
    detection_id: Optional[str]
    tags: Optional[str]
    metadata: Optional[str]
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[int]
    assigned_to: Optional[str]
    
    class Config:
        from_attributes = True


class IncidentEventResponse(BaseModel):
    """Incident event response model."""
    id: int
    incident_id: int
    event_type: str
    title: str
    description: Optional[str]
    risk_level: Optional[str]
    actor_id: Optional[int]
    actor_type: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class IncidentCommentCreate(BaseModel):
    """Create incident comment."""
    content: str
    comment_type: Optional[str] = "analyst"
    evidence_ids: Optional[str] = None


class ObservableResponse(BaseModel):
    """Observable response model."""
    id: int
    incident_id: int
    observable_type: ObservableType
    value: str
    threat_level: Optional[str]
    confidence: int
    confidence_source: Optional[str]
    metadata: Optional[str]
    extracted_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncidentRelationshipResponse(BaseModel):
    """Incident relationship response model."""
    id: int
    incident_id: int
    entity_type: str
    entity_id: int
    relationship_type: str
    direction: Optional[str]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
