#!/bin/bash
set -e

NETWORK="n8nnet"
CONTAINER_NAME="postgres"
IMAGE="pgvector/pgvector:pg17-bookworm"
DATA_VOLUME="pgvector_data"
SHM_SIZE="2g"
HOST_PORT="5432"

echo "=== PostgreSQL Vector Database Setup ==="
echo "Image: $IMAGE"
echo "Container: $CONTAINER_NAME"
echo "Network: $NETWORK"
echo ""

# Create network if not exists
if ! podman network inspect "$NETWORK" >/dev/null 2>&1; then
	echo "Creating network: $NETWORK"
	podman network create "$NETWORK"
else
	echo "Network $NETWORK already exists"
fi

# Create volume if not exists
if ! podman volume inspect "$DATA_VOLUME" >/dev/null 2>&1; then
	echo "Creating volume: $DATA_VOLUME"
	podman volume create "$DATA_VOLUME"
else
	echo "Volume $DATA_VOLUME already exists"
fi

# Stop and remove existing container
if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
	echo "Removing existing container: $CONTAINER_NAME"
	podman stop "$CONTAINER_NAME" 2>/dev/null || true
	podman rm "$CONTAINER_NAME"
fi

# Run new container
echo ""
echo "Starting PostgreSQL with pgvector..."
podman run -d \
	--name "$CONTAINER_NAME" \
	--network "$NETWORK" \
	-e POSTGRES_PASSWORD="learnvectordb" \
	-e POSTGRES_DB="vectordb" \
	-e POSTGRES_USER="postgres" \
	-p "${HOST_PORT}:5432" \
	-v "$DATA_VOLUME":/var/lib/postgresql/data \
	--shm-size="$SHM_SIZE" \
	--restart unless-stopped \
	"$IMAGE"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
for i in {1..60}; do
	if podman exec "$CONTAINER_NAME" pg_isready -U postgres >/dev/null 2>&1; then
		echo "PostgreSQL is ready!"
		break
	fi
	if [ $i -eq 60 ]; then
		echo "ERROR: PostgreSQL failed to start within 60 seconds"
		exit 1
	fi
	sleep 1
done

# Initialize pgvector extension
echo ""
echo "Enabling pgvector extension..."
podman exec "$CONTAINER_NAME" psql -U postgres -d vectordb -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Create the schema
echo "Creating schema..."
podman exec "$CONTAINER_NAME" psql -U postgres -d vectordb <<'EOF'
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    session_content TEXT NOT NULL,
    session_title TEXT,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_conversations_embedding 
ON conversations USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN index for full-text search comparison
CREATE INDEX IF NOT EXISTS idx_conversations_tsvector 
ON conversations USING gin (to_tsvector('english', session_content));
EOF

echo ""
echo "=== PostgreSQL Vector Database Started ==="
echo ""
echo "Connection Details:"
echo "  Host: localhost"
echo "  Port: ${HOST_PORT}"
echo "  Database: vectordb"
echo "  User: postgres"
echo "  Password: learnvectordb"
echo ""
echo "Connection String:"
echo "  postgresql://postgres:learnvectordb@localhost:${HOST_PORT}/vectordb"
echo ""
echo "=============================================="
echo "SECURITY WARNING: Change the default password!"
echo "=============================================="
echo ""
echo "To change the password, connect and run:"
echo "  ALTER USER postgres WITH PASSWORD 'your_secure_password';"
echo ""
echo "To connect with psql:"
echo "  podman exec -it $CONTAINER_NAME psql -U postgres -d vectordb"
echo ""
echo "To stop:"
echo "  ./scripts/stop-postgres.sh"
