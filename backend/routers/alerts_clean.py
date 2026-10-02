"""
Alert CRUD Router (clean, working implementation)
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Alert, Incident, AlertObservable, IncidentObservable, AnalysisQuestion
from utils.number_generator import generate_incident_number
from utils.observable_extractor import extract_observables
from utils.enricher import enrich_value
from utils.llm_client import analyze_alert, ask_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    status: str = "new"
    source_type: str = "manual"
    source_id: Optional[str] = None
    detection_id: Optional[str] = None
    auto_enrich: bool = False


class AlertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    detection_id: Optional[str] = None


def _next_alert_number(db: Session) -> str:
    year = datetime.now().year
    count = db.query(Alert).filter(Alert.number.like(f"ALT-{year}-%")).count()
    seq = count + 1
    number = f"ALT-{year}-{seq:06d}"
    while db.query(Alert).filter(Alert.number == number).first() is not None:
        seq += 1
        number = f"ALT-{year}-{seq:06d}"
    return number


def _next_incident_number(db: Session) -> str:
    year = datetime.now().year
    count = db.query(Incident).filter(Incident.number.like(f"INC-{year}-%")).count()
    seq = count + 1
    number = generate_incident_number(year, seq)
    while db.query(Incident).filter(Incident.number == number).first() is not None:
        seq += 1
        number = generate_incident_number(year, seq)
    return number


def alert_to_dict(a: Alert) -> dict:
    return {
        "id": a.id,
        "number": a.number,
        "title": a.title,
        "description": a.description,
        "severity": a.severity,
        "status": a.status,
        "source_type": a.source_type,
        "source_id": a.source_id,
        "detection_id": a.detection_id,
        "incident_id": a.incident_id,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }


def _alert_observable_to_dict(o: AlertObservable) -> dict:
    return {
        "id": o.id,
        "observable_type": o.observable_type,
        "observable_value": o.observable_value,
        "severity": o.severity,
        "enrichment_status": o.enrichment_status,
        "malicious_score": o.malicious_score,
        "reputation": o.reputation,
        "enrichment_data": o.enrichment_data,
        "enriched_at": o.enriched_at.isoformat() if o.enriched_at else None,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


@router.get("")
def list_alerts(
    offset: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.is_deleted == False)  # noqa: E712
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    alerts = (
        query.order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [alert_to_dict(a) for a in alerts]


@router.post("")
def create_alert(data: AlertCreate, db: Session = Depends(get_db)):
    alert = Alert(
        number=_next_alert_number(db),
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=data.status,
        source_type=data.source_type,
        source_id=data.source_id,
        detection_id=data.detection_id,
    )
    db.add(alert)
    db.flush()  # assign alert.id

    # auto-extract IOCs from title + description
    text = " ".join(x for x in [alert.title, alert.description] if x)
    extracted = extract_observables(text)
    enriched_count = 0
    for item in extracted:
        obs = AlertObservable(
            alert_id=alert.id,
            observable_type=item["type"],
            observable_value=item["value"],
            observed_at=datetime.now(timezone.utc),
        )
        if data.auto_enrich:
            enrichment = enrich_value(item["type"], item["value"])
            if enrichment:
                obs.enrichment_status = "enriched"
                obs.malicious_score = enrichment["score"]
                obs.reputation = enrichment["reputation"]
                obs.enrichment_data = enrichment
                obs.enriched_at = datetime.now(timezone.utc)
                enriched_count += 1
        db.add(obs)

    db.commit()
    db.refresh(alert)
    result = alert_to_dict(alert)
    result["auto_extracted"] = len(extracted)
    result["auto_enriched"] = enriched_count
    return result


@router.get("/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    result = alert_to_dict(alert)
    result["observables"] = [
        _alert_observable_to_dict(o)
        for o in db.query(AlertObservable)
        .filter(AlertObservable.alert_id == alert_id)
        .order_by(AlertObservable.id.asc())
        .all()
    ]
    result["qa_history"] = [
        {
            "id": q.id,
            "question": q.question,
            "answer": q.answer,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in db.query(AnalysisQuestion)
        .filter(
            AnalysisQuestion.entity_type == "alert",
            AnalysisQuestion.entity_id == alert_id,
        )
        .order_by(AnalysisQuestion.created_at.asc())
        .all()
    ]
    return result


@router.post("/{alert_id}/analyze")
def analyze_alert_with_ai(alert_id: int, db: Session = Depends(get_db)):
    """Generate an AI analysis summary for the alert."""
    alert_data = _build_alert_detail_data(alert_id, db)
    if alert_data is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    summary = analyze_alert(alert_data)
    return {"alert_id": alert_id, "summary": summary}


class AskRequest(BaseModel):
    question: str


@router.post("/{alert_id}/ask")
def ask_alert_ai(alert_id: int, data: AskRequest, db: Session = Depends(get_db)):
    """Answer a custom analyst question using the full alert context, persisted."""
    alert_data = _build_alert_detail_data(alert_id, db)
    if alert_data is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    answer = ask_alert(alert_data, data.question)

    # persist Q&A
    db.add(
        AnalysisQuestion(
            entity_type="alert",
            entity_id=alert_id,
            question=data.question,
            answer=answer,
        )
    )
    db.commit()

    return {"alert_id": alert_id, "question": data.question, "answer": answer}


def _build_alert_detail_data(alert_id: int, db: Session):
    """Build a full dict for an alert (incl. observables)."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None

    data = alert_to_dict(alert)
    data["observables"] = [
        _alert_observable_to_dict(o)
        for o in db.query(AlertObservable)
        .filter(AlertObservable.alert_id == alert_id)
        .order_by(AlertObservable.id.asc())
        .all()
    ]
    return data


