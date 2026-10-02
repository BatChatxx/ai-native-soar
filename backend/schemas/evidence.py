"""
SOAR Platform - Evidence Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
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


class EvidenceClassification(str, Enum):
    UNTRUSTED = "untrusted"
    SENSITIVE = "sensitive"
    PUBLIC = "public"


class FindingType(str, Enum):
    FACT = "fact"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    RECOMMENDATION = "recommendation"
    ACTION = "action"


class FindingConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceResponse(BaseModel):
    """Evidence response model."""
    id: int
    evidence_id: str
    content: Optional[str]
    content_hash: Optional[str]
    evidence_type: Optional[EvidenceType]
    format: str
    classification: EvidenceClassification
    source: Optional[str]
    source_type: Optional[str]
    source_id: Optional[str]
    extracted_at: datetime
    updated_at: datetime
    ai_findings: Optional[str]
    metadata: Optional[str]
    
    class Config:
        from_attributes = True


class FindingResponse(BaseModel):
    """Finding response model."""
    id: int
    finding_id: str
    incident_id: int
    finding_type: FindingType
    title: str
    content: str
    confidence: Optional[FindingConfidence]
    evidence_ids: Optional[str]
    
    class Config:
        from_attributes = True


class EvidenceLinkResponse(BaseModel):
    """Evidence link response model."""
    id: int
    source_evidence_id: int
    target_evidence_id: int
    link_type: str
    description: Optional[str]
    confidence: int
    metadata: Optional[str]
    
    class Config:
        from_attributes = True
