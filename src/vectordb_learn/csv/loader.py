"""CSV processing utilities."""

import csv
from pathlib import Path
from typing import Iterator


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
