"""
SOAR Platform - Audit Logger
Immutable audit logging for all actions.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import json


class AuditLogger:
    """
    Immutable audit logger for SOAR platform.
    
    All important actions must generate audit events.
    """
    
    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        self._event_counter = 0
    
    def log(
        self,
        actor_id: Optional[int] = None,
        actor_type: Optional[str] = None,
        action: str = "",
        action_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        category: Optional[str] = None,
        details: Optional[str] = None,
        incident_id: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log an audit event.
        
        All audit events are immutable and append-only.
        """
        self._event_counter += 1
        
        event = {
            "id": self._event_counter,
            "incident_id": incident_id,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "action": action,
            "action_type": action_type,
            "risk_level": risk_level,
            "category": category,
            "details": details,
            "success": success,
            "error_message": error_message,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._events.append(event)
        return event
    
    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get audit event by ID."""
        for event in self._events:
            if event["id"] == event_id:
                return event
        return None
    
    def get_incident_events(self, incident_id: int) -> List[Dict[str, Any]]:
        """Get all audit events for an incident."""
        return [
            event for event in self._events
            if event.get("incident_id") == incident_id
        ]
    
    def get_actor_events(self, actor_id: int) -> List[Dict[str, Any]]:
        """Get all audit events for an actor."""
        return [
            event for event in self._events
            if event.get("actor_id") == actor_id
        ]
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit events."""
        return self._events[-limit:]
    
    def get_events_by_action(
        self,
        action: str,
        success: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get events by action."""
        events = [
            event for event in self._events
            if event.get("action") == action
        ]
        
        if success is not None:
            events = [e for e in events if e.get("success") == success]
        
        return events
    
    def clear(self):
        """Clear all audit events (for testing only)."""
        self._events.clear()
        self._event_counter = 0
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all audit events."""
        return self._events.copy()
