from __future__ import annotations

import enum
import hashlib
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.group import FacebookGroup
    from app.db.models.match import Match


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums ─────────────────────────────────────────────────────────────────────

class PostType(str, enum.Enum):
    LOST = "lost"
    FOUND = "found"
    IRRELEVANT = "irrelevant"


# ── RawPost ───────────────────────────────────────────────────────────────────

class RawPost(Base):
    """
    Raw scraped Facebook post — exactly as returned by Apify/BrightData.

    No transformation is applied here. This is the immutable source of truth
    that can be reprocessed at any time if DSPy signatures change.
    """

    __tablename__ = "raw_posts"

    # ── Primary key ─────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Facebook identity ────────────────────────────────────────────────────
    post_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True,
        comment="Native Facebook post ID — primary dedup key"
    )

    # ── Source context ───────────────────────────────────────────────────────
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("facebook_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scrape_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scrape_jobs.id", ondelete="SET NULL"),
        nullable=True,
        comment="Which job produced this post — for debugging / cost attribution"
    )

    # ── Post content ─────────────────────────────────────────────────────────
    text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Raw post body — may be Arabic, MSA, or dialect"
    )
    post_text_checksum: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="SHA-256 of cleaned text — detect if post was edited on re-scrape"
    )

    # ── Author ───────────────────────────────────────────────────────────────
    author_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    author_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True,
        comment="Facebook user ID — more stable identifier than name"
    )
    author_profile_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Post meta ────────────────────────────────────────────────────────────
    post_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Original post timestamp from Facebook"
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=_utcnow, server_default=func.now(),
        comment="When our scraper captured this post"
    )

    # ── Rich content ─────────────────────────────────────────────────────────
    images: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Array of image URLs: [{url, width, height}]"
    )
    engagement: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="{likes: int, comments: int, shares: int}"
    )
    comments_sample: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Top 3 comments — often contain contact info missed in post body"
    )

    # ── Scraper provenance ───────────────────────────────────────────────────
    scraper_version: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="Apify actor version / BrightData scraper version used"
    )
    raw_json: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="Full original scraper response — for reprocessing or debugging"
    )

    # ── Processing pipeline state ────────────────────────────────────────────
    is_processed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
        comment="False = waiting in processing queue"
    )
    processing_attempts: Mapped[int] = mapped_column(
        default=0, server_default="0",
        comment="Number of DSPy processing attempts — stops at max_retries"
    )
    processing_error: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Last error message if processing failed"
    )

    # ── Relationships ────────────────────────────────────────────────────────
    group: Mapped["FacebookGroup"] = relationship(
        "FacebookGroup", back_populates="raw_posts", lazy="raise"
    )
    processed_post: Mapped[Optional["ProcessedPost"]] = relationship(
        "ProcessedPost", back_populates="raw_post", uselist=False, lazy="raise"
    )

    # ── Indices ──────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_raw_posts_unprocessed", "is_processed", "processing_attempts",
              postgresql_where="is_processed = false"),
        Index("ix_raw_posts_posted_at", "posted_at"),
    )

    # ── Helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def compute_checksum(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return f"<RawPost id={self.id} post_id={self.post_id!r}>"


# ── ProcessedPost ─────────────────────────────────────────────────────────────

class ProcessedPost(Base):
    """
    DSPy-extracted structured data derived from a RawPost.

    Intentionally separate from RawPost so we can:
    - Reprocess without touching raw data
    - Track model version changes
    - Store embeddings for similarity search
    """

    __tablename__ = "processed_posts"

    # ── Primary key ─────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Source link ──────────────────────────────────────────────────────────
    raw_post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw_posts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # one processed record per raw post
        index=True,
    )

    # ── Classification ───────────────────────────────────────────────────────
    post_type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type_enum"), nullable=False, index=True
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="DSPy confidence score [0, 1]"
    )

    # ── Extracted entities ───────────────────────────────────────────────────
    item_type: Mapped[Optional[str]] = mapped_column(
        String(256), nullable=True,
        comment="Type of item/person — e.g. 'wallet', 'child', 'dog'"
    )
    person_name: Mapped[Optional[str]] = mapped_column(
        String(256), nullable=True,
        comment="Name of person mentioned in the post"
    )

    # Location — raw (as-extracted) + normalized (structured)
    location_raw: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Location string exactly as extracted from text"
    )
    location_normalized: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="{city, area, country, coords: {lat, lng}}"
    )

    # Contact info
    contact_info: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        comment="{phone, whatsapp, facebook_profile, other}"
    )

    # ── Embedding (pgvector) ─────────────────────────────────────────────────
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(768), nullable=True,
        comment="Gemini text-embedding-004 vector (768-dim) for similarity search"
    )

    # ── Provenance ───────────────────────────────────────────────────────────
    model_version: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True,
        comment="DSPy + Gemini model identifier used for this extraction"
    )
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=_utcnow, server_default=func.now()
    )

    # ── Relationships ────────────────────────────────────────────────────────
    raw_post: Mapped["RawPost"] = relationship(
        "RawPost", back_populates="processed_post", lazy="raise"
    )
    lost_matches: Mapped[list["Match"]] = relationship(
        "Match", foreign_keys="Match.lost_post_id",
        back_populates="lost_post", lazy="raise"
    )
    found_matches: Mapped[list["Match"]] = relationship(
        "Match", foreign_keys="Match.found_post_id",
        back_populates="found_post", lazy="raise"
    )

    # ── Indices ──────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_processed_posts_type_item",
              "post_type", "item_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ProcessedPost id={self.id} type={self.post_type} "
            f"item={self.item_type!r}>"
        )
