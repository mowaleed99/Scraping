from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import MetaData

# Naming convention for Alembic auto-generated constraints
# This ensures deterministic constraint names across migrations
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy ORM models.

    All models that inherit from this class are automatically
    registered and visible to Alembic for migration generation.
    """
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
