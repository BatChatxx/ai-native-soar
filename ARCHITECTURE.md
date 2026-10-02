# System Architecture

This document describes the complete architecture of the AI-Native SOAR platform.

## Overview

The AI-Native SOAR platform is a secure, local-first security orchestration, automation, and response system. It follows a modular, layered architecture that separates concerns and enforces security boundaries.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                             │
│                     (localhost:3000)                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Incident Management                                        │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Incident List / Detail / Timeline                     │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Evidence Viewer                                       │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Playbook Runner                                        │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ AI Assistant                                           │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Integrations Hub                                       │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND SERVER                         │
│                   (localhost:8000 /api/v1)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API Layer                                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ HTTP / WebSocket Endpoints                            │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Authentication & Authorization                        │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Input Validation (Pydantic Schemas)                   │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Service Layer (Business Logic)                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Incident Service                                       │ │ │
│  │  │ - Create/Update/Delete incidents                       │ │ │
│  │  │ - Incident timeline management                         │ │ │
│  │  │ - Evidence extraction                                   │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Evidence Service                                        │ │ │
│  │  │ - Evidence CRUD                                         │ │ │
│  │  │ - Evidence classification                              │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Integration Service                                      │ │ │
│  │  │ - Integration configuration                             │ │ │
│  │  │ - Integration action execution                          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Playbook Service                                         │ │ │
│  │  │ - Playbook parsing                                       │ │ │
│  │  │ - Playbook execution                                     │ │ │
│  │  │ - Playbook step orchestration                           │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Approval Service                                         │ │ │
│  │  │ - Approval request creation                              │ │ │
│  │  │ - Approval validation                                     │ │ │
│  │  │ - Approval execution                                      │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Automation Service                                        │ │ │
│  │  │ - Automation script execution                            │ │ │
│  │  │ - Automation versioning                                  │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ AI Service                                                │ │ │
│  │  │ - AI investigation session management                   │ │ │
│  │  │ - Tool registration and routing                          │ │ │
│  │  │ - LLM interaction                                        │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Audit Service                                             │ │ │
│  │  │ - Audit event creation                                    │ │ │
│  │  │ - Audit logging                                          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Tool Broker (AI Integration Layer)                          │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Registered Integration Tools                            │ │ │
│  │  │ ┌──────────────────────────────────────────────────┐ │ │ │
│  │  │ │ threat_intel.lookup_ip (READ)                      │ │ │ │
│  │  │ └──────────────────────────────────────────────────┘ │ │ │
│  │  │ ┌──────────────────────────────────────────────────┐ │ │ │
│  │  │ │ threatcrowd.lookup_domain (ENRICH)               │ │ │ │
│  │  │ └──────────────────────────────────────────────────┘ │ │ │
│  │  │ ┌──────────────────────────────────────────────────┐ │ │ │
│  │  │ │ generic_edr.get_host (READ)                      │ │ │ │
│  │  │ └──────────────────────────────────────────────────┘ │ │ │
│  │  │ ┌──────────────────────────────────────────────────┐ │ │ │
│  │  │ │ generic_edr.contain_host (CONTAIN)               │ │ │ │
│  │  │ └──────────────────────────────────────────────────┘ │ │ │
│  │  │ ┌──────────────────────────────────────────────────┐ │ │ │
│  │  │ │ splunk.search_siema (READ)                       │ │ │ │
│  │  │ └──────────────────────────────────────────────────┘ │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Risk Classification                                    │ │ │
│  │  │ - READ: No approval required                            │ │ │
│  │  │ - ENRICH: No approval required                           │ │ │
│  │  │ - MODIFY_LOW: No approval required                       │ │ │
│  │  │ - MODIFY: Approval required                               │ │ │
│  │  │ - CONTAIN: Approval required                              │ │ │
│  │  │ - EXECUTE: Approval required                              │ │ │
│  │  │ - DESTRUCTIVE: Approval required                          │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AI Assistant                                              │ │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Context Management                                      │ │ │
│  │  │ - Incident context                                       │ │ │
│  │  │ - Evidence context                                        │ │ │
│  │  │ - Relationship context                                     │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Tool Selection                                          │ │ │
│  │  │ - Available tools filtering                               │ │ │
│  │  │ - Risk assessment                                          │ │ │
│  │  │ - Authorization check                                       │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Prompt Engineering                                       │ │ │
│  │  │ - System prompts                                          │ │ │
│  │  │ - Context injection                                       │ │ │
│  │  │ - Response formatting                                     │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Database Access Layer                                      │ │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ SQLAlchemy ORM                                         │ │ │
│  │  │ - Model definitions                                      │ │ │
│  │  │ - Relationship mapping                                    │ │ │
│  │  │ - Query construction                                     │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │ Caching (Redis)                                         │ │ │
│  │  │ - Integration configs cache                               │ │ │
│  │  │ - Incident data cache                                      │ │ │
│  │  │ - LRU cache wrapper                                         │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              POSTGRESQL (Source of Truth)                         │
│             (PostgreSQL 16)                                      │
│                                                                  │
│  Core Tables:                                                    │
│  - users, roles, permissions                                     │
│  - incidents                                                     │
│  - incident_events (timeline)                                    │
│  - incident_comments                                             │
│  - incident_observables (evidence)                               │
│  - incident_findings                                             │
│  - incident_relationships                                        │
│  - integration_configs, integration_instances, integration_actions│
│  - automation_scripts                                            │
│  - playbooks                                                     │
│  - approval_requests                                             │
│  - audit_events                                                  │
│  - llm_sessions, llm_messages, llm_tool_calls                    │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                 REDIS (Cache & Events)                            │
│                    (Redis 7)                                     │
│                                                                  │
│  - Integration configs cache                                     │
│  - Incident data cache                                           │
│  - Event broadcasting                                            │
│  - Rate limiting                                                 │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              APACHE AIRFLOW (Internal Orchestration)              │
│               (Internal Service Only)                             │
│                                                                  │
│  Note:                                                             │
│  - NOT exposed to analysts                                        │
│  - NOT used for incident management                               │
│  - Used for long-running workflows                                │
│  - Backend initiates Airflow workflows                            │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              EXTERNAL SECURITY SYSTEMS                            │
│                                                                  │
│  - SIEM (Splunk, Elastic, etc.)                                   │
│  - EDR (MockEDR, etc.)                                        │
│  - Threat Intelligence (ThreatIntel, etc.)                          │
│  - Ticketing (ServiceNow, etc.)                                    │
│  - Email, Web, File Systems (for evidence processing)              │
└──────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Security Boundaries

