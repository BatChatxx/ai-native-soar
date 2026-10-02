"""
Phishing analysis router: upload an .eml file and get a structured analysis.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db
from models.models import Incident, IncidentObservable
from utils.phishing_analyzer import analyze_eml, parse_eml, extract_indicators
from utils.llm_client import chat
from utils.number_generator import generate_incident_number

router = APIRouter(prefix="/phishing", tags=["phishing"])


@router.post("/analyze")
def analyze_phishing_email(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload an .eml file and run the full phishing analysis pipeline."""
    if not file.filename or not file.filename.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail="Only .eml files are supported")

    raw = file.file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        result = analyze_eml(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse email: {e}")

    return {
        "filename": file.filename,
        "size": len(raw),
        **result,
    }


class AIAnalysisRequest(BaseModel):
    parsed: dict
    indicators: dict
    scored: list


@router.post("/ai-analysis")
def ai_phishing_analysis(data: AIAnalysisRequest):
    """Generate an AI analysis of a phishing email using the LLM."""
    prompt = _build_ai_prompt(data.parsed, data.indicators, data.scored)
    answer = chat(prompt, max_tokens=2000)
    return {"analysis": answer}


def _build_ai_prompt(parsed: dict, indicators: dict, scored: list) -> str:
    scored_str = "\n".join(
        f"- {s['type']}={s['value']} (score {s.get('score', 0)}, {s.get('reputation', 'unknown')})"
        for s in scored
    ) or "(none)"

    auth = parsed.get("auth_results") or {}
    return f"""You are a phishing email analyst. Analyze the following email and provide:
1. Is this a phishing / malicious email? (Yes/No + confidence)
2. What are the key red flags?
3. What is the likely attack purpose (credential theft, malware, etc.)?
4. Recommended actions for the recipient/security team.

EMAIL:
- Subject: {parsed.get('subject')}
- From: {parsed.get('sender')}
- To: {parsed.get('to')}
- Date: {parsed.get('date')}
- SPF: {auth.get('spf', 'N/A')}
- DKIM: {auth.get('dkim', 'N/A')}
- DMARC: {auth.get('dmarc', 'N/A')}
- URLs: {', '.join(indicators.get('urls', [])[:8]) or '(none)'}
- Domains: {', '.join(indicators.get('domains', [])[:10]) or '(none)'}
- IPs: {', '.join(indicators.get('ips', [])[:10]) or '(none)'}

Body (plain text excerpt):
{parsed.get('text_body', '')[:1500]}

Threat intel scores:
{scored_str}

Output ONLY the final answer directly — do not include step-by-step thinking."""


class CreateIncidentRequest(BaseModel):
    """Data to convert a phishing analysis result into an incident."""
    subject: str
    sender: str
    indicators: dict
    ai_analysis: str = ""


@router.post("/create-incident")
def create_incident_from_phishing(data: CreateIncidentRequest, db: Session = Depends(get_db)):
    """Convert a phishing analysis result into an incident."""
    year = datetime.now().year
    count = db.query(Incident).filter(Incident.number.like(f"INC-{year}-%")).count()
    seq = count + 1
    number = generate_incident_number(year, seq)
    while db.query(Incident).filter(Incident.number == number).first() is not None:
        seq += 1
        number = generate_incident_number(year, seq)

    description = f"Sender: {data.sender}\n"
    if data.ai_analysis:
        description += f"\nAI Analysis:\n{data.ai_analysis}\n"

    incident = Incident(
        number=number,
        title=f"Phishing: {data.subject}",
        description=description,
        severity="high",
        status="open",
        priority="high",
        source_type="Phishing Email",
    )
    db.add(incident)
    db.flush()

    # Add IOCs as observables
    for d in (data.indicators.get("domains") or [])[:20]:
        db.add(IncidentObservable(incident_id=incident.id, observable_type="domain", observable_value=d, observed_at=datetime.now(timezone.utc)))
    for ip in (data.indicators.get("ips") or [])[:10]:
        db.add(IncidentObservable(incident_id=incident.id, observable_type="ip", observable_value=ip, observed_at=datetime.now(timezone.utc)))
    for u in (data.indicators.get("urls") or [])[:20]:
        db.add(IncidentObservable(incident_id=incident.id, observable_type="url", observable_value=u, observed_at=datetime.now(timezone.utc)))

    db.commit()
    db.refresh(incident)
    return {"incident_id": incident.id, "incident_number": incident.number, "title": incident.title}
