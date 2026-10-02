"""
SOAR Platform - Playbook Models
Defines playbook and execution entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Table, Text as TextType
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class PlaybookStatus(str, Enum):
    """Playbook lifecycle status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class PlaybookStepType(str, Enum):
    """Playbook step types."""
    TASK = "task"
    IF = "if"
    PARALLEL = "parallel"
    FOR_EACH = "for_each"
    WAIT = "wait"
    APPROVAL = "approval"
    ERROR_HANDLER = "error_handler"
    END = "end"


class PlaybookStepStatus(str, Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class PlaybookTrigger(str, Enum):
    """Playbook triggers."""
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    SEVERITY_THRESHOLD = "severity_threshold"
    TAG_MATCH = "tag_match"
    OBSERVABLE_MATCH = "observable_match"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class Playbook(Base):
    """Playbook definition."""
    __tablename__ = "playbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Playbook name
    name = Column(String(150), nullable=False)
    
    # Version (e.g., "1.0.0")
    version = Column(String(20), nullable=False)
    
    # Full version identifier (e.g., "1.0.0-abc123")
    version_hash = Column(String(40), nullable=True)
    
    # Playbook definition (YAML/JSON)
    definition = Column(TextType, nullable=True)
    
    # Trigger definition
    trigger = Column(SQLEnum(PlaybookTrigger), nullable=True)
    trigger_config = Column(TextType, nullable=True)
    
    # Status
    status = Column(SQLEnum(PlaybookStatus), nullable=False, default=PlaybookStatus.DRAFT)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Tags
    tags = Column(String(500), nullable=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    # Author
    author = Column(String(100), nullable=True)
    
    # Created/updated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Playbook(name={self.name}, version={self.version}, status={self.status.value})>"


class PlaybookVersion(Base):
    """Version history for playbooks."""
    __tablename__ = "playbook_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to parent playbook
    playbook_id = Column(Integer, ForeignKey("playbooks.id", ondelete="CASCADE"), nullable=False)
    playbook = relationship("Playbook", foreign_keys=[playbook_id])
    
    # Version info
    version = Column(String(20), nullable=False)
    version_hash = Column(String(40), nullable=True)
    
    # Definition
    definition = Column(TextType, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="active")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    runs = relationship("PlaybookRun", back_populates="playbook_version")
    
    def __repr__(self):
        return f"<PlaybookVersion(playbook_id={self.playbook_id}, version={self.version})>"


class PlaybookStep(Base):
    """Playbook step definition."""
    __tablename__ = "playbook_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to playbook version
    playbook_version_id = Column(Integer, ForeignKey("playbook_versions.id", ondelete="CASCADE"), nullable=False)
    playbook_version = relationship("PlaybookVersion", foreign_keys=[playbook_version_id])
    
    # Step type
    step_type = Column(SQLEnum(PlaybookStepType), nullable=False)
    
    # Step name
    name = Column(String(150), nullable=True)
    
    # Step description
    description = Column(Text, nullable=True)
    
    # Step definition (YAML/JSON)
    definition = Column(TextType, nullable=True)
    
    # Order
    order = Column(Integer, nullable=False)
    
    # Dependencies (JSON array)
    dependencies = Column(TextType, nullable=True)
    
    # Status (for execution)
    status = Column(SQLEnum(PlaybookStepStatus), nullable=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    # Created
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("PlaybookStepRun", back_populates="step")
    
    def __repr__(self):
        return f"<PlaybookStep(playbook_version_id={self.playbook_version_id}, type={self.step_type.value})>"


class PlaybookRun(Base):
    """Playbook execution record."""
    __tablename__ = "playbook_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to playbook version (exact version that executed)
    playbook_version_id = Column(Integer, ForeignKey("playbook_versions.id", ondelete="CASCADE"), nullable=False)
    playbook_version = relationship("PlaybookVersion", foreign_keys=[playbook_version_id])
    
    # Incident reference (if applicable)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    # Trigger
    trigger = Column(String(100), nullable=True)
    
    # Playbook input
    input_data = Column(TextType, nullable=True)
    
    # Execution status
    status = Column(String(50), nullable=False, default="running")  # "running", "completed", "failed", "cancelled"
    
    # Results
    output_data = Column(TextType, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    # Relationships
    incident = relationship("Incident", foreign_keys=[incident_id], backref="playbook_runs")
    playbook_version = relationship("PlaybookVersion", back_populates="runs")
    steps = relationship("PlaybookStepRun", back_populates="run")
    
    def __repr__(self):
        return f"<PlaybookRun(playbook_version_id={self.playbook_version_id}, incident_id={self.incident_id}, status={self.status})>"


class PlaybookStepRun(Base):
    """Individual step execution record."""
    __tablename__ = "playbook_step_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to playbook run
    playbook_run_id = Column(Integer, ForeignKey("playbook_runs.id", ondelete="CASCADE"), nullable=False)
    playbook_run = relationship("PlaybookRun", back_populates="steps")
    
    # Reference to step definition
    step_id = Column(Integer, ForeignKey("playbook_steps.id", ondelete="SET NULL"), nullable=True)
    step = relationship("PlaybookStep", foreign_keys=[step_id])
    
    # Step execution status
    status = Column(SQLEnum(PlaybookStepStatus), nullable=False, default=PlaybookStepStatus.PENDING)
    
    # Step result
    output_data = Column(TextType, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    # Execution timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Retry info
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, nullable=True)
    
    # Approval info
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    # Created
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("PlaybookRun", back_populates="steps")
    step = relationship("PlaybookStep", back_populates="run")
    approval = relationship("ApprovalRequest", foreign_keys=[approval_id])
    
    def __repr__(self):
        return f"<PlaybookStepRun(playbook_run_id={self.playbook_run_id}, step_id={self.step_id}, status={self.status.value})>"


class PlaybookApproval(Base):
    """Approval required for playbook execution."""
    __tablename__ = "playbook_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to playbook run
    playbook_run_id = Column(Integer, ForeignKey("playbook_runs.id", ondelete="CASCADE"), nullable=False)
    playbook_run = relationship("PlaybookRun", foreign_keys=[playbook_run_id])
    
    # Approval ID
    approval_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # Action being approved
    action_type = Column(String(200), nullable=False)
    action_target = Column(String(500), nullable=True)
    
    # Risk level
    risk_level = Column(String(20), nullable=False)
    
    # Status
    status = Column(SQLEnum(PlaybookStatus), nullable=False, default=PlaybookStatus.PENDING_APPROVAL)
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Approver
    approved_by = Column(String(100), nullable=True)
    rejected_by = Column(String(100), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # AI info
    ai_recommendation = Column(String(50), nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    
    # Relationships
    playbook_run = relationship("PlaybookRun", back_populates="approvals")
    
    def __repr__(self):
        return f"<PlaybookApproval(playbook_run_id={self.playbook_run_id}, approval_id={self.approval_id})>"


PlaybookRun.approvals = relationship("PlaybookApproval", back_populates="playbook_run")
