# PostgreSQL + pgvector Research

## PGVector Extension Overview

### What is PGVector?

**PGVector** is an open-source PostgreSQL extension that adds vector similarity search 
capabilities to PostgreSQL. It is the most widely-used and mature vector extension for 
PostgreSQL, with **19,500+ stars** on GitHub and active maintenance since its creation.

### Key Features of PGVector

**Vector Data Types:**
- `vector(n)` - Standard vectors with up to 16,000 dimensions (recommended: up to 2,000 for indexing)
- `halfvec(n)` - Half-precision (16-bit) floating-point vectors, reducing storage by 50%
- `bit(n)` - Binary vectors for Hamming and Jaccard distance operations
- `sparsevec(n)` - Sparse vectors with non-zero element tracking

**Distance Functions and Operators:**
- `<->` - L2 (Euclidean) distance
- `<#>` - Negative inner product (use `-embedding <#> query` for actual inner product)
- `<=>` - Cosine distance
- `<+>` - L1 (Manhattan/taxicab) distance
- `<~>` - Hamming distance (for binary vectors)
- `<%>` - Jaccard distance (for binary vectors)

**Advanced Features:**
- Exact nearest neighbor search (perfect recall)
- Approximate nearest neighbor (ANN) search with HNSW and IVFFlat indexes
- Vector aggregation functions (AVG, SUM)
- Binary quantization for memory-efficient indexing
- Iterative index scans for improved filtered queries

### How PGVector Works

PGVector integrates seamlessly with PostgreSQL by:
1. Storing vector data in a custom, memory-efficient binary format
2. Leveraging PostgreSQL's index infrastructure for approximate search algorithms
3. Supporting ACID compliance and write-ahead logging (WAL)
4. Utilizing PostgreSQL's query planner and executor for optimal query execution

The extension is written in C for performance and supports PostgreSQL 13 through 18 (current versions).

---

## 2. Official PGVector Docker Images

### Official Docker Hub Repository

**Primary Repository:** `docker.io/pgvector/pgvector`

The official PGVector project maintains Docker images that combine PostgreSQL with pgvector extension pre-installed. These images are based on the official PostgreSQL Docker images with pgvector added.

### Available Tags and Versions

The official images support multiple PostgreSQL versions and base operating systems:

**PostgreSQL 17:**
- `pgvector/pgvector:pg17-trixie` - Debian Trixie base
- `pgvector/pgvector:pg17-bookworm` - Debian Bookworm base
- `pgvector/pgvector:pg17-alpine` - Alpine Linux base

**PostgreSQL 16:**
- `pgvector/pgvector:pg16-bookworm`
- `pgvector/pgvector:pg16-alpine`
- `pgvector/pgvector:pg16` - Default tag

**PostgreSQL 15:**
- `pgvector/pgvector:pg15-bookworm`
- `pgvector/pgvector:pg15-alpine`

### Pull Command

```bash
# Recommended: Use specific version tags for production
docker pull pgvector/pgvector:pg17-bookworm

# Or use the default tag
docker pull pgvector/pgvector:pg17
```

---

## 3. Alternative Vector Extensions for PostgreSQL

### PGVector.rs (VectorChord)

**Repository:** `github.com/tensorchord/pgvecto.rs` (2,100 stars)

An alternative extension written in Rust that offers several advantages over PGVector:

