"""Database operations for PostgreSQL with pgvector."""

from .connection import get_pool, close_pool
from .operations import (
    create_schema,
    insert_conversation,
    search_similar,
    get_schema_stats,
    create_hnsw_index,
    create_ivfflat_index,
    drop_indexes,
    explain_query,
)

__all__ = [
    "get_pool",
    "close_pool",
    "create_schema",
    "insert_conversation",
    "search_similar",
    "get_schema_stats",
    "create_hnsw_index",
    "create_ivfflat_index",
    "drop_indexes",
    "explain_query",
]