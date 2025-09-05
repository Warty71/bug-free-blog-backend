"""
Pydantic models for authentication API requests and responses.

These models define the structure of data for:
- User registration
- User login
- JWT token responses
"""

from pydantic import BaseModel, EmailStr

class RegisterInput(BaseModel):
    """
    Request model for user registration.
    
    Fields:
        name: User's full name
        email: Valid email address (validated by EmailStr)
        password: Plain text password (will be hashed before storage)
    """
    name: str
    email: EmailStr
    password: str

class LoginInput(BaseModel):
    """
    Request model for user login.
    
    Fields:
        email: User's email address
        password: Plain text password (will be verified against hash)
    """
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Response model for JWT token.
    
    Fields:
        access_token: JWT token string
        token_type: Always "bearer" for JWT tokens
    """
    access_token: str
    token_type: str = "bearer"