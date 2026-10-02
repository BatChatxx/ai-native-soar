"""
SOAR Platform - Alembic Migration Environment
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# Add parent directory to path for models import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all model bases to merge metadata
from models.users import Base as UsersBase
from models.incidents import Base as IncidentsBase
from models.evidence import Base as EvidenceBase
from models.approvals import Base as ApprovalsBase
from models.audit import Base as AuditBase
from models.integrations import Base as IntegrationsBase
from models.playbooks import Base as PlaybooksBase
from models.automation import Base as AutomationBase
from models.ai import Base as AIBase

# Collect all bases and merge
all_bases = [
    UsersBase,
    IncidentsBase,
    EvidenceBase,
    ApprovalsBase,
    AuditBase,
    IntegrationsBase,
    PlaybooksBase,
    AutomationBase,
    AIBase,
]

target_metadata = all_bases[0]

# Add other metadata
for base in all_bases[1:]:
    target_metadata.meta.tables.update(base.meta.tables)

# Alembic config
config = context.config


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
