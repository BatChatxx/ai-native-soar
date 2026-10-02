"""
SOAR Platform - Audit Models
Defines audit logging entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AuditLevel(str, Enum):
    """Audit log levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Audit event categories."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    MFA = "mfa"
    PASSWORD_CHANGE = "password_change"
    
    # Data operations
    INCIDENT_CREATE = "incident:create"
    INCIDENT_UPDATE = "incident:update"
    INCIDENT_DELETE = "incident:delete"
    INCIDENT_ARCHIVE = "incident:archive"
    INCIDENT_CLOSE = "incident:close"
    
    EVIDENCE_CREATE = "evidence:create"
    EVIDENCE_UPDATE = "evidence:update"
    EVIDENCE_DELETE = "evidence:delete"
    
    COMMENT_CREATE = "comment:create"
    COMMENT_UPDATE = "comment:update"
    
    # Automation
    PLAYBOOK_EXECUTE = "playbook:execute"
    PLAYBOOK_CREATE = "playbook:create"
    PLAYBOOK_UPDATE = "playbook:update"
    
    AUTOMATION_EXECUTE = "automation:execute"
    AUTOMATION_CREATE = "automation:create"
    
    # Integrations
    INTEGRATION_CREATE = "integration:create"
    INTEGRATION_UPDATE = "integration:update"
    INTEGRATION_DELETE = "integration:delete"
    INTEGRATION_ACTION = "integration:action"
    
    # AI
    AI_SESSION_START = "ai:session_start"
    AI_TOOL_CALL = "ai:tool_call"
    AI_FINDING = "ai:finding"
    
    # Approvals
    APPROVAL_REQUESTED = "approval:requested"
    APPROVAL_GRANTED = "approval:granted"
    APPROVAL_DENIED = "approval:denied"
    
    # System
    ERROR = "error"
    CONFIG_CHANGE = "config:change"
    SECURITY_EVENT = "security:event"
    
    # Read operations (for audit)
    INCIDENT_READ = "incident:read"
    EVIDENCE_READ = "evidence:read"
    AUDIT_READ = "audit:read"


class AuditEvent(Base):
    """Audit event record."""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference back to incident
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    # Actor info
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_type = Column(String(50), nullable=True)  # "user", "ai_agent", "system"
    
    # Action
    action = Column(String(200), nullable=False)
    action_type = Column(String(50), nullable=True)
    
    # Risk level (if applicable)
    risk_level = Column(String(20), nullable=True)  # READ, ENRICH, MODIFY, etc.
    
    # Category
    category = Column(SQLEnum(AuditCategory), nullable=True)
    
    # Details - stored securely, never in logs
    details = Column(Text, nullable=True)
    # Sensitive fields are filtered from details before storage
    
    # Outcome
    success = Column(Boolean, default=True)
    error_message = Column(String(500), nullable=True)
    
    # Metadata JSON
    meta = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    incident = relationship("Incident", foreign_keys=[incident_id], backref="audit_events")
    actor = relationship("User", foreign_keys=[actor_id], backref="audit_events")
    
    def __repr__(self):
        return f"<AuditEvent(id={self.id}, actor={self.actor_id}, action={self.action}, level={AuditLevel.INFO})>"


class AuditSnapshot(Base):
    """Snapshot of critical data for audit trail."""
    __tablename__ = "audit_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Related record
    entity_type = Column(String(50), nullable=False)  # "incident", "user", etc.
    entity_id = Column(Integer, nullable=False)
    
    # Snapshot of entity state (JSON)
    snapshot_data = Column(Text, nullable=False)
    
    # Triggering event
    triggering_event = Column(String(500), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", foreign_keys=[entity_id], remote_side=[id])
    
    def __repr__(self):
        return f"<AuditSnapshot(id={self.id}, entity={self.entity_type}, id={self.entity_id})>"
