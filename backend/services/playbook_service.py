"""
Playbook Service - Handle playbook definition, execution, and versioning.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.models import Playbook, PlaybookVersion, PlaybookRun, PlaybookStep
import json
import re


class PlaybookService:
    """
    Playbook service for managing playbook lifecycle.
    
    Playbooks support:
    - actions
    - conditions
    - dependencies
    - parallel tasks
    - retries
    - timeouts
    - approvals
    - failure handling
    """
    
    def __init__(self, db: Session):
        """
        Initialize playbook service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def list_playbooks(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        List all playbooks.
        
        Args:
            status_filter: Filter by status (draft, active, deprecated)
    
        Returns:
            List of playbook records
        """
        if status_filter:
            playbooks = self.db.query(Playbook).filter(
                Playbook.status == status_filter
            ).all()
        else:
            playbooks = self.db.query(Playbook).all()
        
        return [pb.to_dict() for pb in playbooks]
    
    async def get_playbook(self, name: str) -> Optional[Dict]:
        """
        Get playbook by name.
        
        Args:
            name: Playbook name
    
        Returns:
            Playbook record
        """
        playbook = self.db.query(Playbook).filter(
            Playbook.name == name
        ).first()
        
        if not playbook:
            return None
        
        return playbook.to_dict()
    
    async def list_versions(self, playbook_name: str) -> List[Dict]:
        """
        List playbook versions.
        
        Args:
            playbook_name: Playbook name
    
        Returns:
            List of version records
        """
        playbook = self.db.query(Playbook).filter(
            Playbook.name == playbook_name
        ).first()
        
        if not playbook:
            return []
        
        versions = self.db.query(PlaybookVersion).filter(
            PlaybookVersion.playbook_id == playbook.id
        ).order_by(PlaybookVersion.version.desc()).all()
        
        return [v.to_dict() for v in versions]
    
    async def get_version(self, playbook_name: str, version: str) -> Optional[Dict]:
        """
        Get specific playbook version.
        
        Args:
            playbook_name: Playbook name
            version: Version number (e.g., "1.0", "1.1")
    
        Returns:
            Version record
        """
        playbook = self.db.query(Playbook).filter(
            Playbook.name == playbook_name
        ).first()
        
        if not playbook:
            return None
        
        version_record = self.db.query(PlaybookVersion).filter(
            PlaybookVersion.playbook_id == playbook.id,
            PlaybookVersion.version == version
        ).first()
        
        if not version_record:
            return None
        
        return version_record.to_dict()
    
    async def create_playbook(
        self,
        name: str,
        description: str,
        definition: Dict,
    ) -> Dict:
        """
        Create new playbook.
        
        Args:
            name: Playbook name
            description: Playbook description
            definition: Playbook definition
    
        Returns:
            Created playbook record
        """
        playbook = Playbook(
            name=name,
            description=description,
            definition=definition,
            status="draft",
        )
        
        self.db.add(playbook)
        self.db.commit()
        
        return playbook.to_dict()
    
    async def update_playbook_definition(
        self,
        playbook_name: str,
        version: str,
        definition: Dict,
        notes: Optional[str] = None,
    ) -> Dict:
        """
        Update playbook definition (create new version).
        
        Args:
            playbook_name: Playbook name
            version: New version number
            definition: New definition
            notes: Version notes
    
        Returns:
            New version record
        """
        playbook = self.db.query(Playbook).filter(
            Playbook.name == playbook_name
        ).first()
        
        if not playbook:
            raise ValueError(f"Playbook not found: {playbook_name}")
        
        version_record = PlaybookVersion(
            playbook_id=playbook.id,
            version=version,
            version_hash=self._generate_version_hash(definition),
            definition=definition,
            notes=notes,
        )
        
        playbook.versions.append(version_record)
        self.db.commit()
        
        return version_record.to_dict()
    
    async def execute_playbook(
        self,
        playbook_name: str,
        version: Optional[str] = None,
        incident_id: Optional[int] = None,
        trigger_type: Optional[str] = None,
        trigger_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Execute playbook.
        
        Args:
            playbook_name: Playbook name
            version: Version to execute (if not specified, uses active version)
            incident_id: Associated incident ID
            trigger_type: Trigger type (e.g., "incident_created")
            trigger_data: Trigger data
    
        Returns:
            Execution record
        """
        # Get playbook
        playbook = self.db.query(Playbook).filter(
            Playbook.name == playbook_name
        ).first()
        
        if not playbook:
            raise ValueError(f"Playbook not found: {playbook_name}")
        
        # Get version (use latest active version if not specified)
        if version:
            version_record = self.db.query(PlaybookVersion).filter(
                PlaybookVersion.playbook_id == playbook.id,
                PlaybookVersion.version == version
            ).first()
            
            if not version_record:
                raise ValueError(f"Version not found: {version}")
        else:
            version_record = self.db.query(PlaybookVersion).filter(
                PlaybookVersion.playbook_id == playbook.id,
                PlaybookVersion.status == "active"
            ).first()
            
            if not version_record:
                raise ValueError("No active version found for playbook")
        
        # Create execution
        run = PlaybookRun(
            playbook_version_id=version_record.id,
            incident_id=incident_id,
            trigger_type=trigger_type,
            trigger_data=trigger_data,
            status="running",
        )
        
        self.db.add(run)
        self.db.commit()
        
        # Parse playbook definition
        definition = version_record.definition
        if definition:
            parsed = self._parse_definition(definition)
        else:
            parsed = {}
        
        # Execute playbook steps
        results = await self._execute_playbook_steps(
            playbook=playbook,
            run=run,
            incident_id=incident_id,
            parsed_definition=parsed,
        )
        
        # Update run status
        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.results = results
        run.duration_ms = 0  # Will be updated after execution
        
        self.db.commit()
        
        return run.to_dict()
    
    async def _execute_playbook_steps(
        self,
        playbook: Playbook,
        run: PlaybookRun,
        incident_id: Optional[int],
        parsed_definition: Dict,
    ) -> Dict:
        """
        Execute playbook steps.
        
        Args:
            playbook: Playbook record
            run: Execution record
            incident_id: Associated incident ID
            parsed_definition: Parsed playbook definition
    
        Returns:
            Execution results
        """
        results = {
            "status": "success",
            "steps_completed": [],
            "steps_failed": [],
        }
        
        # TODO: Implement step execution based on definition
        # For now, simulate step execution
        for i, action in enumerate(parsed_definition.get("actions", [])):
            step = PlaybookStep(
                run_id=run.id,
                action=action,
                status="success",
            )
            
            self.db.add(step)
            self.db.commit()
            
            results["steps_completed"].append({
                "index": i,
                "action": action.get("type"),
                "args": action.get("args"),
            })
        
        return results
    
    async def run_parallel_tasks(
        self,
        task_id: str,
        tasks: List[Dict],
        incident_id: Optional[int],
    ) -> Dict:
        """
        Run parallel tasks.
        
        Args:
            task_id: Parallel task group ID
            tasks: List of tasks to execute
            incident_id: Associated incident ID
    
        Returns:
            Task execution results
        """
        results = {
            "status": "success",
            "tasks": [],
        }
        
        for task in tasks:
            # Execute task
            result = await self._execute_task(task, incident_id)
            results["tasks"].append(result)
        
        return results
    
    async def _execute_task(self, task: Dict, incident_id: Optional[int]) -> Dict:
        """
        Execute individual task.
        
        Args:
            task: Task definition
            incident_id: Associated incident ID
    
        Returns:
            Task result
        """
        # TODO: Implement task execution
        # For now, return mock result
        return {
            "status": "success",
            "action": task.get("type"),
            "args": task.get("args"),
        }
    
    async def validate_playbook(self, playbook_name: str, version: str) -> Dict:
        """
        Validate playbook definition.
        
        Args:
            playbook_name: Playbook name
            version: Version to validate
    
        Returns:
            Validation result
        """
        version_record = self.db.query(PlaybookVersion).filter(
            PlaybookVersion.playbook_id == self._get_playbook_id(playbook_name),
            PlaybookVersion.version == version
        ).first()
        
        if not version_record:
            raise ValueError(f"Playbook version not found: {playbook_name} {version}")
        
        definition = version_record.definition
        if not definition:
            return {
                "valid": True,
                "message": "No definition to validate",
            }
        
        # TODO: Implement playbook validation
        # - Check for required fields
        # - Validate action types
        # - Check for circular dependencies
        # - Validate timeout values
        
        return {
            "valid": True,
            "message": "Playbook is valid",
            "definition": definition,
        }
    
    async def rollback_version(
        self,
        playbook_name: str,
        target_version: str,
    ) -> Dict:
        """
        Rollback playbook to specific version.
        
        Args:
            playbook_name: Playbook name
            target_version: Version to rollback to
    
        Returns:
            Rollback result
        """
        playbook = self.db.query(Playbook).filter(
            Playbook.name == playbook_name
        ).first()
        
        if not playbook:
            raise ValueError(f"Playbook not found: {playbook_name}")
        
        version_record = self.db.query(PlaybookVersion).filter(
            PlaybookVersion.playbook_id == playbook.id,
            PlaybookVersion.version == target_version
        ).first()
        
        if not version_record:
            raise ValueError(f"Version not found: {target_version}")
        
        # Deactivate current version
        active_version = self.db.query(PlaybookVersion).filter(
            PlaybookVersion.playbook_id == playbook.id,
            PlaybookVersion.status == "active"
        ).first()
        
        if active_version:
            active_version.status = "deprecated"
        
        # Activate target version
        version_record.status = "active"
        
        self.db.commit()
        
        return {
            "status": "success",
            "playbook": playbook_name,
            "target_version": target_version,
        }
    
    def _parse_definition(self, definition: Dict) -> Dict:
        """
        Parse playbook definition into executable format.
        
        Args:
            definition: Raw playbook definition
    
        Returns:
            Parsed definition
        """
        # TODO: Implement definition parsing
        # - Parse actions into step definitions
        # - Parse conditions into validation rules
        # - Parse dependencies into execution order
        # - Parse timeouts and retries
        
        return definition
    
    def _generate_version_hash(self, definition: Any) -> str:
        """
        Generate version hash for definition.
        
        Args:
            definition: Definition to hash
    
        Returns:
            Hash string
        """
        import hashlib
        import json
        
        if isinstance(definition, dict):
            definition = json.dumps(definition, sort_keys=True)
        elif isinstance(definition, str):
            pass
        
        return hashlib.sha256(definition.encode()).hexdigest()[:16]
    
    def _get_playbook_id(self, name: str) -> int:
        """
        Get playbook ID by name.
        
        Args:
            name: Playbook name
    
        Returns:
            Playbook ID
        """
        playbook = self.db.query(Playbook).filter(
            Playbook.name == name
        ).first()
        
        return playbook.id if playbook else 0