class ObservableCreate(BaseModel):
    observable_type: str
    observable_value: str


@router.get("/{alert_id}/observables")
def list_alert_observables(alert_id: int, db: Session = Depends(get_db)):
    observables = (
        db.query(AlertObservable)
        .filter(AlertObservable.alert_id == alert_id)
        .order_by(AlertObservable.id.asc())
        .all()
    )
    return [_alert_observable_to_dict(o) for o in observables]


@router.post("/{alert_id}/observables")
def add_alert_observable(alert_id: int, data: ObservableCreate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    observable = AlertObservable(
        alert_id=alert_id,
        observable_type=data.observable_type,
        observable_value=data.observable_value,
        observed_at=datetime.now(timezone.utc),
    )
    db.add(observable)
    db.commit()
    db.refresh(observable)
    return _alert_observable_to_dict(observable)


@router.post("/{alert_id}/observables/extract")
def extract_alert_observables(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    text = " ".join(x for x in [alert.title, alert.description] if x)
    extracted = extract_observables(text)

    existing = {
        (o.observable_type, o.observable_value)
        for o in db.query(AlertObservable).filter(AlertObservable.alert_id == alert_id).all()
    }

    added = []
    for item in extracted:
        key = (item["type"], item["value"])
        if key in existing:
            continue
        obs = AlertObservable(
            alert_id=alert_id,
            observable_type=item["type"],
            observable_value=item["value"],
            observed_at=datetime.now(timezone.utc),
        )
        db.add(obs)
        added.append(item)

    db.commit()
    return {"added": len(added), "observables": added}


@router.post("/{alert_id}/observables/enrich")
def enrich_alert_observables(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    observables = (
        db.query(AlertObservable).filter(AlertObservable.alert_id == alert_id).all()
    )
    results = []
    for obs in observables:
        enrichment = enrich_value(obs.observable_type, obs.observable_value)
        if enrichment:
            obs.enrichment_status = "enriched"
            obs.malicious_score = enrichment["score"]
            obs.reputation = enrichment["reputation"]
            obs.enrichment_data = enrichment
            obs.enriched_at = datetime.now(timezone.utc)
            results.append(
                {
                    "id": obs.id,
                    "observable_type": obs.observable_type,
                    "observable_value": obs.observable_value,
                    "malicious_score": enrichment["score"],
                    "reputation": enrichment["reputation"],
                }
            )
        else:
            obs.enrichment_status = "failed"

    db.commit()
    return {"enriched": len(results), "results": results}


@router.delete("/{alert_id}/observables/{observable_id}")
def delete_alert_observable(alert_id: int, observable_id: int, db: Session = Depends(get_db)):
    observable = (
        db.query(AlertObservable)
        .filter(AlertObservable.id == observable_id, AlertObservable.alert_id == alert_id)
        .first()
    )
    if not observable:
        raise HTTPException(status_code=404, detail="Observable not found")
    db.delete(observable)
    db.commit()
    return {"message": "Observable deleted", "id": observable_id}


@router.put("/{alert_id}")
def update_alert(alert_id: int, data: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(alert, key, value)

    db.commit()
    db.refresh(alert)
    return alert_to_dict(alert)


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_deleted = True
    db.commit()
    return {"message": "Alert deleted successfully", "id": alert_id}


@router.post("/{alert_id}/promote")
def promote_alert_to_incident(alert_id: int, db: Session = Depends(get_db)):
    """Convert an alert into an incident (SOAR core workflow)."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.incident_id:
        raise HTTPException(
            status_code=400,
            detail=f"Alert already promoted to incident {alert.incident_id}",
        )

    incident = Incident(
        number=_next_incident_number(db),
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        status="open",
        priority="medium",
        source_type=alert.source_type,
        detection_id=alert.detection_id,
    )
    db.add(incident)
    db.flush()  # assign incident.id without committing yet

    # copy alert observables to the new incident
    alert_observables = (
        db.query(AlertObservable).filter(AlertObservable.alert_id == alert_id).all()
    )
    for ao in alert_observables:
        incident_obs = IncidentObservable(
            incident_id=incident.id,
            observable_type=ao.observable_type,
            observable_value=ao.observable_value,
            enrichment_status=ao.enrichment_status,
            malicious_score=ao.malicious_score,
            reputation=ao.reputation,
            enrichment_data=ao.enrichment_data,
            enriched_at=ao.enriched_at,
            observed_at=ao.observed_at,
        )
        db.add(incident_obs)

    alert.incident_id = incident.id
    alert.status = "promoted"
    db.commit()
    db.refresh(incident)

    return {
        "incident_id": incident.id,
        "incident_number": incident.number,
        "alert_id": alert.id,
    }
