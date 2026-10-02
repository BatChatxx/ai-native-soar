"""
Authentication utilities for SOAR Platform.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import hashlib
import secrets
import os
from typing import Optional, Callable

# Security configuration
SECRET_KEY = os.environ.get("SOAR_API_SECRET", "secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing via PBKDF2 (stdlib, no bcrypt/passlib compatibility issues)
_PBKDF2_ITERATIONS = 260000


def _hash_password(plain: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS)
    return dk.hex()


def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2. Returns "salt$hash"."""
    salt = secrets.token_hex(16)
    return f"{salt}${_hash_password(password, salt)}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a "salt$hash" string."""
    try:
        salt, expected = hashed_password.split("$", 1)
    except ValueError:
        return False
    actual = _hash_password(plain_password, salt)
    return secrets.compare_digest(actual, expected)


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Token payload data
        expires_delta: Optional expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode["exp"] = expire
    to_encode.update(data)
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Get current user from JWT token.
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        User data dict
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # TODO: Look up user in database
        # user = db.query(User).filter(User.username == username).first()
        # if user is None:
        #     raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    return {"username": username}


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = None
) -> Optional[dict]:
    """
    Get current user (optional - for non-authenticated endpoints).
    
    Args:
        token: JWT token from Authorization header
        db: Database session
    
    Returns:
        User data dict or None if no token
    
    Raises:
        HTTPException: If token is invalid
    """
    if token is None:
        return None
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        username: str = payload.get("sub")
        if username is None:
            return None
        
    except JWTError:
        return None
    
    # TODO: Look up user in database
    # user = db.query(User).filter(User.username == username).first()
    # if user is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"username": username}


async def check_permission(
    username: str,
    permission: str,
    db: Session = None
) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        username: Username of the user
        permission: Permission to check (e.g., "approve_action")
        db: Database session
    
    Returns:
        True if user has permission, False otherwise
    """
    # TODO: Implement permission check against database
    # This would check user_roles and roles_permissions tables
    
    # For now, return True for demo purposes
    return True


def require_permission(permission: str) -> Callable:
    """
    Decorator to require a specific permission.
    
    Args:
        permission: Permission string (e.g., "approve_action")
    
    Returns:
        Decorator function
    """
    def decorator(func):
        from fastapi import Depends, HTTPException, status
        
        async def wrapper(*args, **kwargs):
            # Extract db from args or kwargs
            db = next((arg for arg in args if isinstance(arg, Session)), 
                      kwargs.get("db"))
            
            if db is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Database session required")
            
            username = kwargs.get("current_user")
            if username is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
            
            if not await check_permission(username, permission, db):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
