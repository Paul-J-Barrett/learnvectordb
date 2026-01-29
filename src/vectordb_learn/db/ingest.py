#!/usr/bin/env python3
"""Ingest CSV data into PostgreSQL with automatic embedding generation."""

import asyncio
import csv
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
env_example_path = Path(__file__).parent.parent.parent / ".env.example"

if not env_path.exists() and env_example_path.exists():
    shutil.copy(env_example_path, env_path)
    print(f"Created .env from .env.example")

load_dotenv(env_path)

from vectordb_learn.db.connection import get_pool
from vectordb_learn.db.operations import create_schema, insert_conversation
from vectordb_learn.embedding.ollama import get_embedding


async def ingest_csv(filepath: str, batch_size: int = 10) -> int:
    """Ingest a CSV file into the database with embeddings."""
    pool = await get_pool()
    await create_schema(pool)
    
    count = 0
    batch = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            username = row['username']
            content = row['session_content']
            title = row.get('title')
            
            batch.append((username, content, title))
            
            if len(batch) >= batch_size:
                for username, content, title in batch:
                    print(f"\rGenerating embedding for record {count + 1}...", end="")
                    embedding = await get_embedding(content)
                    await insert_conversation(
                        pool, username, content, embedding, title=title
                    )
                    count += 1
                    print(f"\rInserted {count} conversations...", end="")
                    
                batch = []
    
    for username, content, title in batch:
        print(f"\rGenerating embedding for record {count + 1}...", end="")
        embedding = await get_embedding(content)
        await insert_conversation(pool, username, content, embedding, title=title)
        count += 1
        print(f"\rInserted {count} conversations...", end="")
    
    print(f"\nCompleted! Total: {count} conversations")
    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m vectordb_learn.db.ingest <csv_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    asyncio.run(ingest_csv(filepath))


if __name__ == "__main__":
    main()