**Key Advantages:**
- **Higher dimensional support:** Up to 65,535 dimensions (vs. PGVector's 2,000)
- **SIMD optimization:** Dynamic runtime SIMD dispatch for better performance
- **Additional data types:** FP16 (16-bit), INT8 (8-bit integer), and binary vectors
- **VBASE method:** Improved filtering with vector search and relational queries
- **Separate index storage:** Better memory management for large indexes

**Docker Image:** `tensorchord/pgvecto-rs:pg16-v0.2.1` (GHCR also available)

```bash
docker pull tensorchord/pgvecto-rs:pg17-v0.4.0
```

### pgai (Timescale)

**Repository:** `github.com/timescale/pgai` (5,600 stars)

While not a vector extension itself, pgai is a comprehensive AI toolkit for PostgreSQL that works with pgvector:

**Features:**
- Automatic embedding creation and synchronization
- Vectorizer workers for continuous embedding updates
- Semantic catalog for natural language to SQL translation
- Integration with multiple LLM providers (OpenAI, Ollama, Cohere, etc.)
- Production-ready error handling for embedding services

---

## 4. Docker Image Comparison and Recommendations

### Comparison of Top 3 Docker Image Options

#### Option 1: Official PGVector Images

**Image:** `pgvector/pgvector:pg17-bookworm`

**Pros:**
- **Official project support:** Maintained by the pgvector team
- **Maximum compatibility:** Works exactly like standard PostgreSQL
- **Multi-platform support:** amd64, arm64, and other architectures
- **Regular updates:** Aligned with PostgreSQL release cycle
- **Well-documented:** Extensive documentation and community support
- **ACID compliant:** Full PostgreSQL reliability and WAL support

**Cons:**
- **Image size:** Larger than Alpine variants (~156 MB for bookworm)
- **Fewer advanced features:** No SIMD dispatch or extreme dimensional support

**Best For:** Production deployments requiring stability and long-term support

```yaml
# Example docker-compose.yml
services:
  pgvector:
    image: pgvector/pgvector:pg17-bookworm
    environment:
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: vector_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    shm_size: 1g  # Important for HNSW index builds
```

#### Option 2: Alpine-Based PGVector Images

**Image:** `pgvector/pgvector:pg17-alpine`

**Pros:**
- **Minimal image size:** ~60-70% smaller than Debian variants
- **Faster container startup**
- **Lower resource footprint**
- **Security benefits:** Smaller attack surface

**Cons:**
- **Missing libraries:** Some PostgreSQL extensions may require compilation
- **Locale limitations:** Limited locale support compared to Debian
- **Binary compatibility:** May encounter issues with some C extensions

**Best For:** Development environments, resource-constrained deployments, CI/CD pipelines

```bash
docker pull pgvector/pgvector:pg17-alpine
```

#### Option 3: PGVector.rs (VectorChord) Images

**Image:** `tensorchord/pgvecto-rs:pg17-v0.4.0`

**Pros:**
- **Higher performance:** Rust-based with SIMD optimizations
- **Greater dimensional capacity:** Up to 65,535 dimensions
- **Better filtered search:** VBASE method for combined vector-relational queries
- **Memory efficiency:** Separate index storage management

**Cons:**
- **Less mature:** Fewer production deployments and community resources
- **Different API:** Some SQL syntax differences from pgvector
- **WAL limitations:** Index WAL support still in development
- **Migration complexity:** May require migration from pgvector

**Best For:** High-dimensional embedding use cases, performance-critical applications with advanced filtering requirements

```bash
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg17-v0.4.0
```

### Recommendation Matrix

| Use Case | Recommended Image | Rationale |
|----------|-------------------|-----------|
| **Production Enterprise** | `pgvector/pgvector:pg17-bookworm` | Stability, support, compatibility |
| **Development/Testing** | `pgvector/pgvector:pg17-alpine` | Speed, resource efficiency |
| **High-Dimensional Vectors** | `tensorchord/pgvecto-rs:pg17-v0.4.0` | 65K dimension support |
| **Resource-Constrained** | `pgvector/pgvector:pg17-alpine` | Minimal footprint |
| **AI/RAG Pipeline** | `pgvector/pgvector:pg17` + `pgai` | Automated embedding management |

---

## 5. Setting Up PostgreSQL with PGVector

### Quick Start with Docker

```bash
# Pull and run the official pgvector image
docker pull pgvector/pgvector:pg17-bookworm

# Run the container
docker run --name pgvector \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=vector_db \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  --shm-size=1g \
  -d pgvector/pgvector:pg17-bookworm

# Connect to the database
psql -h localhost -p 5432 -U postgres -d vector_db
```

### Database Setup and Extension Installation

```sql
-- Enable the vector extension (run once per database)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check available functions
\df *vector*
```

### Creating Vector Tables

```sql
-- Basic vector table (1536 dimensions for OpenAI embeddings)
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    embedding vector(1536),  -- Standard embedding dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW index for fast approximate search
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- Alternative: IVFFlat index (faster build, slightly slower queries)
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

### Vector Operations

```sql
-- Insert vectors
INSERT INTO documents (title, content, embedding)
VALUES (
    'Introduction to Vector Databases',
    'A comprehensive guide...',
    '[0.1, 0.2, 0.3, ...]'  -- 1536 dimensions
);

-- Exact nearest neighbor search
SELECT id, title, embedding <=> '[0.1, 0.2, 0.3, ...]' AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, 0.3, ...]'
LIMIT 10;

-- Similarity search with threshold
SELECT id, title, 1 - (embedding <=> '[0.1, 0.2, 0.3, ...]') AS similarity
FROM documents
WHERE embedding <=> '[0.1, 0.2, 0.3, ...]' < 0.5
ORDER BY similarity DESC
LIMIT 10;

