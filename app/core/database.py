"""
Database connection pool management.

This module provides database connection pooling functionality
for the entire application. It's part of the core infrastructure.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import psycopg
from psycopg_pool import ConnectionPool

# Database configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://merislihic@localhost:5432/learning_db")

# Global connection pool (lazy initialization)
_connection_pool = None

def get_connection_pool():
    """
    Get the connection pool, creating it if it doesn't exist.
    
    This uses lazy initialization - the pool is only created
    when first needed, not at import time.
    """
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(
            DATABASE_URL,
            min_size=1,
            max_size=10,    
        )
    return _connection_pool

@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[psycopg.Connection, None]:
    """
    Context manager for getting a database connection from the pool.
    
    Usage:
        async with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")
                results = cur.fetchall()
    
    The connection is automatically returned to the pool when the
    context manager exits.
    """
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def close_connection_pool():
    """
    Close all connections in the pool.
    
    This should be called when the application shuts down
    to properly clean up resources.
    """
    global _connection_pool
    if _connection_pool:
        print("🔒 Closing all connections in pool...")
        _connection_pool.close()
        _connection_pool = None
        print("✅ All connections closed")