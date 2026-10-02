"""
Dashboard summary router.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Incident, Alert, IncidentObservable, AlertObservable

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    incidents = db.query(Incident).filter(Incident.is_deleted == False).all()  # noqa: E712
    alerts = db.query(Alert).filter(Alert.is_deleted == False).all()  # noqa: E712

    # severity distribution
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for i in incidents:
        if i.severity in severity_counts:
            severity_counts[i.severity] += 1

    # incident status distribution
    status_counts: dict = {}
    for i in incidents:
        s = i.status or "unknown"
        status_counts[s] = status_counts.get(s, 0) + 1

    # alert status distribution
    alert_status_counts: dict = {}
    for a in alerts:
        s = a.status or "unknown"
        alert_status_counts[s] = alert_status_counts.get(s, 0) + 1

    # malicious/suspicious/clean observable stats (incidents + alerts)
    obs_stats = {"malicious": 0, "suspicious": 0, "clean": 0, "unknown": 0, "total": 0}
    incident_obs = db.query(IncidentObservable).all()
    alert_obs = db.query(AlertObservable).all()
    for o in list(incident_obs) + list(alert_obs):
        obs_stats["total"] += 1
        rep = o.reputation or "unknown"
        if rep in obs_stats:
            obs_stats[rep] += 1

    # recent items
    recent_incidents = (
        db.query(Incident)
        .filter(Incident.is_deleted == False)  # noqa: E712
        .order_by(Incident.created_at.desc())
        .limit(5)
        .all()
    )
    recent_alerts = (
        db.query(Alert)
        .filter(Alert.is_deleted == False)  # noqa: E712
        .order_by(Alert.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "totals": {
            "incidents": len(incidents),
            "alerts": len(alerts),
            "critical": severity_counts["critical"],
            "malicious_observables": obs_stats["malicious"],
        },
        "severity_counts": severity_counts,
        "status_counts": status_counts,
        "alert_status_counts": alert_status_counts,
        "observable_stats": obs_stats,
        "recent_incidents": [
            {
                "id": i.id,
                "number": i.number,
                "title": i.title,
                "severity": i.severity,
                "status": i.status,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in recent_incidents
        ],
        "recent_alerts": [
            {
                "id": a.id,
                "number": a.number,
                "title": a.title,
                "severity": a.severity,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in recent_alerts
        ],
    }
