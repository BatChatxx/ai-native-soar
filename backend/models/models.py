"""
Core SOAR Database Models

All models inherit from Base and are mapped to PostgreSQL tables.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum,
    Boolean, JSON, ForeignKey, Table, BigInteger, Float,
    func, event
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# Allow legacy relationship annotations (SQLAlchemy 2.0 migration)
Base.__allow_unmapped__ = True

# ============= USER & AUTHENTICATION =============

class User(Base):
    """SOAR user account"""
    __allow_unmapped__ = True
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    incidents = relationship("Incident", back_populates="owner", foreign_keys="Incident.owner_id", lazy="dynamic")
    events = relationship("IncidentEvent", back_populates="user", foreign_keys="IncidentEvent.user_id", lazy="dynamic")
    approvals = relationship("ApprovalRequest", back_populates="user", foreign_keys="ApprovalRequest.submitted_by", lazy="dynamic")
    comments = relationship("IncidentComment", back_populates="user", foreign_keys="IncidentComment.user_id", lazy="dynamic")


class Role(Base):
    """User role"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", secondary="user_roles")


class UserRole(Base):
    """User-role association"""
    __tablename__ = "user_roles"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)


# ============= INCIDENTS =============

class Incident(Base):
    """Security incident"""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(50), default="medium")
    status = Column(String(50), default="open")
    priority = Column(String(50), default="medium")
    source_type = Column(String(100), default="manual")
    detection_id = Column(String(255))
    detection_source = Column(String(100))
    number = Column(String(50), unique=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    parent_incident_id = Column(Integer, ForeignKey("incidents.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # Flags
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    parent_incident = relationship("Incident", foreign_keys=[parent_incident_id])
    events = relationship("IncidentEvent", back_populates="incident")
    comments = relationship("IncidentComment", back_populates="incident")
    findings = relationship("IncidentFinding", back_populates="incident")
    tags = relationship("IncidentTag", back_populates="incident")
    artifacts = relationship("IncidentArtifact", back_populates="incident")
    observables = relationship("IncidentObservable", back_populates="incident")
    relationships = relationship("IncidentRelationship", back_populates="incident")
    approvals = relationship("ApprovalRequest", back_populates="incident")


# ============= ALERTS =============

class Alert(Base):
    """Security alert (pre-incident detection signal)"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), unique=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(50), default="medium")
    status = Column(String(50), default="new")
    source_type = Column(String(100), default="manual")
    source_id = Column(String(255))
    detection_id = Column(String(255))
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    incident = relationship("Incident", foreign_keys=[incident_id])
    observables = relationship("AlertObservable", back_populates="alert")


class AlertObservable(Base):
    """Observable (IOC) attached to an alert"""
    __tablename__ = "alert_observables"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    observable_type = Column(String(50), nullable=False)
    observable_value = Column(String(500), nullable=False)
    severity = Column(String(50))

    # Enrichment fields
    enrichment_status = Column(String(20), default="pending")
    malicious_score = Column(Integer)
    reputation = Column(String(20))
    enrichment_data = Column(JSON)
    enriched_at = Column(DateTime(timezone=True))

    # Timestamps
    observed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    alert = relationship("Alert", back_populates="observables")


class IncidentEvent(Base):
    """Incident timeline event"""
    __tablename__ = "incident_events"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="events")
    user = relationship("User")


class IncidentComment(Base):
    """Incident comment"""
    __tablename__ = "incident_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="comments")
    user = relationship("User")


class IncidentTag(Base):
    """Incident tag"""
    __tablename__ = "incident_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="tags")


class IncidentArtifact(Base):
    """Incident attachment/artifact"""
    __tablename__ = "incident_artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_hash = Column(String(64))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    incident = relationship("Incident", back_populates="artifacts")

# ============= OBSERVABLES =============

class IncidentObservable(Base):
    """Observable (file, process, IP, domain, hash, etc.)"""
    __tablename__ = "incident_observables"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    observable_type = Column(String(50), nullable=False)
    observable_value = Column(String(500), nullable=False)
    observable_hash = Column(String(64))
    file_name = Column(String(500))
    file_path = Column(String(1000))
    severity = Column(String(50))
    detection_id = Column(String(255))

    # Enrichment fields
    enrichment_status = Column(String(20), default="pending")  # pending/enriched/failed
    malicious_score = Column(Integer)  # 0-100
    reputation = Column(String(20))  # malicious/suspicious/clean/unknown
    enrichment_data = Column(JSON)
    enriched_at = Column(DateTime(timezone=True))

    # Timestamps
    observed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    incident = relationship("Incident", back_populates="observables")


# ============= FINDINGS =============

class IncidentFinding(Base):
    """Incident finding"""
    __tablename__ = "incident_findings"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    finding_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(50))
    confidence = Column(Float)
    mitre_technique = Column(String(100))
    evidence_ids = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    incident = relationship("Incident", back_populates="findings")


# ============= RELATIONSHIPS =============

class IncidentRelationship(Base):
    """Relationship between entities"""
    __tablename__ = "incident_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    related_entity_type = Column(String(50), nullable=False)
    related_entity_id = Column(String(255), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    description = Column(Text)
    confidence = Column(Float)
    
    # Relationships
    incident = relationship("Incident", back_populates="relationships")


# ============= APPROVALS =============

class ApprovalRequest(Base):
    """Approval request for actions"""
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    integration = Column(String(100))
    action = Column(String(100), nullable=False)
    parameters = Column(JSON)
    risk_level = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    submitted_by = Column(Integer, ForeignKey("users.id"))
    submitted_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    
    # Relationships
    incident = relationship("Incident", back_populates="approvals")
    user = relationship("User", foreign_keys=[submitted_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])


# ============= INTEGRATIONS =============

class Integration(Base):
    """Integration type"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(String(500))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    instances = relationship("IntegrationInstance", back_populates="integration", lazy="dynamic")


class IntegrationInstance(Base):
    """Integration instance"""
    __tablename__ = "integration_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    instance_name = Column(String(100), nullable=False)
    credentials = Column(JSON)
    configuration = Column(JSON)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    integration = relationship("Integration", back_populates="instances")


# ============= AUTOMATION =============

class AutomationScript(Base):
    """Automation script"""
    __tablename__ = "automation_scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    script_content = Column(Text, nullable=False)
    risk_level = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True)
    timeout_seconds = Column(Integer, default=300)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AutomationRun(Base):
    """Automation run"""
    __tablename__ = "automation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("automation_scripts.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    status = Column(String(50), default="pending")
    parameters = Column(JSON)
    output = Column(JSON)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    script = relationship("AutomationScript")
    incident = relationship("Incident")
    user = relationship("User", foreign_keys=[created_by])


# ============= PLAYBOOKS =============

class Playbook(Base):
    """Playbook definition"""
    __tablename__ = "playbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0.0")
    playbook_content = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PlaybookRun(Base):
    """Playbook run"""
    __tablename__ = "playbook_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    output = Column(JSON)
    error = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    playbook = relationship("Playbook", lazy="selectin")
    incident = relationship("Incident", lazy="selectin")
    user = relationship("User", foreign_keys=[created_by], lazy="selectin")


# ============= AUDIT LOG =============

class AuditEvent(Base):
    """Audit log entry"""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    actor_id = Column(Integer, ForeignKey("users.id"))
    actor_type = Column(String(50), default="user")
    action = Column(String(255), nullable=False)
    risk_level = Column(String(50))
    category = Column(String(100))
    success = Column(Boolean, default=True)
    meta = Column("metadata", JSON, nullable=True)  # Using 'meta' as Python name to avoid 'metadata' reserved word
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============= AI MODELS =============

class LLMTool(Base):
    """Registered AI tool"""
    __tablename__ = "llm_tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    path = Column(String(500))
    description = Column(Text)
    input_schema = Column(JSON, default={})
    output_schema = Column(JSON, default={})
    risk_level = Column(String(50), nullable=False)
    requires_approval = Column(Boolean, default=False)
    ai_callable = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    meta = Column("llm_metadata", JSON, default={})  # Using 'meta' to avoid 'metadata' reserved word
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[created_by])


