#!/usr/bin/env python3
"""Entry point for flashcard TUI application."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vectordb_learn.flashcards.main import run_flashcards


if __name__ == "__main__":
    csv_path = None
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    
    run_flashcards(csv_path)