# Development Guide

## Quick Start

### Initial Setup

```bash
# Clone repository
git clone https://github.com/example/ai-native-soar.git
cd ai-native-soar

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# Install Airflow
pip install apache-airflow

# Install LLM Studio (optional)
pip install lmstudio
```

### Docker Setup (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Access services
# - Frontend: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Airflow: http://localhost:8080
```

---

## Backend Development

### Project Structure

```
backend/
├── main.py                      # FastAPI application
├── models/
│   ├── models.py                # SQLAlchemy ORM models
│   └── database.py              # DB connection/session
├── routers/
│   ├── __init__.py
│   ├── incidents_router.py      # Incident endpoints
│   ├── evidence_router.py       # Evidence endpoints
│   ├── playbooks_router.py      # Playbook endpoints
│   ├── approvals_router.py      # Approval endpoints
│   ├── automation_router.py     # Automation endpoints
│   ├── integrations_router.py   # Integration endpoints
│   └── audit_router.py          # Audit endpoints
├── utils/
│   ├── auth_utils.py            # Authentication helpers
│   ├── validation_utils.py      # Validation helpers
│   └── __init__.py
├── tests/                       # Test files
├── alembic/                     # Database migrations
├── requirements.txt
├── Dockerfile
└── pyproject.toml
```

### Adding a New Endpoint

```python
# File: routers/incidents_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.models import Incident, IncidentCreate
from models.database import get_db
from utils.auth_utils import get_current_user, verify_password

router = APIRouter()

@router.get("/incidents")
async def list_incidents(db: Session = Depends(get_db)):
    """List all incidents."""
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    return {"incidents": [inc.model_dump() for inc in incidents]}

@router.post("/incidents")
async def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create new incident."""
    incident = Incident(
        number=generate_incident_number(),
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        status="open",
        source_type=incident_data.source_type,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident.model_dump()

@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get incident by ID."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.model_dump()

@router.delete("/incidents/{incident_id}")
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete incident (requires approval for DESTRUCTIVE actions)."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Check if DESTRUCTIVE
    if is_destructive_action(incident):
        await require_approval(
            db=db,
            incident_id=incident_id,
            action="delete_incident",
            user=user,
        )
    
    db.delete(incident)
    db.commit()
    return {"message": "Incident deleted"}
```

### Adding Integration Support

```python
# File: routers/integrations_router.py

from fastapi import APIRouter, Depends
from models.database import get_db
from models.models import IntegrationConfig, IntegrationInstanceCreate
from utils.validation_utils import validate_action

router = APIRouter()

@router.get("/integrations")
async def list_integrations(db: Session = Depends(get_db)):
    """List all integrations."""
    configs = db.query(IntegrationConfig).all()
    return {"integrations": [c.model_dump() for c in configs]}

@router.post("/integrations")
async def create_integration(
    integration_config: IntegrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create new integration configuration."""
    config = IntegrationConfig(
        name=integration_config.name,
        category=integration_config.category,
        description=integration_config.description,
        config_schema=integration_config.config_schema,
        action_schemas=integration_config.action_schemas,
        base_url=integration_config.base_url,
        auth_type=integration_config.auth_type,
        enabled=integration_config.enabled,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config.model_dump()

@router.get("/integrations/{name}/instances")
async def list_integration_instances(
    name: str,
    db: Session = Depends(get_db),
):
    """List integration instances."""
    config = db.query(IntegrationConfig).filter(
        IntegrationConfig.name == name
    ).first()
    if not config:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    instances = db.query(IntegrationInstance).filter(
        IntegrationInstance.config_id == config.id
    ).all()
    return {"instances": [i.model_dump() for i in instances]}
```

### Adding AI Tool Registration

```python
# File: routers/ai_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.models import LLMTool, LLMToolCreate
from models.database import get_db

router = APIRouter()

@router.post("/ai/tools")
async def register_ai_tool(
    tool_data: LLMToolCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register a new AI tool."""
    
    # Validate tool configuration
    validated_input = tool_data.input_schema
    
    tool = LLMTool(
        name=tool_data.name,
        path=tool_data.path,
        description=tool_data.description,
        input_schema=validated_input.model_dump_json(),
        output_schema=tool_data.output_schema,
        risk_level=tool_data.risk_level,
        requires_approval=tool_data.requires_approval,
        ai_callable=tool_data.ai_callable,
        enabled=tool_data.enabled,
        metadata=tool_data.metadata,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool.model_dump()

@router.get("/ai/tools/{name}")
async def get_ai_tool(name: str, db: Session = Depends(get_db)):
    """Get AI tool details."""
    tool = db.query(LLMTool).filter(LLMTool.name == name).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool.model_dump()
```

### Adding Playbook Support

```python
# File: routers/playbooks_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Playbook, PlaybookCreate
from models.database import get_db

router = APIRouter()

@router.get("/playbooks")
async def list_playbooks(db: Session = Depends(get_db)):
    """List all playbooks."""
    playbooks = db.query(Playbook).order_by(
        Playbook.created_at.desc()
    ).all()
    return {"playbooks": [p.model_dump() for p in playbooks]}

@router.post("/playbooks")
async def create_playbook(
    playbook_data: PlaybookCreate,
    db: Session = Depends(get_db),
):
    """Create new playbook."""
    playbook = Playbook(
        name=playbook_data.name,
        version=playbook_data.version,
        definition=playbook_data.definition,
        trigger=playbook_data.trigger,
        trigger_config=playbook_data.trigger_config,
        status="active",
        description=playbook_data.description,
        tags=playbook_
