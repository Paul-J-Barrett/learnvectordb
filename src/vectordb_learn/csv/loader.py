"""CSV processing utilities."""

import csv
from pathlib import Path
from typing import Iterator
import asyncpg


def read_conversations(filepath: str) -> Iterator[dict]:
    """Read conversations from CSV file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def write_conversations(filepath: str, conversations: list[dict]) -> None:
    """Write conversations to CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'session_content'])
        writer.writeheader()
        writer.writerows(conversations)


async def load_csv(pool: asyncpg.Pool, filepath: str, batch_size: int = 10) -> int:
    """Ingest a CSV file into the database with embeddings."""
    from ..db.operations import create_schema, insert_conversation
    from ..embedding.ollama import get_embedding, generate_title

    await create_schema(pool)

    count = 0
    batch = []

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            username = row['username']
            content = row['session_content']
            batch.append((username, content))

            if len(batch) >= batch_size:
                for username, content in batch:
                    embedding = await get_embedding(content)
                    title = generate_title(content)
                    await insert_conversation(pool, username, content, embedding, title=title)
                    count += 1
                batch = []

    for username, content in batch:
        embedding = await get_embedding(content)
        title = generate_title(content)
        await insert_conversation(pool, username, content, embedding, title=title)
        count += 1

    return count
