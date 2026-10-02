# Setup Guide

This guide walks you through setting up the AI-Native SOAR platform from scratch.

## Prerequisites

### Required Software

- **Docker** 24.0+
- **Docker Compose** 2.20+
- **Python** 3.11+ (for local development)
- **Git** (for version control)

### Verify Installation

```bash
# Check Docker
docker --version
# Expected: Docker version 24.x.x

# Check Docker Compose
docker compose version
# Expected: Docker Compose version 2.x.x

# Check Python (optional, for local dev)
python --version
# Expected: Python 3.11.x or higher
```

## Initial Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ai-native-soar
```

### Step 2: Review Documentation

Before starting, read these files:

- [README.md](README.md) - Project overview and quick start
- [SECURITY.md](SECURITY.md) - Security guidelines and best practices
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture details
- [docs/database-schema.md](backend/docs/database-schema.md) - Database schema
- [docs/api-reference.md](backend/docs/api-reference.md) - API reference

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

#### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL admin password | `SecureP@ssw0rd!` |
| `SOAR_API_SECRET` | API secret key | `your_api_secret_here` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `LLM_ENDPOINT` | Local LLM endpoint (optional) | `http://localhost:11434` |

#### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_MODEL` | LLM model to use | `qwen3.5:9b` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `DATABASE_URL` | PostgreSQL connection string | Auto-generated |

### Step 4: Start the Platform

```bash
# Run the start script
./start.sh
```

#### What the Start Script Does

1. Checks for `.env` file
2. Creates `.env` from `.env.example` if needed
3. Pulls Docker images
4. Builds backend images
5. Starts all services
6. Waits for services to become healthy
7. Displays service status

#### Expected Output

```
==========================================
  SOAR Platform - Starting Services
==========================================

Pulling Docker images...
Using cache

Building Docker images...
backend

Starting services...

Waiting for services to become healthy...

Checking backend health...
✓ Backend is healthy

==========================================
  Service Status
==========================================
NAME                       STATE                  STATUS
backend                    Up                    healthy
database                   Up                    healthy
redis                      Up                    healthy
...

==========================================
  SOAR Platform Ready
==========================================

Endpoints:
  - Backend API:   http://localhost:8000
  - API Docs:      http://localhost:8000/docs
  - Health Check:  http://localhost:8000/health
```

### Step 5: Initialize Database

```bash
# Initialize database and create default data
docker compose exec backend python init_db.py
```

#### What init_db.py Does

1. Creates default admin user:
   - Username: `admin`
   - Password: `admin`
   - **Change this immediately after first login!**

2. Creates default integration configurations:
   - VirusTotal
   - ThreatCrowd
   - Shodan
   - CrowdStrike

3. Sets up default roles and permissions

4. Inserts sample playbooks (optional)

#### Verify Database Initialization

```bash
# Check users
docker compose exec backend python -c "from models.database import get_db; from models.models import User; db = get_db(); print([u.username for u in db.query(User).all()])"

# Check integrations
docker compose exec -T database psql -U soar_user -d soar -c "SELECT integration_name, enabled FROM integration_configs;"

# Check playbooks
docker compose exec -T database psql -U soar_user -d soar -c "SELECT name, enabled FROM playbooks;"
```

### Step 6: Access the Platform

#### Backend API

- **URL**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`
- **Health**: `http://localhost:8000/health`

Test with curl:

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "SOAR Platform"}
```

#### Frontend

- **URL**: `http://localhost:3000`
- **Build**: `docker compose exec frontend npm run build`
- **Dev**: `docker compose exec frontend npm run dev`

### Step 7: Configure Integrations

#### Option 1: Via Database (Quick Start)

```bash
docker compose exec -T database psql -U soar_user -d soar <<EOF

-- VirusTotal
UPDATE integration_configs 
SET configuration = '{"api_key": "YOUR_VT_API_KEY"}'
WHERE integration_name = 'virustotal';

-- ThreatCrowd
UPDATE integration_configs 
SET configuration = '{"api_key": "YOUR_THREATCROWD_API_KEY"}'
WHERE integration_name = 'threatcrowd';

-- Shodan
UPDATE integration_configs 
SET configuration = '{"api_key": "YOUR_SHODAN_API_KEY"}'
WHERE integration_name = 'shodan';

-- CrowdStrike (requires additional setup)
-- UPDATE integration_configs 
-- SET configuration = '{"client_id": "...", "client_secret": "..."}'
-- WHERE integration_name = 'crowdstrike';
EOF
```