-- Inner product (fastest for normalized vectors)
SELECT * FROM documents
ORDER BY embedding <#> '[0.1, 0.2, 0.3, ...]'
LIMIT 10;
```

---

## 6. Performance Considerations

### Memory Configuration

**Critical Setting for HNSW Indexes:**
```sql
-- Check current settings
SHOW maintenance_work_mem;

-- Increase for faster index building (run before CREATE INDEX)
SET maintenance_work_mem = '1GB';

-- For large datasets, increase shared memory
docker run --shm-size=4g ...
```

**Recommended PostgreSQL Settings:**
```sql
-- Add to postgresql.conf or docker command
shared_buffers = '1GB'              -- 25% of system RAM
effective_cache_size = '2GB'        -- 75% of system RAM
maintenance_work_mem = '512MB'      -- For index builds
work_mem = '64MB'                   -- For query operations
max_parallel_workers_per_gather = 4 -- Parallel query support
```

### Index Selection Guidelines

**HNSW (Hierarchical Navigable Small World):**
```sql
CREATE INDEX ON table_name USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Characteristics:**
- **Best for:** Production workloads with large datasets (100K+ vectors)
- **Query speed:** Faster queries at same recall level vs IVFFlat
- **Build time:** Slower, more memory-intensive
- **Memory usage:** Higher than IVFFlat
- **Recall:** Higher at equivalent speed

**Parameters:**
- `m`: Connections per layer (default: 16, increase for higher recall)
- `ef_construction`: Index build quality (default: 64, increase for better recall)

**IVFFlat (Inverted File Flat):**
```sql
CREATE INDEX ON table_name USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Characteristics:**
- **Best for:** Datasets with 10K-1M vectors, faster builds needed
- **Query speed:** Slower than HNSW at same recall
- **Build time:** Faster, less memory
- **Memory usage:** Lower than HNSW
- **Recall:** Depends heavily on lists/probes configuration

**Parameters:**
- `lists`: Number of inverted lists (rows/1000 for <1M, sqrt(rows) for >1M)
- `probes`: Query-time probes (sqrt(lists) is good starting point)

### Query Optimization

```sql
-- Set effective search parameters
SET hnsw.ef_search = 100;  -- Increase for higher recall

-- Use iterative scans for filtered queries (pgvector 0.8.0+)
SET hnsw.iterative_scan = strict_order;

-- Check query execution plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM documents
ORDER BY embedding <=> '[0.1, 0.2, 0.3, ...]'
LIMIT 10;

-- Monitor index usage
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%hnsw%' OR indexrelname LIKE '%ivfflat%';
```

### Performance Monitoring

```sql
-- Enable pg_stat_statements for query analysis
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow vector queries
SELECT query, 
       round(total_exec_time) as exec_time_ms,
       calls,
       round(total_exec_time / calls) as avg_time_ms
FROM pg_stat_statements
WHERE query ILIKE '%<->%' OR query ILIKE '%<#%>%' OR query ILIKE '%<=>%'
ORDER BY total_exec_time DESC
LIMIT 10;

-- Check index size
SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) as size
FROM pg_indexes
WHERE tablename = 'documents';
```

---

## 7. Summary and Recommendations

### For New Projects

**Primary Recommendation:**
```bash
# Use official pgvector image for stability
docker pull pgvector/pgvector:pg17-bookworm
```

**Rationale:**
- Most mature and tested solution
- Extensive documentation and community support
- Full PostgreSQL compatibility
- Regular updates and security patches

### Key Takeaways

1. **PGVector is the industry standard** for PostgreSQL vector search with 19.5K GitHub stars and proven production deployments

2. **Official Docker images** (`pgvector/pgvector`) provide the most reliable and well-tested setup

3. **HNSW indexes** are recommended for most production use cases due to better speed-recall tradeoff

4. **Memory configuration is critical** - set `maintenance_work_mem` appropriately and allocate sufficient shared memory

5. **Consider alternatives** only if you have specific requirements (high dimensions, advanced filtering) that pgvector cannot meet

---

## Resources

- **PGVector GitHub:** https://github.com/pgvector/pgvector
- **PGVector Documentation:** https://github.com/pgvector/pgvector/tree/master/docs
- **Official Docker Hub:** https://hub.docker.com/r/pgvector/pgvector
- **PGVector.rs (Alternative):** https://github.com/tensorchord/pgvecto.rs
- **pgai (Timescale):** https://github.com/timescale/pgai