The platform enforces strict security boundaries at multiple layers:

#### Layer 1: Network Boundaries

```
Internet
  └─> Load Balancer (SSL Termination)
      └─> API Gateway
          └─> Backend Services
              └─> Database (Internal)
```

#### Layer 2: Application Boundaries

```
Frontend App
  └─> FastAPI Backend (ONLY communication)
      └─> Service Layer
          └─> Database Layer
          └─> Integration Layer
          └─> AI Layer
```

#### Layer 3: Data Boundaries

```
PostgreSQL
  └─> SOAR Data ONLY
      └─> No user data from external sources
      └─> No operational data from external sources

Redis
  └─> Cache Data ONLY
      └─> No persistent credentials
      └─> No sensitive data
```

#### Layer 4: AI/LLM Boundaries

```
LLM
  └─> NO direct access to:
      - Database credentials
      - API credentials
      - Airflow credentials
      - OS shell
      - Docker socket
      - Arbitrary filesystem paths
```

### Risk Classification Model

Every integration action is classified by risk level:

| Risk Level | Description | Examples | Approval |
|------------|-------------|----------|----------|
| READ | Read-only operations | Query SIEM, get host | No |
| ENRICH | Enrichment operations | IP lookup, domain lookup | No |
| MODIFY_LOW | Low-impact modifications | Add incident tag | No |
| MODIFY | Moderate modifications | Update external ticket | Yes |
| CONTAIN | Containment actions | Isolate endpoint | Yes |
| EXECUTE | Execution actions | Remote PowerShell | Yes |
| DESTRUCTIVE | Destructive actions | Delete object | Yes |

### Authorization Model

#### Permission Levels

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
```

#### Role-Based Access Control

```
Roles:
  - admin: All permissions
  - analyst: read, create, update (limited)
  - viewer: read only
  - approver: Can approve actions
  - auditor: Read-only access to audit logs
```

### AI Security Model

The AI assistant operates within strict security boundaries:

#### Tool Registration

```python
# Tools are registered with metadata
@tool("threat_intel.lookup_ip", risk_level="READ", requires_approval=False)
async def lookup_ip(ip: str) -> Dict:
    """Look up IP address."""
    ...
