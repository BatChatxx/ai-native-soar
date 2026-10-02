# AI-Native SOAR Platform

## Overview

This is a secure, local-first Security Orchestration, Automation and Response (SOAR) platform inspired by Cortex XSOAR. The system is built with React + TypeScript frontend, Python + FastAPI backend, PostgreSQL database, Redis cache, and Apache Airflow for orchestration.

## Architecture

```
SOC Analyst
    ↓
React Frontend (http://localhost:3000)
    ↓
FastAPI Backend (http://localhost:8000)
    ↓
PostgreSQL / Redis
    ↓
Playbook and Integration Services
    ↓
Airflow
    ↓
External Security Systems

The AI architecture is:
Local LLM
    ↓
Agent Tool Broker
    ↓
Registered SOAR tools
    ↓
Integration / Incident / Playbook services
```

## Security Boundaries

- The frontend communicates only with the SOAR backend
- The frontend must NOT communicate directly with:
  - PostgreSQL
  - Airflow
  - external security integrations
  - LLM infrastructure
- The LLM must NEVER directly access:
  - database credentials
  - API credentials
  - Airflow credentials
  - operating system shell
  - Docker socket
  - arbitrary filesystem paths
  - arbitrary Python execution

## Risk Model

Every action has a risk classification:
- **READ**: Query SIEM, retrieve host, retrieve detection
- **ENRICH**: IP reputation, domain lookup, hash reputation
- **MODIFY_LOW**: Add incident tag, update metadata
- **MODIFY**: Modify external ticket, modify identity
- **CONTAIN**: Isolate endpoint, disable account
- **EXECUTE**: Endpoint RTR, remote PowerShell, remote shell
- **DESTRUCTIVE**: Delete object, destructive quarantine

READ and ENRICH may execute automatically.
MODIFY, CONTAIN, EXECUTE and DESTRUCTIVE require authorization or human approval.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Access services
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Airflow Web: http://localhost:8080
# - LLM Studio: http://localhost:1234
```

### Using Docker Compose with LLM

```bash
# Build and run all services including LLM
docker-compose up -d --build

# For Qwen 3.5 9B, pull the model first:
# docker pull ghcr.io/lmstudio-community/lmstudio-server
# Then run with model volume mount:
# docker run -d --rm -p 1234:1234 \
#   --name soar_llm \
#   ghcr.io/lmstudio-community/lmstudio-server \
#   --model /path/to/qwen3.5-9b
```

### Manual Setup (PostgreSQL Required)

1. Start PostgreSQL:
```bash
docker run -d --name postgres \
  -e POSTGRES_USER=soar_user \
  -e POSTGRES_PASSWORD=soar_password \
  -e POSTGRES_DB=soar \
  -p 5432:5432 \
  postgres:16-alpine
```

2. Start Redis:
```bash
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

3. Start backend:
```bash
cd backend
python main.py
```

## API Endpoints

### Incidents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/incidents` | List all incidents |
| POST | `/api/v1/incidents` | Create new incident |

### Evidence

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/evidence` | List all evidence |
| POST | `/api/v1/evidence` | Create new evidence |

### Playbooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/playbooks` | List all playbooks |
| POST | `/api/v1/playbooks` | Create new playbook |

### Approvals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/approvals` | List approval requests |
| POST | `/api/v1/approvals/{id}/approve` | Approve action |
| POST | `/api/v1/approvals/{id}/deny` | Deny action |

### Automation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/automation` | List automation scripts |
| POST | `/api/v1/automation` | Create automation script |
| POST | `/api/v1/automation/{slug}/run` | Run automation |

### Integrations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/integrations` | List integrations |
| POST | `/api/v1/integrations` | Create integration |
| GET | `/api/v1/integrations/{name}/actions` | List actions |
| POST | `/api/v1/integrations/{name}/actions` | Create action |

### Audit

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit` | List audit events |

## Example Incident Creation

```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Suspicious Process Detected",
    "description": "PowerShell execution from Word document",
    "severity": "high",
    "source_type": "EDR"
  }'
```

Response:
```json
{
  "incident_number": "INC-2026-000184",
  "title": "Suspicious Process Detected",
  "description": "PowerShell execution from Word document",
  "severity": "high",
  "status": "open",
  "created_at": "2026-01-15T10:21:00Z"
}
```

## Incident Timeline

Events are appended to an append-only incident timeline:

```
10:21 Incident created
10:22 Observable extracted
10:23 SIEM query executed
10:24 Evidence attached
10:25 AI investigation started
10:27 Containment requested
10:28 Analyst approved action
10:29 Endpoint contained
```

## Investigation Graph

The system supports relationships:

```
Incident
    ↓
Host
    ↓
Process
    ↓
IP
```

Example:
```
Hash
    ↓
Incident A
    ↓
Host A
```

## Engineering Rules

1. Implement ONE roadmap task at a time
2. Do not implement future tasks unless required
3. Before coding:
   - Inspect existing repository
   - Understand existing architecture
   - Identify affected files
   - Explain proposed change
   - Identify security consequences
4. After implementation:
   - Run unit tests
   - Run integration tests
   - Run linting
   - Run type checking
   - Report files changed
   - Report tests executed
   - Report architectural decisions
   - Report known limitations
   - Report security considerations

## Development Philosophy

The first objective is NOT to reproduce every Cortex XSOAR capability.

The first objective is to prove this complete workflow:

```
Security Alert
    ↓
Incident
    ↓
Observable Extraction
    ↓
Playbook
    ↓
Evidence Collection
    ↓
AI Investigation
    ↓
Recommendation
    ↓
Human Approval
    ↓
Response Action
    ↓
Auditable Incident Timeline
```

## Technology Stack

### Frontend
- React
- TypeScript

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic

### Database
- PostgreSQL

### Cache / Event Messaging
- Redis

### Orchestration
- Apache Airflow

### AI
- Local OpenAI-compatible LLM endpoint
- Qwen 3.5 9B initially

### Deployment
- Docker Compose

## Project Structure

```
ai-native-soar/
├── backend/
│   ├── main.py
│   ├── models/
│   │   ├── models.py
│   │   └── database.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── incidents_router.py
│   │   ├── evidence_router.py
│   │   ├── playbooks_router.py
│   │   ├── approvals_router.py
│   │   ├── automation_router.py
│   │   ├── integrations_router.py
│   │   └── audit_router.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── (React app)
├── docker-compose.yml
└── docs/
    └── README.md
```

## Known Limitations

1. PostgreSQL required (use Docker Compose to avoid manual setup)
2. Airflow is optional and can be started later
3. LLM integration requires local OpenAI-compatible endpoint
4. No authentication/authorization yet (to be implemented)

## Security Considerations

1. Never store plaintext credentials in integration configurations
2. All sensitive operations require server-side authorization
3. Use least privilege
4. Use RBAC
5. Audit all important actions
6. Do not use eval()
7. Do not create unrestricted shell execution
8. Validate all tool inputs against schemas
9. Do not expose arbitrary Python execution through APIs

## License

MIT
