"""
SOAR Platform - Integration Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class IntegrationCategory(str, Enum):
    SIEM = "siem"
    EDR = "edr"
    TICKETING = "ticketing"
    EMAIL = "email"
    IP_INTEL = "ip_intelligence"
    THREAT_INTEL = "threat_intelligence"
    ENDPOINT = "endpoint"
    NETWORK = "network"
    FILE_SHARE = "file_share"
    IDENTITY = "identity"
    CLOUD = "cloud"


class ActionRiskLevel(str, Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY_LOW = "MODIFY_LOW"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ActionPermission(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class IntegrationStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class IntegrationHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class IntegrationConfigResponse(BaseModel):
    """Integration config response model."""
    id: int
    name: str
    category: IntegrationCategory
    description: Optional[str]
    config_schema: Optional[str]
    action_schemas: Optional[str]
    base_url: Optional[str]
    auth_type: Optional[str]
    default_timeout: int
    default_retry_count: int
    default_retry_delay: int
    enabled: bool
    version: Optional[str]
    metadata: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntegrationInstanceResponse(BaseModel):
    """Integration instance response model."""
    id: int
    config_id: int
    instance_name: str
    status: IntegrationStatus
    last_check: Optional[datetime]
    configuration: Optional[str]
    health_status: Optional[IntegrationHealthStatus]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntegrationActionResponse(BaseModel):
    """Integration action response model."""
    id: int
    config_id: int
    action_name: str
    full_path: Optional[str]
    description: Optional[str]
    input_schema: Optional[str]
    output_schema: Optional[str]
    risk_level: ActionRiskLevel
    required_permission: Optional[ActionPermission]
    requires_approval: bool
    ai_callable: bool
    default_timeout: int
    enabled: bool
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class IntegrationExecutionResponse(BaseModel):
    """Integration execution response model."""
    id: int
    action_instance_id: int
    incident_id: Optional[int]
    risk_level: ActionRiskLevel
    input_data: Optional[str]
    output_data: Optional[str]
    error_message: Optional[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    requires_approval: bool
    approval_id: Optional[int]
    metadata: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
