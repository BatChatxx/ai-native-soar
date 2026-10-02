# Project Structure

This document describes the complete project structure and organization of the AI-Native SOAR platform.

## Root Directory

```
ai-native-soar/
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── ARCHITECTURE.md                 # System architecture documentation
├── DEVELOPMENT.md                  # Development guidelines
├── PROJECT_STRUCTURE.md            # This file
├── README.md                       # Project overview
├── SECURITY.md                     # Security guidelines
├── SETUP.md                       # Setup instructions
├── docker-compose.yml              # Docker Compose configuration
├── start.sh                       # Startup script
├── secrets.example.toml            # Secret templates
├── incident_templates/             # Incident templates
│   └── [incident definitions]
├── playbook_templates/             # Playbook templates
│   ├── [playbook YAML files]
│   └── [workflow definitions]
├── automation_templates/           # Automation templates
│   ├── playbooks/
│   ├── scripts/
│   └── workflows/
└── frontend/                       # React frontend application
```

## Backend Directory

```
backend/
├── .env.example                    # Backend environment template
├── Dockerfile                      # Backend Docker image definition
├── alembic.ini                     # Alembic migration configuration
├── init_db.py                      # Database initialization script
├── main.py                        # FastAPI application entrypoint
├── requirements.txt                # Python dependencies
├── alembic/                       # Database migrations
│   ├── env.py                      # Alembic environment
│   └── versions/
│       └── 001_initial_schema.py   # Initial migration
├── migrations/                     # Manual migration scripts
├── models/                        # SQLAlchemy models
│   ├── __init__.py                # Model exports
│   ├── ai.py                      # AI/LLM models
│   ├── approvals.py               # Approval request models
│   ├── audit.py                   # Audit event models
│   ├── automation.py              # Automation script models
│   ├── database.py                # Database base class
│   ├── evidence.py                # Evidence models
│   ├── incidents.py               # Incident models
│   ├── integrations.py            # Integration models
│   ├── models.py                  # Core models (incidents, users, etc.)
│   ├── playbooks.py               # Playbook models
│   └── users.py                   # User/Role models
├── routers/                       # API route definitions
│   ├── __init__.py                # Router exports
│   ├── ai.py                      # AI/LLM routes
│   ├── approvals.py               # Approval routes
│   ├── audit.py                   # Audit routes
│   ├── auth.py                    # Authentication routes
│   ├── automation.py              # Automation routes
│   ├── dashboard.py               # Dashboard routes
│   ├── evidence.py                # Evidence routes
│   ├── incidents.py               # Incident routes
│   ├── integrations.py            # Integration routes
│   └── playbooks.py               # Playbook routes
├── schemas/                       # Pydantic schemas
│   ├── __init__.py                # Schema exports
│   ├── ai.py                      # AI request/response schemas
│   ├── approvals.py               # Approval schemas
│   ├── audit.py                   # Audit schemas
│   ├── automation.py              # Automation schemas
│   ├── dashboard.py               # Dashboard schemas
│   ├── evidence.py                # Evidence schemas
│   ├── incidents.py               # Incident schemas
│   ├── integrations.py            # Integration schemas
│   └── playbooks.py               # Playbook schemas
├── schemas/users.py               # User schemas
├── services/                      # Business logic services
│   ├── __init__.py                # Service exports
│   ├── ai.py                      # AI service
│   ├── approvals.py               # Approval service
│   ├── audit.py                   # Audit logging service
│   ├── auth.py                    # Authentication service
│   ├── automation.py              # Automation service
│   ├── evidence.py                # Evidence service
│   ├── incident_service.py        # Incident service
│   ├── incidents.py               # Incident handlers
│   ├── integration_service.py     # Integration service
│   ├── integrations.py            # Integration handlers
│   └── playbook_service.py        # Playbook service
├── utils/                         # Utility functions
│   ├── __init__.py                # Utility exports
│   ├── auth_utils.py              # Authentication utilities
│   └── validation_utils.py        # Input validation utilities
└── workers/                       # Background workers
    └── [worker implementations]
```

## Frontend Directory

