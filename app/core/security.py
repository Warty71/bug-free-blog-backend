"""
Security utilities for password hashing and JWT token management.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(password, hashed_password)

def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for a user."""
    to_encode: Dict[str, Any] = {"sub": str(subject)}
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])