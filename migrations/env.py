"""
Alembic environment — async-compatible with Neon PostgreSQL.

Key decisions:
- Uses the direct DATABASE_URL (not pooler) to avoid NullPool conflicts
  that happen when Alembic tries to use asyncpg with connection pooling.
- Enables pgvector extension before running migrations.
- Loads all ORM models via `app.db.models` so autogenerate can diff them.
"""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Load .env so DATABASE_URL is available
load_dotenv()

# ── Alembic Config object ─────────────────────────────────────────────────────
config = context.config

# Inject DATABASE_URL from environment (keeps secrets out of alembic.ini)
database_url = os.environ["DATABASE_URL"]
# Alembic needs a synchronous-looking URL for config; asyncpg prefix is fine
# since we use async_engine_from_config below
config.set_main_option("sqlalchemy.url", database_url)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import all models so autogenerate can see them ────────────────────────────
from app.db.base import Base  # noqa: E402
import app.db.models  # noqa: E402, F401 — registers all models on Base.metadata

target_metadata = Base.metadata


# ── Offline migrations (generate SQL without a live DB connection) ─────────────
def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migrations (run against live Neon DB) ──────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Render ENUM types as their native PG ENUM (not VARCHAR)
        render_as_batch=False,
    )
    with context.begin_transaction():
        # Ensure pgvector extension exists before creating tables
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in an async context using NullPool (Alembic-safe)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": "require"},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
