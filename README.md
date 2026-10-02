# AI-Native SOAR (Security Orchestration, Automation and Response)

A secure, local-first Security Orchestration, Automation and Response platform inspired by Cortex XSOAR.

## Technology Stack

- **Frontend**: React + TypeScript (Vite)
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL
- **Cache/Messaging**: Redis
- **Orchestration**: Apache Airflow (planned)
- **AI**: Local OpenAI-compatible LLM endpoint + Qwen 3.5 9B
- **Deployment**: Docker Compose

## Core Architecture

```
SOC Analyst
    ↓
React Frontend
    ↓
FastAPI Backend
    ↓
PostgreSQL / Redis
    ↓
Playbook and Integration Services
    ↓
Airflow
    ↓
External Security Systems
```

The AI architecture:
```
Local LLM
    ↓
Agent Tool Broker
    ↓
Registered SOAR tools
    ↓
Integration / Incident / Playbook services
```

## Security Principles

- Security boundaries enforced by application code, not LLM instructions
- All incident evidence treated as untrusted
- Risk classifications for every action (READ, ENRICH, MODIFY, CONTAIN, EXECUTE, DESTRUCTIVE)
- Dangerous actions require human approval
- Least privilege and RBAC
- No plaintext credentials in API responses, logs, or LLM prompts
- No eval() or unrestricted shell execution

## Incident Architecture

Incidents are the primary investigation container with:
- Title, severity, status, owner
- Source, detection ID
- Hosts, users, IP addresses, domains, hashes
- Files, processes, MITRE ATT&CK techniques
- Evidence, findings, comments, tags
- Playbook executions, automation executions, AI investigation sessions

Incident numbering: `INC-YYYY-NNNNNN`

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

## Evidence Model

- Stable IDs: `EVID-NNNNN`
- AI findings reference evidence IDs
- AI output distinguishes: observed fact, inference, hypothesis, recommendation

## Integration Architecture

Common integration abstraction with:
- Integration → IntegrationInstance → IntegrationAction
- Each action defines: name, description, input/output schema, required permission, risk classification

## Playbook Architecture

- Declarative YAML/JSON playbooks
- Support for actions, conditions, dependencies, parallel tasks, retries, timeouts, approvals, failure handling
- Versioned playbooks with historical execution references

## Automation Architecture

- Versioned automation scripts
- Restricted execution (timeout, filesystem, networking, secrets, resource limits)
- No arbitrary unsandboxed code execution

## AI Investigation Architecture
- Operates within incident context
- Registered tools: get_incident, get_evidence, get_process_tree, search_siem, lookup_hash, lookup_ip, lookup_user, search_related_incidents
- Dangerous actions require approval workflow

## Phishing Email Analysis

The `/phishing` page ingests `.eml` files and runs an automated phishing playbook:
1. **Parse** message headers, routing table (Received chain), and SPF/DKIM/DMARC auth results
2. **Extract** indicators of compromise (domains, URLs, IPs)
3. **DNS / WhoIs** lookups (nslookup-equivalent) + local threat-intel scoring (optional VirusTotal)
4. **AI analysis** for a verdict, red flags, attack purpose, and recommendations
5. **One-click** conversion into a full incident with IOCs as observables

## Investigation Graph

Supports relationships between:
- Incident → Host → Process → IP
- Hash → Incident A → Host A
- Hash → Incident B → Host B

## Initial Database Domains

- users, roles, permissions
- incidents, incident_events, incident_comments, incident_tags, incident_artifacts, incident_observables, incident_findings, incident_relationships
- integrations, integration_instances, integration_actions
- automation_scripts, automation_versions, automation_runs
- playbooks, playbook_versions, playbook_steps, playbook_runs, playbook_step_runs
- approval_requests
- llm_sessions, llm_messages, llm_tool_calls, llm_findings
- audit_events

## Development Philosophy

First objective: Prove this complete workflow:

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

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Start Services

```bash
cd ai-native-soar
docker-compose up -d
```

### Access Points

- **Frontend**: http://localhost:3000
  - Dashboard: `/`
  - Incidents: `/incidents` (+ detail `/incidents/:id`)
  - Alerts: `/alerts` (+ detail `/alerts/:id`)
  - Phishing Analysis: `/phishing` (upload .eml files)
  - Settings: `/settings`
  - Login: `/login` (default account: **admin / admin**)
- **Backend API**: http://localhost:8000 (Swagger UI at `/docs`)
- **PostgreSQL**: localhost:5432 (user: `soar`, password from `${DB_PASSWORD}`)
- **Redis**: localhost:6379

### Database Setup

The backend automatically creates all database tables on startup via `Base.metadata.create_all`.

## API Endpoints

Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`.

### Key working endpoints (summary)

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/v1/incidents` | List / create incidents (auto-extract IOCs) |
| GET/PUT/DELETE | `/api/v1/incidents/{id}` | Incident detail / update / soft-delete |
| GET/POST | `/api/v1/incidents/{id}/events` | Timeline events |
| GET/POST | `/api/v1/incidents/{id}/comments` | Comments |
| POST | `/api/v1/incidents/{id}/observables/extract` | Extract IOCs from description |
| POST | `/api/v1/incidents/{id}/observables/enrich` | Enrich IOCs (threat intel) |
| POST | `/api/v1/incidents/{id}/analyze` | AI analysis summary |
| POST | `/api/v1/incidents/{id}/ask` | Custom AI question (full context) |
| GET/POST | `/api/v1/alerts` | List / create alerts |
| GET/PUT/DELETE | `/api/v1/alerts/{id}` | Alert detail / update / soft-delete |
| POST | `/api/v1/alerts/{id}/observables/extract` | Extract IOCs |
| POST | `/api/v1/alerts/{id}/observables/enrich` | Enrich IOCs |
| POST | `/api/v1/alerts/{id}/promote` | Promote alert → incident |
| POST | `/api/v1/alerts/{id}/analyze` | AI triage summary |
| POST | `/api/v1/alerts/{id}/ask` | Custom AI question (full context) |
| GET | `/api/v1/dashboard/summary` | Aggregate dashboard stats |
| GET | `/api/v1/settings/health` | System/database/LLM health |
| GET/POST/PUT/DELETE | `/api/v1/settings/llm` | LLM profile management |
| POST | `/api/v1/auth/login` | Login (default admin/admin) |
| POST | `/api/v1/auth/change-password` | Change password |
| POST | `/api/v1/phishing/analyze` | Upload .eml, run phishing analysis |
| POST | `/api/v1/phishing/ai-analysis` | AI analysis of parsed email |
| POST | `/api/v1/phishing/create-incident` | Convert analysis → incident |

## Security Considerations

1. **Secrets Management**: Use environment variables for all credentials
2. **Risk Classification**: All actions have predefined risk levels
3. **Approval Workflow**: High-risk actions require human approval
4. **Audit Logging**: All important actions generate audit events
5. **No Shell Execution**: No arbitrary Python or shell commands
6. **Input Validation**: All inputs validated against schemas
7. **Least Privilege**: Users and integrations operate with minimal required permissions

## Configuration

Environment variables are loaded from `.env` files:
- `.env` - Main application configuration
- `.env.development` - Development settings
- `.env.production` - Production settings

## License

MIT License — see the [LICENSE](LICENSE) file for details. This project is fully open source.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For support, please contact the development team.
