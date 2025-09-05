"""
Security utilities for password hashing and JWT token management.

This module provides:
- Password hashing using bcrypt
- JWT token creation and validation
- Secure configuration management
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing configuration
# bcrypt is a secure, slow hashing algorithm that's resistant to brute force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY")  # Secret for signing tokens
ALGORITHM = os.getenv("ALGORITHM", "HS256")                # JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # Token lifetime

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    bcrypt automatically generates a random salt for each password,
    making it secure against rainbow table attacks.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Hashed password string (e.g., "$2b$12$...")
    """
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hash to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(password, hashed_password)

def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for a user.
    
    The token contains:
    - 'sub' (subject): User ID
    - 'exp' (expiration): Token expiration timestamp
    
    Args:
        subject: User ID to encode in the token
        expires_delta: Custom expiration time (optional)
        
    Returns:
        str: JWT token string
    """
    # Create token payload with user ID
    to_encode: Dict[str, Any] = {"sub": str(subject)}
    
    # Set expiration time (default or custom)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # Sign and encode the token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    This function:
    1. Verifies the token signature using our secret key
    2. Checks if the token has expired
    3. Returns the token payload
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Dict[str, Any]: Token payload containing user ID and expiration
        
    Raises:
        JWTError: If token is invalid, expired, or tampered with
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])