```
frontend/
├── [React application files]
├── src/
│   ├── components/               # Reusable components
│   ├── pages/                    # Page components
│   ├── services/                 # API services
│   ├── store/                    # State management
│   ├── utils/                    # Utility functions
│   └── App.tsx                   # Application entry
└── package.json
```

## Docker Compose Configuration

```yaml
# docker-compose.yml
services:
  backend:
    image: soar-backend
    build:
      context: .
      dockerfile: backend/Dockerfile
    environment:
      - DATABASE_URL=postgresql://soar_user:soar_password@database:5432/soar
      - REDIS_URL=redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      - database
      - redis
    volumes:
      - ./backend:/app

  database:
    image: postgres:16
    environment:
      - POSTGRES_USER=soar_user
      - POSTGRES_PASSWORD=soar_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  frontend:
    image: soar-frontend
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
```

## Database Schema

### Core Tables

| Table | Description | Records |
|-------|-------------|---------|
| users | Platform users | 10-1000 |
| roles | User roles | 5-20 |
| permissions | Available permissions | 50-100 |
| incidents | Incident records | 100-10000+ |
| incident_events | Incident timeline | 10-100 per incident |
| incident_comments | Incident comments | 1-50 per incident |
| incident_tags | Incident tags | 10-50 |
| incident_observables | Evidence items | 5-100 per incident |
| incident_findings | AI findings | 0-50 per incident |
| incident_artifacts | File attachments | 0-20 per incident |
| incident_relationships | Entity relationships | 0-100 per incident |
| incident_hosts | Host associations | 0-50 per incident |
| incident_users | User associations | 0-50 per incident |
| incident_approval_requests | Approval requests | 0-10 per incident |
| integration_configs | Integration definitions | 10-30 |
| integration_instances | Integration instances | 1-5 per integration |
| integration_actions | Registered tool actions | 10-100 |
| integration_executions | Execution logs | 10-100 per action |
| automation_scripts | Script definitions | 5-50 |
| automation_versions | Script versions | 1-10 per script |
| automation_runs | Script executions | 1-100 per script |
| playbooks | Playbook definitions | 5-50 |
| playbook_versions | Playbook versions | 1-10 per playbook |
| playbook_runs | Playbook executions | 1-100 per playbook |
| playbook_step_runs | Step execution logs | 5-50 per run |
| approval_requests | High-risk action approvals | 0-50 |
| audit_events | System audit log | 10-1000 per hour |
| llm_sessions | AI investigation sessions | 0-50 per incident |
| llm_messages | LLM message history | 10-100 per session |
| llm_tool_calls | LLM tool calls | 1-20 per session |
| llm_findings | AI-generated findings | 0-10 per session |

### Table Relationships

