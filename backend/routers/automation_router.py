from fastapi import APIRouter, Depends, HTTPException, status
from models.models import AutomationScript
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


@router.get("/automation", response_model=None)
async def list_automation(db: AsyncSession = Depends(get_db)) -> List[AutomationScript]:
    """
    List all automation scripts
    
    **GET** `/api/v1/automation`
    """
    scripts = db.query(AutomationScript).all()
    return scripts


@router.post("/automation", response_model=None)
async def create_automation(
    script_data: dict,
    db: AsyncSession = Depends(get_db)
) -> AutomationScript:
    """
    Create a new automation script
    
    **POST** `/api/v1/automation`
    """
    script = AutomationScript(
        name=script_data.get("name", ""),
        slug=script_data.get("slug", ""),
        description=script_data.get("description", ""),
        content=script_data.get("content", ""),
        script_type=script_data.get("script_type", "python"),
    )
    
    db.add(script)
    db.commit()
    
    return script


@router.post("/automation/{slug}/run", response_model=None)
async def run_automation(
    slug: str,
    script_data: dict,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Run an automation script
    
    **POST** `/api/v1/automation/{slug}/run`
    """
    # Placeholder implementation
    return {"status": "running"}
