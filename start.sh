#!/bin/bash
#
# SOAR Platform Start Script
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  SOAR Platform - Starting Services"
echo "=========================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
    
    echo ""
    echo "Please edit .env with your configuration:"
    echo "  - POSTGRES_PASSWORD"
    echo "  - SOAR_API_SECRET"
    echo "  - CORS_ORIGINS"
    echo ""
    echo "For now, continuing with default values..."
    echo ""
fi

# Pull images
echo ""
echo "Pulling Docker images..."
docker compose pull

# Build images
echo ""
echo "Building Docker images..."
docker compose build

# Start services
echo ""
echo "Starting services..."
docker compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to become healthy..."
sleep 15

# Check health
echo ""
echo "Checking backend health..."
if docker compose exec -T backend curl -sf http://localhost:8000/health 2>/dev/null; then
    echo "✓ Backend is healthy"
else
    echo "⚠ Backend may need a moment to start"
    echo ""
    echo "Showing backend logs..."
    docker compose logs backend --tail 20
fi

# Show status
echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="
docker compose ps

echo ""
echo "=========================================="
echo "  SOAR Platform Ready"
echo "=========================================="
echo ""
echo "Endpoints:"
echo "  - Backend API:   http://localhost:8000"
echo "  - API Docs:      http://localhost:8000/docs"
echo "  - Health Check:  http://localhost:8000/health"
echo ""
echo "If AI/LLM is enabled:"
echo "  - LLM Endpoint:  ${LLM_ENDPOINT:-http://host.docker.internal:11434}"
echo ""
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Initialize database:"
echo "     docker compose exec backend python init_db.py"
echo ""
echo "  2. Configure integrations in database:"
echo "     SELECT * FROM integration_configs;"
echo ""
echo "  3. Create playbooks:"
echo "     INSERT INTO playbooks (name, slug, yaml_content, ..."
echo ""
echo "=========================================="
