"""
Simple incident model tests
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, User, Incident
from models.database import init_db


@pytest.fixture
def db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create default admin user
    admin = User(
        username="admin",
        email="admin@soar.local",
        hashed_password="hashed_password",
        is_superuser=True,
        is_active=True,
    )
    session.add(admin)
    session.commit()
    
    yield session
    
    session.close()


def test_create_incident(db):
    """Test creating a new incident."""
    incident = Incident(
        number="INC-2026-000001",
        title="Test Incident",
        description="Test incident description",
        severity="high",
        status="open",
        source_type="SIEM",
    )
    
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    assert incident.id is not None
    assert incident.title == "Test Incident"
    assert incident.severity == "high"
    assert incident.status == "open"


def test_create_incident_with_owner(db):
    """Test creating incident with owner."""
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
    )
    db.add(user)
    db.commit()
    
    incident = Incident(
        number="INC-2026-000002",
        title="Test with Owner",
        severity="medium",
        status="investigating",
        owner_id=user.id,
    )
    
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    assert incident.owner_id == user.id


def test_list_incidents(db):
    """Test listing incidents."""
    incidents = [
        Incident(
            number=f"INC-2026-000{i:03d}",
            title=f"Test Incident {i}",
            severity="high",
            status="open",
        )
        for i in range(1, 6)
    ]
    
    for inc in incidents:
        db.add(inc)
    db.commit()
    
    query = db.query(Incident).order_by(Incident.id.desc()).limit(3)
    results = query.all()
    
    assert len(results) == 3
    assert results[0].number == "INC-2026-000005"


def test_delete_incident(db):
    """Test deleting an incident."""
    incident = Incident(
        number="INC-2026-000010",
        title="To be deleted",
        severity="low",
    )
    
    db.add(incident)
    db.commit()
    
    db.delete(incident)
    db.commit()
    
    result = db.query(Incident).filter(Incident.number == "INC-2026-000010").first()
    assert result is None


@pytest.mark.skip(reason="Database connection required")
def test_database_health_check(db):
    """Test database health check."""
    health = health_check()
    assert health is True
