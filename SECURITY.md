# Security Guidelines

## Security Architecture Overview

This platform follows a "security by design" approach with strict boundaries and least privilege principles.

### Core Security Principles

1. **Zero Trust**: Never trust, always verify
2. **Least Privilege**: Give only the permissions needed
3. **Defense in Depth**: Multiple layers of security
4. **Fail Secure**: Default deny when in doubt
5. **Audit Everything**: Log all important actions
6. **Separation of Concerns**: Isolate different functions

## Security Boundaries

### Architecture Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                  ANALYST (Human User)                        │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                REACT FRONTEND (localhost:3000)               │
│  - No direct database access                                  │
│  - No direct external system access                           │
│  - Only communicates with FastAPI backend                     │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            FASTAPI BACKEND (localhost:8000)                  │
│  - Validates all inputs                                       │
│  - Enforces authorization                                     │
│  - Sanitizes all outputs                                      │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         POSTGRESQL (Source of Truth)                         │
│  - Credentials never in API responses                         │
│  - Sensitive columns encrypted                                │
│  - All access logged                                          │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│        APACHE AIRFLOW (Internal Orchestration)               │
│  - NOT the incident database                                  │
│  - NOT the analyst UI                                         │
│  - NOT the authentication authority                           │
│  - Backend initiates and monitors workflows                   │
└─────────────────────────────────────────────────────────────┘
```

### AI Security Boundaries

**The LLM must NEVER directly access:**

- ❌ Database credentials
- ❌ API credentials
- ❌ Airflow credentials
- ❌ Operating system shell
- ❌ Docker socket
- ❌ Arbitrary filesystem paths
- ❌ Arbitrary Python execution

**The LLM may only use:**

- ✅ Registered tools via tool broker
- ✅ Pre-validated tool schemas
- ✅ Incidental read operations (READ/ENRICH)
- ✅ High-risk actions via approval workflow

**Tool Broker Architecture:**

```
LLM Request
    │
    ▼
┌─────────────────────────────────────────┐
│      Tool Broker                        │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Registered Tools               │   │
│  │  - get_incident()               │   │
│  │  - get_evidence()                │   │
│  │  - get_process_tree()           │   │
│  │  - search_siem()                │   │
│  │  - lookup_hash()                │   │
│  │  - lookup_ip()                  │   │
│  │  - lookup_user()                │   │
│  │  - search_related_incidents()   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Dangerous Actions               │   │
│  │  - contain_host()               │   │
│  │  - isolate_endpoint()           │   │
│  │  - run_rtr_command()            │   │
│  │                                   │   │
│  │  Response: ACTION_REQUIRES_      │   │
│  │  APPROVAL APR-000123            │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Integration Abstraction Layer          │
│  - Validates input schemas               │
│  - Enforces risk classification          │
│  - Routes to appropriate integration    │
│  - Logs all actions                      │
└─────────────────────────────────────────┘
```

## Risk Classification

### Action Risk Levels

| Level | Description | Examples | Approval Required |
|-------|-------------|----------|-------------------|
| **READ** | Read-only operations | Query SIEM, retrieve host, lookup detection | ❌ No |
| **ENRICH** | Enrichment operations | IP reputation lookup, domain lookup, hash reputation | ❌ No |
| **MODIFY_LOW** | Low-risk modifications | Add incident tag, update incident metadata | ❌ No |
| **MODIFY** | Moderate modifications | Modify external ticket, update identity info | ✅ Yes |
| **CONTAIN** | Containment actions | Isolate endpoint, disable account, block indicator | ✅ Yes |
| **EXECUTE** | Execution operations | Endpoint RTR command, remote PowerShell | ✅ Yes |
| **DESTRUCTIVE** | Destructive operations | Delete object, destructive quarantine | ✅ Yes |

### Risk Classification Examples

```python
# Integration Action Examples

crowdstrike:
  get_host:
    risk: READ
    requires_approval: false
    description: "Get host details"

  get_process_tree:
    risk: READ
    requires_approval: false
    description: "Get process tree"

  contain_host:
    risk: CONTAIN
    requires_approval: true
    description: "Isolate host from network"

  run_rtr_command:
    risk: EXECUTE
    requires_approval: true
    description: "Run RTR remote command"

virustotal:
  lookup_ip:
    risk: READ
    requires_approval: false
    description: "Check IP reputation"

  lookup_hash:
    risk: READ
    requires_approval: false
    description: "Check hash reputation"

splunk:
  search:
    risk: READ
    requires_approval: false
    description: "Search SIEM"

  tail_logs:
    risk: READ
    requires_approval: false
    description: "Tail logs"

  modify_alert:
    risk: MODIFY
    requires_approval: true
    description: "Modify alert status"
