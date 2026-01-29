#!/bin/bash
set -e

CONTAINER_NAME="postgres"

echo "Stopping PostgreSQL container..."

if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
	podman stop "$CONTAINER_NAME"
	echo "Container stopped: $CONTAINER_NAME"
else
	echo "Container $CONTAINER_NAME is not running"
fi

echo ""
echo "To start again: ./scripts/start-postgres.sh"
echo ""
echo "To remove all data (including volumes), run:"
echo "  podman volume rm pgvector_data"
