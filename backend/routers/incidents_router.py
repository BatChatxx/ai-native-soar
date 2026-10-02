"""
Incident Management Router

Handles incident CRUD operations, number generation, and status transitions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.models import Incident
from schemas.incident_schemas import IncidentCreate, IncidentResponse
from utils.number_generator import generate_incident_number
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    offset: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all incidents
    
    **GET** `/api/v1/incidents`
    
    Query parameters:
    - `offset`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records (default: 20)
    - `status`: Filter by status (optional)
    - `severity`: Filter by severity (optional)
    """
    query = db.query(Incident).offset(offset).limit(limit)
    
    # Filter by status if provided
    if status:
        query = query.filter(Incident.status == status)
    
    # Filter by severity if provided
    if severity:
        query = query.filter(Incident.severity == severity)
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    return incidents


@router.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Create a new incident
    
    **POST** `/api/v1/incidents`
    
    Request body:
    ```json
    {
        "title": "Suspicious Process Detected",
        "description": "PowerShell execution from Word document",
        "severity": "high",
        "source_type": "EDR"
    }
    ```
    """
    # Generate incident number
    incident_number = generate_incident_number(
        year=datetime.now().year,
        sequence=0  # Will be incremented
    )
    
    # Create incident
    incident = Incident(
        incident_number=incident_number,
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        status="open",
        source_type=incident_data.source_type,
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    return incident


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)) -> IncidentResponse:
    """
    Get incident by ID
    
    **GET** `/api/v1/incidents/{incident_id}`
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@router.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an incident
    
    **DELETE** `/api/v1/incidents/{incident_id}`
    
    WARNING: This permanently deletes the incident and all related data.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    db.delete(incident)
    db.commit()
    
    return {"message": "Incident deleted successfully"}


async def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


SessionLocal = SessionLocal
