"""
Lightweight auth router: login + default admin account management.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import User
from utils.auth_utils import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

DEFAULT_ADMIN = "admin"


def _get_or_create_admin(db: Session) -> User:
    """Ensure a default admin user exists (created from env password)."""
    admin = db.query(User).filter(User.username == DEFAULT_ADMIN).first()
    if admin:
        return admin

    default_pw = os.getenv("SOAR_ADMIN_PASSWORD", "admin")
    admin = User(
        username=DEFAULT_ADMIN,
        email="admin@soar.local",
        hashed_password=get_password_hash(default_pw),
        full_name="Administrator",
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    admin = _get_or_create_admin(db)
    if data.username != admin.username:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(data.password, admin.hashed_password or ""):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": admin.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": admin.username,
        "is_superuser": admin.is_superuser,
    }


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db)):
    """Change the admin password (verifies current password first)."""
    admin = _get_or_create_admin(db)
    if not verify_password(data.current_password, admin.hashed_password or ""):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    admin.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me")
def me(db: Session = Depends(get_db)):
    """Return info about the default account (no auth needed for demo)."""
    admin = _get_or_create_admin(db)
    return {
        "username": admin.username,
        "email": admin.email,
        "full_name": admin.full_name,
        "is_superuser": admin.is_superuser,
    }
