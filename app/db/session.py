from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)

# ── Engine factory ────────────────────────────────────────────────────────────

def _build_engine(url: str, *, is_pool: bool = False) -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    Args:
        url: asyncpg-compatible connection string
        is_pool: If True, applies connection pool settings suitable for
                 runtime workloads. Alembic uses the direct (non-pooled)
                 engine with NullPool instead.
    """
    settings = get_settings()

    connect_args: dict = {
        # Required for Neon's TLS setup
        "ssl": "require",
    }

    if is_pool:
        return create_async_engine(
            url,
            echo=not settings.is_production,       # log SQL in dev
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            pool_pre_ping=True,                     # detect stale connections
            connect_args=connect_args,
        )
    else:
        # Synchronous-safe engine for Alembic (NullPool avoids asyncpg conflicts)
        from sqlalchemy.pool import NullPool
        return create_async_engine(
            url,
            poolclass=NullPool,
            connect_args=connect_args,
        )


# ── Singleton engine (runtime) ────────────────────────────────────────────────

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the singleton async engine (lazily initialized)."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = _build_engine(settings.database_pool_url, is_pool=True)
        log.info("database.engine_created", url_host=settings.database_pool_url.split("@")[-1])
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the singleton session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,  # safe for async — avoids lazy-load after commit
            autoflush=False,
        )
    return _session_factory


# ── Session helpers ───────────────────────────────────────────────────────────

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a session and auto-commits/rolls back.

    Usage:
        async with get_db_session() as session:
            result = await session.execute(select(RawPost))
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a DB session per request."""
    async with get_db_session() as session:
        yield session


# ── Cleanup ───────────────────────────────────────────────────────────────────

async def close_engine() -> None:
    """Dispose of the engine — call on application shutdown."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        log.info("database.engine_disposed")
        _engine = None
        _session_factory = None