```
users
  ├── roles (1:1)
  ├── incident_comments (1:N)
  ├── incident_approval_requests (1:N)

roles
  ├── permissions (N:1 via role_permissions)

incidents
  ├── incident_events (1:N)
  ├── incident_comments (1:N)
  ├── incident_tags (1:N)
  ├── incident_observables (1:N)
  ├── incident_findings (1:N)
  ├── incident_artifacts (1:N)
  ├── incident_relationships (1:N)
  ├── incident_hosts (1:N)
  ├── incident_users (1:N)
  ├── incident_approval_requests (1:N)
  ├── integration_executions (1:N)

integration_configs
  ├── integration_instances (1:N)
  ├── integration_actions (1:N)

integration_configs
  └── integration_actions (1:N)

integration_configs
  ├── integration_instances (1:N)

automation_scripts
  ├── automation_versions (1:N)
  ├── automation_runs (1:N)

playbooks
  ├── playbook_versions (1:N)
  ├── playbook_runs (1:N)

playbook_runs
  ├── playbook_step_runs (1:N)

llm_sessions
  ├── llm_messages (1:N)
  ├── llm_tool_calls (1:N)
  ├── llm_findings (1:N)
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/incidents/ | POST | Create incident |
| /api/v1/incidents/{id} | GET | Get incident |
| /api/v1/incidents/{id} | PATCH | Update incident |
| /api/v1/incidents/number/{number} | GET | Get by number |
| /api/v1/incidents/{id}/timeline | GET | Get timeline |
| /api/v1/incidents/{id}/evidence | GET | Get evidence |
| /api/v1/incidents/{id}/findings | GET | Get findings |
| /api/v1/incidents/{id}/relationships | GET | Get relationships |
| /api/v1/incidents/{id}/approvals | GET | Get pending approvals |
| /api/v1/incidents/{id}/approvals/{id} | POST | Approve action |
| /api/v1/incidents/{id}/approvals/{id} | DELETE | Deny action |

### Evidence Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/evidence/ | POST | Create evidence |
| /api/v1/evidence/{id} | GET | Get evidence |
| /api/v1/evidence/{id} | PATCH | Update evidence |
| /api/v1/evidence/{id}/classify | POST | Classify evidence |

### Integration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/integrations/ | GET | List integrations |
| /api/v1/integrations/{name} | GET | Get integration |
| /api/v1/integrations/{name} | PATCH | Update integration |
| /api/v1/integrations/{name}/execute | POST | Execute action |
| /api/v1/integrations/{name}/lookup_ip | POST | Lookup IP |
| /api/v1/integrations/{name}/lookup_hash | POST | Lookup hash |
| /api/v1/integrations/{name}/lookup_domain | POST | Lookup domain |
| /api/v1/integrations/{name}/get_host | POST | Get host |
| /api/v1/integrations/{name}/get_process_tree | POST | Get process tree |
| /api/v1/integrations/{name}/contain_host | POST | Contain host |
| /api/v1/integrations/{name}/run_rtr | POST | Run RTR command |

### Playbook Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/playbooks/ | GET | List playbooks |
| /api/v1/playbooks/{slug} | GET | Get playbook |
| /api/v1/playbooks/{slug} | PATCH | Update playbook |
| /api/v1/playbooks/{slug}/execute | POST | Execute playbook |
| /api/v1/playbooks/{slug}/run | GET | Get playbook run |
| /api/v1/playbooks/{slug}/runs | GET | List playbook runs |
| /api/v1/playbooks/{slug}/versions | GET | List versions |

### Automation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/automation/ | GET | List automation scripts |
| /api/v1/automation/{slug} | GET | Get automation script |
| /api/v1/automation/{slug} | PATCH | Update automation script |
| /api/v1/automation/{slug}/execute | POST | Execute automation |
| /api/v1/automation/{slug}/runs | GET | List runs |
| /api/v1/automation/{slug}/versions | GET | List versions |

### Approval Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/approvals/ | GET | List all approvals |
| /api/v1/approvals/pending | GET | List pending approvals |
| /api/v1/approvals/{id} | GET | Get approval |
| /api/v1/approvals/{id} | POST | Approve action |
| /api/v1/approvals/{id} | DELETE | Deny action |
| /api/v1/approvals/{id}/revoke | POST | Revoke approval |

### AI Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/ai/investigate | POST | Start AI investigation |
| /api/v1/ai/message | POST | Send message to AI |
| /api/v1/ai/findings | GET | Get AI findings |
| /api/v1/ai/recommendations | GET | Get recommendations |

### Audit Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/audit/ | GET | List audit events |
| /api/v1/audit/{type} | GET | Filter by type |
| /api/v1/audit/incident/{id} | GET | Incident audit log |
| /api/v1/audit/filter | POST | Filter audit events |

### Dashboard Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/dashboard/stats | GET | Get dashboard stats |
| /api/v1/dashboard/incidents | GET | Incident stats |
| /api/v1/dashboard/topics | GET | Hot topics |
| /api/v1/dashboard/health | GET | System health |

## Service Architecture

### Core Services

| Service | Responsibility | Files |
|---------|---------------|-------|
| Incident Service | Incident CRUD operations | services/incidents.py |
| Evidence Service | Evidence management | services/evidence.py |
| Integration Service | Integration execution | services/integration_service.py |
| Playbook Service | Playbook execution | services/playbook_service.py |
| Approval Service | Approval workflow | services/approvals.py |
| Automation Service | Automation execution | services/automation.py |
| AI Service | AI investigation | services/ai.py |
| Audit Service | Audit logging | services/audit.py |
| Auth Service | Authentication | services/auth.py |

### Service Dependencies

```
Incident Service
  ├── Database (SQLAlchemy)
  ├── Evidence Service
  ├── Integration Service
  ├── Playbook Service
  └── Audit Service

