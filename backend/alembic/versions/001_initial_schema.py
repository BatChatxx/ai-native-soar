"""initial_schema

Revision id: 001_initial
Create: 2026-01-01

Create all initial tables for SOAR platform.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all SOAR platform tables."""
    # Users and roles
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=False)

    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=False)

    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_permissions_name', 'permissions', ['name'], unique=False)

    op.create_table('role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id')
    )
    op.create_index('ix_role_permissions_id', 'role_permissions', ['id'], unique=False)

    # Incidents
    op.create_table('incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_number', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('detection_id', sa.String(length=200), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('assigned_to', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_incidents_incident_number', 'incidents', ['incident_number'], unique=True)
    op.create_index('ix_incidents_status', 'incidents', ['status'], unique=False)
    op.create_index('ix_incidents_severity', 'incidents', ['severity'], unique=False)

    # Incident events
    op.create_table('incident_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_type', sa.String(length=50), nullable=True),
        sa.Column('approval_id', sa.Integer(), nullable=True),
        sa.Column('required_approval', sa.Boolean(), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_incident_events_incident_id', 'incident_events', ['incident_id'], unique=False)
    op.create_index('ix_incident_events_timestamp', 'incident_events', ['timestamp'], unique=False)

    # Incident comments
    op.create_table('incident_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('comment_type', sa.String(length=50), nullable=True),
        sa.Column('evidence_ids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_incident_comments_incident_id', 'incident_comments', ['incident_id'], unique=False)

    # Incident relationships
    op.create_table('incident_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('direction', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_incident_relationships_incident_id', 'incident_relationships', ['incident_id'], unique=False)
    op.create_index('ix_incident_relationships_entity', 'incident_relationships', ['entity_type', 'entity_id'], unique=False)

    # Evidence
    op.create_table('evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('evidence_type', sa.String(length=20), nullable=True),
        sa.Column('format', sa.String(length=20), nullable=True),
        sa.Column('classification', sa.String(length=20), nullable=True),
        sa.Column('source', sa.String(length=200), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('source_id', sa.String(length=200), nullable=True),
        sa.Column('extracted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('ai_findings', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evidence_evidence_id', 'evidence', ['evidence_id'], unique=True)
    op.create_index('ix_evidence_evidence_type', 'evidence', ['evidence_type'], unique=False)

    # Findings
    op.create_table('findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.String(length=20), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('finding_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('confidence', sa.String(length=20), nullable=True),
        sa.Column('evidence_ids', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_findings_incident_id', 'findings', ['incident_id'], unique=False)
    op.create_index('ix_findings_finding_id', 'findings', ['finding_id'], unique=True)

    # Evidence links
    op.create_table('evidence_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_evidence_id', sa.Integer(), nullable=False),
        sa.Column('target_evidence_id', sa.Integer(), nullable=False),
        sa.Column('link_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_evidence_links_source', 'evidence_links', ['source_evidence_id', 'target_evidence_id'], unique=False)

    # Approval requests
    op.create_table('approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('approval_id', sa.String(length=20), nullable=False),
        sa.Column('request_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=200), nullable=True),
        sa.Column('action_target', sa.String(length=500), nullable=True),
        sa.Column('action_metadata', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('requested_by', sa.String(length=100), nullable=True),
        sa.Column('requested_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('rejected_by', sa.String(length=100), nullable=True),
        sa.Column('rejected_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('approver_type', sa.String(length=20), nullable=True),
        sa.Column('ai_recommendation', sa.String(length=20), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.Column('audit_event_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['audit_event_id'], ['audit_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_approval_requests_incident_id', 'approval_requests', ['incident_id'], unique=False)
    op.create_index('ix_approval_requests_status', 'approval_requests', ['status'], unique=False)
    op.create_index('ix_approval_requests_risk_level', 'approval_requests', ['risk_level'], unique=False)

    # Approval comments
    op.create_table('approval_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('approval_request_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('comment_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['approval_request_id'], ['approval_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_approval_comments_approval_request_id', 'approval_comments', ['approval_request_id'], unique=False)

    # Audit events
    op.create_table('audit_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_type', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=200), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=20), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_events_created_at', 'audit_events', ['created_at'], unique=False)
    op.create_index('ix_audit_events_actor_id', 'audit_events', ['actor_id'], unique=False)
    op.create_index('ix_audit_events_incident_id', 'audit_events', ['incident_id'], unique=False)

    # Integration configs
    op.create_table('integration_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config_schema', sa.Text(), nullable=True),
        sa.Column('action_schemas', sa.Text(), nullable=True),
        sa.Column('base_url', sa.String(length=500), nullable=True),
        sa.Column('auth_type', sa.String(length=50), nullable=True),
        sa.Column('default_timeout', sa.Integer(), nullable=True),
        sa.Column('default_retry_count', sa.Integer(), nullable=True),
        sa.Column('default_retry_delay', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_integration_configs_name', 'integration_configs', ['name'], unique=False)

    # Integration instances
    op.create_table('integration_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('instance_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('last_check', sa.TIMESTAMP(), nullable=True),
        sa.Column('configuration', sa.Text(), nullable=True),
        sa.Column('health_status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['integration_configs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_integration_instances_config_id', 'integration_instances', ['config_id'], unique=False)

    # Integration actions
    op.create_table('integration_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('action_name', sa.String(length=100), nullable=False),
        sa.Column('full_path', sa.String(length=150), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('input_schema', sa.Text(), nullable=True),
        sa.Column('output_schema', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('required_permission', sa.String(length=20), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('ai_callable', sa.Boolean(), nullable=True),
        sa.Column('default_timeout', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['integration_configs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_integration_actions_config_id', 'integration_actions', ['config_id'], unique=False)

    # Integration instance actions
    op.create_table('integration_instance_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instance_id', sa.Integer(), nullable=False),
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('execution_count', sa.Integer(), nullable=True),
        sa.Column('last_execution', sa.TIMESTAMP(), nullable=True),
        sa.Column('last_result', sa.Text(), nullable=True),
        sa.Column('last_error', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['action_id'], ['integration_actions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['instance_id'], ['integration_instances.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_integration_instance_actions_id', 'integration_instance_actions', ['id'], unique=False)

    # Integration executions
    op.create_table('integration_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action_instance_id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('input_data', sa.Text(), nullable=True),
        sa.Column('output_data', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approval_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['action_instance_id'], ['integration_instance_actions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_integration_executions_action_instance_id', 'integration_executions', ['action_instance_id'], unique=False)
    op.create_index('ix_integration_executions_incident_id', 'integration_executions', ['incident_id'], unique=False)

    # Playbooks
    op.create_table('playbooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('version_hash', sa.String(length=40), nullable=True),
        sa.Column('definition', sa.Text(), nullable=True),
        sa.Column('trigger', sa.String(length=20), nullable=True),
        sa.Column('trigger_config', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_playbooks_name', 'playbooks', ['name'], unique=False)
    op.create_index('ix_playbooks_version', 'playbooks', ['version'], unique=False)

    # Playbook versions
    op.create_table('playbook_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playbook_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('version_hash', sa.String(length=40), nullable=True),
        sa.Column('definition', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['playbook_id'], ['playbooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_playbook_versions_playbook_id', 'playbook_versions', ['playbook_id'], unique=False)

    # Playbook steps
    op.create_table('playbook_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playbook_version_id', sa.Integer(), nullable=False),
        sa.Column('step_type', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('definition', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('dependencies', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['playbook_version_id'], ['playbook_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_playbook_steps_playbook_version_id', 'playbook_steps', ['playbook_version_id'], unique=False)

    # Playbook runs
    op.create_table('playbook_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playbook_version_id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('trigger', sa.String(length=100), nullable=True),
        sa.Column('input_data', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('output_data', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['playbook_version_id'], ['playbook_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_playbook_runs_playbook_version_id', 'playbook_runs', ['playbook_version_id'], unique=False)
    op.create_index('ix_playbook_runs_incident_id', 'playbook_runs', ['incident_id'], unique=False)

    # Playbook step runs
    op.create_table('playbook_step_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playbook_run_id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('output_data', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approval_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['playbook_run_id'], ['playbook_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['step_id'], ['playbook_steps.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_playbook_step_runs_playbook_run_id', 'playbook_step_runs', ['playbook_run_id'], unique=False)
    op.create_index('ix_playbook_step_runs_step_id', 'playbook_step_runs', ['step_id'], unique=False)

    # Playbook approvals
    op.create_table('playbook_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playbook_run_id', sa.Integer(), nullable=False),
        sa.Column('approval_id', sa.String(length=20), nullable=False),
        sa.Column('action_type', sa.String(length=200), nullable=False),
        sa.Column('action_target', sa.String(length=500), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('requested_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('rejected_by', sa.String(length=100), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('ai_recommendation', sa.String(length=20), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['playbook_run_id'], ['playbook_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_playbook_approvals_playbook_run_id', 'playbook_approvals', ['playbook_run_id'], unique=False)

    # Automation scripts
    op.create_table('automation_scripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('definition', sa.Text(), nullable=True),
        sa.Column('script_type', sa.String(length=20), nullable=True),
        sa.Column('trigger', sa.String(length=20), nullable=True),
        sa.Column('trigger_config', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('input_schema', sa.Text(), nullable=True),
        sa.Column('output_schema', sa.Text(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('retry_delay', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_automation_scripts_name', 'automation_scripts', ['name'], unique=False)

    # Automation versions
    op.create_table('automation_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('version_hash', sa.String(length=40), nullable=True),
        sa.Column('definition', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['script_id'], ['automation_scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_automation_versions_script_id', 'automation_versions', ['script_id'], unique=False)

    # Automation runs
    op.create_table('automation_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=True),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('input_data', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('output_data', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approval_id', sa.Integer(), nullable=True),
        sa.Column('audit_event_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['audit_event_id'], ['audit_events.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['script_id'], ['automation_scripts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['version_id'], ['automation_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_automation_runs_version_id', 'automation_runs', ['version_id'], unique=False)
    op.create_index('ix_automation_runs_script_id', 'automation_runs', ['script_id'], unique=False)
    op.create_index('ix_automation_runs_incident_id', 'automation_runs', ['incident_id'], unique=False)

    # LLM sessions
    op.create_table('llm_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=40), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('session_type', sa.String(length=50), nullable=True),
        sa.Column('intent', sa.String(length=20), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('model_version', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('final_response', sa.Text(), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_llm_sessions_session_id', 'llm_sessions', ['session_id'], unique=True)
    op.create_index('ix_llm_sessions_incident_id', 'llm_sessions', ['incident_id'], unique=False)

    # LLM messages
    op.create_table('llm_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['llm_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_llm_messages_session_id', 'llm_messages', ['session_id'], unique=False)

    # LLM tool calls
    op.create_table('llm_tool_calls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('tool_name', sa.String(length=100), nullable=False),
        sa.Column('tool_path', sa.String(length=150), nullable=True),
        sa.Column('tool_type', sa.String(length=20), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('arguments', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('output', sa.Text(), nullable=True),
        sa.Column('error', sa.String(length=500), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approval_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['approval_id'], ['approval_requests.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['session_id'], ['llm_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_llm_tool_calls_session_id', 'llm_tool_calls', ['session_id'], unique=False)

    # LLM findings
    op.create_table('llm_findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('finding_type', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('evidence_ids', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['llm_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_llm_findings_session_id', 'llm_findings', ['session_id'], unique=False)

    # LLM tools
    op.create_table('llm_tools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('path', sa.String(length=150), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('input_schema', sa.Text(), nullable=True),
        sa.Column('output_schema', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('requires_approval', sa.Boolean(), nullable=False),
        sa.Column('ai_callable', sa.Boolean(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_llm_tools_name', 'llm_tools', ['name'], unique=False)

    # LLM session-tool associations
    op.create_table('llm_session_tools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('tool_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['llm_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tool_id'], ['llm_tools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_llm_session_tools_session_id', 'llm_session_tools', ['session_id', 'tool_id'], unique=True)


def downgrade() -> None:
    """Drop all SOAR platform tables."""
    op.drop_table('llm_session_tools')
    op.drop_table('llm_tools')
    op.drop_table('llm_findings')
    op.drop_table('llm_tool_calls')
    op.drop_table('llm_messages')
    op.drop_table('llm_sessions')
    op.drop_table('automation_runs')
    op.drop_table('automation_versions')
    op.drop_table('automation_scripts')
    op.drop_table('playbook_approvals')
    op.drop_table('playbook_step_runs')
    op.drop_table('playbook_runs')
    op.drop_table('playbook_steps')
    op.drop_table('playbook_versions')
    op.drop_table('playbooks')
    op.drop_table('integration_executions')
    op.drop_table('integration_instance_actions')
    op.drop_table('integration_actions')
    op.drop_table('integration_instances')
    op.drop_table('integration_configs')
    op.drop_table('audit_events')
    op.drop_table('approval_comments')
    op.drop_table('approval_requests')
    op.drop_table('evidence_links')
    op.drop_table('findings')
    op.drop_table('evidence')
    op.drop_table('incident_relationships')
    op.drop_table('incident_comments')
    op.drop_table('incident_events')
    op.drop_table('incidents')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
