"""
SOAR Platform - Incident Models
Defines incident and related entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class IncidentStatus(str, Enum):
    """Incident lifecycle states."""
    NEW = "new"
    INVESTIGATING = "investigating"
    Triage = "triage"
    ANALYSIS = "analysis"
    CONTAINMENT = "containment"
    RESOLUTION = "resolution"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentSourceType(str, Enum):
    """Sources of incident detection."""
    SIEM = "siem"
    EDR = "edr"
    FIREWALL = "firewall"
    NETWORK = "network"
    MALWARE_DETECTION = "malware_detection"
    USER_REPORT = "user_report"
    AUTOMATION = "automation"
    EXTERNAL = "external"


class IncidentRelationshipType(str, Enum):
    """Types of relationships between entities."""
    CAUSATION = "causation"
    CONTRIBUTOR = "contributor"
    PART_OF = "part_of"
    RELATES_TO = "relates_to"
    RELATED_TO = "related_to"
    SUB_OF = "sub_of"
    SOURCE_OF = "source_of"


class ObservableType(str, Enum):
    """Types of network observables."""
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


class IncidentRelationship(Base):
    """Relationships between entities (incidents, hosts, users, etc.)."""
    __tablename__ = "incident_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Incident being referenced
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    # Related entity type
    entity_type = Column(String(50), nullable=False)  # e.g., "host", "user", "process"
    
    # Related entity ID (polymorphic)
    entity_id = Column(Integer, nullable=False)
    
    # Relationship type
    relationship_type = Column(String(50), nullable=False, default=IncidentRelationshipType.RELATED_TO)
    
    # Relationship direction
    direction = Column(String(20), nullable=True)  # "incident->entity" or "entity->incident"
    
    # Description
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="relationships")


class Incident(Base):
    """Main incident entity."""
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Incident number (e.g., "INC-2026-000184")
    incident_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    source_type = Column(String(50), nullable=True)
    detection_id = Column(String(200), nullable=True)
    
    # Classification
    severity = Column(SQLEnum(IncidentSeverity), nullable=True)
    status = Column(SQLEnum(IncidentStatus), nullable=True, default=IncidentStatus.NEW)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to = Column(String(100), nullable=True)
    
    # Tags
    tags = Column(String(500), nullable=True)
    
    # Metadata JSON
    meta = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Owner relationship
    owner = relationship("User", foreign_keys=[owner_id], back_populates="incidents")
    
    # Relationships
    relationships = relationship("IncidentRelationship", back_populates="incident")
    
    # Events timeline
    events = relationship("IncidentEvent", back_populates="incident")
    
    # Comments
    comments = relationship("IncidentComment", back_populates="incident")
    
    # Observables
    observables = relationship("Observable", back_populates="incident")
    
    # Evidence (many-to-many with junction)
    evidences = relationship("Evidence", secondary="incident_evidence", back_populates="incident")
    
    # Findings
    findings = relationship("Finding", back_populates="incident")
    
    # Audit events
    audit_events = relationship("AuditEvent", back_populates="incident")
    
    # AI sessions
    ai_sessions = relationship("LLMSession", back_populates="incident")
    
    def __repr__(self):
        return f"<Incident(id={self.id}, number={self.incident_number}, title={self.title[:50]}..., severity={self.severity}, status={self.status})>"


class IncidentEvent(Base):
    """Append-only incident timeline events."""
    __tablename__ = "incident_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    # Event type
    event_type = Column(String(100), nullable=False)  # e.g., "created", "evidence_extracted", "playbook_executed"
    
    # Event title/description
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata JSON
    meta = Column(Text, nullable=True)
    
    # Risk level for the action
    risk_level = Column(String(20), nullable=True)  # READ, ENRICH, MODIFY, CONTAIN, EXECUTE, DESTRUCTIVE
    
    # Actor (user or AI agent)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_type = Column(String(50), nullable=True)  # "user" or "ai_agent"
    
    # Approval info
    approval_id = Column(Integer, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)
    required_approval = Column(Boolean, default=False)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    incident = relationship("Incident", back_populates="events")
    actor = relationship("User", foreign_keys=[actor_id])
    approval = relationship("ApprovalRequest", foreign_keys=[approval_id])
    
    def __repr__(self):
        return f"<IncidentEvent(id={self.id}, incident_id={self.incident_id}, type={self.event_type}, title={self.title})>"


class IncidentComment(Base):
    """Incident comments."""
    __tablename__ = "incident_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Comment type
    comment_type = Column(String(50), nullable=True)  # "analyst", "ai_assistant", "system"
    
    # References
    evidence_ids = Column(String(500), nullable=True)  # JSON array of evidence IDs
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    incident = relationship("Incident", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<IncidentComment(id={self.id}, incident_id={self.incident_id})>"


class Observable(Base):
    """Extracted observables from incident evidence."""
    __tablename__ = "observables"
    
    id = Column(Integer, primary_key=True, index=True)
    
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    observable_type = Column(SQLEnum(ObservableType), nullable=False)
    value = Column(String(500), nullable=False)
    
    # Classification
    threat_level = Column(String(20), nullable=True)  # "malicious", "suspicious", "benign", "unknown"
    
    # Confidence
    confidence = Column(Integer, default=100)
    confidence_source = Column(String(100), nullable=True)
    
    # Metadata JSON
    meta = Column(Text, nullable=True)
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="observables")
    
    def __repr__(self):
        return f"<Observable(id={self.id}, type={self.observable_type.value}, value={self.value})>"


# Many-to-many tables

class IncidentEvidence(Base):
    """Junction table for incident-evidence relationship."""
    __tablename__ = "incident_evidence"
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    evidence_id = Column(Integer, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        {'unique': True, 'extend_existing': True},
    )


class IncidentObservable(Base):
    """Junction table for incident-observable relationship."""
    __tablename__ = "incident_observables"
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    observable_id = Column(Integer, ForeignKey("observables.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        {'unique': True, 'extend_existing': True},
    )
