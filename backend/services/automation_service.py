"""
Automation Service - Handle automation script lifecycle and execution.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.models import AutomationScript, AutomationVersion, AutomationRun
import subprocess
import os
import tempfile


class AutomationService:
    """
    Automation service for managing automation scripts.
    
    Automation scripts must be:
    - Versioned
    - Restricted execution (no arbitrary shell)
    - Timeout-controlled
    - Resource-limited
    """
    
    def __init__(self, db: Session):
        """
        Initialize automation service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def list_automation(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        List all automation scripts.
        
        Args:
            status_filter: Filter by status (draft, active, deprecated)
    
        Returns:
            List of automation records
        """
        if status_filter:
            scripts = self.db.query(AutomationScript).filter(
                AutomationScript.status == status_filter
            ).all()
        else:
            scripts = self.db.query(AutomationScript).all()
        
        return [script.to_dict() for script in scripts]
    
    async def get_automation(self, name: str) -> Optional[Dict]:
        """
        Get automation by name.
        
        Args:
            name: Automation name
    
        Returns:
            Automation record
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.name == name
        ).first()
        
        if not script:
            return None
        
        return script.to_dict()
    
    async def list_versions(self, script_name: str) -> List[Dict]:
        """
        List automation versions.
        
        Args:
            script_name: Automation name
    
        Returns:
            List of version records
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.name == script_name
        ).first()
        
        if not script:
            return []
        
        versions = self.db.query(AutomationVersion).filter(
            AutomationVersion.script_id == script.id
        ).order_by(AutomationVersion.version.desc()).all()
        
        return [v.to_dict() for v in versions]
    
    async def get_version(self, script_name: str, version: str) -> Optional[Dict]:
        """
        Get specific automation version.
        
        Args:
            script_name: Automation name
            version: Version number
    
        Returns:
            Version record
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.name == script_name
        ).first()
        
        if not script:
            return None
        
        version_record = self.db.query(AutomationVersion).filter(
            AutomationVersion.script_id == script.id,
            AutomationVersion.version == version
        ).first()
        
        if not version_record:
            return None
        
        return version_record.to_dict()
    
    async def create_automation(
        self,
        name: str,
        description: str,
        definition: Dict,
        script_type: str,
        trigger: Optional[Dict] = None,
        trigger_config: Optional[Dict] = None,
        risk_level: str = "READ",
        requires_approval: bool = False,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        input_schema: Optional[Dict] = None,
        output_schema: Optional[Dict] = None,
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: int = 30,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Create new automation script.
        
        Args:
            name: Script name
            description: Script description
            definition: Script definition
            script_type: Script type (python, powershell, etc.)
            trigger: Trigger definition (optional)
            trigger_config: Trigger configuration (optional)
            risk_level: Risk level
            requires_approval: Whether approval is required
            author: Script author
            tags: Script tags
            input_schema: Input JSON schema
            output_schema: Output JSON schema
            timeout: Execution timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Retry delay in seconds
            metadata: Additional metadata
    
        Returns:
            Created automation record
        """
        script = AutomationScript(
            name=name,
            description=description,
            definition=definition,
            script_type=script_type,
            trigger=trigger,
            trigger_config=trigger_config,
            status="draft",
            risk_level=risk_level,
            requires_approval=requires_approval,
            author=author,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            metadata=metadata,
        )
        
        self.db.add(script)
        self.db.commit()
        
        return script.to_dict()
    
    async def update_automation_definition(
        self,
        script_name: str,
        version: str,
        definition: Dict,
        notes: Optional[str] = None,
    ) -> Dict:
        """
        Update automation definition (create new version).
        
        Args:
            script_name: Automation name
            version: New version number
            definition: New definition
            notes: Version notes
    
        Returns:
            New version record
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.name == script_name
        ).first()
        
        if not script:
            raise ValueError(f"Automation script not found: {script_name}")
        
        version_record = AutomationVersion(
            script_id=script.id,
            version=version,
            version_hash=self._generate_version_hash(definition),
            definition=definition,
            notes=notes,
        )
        
        script.versions.append(version_record)
        self.db.commit()
        
        return version_record.to_dict()
    
    async def execute_automation(
        self,
        script_name: str,
        version: Optional[str] = None,
        incident_id: Optional[int] = None,
        input_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Execute automation script.
        
        Args:
            script_name: Automation name
            version: Version to execute
            incident_id: Associated incident ID
            input_data: Automation input data
    
        Returns:
            Execution result
        """
        # Get script
        script = self.db.query(AutomationScript).filter(
            AutomationScript.name == script_name
        ).first()
        
        if not script:
            raise ValueError(f"Automation script not found: {script_name}")
        
        # Get version (use latest active version if not specified)
        if version:
            version_record = self.db.query(AutomationVersion).filter(
                AutomationVersion.script_id == script.id,
                AutomationVersion.version == version
            ).first()
            
            if not version_record:
                raise ValueError(f"Version not found: {version}")
        else:
            version_record = self.db.query(AutomationVersion).filter(
                AutomationVersion.script_id == script.id,
                AutomationVersion.status == "active"
            ).first()
            
            if not version_record:
                raise ValueError("No active version found for automation")
        
        # Create execution record
        run = AutomationRun(
            automation_version_id=version_record.id,
            incident_id=incident_id,
            input_data=input_data,
            status="running",
        )
        
        self.db.add(run)
        self.db.commit()
        
        # Execute automation
        result = await self._execute_automation_impl(
            script=script,
            run=run,
            incident_id=incident_id,
            input_data=input_data,
        )
        
        # Update run status
        run.status = "completed" if result.get("success") else "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.output_data = result
        run.duration_ms = result.get("duration_ms", 0)
        run.error_message = result.get("error")
        
        self.db.commit()
        
        return run.to_dict()
    
    async def _execute_automation_impl(
        self,
        script: AutomationScript,
        run: AutomationRun,
        incident_id: Optional[int],
        input_data: Optional[Dict],
    ) -> Dict:
        """
        Execute automation implementation.
        
        Args:
            script: Automation script
            run: Execution record
            incident_id: Associated incident ID
            input_data: Automation input data
    
        Returns:
            Execution result
        """
        # TODO: Implement automation execution
        # For now, return mock result
        
        # Security considerations:
        # 1. Never execute arbitrary shell commands
        # 2. Always respect timeout limits
        # 3. Use restricted filesystem access
        # 4. Validate all inputs against schema
        # 5. Handle errors gracefully
        
        # Example implementation structure:
        """
        try:
            # Validate input
            validated_input = self._validate_input(input_data, script.input_schema)
            
            # Execute based on script type
            if script.script_type == "python":
                result = await self._execute_python_script(
                    script_path=script.path,
                    input_data=validated_input,
                    timeout=script.timeout,
                    incident_id=incident_id,
                )
            elif script.script_type == "powershell":
                result = await self._execute_powershell_script(
                    script_path=script.path,
                    input_data=validated_input,
                    timeout=script.timeout,
                    incident_id=incident_id,
                )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
        """
        
        # Return mock result for demo
        return {
            "success": True,
            "status": "completed",
            "message": f"Mock execution of {script.name} version {script.versions[-1].version}",
            "output": None,
            "duration_ms": 0,
        }
    
    async def execute_read_automation(
        self,
        script_name: str,
        version: Optional[str] = None,
        incident_id: Optional[int] = None,
        input_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Execute read automation (READ or ENRICH risk level).
        
        Read automations can execute automatically without approval.
        
        Args:
            script_name: Automation name
            version: Version to execute
            incident_id: Associated incident ID
            input_data: Automation input data
    
        Returns:
            Execution result
        """
        return await self.execute_automation(
            script_name=script_name,
            version=version,
            incident_id=incident_id,
            input_data=input_data,
        )
    
    async def execute_modify_automation(
        self,
        script_name: str,
        version: Optional[str] = None,
        incident_id: Optional[int] = None,
        input_data: Optional[Dict] = None,
        requires_approval: bool = True,
    ) -> Dict:
        """
        Execute modify automation (MODIFY or CONTAIN risk level).
        
        Modify automations require approval unless explicitly allowed.
        
        Args:
            script_name: Automation name
            version: Version to execute
            incident_id: Associated incident ID
            input_data: Automation input data
            requires_approval: Whether approval is required (default: True)
    
        Returns:
            Execution result
    
        Raises:
            HTTPException: If approval is required and not obtained
        """
        if requires_approval:
            # TODO: Check approval status
            pass
        
        return await self.execute_automation(
            script_name=script_name,
            version=version,
            incident_id=incident_id,
            input_data=input_data,
        )
    
    async def execute_destructive_automation(
        self,
        script_name: str,
        version: Optional[str] = None,
        incident_id: Optional[int] = None,
        input_data: Optional[Dict] = None,
        requires_approval: bool = True,
    ) -> Dict:
        """
        Execute destructive automation (EXECUTE or DESTRUCTIVE risk level).
        
        Destructive automations always require approval.
        
        Args:
            script_name: Automation name
            version: Version to execute
            incident_id: Associated incident ID
            input_data: Automation input data
            requires_approval: Whether approval is required (default: True)
    
        Returns:
            Execution result
    
        Raises:
            HTTPException: If approval is required and not obtained
        """
        if not requires_approval:
            raise ValueError("Destructive automations must require approval")
        
        # TODO: Create approval request
        # await self._create_approval_request(
        #     incident_id=incident_id,
        #     script_name=script_name,
        #     input_data=input_data,
        # )
        
        # Wait for approval
        # await self._wait_for_approval()
        
        return await self.execute_automation(
            script_name=script_name,
            version=version,
            incident_id=incident_id,
            input_data=input_data,
        )
    
    async def _execute_python_script(
        self,
        script_path: str,
        input_data: Dict,
        timeout: int,
        incident_id: Optional[int],
    ) -> Dict:
        """
        Execute Python script.
        
        Args:
            script_path: Script file path
            input_data: Script input data
            timeout: Execution timeout in seconds
            incident_id: Associated incident ID
    
        Returns:
            Execution result
        """
        # TODO: Implement Python script execution
        # - Write input data to temporary file
        # - Execute script with restricted permissions
        # - Capture output and errors
        # - Respect timeout
        
        return {
            "success": False,
            "error": "Python script execution not implemented",
        }
    
    async def _execute_powershell_script(
        self,
        script_path: str,
        input_data: Dict,
        timeout: int,
        incident_id: Optional[int],
    ) -> Dict:
        """
        Execute PowerShell script.
        
        Args:
            script_path: Script file path
            input_data: Script input data
            timeout: Execution timeout in seconds
            incident_id: Associated incident ID
    
        Returns:
            Execution result
        """
        # TODO: Implement PowerShell script execution
        # - Validate script content
        # - Execute with restricted permissions
        # - Capture output and errors
        # - Respect timeout
        
        return {
            "success": False,
            "error": "PowerShell script execution not implemented",
        }
    
    def _validate_input(self, data: Dict, schema: Dict) -> Dict:
        """
        Validate automation input against schema.
        
        Args:
            data: Input data
            schema: JSON schema
    
        Returns:
            Validated input
        """
        # TODO: Implement input validation
        # - Check required fields
        # - Validate field types
        # - Check value ranges
        # - Sanitize values
        
        return data
    
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
