"""Vector database operations using pgvector."""

import asyncpg
from typing import Optional
from ..config import postgres


async def create_schema(pool: asyncpg.Pool) -> None:
    """Create the conversations table with pgvector extension."""
    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id BIGSERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                session_content TEXT NOT NULL,
                session_title TEXT,
                embedding vector(768),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_embedding 
            ON conversations USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """)


async def insert_conversation(
    pool: asyncpg.Pool,
    username: str,
    content: str,
    embedding: list[float],
    title: Optional[str] = None,
) -> int:
    """Insert a conversation with its embedding."""
    async with pool.acquire() as conn:
        embedding_str = "[" + ", ".join(str(x) for x in embedding) + "]"
        return await conn.fetchval(
            """
            INSERT INTO conversations (username, session_content, session_title, embedding)
            VALUES ($1, $2, $3, $4::vector)
            RETURNING id
            """,
            username, content, title, embedding_str,
        )


async def search_similar(
    pool: asyncpg.Pool,
    query_embedding: list[float],
    limit: int = 10,
) -> list[dict]:
    """Search for similar conversations using cosine distance."""
    embedding_str = "[" + ", ".join(str(x) for x in query_embedding) + "]"
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, username, session_content, session_title,
                   embedding <=> $1::vector AS distance
            FROM conversations
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            embedding_str, limit,
        )
        return [dict(row) for row in rows]


async def search_combined(
    pool: asyncpg.Pool,
    query_embedding: list[float],
    search_text: str,
    limit: int = 10,
) -> list[dict]:
    """Search using both vector similarity and full-text search."""
    embedding_str = "[" + ", ".join(str(x) for x in query_embedding) + "]"
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, username, session_content, session_title,
                   embedding <=> $1::vector AS distance,
                    ts_rank(to_tsvector('english', session_content), 
                            plainto_tsquery('english', $2)) AS rank
            FROM conversations
            WHERE to_tsvector('english', session_content) @@ plainto_tsquery('english', $2)
               OR embedding <=> $1::vector < 0.5
            ORDER BY rank DESC, embedding <=> $1::vector ASC
            LIMIT $3
            """,
            embedding_str, search_text, limit,
        )
        return [dict(row) for row in rows]


async def get_schema_stats(pool: asyncpg.Pool) -> dict:
    """Get database statistics."""
    async with pool.acquire() as conn:
        row_count = await conn.fetchval("SELECT COUNT(*) FROM conversations")
        index_info = await conn.fetch(
            """
            SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes WHERE tablename = 'conversations'
            """
        )
        return {
            "row_count": row_count,
            "indexes": [dict(row) for row in index_info],
        }


async def create_hnsw_index(pool: asyncpg.Pool, metric: str = "cosine") -> str:
    """Create an HNSW index for vector search."""
    async with pool.acquire() as conn:
        op = {"cosine": "vector_cosine_ops", "inner": "vector_ip_ops", "l2": "vector_l2_ops"}
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_conversations_hnsw 
            ON conversations USING hnsw (embedding {op.get(metric, 'vector_cosine_ops')})
            WITH (m = 16, ef_construction = 64)
        """)
        return f"HNSW index created with {metric} distance"


async def create_ivfflat_index(pool: asyncpg.Pool, lists: int = 10) -> str:
    """Create an IVFFlat index for vector search."""
    async with pool.acquire() as conn:
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_conversations_ivfflat 
            ON conversations USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = {lists})
        """)
        return f"IVFFlat index created with {lists} lists"


async def drop_indexes(pool: asyncpg.Pool) -> str:
    """Drop all vector indexes."""
    async with pool.acquire() as conn:
        await conn.execute("""
            DROP INDEX IF EXISTS idx_conversations_embedding,
                               idx_conversations_hnsw,
                               idx_conversations_ivfflat
        """)
        return "All vector indexes dropped"


async def explain_query(
    pool: asyncpg.Pool,
    query: str,
) -> str:
    """Get EXPLAIN ANALYZE output for a query."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {query}")
            return "\n".join(str(row[0]) for row in rows)
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"