Evidence Service
  ├── Database (SQLAlchemy)
  └── Integration Service (optional)

Integration Service
  ├── Database (SQLAlchemy)
  └── IntegrationConfig (from DB)

Playbook Service
  ├── Database (SQLAlchemy)
  ├── Integration Service
  ├── Automation Service
  └── Approval Service

Approval Service
  ├── Database (SQLAlchemy)
  └── Audit Service

AI Service
  ├── Database (SQLAlchemy)
  ├── Integration Service
  └── LLM Client
```

## Security Architecture

### Authentication Flow

```
Frontend
  └─> POST /api/v1/auth/login
      └─> JWT Token
          └─> Include in all requests

Backend
  └─> services/auth.py
      ├── Validate JWT
      ├── Check user permissions
      └─> Return user context
```

### Authorization Model

```
Permission Levels:
  - read:incidents
  - create:incidents
  - update:incidents
  - delete:incidents
  - read:evidence
  - create:evidence
  - update:evidence
  - read:playbooks
  - execute:playbooks
  - read:integrations
  - execute:integrations
  - read:approvals
  - approve:actions
  - read:audit

Role-Based Access:
  - admin: All permissions
  - analyst: read, create, update (limited)
  - viewer: read only
```

### Risk Classification

```python
RiskLevel.READ = "read"           # No approval
RiskLevel.ENRICH = "enrich"       # No approval
RiskLevel.MODIFY_LOW = "modify_low"  # No approval
RiskLevel.MODIFY = "modify"       # Approval required
RiskLevel.CONTAIN = "contain"     # Approval required
RiskLevel.EXECUTE = "execute"     # Approval required
RiskLevel.DESTRUCTIVE = "destructive"  # Approval required
```

## Data Flow

### Incident Creation

```
Frontend
  └─> POST /api/v1/incidents/
      └─> IncidentService.create()
          └─> Incident created
          └─> AuditEvent created
          └─> IncidentEvent created
          └─> Return incident
```

### Evidence Extraction

```
Playbook
  └─> Extract observables
      └─> EvidenceService.create()
          └─> Evidence created
          └─> IncidentEvent created
          └─> Return evidence IDs
```

### Integration Execution

```
Frontend/Playbook/AI
  └─> IntegrationService.execute()
      └─> Validate input
      └─> Check authorization
      └─> Check risk level
      └─> Get integration config
      └─> Execute action
      └─> Log audit event
      └─> Return result
```

### Approval Workflow

```
AI/Integration Service
  └─> High-risk action requested
      └─> ApprovalService.request()
          └─> ApprovalRequest created
          └─> IncidentEvent created
          └─> AuditEvent created
          └─> Return approval_request_id
Frontend/Analyst
  └─> POST /api/v1/approvals/{id}
      └─> ApprovalService.approve()
          └─> Update approval request
          └─> Execute original action
          └─> AuditEvent created
```

### AI Investigation

```
Frontend/AI
  └─> AIService.start_investigation()
      └─> LLMSession created
      └─> Get incident
      └─> Get evidence
      └─> Call registered tools
      └─> Log tool calls
      └─> Generate findings
      └─> Log messages
      └─> Return recommendations
```

## Database Design Principles

### Primary Keys

- All tables use integer primary keys (auto-increment)
- Business IDs are stored as strings (e.g., "EVID-00192")

### Foreign Keys

- CASCADE delete for child relationships
- RESTRICT delete for parent relationships
- Proper indexing on foreign key columns

### Indexes

- Primary key indexes (automatic)
- Foreign key indexes (automatic)
- Unique indexes on business IDs
- Search indexes on frequently queried fields

### Soft Deletes

- No soft deletes for critical data
- Audit events for all deletions
- Archived tables for historical data

## Caching Strategy

### Redis Usage

```python
# Cache integration configs
@lru_cache(maxsize=100)
def get_integration_config(integration_name: str) -> IntegrationConfig:
    return db.query(IntegrationConfig).filter(
        IntegrationConfig.integration_name == integration_name
    ).first()

