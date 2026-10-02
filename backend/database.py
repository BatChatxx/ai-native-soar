"""
Database Connection Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    SOAR_DB_URL: str = "postgresql://soar:soar@localhost:5432/soar"
    SOAR_DB_USER: str = "soar"
    SOAR_DB_PASSWORD: str = "soar"
    SOAR_DB_NAME: str = "soar"
    
    # Redis
    SOAR_REDIS_URL: str = "redis://localhost:6379"
    
    # Airflow
    SOAR_AIRFLOW_URL: str = "http://airflow-webserver:8080"
    
    # AI/LLM
    SOAR_AI_URL: str = "http://llm-api:11434/v1"
    
    # Security
    SOAR_API_SECRET: str = "secret-key-change-in-production"
    SOAR_SESSION_COOKIE_NAME: str = "soar_session"
    SOAR_SESSION_TIMEOUT_MINUTES: int = 30


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def get_db() -> Session:
    """Dependency to get database session."""
    engine = create_engine(
        settings.SOAR_DB_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,  # Set to True for debugging
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create declarative base
DeclarativeBase = declarative_base()


class DatabaseManager:
    """Database management utilities."""
    
    @staticmethod
    def get_engine() -> create_engine:
        """Get database engine."""
        return create_engine(
            settings.SOAR_DB_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    
    @staticmethod
    def get_session() -> Session:
        """Get database session."""
        engine = DatabaseManager.get_engine()
        session = SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
        return session()
    
    @staticmethod
    def init_db():
        """Initialize database tables."""
        engine = DatabaseManager.get_engine()
        DeclarativeBase.metadata.create_all(engine)


if __name__ == "__main__":
    # Test connection
    engine = create_engine(settings.SOAR_DB_URL)
    print(f"Database URL: {settings.SOAR_DB_URL}")
    print(f"Connection pool size: {engine.pool.size()}")
