"""
SOAR Platform - Evidence Models
Defines evidence and finding entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class EvidenceType(str, Enum):
    """Types of evidence."""
    EMAIL = "email"
    WEBPAGE = "webpage"
    LOG = "log"
    PROCESS_COMMAND = "process_command"
    POWERSHELL = "powershell"
    EDR = "edr"
    SIEM = "siem"
    TICKET_COMMENT = "ticket_comment"
    FILE = "file"
    MALWARE_OUTPUT = "malware_output"
    CUSTOM = "custom"


class EvidenceFormat(str, Enum):
    """Evidence data formats."""
    TEXT = "text"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"


class EvidenceClassification(str, Enum):
    """Evidence classification."""
    UNTRUSTED = "untrusted"
    SENSITIVE = "sensitive"
    PUBLIC = "public"


class FindingType(str, Enum):
    """Finding types."""
    FACT = "fact"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    RECOMMENDATION = "recommendation"
    ACTION = "action"


class FindingConfidence(str, Enum):
    """Finding confidence levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Evidence(Base):
    """Evidence record with stable ID."""
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Stable evidence ID (EVID-XXXXX)
    evidence_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # Content - stored securely, not in plain text for sensitive types
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)  # SHA256 of content
    
    # Metadata
    evidence_type = Column(SQLEnum(EvidenceType), nullable=True)
    format = Column(SQLEnum(EvidenceFormat), default=EvidenceFormat.TEXT)
    classification = Column(SQLEnum(EvidenceClassification), default=EvidenceClassification.UNTRUSTED)
    
    # Source
    source = Column(String(200), nullable=True)
    source_type = Column(String(50), nullable=True)
    source_id = Column(String(200), nullable=True)
    
    # Processing
    extracted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI findings (JSON array)
    ai_findings = Column(Text, nullable=True)
    
    # Metadata JSON
    meta = Column(Text, nullable=True)
    
    # Relationships
    incident_evidence = relationship("IncidentEvidence", back_populates="evidence")
    evidence_links = relationship("EvidenceLink", back_populates="source_evidence")
    
    def __repr__(self):
        return f"<Evidence(id={self.id}, evidence_id={self.evidence_id}, type={self.evidence_type.value})>"


class Finding(Base):
    """AI investigation finding."""
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Stable finding ID
    finding_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # Incident reference
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    # Finding type
    finding_type = Column(SQLEnum(FindingType), nullable=False)
    
    # Content
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    
    # Classification
    confidence = Column(SQLEnum(FindingConfidence), nullable=True)
    
    # Evidence references
    evidence_ids = Column(String(500), nullable=True)  # JSON array
    
    # Relationships
    incident = relationship("Incident", back_populates="findings")
    
    def __repr__(self):
        return f"<Finding(id={self.id}, finding_id={self.finding_id}, type={self.finding_type.value})>"


class EvidenceLink(Base):
    """Links between evidence pieces (relationship mapping)."""
    __tablename__ = "evidence_links"
    
    id = Column(Integer, primary_key=True, index=True)
    
    source_evidence_id = Column(Integer, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    target_evidence_id = Column(Integer, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    
    # Link type
    link_type = Column(String(100), nullable=False)  # "derived_from", "references", "supports", etc.
    
    # Description
    description = Column(Text, nullable=True)
    
    # Confidence
    confidence = Column(Integer, default=100)
    
    # Metadata
    meta = Column(Text, nullable=True)
    
    # Relationships
    source_evidence = relationship("Evidence", foreign_keys=[source_evidence_id], back_populates="evidence_links")
    target_evidence = relationship("Evidence", relationship="evidence_links_target", back_populates="link_sources")
    
    def __repr__(self):
        return f"<EvidenceLink(id={self.id}, source={self.source_evidence_id} -> target={self.target_evidence_id}, type={self.link_type})>"


Evidence.evidence_links_target = relationship(
    "EvidenceLink",
    back_populates="source_evidence",
    primaryjoin="and_(Evidence.id==EvidenceLink.target_evidence_id)"
)
