"""
SOAR Platform - Dashboard Schemas
"""
from typing import Optional
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_incidents: int
    open_incidents: int
    critical_incidents: int
    recent_alerts: int
    recent_activity: list
    
    class Config:
        from_attributes = True
