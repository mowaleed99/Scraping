"""
DB models package.

Import all models here so that:
1. Alembic's env.py can discover them via `from app.db.models import *`
2. SQLAlchemy's mapper knows all relationships at startup.
"""

from app.db.models.group import FacebookGroup
from app.db.models.job import ScrapeJob
from app.db.models.post import ProcessedPost, PostType, RawPost

__all__ = [
    "FacebookGroup",
    "ScrapeJob",
    "RawPost",
    "ProcessedPost",
    "PostType",
]
