"""
AI-Native SOAR Backend - FastAPI Application

Security Orchestration, Automation and Response Platform
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from models.database import init_db, get_engine
from models.models import Base, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= LLM Configuration =============

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:56987")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3.5-9b")

logger.info(f"LLM Config: URL={LLM_BASE_URL}, Model={LLM_MODEL}")


# ============= CORS Configuration =============

def get_cors_origins() -> list[str]:
    """Get CORS origins from environment"""
    origins = os.getenv("CORS_ORIGINS", "")
    if origins:
        return [origins]
    # Default origins
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


# ============= Database Initialization =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # On startup
    logger.info("Initializing database...")
    init_db(get_engine())
    logger.info("Database initialized")

    _ensure_default_llm_profile()
    
    # Check LLM connection
    if LLM_API_KEY:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{LLM_BASE_URL}/v1/models", timeout=5.0)
                logger.info(f"LLM connection check: {response.status_code}")
        except Exception as e:
            logger.warning(f"LLM connection check failed: {e}")
    
    yield
    
    # On shutdown
    logger.info("Shutting down...")


def _ensure_default_llm_profile():
    """Create a default LLM profile from env vars if none exists yet."""
    from models.database import get_session_local
    from models.models import LLMProfile

    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        existing = db.query(LLMProfile).first()
        if existing:
            return
        profile = LLMProfile(
            name="Local Qwen 3.5",
            base_url=os.getenv("LLM_BASE_URL", "http://host.docker.internal:56987"),
            model=os.getenv("LLM_MODEL", "qwen/qwen3.5-9b"),
            api_key=os.getenv("LLM_API_KEY", ""),
            context_window=int(os.getenv("LLM_CONTEXT_WINDOW", "40000")),
            is_active=True,
        )
        db.add(profile)
        db.commit()
        logger.info("Created default LLM profile from environment variables")
    finally:
        db.close()


# ============= Create FastAPI Application =============

app = FastAPI(
    title="AI-Native SOAR API",
    description="Security Orchestration, Automation and Response Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Routers =============

from routers.incidents_clean import router as incidents_clean_router
from routers.alerts_clean import router as alerts_clean_router
from routers.dashboard_clean import router as dashboard_clean_router
from routers.settings_clean import router as settings_clean_router
from routers.auth_clean import router as auth_clean_router

app.include_router(incidents_clean_router, prefix="/api/v1")
app.include_router(alerts_clean_router, prefix="/api/v1")
app.include_router(dashboard_clean_router, prefix="/api/v1")
app.include_router(settings_clean_router, prefix="/api/v1")
app.include_router(auth_clean_router, prefix="/api/v1")


# ============= Global Exception Handlers =============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "InternalServerError",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    if exc.detail == "Not authenticated":
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Not authenticated",
                "type": "Unauthorized",
            },
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "Validation Error" if exc.status_code == 422 else "HTTP Error",
        },
    )


# ============= Health Check Endpoint =============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============= Root Endpoint =============

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI-Native SOAR",
        "version": "1.0.0",
        "api_docs": "/docs",
        "health": "/health",
    }


# ============= Placeholder Endpoints =============

# These endpoints will be implemented in routers
@app.get("/api/v1/incidents", tags=["Placeholders"])
async def placeholder_list_incidents():
    """List incidents - implemented in routers/incidents_router.py"""
    return {"detail": "Implemented in routers/incidents_router.py"}


@app.post("/api/v1/incidents", tags=["Placeholders"])
async def placeholder_create_incident():
    """Create incident - implemented in routers/incidents_router.py"""
    return {"detail": "Implemented in routers/incidents_router.py"}


@app.get("/api/v1/evidence", tags=["Placeholders"])
async def placeholder_list_evidence():
    """List evidence - implemented in routers/evidence_router.py"""
    return {"detail": "Implemented in routers/evidence_router.py"}


@app.post("/api/v1/evidence", tags=["Placeholders"])
async def placeholder_upload_evidence():
    """Upload evidence - implemented in routers/evidence_router.py"""
    return {"detail": "Implemented in routers/evidence_router.py"}


@app.get("/api/v1/playbooks", tags=["Placeholders"])
async def placeholder_list_playbooks():
    """List playbooks - implemented in routers/playbooks_router.py"""
    return {"detail": "Implemented in routers/playbooks_router.py"}


@app.post("/api/v1/playbooks/{name}/run", tags=["Placeholders"])
async def placeholder_run_playbook(name: str):
    """Run playbook - implemented in routers/playbooks_router.py"""
    return {"detail": "Implemented in routers/playbooks_router.py"}


@app.get("/api/v1/approvals", tags=["Placeholders"])
async def placeholder_list_approvals():
    """List approvals - implemented in routers/approvals_router.py"""
    return {"detail": "Implemented in routers/approvals_router.py"}


@app.post("/api/v1/approvals/{id}/approve", tags=["Placeholders"])
async def placeholder_approve(id: int):
    """Approve action - implemented in routers/approvals_router.py"""
    return {"detail": "Implemented in routers/approvals_router.py"}


@app.get("/api/v1/automation", tags=["Placeholders"])
async def placeholder_list_automation():
    """List automation - implemented in routers/automation_router.py"""
    return {"detail": "Implemented in routers/automation_router.py"}


@app.post("/api/v1/automation/{slug}/run", tags=["Placeholders"])
async def placeholder_run_automation(slug: str):
    """Run automation - implemented in routers/automation_router.py"""
    return {"detail": "Implemented in routers/automation_router.py"}


@app.get("/api/v1/integrations", tags=["Placeholders"])
async def placeholder_list_integrations():
    """List integrations - implemented in routers/integrations_router.py"""
    return {"detail": "Implemented in routers/integrations_router.py"}


@app.get("/api/v1/audit", tags=["Placeholders"])
async def placeholder_audit_log():
    """Audit log - implemented in routers/audit_router.py"""
    return {"detail": "Implemented in routers/audit_router.py"}


@app.get("/api/v1/ai/tools", tags=["Placeholders"])
async def placeholder_ai_tools():
    """AI tools - implemented in routers/ai_tools_router.py"""
    return {"detail": "Implemented in routers/ai_tools_router.py"}


# ============= Run Server =============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
