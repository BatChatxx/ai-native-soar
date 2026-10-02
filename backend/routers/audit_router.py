from fastapi import APIRouter, Depends
from models.models import AuditEvent
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


@router.get("/audit", response_model=None)
async def list_audit(db: AsyncSession = Depends(get_db)) -> List[AuditEvent]:
    """
    List audit events
    
    **GET** `/api/v1/audit`
    """
    events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()
    return events
