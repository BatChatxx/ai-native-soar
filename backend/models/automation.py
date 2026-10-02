"""
SOAR Platform - Automation Models
Defines automation script entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text as TextType
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AutomationTrigger(str, Enum):
    """Automation triggers."""
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    INCIDENT_TAG_CHANGE = "incident_tag_change"
    OBSERVABLE_DETECTED = "observable_detected"
    SCHEDULED = "scheduled"
    EVENT_MATCH = "event_match"
    MANUAL = "manual"


class AutomationType(str, Enum):
    """Automation script types."""
    SCRIPT = "script"
    FUNCTION = "function"
    WORKFLOW = "workflow"


class AutomationStatus(str, Enum):
    """Automation lifecycle status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class AutomationRisk(str, Enum):
    """Automation risk classification."""
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class AutomationScript(Base):
    """Automation script definition."""
    __tablename__ = "automation_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Script name
    name = Column(String(150), nullable=False)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Script definition (Python, YAML, etc.)
    definition = Column(TextType, nullable=True)
    
    # Script type
    script_type = Column(SQLEnum(AutomationType), nullable=True)
    
    # Trigger
    trigger = Column(SQLEnum(AutomationTrigger), nullable=True)
    trigger_config = Column(TextType, nullable=True)
    
    # Status
    status = Column(SQLEnum(AutomationStatus), nullable=False, default=AutomationStatus.DRAFT)
    
    # Risk classification
    risk_level = Column(SQLEnum(AutomationRisk), nullable=False, default=AutomationRisk.READ)
    
    # Whether script requires approval to execute
    requires_approval = Column(Boolean, default=False)
    
    # Author
    author = Column(String(100), nullable=True)
    
    # Tags
    tags = Column(String(500), nullable=True)
    
    # Input/output schemas
    input_schema = Column(TextType, nullable=True)
    output_schema = Column(TextType, nullable=True)
    
    # Timeout (seconds)
    timeout = Column(Integer, default=300)
    
    # Retry settings
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)
    
    # Metadata JSON
    meta = Column("metadata", TextType, nullable=True)  # Using 'meta' to avoid 'metadata' reserved word
    
    # Created/updated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("AutomationVersion", back_populates="script")
    runs = relationship("AutomationRun", back_populates="script")
    
    def __repr__(self):
        return f"<AutomationScript(name={self.name}, risk={self.risk_level.value}, status={self.status.value})>"


class AutomationVersion(Base):
    """Version history for automation scripts."""
    __tablename__ = "automation_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to parent script
    script_id = Column(Integer, ForeignKey("automation_scripts.id", ondelete="CASCADE"), nullable=False)
    script = relationship("AutomationScript", foreign_keys=[script_id])
    
    # Version info
    version = Column(String(20), nullable=False)
    version_hash = Column(String(40), nullable=True)
    
    # Definition
    definition = Column(TextType, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    runs = relationship("AutomationRun", back_populates="version")
    
    def __repr__(self):
        return f"<AutomationVersion(script_id={self.script_id}, version={self.version})>"


class AutomationRun(Base):
    """Automation execution record."""
    __tablename__ = "automation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to automation script version
    version_id = Column(Integer, ForeignKey("automation_versions.id", ondelete="CASCADE"), nullable=False)
    version = relationship("AutomationVersion", foreign_keys=[version_id])
    
    # Reference to parent script
    script_id = Column(Integer, ForeignKey("automation_scripts.id", ondelete="SET NULL"), nullable=True)
    script = relationship("AutomationScript", foreign_keys=[script_id])
    
    # Incident reference (if applicable)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    # Input data (never store secrets!)
    input_data = Column(TextType, nullable=True)
    
    # Execution status
    status = Column(String(50), nullable=False, default="running")  # "running", "completed", "failed", "cancelled", "timeout"
    
    # Output
    output_data = Column(TextType, nullable=True)
    
    # Error info
    error_message = Column(String(500), nullable=True)
    
    # Risk level
    risk_level = Column(String(20), nullable=False)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Approval info
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    
    # Audit
    audit_event_id = Column(Integer, ForeignKey("audit_events.id"), nullable=True)
    
    # Metadata JSON
    meta = Column("metadata", TextType, nullable=True)  # Using 'meta' to avoid 'metadata' reserved word
    
    # Relationships
    incident = relationship("Incident", foreign_keys=[incident_id], backref="automation_runs")
    version = relationship("AutomationVersion", back_populates="runs")
    script = relationship("AutomationScript", back_populates="runs")
    approval = relationship("ApprovalRequest", foreign_keys=[approval_id])
    audit = relationship("AuditEvent", foreign_keys=[audit_event_id])
    
    def __repr__(self):
        return f"<AutomationRun(version_id={self.version_id}, script_id={self.script_id}, status={self.status})>"


class AutomationExecution(Base):
    """Detailed execution log for automation run."""
    __tablename__ = "automation_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to automation run
    automation_run_id = Column(Integer, ForeignKey("automation_runs.id", ondelete="CASCADE"), nullable=False)
    automation_run = relationship("AutomationRun", foreign_keys=[automation_run_id])
    
    # Execution line/step
    line_number = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="pending")  # "pending", "running", "completed", "failed"
    
    # Output
    output = Column(TextType, nullable=True)
    
    # Error
    error = Column(String(500), nullable=True)
    
    # Duration
    duration_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    automation_run = relationship("AutomationRun", back_populates="executions")
    
    def __repr__(self):
        return f"<AutomationExecution(run_id={self.automation_run_id}, line={self.line_number}, status={self.status})>"


AutomationRun.executions = relationship("AutomationExecution", back_populates="automation_run")
