"""
Database Initialization Script

Run this script to initialize the database with default data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_db, health_check
from models.models import *

def main():
    """Initialize database with default data."""
    print("=" * 60)
    print("Initializing SOAR Platform Database")
    print("=" * 60)
    
    # Initialize tables
    init_db()
    
    # Check health
    health = health_check()
    print(f"Health check: {health['status']}")
    
    print("=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    
    # Insert default admin user
    print("\nCreating default admin user...")
    admin_user = User(
        username="admin",
        email="admin@soar.local",
        is_active=True,
        is_admin=True,
    )
    
    with get_db() as db:
        db.add(admin_user)
        
        # Insert default role
        admin_role = Role(
            name="admin",
            description="Administrator role",
            permissions=["*:*"],  # All permissions
        )
        db.add(admin_role)
        admin_user.role = admin_role
        
        # Insert default user role
        user_role = Role(
            name="user",
            description="Standard analyst role",
            permissions=["incident:read", "incident:write", "integration:read"],
        )
        db.add(user_role)
        
        print("✓ Default admin user created")
    
    # Insert default integration configs (examples)
    print("\nCreating default integration configurations...")
    
    with get_db() as db:
        # VirusTotal integration
        vt_config = IntegrationConfig(
            integration_name="virustotal",
            display_name="VirusTotal",
            enabled=True,
            configuration={
                "api_url": "https://www.virustotal.com/api/v3/",
                "rate_limit": 400,
            },
        )
        db.add(vt_config)
        
        # ThreatCrowd integration
        tc_config = IntegrationConfig(
            integration_name="threatcrowd",
            display_name="ThreatCrowd",
            enabled=True,
            configuration={
                "api_url": "https://www.threatcrowd.services/api/v1/",
            },
        )
        db.add(tc_config)
        
        print("✓ VirusTotal integration configured")
        print("✓ ThreatCrowd integration configured")
    
    print("\n" + "=" * 60)
    print("Initialization complete!")
    print("=" * 60)
    print("\nDefault admin credentials:")
    print("  Username: admin")
    print("  Password: (set in database - default: admin)")
    print("\nNext steps:")
    print("  1. Change admin password")
    print("  2. Configure integration API keys")
    print("  3. Create playbooks")
    print("  4. Add automation scripts")

if __name__ == "__main__":
    main()
