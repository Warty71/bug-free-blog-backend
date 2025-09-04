from fastapi import APIRouter, status
from app.schemas.users import User
import psycopg2
import os
CONNINFO = os.getenv("DATABASE_URL", "postgresql://merislihic@localhost:5432/learning_db")
 
router = APIRouter()

@router.get("/users", response_model=list[User], status_code=status.HTTP_200_OK)
async def get_users() -> list[User]:
    conn = psycopg2.connect(CONNINFO)
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_users")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
    conn.close()
    return [User(id=row[0], name=row[1], email=row[2]) for row in rows]

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User) -> User:
    conn = psycopg2.connect(CONNINFO)
    cur = conn.cursor()
    cur.execute("INSERT INTO test_users (name, email) VALUES (%s, %s)", (user.name, user.email))
    conn.commit()
    conn.close()
    return user