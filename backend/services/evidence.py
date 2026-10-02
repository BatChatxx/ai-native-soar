"""
SOAR Platform - Evidence Service
Handles evidence and observables management.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from models.evidence import Evidence, Finding, EvidenceLink


class EvidenceService:
    """Evidence service for managing evidence and findings."""
    
    async def initialize(self, db_session: Session):
        """Initialize evidence service."""
        pass
    
    def link_evidence(
        self,
        db_session: Session,
        source_evidence_id: int,
        target_evidence_id: int,
        link_type: str,
        description: Optional[str] = None,
        confidence: int = 50,
        metadata: Optional[dict] = None,
    ) -> EvidenceLink:
        """
        Link two pieces of evidence together.
        
        AI findings should reference evidence IDs whenever possible.
        """
        link = EvidenceLink(
            source_evidence_id=source_evidence_id,
            target_evidence_id=target_evidence_id,
            link_type=link_type,
            description=description or "",
            confidence=confidence,
            metadata=str(metadata) if metadata else None,
        )
        
        db_session.add(link)
        db_session.commit()
        
        return link
    
    def generate_evidence_id(self) -> str:
        """Generate a stable evidence ID."""
        import random
        number = random.randint(10000, 99999)
        return f"EVID-{number:05d}"
    
    def add_finding(
        self,
        db_session: Session,
        incident_id: int,
        finding_type: str,
        title: str,
        content: str,
        confidence: Optional[int] = None,
        evidence_ids: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Finding:
        """
        Add a finding to an incident.
        
        AI findings should reference evidence IDs whenever possible.
        Prefer:
        'powershell.exe was launched by WINWORD.EXE according to EVID-00192.'
        Avoid unsupported conclusions like: 'The computer is definitely compromised.'
        """
        finding = Finding(
            incident_id=incident_id,
            finding_type=finding_type,
            title=title,
            content=content,
            confidence=confidence or 0,
            evidence_ids=evidence_ids,
            metadata=str(metadata) if metadata else None,
            created_at=datetime.utcnow(),
        )
        
        db_session.add(finding)
        db_session.commit()
        
        return finding
