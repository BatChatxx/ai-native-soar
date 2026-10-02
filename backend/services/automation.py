"""
SOAR Platform - Automation Service
Handles automation script versioning and execution.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from models.automation import AutomationScript, AutomationVersion, AutomationRun


class AutomationType(Enum):
    SCRIPT = "script"
    FUNCTION = "function"
    WORKFLOW = "workflow"


class AutomationTrigger(Enum):
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    INCIDENT_TAG_CHANGE = "incident_tag_change"
    OBSERVABLE_DETECTED = "observable_detected"
    SCHEDULED = "scheduled"
    EVENT_MATCH = "event_match"
    MANUAL = "manual"


class AutomationStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class AutomationRisk(Enum):
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class AutomationStatusEnum(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AutomationService:
    """
    Automation service for managing automation scripts.
    
    Automation scripts must be versioned.
    Do not allow arbitrary unsandboxed code execution.
    
    Eventually automation workers should execute scripts inside restricted workers or containers with controls such as:
    - execution timeout
    - restricted filesystem
    - restricted networking
    - restricted secrets
    - resource limits
    - structured JSON input
    - structured JSON output
    
    Do not implement unrestricted arbitrary shell execution merely for convenience.
    """
    
    async def initialize(self, db_session: Session):
        """Initialize automation service."""
        pass
    
    def register_automation_script(
        self,
        db_session: Session,
        name: str,
        description: Optional[str] = None,
        definition: Optional[str] = None,
        script_type: Optional[AutomationType] = AutomationType.SCRIPT,
        trigger: Optional[AutomationTrigger] = AutomationTrigger.MANUAL,
        trigger_config: Optional[str] = None,
        status: AutomationStatus = AutomationStatus.DRAFT,
        risk_level: AutomationRisk = AutomationRisk.READ,
        requires_approval: bool = False,
        author: Optional[str] = None,
        tags: Optional[str] = None,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None,
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: int = 30,
        metadata: Optional[dict] = None,
    ) -> AutomationScript:
        """
        Register an automation script.
        
        Automation scripts must be versioned.
        Do not allow arbitrary unsandboxed code execution.
        """
        script = AutomationScript(
            name=name,
            description=description or "",
            definition=definition,
            script_type=script_type,
            trigger=trigger,
            trigger_config=trigger_config,
            status=status,
            risk_level=risk_level,
            requires_approval=requires_approval,
            author=author,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            metadata=str(metadata) if metadata else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db_session.add(script)
        db_session.commit()
        
        return script
    
    def create_automation_version(
        self,
        db_session: Session,
        script_id: int,
        version: str,
        definition: str,
        notes: Optional[str] = None,
    ) -> AutomationVersion:
        """Create a new automation version."""
        # Use simple versioning for now
        version_hash = self._generate_version_hash(definition)
        
        version = AutomationVersion(
            script_id=script_id,
            version=version,
            version_hash=version_hash,
            definition=definition,
            notes=notes or "",
            created_at=datetime.utcnow(),
        )
        
        db_session.add(version)
        db_session.commit()
        
        return version
    
    def _generate_version_hash(self, definition: str) -> str:
        """Generate a simple hash for version."""
        import hashlib
        import json
        data = json.dumps(definition, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def create_automation_run(
        self,
        db_session: Session,
        version_id: int,
        incident_id: Optional[int] = None,
        input_data: Optional[str] = None,
    ) -> AutomationRun:
        """
        Create an automation run.
        
        Structured JSON input and output.
        """
        run = AutomationRun(
            version_id=version_id,
            incident_id=incident_id,
            input_data=input_data,
            status=AutomationStatusEnum.RUNNING,
            started_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        
        db_session.add(run)
        db_session.commit()
        
        return run
    
    def complete_automation_run(
        self,
        db_session: Session,
        run_id: int,
        status: AutomationStatusEnum,
        output_data: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        audit_event_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> AutomationRun:
        """Complete an automation run."""
        run = db_session.query(AutomationRun).get(run_id)
        
        if run:
            run.status = status
            run.output_data = output_data
            run.error_message = error_message
            run.completed_at = datetime.utcnow()
            run.duration_ms = duration_ms
            run.audit_event_id = audit_event_id
            run.meta = str(metadata) if metadata else None
            db_session.commit()
        
        return run
