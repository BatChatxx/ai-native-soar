"""
Incident Service

Handles incident CRUD operations and timeline management.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from models.database import get_db
from models.models import (
    Incident,
    IncidentEvent,
    IncidentComment,
    IncidentTag,
    IncidentObservable,
    IncidentFinding,
    IncidentArtifact,
    IncidentRelationship,
    IncidentHost,
    IncidentUser,
    IncidentStatusEnum,
    IncidentSeverityEnum,
    EvidenceClassification,
)


class IncidentService:
    """
    Incident service for CRUD operations.
    
    Maintains append-only incident timeline.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_incident(
        self,
        title: str,
        description: Optional[str] = None,
        severity: IncidentSeverityEnum = IncidentSeverityEnum.MEDIUM,
        source_type: Optional[str] = None,
        source_integration: Optional[str] = None,
        detection_id: Optional[str] = None,
        detection_timestamp: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Incident:
        """
        Create a new incident.
        
        Args:
            title: Incident title
            description: Incident description
            severity: Incident severity
            source_type: Detection source type (e.g., "SIEM")
            source_integration: Integration name
            detection_id: Original detection ID
            detection_timestamp: Detection timestamp
            tags: Initial tags
            
        Returns:
            Created Incident
        """
        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            source_type=source_type,
            source_integration=source_integration,
            detection_id=detection_id,
            detection_timestamp=detection_timestamp,
            tags=tags or [],
        )
        
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        
        # Add initial event
        self._add_event(
            incident,
            event_type="incident_created",
            description=f"Incident {incident.number} created: {title}"
        )
        
        return incident
    
    def get_incident(self, incident_id: int) -> Incident:
        """Get incident by ID."""
        return self.db.query(Incident).filter(
            Incident.id == incident_id
        ).first()
    
    def get_incident_by_number(self, incident_number: str) -> Optional[Incident]:
        """Get incident by number (e.g., "INC-2026-000184")."""
        return self.db.query(Incident).filter(
            Incident.number == incident_number
        ).first()
    
    def get_incidents(
        self,
        status: Optional[IncidentStatusEnum] = None,
        severity: Optional[IncidentSeverityEnum] = None,
        owner_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[Incident]:
        """Get incidents with optional filters."""
        query = self.db.query(Incident)
        
        if status:
            query = query.filter(Incident.status == status)
        if severity:
            query = query.filter(Incident.severity == severity)
        if owner_id:
            query = query.filter(Incident.owner_id == owner_id)
        
        offset = (page - 1) * page_size
        return query.order_by(Incident.created_at.desc()).offset(offset).limit(page_size).all()
    
    def update_incident(
        self,
        incident_id: int,
        **kwargs,
    ) -> Incident:
        """
        Update incident fields.
        
        Args:
            incident_id: Incident ID
            **kwargs: Fields to update
            
        Returns:
            Updated Incident
        """
        incident = self.get_incident(incident_id)
        
        if not incident:
            raise ValueError(f"Incident not found: {incident_id}")
        
        for key, value in kwargs.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
        
        self.db.commit()
        self.db.refresh(incident)
        
        return incident
    
    def close_incident(
        self,
        incident_id: int,
        closed_reason: Optional[str] = None,
    ) -> Incident:
        """
        Close an incident.
        
        Args:
            incident_id: Incident ID
            closed_reason: Reason for closing
            
        Returns:
            Closed Incident
        """
        incident = self.get_incident(incident_id)
        
        if not incident:
            raise ValueError(f"Incident not found: {incident_id}")
        
        incident.status = IncidentStatusEnum.CLOSED
        incident.closed_reason = closed_reason
        incident.closed_at = func.now()
        
        self.db.commit()
        self.db.refresh(incident)
        
        # Add closure event
        self._add_event(
            incident,
            event_type="incident_closed",
            description=f"Incident closed: {closed_reason or 'No reason provided'}"
        )
        
        return incident
    
    def add_event(
        self,
        incident_id: int,
        event_type: str,
        description: str,
    ) -> IncidentEvent:
        """
        Add event to incident timeline.
        
        Timeline events are append-only.
        
        Args:
            incident_id: Incident ID
            event_type: Event type (e.g., "observable_extracted")
            description: Event description
            
        Returns:
            Created IncidentEvent
        """
        incident = self.get_incident(incident_id)
        
        event = IncidentEvent(
            incident_id=incident_id,
            event_type=event_type,
            description=description,
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def _add_event(
        self,
        incident: Incident,
        event_type: str,
        description: str,
    ) -> IncidentEvent:
        """Add event to incident (helper method)."""
        event = IncidentEvent(
            incident_id=incident.id,
            event_type=event_type,
            description=description,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def add_comment(
        self,
        incident_id: int,
        user_id: Optional[int],
        content: str,
    ) -> IncidentComment:
        """
        Add comment to incident.
        
        Args:
            incident_id: Incident ID
            user_id: User ID (optional for anonymous)
            content: Comment content
            
        Returns:
            Created IncidentComment
        """
        incident = self.get_incident(incident_id)
        
        comment = IncidentComment(
            incident_id=incident_id,
            user_id=user_id,
            content=content,
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        
        return comment
    
    def add_observable(
        self,
        incident_id: int,
        evidence_id: Optional[str] = None,
        observable_type: str = "ip",
        content: str = "",
        source: Optional[str] = None,
        timestamp: Optional[str] = None,
        classification: EvidenceClassification = EvidenceClassification.UNTRUSTED,
    ) -> IncidentObservable:
        """
        Add observable (evidence) to incident.
        
        Evidence IDs are stable and used in AI findings.
        
        Args:
            incident_id: Incident ID
            evidence_id: Stable evidence ID (e.g., "EVID-00192")
            observable_type: Observable type (e.g., "ip", "domain")
            content: Observable content (e.g., "192.168.1.1")
            source: Source system (e.g., "EDR")
            timestamp: Observable timestamp
            classification: Evidence classification
            
        Returns:
            Created IncidentObservable
        """
        incident = self.get_incident(incident_id)
        
        observable = IncidentObservable(
            incident_id=incident_id,
            evidence_id=evidence_id,
            observable_type=observable_type,
            content=content,
            source=source,
            timestamp=timestamp,
            classification=classification,
        )
        
        self.db.add(observable)
        self.db.commit()
        self.db.refresh(observable)
        
        # Add extraction event
        self._add_event(
            incident,
            event_type="observable_extracted",
            description=f"Observable added: {observable_type}={content}"
        )
        
        return observable
    
    def add_finding(
        self,
        incident_id: int,
        title: str,
        description: Optional[str] = None,
        severity: Optional[IncidentSeverityEnum] = None,
        confidence: Optional[str] = None,
        category: Optional[str] = None,
        evidence_refs: Optional[List[str]] = None,
    ) -> IncidentFinding:
        """
        Add finding to incident.
        
        Args:
            incident_id: Incident ID
            title: Finding title
            description: Finding description
            severity: Finding severity
            confidence: Finding confidence
            category: Finding category
            evidence_refs: List of evidence IDs
            
        Returns:
            Created IncidentFinding
        """
        incident = self.get_incident(incident_id)
        
        finding = IncidentFinding(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            confidence=confidence,
            category=category,
            evidence_refs=evidence_refs,
        )
        
        self.db.add(finding)
        self.db.commit()
        self.db.refresh(finding)
        
        return finding
    
    def add_relationship(
        self,
        incident_id: int,
        entity_type: str,
        entity_id: str,
        relationship_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> IncidentRelationship:
        """
        Add relationship between incident and entity.
        
        Args:
            incident_id: Incident ID
            entity_type: Entity type (e.g., "host", "ip")
            entity_id: Entity ID (e.g., "HOST-00123")
            relationship_type: Relationship type (e.g., "affected")
            description: Relationship description
            
        Returns:
            Created IncidentRelationship
        """
        incident = self.get_incident(incident_id)
        
        relationship = IncidentRelationship(
            incident_id=incident_id,
            entity_type=entity_type,
            entity_id=entity_id,
            relationship_type=relationship_type,
            description=description,
        )
        
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        
        return relationship
    
    def get_timeline(
        self,
        incident_id: int,
        limit: int = 100,
    ) -> List[IncidentEvent]:
        """
        Get incident timeline events.
        
        Events are returned in chronological order.
        
        Args:
            incident_id: Incident ID
            limit: Maximum number of events
            
        Returns:
            List of IncidentEvents
        """
        incident = self.get_incident(incident_id)
        return self.db.query(IncidentEvent).filter(
            IncidentEvent.incident_id == incident_id,
        ).order_by(IncidentEvent.timestamp.asc()).limit(limit).all()
    
    def get_evidence(
        self,
        incident_id: int,
    ) -> List[IncidentObservable]:
        """Get all evidence for an incident."""
        incident = self.get_incident(incident_id)
        return self.db.query(IncidentObservable).filter(
            IncidentObservable.incident_id == incident_id,
        ).all()
    
    def get_findings(
        self,
        incident_id: int,
    ) -> List[IncidentFinding]:
        """Get all findings for an incident."""
        incident = self.get_incident(incident_id)
        return self.db.query(IncidentFinding).filter(
            IncidentFinding.incident_id == incident_id,
        ).all()
    
    def get_hosts(
        self,
        incident_id: int,
    ) -> List[IncidentHost]:
        """Get all hosts for an incident."""
        incident = self.get_incident(incident_id)
        return self.db.query(IncidentHost).filter(
            IncidentHost.incident_id == incident_id,
        ).all()
    
    def get_relationships(
        self,
        incident_id: int,
    ) -> List[IncidentRelationship]:
        """Get all relationships for an incident."""
        incident = self.get_incident(incident_id)
        return self.db.query(IncidentRelationship).filter(
            IncidentRelationship.incident_id == incident_id,
        ).all()
