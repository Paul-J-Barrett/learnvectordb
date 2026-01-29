# Vector Database Learning Tool

An educational project for learning PostgreSQL with pgvector through hands-on experimentation. Uses ollama and OpenRouter for generating embeddings and titles from conversation content.

## Building Notes
This application was built using opencoder and the model MiniMax M2.1. If you have any issues with any component please try to fix and make a PR. Also the generic conversations in the conversations.csv file are just random text they are not meant to be real users, and sessions data. I was building this to understand how I could add chat conversations to a database and then search that database as memory similar to how ChatGPT stores your conversation history to add to new chat sessions.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Paul-J-Barrett/learnvectordb.git
cd learnvectordb

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Start PostgreSQL with pgvector
./scripts/start-postgres.sh

# Generate sample conversations CSV
uv run python scripts/generate_conversations.py

# Ingest CSV into database
uv run python -m vectordb_learn.db.ingest data/conversations.csv

# Run the TUI application
uv run python -m vectordb_learn.app

# Start psql interactively
podman exec -it postgres psql -U postgres -d vectordb
```

## Available Entry Points

| Entry Point | Description |
|-------------|-------------|
| `uv run python -m vectordb_learn.app` | Main TUI application |
| `uv run python -m vectordb_learn.flashcards.main` | Flashcards TUI |
| `uv run python -m vectordb_learn.flashcards.generator` | Generate flashcards using OpenRouter |
| `uv run python -m vectordb_learn.db.ingest <csv>` | Ingest CSV data into database |

## Script Reference

| Script | Description |
|--------|-------------|
| `./scripts/start-postgres.sh` | Start PostgreSQL with pgvector in a Podman container |
| `./scripts/stop-postgres.sh` | Stop the PostgreSQL container |
| `uv run python scripts/generate_conversations.py` | Generate synthetic conversation dataset |
| `uv run python scripts/run_flashcards.py [csv]` | Run flashcards TUI (optional CSV path) |

## Features

- **CSV Ingestion**: Load conversation data with automatic embedding generation
- **Vector Search**: Search using cosine similarity with explanatory output
- **Query Debug Panel**: See raw SQL, execution plans, and performance metrics
- **Index Manager**: Create and compare HNSW and IVFFlat indexes
- **SQL Playground**: Write and execute custom queries
- **Full Observability**: OpenTelemetry tracing to Signoz
- **Flashcards**: Interactive Q&A for learning vector database concepts

## Flashcards Module

Interactive flashcards covering pgvector, Ollama, OpenRouter, pydantic-ai, PostgreSQL, embeddings, and AI concepts.

### Run Flashcards

```bash
# Run the flashcards TUI
uv run python -m vectordb_learn.flashcards.main

# Or use the script
uv run python scripts/run_flashcards.py
```

### Generate New Flashcards

Requires `OPENROUTER_API_KEY` in `.env`:

```bash
# Generate 400 flashcards using OpenRouter (Minimax M2.1)
uv run python -m vectordb_learn.flashcards.generator
```

### Flashcard Topics

- pgVector operators, indexes, and data types
- Ollama Python library usage
- OpenRouter API integration
- pydantic-ai framework
- asyncpg and psycopg2 PostgreSQL clients
- AI embeddings and vector databases
- PostgreSQL concepts and SQL

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Show answer / Mark correct |
| `R` | Random card |
| `S` | Shuffle deck |
| `Escape` | Exit |

## Project Structure

```
learnvectordb/
├── scripts/
│   ├── start-postgres.sh    # Podman container setup
│   ├── generate_conversations.py
├── src/vectordb_learn/
│   ├── app.py              # Main TUI application
│   ├── db/                 # Database operations
│   ├── embedding/          # Ollama/OpenRouter clients
│   └── ui/                 # Textual screens and widgets
└── data/                   # CSV data files
```

## Learning Topics

This tool covers:
- Vector embeddings and similarity search
- pgvector operators and indexes
- Query optimization and EXPLAIN ANALYZE
- HNSW vs IVFFlat indexing strategies
- Hybrid search combining vectors and full-text search

## Requirements

- Python 3.13+
- Podman (or Docker)
- Ollama running locally
- Access to OpenRouter API (optional, for fallback)

## Some Example SQL Queries

Fetch 1 conversation:

```sql
SELECT id, username, session_title, embedding, LEFT(session_content, 200) as preview
FROM conversations
ORDER BY id ASC
LIMIT 1;
```

## UV Quick Reference

| Command | Description |
|---------|-------------|
| `uv sync` | Install exact versions from lock file |
| `uv lock` | Create reproducible lock file |
| `uv run python <script>` | Run script with project dependencies |
| `uv add <package>` | Add a dependency |
| `uv add --dev <package>` | Add a dev dependency |

## License

MIT