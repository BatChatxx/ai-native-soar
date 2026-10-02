from fastapi import APIRouter, Depends, HTTPException, status
from models.models import IntegrationConfig, IntegrationInstance, IntegrationAction
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


@router.get("/integrations", response_model=None)
async def list_integrations(db: AsyncSession = Depends(get_db)) -> List[IntegrationConfig]:
    """
    List all integrations
    
    **GET** `/api/v1/integrations`
    """
    integrations = db.query(IntegrationConfig).all()
    return integrations


@router.post("/integrations", response_model=None)
async def create_integration(
    integration_data: dict,
    db: AsyncSession = Depends(get_db)
) -> IntegrationConfig:
    """
    Create a new integration
    
    **POST** `/api/v1/integrations`
    """
    integration = IntegrationConfig(
        integration_name=integration_data.get("integration_name", ""),
        display_name=integration_data.get("display_name", ""),
        enabled=integration_data.get("enabled", True),
        configuration=integration_data.get("configuration", None),
    )
    
    db.add(integration)
    db.commit()
    
    return integration


@router.get("/integrations/{integration_name}/actions", response_model=None)
async def list_integration_actions(
    integration_name: str,
    db: AsyncSession = Depends(get_db)
) -> List[IntegrationAction]:
    """
    List actions for an integration
    
    **GET** `/api/v1/integrations/{integration_name}/actions`
    """
    # Note: integration_name here is actually the config id, not the name
    # This is a placeholder - in production, use proper FK relationships
    actions = db.query(IntegrationAction).filter(
        IntegrationAction.integration_config_id == integration_name
    ).all()
    return actions


@router.post("/integrations/{integration_name}/actions", response_model=None)
async def create_integration_action(
    integration_name: str,
    action_data: dict,
    db: AsyncSession = Depends(get_db)
) -> IntegrationAction:
    """
    Create a new integration action
    
    **POST** `/api/v1/integrations/{integration_name}/actions`
    """
    action = IntegrationAction(
        action_name=action_data.get("action_name", ""),
        action_group=action_data.get("action_group", ""),
        description=action_data.get("description", ""),
        risk_level=action_data.get("risk_level", "READ"),
        requires_approval=action_data.get("requires_approval", False),
        input_schema=action_data.get("input_schema", None),
        output_schema=action_data.get("output_schema", None),
        enabled=action_data.get("enabled", True),
    )
    
    db.add(action)
    db.commit()
    
    return action
