from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.group import FacebookGroup


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ScraperProvider(str, enum.Enum):
    APIFY = "apify"
    BRIGHTDATA = "brightdata"


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"   # group was disabled or rate-limited


class ScrapeJob(Base):
    """
    Audit trail for every scraping run against a Facebook group.

    Enables:
    - Cost tracking per group / provider
    - Failure analysis and retry decisions
    - Throughput metrics (posts_scraped / duration)
    - Debugging which job produced a given raw post
    """

    __tablename__ = "scrape_jobs"

    # ── Primary key ─────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Target ───────────────────────────────────────────────────────────────
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facebook_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[ScraperProvider] = mapped_column(
        Enum(ScraperProvider, name="scraper_provider_enum"),
        nullable=False,
        default=ScraperProvider.APIFY,
    )
    scraper_version: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="Apify actor version or BrightData scraper version"
    )

    # ── Status lifecycle ─────────────────────────────────────────────────────
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status_enum"),
        nullable=False,
        default=JobStatus.QUEUED,
        server_default="QUEUED",
        index=True,
    )

    # ── Timing ───────────────────────────────────────────────────────────────
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=_utcnow, server_default=func.now()
    )

    # ── Results ──────────────────────────────────────────────────────────────
    posts_scraped: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
        comment="Number of posts returned by the scraper (before dedup)"
    )
    posts_new: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
        comment="Net-new posts inserted (after dedup)"
    )

    # ── Cost tracking ────────────────────────────────────────────────────────
    cost_usd: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Reported cost in USD from provider — for budget monitoring"
    )

    # ── Failure info ─────────────────────────────────────────────────────────
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Last error message — set when status=failed"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # ── Relationships ────────────────────────────────────────────────────────
    group: Mapped["FacebookGroup"] = relationship(
        "FacebookGroup", back_populates="scrape_jobs", lazy="raise"
    )

    def __repr__(self) -> str:
        return (
            f"<ScrapeJob id={self.id} group_id={self.group_id} "
            f"status={self.status} scraped={self.posts_scraped}>"
        )
