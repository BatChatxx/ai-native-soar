"""
SOAR Platform - User and Role Models
Defines authentication and authorization entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(str, Enum):
    """User roles for RBAC."""
    ANALYST = "analyst"
    SECURITY_ADMIN = "security_admin"
    SOC_MANAGER = "soc_manager"
    AUDITOR = "auditor"
    AI_AGENT = "ai_agent"


class Permission(str, Enum):
    """Available permissions."""
    # Read operations
    INCIDENT_READ = "incident:read"
    EVIDENCE_READ = "evidence:read"
    PLAYBOOK_READ = "playbook:read"
    INTEGRATION_READ = "integration:read"
    
    # Write operations
    INCIDENT_CREATE = "incident:create"
    INCIDENT_UPDATE = "incident:update"
    EVIDENCE_CREATE = "evidence:create"
    COMMENT_CREATE = "comment:create"
    
    # Automation
    AUTOMATION_EXECUTE = "automation:execute"
    PLAYBOOK_EXECUTE = "playbook:execute"
    
    # High-risk operations
    APPROVAL_MODIFY = "approval:modify"
    APPROVAL_CONTAIN = "approval:contain"
    APPROVAL_EXECUTE = "approval:execute"
    APPROVAL_DESTRUCTIVE = "approval:destructive"
    
    # Audit
    AUDIT_READ = "audit:read"


class User(Base):
    """User account."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", backref="users", lazy="joined")
    incidents = relationship("Incident", back_populates="owner", foreign_keys="Incident.owner_id")
    approval_requests = relationship("ApprovalRequest", back_populates="requester")
    audit_events = relationship("AuditEvent", back_populates="actor")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.name})>"


class RoleModel(Base):
    """Role definition with permissions."""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many with permissions
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class PermissionModel(Base):
    """Permission definition."""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RolePermission(Base):
    """Role-Permission junction table."""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    
    role = relationship("RoleModel", foreign_keys=[role_id])
    permission = relationship("PermissionModel", foreign_keys=[permission_id])
    
    __table_args__ = (
        {'unique': True, 'extend_existing': True},
    )