```

## Secret Management

### Storage

**Never store plaintext credentials in:**

- ❌ PostgreSQL tables
- ❌ Integration configuration records
- ❌ API responses
- ❌ Logs
- ❌ LLM prompts
- ❌ Incident comments
- ❌ Audit messages

**Use encrypted storage or external secret management:**

- ✅ Environment variables (DO_NOT_STORE_IN_DB)
- ✅ Docker secrets
- ✅ HashiCorp Vault
- ✅ AWS Secrets Manager
- ✅ Azure Key Vault
- ❌ Never in database records

### Environment Variables

```bash
# Required in .env (never commit to git)
POSTGRES_PASSWORD=your_secure_password_here
SOAR_API_SECRET=your_api_secret_here

# Integration credentials (use external secret storage)
# DO NOT store these in integration_configs table
# VT_API_KEY=vt_api_key_here
# CS_CLIENT_SECRET=cs_client_secret_here
# SPLUNK_HEC_TOKEN=splunk_token_here
```

### API Responses

**Never include credentials in API responses:**

```python
# ❌ BAD - Include credentials in response
{
  "status": "success",
  "data": {
    "host": "WS123",
    "user": "attacker",
    "password": "secret123"  # NEVER include this
  }
}

# ✅ GOOD - Include only necessary data
{
  "status": "success",
  "data": {
    "host": "WS123",
    "user": "attacker"
    # Password filtered out
  }
}
```

## Input Validation

### Schema Validation

All tool inputs must be validated against schemas:

```python
from pydantic import BaseModel, Field

class LookupIPInput(BaseModel):
    ip_address: str = Field(..., min_length=7, max_length=15)
    query: str = Field(default="reputation", min_length=1)

class LookupHashInput(BaseModel):
    hash: str = Field(..., pattern=r"^[a-fA-F0-9]{32,64}$")
    query: str = Field(default="reputation")
```

### Validation Rules

1. **Validate all inputs against schemas**
2. **Validate all outputs where appropriate**
3. **Reject inputs with invalid schemas**
4. **Log validation errors with context**

```python
# ✅ GOOD - Validate before processing
@router.post("/api/v1/incidents/{incident_id}/evidence")
async def add_evidence(
    incident_id: str,
    evidence: EvidenceInput
):
    # Validate input
    validated = evidence_schema.validate(evidence)
    
    # Check authorization
    if not await check_permission("incident:write", incident_id):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Process
    await incident_service.add_evidence(incident_id, validated)
```

## Output Sanitization

### Filtering Sensitive Data

**Filter sensitive data from API responses:**

```python
# ✅ GOOD - Filter sensitive columns
class IncidentResponse(BaseModel):
    id: int
    number: str
    title: str
    status: str
    severity: str
    created_at: datetime
    # password, credit_card, ssh_key, etc. filtered out
    
def sanitize_host_data(data):
    sensitive_fields = ["password", "secret", "token", "key", "credential"]
    for field in sensitive_fields:
        if field in data:
            data[field] = "FILTERED"
    return data
```

### Error Messages

**Never expose internal details in error messages:**

```python
# ❌ BAD - Exposes internal error
{"detail": "Database connection failed: psycopg2.Error: connection refused"}

# ✅ GOOD - Generic error message
{"detail": "Unable to process request"}

# For debugging, log full error server-side:
logger.error(f"Database connection failed: {e}")
```

## Audit Logging

### Log All Important Actions

**Every action should generate audit events:**

```python
async def execute_action(action_name: str, incident_id: int, result: Any):
    # Execute action
    result = await integration_service.execute(incident_id, action_name)
    
    # Generate audit event
    await audit_service.create(
        incident_id=incident_id,
        actor_username="analyst_john",
        action=action_name,
        resource_type="integration_execution",
        risk_level=get_risk_level(action_name),
        response=result.status,
        event_data={"result": result.data},
        event_type="integration_executed"
    )
    
    return result
```

### Audit Event Structure

```json
{
  "id": 1234,
  "incident_id": 42,
  "actor_username": "analyst_john",
  "action": "virustotal.lookup_ip",
  "resource_type": "integration_execution",
  "risk_level": "read",
  "response": "success",
  "error_message": null,
  "event_type": "integration_executed",
  "event_data": {
    "ip": "192.168.1.1",
    "report": {...}
  },
  "created_at": "2026-01-15T10:30:00Z"
}
```

## Authorization Flow

### RBAC Implementation

```python
class Permission:
    incident_read = "incident:read"
    incident_write = "incident:write"
    incident_delete = "incident:delete"
    integration_read = "integration:read"
    integration_write = "integration:write"
    playbook_read = "playbook:read"
    playbook_execute = "playbook:execute"
    ai_use = "ai:use"
    approval_request = "approval:request"
    approval_approve = "approval:approve"

