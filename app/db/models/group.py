from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FacebookGroup(Base):
    """
    Represents a Facebook group or page that we are monitoring for
    lost & found posts.

    Priority levels:
        1 = high    → scrape every 6 h
        2 = medium  → scrape every 12 h
        3 = low     → scrape every 24 h
    """

    __tablename__ = "facebook_groups"

    # ── Primary key ─────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Facebook identity ────────────────────────────────────────────────────
    group_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True,
        comment="Native Facebook group / page ID"
    )
    group_url: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Full canonical URL of the group"
    )
    group_name: Mapped[str] = mapped_column(
        String(256), nullable=False,
        comment="Human-readable display name"
    )

    # ── Scheduling controls ──────────────────────────────────────────────────
    scrape_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true",
        comment="Toggle scraping without deleting the record"
    )
    scrape_priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2,
        comment="1=high, 2=medium, 3=low"
    )

    # ── Cursor / state tracking (Phase 1 improvement) ────────────────────────
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Wall-clock time the last scrape job started for this group"
    )
    last_post_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Timestamp of the most recent post successfully ingested. "
                "Next run fetches posts after (this - overlap_hours)."
    )
    cursor_token: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Apify/BrightData pagination token from the last run"
    )

    # ── Statistics ───────────────────────────────────────────────────────────
    post_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
        comment="Running total of posts ingested from this group"
    )

    # ── Audit ────────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=_utcnow, server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    raw_posts: Mapped[list["RawPost"]] = relationship(  # noqa: F821
        "RawPost", back_populates="group", lazy="raise"
    )
    scrape_jobs: Mapped[list["ScrapeJob"]] = relationship(  # noqa: F821
        "ScrapeJob", back_populates="group", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<FacebookGroup id={self.id} name={self.group_name!r}>"
