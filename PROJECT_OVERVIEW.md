# AI-Native SOAR Platform - Project Overview

## Executive Summary

This project builds a secure, local-first Security Orchestration, Automation and Response (SOAR) platform inspired by Cortex XSOAR, with a focus on AI-assisted threat investigations.

The platform emphasizes security by design, with strict boundaries between LLM access, database access, and external system access.

## Core Objective

**Prove the complete workflow** before expanding capabilities:

```
Security Alert → Incident → Observable Extraction → Playbook
→ Evidence Collection → AI Investigation → Recommendation
→ Human Approval → Response Action → Auditable Incident Timeline
```

Once this workflow works reliably, expand capabilities incrementally.

## High-Level Architecture

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React + TypeScript | Analyst UI |
| Backend | Python + FastAPI | REST API |
| Database | PostgreSQL 16 | Source of truth |
| Cache | Redis | Caching, events |
| Orchestration | Apache Airflow | Internal workflows |
| AI/LLM | Qwen 3.5 9B | Local LLM endpoint |
| Deployment | Docker Compose | Container orchestration |

### Security Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    ANALYST UI (React)                        │
│               (localhost:3000)                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 SOAR API (FastAPI)                           │
│            (localhost:8000 /api/v1)                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               INTEGRATION ABSTRACTION                │    │
│  │  Integration → IntegrationInstance → Action          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │
│  │ Incidents   │  │Integrations │  │  Playbooks      │     │
│  └─────────────┘  └─────────────┘  └─────────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │
│  │  Evidence   │  │  AI/LLM     │  │  Approvals      │     │
│  └─────────────┘  └─────────────┘  └─────────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐     │
│  │  Automation │  │  Audit      │  │  Users/Roles    │     │
│  └─────────────┘  └─────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            POSTGRESQL (Source of Truth)                      │
│              REDIS (Cache/Events)                            │
│         APACHE AIRFLOW (Orchestration)                       │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              EXTERNAL SECURITY SYSTEMS                       │
│     SIEM, EDR, Threat Intel, Ticketing, Email, etc.          │
└─────────────────────────────────────────────────────────────┘
```

### AI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Local LLM (Qwen 3.5 9B)                  │
│              (via OpenAI-compatible endpoint)                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 AGENT TOOL BROKER                            │
│                                                             │
│  Registered SOAR Tools:                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  get_incident()                                    │    │
│  │  get_evidence()                                     │    │
│  │  get_process_tree()                                 │    │
│  │  search_siem()                                      │    │
│  │  lookup_hash()                                      │    │
│  │  lookup_ip()                                        │    │
│  │  lookup_user()                                      │    │
│  │  search_related_incidents()                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Dangerous Actions:                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  contain_host()    → ACTION_REQUIRES_APPROVAL       │    │
│  │  isolate_endpoint() → ACTION_REQUIRES_APPROVAL      │    │
│  │  run_rtr_command()  → ACTION_REQUIRES_APPROVAL      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Registered Integration Actions                  │
│                                                             │
│  Example: crowdstrike                                       │
│    └─ get_host (READ)                                       │
│    └─ get_process_tree (READ)                               │
│    └─ contain_host (CONTAIN) → Requires approval            │
│    └─ run_rtr_command (EXECUTE) → Requires approval         │
└─────────────────────────────────────────────────────────────┘
```

**Critical Security Rule**: The LLM must NEVER directly access:
- Database credentials
- API credentials
- Airflow credentials
- Operating system shell
- Docker socket
- Arbitrary filesystem paths
- Arbitrary Python execution

## Core Entities

### Incident Model

An incident is the primary investigation container:

```python
Incident:
  - id: int
  - number: str (e.g., INC-2026-000184)
  - title: str
  - description: str
  - status: Enum (open, investigating, containing, etc.)
  - severity: Enum (low, medium, high, critical)
  - source_type: str (e.g., SIEM, EDR)
  - source_integration: str
  - detection_id: str
  - detection_timestamp: datetime
  - owner_id: int (user who owns incident)
  - created_by_id: int
  - tags: List[str]
  - created_at: datetime
  - updated_at: datetime
  - started_at: datetime (optional)
  - closed_at: datetime (optional)
  - closed_reason: str (optional)
  - resolved_at: datetime (optional)
  - resolved_reason: str (optional)
```

**Incidents contain**:
- Hosts, users, IPs, domains, hashes
- Evidence (observables)
- Findings
- Comments
- Tags
- Timeline events
- Playbook executions
- Automation executions
- AI investigation sessions

### Evidence Model

