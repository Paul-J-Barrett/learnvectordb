"""Database connection pool management."""

import asyncpg
from ..config import postgres


_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=postgres.host,
            port=postgres.port,
            user=postgres.user,
            password=postgres.password,
            database=postgres.database,
            min_size=2,
            max_size=10,
            command_timeout=60.0,
        )
    return _pool


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def test_connection() -> bool:
    """Test if database connection is available."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception:
        return False