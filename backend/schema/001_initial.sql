-- SOAR Platform Initial Schema
-- This file is loaded automatically when PostgreSQL container starts

-- Users and roles
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);

-- Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    incident_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source_type VARCHAR(50),
    detection_id VARCHAR(200),
    severity VARCHAR(20),
    status VARCHAR(20),
    owner_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    assigned_to VARCHAR(100),
    tags VARCHAR(500),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON incidents (incident_number);
CREATE INDEX ON incidents (status);
CREATE INDEX ON incidents (severity);

-- Incident events (timeline)
CREATE TABLE IF NOT EXISTS incident_events (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    metadata TEXT,
    risk_level VARCHAR(20),
    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    actor_type VARCHAR(50),
    approval_id INTEGER REFERENCES approval_requests(id) ON DELETE SET NULL,
    required_approval BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON incident_events (incident_id);
CREATE INDEX ON incident_events (timestamp);

-- Incident comments
CREATE TABLE IF NOT EXISTS incident_comments (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    comment_type VARCHAR(50),
    evidence_ids TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ON incident_comments (incident_id);

-- Incident-incident relationships
CREATE TABLE IF NOT EXISTS incident_relationships (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) DEFAULT 'related_to',
    direction VARCHAR(20),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON incident_relationships (incident_id);
CREATE INDEX ON incident_relationships (entity_type, entity_id);

-- Evidence
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    evidence_id VARCHAR(20) UNIQUE NOT NULL,
    content TEXT,
    content_hash VARCHAR(64),
    evidence_type VARCHAR(20),
    format VARCHAR(20) DEFAULT 'text',
    classification VARCHAR(20) DEFAULT 'untrusted',
    source VARCHAR(200),
    source_type VARCHAR(50),
    source_id VARCHAR(200),
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    ai_findings TEXT,
    metadata TEXT
);

CREATE INDEX ON evidence (evidence_id);
CREATE INDEX ON evidence (evidence_type);

-- Findings
CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    finding_id VARCHAR(20) UNIQUE NOT NULL,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    finding_type VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    confidence VARCHAR(20),
    evidence_ids TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON findings (incident_id);
CREATE INDEX ON findings (finding_id);

-- Evidence links (relationships)
CREATE TABLE IF NOT EXISTS evidence_links (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE CASCADE,
    target_evidence_id INTEGER REFERENCES evidence(id) ON DELETE CASCADE,
    link_type VARCHAR(100) NOT NULL,
    description TEXT,
    confidence INTEGER DEFAULT 100,
    metadata TEXT
);

CREATE INDEX ON evidence_links (source_evidence_id, target_evidence_id);

-- Approval requests
CREATE TABLE IF NOT EXISTS approval_requests (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    approval_id VARCHAR(20) UNIQUE NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    action_type VARCHAR(200),
    action_target VARCHAR(500),
    action_metadata TEXT,
    risk_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    requested_by VARCHAR(100),
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    rejected_by VARCHAR(100),
    rejected_at TIMESTAMPTZ,
    approver_type VARCHAR(20),
    ai_recommendation VARCHAR(20),
    ai_reasoning TEXT,
    audit_event_id INTEGER REFERENCES audit_events(id)
);

CREATE INDEX ON approval_requests (incident_id);
CREATE INDEX ON approval_requests (status);
CREATE INDEX ON approval_requests (risk_level);

-- Approval comments
CREATE TABLE IF NOT EXISTS approval_comments (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    approval_request_id INTEGER REFERENCES approval_requests(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    comment_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX ON approval_comments (approval_request_id);

-- Audit events
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    actor_type VARCHAR(50),
    action VARCHAR(200) NOT NULL,
    action_type VARCHAR(50),
    risk_level VARCHAR(20),
    category VARCHAR(20),
    details TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message VARCHAR(500),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON audit_events (created_at);
CREATE INDEX ON audit_events (actor_id);
CREATE INDEX ON audit_events (incident_id);

-- Integration configs
CREATE TABLE IF NOT EXISTS integration_configs (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(20) NOT NULL,
    description TEXT,
    config_schema TEXT,
    action_schemas TEXT,
    base_url VARCHAR(500),
    auth_type VARCHAR(50),
    default_timeout INTEGER DEFAULT 300,
    default_retry_count INTEGER DEFAULT 3,
    default_retry_delay INTEGER DEFAULT 60,
    enabled BOOLEAN DEFAULT TRUE,
    version VARCHAR(20),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_instances (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    config_id INTEGER REFERENCES integration_configs(id) ON DELETE CASCADE,
    instance_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'connected',
    last_check TIMESTAMPTZ,
    configuration TEXT,
    health_status VARCHAR(20),
    error_message VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_actions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    config_id INTEGER REFERENCES integration_configs(id) ON DELETE CASCADE,
    action_name VARCHAR(100) NOT NULL,
    full_path VARCHAR(150),
    description TEXT,
    input_schema TEXT,
    output_schema TEXT,
    risk_level VARCHAR(20) NOT NULL,
    required_permission VARCHAR(20),
    requires_approval BOOLEAN DEFAULT FALSE,
    ai_callable BOOLEAN DEFAULT FALSE,
    default_timeout INTEGER DEFAULT 300,
    enabled BOOLEAN DEFAULT TRUE,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_instance_actions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    instance_id INTEGER REFERENCES integration_instances(id) ON DELETE CASCADE,
    action_id INTEGER REFERENCES integration_actions(id) ON DELETE CASCADE,
    execution_count INTEGER DEFAULT 0,
    last_execution TIMESTAMPTZ,
    last_result TEXT,
    last_error VARCHAR(500),
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS integration_executions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    action_instance_id INTEGER REFERENCES integration_instance_actions(id) ON DELETE CASCADE,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    risk_level VARCHAR(20) NOT NULL,
    input_data TEXT,
    output_data TEXT,
    error_message VARCHAR(500),
    status VARCHAR(20) DEFAULT 'completed',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_id INTEGER REFERENCES approval_requests(id),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON integration_executions (action_instance_id);
CREATE INDEX ON integration_executions (incident_id);

-- Playbooks
CREATE TABLE IF NOT EXISTS playbooks (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    name VARCHAR(150) NOT NULL,
    version VARCHAR(20) NOT NULL,
    version_hash VARCHAR(40),
    definition TEXT,
    trigger VARCHAR(20),
    trigger_config TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    description TEXT,
    tags VARCHAR(500),
    metadata TEXT,
    author VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS playbook_versions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    playbook_id INTEGER REFERENCES playbooks(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    version_hash VARCHAR(40),
    definition TEXT,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON playbook_versions (playbook_id);

-- Playbook steps (in definition)
CREATE TABLE IF NOT EXISTS playbook_steps (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    playbook_version_id INTEGER REFERENCES playbook_versions(id) ON DELETE CASCADE,
    step_type VARCHAR(20) NOT NULL,
    name VARCHAR(150),
    description TEXT,
    definition TEXT,
    order INTEGER NOT NULL,
    dependencies TEXT,
    status VARCHAR(20),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON playbook_steps (playbook_version_id);

-- Playbook runs
CREATE TABLE IF NOT EXISTS playbook_runs (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    playbook_version_id INTEGER REFERENCES playbook_versions(id) ON DELETE CASCADE,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    trigger VARCHAR(20),
    input_data TEXT,
    status VARCHAR(20) DEFAULT 'running',
    output_data TEXT,
    error_message VARCHAR(500),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    metadata TEXT
);

CREATE INDEX ON playbook_runs (playbook_version_id);
CREATE INDEX ON playbook_runs (incident_id);

-- Playbook step runs
CREATE TABLE IF NOT EXISTS playbook_step_runs (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    playbook_run_id INTEGER REFERENCES playbook_runs(id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES playbook_steps(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending',
    output_data TEXT,
    error_message VARCHAR(500),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER,
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_id INTEGER REFERENCES approval_requests(id),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON playbook_step_runs (playbook_run_id);
CREATE INDEX ON playbook_step_runs (step_id);

-- Playbook approvals
CREATE TABLE IF NOT EXISTS playbook_approvals (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    playbook_run_id INTEGER REFERENCES playbook_runs(id) ON DELETE CASCADE,
    approval_id VARCHAR(20) UNIQUE NOT NULL,
    action_type VARCHAR(200) NOT NULL,
    action_target VARCHAR(500),
    risk_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending_approval',
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    approved_by VARCHAR(100),
    rejected_by VARCHAR(100),
    rejection_reason TEXT,
    ai_recommendation VARCHAR(20),
    ai_reasoning TEXT
);

CREATE INDEX ON playbook_approvals (playbook_run_id);

-- Automation scripts
CREATE TABLE IF NOT EXISTS automation_scripts (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    definition TEXT,
    script_type VARCHAR(20),
    trigger VARCHAR(20),
    trigger_config TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    risk_level VARCHAR(20) DEFAULT 'READ',
    requires_approval BOOLEAN DEFAULT FALSE,
    author VARCHAR(100),
    tags VARCHAR(500),
    input_schema TEXT,
    output_schema TEXT,
    timeout INTEGER DEFAULT 300,
    max_retries INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 60,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automation_versions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    script_id INTEGER REFERENCES automation_scripts(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    version_hash VARCHAR(40),
    definition TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON automation_versions (script_id);

-- Automation runs
CREATE TABLE IF NOT EXISTS automation_runs (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    version_id INTEGER REFERENCES automation_versions(id) ON DELETE CASCADE,
    script_id INTEGER REFERENCES automation_scripts(id) ON DELETE SET NULL,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE SET NULL,
    input_data TEXT,
    status VARCHAR(20) DEFAULT 'running',
    output_data TEXT,
    error_message VARCHAR(500),
    risk_level VARCHAR(20),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_id INTEGER REFERENCES approval_requests(id),
    audit_event_id INTEGER REFERENCES audit_events(id),
    metadata TEXT
);

CREATE INDEX ON automation_runs (version_id);
CREATE INDEX ON automation_runs (script_id);
CREATE INDEX ON automation_runs (incident_id);

-- LLM sessions
CREATE TABLE IF NOT EXISTS llm_sessions (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    session_id VARCHAR(40) UNIQUE NOT NULL,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    session_type VARCHAR(50),
    intent VARCHAR(20),
    system_prompt TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    model VARCHAR(100),
    model_version VARCHAR(20),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    total_tokens INTEGER,
    final_response TEXT,
    error_message VARCHAR(500),
    metadata TEXT
);

CREATE INDEX ON llm_sessions (session_id);
CREATE INDEX ON llm_sessions (incident_id);

-- LLM messages
CREATE TABLE IF NOT EXISTS llm_messages (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    session_id INTEGER REFERENCES llm_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON llm_messages (session_id);

-- LLM tool calls
CREATE TABLE IF NOT EXISTS llm_tool_calls (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    session_id INTEGER REFERENCES llm_sessions(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    tool_path VARCHAR(150),
    tool_type VARCHAR(20),
    risk_level VARCHAR(20) NOT NULL,
    arguments TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    output TEXT,
    error VARCHAR(500),
    duration_ms INTEGER,
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_id INTEGER REFERENCES approval_requests(id),
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX ON llm_tool_calls (session_id);

-- LLM findings
CREATE TABLE IF NOT EXISTS llm_findings (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    session_id INTEGER REFERENCES llm_sessions(id) ON DELETE CASCADE,
    finding_type VARCHAR(20),
    title VARCHAR(500),
    content TEXT,
    confidence INTEGER DEFAULT 100,
    evidence_ids TEXT,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON llm_findings (session_id);

-- LLM tools
CREATE TABLE IF NOT EXISTS llm_tools (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    name VARCHAR(100) UNIQUE NOT NULL,
    path VARCHAR(150),
    description TEXT,
    input_schema TEXT,
    output_schema TEXT,
    risk_level VARCHAR(20) NOT NULL,
    requires_approval BOOLEAN DEFAULT FALSE,
    ai_callable BOOLEAN DEFAULT FALSE,
    enabled BOOLEAN DEFAULT TRUE,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- LLM session-tool associations
CREATE TABLE IF NOT EXISTS llm_session_tools (
    id INTEGER PRIMARY KEY GENERATED AS IDENTITY,
    session_id INTEGER REFERENCES llm_sessions(id) ON DELETE CASCADE,
    tool_id INTEGER REFERENCES llm_tools(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX ON llm_session_tools (session_id, tool_id);