class LLMSession(Base):
    """LLM investigation session"""
    __tablename__ = "llm_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    session_id = Column(String(100), nullable=False)
    status = Column(String(50), default="in_progress")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    incident = relationship("Incident")
    user = relationship("User", foreign_keys=[created_by])


class LLMMessage(Base):
    """LLM message in session"""
    __tablename__ = "llm_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("llm_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("LLMSession")


class LLMToolCall(Base):
    """LLM tool call in session"""
    __tablename__ = "llm_tool_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("llm_sessions.id"), nullable=False)
    tool_name = Column(String(255), nullable=False)
    arguments = Column(JSON, default={})
    status = Column(String(50), nullable=False)
    output = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("LLMSession")


class LLMFinding(Base):
    """LLM investigation finding"""
    __tablename__ = "llm_findings"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("llm_sessions.id"), nullable=False)
    evidence_ids = Column(JSON, default=[])
    finding_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(String(50))
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("LLMSession")


class AnalysisQuestion(Base):
    """An analyst's AI question and its answer (persisted for history)."""
    __tablename__ = "analysis_questions"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # "incident" | "alert"
    entity_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    model = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LLMProfile(Base):
    """A configurable LLM provider profile (e.g. local Qwen, fallback model)."""
    __tablename__ = "llm_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    base_url = Column(String(500), nullable=False)
    model = Column(String(100), nullable=False)
    api_key = Column(String(500))  # stored locally in DB; never returned in full
    context_window = Column(Integer, default=40000)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



