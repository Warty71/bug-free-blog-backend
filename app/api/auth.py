"""
Authentication API endpoints for user registration, login, and session management.

This module provides:
- User registration with email validation and password hashing
- User login with JWT token generation
- Protected routes that require authentication
- Session management with HttpOnly cookies
- Token validation and user lookup
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
import psycopg2

from app.schemas.auth import RegisterInput, LoginInput, Token
from app.schemas.users import User
from app.core.security import create_access_token, decode_token, hash_password, verify_password

# Database connection string - uses environment variable or defaults to local PostgreSQL
CONNINFO = os.getenv("DATABASE_URL", "postgresql://merislihic@localhost:5432/learning_db")

# FastAPI router for auth endpoints
router = APIRouter()

# Cookie name for storing JWT tokens in browser
COOKIE_NAME = "access_token"

def get_current_user(request: Request) -> User:
    """
    Dependency function to get the current authenticated user from JWT token.
    
    This function:
    1. Extracts JWT token from cookies or Authorization header
    2. Validates and decodes the token
    3. Looks up the user in the database
    4. Returns the user object or raises 401 if invalid
    
    Args:
        request: FastAPI Request object containing headers and cookies
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: 401 if token is missing, invalid, or user not found
    """
    # Step 1: Try to get token from HttpOnly cookie (preferred for browser clients)
    token = request.cookies.get(COOKIE_NAME)
    
    # Step 2: Fall back to Authorization header (for API clients)
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
    
    # Step 3: Ensure we have a token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Step 4: Decode and validate the JWT token
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")  # 'sub' contains the user ID
        
        # Ensure user ID exists in token
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError):
        # Token is malformed, expired, or invalid
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Step 5: Look up user in database
    conn = psycopg2.connect(CONNINFO)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM test_users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        
        if not row:
            # User ID from token doesn't exist in database (user was deleted)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        # Return user object
        return User(id=row[0], name=row[1], email=row[2])
    finally:
        conn.close()

@router.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(body: RegisterInput) -> User:
    """
    Register a new user account.
    
    This endpoint:
    1. Validates that the email is not already registered
    2. Hashes the password using bcrypt
    3. Creates a new user in the database
    4. Returns the user data (without password)
    
    Args:
        body: RegisterInput containing name, email, and password
        
    Returns:
        User: The newly created user object
        
    Raises:
        HTTPException: 409 if email already exists, 500 if database error
    """
    conn = psycopg2.connect(CONNINFO)
    try:
        cur = conn.cursor()
        
        # Step 1: Check if email already exists (prevent duplicate accounts)
        cur.execute("SELECT 1 FROM test_users WHERE email = %s", (body.email,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Email already registered"
            )
        
        # Step 2: Hash the password before storing (never store plain text passwords)
        hashed_pw = hash_password(body.password)
        
        # Step 3: Insert new user into database
        cur.execute(
            "INSERT INTO test_users (name, email, hashed_password) VALUES (%s, %s, %s) RETURNING id",
            (body.name, body.email, hashed_pw),
        )
        
        # Step 4: Get the new user's ID
        result = cur.fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to create user"
            )
        user_id = result[0]
        
        # Step 5: Commit the transaction
        conn.commit()
        
        # Step 6: Return user data (without password hash)
        return User(id=user_id, name=body.name, email=body.email)
    finally:
        conn.close()

@router.post("/auth/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(body: LoginInput, response: Response) -> Token:
    """
    Authenticate user and create a JWT session token.
    
    This endpoint:
    1. Looks up user by email
    2. Verifies the password against the stored hash
    3. Creates a JWT token with user ID
    4. Sets an HttpOnly cookie for browser clients
    5. Returns the token for API clients
    
    Args:
        body: LoginInput containing email and password
        response: FastAPI Response object for setting cookies
        
    Returns:
        Token: JWT token object with access_token and type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    conn = psycopg2.connect(CONNINFO)
    try:
        cur = conn.cursor()
        
        # Step 1: Look up user by email
        cur.execute(
            "SELECT id, name, email, hashed_password FROM test_users WHERE email = %s",
            (body.email,),
        )
        row = cur.fetchone()
        
        # Step 2: Verify user exists and password is correct
        if not row or not verify_password(body.password, row[3]):
            # Don't reveal whether email exists or password is wrong (security best practice)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )

        # Step 3: Create JWT token with user ID as subject
        token = create_access_token(subject=row[0])

        # Step 4: Set HttpOnly cookie for browser-based clients
        # This prevents XSS attacks by making the cookie inaccessible to JavaScript
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,      # Cookie not accessible via JavaScript
            samesite="lax",     # CSRF protection
            secure=False,       # Set to True in production with HTTPS
            max_age=60 * 15,    # 15 minutes expiration
        )
        
        # Step 5: Return token for API clients (mobile apps, etc.)
        return Token(access_token=token)
    finally:
        conn.close()

@router.get("/auth/me", response_model=User, status_code=status.HTTP_200_OK)
def me(user: User = Depends(get_current_user)) -> User:
    """
    Get current authenticated user information.
    
    This is a protected endpoint that requires a valid JWT token.
    The get_current_user dependency handles token validation and user lookup.
    
    Args:
        user: Current authenticated user (injected by FastAPI dependency)
        
    Returns:
        User: Current user's information (id, name, email)
        
    Raises:
        HTTPException: 401 if not authenticated or token is invalid
    """
    return user

@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """
    Logout the current user by clearing the authentication cookie.
    
    This endpoint:
    1. Deletes the HttpOnly cookie containing the JWT token
    2. Returns 204 No Content on success
    
    Note: This only clears the cookie on the server side.
    The client should also clear any stored tokens.
    
    Args:
        response: FastAPI Response object for cookie manipulation
        
    Returns:
        None: 204 No Content response
    """
    response.delete_cookie(COOKIE_NAME)
    return None