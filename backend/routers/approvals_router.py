from fastapi import APIRouter, Depends, HTTPException, status
from models.models import IncidentApprovalRequest
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgresql+psycopg2://soar_user:soar_password@localhost:5432/soar",
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

router = APIRouter()


@router.get("/approvals", response_model=None)
async def list_approvals(db: AsyncSession = Depends(get_db)) -> List[IncidentApprovalRequest]:
    """
    List all approval requests
    
    **GET** `/api/v1/approvals`
    """
    approvals = db.query(IncidentApprovalRequest).all()
    return approvals


@router.post("/approvals/{request_id}/approve", response_model=None)
async def approve_request(
    request_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Approve an action
    
    **POST** `/api/v1/approvals/{request_id}/approve`
    """
    # Placeholder implementation
    return {"status": "approved"}


@router.post("/approvals/{request_id}/deny", response_model=None)
async def deny_request(
    request_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Deny an action
    
    **POST** `/api/v1/approvals/{request_id}/deny`
    """
    # Placeholder implementation
    return {"status": "denied"}