class Role:
    SOC_ANALYST = "soc_analyst"
    SOC_MANAGER = "soc_manager"
    SOC_LEAD = "soc_lead"
    AUDITOR = "auditor"
```

### Authorization Checks

```python
async def execute_action(action_name: str, actor: User, incident: Incident) -> bool:
    # Check if actor has permission
    action_risk = get_action_risk(action_name)
    required_permission = get_permission_for_risk(action_risk)
    
    if not await check_permission(required_permission, actor):
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )
    
    return True
```

## Integration Security

### Integration Configuration

**Never store plaintext credentials in DB:**

```python
# ❌ BAD - Store plaintext credentials
integration_configs:
  - integration_name: virustotal
    configuration:
      api_key: "vt_api_key_here"  # NEVER!
      enabled: true

# ✅ GOOD - Use encrypted storage or external secrets
integration_configs:
  - integration_name: virustotal
    configuration:
      api_key_encrypted: "encrypted_api_key"
      vault_path: "secret/data/virustotal"
      enabled: true
```

### Integration Execution

**Validate inputs, enforce risk classification:**

```python
async def execute_integration_action(
    incident_id: int,
    integration_config: IntegrationConfig,
    action_name: str,
    input_data: dict
) -> IntegrationExecution:
    # 1. Validate integration config
    if not integration_config.enabled:
        raise HTTPException(400, "Integration not enabled")
    
    # 2. Validate inputs
    input_schema = get_action_schema(action_name)
    validated = input_schema.validate(input_data)
    
    # 3. Check authorization
    if not await check_authorization(
        integration_config, action_name, input_data
    ):
        raise HTTPException(403, "Permission denied")
    
    # 4. Determine risk level
    risk_level = get_risk_level(action_name)
    
    # 5. Check for required approval
    if risk_level in ["MODIFY", "CONTAIN", "EXECUTE", "DESTRUCTIVE"]:
        if not await check_approval_required(risk_level, action_name):
            # Request approval
            approval_request = await create_approval_request(
                incident_id,
                integration_config,
                action_name,
                validated
            )
            return approval_request
    
    # 6. Execute action (with timeout)
    try:
        result = await integration_executor.execute(
            integration_config,
            action_name,
            validated,
            timeout=30  # seconds
        )
        
        # 7. Log audit event
        await audit_service.create(...)
        
        return result
        
    except Exception as e:
        # 8. Log error
        await audit_service.create(..., error=str(e))
        raise
```

## AI Security

### Prompt Injection Prevention

**Never allow prompt injection:**

```python
# ❌ BAD - User input in prompt
prompt = f"Analyze this evidence:\n{user_provided_evidence}"

# ✅ GOOD - Sanitize and structure input
sanitized_evidence = sanitize_evidence(user_provided_evidence)
prompt = (
    "Analyze this evidence for security threats. "
    "Only use information provided in the evidence section. "
    "Do not use any external knowledge.\n\n"
    "Evidence (untrusted):\n" + sanitized_evidence
)
```

### Output Validation

**Validate AI outputs:**

```python
# ❌ BAD - Trust AI output directly
ai_finding = llm.generate(prompt)
# Store directly without validation

# ✅ GOOD - Validate AI output
class Finding(BaseModel):
    id: str
    incident_id: int
    evidence_id: str
    finding_type: str
    severity: str
    description: str
    recommended_actions: List[str]

try:
    validated_finding = Finding.model_validate_json(ai_finding)
    # Store validated finding
except ValidationError as e:
    logger.error(f"Invalid AI finding: {e}")
    # Reject finding
```

### Dangerous Actions

**Always require approval for dangerous actions:**

```python
async def ai_request_containment(host_id: int) -> Dict:
    """AI requests host containment."""
    
    # AI cannot directly request containment
    # Must go through approval workflow
    
    approval_request = await create_approval_request(
        incident_id=incident_id,
        actor_username="ai_assistant",
        action="crowdstrike.contain_host",
        resource_type="host",
        risk_level="CONTAIN",
        event_data={
            "host_id": host_id,
            "reason": "AI detected malicious activity"
        },
        event_type="ai_request_action"
    )
    
    return {
        "status": "ACTION_REQUIRES_APPROVAL",
        "approval_request_id": approval_request.id
    }
```

## Incident Evidence Handling

### Evidence Classification

**Classify all evidence:**

```python
EvidenceClassification:
  - untrusted: External sources (emails, webpages, logs)
  - internal: Internal systems (EDR, SIEM, ticketing)
  - public: Public information (OSINT)
