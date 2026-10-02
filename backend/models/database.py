"""
Database Initialization and Connection Management
"""
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

logger = logging.getLogger(__name__)

# Global engine and session factory singletons
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the global database engine."""
    global _engine
    if _engine is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://soar:soar_password@db:5432/soar",
        )
        _engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return _engine


def get_session_local():
    """Get or create the global session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def init_db(engine=None) -> None:
    """Create all database tables."""
    if engine is None:
        engine = get_engine()
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def get_db():
    """FastAPI dependency that yields a database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
