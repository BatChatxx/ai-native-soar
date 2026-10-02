"""
SOAR Platform - Integration Models
Defines integration framework entities.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Table, Text as TextType
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class IntegrationCategory(str, Enum):
    """Integration categories."""
    SIEM = "siem"
    EDR = "edr"
    TICKETING = "ticketing"
    EMAIL = "email"
    IP_INTEL = "ip_intelligence"
    THREAT_INTEL = "threat_intelligence"
    ENDPOINT = "endpoint"
    NETWORK = "network"
    FILE_SHARE = "file_share"
    IDENTITY = "identity"
    CLOUD = "cloud"
    GENERIC_EDR = "generic_edr"
    GENERIC_ENDPOINT = "generic_endpoint"
    VULN = "vulnerability"
    CUSTOM = "custom"


class ActionRiskLevel(str, Enum):
    """Risk levels for integration actions."""
    READ = "READ"
    ENRICH = "ENRICH"
    MODIFY_LOW = "MODIFY_LOW"
    MODIFY = "MODIFY"
    CONTAIN = "CONTAIN"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ActionPermission(str, Enum):
    """Permission levels for actions."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class IntegrationConfig(Base):
    """Integration configuration registry (definitions only, not secrets)."""
    __tablename__ = "integration_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Integration name (e.g., "MockEDR", "GenericEndpoint")
    name = Column(String(100), unique=True, nullable=False)
    
    # Category
    category = Column(SQLEnum(IntegrationCategory), nullable=False)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Configuration schema (JSON Schema)
    config_schema = Column(TextType, nullable=True)
    
    # Input/output schemas for actions
    action_schemas = Column(TextType, nullable=True)
    
    # API endpoint (if applicable)
    base_url = Column(String(500), nullable=True)
    
    # Authentication type (e.g., "api_key", "oauth2", "bearer")
    auth_type = Column(String(50), nullable=True)
    
    # Default timeout
    default_timeout = Column(Integer, default=300)
    
    # Default retry settings
    default_retry_count = Column(Integer, default=3)
    default_retry_delay = Column(Integer, default=60)
    
    # Status
    enabled = Column(Boolean, default=True)
    version = Column(String(20), nullable=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    # Created/updated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<IntegrationConfig(name={self.name}, category={self.category.value})>"


class IntegrationInstance(Base):
    """Live integration instance with connection info."""
    __tablename__ = "integration_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to integration definition
    config_id = Column(Integer, ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    config = relationship("IntegrationConfig", foreign_keys=[config_id])
    
    # Instance name (e.g., "generic_edr-main", "sentinel-lab")
    instance_name = Column(String(100), nullable=False)
    
    # Connection status
    status = Column(String(50), nullable=False, default="connected")  # "connected", "disconnected", "error"
    last_check = Column(DateTime, nullable=True)
    
    # Configuration - never store secrets!
    # Only store configuration values, API keys go in secrets vault
    configuration = Column(TextType, nullable=True)
    
    # Health
    health_status = Column(String(50), nullable=True)  # "healthy", "degraded", "unhealthy"
    error_message = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    integrations_actions = relationship("IntegrationInstanceAction", back_populates="instance")
    
    def __repr__(self):
        return f"<IntegrationInstance(name={self.instance_name}, config={self.config.name}, status={self.status})>"


class IntegrationAction(Base):
    """Action definitions for integrations."""
    __tablename__ = "integration_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to integration config
    config_id = Column(Integer, ForeignKey("integration_configs.id", ondelete="CASCADE"), nullable=False)
    config = relationship("IntegrationConfig", foreign_keys=[config_id])
    
    # Action name (e.g., "get_host", "get_process_tree", "contain_host")
    action_name = Column(String(100), nullable=False)
    
    # Full action path (e.g., "generic_edr.get_host")
    full_path = Column(String(150), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Input schema (JSON Schema)
    input_schema = Column(TextType, nullable=True)
    
    # Output schema (JSON Schema)
    output_schema = Column(TextType, nullable=True)
    
    # Risk classification
    risk_level = Column(SQLEnum(ActionRiskLevel), nullable=False)
    
    # Required permission
    required_permission = Column(SQLEnum(ActionPermission), nullable=True)
    
    # Whether action requires approval
    requires_approval = Column(Boolean, default=False)
    
    # Whether action is AI-callable
    ai_callable = Column(Boolean, default=False)
    
    # Default timeout for action
    default_timeout = Column(Integer, default=300)
    
    # Status
    enabled = Column(Boolean, default=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    instance_actions = relationship("IntegrationInstanceAction", back_populates="action")
    
    def __repr__(self):
        return f"<IntegrationAction(name={self.action_name}, config={self.config.name}, risk={self.risk_level.value})>"


class IntegrationInstanceAction(Base):
    """Live action instance with execution metadata."""
    __tablename__ = "integration_instance_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to integration instance
    instance_id = Column(Integer, ForeignKey("integration_instances.id", ondelete="CASCADE"), nullable=False)
    instance = relationship("IntegrationInstance", back_populates="integrations_actions")
    
    # Reference to action definition
    action_id = Column(Integer, ForeignKey("integration_actions.id", ondelete="CASCADE"), nullable=False)
    action = relationship("IntegrationAction", back_populates="instance_actions")
    
    # Execution metadata
    execution_count = Column(Integer, default=0)
    last_execution = Column(DateTime, nullable=True)
    
    # Last execution result
    last_result = Column(TextType, nullable=True)
    last_error = Column(String(500), nullable=True)
    
    # Execution status
    status = Column(String(50), nullable=True)  # "idle", "running", "error"
    
    # Created at
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    executions = relationship("IntegrationExecution", back_populates="action")
    
    def __repr__(self):
        return f"<IntegrationInstanceAction(instance={self.instance.instance_name}, action={self.action.action_name})>"


class IntegrationExecution(Base):
    """Record of integration action execution."""
    __tablename__ = "integration_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to action instance
    action_instance_id = Column(Integer, ForeignKey("integration_instance_actions.id", ondelete="CASCADE"), nullable=False)
    action_instance = relationship("IntegrationInstanceAction", back_populates="executions")
    
    # Incident reference (if applicable)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    # Risk level of this execution
    risk_level = Column(SQLEnum(ActionRiskLevel), nullable=False)
    
    # Input parameters
    input_data = Column(TextType, nullable=True)
    
    # Output results
    output_data = Column(TextType, nullable=True)
    
    # Error information
    error_message = Column(String(500), nullable=True)
    
    # Execution status
    status = Column(String(50), nullable=False, default="completed")  # "running", "completed", "failed", "timeout"
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Approval info
    requires_approval = Column(Boolean, default=False)
    approval_id = Column(Integer, ForeignKey("approval_requests.id"), nullable=True)
    
    # Metadata JSON
    meta = Column(TextType, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", foreign_keys=[incident_id], backref="executions")
    approval = relationship("ApprovalRequest", foreign_keys=[approval_id])
    
    def __repr__(self):
        return f"<IntegrationExecution(id={self.id}, action={self.action_instance.action.action_name}, status={self.status})>"