# Cache incident data
@lru_cache(maxsize=100)
def get_incident_by_number(number: str) -> Incident:
    return db.query(Incident).filter(Incident.number == number).first()
```

### Cache Invalidation

- Invalidate on incident update
- Invalidate on evidence update
- Invalidate on integration config update
- Set TTL for dynamic data

## Monitoring and Logging

### Log Levels

```python
# DEBUG - Detailed debugging info
# INFO - General operational info
# WARNING - Unexpected events
# ERROR - Error conditions
# CRITICAL - Critical failures
```

### Metrics

- Incident creation rate
- Integration execution time
- Playbook execution time
- AI response time
- Approval request rate
- Error rates by endpoint

## Testing Strategy

### Unit Tests

```
tests/
├── models/          # Model tests
├── schemas/         # Schema tests
├── services/        # Service tests
├── routers/         # API route tests
└── utils/           # Utility tests
```

### Integration Tests

```
tests/integration/
├── incidents.py
├── evidence.py
├── integrations.py
├── playbooks.py
├── approvals.py
└── ai.py
```

### Test Coverage Targets

- Models: 100%
- Services: 80%
- Schemas: 100%
- Routers: 80%

## Deployment Architecture

### Development

```
Development
  ├── Backend (localhost:8000)
  ├── Frontend (localhost:3000)
  ├── Database (PostgreSQL in Docker)
  └── Redis (in Docker)
```

### Production

```
Production
  ├── Load Balancer
  │   ├── Backend (N instances)
  │   └── Frontend (N instances)
  ├── Database (Primary + Replicas)
  └── Redis Cluster
```

### Kubernetes

```
Kubernetes
  ├── Namespace: soar
  │   ├── Deployment: backend
  │   ├── Deployment: frontend
  │   ├── StatefulSet: database
  │   └── Deployment: redis
  ├── Ingress: soar.example.com
  └── HPA: Auto-scaling
```

## File Conventions

### Python Files

- `models/*.py` - SQLAlchemy models
- `schemas/*.py` - Pydantic schemas
- `services/*.py` - Business logic
- `routers/*.py` - API routes
- `utils/*.py` - Utility functions

### Naming Conventions

- Models: PascalCase (e.g., `Incident`)
- Functions: snake_case (e.g., `create_incident`)
- Classes: PascalCase (e.g., `IncidentService`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_TITLE_LENGTH`)
- Database tables: snake_case (e.g., `incident_events`)

### Code Style

- Follow PEP 8
- Use black formatter
- Use mypy type checking
- Use flake8 linting

## Environment Configuration

### Development

```bash
# .env
DATABASE_URL=postgresql://soar_user:password@localhost:5432/soar
REDIS_URL=redis://localhost:6379
DEBUG=true
LOG_LEVEL=debug
```

### Production

```bash
# .env
DATABASE_URL=postgresql://user:password@postgres:5432/soar
REDIS_URL=redis://redis:6379
DEBUG=false
LOG_LEVEL=info
```

## Version Control

### Branch Strategy

```
main           # Production-ready code
develop        # Development integration
feature/*      # New features
bugfix/*       # Bug fixes
hotfix/*       # Production hotfixes
```

### Commit Messages

```
feat: Add ThreatIntel integration
fix: Resolve incident timeline pagination
docs: Update API documentation
test: Add tests for evidence service
refactor: Improve incident service performance
```

## Summary

The AI-Native SOAR platform follows a well-organized, modular architecture with:

- **Clear separation of concerns** (models, schemas, services, routes)
- **Comprehensive testing** (unit, integration, coverage)
- **Robust security** (RBAC, audit logging, risk classification)
- **Scalable design** (caching, database indexing, containerization)
- **Developer-friendly** (documentation, conventions, tooling)

The architecture supports the complete threat response workflow while maintaining security, maintainability, and scalability.
