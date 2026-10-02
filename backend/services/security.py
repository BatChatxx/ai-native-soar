"""
SOAR Platform - Security Context
Handles risk classification and authorization.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


RISK_LEVELS = {
    "READ": {"description": "Read-only operations", "requires_approval": False, "default_timeout": 300},
    "ENRICH": {"description": "Enrichment operations", "requires_approval": False, "default_timeout": 300},
    "MODIFY_LOW": {"description": "Low-risk modifications", "requires_approval": False, "default_timeout": 300},
    "MODIFY": {"description": "Moderate-risk modifications", "requires_approval": True, "default_timeout": 300},
    "CONTAIN": {"description": "Containment operations", "requires_approval": True, "default_timeout": 600},
    "EXECUTE": {"description": "Remote execution operations", "requires_approval": True, "default_timeout": 600},
    "DESTRUCTIVE": {"description": "Destructive operations", "requires_approval": True, "default_timeout": 300},
}


@dataclass
class ActionPermission:
    """Action permission."""
    name: str
    description: str
    risk_level: str
    requires_approval: bool
    default_timeout: int
    ai_callable: bool = False


class SecurityContext:
    """Security context manager for risk classification and authorization."""
    
    def __init__(self):
        self._registered_tools: Dict[str, ActionPermission] = {}
        self._risk_definitions = RISK_LEVELS.copy()
    
    async def initialize(self):
        """Initialize security context."""
        self._registered_tools.clear()
    
    def register_tool(
        self,
        tool_name: str,
        risk_level: str,
        description: str,
        requires_approval: bool = False,
        ai_callable: bool = False,
        default_timeout: int = 300,
    ):
        """Register a tool with risk classification."""
        key = f"{risk_level}:{tool_name}"
        if risk_level not in self._risk_definitions:
            raise ValueError(f"Invalid risk level: {risk_level}")
        permission = ActionPermission(
            name=tool_name,
            description=description,
            risk_level=risk_level,
            requires_approval=requires_approval,
            default_timeout=default_timeout,
            ai_callable=ai_callable,
        )
        self._registered_tools[key] = permission
    
    def get_tool(self, tool_name: str) -> Optional[ActionPermission]:
        """Get tool permission by name."""
        for key, tool in self._registered_tools.items():
            if tool.name == tool_name:
                return tool
        return None
    
    def validate_action(self, risk_level: str, action_type: str, action_target: str) -> ActionPermission:
        """Validate an action and get its permission."""
        if risk_level not in self._risk_definitions:
            raise ValueError(f"Invalid risk level: {risk_level}")
        
        risk_config = self._risk_definitions[risk_level]
        return ActionPermission(
            name=action_type,
            description=risk_config["description"],
            risk_level=risk_level,
            requires_approval=risk_config["requires_approval"],
            default_timeout=risk_config["default_timeout"],
            ai_callable=True,
        )
    
    def requires_approval(self, risk_level: str) -> bool:
        """Check if risk level requires approval."""
        if risk_level not in self._risk_definitions:
            raise ValueError(f"Invalid risk level: {risk_level}")
        return self._risk_definitions[risk_level]["requires_approval"]
