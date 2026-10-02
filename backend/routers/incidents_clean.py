"""
Incident CRUD Router (clean, working implementation)
"""
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Incident, IncidentEvent, IncidentComment, Alert, IncidentObservable, AnalysisQuestion
from utils.number_generator import generate_incident_number
from utils.observable_extractor import extract_observables
from utils.enricher import enrich_value
from utils.llm_client import analyze_incident, ask_incident

router = APIRouter(prefix="/incidents", tags=["incidents"])


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    status: str = "open"
    priority: str = "medium"
    source_type: str = "manual"
    detection_id: Optional[str] = None
    detection_source: Optional[str] = None
    auto_enrich: bool = False


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    source_type: Optional[str] = None
    detection_id: Optional[str] = None
    detection_source: Optional[str] = None


def _next_number(db: Session) -> str:
    """Generate a unique incident number like INC-2026-000001."""
    year = datetime.now().year
    count = db.query(Incident).filter(Incident.number.like(f"INC-{year}-%")).count()
    seq = count + 1
    number = generate_incident_number(year, seq)
    while db.query(Incident).filter(Incident.number == number).first() is not None:
        seq += 1
        number = generate_incident_number(year, seq)
    return number


def incident_to_dict(i: Incident) -> dict:
    return {
        "id": i.id,
        "number": i.number,
        "title": i.title,
        "description": i.description,
        "severity": i.severity,
        "status": i.status,
        "priority": i.priority,
        "source_type": i.source_type,
        "detection_id": i.detection_id,
        "detection_source": i.detection_source,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
    }


