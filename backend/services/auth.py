"""
SOAR Platform - Authentication Manager
Handles user authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import bcrypt


class Role(Enum):
    """User roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(Enum):
    """User permissions."""
    # Incident management
    INCIDENT_CREATE = "incident:create"
    INCIDENT_READ = "incident:read"
    INCIDENT_WRITE = "incident:write"
    INCIDENT_DELETE = "incident:delete"
    INCIDENT_TRANSFER = "incident:transfer"
    
    # Evidence management
    EVIDENCE_READ = "evidence:read"
    EVIDENCE_WRITE = "evidence:write"
    EVIDENCE_DELETE = "evidence:delete"
    
    # Integration management
    INTEGRATION_READ = "integration:read"
    INTEGRATION_WRITE = "integration:write"
    INTEGRATION_EXECUTE = "integration:execute"
    
    # Playbook management
    PLAYBOOK_READ = "playbook:read"
    PLAYBOOK_WRITE = "playbook:write"
    PLAYBOOK_EXECUTE = "playbook:execute"
    
    # Automation management
    AUTOMATION_READ = "automation:read"
    AUTOMATION_WRITE = "automation:write"
    AUTOMATION_EXECUTE = "automation:execute"
    
    # Approval management
    APPROVAL_READ = "approval:read"
    APPROVAL_VOTE = "approval:vote"
    
    # Audit management
    AUDIT_READ = "audit:read"
    
    # AI management
    AI_READ = "ai:read"
    AI_EXECUTE = "ai:execute"


class RolePermissionMap:
    """Maps roles to permissions."""
    
    SUPER_ADMIN = {
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ, Permission.INCIDENT_WRITE, Permission.INCIDENT_DELETE,
        Permission.EVIDENCE_READ, Permission.EVIDENCE_WRITE, Permission.EVIDENCE_DELETE,
        Permission.INTEGRATION_READ, Permission.INTEGRATION_WRITE, Permission.INTEGRATION_EXECUTE,
        Permission.PLAYBOOK_READ, Permission.PLAYBOOK_WRITE, Permission.PLAYBOOK_EXECUTE,
        Permission.AUTOMATION_READ, Permission.AUTOMATION_WRITE, Permission.AUTOMATION_EXECUTE,
        Permission.APPROVAL_READ, Permission.APPROVAL_VOTE,
        Permission.AUDIT_READ,
        Permission.AI_READ, Permission.AI_EXECUTE,
    }
    
    ADMIN = {
        Permission.INCIDENT_CREATE,
        Permission.INCIDENT_READ, Permission.INCIDENT_WRITE, Permission.INCIDENT_TRANSFER,
        Permission.EVIDENCE_READ, Permission.EVIDENCE_WRITE,
        Permission.INTEGRATION_READ, Permission.INTEGRATION_WRITE,
        Permission.PLAYBOOK_READ, Permission.PLAYBOOK_WRITE, Permission.PLAYBOOK_EXECUTE,
        Permission.AUTOMATION_READ, Permission.AUTOMATION_WRITE, Permission.AUTOMATION_EXECUTE,
        Permission.APPROVAL_READ, Permission.APPROVAL_VOTE,
        Permission.AUDIT_READ,
        Permission.AI_READ, Permission.AI_EXECUTE,
    }
    
    OPERATOR = {
        Permission.INCIDENT_CREATE, Permission.INCIDENT_READ, Permission.INCIDENT_WRITE,
        Permission.EVIDENCE_READ, Permission.EVIDENCE_WRITE,
        Permission.INTEGRATION_READ, Permission.INTEGRATION_EXECUTE,
        Permission.PLAYBOOK_READ, Permission.PLAYBOOK_EXECUTE,
        Permission.AUTOMATION_READ, Permission.AUTOMATION_EXECUTE,
        Permission.APPROVAL_READ,
        Permission.AI_READ, Permission.AI_EXECUTE,
    }
    
    ANALYST = {
        Permission.INCIDENT_CREATE, Permission.INCIDENT_READ, Permission.INCIDENT_WRITE,
        Permission.EVIDENCE_READ, Permission.EVIDENCE_WRITE,
        Permission.INTEGRATION_READ, Permission.INTEGRATION_EXECUTE,
        Permission.PLAYBOOK_READ, Permission.PLAYBOOK_EXECUTE,
        Permission.AUTOMATION_READ, Permission.AUTOMATION_EXECUTE,
        Permission.APPROVAL_READ, Permission.APPROVAL_VOTE,
        Permission.AI_READ, Permission.AI_EXECUTE,
    }
    
    VIEWER = {
        Permission.INCIDENT_READ,
        Permission.EVIDENCE_READ,
        Permission.INTEGRATION_READ,
        Permission.PLAYBOOK_READ,
        Permission.AUTOMATION_READ,
        Permission.AUDIT_READ,
        Permission.AI_READ,
    }


class AuthManager:
    """
    Authentication and authorization manager.
    
    Handles user authentication and RBAC authorization.
    """
    
    def __init__(self):
        self._users: Dict[int, Dict[str, Any]] = {}
        self._user_counter = 0
        self._token_secret = b"soar-secret-key-change-in-production"
    
    async def initialize(self):
        """Initialize auth manager."""
        pass
    
    def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        password: str = None,
        role: Role = Role.ANALYST,
    ) -> Dict[str, Any]:
        """Create a new user."""
        if password is not None:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            password_hash = password_hash.decode()
        else:
            password_hash = ""
        
        self._user_counter += 1
        user = {
            "id": self._user_counter,
            "username": username,
            "email": email,
            "hashed_password": password_hash,
            "role": role.value,
            "permissions": list(RolePermissionMap[role]),
            "is_active": True,
            "is_superuser": role == Role.SUPER_ADMIN,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self._users[user["id"]] = user
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user by username and password."""
        for user in self._users.values():
            if user["username"] == username:
                password_hash = user["hashed_password"].encode()
                if bcrypt.checkpw(password.encode(), password_hash):
                    return user.copy()
        return None
    
    def has_permission(self, user_id: int, permission: Permission) -> bool:
        """Check if user has permission."""
        user = self._users.get(user_id)
        if not user:
            return False
        return permission in user.get("permissions", set())
    
    def has_permission_list(self, user_id: int, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        user = self._users.get(user_id)
        if not user:
            return False
        user_perms = set(user.get("permissions", set()))
        return any(p in user_perms for p in permissions)
    
    def get_user_role(self, user_id: int) -> Optional[str]:
        """Get user role by ID."""
        user = self._users.get(user_id)
        if user:
            return user.get("role")
        return None
    
    def get_permissions_by_role(self, role: str) -> set:
        """Get permissions for a role."""
        role_map = {
            Role.SUPER_ADMIN: RolePermissionMap.SUPER_ADMIN,
            Role.ADMIN: RolePermissionMap.ADMIN,
            Role.OPERATOR: RolePermissionMap.OPERATOR,
            Role.ANALYST: RolePermissionMap.ANALYST,
            Role.VIEWER: RolePermissionMap.VIEWER,
        }
        role = Role(role)
        return role_map.get(role, set())
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (for admin)."""
        return [u.copy() for u in self._users.values()]
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user."""
        user = self._users.get(user_id)
        if user:
            user["is_active"] = False
            user["updated_at"] = datetime.utcnow().isoformat()
            return True
        return False
    
    def clear(self):
        """Clear all users (for testing only)."""
        self._users.clear()
        self._user_counter = 0
