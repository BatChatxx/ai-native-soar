"""
SOAR Platform - User Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Create user."""
    username: str
    email: Optional[EmailStr] = None
    password: str
    role_name: str = "analyst"


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: Optional[str]
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