@router.get("")
def list_incidents(
    offset: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Incident).filter(Incident.is_deleted == False)  # noqa: E712
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    incidents = (
        query.order_by(Incident.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [incident_to_dict(i) for i in incidents]


@router.post("")
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(
        number=_next_number(db),
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=data.status,
        priority=data.priority,
        source_type=data.source_type,
        detection_id=data.detection_id,
        detection_source=data.detection_source,
    )
    db.add(incident)
    db.flush()  # assign incident.id

    # auto-extract IOCs from title + description
    text = " ".join(x for x in [incident.title, incident.description] if x)
    extracted = extract_observables(text)
    enriched_count = 0
    for item in extracted:
        obs = IncidentObservable(
            incident_id=incident.id,
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
    db.refresh(incident)
    result = incident_to_dict(incident)
    result["auto_extracted"] = len(extracted)
    result["auto_enriched"] = enriched_count
    return result


@router.get("/{incident_id}/events")
def list_incident_events(incident_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(IncidentEvent)
        .filter(IncidentEvent.incident_id == incident_id, IncidentEvent.is_deleted == False)  # noqa: E712
        .order_by(IncidentEvent.timestamp.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None


@router.post("/{incident_id}/events")
def add_incident_event(incident_id: int, data: EventCreate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    event = IncidentEvent(
        incident_id=incident_id,
        title=data.title,
        description=data.description,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
    }


@router.get("/{incident_id}/comments")
def list_incident_comments(incident_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(IncidentComment)
        .filter(IncidentComment.incident_id == incident_id, IncidentComment.is_deleted == False)  # noqa: E712
        .order_by(IncidentComment.created_at.asc())
        .all()
    )
    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in comments
    ]


class CommentCreate(BaseModel):
    content: str


class ObservableCreate(BaseModel):
    observable_type: str
    observable_value: str


def _observable_to_dict(o: IncidentObservable) -> dict:
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


@router.get("/{incident_id}/observables")
def list_observables(incident_id: int, db: Session = Depends(get_db)):
    observables = (
        db.query(IncidentObservable)
        .filter(IncidentObservable.incident_id == incident_id)
        .order_by(IncidentObservable.id.asc())
        .all()
    )
    return [_observable_to_dict(o) for o in observables]


@router.post("/{incident_id}/observables")
def add_observable(incident_id: int, data: ObservableCreate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    observable = IncidentObservable(
        incident_id=incident_id,
        observable_type=data.observable_type,
        observable_value=data.observable_value,
        observed_at=datetime.now(timezone.utc),
    )
    db.add(observable)
    db.commit()
    db.refresh(observable)
    return _observable_to_dict(observable)


@router.post("/{incident_id}/observables/extract")
def extract_incident_observables(incident_id: int, db: Session = Depends(get_db)):
    """Extract IOCs from the incident description and save them as observables."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # combine title + description for extraction
    text = " ".join(x for x in [incident.title, incident.description] if x)
    extracted = extract_observables(text)

    existing = {
        (o.observable_type, o.observable_value)
        for o in db.query(IncidentObservable)
        .filter(IncidentObservable.incident_id == incident_id)
        .all()
    }

    added = []
    for item in extracted:
        key = (item["type"], item["value"])
        if key in existing:
            continue
        obs = IncidentObservable(
            incident_id=incident_id,
            observable_type=item["type"],
            observable_value=item["value"],
            observed_at=datetime.now(timezone.utc),
        )
        db.add(obs)
        added.append(item)

    db.commit()
    return {"added": len(added), "observables": added}


@router.post("/{incident_id}/observables/enrich")
def enrich_incident_observables(incident_id: int, db: Session = Depends(get_db)):
    """Enrich all observables of an incident against the threat-intel feed."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    observables = (
        db.query(IncidentObservable)
        .filter(IncidentObservable.incident_id == incident_id)
        .all()
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
                    "tags": enrichment.get("tags", []),
                }
            )
        else:
            obs.enrichment_status = "failed"

    db.commit()
    return {"enriched": len(results), "results": results}


@router.delete("/{incident_id}/observables/{observable_id}")
def delete_observable(incident_id: int, observable_id: int, db: Session = Depends(get_db)):
    observable = (
        db.query(IncidentObservable)
        .filter(
            IncidentObservable.id == observable_id,
            IncidentObservable.incident_id == incident_id,
        )
        .first()
    )
    if not observable:
        raise HTTPException(status_code=404, detail="Observable not found")
    db.delete(observable)
    db.commit()
    return {"message": "Observable deleted", "id": observable_id}


@router.post("/{incident_id}/comments")
def add_incident_comment(incident_id: int, data: CommentCreate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    comment = IncidentComment(
        incident_id=incident_id,
        content=data.content,
        created_at=datetime.now(timezone.utc),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


@router.get("/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # source alert (reverse relation)
    source_alert = db.query(Alert).filter(Alert.incident_id == incident_id).first()

    result = incident_to_dict(incident)
    result["source_alert"] = (
        {"id": source_alert.id, "number": source_alert.number, "title": source_alert.title}
        if source_alert
        else None
    )
    result["events"] = [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in db.query(IncidentEvent)
        .filter(IncidentEvent.incident_id == incident_id, IncidentEvent.is_deleted == False)  # noqa: E712
        .order_by(IncidentEvent.timestamp.desc())
        .all()
    ]
    result["comments"] = [
        {
            "id": c.id,
            "content": c.content,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in db.query(IncidentComment)
        .filter(IncidentComment.incident_id == incident_id, IncidentComment.is_deleted == False)  # noqa: E712
        .order_by(IncidentComment.created_at.asc())
        .all()
    ]
    result["observables"] = [
        _observable_to_dict(o)
        for o in db.query(IncidentObservable)
        .filter(IncidentObservable.incident_id == incident_id)
        .order_by(IncidentObservable.id.asc())
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
            AnalysisQuestion.entity_type == "incident",
            AnalysisQuestion.entity_id == incident_id,
        )
        .order_by(AnalysisQuestion.created_at.asc())
        .all()
    ]
    return result


@router.post("/{incident_id}/analyze")
def analyze_incident_with_ai(incident_id: int, db: Session = Depends(get_db)):
    """Generate an AI analysis summary for the incident."""
    incident_data = _build_incident_detail_data(incident_id, db)
    if incident_data is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    summary = analyze_incident(incident_data)
    return {"incident_id": incident_id, "summary": summary}


class AskRequest(BaseModel):
    question: str


@router.post("/{incident_id}/ask")
def ask_incident_ai(incident_id: int, data: AskRequest, db: Session = Depends(get_db)):
    """Answer a custom analyst question using the full incident context, persisted."""
    incident_data = _build_incident_detail_data(incident_id, db)
    if incident_data is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    answer = ask_incident(incident_data, data.question)

    # persist Q&A
    db.add(
        AnalysisQuestion(
            entity_type="incident",
            entity_id=incident_id,
            question=data.question,
            answer=answer,
        )
    )
    db.commit()

    return {"incident_id": incident_id, "question": data.question, "answer": answer}


def _build_incident_detail_data(incident_id: int, db: Session):
    """Build a full dict for an incident (incl. observables, events, comments)."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return None

    data = incident_to_dict(incident)
    data["observables"] = [
        _observable_to_dict(o)
        for o in db.query(IncidentObservable)
        .filter(IncidentObservable.incident_id == incident_id)
        .order_by(IncidentObservable.id.asc())
        .all()
    ]
    data["events"] = [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in db.query(IncidentEvent)
        .filter(IncidentEvent.incident_id == incident_id, IncidentEvent.is_deleted == False)  # noqa: E712
        .order_by(IncidentEvent.timestamp.desc())
        .all()
    ]
    data["comments"] = [
        {
            "id": c.id,
            "content": c.content,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in db.query(IncidentComment)
        .filter(IncidentComment.incident_id == incident_id, IncidentComment.is_deleted == False)  # noqa: E712
        .order_by(IncidentComment.created_at.asc())
        .all()
    ]
    return data


@router.put("/{incident_id}")
def update_incident(incident_id: int, data: IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(incident, key, value)

    db.commit()
    db.refresh(incident)
    return incident_to_dict(incident)


@router.delete("/{incident_id}")
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.is_deleted = True
    db.commit()
    return {"message": "Incident deleted successfully", "id": incident_id}