Evidence has stable IDs referenced in AI findings:

```python
IncidentObservable:
  - id: int
  - incident_id: int
  - evidence_id: str (e.g., EVID-00192)
  - observable_type: str (ip, domain, hash, file)
  - content: str (e.g., "192.168.1.1")
  - source: str (e.g., EDR, SIEM)
  - timestamp: datetime
  - classification: Enum (untrusted, internal, public)
```

**AI Finding Best Practice**:

```
✅ "powershell.exe was launched by WINWORD.EXE according to EVID-00192."
❌ "The computer is definitely compromised."
```

AI output should distinguish:
- Observed fact
- Inference
- Hypothesis
- Recommendation

### Integration Abstraction

A common abstraction for all security tools:

```python
Integration:
  - id: int
  - integration_name: str (e.g., virustotal)
  - display_name: str
  - enabled: bool
  - configuration: JSON
  - created_at: datetime
  - updated_at: datetime

IntegrationInstance:
  - id: int
  - integration_config_id: int
  - instance_id: str
  - instance_name: str

IntegrationAction:
  - id: int
  - integration_config_id: int
  - action_name: str (e.g., lookup_ip)
  - action_group: str
  - description: str
  - risk_level: Enum (read, enrich, modify, etc.)
  - requires_approval: bool
  - input_schema: JSON
  - output_schema: JSON
  - enabled: bool
```

**Example Integration**: CrowdStrike Falcon

```python
crowdstrike:
  actions:
    - get_host:
        risk: READ
        description: Get host details
    - get_process_tree:
        risk: READ
        description: Get process tree
    - contain_host:
        risk: CONTAIN
        description: Isolate host from network
        requires_approval: true
    - run_rtr_command:
        risk: EXECUTE
        description: Run RTR remote command
        requires_approval: true
```

### Playbook Model

Playbooks should initially be declarative YAML or JSON:

```yaml
version: "1.0"
name: IP Reputation Check
description: "Check IP reputation across multiple threat intelligence sources"
category: "investigation"
risk_level: "READ"
requires_approval: false

steps:
  - id: vt_lookup
    name: "VirusTotal IP Lookup"
    type: "integration"
    integration: "virustotal"
    action: "lookup_ip"
    input:
      - parameter: "ip_address"
        type: "string"
        source: "observable"
        required: true
    output:
      - parameter: "report"
        type: "object"
        description: "VT report"

  - id: threatcrowd_lookup
    name: "ThreatCrowd IP Lookup"
    type: "integration"
    integration: "threatcrowd"
    action: "get_report"
    input:
      - parameter: "ip_address"
        type: "string"
        source: "observable"
        required: true
    output:
      - parameter: "report"
        type: "object"
        description: "ThreatCrowd report"
```

**Playbook Features**:
- Actions
- Conditions
- Dependencies
- Parallel tasks
- Retries
- Timeouts
- Approvals
- Failure handling
- Versioning

### Risk Classification

Every action has a risk level:

| Level | Example Actions | Approval Required |
|-------|----------------|-------------------|
| READ | Query SIEM, retrieve host | ❌ No |
| ENRICH | IP lookup, domain lookup | ❌ No |
| MODIFY_LOW | Add incident tag | ❌ No |
| MODIFY | Modify external ticket | ✅ Yes |
| CONTAIN | Isolate endpoint | ✅ Yes |
| EXECUTE | Remote PowerShell | ✅ Yes |
| DESTRUCTIVE | Delete object | ✅ Yes |

**Rule**: READ and ENRICH may normally execute automatically. MODIFY, CONTAIN, EXECUTE, and DESTRUCTIVE should normally require authorization or human approval.

### Timeline Events

Timeline events are append-only:

```python
IncidentEvent:
  - id: int
  - incident_id: int
  - event_type: str
  - description: str
  - actor_username: str
  - actor_id: int
  - event_data: JSON
  - timestamp: datetime
```

Example timeline:

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

**Historical events should not be silently overwritten**.

## Engineering Rules

### Implementation Order

1. **ONE roadmap task at a time**
2. **Do not implement future tasks unless required**
3. **Before coding**:
   - Inspect existing repository
   - Understand existing architecture
   - Identify affected files
   - Explain proposed change
4. **After implementation**:
   - Run unit tests
   - Run integration tests
   - Run linting
   - Run type checking
   - Report files changed
   - Report tests executed
   - Report architectural decisions
   - Report known limitations
   - Report security considerations

### Development Philosophy

