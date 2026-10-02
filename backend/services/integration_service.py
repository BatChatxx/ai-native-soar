"""
Integration Service

Handles integration action execution with proper risk classification.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

from models.database import get_db
from models.models import (
    IntegrationConfig,
    IntegrationInstance,
    IntegrationAction,
    IntegrationExecution,
    Incident,
    IncidentEvent,
    AuditEvent,
    IntegrationRiskLevel,
)


class IntegrationService:
    """
    Integration service for executing security tool actions.
    
    Security boundaries:
    - All actions go through registered integration definitions
    - Risk classification enforced at service level
    - High-risk actions require approval
    - All actions logged to audit_events
    - Never store credentials in responses
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_action(
        self,
        incident_id: Optional[int],
        integration_config_id: int,
        action_name: str,
        inputs: Dict[str, Any],
        actor_username: str,
    ) -> Dict[str, Any]:
        """
        Execute an integration action.
        
        Args:
            incident_id: Optional incident ID for context
            integration_config_id: Integration configuration ID
            action_name: Action name (e.g., "virustotal.lookup_ip")
            inputs: Input parameters for the action
            actor_username: Username of the actor
            
        Returns:
            Dict with execution result
            
        Raises:
            ValueError: If action is not defined or requires approval
            PermissionError: If risk level is too high
        """
        # Get integration configuration
        config = self.db.query(IntegrationConfig).filter(
            IntegrationConfig.id == integration_config_id
        ).first()
        
        if not config:
            raise ValueError(f"Integration config not found: {integration_config_id}")
        
        if not config.enabled:
            raise ValueError(f"Integration disabled: {config.display_name}")
        
        # Find matching action
        action = self._find_action(config.integration_name, action_name)
        
        if not action:
            raise ValueError(
                f"Action not found in {config.display_name}: {action_name}"
            )
        
        # Check if action requires approval
        if action.risk_level in (
            IntegrationRiskLevel.MODIFY,
            IntegrationRiskLevel.CONTAIN,
            IntegrationRiskLevel.EXECUTE,
            IntegrationRiskLevel.DESTRUCTIVE,
        ):
            if action.requires_approval:
                raise PermissionError(
                    f"Action requires approval: {action_name} "
                    f"(Risk: {action.risk_level})"
                )
        
        # Validate inputs against schema
        if action.input_schema:
            self._validate_inputs(action.input_schema, inputs)
        
        # Execute action (placeholder - implement real execution)
        try:
            result = self._execute_action_internal(
                config,
                action,
                inputs,
                incident_id,
                actor_username,
            )
            
            # Log execution
            self._log_execution(
                config,
                action,
                inputs,
                result,
                actor_username,
                incident_id,
            )
            
            # Create audit event
            self._create_audit_event(
                action,
                inputs,
                result,
                actor_username,
                incident_id,
            )
            
            return result
            
        except Exception as e:
            # Log failed execution
            self._log_execution(
                config,
                action,
                inputs,
                None,
                actor_username,
                incident_id,
                error=str(e),
            )
            
            raise
    
    def _find_action(
        self,
        integration_name: str,
        action_name: str,
    ) -> Optional[IntegrationAction]:
        """Find action by integration name and action name."""
        return self.db.query(IntegrationAction).filter(
            IntegrationAction.integration_config_id.in_(
                self.db.query(IntegrationConfig.id).filter(
                    IntegrationConfig.integration_name == integration_name,
                ).values flat=True
            ),
            IntegrationAction.action_name == action_name,
            IntegrationAction.enabled == True,
        ).first()
    
    def _validate_inputs(
        self,
        schema: Dict[str, Any],
        inputs: Dict[str, Any],
    ) -> None:
        """Validate inputs against JSON schema."""
        # Placeholder - implement proper JSON Schema validation
        if schema and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in inputs:
                    # Validate type
                    expected_type = prop_schema.get("type")
                    actual_type = type(inputs[prop_name]).__name__
                    
                    if expected_type == "string" and actual_type != "str":
                        raise ValueError(
                            f"Expected string for {prop_name}, got {actual_type}"
                        )
    
    def _execute_action_internal(
        self,
        config: IntegrationConfig,
        action: IntegrationAction,
        inputs: Dict[str, Any],
        incident_id: Optional[int],
        actor_username: str,
        error: str = None,
    ) -> Dict[str, Any]:
        """
        Execute action internally.
        
        Placeholder implementation - needs to be replaced with
        actual integration execution logic.
        """
        # Placeholder response
        return {
            "status": "success" if not error else "error",
            "action": action.action_name,
            "inputs": inputs,
            "error": error,
        }
    
    def _log_execution(
        self,
        config: IntegrationConfig,
        action: IntegrationAction,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        actor_username: str,
        incident_id: Optional[int],
        error: str = None,
    ) -> None:
        """Log integration execution."""
        if outputs is None:
            outputs = {}
        
        execution = IntegrationExecution(
            incident_id=incident_id,
            integration_config_id=config.id,
            action_name=action.action_name,
            action_inputs=inputs,
            action_outputs=outputs,
            status="failed" if error else "success",
            error_message=error,
            risk_level=action.risk_level,
            actor_username=actor_username,
        )
        
        self.db.add(execution)
    
    def _create_audit_event(
        self,
        action: IntegrationAction,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        actor_username: str,
        incident_id: Optional[int],
    ) -> None:
        """Create audit event for the action."""
        response = outputs or {}
        
        audit_event = AuditEvent(
            incident_id=incident_id,
            actor_username=actor_username,
            action=f"{action.integration_name}.{action.action_name}",
            resource_type="integration",
            risk_level=action.risk_level,
            response=response,
        )
        
        self.db.add(audit_event)


# Singleton instance
_integration_service: Optional[IntegrationService] = None


def get_integration_service(db: Session) -> IntegrationService:
    """Get integration service singleton."""
    global _integration_service
    if _integration_service is None:
        _integration_service = IntegrationService(db)
    return _integration_service
