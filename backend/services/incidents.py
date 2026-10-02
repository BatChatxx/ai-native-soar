"""
SOAR Platform - Incident Service
Core incident management service.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
import random
import string
from sqlalchemy.orm import Session
from models.incidents import Incident, IncidentEvent, IncidentComment, Observable, IncidentRelationship
from models.audit import AuditEvent


class IncidentService:
    """Incident service for creating and managing incidents."""
    
    def __init__(self):
        self._event_counter = 0
    
    async def initialize(self, db_session: Session):
        """Initialize incident service."""
        pass
    
    def generate_incident_number(self, prefix: str = "INC") -> str:
        """Generate incident number. Format: INC-YYYY-NNNNNN"""
        current_year = datetime.utcnow().year
        number = self._event_counter
        self._event_counter += 1
        return f"{prefix}-{current_year:04d}-{number:06d}"
    
    def create_incident(
        self,
        db_session: Session,
        title: str,
        description: Optional[str] = None,
        severity: Optional[str] = None,
        source_type: Optional[str] = None,
        detection_id: Optional[str] = None,
        tags: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        owner_id: Optional[int] = None,
        assigned_to: Optional[str] = None,
    ) -> Incident:
        """Create a new incident."""
        incident = Incident(
            incident_number=self.generate_incident_number(),
            title=title,
            description=description or "",
            severity=severity,
            source_type=source_type,
            detection_id=detection_id,
            tags=tags,
            metadata=str(metadata) if metadata else None,
            owner_id=owner_id,
            assigned_to=assigned_to,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status="new",
        )
        
        db_session.add(incident)
        db_session.flush()
        
        audit_event = AuditEvent(
            actor_id=owner_id,
            actor_type="analyst",
            action="create_incident",
            action_type="incident",
            risk_level="READ",
            category="incident_management",
            details=f"Created incident {incident.incident_number}: {title}",
            success=True,
            incident_id=incident.id,
        )
        
        db_session.add(audit_event)
        db_session.commit()
        
        return incident
    
    def add_evidence(
        self,
        db_session: Session,
        incident_id: int,
        content: str,
        content_hash: Optional[str] = None,
        evidence_type: Optional[str] = None,
        format: str = "json",
        classification: str = "untrusted",
        source: Optional[str] = None,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        extracted_at: Optional[datetime] = None,
        ai_findings: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Observable:
        """Add evidence/observable to incident."""
        observable = Observable(
            incident_id=incident_id,
            content=content,
            content_hash=content_hash,
            evidence_type=evidence_type,
            format=format,
            classification=classification,
            source=source,
            source_type=source_type,
            source_id=source_id,
            extracted_at=extracted_at or datetime.utcnow(),
            ai_findings=ai_findings,
            metadata=str(metadata) if metadata else None,
        )
        
        db_session.add(observable)
        db_session.commit()
        
        return observable
    
    def add_event(
        self,
        db_session: Session,
        incident_id: int,
        event_type: str,
        title: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        risk_level: Optional[str] = None,
        actor_id: Optional[int] = None,
        actor_type: Optional[str] = None,
    ) -> IncidentEvent:
        """Add event to incident."""
        event = IncidentEvent(
            incident_id=incident_id,
            event_type=event_type,
            title=title,
            description=description or "",
            metadata=str(metadata) if metadata else None,
            risk_level=risk_level,
            actor_id=actor_id,
            actor_type=actor_type,
        )
        
        db_session.add(event)
        db_session.commit()
        
        return event
    
    def add_comment(
        self,
        db_session: Session,
        incident_id: int,
        content: str,
        comment_type: str = "analyst",
        evidence_ids: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> IncidentComment:
        """Add comment to incident."""
        comment = IncidentComment(
            incident_id=incident_id,
            content=content,
            comment_type=comment_type,
            evidence_ids=evidence_ids,
            created_at=datetime.utcnow(),
            user_id=user_id,
        )
        
        db_session.add(comment)
        db_session.commit()
        
        return comment
    
    def add_relationship(
        self,
        db_session: Session,
        incident_id: int,
        entity_type: str,
        entity_id: int,
        relationship_type: str,
        direction: Optional[str] = None,
        description: Optional[str] = None,
    ) -> IncidentRelationship:
        """Add relationship between incident and entity."""
        relationship = IncidentRelationship(
            incident_id=incident_id,
            entity_type=entity_type,
            entity_id=entity_id,
            relationship_type=relationship_type,
            direction=direction,
            description=description or "",
            created_at=datetime.utcnow(),
        )
        
        db_session.add(relationship)
        db_session.commit()
        
        return relationship
    
    def get_incident_timeline(self, incident: Incident) -> List[Dict[str, Any]]:
        """Get incident timeline."""
        events = []
        
        events.append({
            "timestamp": incident.created_at,
            "event": "Incident created",
            "title": incident.title,
            "incident_number": incident.incident_number,
        })
        
        for event in incident.events:
            events.append({
                "timestamp": event.timestamp,
                "event": event.event_type,
                "title": event.title,
                "description": event.description,
                "risk_level": event.risk_level,
            })
        
        events.sort(key=lambda x: x["timestamp"])
        return events
    
    def update_status(
        self,
        db_session: Session,
        incident_id: int,
        status: str,
        assigned_to: Optional[str] = None,
    ):
        """Update incident status."""
        incident = db_session.query(Incident).get(incident_id)
        
        if incident:
            incident.status = status
            incident.updated_at = datetime.utcnow()
            
            audit_event = AuditEvent(
                actor_id=incident.owner_id,
                actor_type="analyst",
                action="update_incident_status",
                action_type="incident",
                risk_level="MODIFY_LOW",
                category="incident_management",
                details=f"Updated incident {incident.incident_number} status to {status}",
                success=True,
                incident_id=incident_id,
            )
            
            db_session.add(audit_event)
            db_session.commit()