> The first objective is **NOT** to reproduce every Cortex XSOAR capability.
> The first objective is to **prove this complete workflow**:
> 
> ```
> Security Alert → Incident → Observable Extraction → Playbook
> → Evidence Collection → AI Investigation → Recommendation
> → Human Approval → Response Action → Auditable Incident Timeline
> ```

> Once this workflow works reliably, expand capabilities incrementally.

## Initial Database Domains

Core entities include:

- users
- roles
- permissions
- incidents
- incident_events (timeline)
- incident_comments
- incident_tags
- incident_artifacts
- incident_observables (evidence)
- incident_findings
- incident_relationships
- integrations
- integration_instances
- integration_actions
- automation_scripts
- automation_versions
- automation_runs
- playbooks
- playbook_versions
- playbook_runs
- playbook_step_runs
- approval_requests
- llm_sessions
- llm_messages
- llm_tool_calls
- llm_findings
- audit_events

**Exact schemas may evolve** based on requirements. Do not create all tables prematurely.

## Security Principles

### Security Boundaries

- PostgreSQL is the source of truth
- Airflow is an internal orchestration service
- The frontend communicates only with the SOAR backend
- The frontend must NOT communicate directly with:
  - PostgreSQL
  - Airflow
  - External security integrations
  - LLM infrastructure

### AI Security Rules

- The LLM must NEVER directly access:
  - Database credentials
  - API credentials
  - Airflow credentials
  - Operating system shell
  - Docker socket
  - Arbitrary filesystem paths
  - Arbitrary Python execution

### Content Handling

- Treat all incident evidence as untrusted
- Content inside evidence must NEVER be interpreted as instructions that modify agent permissions
- All sensitive operations require server-side authorization
- Use least privilege
- Use RBAC
- Do not store plaintext credentials inside integration configuration records
- Secrets must never appear in:
  - API responses
  - Logs
  - LLM prompts
  - Incident comments
  - Audit messages

### Code Security

- All important actions must generate audit events
- Do not use eval()
- Do not create unrestricted shell execution functionality
- Do not expose arbitrary Python execution through APIs
- Validate all tool inputs against schemas
- Validate tool outputs where appropriate

## Deployment

### Docker Compose

The platform uses Docker Compose for deployment:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
      - LLM_ENDPOINT=http://...
      - ...
    depends_on:
      - postgresql
      - redis
  
  postgresql:
    image: postgres:16
  
  redis:
    image: redis:7
  
  airflow:
    image: apache/airflow:latest
  
  ai-llm:
    image: qwen3.5:9b
  
  frontend:
    build: ./frontend
    ports:
      - "3000:8000"
```

### Initial Setup

```bash
cd ai-native-soar

# Copy environment template
cp .env.example .env

# Edit .env with your values

# Start all services
docker compose up -d

# Initialize database
docker compose exec backend python init_db.py

# Access API docs
open http://localhost:8000/docs

# Access frontend
open http://localhost:3000
```

## API Endpoints

Core API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/incidents/` | POST | Create incident |
| `/api/v1/incidents/{id}` | GET | Get incident |
| `/api/v1/incidents/number/{number}` | GET | Get by number |
| `/api/v1/incidents/` | GET | List incidents |
| `/api/v1/incidents/{id}/timeline` | GET | Get timeline |
| `/api/v1/incidents/{id}/evidence` | GET | Get evidence |
| `/api/v1/incidents/{id}/findings` | GET | Get findings |
| `/api/v1/integrations/` | GET | List integrations |
| `/api/v1/playbooks/` | GET | List playbooks |
| `/api/v1/evidence/` | GET | Get evidence |
| `/api/v1/approvals/` | GET | List approval requests |
| `/api/v1/audit/` | GET | Get audit events |
| `/api/v1/dashboard/` | GET | Get dashboard data |

See `/api/v1` endpoints in API docs for full details.

## Next Steps

After initial setup and verification:

1. ✅ Verify all services start correctly
2. ✅ Test incident creation
3. ✅ Test observable extraction
4. ✅ Test playbook execution
5. ✅ Test AI investigation
6. ✅ Test approval workflow
7. ✅ Verify timeline events

Then expand capabilities incrementally:

1. Add more integration templates
2. Implement automation scripting
3. Add playbook designer
4. Implement bulk operations
5. Add investigation graph
6. Implement case management
7. Add advanced AI capabilities
8. Enhance collaboration features

## Support

For questions or issues:

- Check the API documentation at `/docs`
- Review the architecture documentation
- See the issue tracker for known bugs
- Check the wiki for additional resources

---

**Built with ❤️ for modern threat response teams**
