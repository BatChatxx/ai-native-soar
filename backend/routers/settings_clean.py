"""
Settings router: health/status and LLM profile management.

LLM profiles are stored in the local database (PostgreSQL) — never exposed
to the frontend in full (api_key is masked when listing).
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.database import get_db, get_engine
from models.models import Incident, Alert, IncidentObservable, AlertObservable, LLMProfile
from utils.llm_client import test_llm_connection, get_active_profile_id, reset_profile_cache

router = APIRouter(prefix="/settings", tags=["settings"])


def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return key[:6] + "..." + key[-4:]


def _profile_to_dict(p: LLMProfile, include_key: bool = False) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "base_url": p.base_url,
        "model": p.model,
        "api_key": p.api_key if include_key else _mask_key(p.api_key or ""),
        "context_window": p.context_window,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


# ============= Health / status =============

@router.get("/health")
def settings_health(db: Session = Depends(get_db)):
    # database connectivity
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    incident_count = db.query(Incident).filter(Incident.is_deleted == False).count()  # noqa: E712
    alert_count = db.query(Alert).filter(Alert.is_deleted == False).count()  # noqa: E712
    observable_count = db.query(IncidentObservable).count() + db.query(AlertObservable).count()

    # LLM connectivity
    llm_ok, llm_msg = test_llm_connection()

    return {
        "status": "ok" if (db_ok and llm_ok) else "degraded",
        "database": {"connected": db_ok},
        "llm": {"connected": llm_ok, "message": llm_msg},
        "counts": {
            "incidents": incident_count,
            "alerts": alert_count,
            "observables": observable_count,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============= LLM profiles =============

class LLMProfileCreate(BaseModel):
    name: str
    base_url: str
    model: str
    api_key: Optional[str] = None
    context_window: int = 40000


class LLMProfileUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    context_window: Optional[int] = None


@router.get("/llm")
def list_llm_profiles(db: Session = Depends(get_db)):
    profiles = db.query(LLMProfile).order_by(LLMProfile.id.asc()).all()
    return {
        "active_profile_id": get_active_profile_id(db),
        "profiles": [_profile_to_dict(p) for p in profiles],
    }


@router.post("/llm")
def create_llm_profile(data: LLMProfileCreate, db: Session = Depends(get_db)):
    profile = LLMProfile(
        name=data.name,
        base_url=data.base_url,
        model=data.model,
        api_key=data.api_key or "",
        context_window=data.context_window,
        is_active=False,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # If this is the first profile, make it active
    count = db.query(LLMProfile).count()
    if count == 1:
        profile.is_active = True
        db.commit()
        db.refresh(profile)

    reset_profile_cache()
    return _profile_to_dict(profile)


@router.put("/llm/{profile_id}")
def update_llm_profile(profile_id: int, data: LLMProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(LLMProfile).filter(LLMProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="LLM profile not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    reset_profile_cache()
    return _profile_to_dict(profile)


@router.delete("/llm/{profile_id}")
def delete_llm_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(LLMProfile).filter(LLMProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="LLM profile not found")

    was_active = profile.is_active
    db.delete(profile)
    db.commit()

    # If we deleted the active profile, activate the first remaining one
    if was_active:
        remaining = db.query(LLMProfile).order_by(LLMProfile.id.asc()).first()
        if remaining:
            remaining.is_active = True
            db.commit()

    reset_profile_cache()
    return {"message": "LLM profile deleted", "id": profile_id}


@router.post("/llm/{profile_id}/activate")
def activate_llm_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(LLMProfile).filter(LLMProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="LLM profile not found")

    # deactivate all, activate this one
    db.query(LLMProfile).update({LLMProfile.is_active: False})
    profile.is_active = True
    db.commit()
    db.refresh(profile)

    reset_profile_cache()
    return {"message": f"Activated LLM profile '{profile.name}'", "id": profile.id, "is_active": True}
