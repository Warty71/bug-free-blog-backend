"""
Authentication API endpoints for user registration, login, and session management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError
from app.core.database import get_db_connection

from app.schemas.auth import RegisterInput, LoginInput, Token
from app.schemas.users import User
from app.core.security import create_access_token, decode_token, hash_password, verify_password

router = APIRouter()
COOKIE_NAME = "access_token"

async def get_current_user(request: Request) -> User:
    """Get current authenticated user from JWT token."""
    # Get token from cookie or Authorization header
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user from database
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM test_users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="User not found")
            return User(id=row[0], name=row[1], email=row[2])

@router.post("/auth/register", response_model=User, status_code=201)
async def register(body: RegisterInput) -> User:
    """Register a new user account."""
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            
            # Check if email already exists
            cur.execute("SELECT 1 FROM test_users WHERE email = %s", (body.email,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="Email already registered")
            
            # Create user
            hashed_pw = hash_password(body.password)
            cur.execute(
                "INSERT INTO test_users (name, email, hashed_password) VALUES (%s, %s, %s) RETURNING id",
                (body.name, body.email, hashed_pw),
            )
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=500, detail="Failed to create user")
            user_id = result[0]
            conn.commit()
            return User(id=user_id, name=body.name, email=body.email)

@router.post("/auth/login", response_model=Token)
async def login(body: LoginInput, response: Response) -> Token:
    """Login and get JWT token."""
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, hashed_password FROM test_users WHERE email = %s",
                (body.email,),
            )
            row = cur.fetchone()
            if not row or not verify_password(body.password, row[3]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            token = create_access_token(subject=row[0])
            
            # Set cookie
            response.set_cookie(
                key=COOKIE_NAME,
                value=token,
                httponly=True,
                samesite="lax",
                secure=False,
                max_age=60 * 15,
            )
            return Token(access_token=token)

@router.get("/auth/me", response_model=User)
def me(user: User = Depends(get_current_user)) -> User:
    """Get current user info."""
    return user

@router.post("/auth/logout", status_code=204)
def logout(response: Response) -> None:
    """Logout by clearing cookie."""
    response.delete_cookie(COOKIE_NAME)