```

### Untrusted Data Handling

**Treat all incident evidence as untrusted:**

```python
# Example untrusted sources:
untrusted_sources = [
    "emails",
    "webpages",
    "logs",
    "process command lines",
    "PowerShell",
    "documents",
    "EDR telemetry",
    "SIEM events",
    "ticket comments",
    "files",
    "malware output"
]

# Content in evidence must NEVER be interpreted as instructions:
# ❌ BAD - Treat evidence content as instructions
if user_input == "delete_account":
    delete_account()

# ✅ GOOD - Validate against predefined schemas
valid_actions = ["read_host", "query_siem", "lookup_ip"]
if user_input in valid_actions:
    execute_action(user_input)
```

## Database Security

### PostgreSQL Configuration

```
# postgresql.conf security settings
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'

# Password hashing
password_encryption_method = 'scrypt'

# Connection limits
max_connections = 100

# Log all connections
log_connections = on
log_disconnections = on

# Audit logging
log_statement = 'ddl'
log_min_duration_statement = 1000
```

### Table-Level Security

**Encrypt sensitive columns:**

```sql
-- Example: Encrypt user credentials
ALTER TABLE users ADD COLUMN password_hash TEXT;
ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;

-- Use encryption functions
CREATE FUNCTION encrypt_column(text) RETURNS TEXT AS $$
BEGIN
    RETURN crypt($1, gen_random_uuid());
END;
$$ LANGUAGE plpgsql;
```

## API Security

### Rate Limiting

```python
# Rate limit API endpoints
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100 per minute")
@router.get("/api/v1/incidents/")
async def list_incidents(request):
    pass
```

### CORS Configuration

```python
# CORS setup in main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment Security

### Docker Security

```dockerfile
# Multi-stage build
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY . .
RUN useradd --create-home --shell /bin/bash soar && \
    chown -R soar:soar /app
USER soar
```

### Kubernetes Security (if applicable)

```yaml
# Pod security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false

# Network policies
networkPolicies:
  - ingress:
      - from:
          - podSelector:
              matchLabels:
                app: react-frontend
        ports:
          - port: 8000
```

## Monitoring and Alerting

### Key Metrics

- API error rate (> 5% = alert)
- Database connection failures
- Integration execution failures
- AI service unresponsiveness
- Approval queue size (> 100 = alert)
- Large response sizes
- Slow queries (> 5 seconds)

### Security Alerts

- Unauthorized access attempts
- Bulk data access
- High-risk action execution
- Approval denied patterns
- Unusual login locations
- Multiple failed login attempts

## Incident Response

### Security Incidents

**Categories:**

1. **Authentication Compromise**
   - Invalid login attempts
   - Session hijacking
   - Credential theft

2. **Data Breach**
   - Unauthorized data access
   - Data exfiltration
   - Sensitive data leakage

3. **Malicious Use**
   - Unauthorized integration use
   - Dangerous action execution
   - Privilege escalation

4. **System Compromise**
   - Container escape
   - Lateral movement
   - Infrastructure takeover

### Response Procedures

1. **Detect**: Monitor for indicators
2. **Contain**: Isolate affected systems
3. **Investigate**: Gather evidence
4. **Eradicate**: Remove threat
5. **Recover**: Restore systems
6. **Learn**: Document and improve

## Compliance Considerations

### Data Protection

- Encrypt sensitive data at rest
- Encrypt data in transit
- Implement access controls
- Audit data access
- Retention policies
- Data deletion procedures

### Access Control

- Role-based access control
- Principle of least privilege
- Multi-factor authentication
- Session management
- Access reviews

## Security Testing

### Static Analysis

```bash
# Run security linters
pip install bandit
bandit -r backend/

# Run SAST tools
pip install semgrep
semgrep --config auto backend/
```

### Dynamic Analysis

```bash
# Run security tests
docker compose exec backend python -m pytest tests/security/ -v

# Run penetration tests
docker compose exec backend python -m pytest tests/pentest/ -v
```

## Security Checklist

### Development

- [ ] All inputs validated against schemas
- [ ] All outputs sanitized
- [ ] Authorization checks in place
- [ ] Audit logging enabled
- [ ] Secrets in environment variables
- [ ] No eval() or arbitrary code execution
- [ ] Rate limiting configured

### Deployment

- [ ] PostgreSQL encrypted
- [ ] Connections use SSL
- [ ] Docker images minimal
- [ ] Non-root user running app
- [ ] Network policies configured
- [ ] Health checks working

### Operations

- [ ] Monitoring enabled
- [ ] Alerting configured
- [ ] Incident response plan
- [ ] Backup and restore tested
- [ ] Security reviews scheduled

---

**Last Updated**: 2026-01-15
