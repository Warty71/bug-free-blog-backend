from fastapi import APIRouter, status
from app.schemas.users import User
from app.core.database import get_db_connection

router = APIRouter()

@router.get("/users", response_model=list[User], status_code=status.HTTP_200_OK)
async def get_users() -> list[User]:
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM test_users")
            rows = cur.fetchall()
            for row in rows:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
            return [User(id=row[0], name=row[1], email=row[2]) for row in rows]

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User) -> User:
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO test_users (name, email) VALUES (%s, %s)", (user.name, user.email))
            conn.commit()
            return user

@router.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: User) -> User:
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE test_users SET name = %s, email = %s WHERE id = %s", (user.name, user.email, user_id))
            conn.commit()
            return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int) -> None:
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM test_users WHERE id = %s", (user_id,))
            conn.commit()
            return None

@router.patch("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def patch_user(user_id: int, user: User) -> User:
    async with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE test_users SET name = %s, email = %s WHERE id = %s", (user.name, user.email, user_id))
            conn.commit()
            return user