```

#### Authorization Flow

```
1. LLM requests tool call
   └─> ToolBroker.validate_request()
       └─> Check if tool is registered
       └─> Check if action is approved (if risk_level requires)
       └─> Validate input schema
           └─> Execute tool
               └─> Log to audit
```

#### Dangerous Actions

```
High-Risk Actions Require Approval:
  1. AI requests action
  2. Backend validates risk level
  3. If high-risk: create approval request
  4. Backend returns: ACTION_REQUIRES_APPROVAL
  5. Analyst reviews and approves
  6. Action executed
  7. Audit logged
```

## Incident Architecture

### Incident Model

An incident is the primary investigation container:

```python
class Incident(Base):
    id: int
    number: str           # e.g., "INC-2026-000184"
    title: str
    severity: IncidentSeverityEnum
    status: IncidentStatusEnum
    owner_id: int
    source: str
    detection_id: str
    hosts: List[Host]
    users: List[User]
    observables: List[Observable]
    findings: List[Finding]
    comments: List[Comment]
    events: List[Event]
    relationships: List[Relationship]
    artifacts: List[Artifact]
    approval_requests: List[ApprovalRequest]
    llm_session: LLMSession
    created_at: datetime
    updated_at: datetime
```

### Incident Timeline

The incident timeline is append-only:

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

### Incident Status Flow

```
OPEN → INVESTIGATING → CONTAINING → RESOLVED/CLOSED

State Transitions:
  - OPEN → INVESTIGATING: First evidence added
  - INVESTIGATING → CONTAINING: Containment action requested
  - CONTAINING → RESOLVED: Containment completed
  - CONTAINING → CLOSED: Investigation closed
```

## Evidence Architecture

### Evidence Model

Evidence has stable IDs for AI reference:

```python
class Observable(Base):
    id: int
    evidence_id: str           # e.g., "EVID-00192"
    incident_id: int
    observable_type: str       # ip, domain, hash, url, file, process
    value: str
    classification: str        # unclassified, malware, benign
    raw_data: JSON
    created_at: datetime
```

### Evidence Classification

AI output distinguishes between:

- **Observed Fact**: "powershell.exe was launched by WINWORD.EXE according to EVID-00192"
- **Inference**: "This suggests document malware"
- **Hypothesis**: "The user might be compromised"
- **Recommendation**: "Investigate this further"

### Evidence Stability

- Stable IDs are assigned on creation
- IDs never change
- Referenced in AI findings
- Preserved in audit logs

## Integration Architecture

### Integration Abstraction

A common abstraction is used for all integrations:

```python
class Integration(Base):
    integration_name: str          # e.g., "threat_intel"
    enabled: bool
    configuration: JSON            # API keys, endpoints, etc.

class IntegrationInstance(Base):
    id: int
    integration_id: int
    instance_name: str
    status: str
    created_at: datetime

class IntegrationAction(Base):
    id: int
    integration_id: int
    action_name: str               # e.g., "lookup_ip"
    description: str
    risk_level: str                # READ, ENRICH, MODIFY, etc.
    requires_approval: bool
    input_schema: JSON
    output_schema: JSON
```

### Integration Execution Flow

```
1. Request: /api/v1/integrations/threat_intel/lookup_ip
2. Validate input schema
3. Check authorization
4. Get integration config
5. Execute action
6. Log audit event
7. Return result
```

### Risk Classification

Each action defines its risk level:

```python
threat_intel.lookup_ip
  - Risk: READ
  - Requires Approval: No

generic_edr.get_host
  - Risk: READ
  - Requires Approval: No

generic_edr.contain_host
  - Risk: CONTAIN
  - Requires Approval: Yes

threat_intel.lookup_hash
  - Risk: ENRICH
  - Requires Approval: No
```

## Playbook Architecture

### Playbook Model

Playbooks are declarative YAML files:

```yaml
name: IP Reputation Check
version: "1.0"
description: "Look up IP reputation and check for threats"
risk_level: READ
requires_approval: false

steps:
  - action: threat_intel.lookup_ip
    input:
      ip_address: "{{ incident.observable_ip }}"
  - action: threatcrowd.lookup_ip
    input:
      ip_address: "{{ incident.observable_ip }}"
