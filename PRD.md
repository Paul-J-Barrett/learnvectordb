# Product Requirement Document: Vector Database Learning Tool

## 1. Executive Summary

This project creates an educational tool for learning vector databases using PostgreSQL with pgvector. The system includes a synthetic CSV dataset of AI conversations about Python/PostgreSQL topics, a PostgreSQL vector store in Podman, and an interactive Textual TUI application for exploring vector operations. The tool uses local Ollama models for embeddings and OpenRouter API for advanced title generation, with OpenTelemetry instrumentation for observability.

## 2. Project Goals

- Learn vector database principles through hands-on experimentation
- Understand embedding generation, storage, and similarity search
- Practice SQL queries for vector operations (cosine distance, inner product, L2 distance)
- Explore performance characteristics of different indexing strategies
- Gain familiarity with pgvector capabilities and limitations

## 3. Technical Architecture

### 3.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Learning Tool Stack                          │
├─────────────────────────────────────────────────────────────────┤
│  TUI Layer         │ Textual App + Rich Output                  │
│                    │ - Interactive menus and forms               │
│                    │ - Beautiful table display                   │
│                    │ - Debug/sidebar panels                      │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer │ Python 3.13 (uv package manager)            │
│                    │ - pydantic-ai for LLM integration           │
│                    │ - asyncpg for PostgreSQL                    │
│                    │ - structlog for structured logging          │
├─────────────────────────────────────────────────────────────────┤
│  Embedding Layer   │ Ollama (local)                             │
│                    │ - nomic-embed-text: embeddings (384-dim)    │
│                    │ - phi4-mini: title generation               │
│                    │ - OpenRouter fallback (Minimax M2.1)        │
├─────────────────────────────────────────────────────────────────┤
│  Vector Store      │ PostgreSQL 17 + pgvector                    │
│                    │ - Podman container                          │
│                    │ - HNSW indexing                             │
│                    │ - Network: n8nnet                           │
├─────────────────────────────────────────────────────────────────┤
│  Observability     │ OpenTelemetry                               │
│                    │ - Tracing to Signoz (dockerhost:4318)       │
│                    │ - Structured logs                           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Database Schema

```sql
-- Main conversations table
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    session_content TEXT NOT NULL,
    session_title TEXT,
    embedding vector(384),  -- nomic-embed-text dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HNSW index for similarity search (created after data load)
CREATE INDEX ON conversations USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN index for full-text search (for comparison)
CREATE INDEX ON conversations USING gin (to_tsvector('english', session_content));
```

### 3.3 Embedding Strategy

**Primary (Local):** `nomic-embed-text` - 384 dimensions, ~274 MB
- Fast, no API costs, privacy-friendly
- Perfect for learning and testing

**Title Generation (Local):** `phi4-mini` - 2.5 GB
- Small enough for quick responses
- Generates concise conversation titles

**Fallback (Cloud):** OpenRouter API with `Minimax M2.1`
- Used when Ollama unavailable
- Higher quality titles when needed

## 4. Deliverables

### 4.1 CSV Dataset (100 rows)

**Format:** `username, session_content`

**Topics (Python/PostgreSQL focused):**
- Debugging Python exceptions and tracebacks
- SQL query optimization techniques
- Setting up PostgreSQL extensions
- Python async/await patterns
- Database migration strategies
- ORM vs raw SQL tradeoffs
- PostgreSQL indexing strategies
- Python type hints best practices
- Connection pooling in PostgreSQL
- PostgreSQL JSONB operations
- Python decorators and metaclasses
- ACID transactions and FastAPI database integration

### 4.2 Podman Container Setup

**Container Configuration:**

| Setting | Value |
|---------|-------|
| Image | `pgvector/pgvector:pg17-bookworm` |
| Container Name | `postgres` |
| Network | `n8nnet` |
| Port | 5432 |
| Volume | `pgvector_data` |
| Shared Memory | 2g |

**Default Credentials:**
- User: `postgres`
- Password: `learnvectordb` ⚠️ **CHANGE BEFORE PRODUCTION**

### 4.3 TUI Python Application

**Main Features:**

1. **Ingest CSV** - Load data into PostgreSQL with automatic embeddings
2. **Search** - Vector similarity search with explanations
3. **Explain Query** - Debug SQL & see execution plans
4. **Index Manager** - Create/compare HNSW/IVFFlat indexes
5. **SQL Playground** - Write custom queries
6. **Metrics** - View performance statistics

**Keyboard Shortcuts:**
- F1: Help
- F2: Toggle debug panel
- F3: Toggle SQL view
- Q/Esc: Quit

## 5. Dependencies

**Core Dependencies:**
- textual, rich - TUI framework
- asyncpg, psycopg2-binary - PostgreSQL drivers
- pydantic-ai, httpx - LLM integration
- ollama - Local embedding client
- opentelemetry-* - Observability
- structlog - Structured logging
- pandas - Data processing
- python-dotenv - Configuration

## 6. Setup Instructions

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Initialize and install
uv init vectordb-learn
cd vectordb-learn
uv sync

# 3. Start PostgreSQL
./scripts/start-postgres.sh

# 4. Generate CSV
python scripts/generate_conversations.py

# 5. Ingest data
uv run python -m vectordb_learn.db.ingest data/conversations.csv

# 6. Run TUI
uv run python -m vectordb_learn.app
```

## 7. Learning Objectives

After completing this project, you will understand:

1. **Vector Basics**
   - What embeddings are and how they're generated
   - Vector dimensions and their meaning
   - Cosine similarity vs Euclidean distance

2. **pgvector Operations**
   - Creating vector columns and tables
   - Inserting and querying vector data
   - Understanding distance operators: `<=>`, `<->`, `<#>`

3. **Indexing Strategies**
   - HNSW: Hierarchical Navigable Small World
   - IVFFlat: Inverted File Flat
   - Tradeoffs in speed vs recall

4. **Performance Tuning**
   - Query planning with EXPLAIN ANALYZE
   - Index usage analysis
   - Memory configuration for vector operations

## 8. Security Considerations

⚠️ **Default password must be changed for production use:**

```sql
ALTER USER postgres WITH PASSWORD 'your_secure_password';
```

## 9. Future Enhancements

- Support for different embedding models
- Filtered vector search with metadata
- RAG pipeline demonstration
- Jupyter notebook examples

## 10. Resources

- PGVector: https://github.com/pgvector/pgvector
- Textual: https://textual.textualize.io/
- uv: https://docs.astral.sh/uv/
- Ollama: https://ollama.com/
