"""
SOAR Platform - Approval Models
Defines approval request entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ActionRisk(str, Enum):
    """Action risk levels requiring approval."""
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    MODIFY_LOW = "MODIFY_LOW"
    CONTAIN = "CONTAIN"
    MODIFY = "MODIFY"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ApprovalStatus(str, Enum):
    """Approval request states."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApproverType(str, Enum):
    """Who can approve an action."""
    USER = "user"
    ROLE = "role"
    GROUP = "group"
    AI_ASSIST = "ai_assist"


class ApprovalRequest(Base):
    """Approval request for high-risk actions."""
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Stable approval ID
    approval_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # Request details
    request_type = Column(String(50), nullable=False)  # "action", "incident_change", etc.
    description = Column(Text, nullable=False)
    
    # Incident reference
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    # Action details
    action_type = Column(String(200), nullable=True)  # e.g., "generic_edr.contain_host"
    action_target = Column(String(500), nullable=True)  # e.g., "host:WS123"
    action_metadata = Column(Text, nullable=True)
    
    # Risk level
    risk_level = Column(SQLEnum(ActionRisk), nullable=False)
    
    # Status
    status = Column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    
    # Request info
    requested_by = Column(String(100), nullable=True)  # User ID or "ai_agent"
    requested_at = Column(DateTime, default=datetime.utcnow)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Approval info
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    rejected_by = Column(String(100), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    # Approver type
    approver_type = Column(SQLEnum(ApproverType), nullable=True)
    
    # AI decision (for AI-assisted approval)
    ai_recommendation = Column(String(50), nullable=True)  # "approve", "reject", "neutral"
    ai_reasoning = Column(Text, nullable=True)
    
    # Audit info
    audit_event_id = Column(Integer, ForeignKey("audit_events.id"), nullable=True)
    
    # Relationships
    incident = relationship("Incident", foreign_keys=[incident_id], backref="pending_approvals")
    audit_event = relationship("AuditEvent", foreign_keys=[audit_event_id])
    
    def __repr__(self):
        return f"<ApprovalRequest(id={self.id}, approval_id={self.approval_id}, type={self.request_type}, status={self.status.value})>"


class ApprovalComment(Base):
    """Comments on approval requests."""
    __tablename__ = "approval_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    approval_request_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False)
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Comment type
    comment_type = Column(String(50), nullable=True)  # "analyst", "ai_assistant"
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    approval_request = relationship("ApprovalRequest", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<ApprovalComment(id={self.id}, approval_id={self.approval_request_id})>"


ApprovalRequest.comments = relationship("ApprovalComment", back_populates="approval_request")
