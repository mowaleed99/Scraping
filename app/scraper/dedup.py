import uuid
from typing import AsyncGenerator
import structlog
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy import type_coerce, select
from datetime import datetime, timezone

from app.db.models.post import RawPost, ProcessedPost, PostType
from app.processing.analyzer import analyze_post

logger = structlog.get_logger(__name__)

async def ingest_raw_posts(
    session: AsyncSession, 
    group_id_uuid: uuid.UUID, 
    scrape_job_uuid: uuid.UUID | None, 
    posts_stream: AsyncGenerator[dict, None]
) -> dict:
    """
    Ingest a stream of raw post dicts into the database,
    deduplicating based on the Facebook post ID,
    and IMMEDIATELY processing them synchronously.
    Returns the number of newly inserted/updated posts.
    """
    processed_count = 0
    skipped_count = 0
    scraped_count = 0
    
    async for raw_item in posts_stream:
        scraped_count += 1
        try:
            fb_post_id = raw_item.get("postId") or raw_item.get("id")
            if not fb_post_id:
                logger.warning("skipping_item_no_post_id", raw_item_keys=list(raw_item.keys()))
                continue
                
            post_url = raw_item.get("url") or f"https://www.facebook.com/{fb_post_id}"
            
            # Check if post already exists in DB
            stmt_check = select(RawPost).where(RawPost.post_id == str(fb_post_id))
            existing = await session.execute(stmt_check)
            if existing.scalars().first():
                logger.debug("post_already_exists_skipping", post_id=str(fb_post_id))
                skipped_count += 1
                continue

            text_content = raw_item.get("text") or raw_item.get("message")
            
            if not text_content:
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
            
            posted_at_str = raw_item.get("date") or raw_item.get("timestamp")
            posted_at = None
            if posted_at_str:
                for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
                    try:
                        posted_at = datetime.strptime(str(posted_at_str)[:26], fmt[:len(str(posted_at_str)[:26])])
                        if posted_at.tzinfo is None:
                            posted_at = posted_at.replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue
                if posted_at is None:
                    try:
                        posted_at = datetime.fromtimestamp(int(posted_at_str), tz=timezone.utc)
                    except (ValueError, OSError):
                        pass
            
            # Insert or update RawPost
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
                raw_json=raw_item,
                is_processed=True
            )
            
            stmt = insert(RawPost).values(row_data).on_conflict_do_update(
                index_elements=['post_id'],
                set_=dict(
                    text=text_content,
                    post_text_checksum=post_text_checksum,
                    images=type_coerce(images, JSONB),
                    raw_json=raw_item,
                )
            ).returning(RawPost.id)
            
            result = await session.execute(stmt)
            raw_post_id = result.scalar_one()

            # Process immediately
            logger.info("analyzing_post", raw_post_id=str(raw_post_id))
            print(f"⚙️ Processing post {fb_post_id}")
            analysis_result = analyze_post(text_content)
            
            ptype_str = analysis_result.get("type", "irrelevant")
            try:
                ptype = PostType(ptype_str)
            except ValueError:
                ptype = PostType.IRRELEVANT
                
            contact_info = None
            if analysis_result.get("contact"):
                contact_info = {"extracted": analysis_result.get("contact")}

            processed = ProcessedPost(
                raw_post_id=raw_post_id,
                post_type=ptype,
                item_type=analysis_result.get("item"),
                location_raw=analysis_result.get("location"),
                contact_info=contact_info
            )
            session.add(processed)
            await session.flush()
            
            processed_count += 1
            
        except Exception as e:
            logger.error("error_processing_single_post", error=str(e), item=raw_item)
            continue
        
    await session.commit()
    logger.info("ingestion_and_processing_complete", processed_count=processed_count, skipped_count=skipped_count, group_id=str(group_id_uuid))
    return {
        "scraped": scraped_count,
        "processed": processed_count,
        "skipped": skipped_count
    }
