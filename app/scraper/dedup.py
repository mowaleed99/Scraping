import uuid
from typing import AsyncGenerator
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy import type_coerce, Boolean

from app.db.models.post import RawPost

logger = structlog.get_logger(__name__)

async def ingest_raw_posts(
    session: AsyncSession, 
    group_id_uuid: uuid.UUID, 
    scrape_job_uuid: uuid.UUID, 
    posts_stream: AsyncGenerator[dict, None]
) -> int:
    """
    Ingest a stream of raw post dicts into the database,
    deduplicating based on the Facebook post ID.
    Returns the number of newly inserted/updated posts.
    """
    processed_count = 0
    
    async for raw_item in posts_stream:
        # Extract Facebook post ID (heuristics depending on the Apify actor)
        fb_post_id = raw_item.get("postId") or raw_item.get("id")
        if not fb_post_id:
            logger.warning("skipping_item_no_post_id", raw_item_keys=list(raw_item.keys()))
            continue
            
        post_url = raw_item.get("url") or f"https://www.facebook.com/{fb_post_id}"
        text_content = raw_item.get("text") or raw_item.get("message")
        
        if not text_content:
             # Skip empty posts, no useful intelligence can be extracted
             continue
             
        post_text_checksum = RawPost.compute_checksum(text_content)
        
        # User details extraction
        user_info = raw_item.get("user") or {}
        author_name = user_info.get("name") or raw_item.get("userName")
        author_id = user_info.get("id") or raw_item.get("userId")
        author_profile_url = user_info.get("url") or raw_item.get("userUrl")
        
        # Images extraction
        images = []
        if "media" in raw_item:
            for m in raw_item["media"]:
                if m.get("type") == "image":
                    images.append({"url": m.get("url")})
        elif "images" in raw_item:
            images = [{"url": img_url} for img_url in raw_item["images"]]
        
        # Engagement metrics
        engagement = {
            "likes": raw_item.get("likes", 0),
            "comments": raw_item.get("comments", 0),
            "shares": raw_item.get("shares", 0)
        }
        
        posted_at_str = raw_item.get("date") or raw_item.get("timestamp")
        posted_at = None
        if posted_at_str:
            from datetime import datetime, timezone
            for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
                try:
                    posted_at = datetime.strptime(str(posted_at_str)[:26], fmt[:len(str(posted_at_str)[:26])])
                    if posted_at.tzinfo is None:
                        posted_at = posted_at.replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
            if posted_at is None:
                # Fallback: try parsing as an integer Unix timestamp
                try:
                    posted_at = datetime.fromtimestamp(int(posted_at_str), tz=timezone.utc)
                except (ValueError, OSError):
                    pass
        
        # Prepare the UPSERT statement
        row_data = dict(
            post_id=str(fb_post_id),
            group_id=group_id_uuid,
            scrape_job_id=scrape_job_uuid,
            text=text_content,
            post_text_checksum=post_text_checksum,
            author_name=author_name,
            author_id=author_id,
            author_profile_url=author_profile_url,
            post_url=post_url,
            posted_at=posted_at,
            images=type_coerce(images, JSONB),
            engagement=engagement,
            raw_json=raw_item,
        )
        
        stmt = insert(RawPost).values(row_data).on_conflict_do_update(
            index_elements=['post_id'],
            set_=dict(
                text=text_content,
                post_text_checksum=post_text_checksum,
                engagement=engagement,
                images=type_coerce(images, JSONB),
                raw_json=raw_item,
                # Only reset is_processed if the post text changed (checksum mismatch).
                # This prevents re-queuing posts that were already processed on re-scrape.
                is_processed=(
                    RawPost.__table__.c.post_text_checksum != post_text_checksum
                ).cast(Boolean)
            )
        )
        
        await session.execute(stmt)
        processed_count += 1
        
    await session.commit()
    logger.info("ingestion_complete", processed_count=processed_count, group_id=str(group_id_uuid))
    return processed_count
