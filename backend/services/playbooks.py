"""
SOAR Platform - Playbook Service
Handles playbook versioning and execution.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy.orm import Session
from models.playbooks import Playbook, PlaybookVersion, PlaybookRun, PlaybookStepRun, PlaybookApproval


class PlaybookTrigger(Enum):
    INCIDENT_CREATED = "incident_created"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    SEVERITY_THRESHOLD = "severity_threshold"
    TAG_MATCH = "tag_match"
    OBSERVABLE_MATCH = "observable_match"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class PlaybookStepType(Enum):
    TASK = "task"
    IF = "if"
    PARALLEL = "parallel"
    FOR_EACH = "for_each"
    WAIT = "wait"
    APPROVAL = "approval"
    ERROR_HANDLER = "error_handler"
    END = "end"


class PlaybookStepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class PlaybookStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class PlaybookService:
    """
    Playbook service for managing playbook versioning and execution.
    
    Playbooks should initially be declarative YAML or JSON.
    Do NOT prioritize a graphical drag-and-drop editor.
    
    A playbook should support:
    - actions
    - conditions
    - dependencies
    - parallel tasks
    - retries
    - timeouts
    - approvals
    - failure handling
    
    Playbooks must be versioned.
    A historical playbook execution must reference the exact version that executed.
    """
    
    async def initialize(self, db_session: Session):
        """Initialize playbook service."""
        pass
    
    def create_playbook_version(
        self,
        db_session: Session,
        playbook_id: int,
        version: str,
        definition: str,
        notes: Optional[str] = None,
    ) -> PlaybookVersion:
        """
        Create a new playbook version.
        
        Playbooks must be versioned.
        A historical playbook execution must reference the exact version that executed.
        """
        # Use simple versioning for now
        version_hash = self._generate_version_hash(definition)
        
        version = PlaybookVersion(
            playbook_id=playbook_id,
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
    
    def create_playbook_run(
        self,
        db_session: Session,
        playbook_version_id: int,
        incident_id: Optional[int] = None,
        trigger: Optional[str] = None,
        input_data: Optional[str] = None,
    ) -> PlaybookRun:
        """
        Create a playbook run.
        """
        run = PlaybookRun(
            playbook_version_id=playbook_version_id,
            incident_id=incident_id,
            trigger=trigger,
            input_data=input_data,
            status="running",
            created_at=datetime.utcnow(),
        )
        
        db_session.add(run)
        db_session.commit()
        
        return run
    
    def create_step_run(
        self,
        db_session: Session,
        playbook_run_id: int,
        step_type: str,
        step_name: Optional[str] = None,
        output_data: Optional[str] = None,
        error_message: Optional[str] = None,
        requires_approval: bool = False,
        approval_id: Optional[int] = None,
    ) -> PlaybookStepRun:
        """Create a step run record."""
        run = PlaybookRun.get_latest(db_session)
        
        step = PlaybookStepRun(
            playbook_run_id=playbook_run_id,
            step_type=step_type,
            name=step_name,
            status=PlaybookStepStatus.COMPLETED,
            output_data=output_data,
            error_message=error_message,
            requires_approval=requires_approval,
            approval_id=approval_id,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        
        db_session.add(step)
        db_session.commit()
        
        return step
    
    def create_playbook_approval(
        self,
        db_session: Session,
        playbook_run_id: int,
        action_type: str,
        action_target: Optional[str] = None,
        risk_level: str = "MODIFY",
        ai_recommendation: Optional[str] = None,
        ai_reasoning: Optional[str] = None,
    ) -> PlaybookApproval:
        """Create a playbook approval request."""
        approval = PlaybookApproval(
            playbook_run_id=playbook_run_id,
            action_type=action_type,
            action_target=action_target,
            risk_level=risk_level,
            ai_recommendation=ai_recommendation,
            ai_reasoning=ai_reasoning,
            created_at=datetime.utcnow(),
        )
        
        db_session.add(approval)
        db_session.commit()
        
        return approval
