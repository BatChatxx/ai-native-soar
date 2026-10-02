"""
SOAR Platform - Pydantic Schemas
API request and response models.
"""

from schemas.users import UserResponse, UserCreate, RoleResponse
from schemas.incidents import (
    IncidentResponse, IncidentCreate,
    IncidentEventResponse,
    IncidentCommentCreate, ObservableResponse,
    IncidentRelationshipResponse
)
from schemas.evidence import (
    EvidenceResponse, FindingResponse,
    EvidenceLinkResponse
)
from schemas.approvals import (
    ApprovalRequestResponse, ApprovalCommentCreate,
    ApprovalResponse
)
from schemas.audit import AuditEventResponse
from schemas.integrations import (
    IntegrationConfigResponse, IntegrationInstanceResponse,
    IntegrationActionResponse, IntegrationExecutionResponse
)
from schemas.playbooks import (
    PlaybookResponse, PlaybookVersionResponse,
    PlaybookRunResponse, PlaybookStepRunResponse,
    PlaybookApprovalResponse
)
from schemas.automation import (
    AutomationScriptResponse, AutomationVersionResponse,
    AutomationRunResponse
)
from schemas.ai import (
    LLMSessionResponse, LLMMessageResponse,
    LLMToolCallResponse, LLMFindingResponse,
    LLMToolResponse
)
from schemas.dashboard import DashboardStats

__all__ = [
    # Users
    "UserResponse",
    "UserCreate",
    "RoleResponse",
    
    # Incidents
    "IncidentResponse",
    "IncidentCreate",
    "IncidentEventResponse",
    "IncidentCommentCreate",
    "ObservableResponse",
    "IncidentRelationshipResponse",
    
    # Evidence
    "EvidenceResponse",
    "FindingResponse",
    "EvidenceLinkResponse",
    
    # Approvals
    "ApprovalRequestResponse",
    "ApprovalCommentCreate",
    "ApprovalResponse",
    
    # Audit
    "AuditEventResponse",
    
    # Integrations
    "IntegrationConfigResponse",
    "IntegrationInstanceResponse",
    "IntegrationActionResponse",
    "IntegrationExecutionResponse",
    
    # Playbooks
    "PlaybookResponse",
    "PlaybookVersionResponse",
    "PlaybookRunResponse",
    "PlaybookStepRunResponse",
    "PlaybookApprovalResponse",
    
    # Automation
    "AutomationScriptResponse",
    "AutomationVersionResponse",
    "AutomationRunResponse",
    
    # AI
    "LLMSessionResponse",
    "LLMMessageResponse",
    "LLMToolCallResponse",
    "LLMFindingResponse",
    "LLMToolResponse",
    
    # Dashboard
    "DashboardStats",
]