```

### Playbook Execution

```python
class Playbook(Base):
    slug: str                    # e.g., "ip-reputation-check"
    name: str
    version: str
    description: str
    yaml_content: JSON           # Parsed YAML
    risk_level: str
    requires_approval: bool
    enabled: bool
    created_at: datetime

class PlaybookRun(Base):
    id: int
    playbook_id: int
    incident_id: int
    status: str                  # running, completed, failed
    started_at: datetime
    completed_at: datetime
    result: JSON

class PlaybookStepRun(Base):
    id: int
    playbook_run_id: int
    step_index: int
    action: str
    status: str
    started_at: datetime
    completed_at: datetime
    result: JSON
```

### Playbook Dependencies

Playbooks support:

- Sequential steps
- Parallel tasks
- Conditional execution
- Error handling
- Retries
- Timeouts

## Automation Architecture

### Automation Script Model

Automation scripts are versioned and sandboxed:

```python
class AutomationScript(Base):
    id: int
    slug: str
    name: str
    version: str
    language: str                # python, javascript
    code: str
    input_schema: JSON
    output_schema: JSON
    risk_level: str
    requires_approval: bool
    enabled: bool

class AutomationRun(Base):
    id: int
    script_id: int
    version: str
    incident_id: int
    input_data: JSON
    status: str
    output_data: JSON
    error: str
    started_at: datetime
    completed_at: datetime
```

### Automation Sandboxing

Automation scripts execute in restricted environments:

```
Restricted Execution Environment:
  - Execution timeout (e.g., 30 seconds)
  - Restricted filesystem
  - Restricted networking
  - Restricted secrets
  - Resource limits
  - Structured JSON input
  - Structured JSON output
```

## AI Investigation Architecture

### AI Investigation Flow

```
1. Analyst creates incident
2. Playbook extracts observables
3. AI analyzes evidence using registered tools
4. AI makes recommendations
5. AI requests high-risk actions
6. Analyst reviews and approves
7. Action executed
8. Timeline updated
```

### LLM Session Model

```python
class LLMSession(Base):
    id: int
    incident_id: int
    model: str
    messages: JSON               # Conversation history
    tool_calls: JSON
    findings: JSON
    started_at: datetime
    completed_at: datetime

class LLMMessage(Base):
    id: int
    session_id: int
    role: str                    # system, user, assistant
    content: str
    created_at: datetime

class LLMTollCall(Base):
    id: int
    session_id: int
    tool: str
    arguments: JSON
    result: JSON
    created_at: datetime

class LLMFinding(Base):
    id: int
    session_id: int
    finding_type: str            # fact, inference, hypothesis, recommendation
    content: str
    evidence_ids: List[str]
    created_at: datetime
```

### Tool Registration

Tools are registered with metadata:

```python
@tool("threat_intel.lookup_ip", 
     description="Look up IP address reputation",
     risk_level="READ",
     requires_approval=False,
     input_schema={"type": "object", "properties": {"ip_address": "string"}},
     output_schema={"type": "object", "properties": {"data": "array"}})
async def lookup_ip(ip_address: str) -> Dict:
    """Look up IP address reputation."""
    ...
```

### AI Tool Execution Flow

```
1. LLM selects tool and arguments
2. ToolBroker.validate_request()
   - Check if tool is registered
   - Check if action is approved (if requires_approval)
   - Validate input schema
3. Execute tool
4. Log to LLM session
5. Return result to LLM
6. LLM uses result for next decision
```

## Audit Architecture

### Audit Event Model

All important actions generate audit events:

```python
class AuditEvent(Base):
    id: int
    event_type: str              # incident.created, evidence.added, etc.
    actor_username: str
    actor_type: str              # user, ai, api
    incident_id: int
    event_data: JSON
    created_at: datetime
```

### Audit Event Types

```
Incident Events:
  - incident.created
  - incident.updated
  - incident.deleted
  - incident.status_changed

Evidence Events:
  - evidence.added
  - evidence.updated
  - evidence.deleted
  - evidence.classified

Integration Events:
  - integration.action_executed
  - integration.config_changed

Playbook Events:
  - playbook.run_started
  - playbook.run_completed
  - playbook.run_failed

Approval Events:
  - approval.requested
  - approval.approved
  - approval.denied

AI Events:
  - ai.investigation_started
  - ai.tool_called
  - ai.finding_generated

