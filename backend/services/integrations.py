"""
SOAR Platform - Integration Service
Handles integration management and execution.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy.orm import Session
from models.integrations import IntegrationConfig, IntegrationInstance, IntegrationAction, IntegrationExecution


class IntegrationCategory(Enum):
    SIEM = "siem"
    EDR = "edr"
    TICKETING = "ticketing"
    EMAIL = "email"
    IP_INTEL = "ip_intelligence"
    THREAT_INTEL = "threat_intelligence"
    ENDPOINT = "endpoint"
    NETWORK = "network"
    FILE_SHARE = "file_share"
    IDENTITY = "identity"
    CLOUD = "cloud"


class ActionRiskLevel(Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY_LOW = "MODIFY_LOW"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class IntegrationService:
    """
    Integration service for managing integration instances.
    
    Do not hardcode every vendor directly into the incident service.
    Use a common integration abstraction.
    """
    
    def __init__(self):
        self._category_descriptions = {
            "siem": "Security Information and Event Management",
            "edr": "Endpoint Detection and Response",
            "ticketing": "Ticketing System",
            "email": "Email System",
            "ip_intelligence": "IP Intelligence",
            "threat_intelligence": "Threat Intelligence",
            "endpoint": "Endpoint Security",
            "network": "Network Security",
            "file_share": "File Share",
            "identity": "Identity Provider",
            "cloud": "Cloud Service",
        }
    
    async def initialize(self, db_session: Session):
        """Initialize integration service."""
        pass
    
    def get_category_description(self, category: str) -> str:
        """Get description for integration category."""
        return self._category_descriptions.get(category, "Integration")
    
    def register_integration_action(
        self,
        db_session: Session,
        config_id: int,
        action_name: str,
        full_path: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None,
        risk_level: str = "READ",
        requires_approval: bool = False,
        ai_callable: bool = True,
        default_timeout: int = 300,
    ) -> IntegrationAction:
        """
        Register an integration action.
        
        Every action defines:
        - name
        - description
        - input schema
        - output schema
        - required permission
        - risk classification
        
        Example:
        MockEDR
        get_host
        Risk: READ
        
        get_process_tree
        Risk: READ
        
        contain_host
        Risk: CONTAIN
        
        run_rtr_command
        Risk: EXECUTE
        
        The same action framework should eventually support:
        - manual execution
        - playbook execution
        - AI agent tool execution
        """
        action = IntegrationAction(
            config_id=config_id,
            action_name=action_name,
            full_path=full_path,
            description=description or "",
            input_schema=input_schema,
            output_schema=output_schema,
            risk_level=risk_level,
            requires_approval=requires_approval,
            ai_callable=ai_callable,
            default_timeout=default_timeout,
            enabled=True,
            created_at=datetime.utcnow(),
        )
        
        db_session.add(action)
        db_session.commit()
        
        return action
    
    def execute_action(
        self,
        db_session: Session,
        action_instance_id: int,
        incident_id: Optional[int] = None,
        input_data: Optional[str] = None,
        requires_approval: bool = False,
        approval_id: Optional[int] = None,
    ) -> IntegrationExecution:
        """
        Execute an integration action.
        
        The LLM does not determine its own permissions.
        Backend determines whether approval is required.
        """
        action_instance = db_session.query(IntegrationAction).get(action_instance_id)
        
        if not action_instance:
            raise ValueError(f"Action instance {action_instance_id} not found")
        
        # For real execution, would call external system here
        execution = IntegrationExecution(
            action_instance_id=action_instance_id,
            incident_id=incident_id,
            input_data=input_data,
            output_data=str(action_instance.output_schema),
            error_message=None,
            status="success",
            requires_approval=requires_approval,
            approval_id=approval_id,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=100,
            created_at=datetime.utcnow(),
        )
        
        db_session.add(execution)
        db_session.commit()
        
        return execution
