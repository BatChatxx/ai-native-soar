"""
Evidence Management Router

Handles evidence upload, listing, and deletion.
Evidence can include files, observables, and attachments.
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from models.models import Evidence
from typing import List
from datetime import datetime, timezone
import uuid

router = APIRouter()


@router.get("/evidence", response_model=List[Evidence])
async def list_evidence(
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all evidence
    
    **GET** `/api/v1/evidence`
    
    Query parameters:
    - `offset`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records (default: 50)
    """
    evidence = db.query(Evidence).offset(offset).limit(limit).order_by(Evidence.uploaded_at.desc()).all()
    return evidence


@router.post("/evidence", response_model=Evidence)
async def upload_evidence(
    incident_id: int = Form(...),
    file: UploadFile = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload evidence file
    
    **POST** `/api/v1/evidence`
    
    Form data:
    - `incident_id`: Incident ID to attach evidence to
    - `file`: File to upload
    
    Supported file types:
    - PCAP files (.pcap, .npcap)
    - Archives (.zip, .tar.gz)
    - Executables (.exe, .dll, .msi)
    - Logs (.log, .txt, .json)
    - Documents (.pdf, .doc, .docx)
    - Images (.jpg, .png, .gif)
    
    Note: Large files should be uploaded to object storage,
    and only metadata stored in the database.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    if file.filename.lower().endswith(('.pcap', '.npcap')):
        pass  # PCAP files
    elif file.filename.lower().endswith(('.zip', '.tar', '.tar.gz', '.tar.bz2')):
        pass  # Archives
    elif file.filename.lower().endswith(('.exe', '.dll', '.msi', '.jar', '.bat', '.sh')):
        pass  # Executables
    elif file.filename.lower().endswith(('.log', '.txt', '.json')):
        pass  # Logs
    elif file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.xlsx')):
        pass  # Documents
    elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        pass  # Images
    elif file.filename.lower().endswith(('.yml', '.yaml', '.json')):
        pass  # Config files
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}. Supported: .pcap, .zip, .exe, .log, .txt, .pdf"
        )
    
    # Generate unique ID
    file_id = str(uuid.uuid4())[:8]
    
    # Calculate hash
    import hashlib
    content = file.file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Create evidence record
    evidence = Evidence(
        id=file_id,
        file=f"/uploads/{file.filename}",
        content=content.decode('utf-8', errors='replace'),
        hash=file_hash,
        observable_type=file.filename.split('.')[-1] if '.' in file.filename else 'file',
        content_type=file.content_type,
        filename=file.filename,
        source="upload",
        uploaded_at=datetime.now(timezone.utc),
    )
    
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    return evidence


@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """
    Get evidence by ID
    
    **GET** `/api/v1/evidence/{evidence_id}`
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return evidence


@router.delete("/evidence/{evidence_id}")
async def delete_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """
    Delete evidence
    
    **DELETE** `/api/v1/evidence/{evidence_id}`
    
    WARNING: This permanently deletes the evidence.
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    db.delete(evidence)
    db.commit()
    
    return {"message": "Evidence deleted successfully"}


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


SessionLocal = SessionLocal