#### Option 2: Via API (Recommended)

Use the Swagger UI at `http://localhost:8000/docs`:

1. Login with admin credentials
2. Navigate to Integrations endpoint
3. Update configurations via API
4. Verify integrations work

Example API call:

```bash
curl -X PATCH http://localhost:8000/api/v1/integrations/virustotal \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d '{
    "configuration": {
      "api_key": "YOUR_VT_API_KEY"
    }
  }'
```

### Step 8: Verify Setup

#### 1. Check All Services Running

```bash
docker compose ps
```

Expected output:

```
NAME          STATUS
backend       Up (healthy)
database      Up (healthy)
redis         Up (healthy)
```

#### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List incidents
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/incidents/

# Create test incident
curl -X POST http://localhost:8000/api/v1/incidents/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Test Incident",
    "severity": "high"
  }'
```

#### 3. Test Integration

```bash
# Test VirusTotal lookup
curl -X POST http://localhost:8000/api/v1/integrations/virustotal \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "action": "lookup_ip",
    "input": {
      "ip_address": "8.8.8.8"
    }
  }'
```

## Common Issues and Solutions

### Issue 1: Port Conflicts

**Problem**: Port 5432, 6379, or 8000 already in use

**Solution**: Edit `docker-compose.yml` to use different ports:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Use 8001 instead of 8000
```

### Issue 2: Database Connection Failures

**Problem**: Backend cannot connect to PostgreSQL

**Solution**:

1. Check PostgreSQL logs:
   ```bash
   docker compose logs database
   ```

2. Verify credentials in `.env`:
   ```bash
   POSTGRES_PASSWORD=your_secure_password_here
   DATABASE_URL=postgresql://soar_user:soar_password@database:5432/soar
   ```

3. Restart services:
   ```bash
   docker compose restart
   ```

### Issue 3: LLM Connection Errors

**Problem**: AI investigations fail to connect to LLM

**Solution**:

1. Verify LLM endpoint:
   ```bash
   LLM_ENDPOINT=http://localhost:11434
   ```

2. Pull Qwen 3.5 9B:
   ```bash
   docker pull qwen3.5:9b
   ```

3. Or use OpenAI-compatible endpoint:
   ```bash
   LLM_ENDPOINT=http://your-llm-server:11434
   ```

### Issue 4: Integration Authentication Errors

**Problem**: Integration API calls fail with 401

**Solution**:

1. Verify API key in database:
   ```sql
   SELECT integration_name, configuration FROM integration_configs;
   ```

2. Check that API key is valid and not expired

3. Ensure API key has required permissions

### Issue 5: CORS Errors on Frontend

**Problem**: Frontend cannot communicate with backend

**Solution**:

1. Add frontend origin to `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS=http://localhost:3000
   ```

2. Or disable CORS for development:
   ```python
   # In backend/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## Development Workflow

### Local Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend with auto-reload
uvicorn main:app --reload --port 8000
```

### Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/integrations/test_virustotal.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Production Deployment

### Docker Deploy

```bash
# Build for production
docker compose build --target production

# Start with production config
docker compose up -d

# Check logs
docker compose logs -f
```

### Kubernetes Deploy

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check status
kubectl get pods

# View logs
kubectl logs -f deployment/soar-backend
```

### Monitoring

```bash
# Check health
curl http://localhost:8000/health

# View logs
docker compose logs -f

# Check metrics
curl http://localhost:9090/metrics  # Prometheus metrics
```

## Security Checklist

After initial setup, verify:

- [ ] Admin password changed from default
- [ ] API keys stored securely (not in git)
- [ ] CORS origins configured correctly
- [ ] SSL/TLS enabled in production
- [ ] Audit logging enabled
- [ ] Rate limiting configured
- [ ] Database backups configured
- [ ] Integration API keys validated
- [ ] LLM endpoint is local or private

## Next Steps

1. **Explore the Platform**:
   - Create an incident via API or UI
   - Run a playbook
   - Test an integration
   - Start an AI investigation

2. **Customize**:
   - Add your integrations
   - Configure playbooks
   - Set up monitoring
   - Configure alerts

3. **Scale**:
   - Add more workers
   - Configure load balancing
   - Set up active-active database

## Support

- Documentation: See `README.md` and other docs
- Issues: Create GitHub issue
- Community: Join Discord/Slack channel

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

**Setup Complete!** 🎉

Your AI-Native SOAR platform is ready to use.