Automation Events:
  - automation.run_started
  - automation.run_completed
  - automation.run_failed
```

### Audit Logging

All audit events are logged to:

- PostgreSQL (audit_events table)
- Audit log files (optional)
- SIEM (optional)

## Database Architecture

### Database Design Principles

1. **PostgreSQL is the source of truth**
2. **All data is persisted**
3. **Foreign keys enforce referential integrity**
4. **Indexing optimizes queries**
5. **Soft deletes for critical data**

### Core Tables

| Table | Description | Records |
|-------|-------------|---------|
| users | Platform users | 10-1000 |
| roles | User roles | 5-20 |
| permissions | Available permissions | 50-100 |
| incidents | Incident records | 100-10000+ |
| incident_events | Incident timeline | 10-100 per incident |
| incident_comments | Incident comments | 1-50 per incident |
| incident_observables | Evidence items | 5-100 per incident |
| incident_findings | AI findings | 0-50 per incident |
| incident_relationships | Entity relationships | 0-100 per incident |
| integration_configs | Integration definitions | 10-30 |
| automation_scripts | Script definitions | 5-50 |
| playbooks | Playbook definitions | 5-50 |
| approval_requests | High-risk action approvals | 0-50 |
| audit_events | System audit log | 10-1000 per hour |

### Database Schema

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
  ├── incident_observables (1:N)
  ├── incident_findings (1:N)
  ├── incident_relationships (1:N)
  ├── integration_executions (1:N)

integration_configs
  ├── integration_instances (1:N)
  ├── integration_actions (1:N)

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

## Deployment Architecture

### Development Environment

```
Development
  ├── Backend (localhost:8000)
  ├── Frontend (localhost:3000)
  ├── Database (PostgreSQL in Docker)
  └── Redis (in Docker)
```

### Production Environment

```
Production
  ├── Load Balancer
  │   ├── Backend (N instances)
  │   └── Frontend (N instances)
  ├── Database (Primary + Replicas)
  └── Redis Cluster
```

### Kubernetes Deployment

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

## Monitoring and Observability

### Health Endpoints

```
Health Check:
  - GET /api/v1/health
    - Database connection
    - Redis connection
    - Service status
```

### Metrics

- Incident creation rate
- Integration execution time
- Playbook execution time
- AI response time
- Approval request rate
- Error rates by endpoint

### Logging

```
Log Levels:
  - DEBUG - Detailed debugging info
  - INFO - General operational info
  - WARNING - Unexpected events
  - ERROR - Error conditions
  - CRITICAL - Critical failures

Log Format:
  %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Security Considerations

### Security Principles

1. **Defense in Depth**: Multiple security layers
2. **Least Privilege**: Minimal permissions
3. **Fail Secure**: Deny by default
4. **Audit Everything**: Log all actions
5. **Secure by Default**: No secrets in code

### Do's

- ✅ Validate all tool inputs against schemas
- ✅ Use least privilege
- ✅ Use RBAC
- ✅ Store secrets in environment variables
- ✅ Never store plaintext credentials in DB records
- ✅ Generate audit events for all important actions
- ✅ Approve high-risk actions before execution
- ✅ Treat all incident evidence as untrusted
- ✅ Use stable evidence IDs in AI findings

### Don'ts

- ❌ Do not use `eval()`
- ❌ Do not create unrestricted shell execution
- ❌ Do not expose arbitrary Python execution through APIs
- ❌ Do not store credentials in API responses
- ❌ Do not store credentials in logs
- ❌ Do not store credentials in LLM prompts
- ❌ Do not store credentials in incident comments
- ❌ Do not store credentials in audit messages
- ❌ Do not let LLM determine its own permissions
- ❌ Do not give LLM direct database credentials
- ❌ Do not give LLM Airflow credentials

## Summary

The AI-Native SOAR platform follows a well-organized, layered architecture with:

- **Clear separation of concerns** (models, schemas, services, routes)
- **Comprehensive security boundaries** (network, application, data, AI)
- **Robust risk classification** (READ, ENRICH, CONTAIN, EXECUTE, DESTRUCTIVE)
- **Scalable design** (caching, database indexing, containerization)
- **Audit-ready** (all actions logged)
- **Developer-friendly** (documentation, conventions, tooling)

The architecture supports the complete threat response workflow while maintaining security, maintainability, and scalability.
