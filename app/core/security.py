import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

# Hash the Password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify the Password
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

# Create a JWT token
def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    to_encode: Dict[str, Any] = {"sub": str(subject)}  # 'sub' = subject (user ID)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # 'exp' = expiration time
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode a JWT token
def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])