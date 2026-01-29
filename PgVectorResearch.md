# PostgreSQL + pgVector: A Learning Guide

pgVector is an extension that adds vector similarity search to PostgreSQL, enabling you to store embeddings and perform semantic search directly in your database.

---

## 1. What is pgVector?

pgVector is an open-source PostgreSQL extension (19.5K+ GitHub stars) that adds vector data types and similarity search operators.

### Supported Data Types

| Type | Description | Storage |
|------|-------------|---------|
| `vector(n)` | Standard float vectors | 4 bytes per dimension |
| `halfvec(n)` | Half-precision (16-bit) | 2 bytes per dimension |
| `bit(n)` | Binary vectors | Variable |
| `sparsevec(n)` | Sparse vectors with non-zero tracking | Variable |

### Distance Operators

pgVector provides specialized operators for comparing vectors:

| Operator | Name | Use Case |
|----------|------|----------|
| `<=>` | Cosine distance | Most common for text embeddings |
| `<->` | L2 (Euclidean) | Geometric distance |
| `<#>` | Negative inner product | Fastest for normalized vectors |
| `<+>` | L1 (Manhattan) | Taxicab distance |
| `<~>` | Hamming | Binary vectors |
| `<%>` | Jaccard | Binary similarity |

---

## 2. Docker Image Options

### Option 1: Official pgVector Images (Recommended)

**Image:** `pgvector/pgvector:pg17-bookworm`

```bash
docker pull pgvector/pgvector:pg17-bookworm
```

**Pros:**
- Maintained by pgVector team
- Full PostgreSQL compatibility
- Excellent documentation

**Cons:**
- Larger image size (~156 MB)

---

### Option 2: Alpine-Based (Minimal Footprint)

**Image:** `pgvector/pgvector:pg17-alpine`

```bash
docker pull pgvector/pgvector:pg17-alpine
```

**Pros:**
- ~70% smaller image
- Faster startup
- Lower resource usage

**Cons:**
- Limited extension compatibility

---

### Option 3: pgVector.rs (High Performance)

**Image:** `tensorchord/pgvecto-rs:pg17-v0.4.0`

```bash
docker pull tensorchord/pgvecto-rs:pg17-v0.4.0
```

**Pros:**
- Rust-based with SIMD optimization
- Up to 65K dimensions
- VBASE method for filtered search

**Cons:**
- Different API from pgVector
- Less mature

---

## 3. Quick Start

### Run PostgreSQL with pgVector

```bash
docker run --name pgvector \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=vectordb \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  --shm-size=2g \
  -d pgvector/pgvector:pg17-bookworm
```

### Enable the Extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 4. Creating Vector Tables

### Basic Table Structure

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    embedding vector(768),  -- Match your embedding model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Insert Data

```sql
INSERT INTO documents (title, content, embedding)
VALUES (
    'Introduction to Vector Databases',
    'A comprehensive guide...',
    '[0.1, 0.2, 0.3, ...]'  -- 768 dimensions
);
```

---

## 5. Vector Indexes

Choosing the right index type is critical for performance.

### HNSW Index (Recommended)

Hierarchical Navigable Small World provides excellent query speed.

```sql
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Characteristics:**
- Fast queries, higher memory usage
- Best for production with 100K+ vectors
- Adjust `m` and `ef_construction` for speed/recall tradeoff

---

### IVFFlat Index

Inverted File Flat offers faster builds with slightly slower queries.

```sql
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Characteristics:**
- Faster build time
- Lower memory usage
- Best for 10K-1M vectors

---

## 6. Similarity Search

### Cosine Similarity Search

```sql
SELECT id, title,
       embedding <=> '[0.1, 0.2, 0.3, ...]' AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, 0.3, ...]'
LIMIT 10;
```

### With Similarity Score

```sql
SELECT id, title,
       1 - (embedding <=> '[0.1, 0.2, 0.3, ...]') AS similarity
FROM documents
WHERE embedding <=> '[0.1, 0.2, 0.3, ...]' < 0.5
ORDER BY similarity DESC
LIMIT 10;
```

---

## 7. Performance Tuning

### Critical Settings

```sql
-- Increase for faster index building
SET maintenance_work_mem = '1GB';

-- Set effective search parameters
SET hnsw.ef_search = 100;
```

### Docker Shared Memory

```bash
docker run --shm-size=4g ...
```

### Memory Configuration Guidelines

| Setting | Recommendation |
|---------|---------------|
| `shared_buffers` | 25% of system RAM |
| `effective_cache_size` | 75% of system RAM |
| `maintenance_work_mem` | 512MB-1GB for indexing |
| `work_mem` | 64MB per operation |

---

## 8. Query Analysis

### Check Execution Plan

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM documents
ORDER BY embedding <=> '[0.1, 0.2, 0.3, ...]'
LIMIT 10;
```

### Monitor Index Usage

```sql
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%hnsw%' OR indexrelname LIKE '%ivfflat%';
```

---

## 9. Storage Optimization

### Half-Precision Vectors

```sql
CREATE TABLE large_embeddings (
    embedding halfvec(1536)  -- 50% storage reduction
);
```

### Binary Quantization

```sql
CREATE INDEX ON embeddings
USING hnsw ((binary_quantize(embedding)::bit(1536)) bit_hamming_ops);
```

---

## 10. Summary

| Use Case | Recommendation |
|----------|---------------|
| Production | `pgvector/pgvector:pg17-bookworm` + HNSW |
| Development | `pgvector/pgvector:pg17-alpine` |
| High dimensions | `tensorchord/pgvecto-rs:pg17` |

**Key Takeaways:**
1. Use cosine distance (`<=>`) for text embeddings
2. HNSW indexes for production workloads
3. Allocate sufficient shared memory for indexes
4. Match vector dimensions to your embedding model

---

## Resources

- **pgVector GitHub:** https://github.com/pgvector/pgvector
- **pgVector Docs:** https://github.com/pgvector/pgvector/tree/master/docs
