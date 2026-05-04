import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import structlog

from app.db.session import get_db
from app.db.models.group import FacebookGroup
from app.scraper.apify_client import ApifyFacebookScraper
from app.scraper.dedup import ingest_raw_posts
from app.api.schemas import ScrapeResponse
from app.api.dependencies import verify_api_key

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/scrape", tags=["Scraping"])

@router.post("", response_model=ScrapeResponse)
async def trigger_scrape(
    limit: int = Query(10, ge=1, le=30, description="Max posts to scrape"),
    group_url: Optional[str] = Query(None, description="Facebook group URL"),
    db: AsyncSession = Depends(get_db),
    # Uncomment next line to require API key
    # api_key: str = Depends(verify_api_key)
):
    if limit > 30:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 30")
    print("🚀 Scraping started")
    logger.info("manual_scrape_triggered", limit=limit, group_url=group_url)

    # 1. Determine which group to scrape
    if group_url:
        # Extract ID from URL for simplicity, e.g., https://www.facebook.com/groups/123456/
        # Very simple extraction for MVP:
        parts = group_url.strip("/").split("/")
        extracted_id = parts[-1]
        
        stmt = select(FacebookGroup).where(FacebookGroup.group_url == group_url)
        result = await db.execute(stmt)
        group = result.scalars().first()
        
        if not group:
            # Create a new group on the fly
            group = FacebookGroup(
                group_id=extracted_id,
                group_url=group_url,
                group_name=f"Manual Scrape {extracted_id}"
            )
            db.add(group)
            await db.commit()
            await db.refresh(group)
    else:
        # Use first enabled group
        stmt = select(FacebookGroup).where(FacebookGroup.scrape_enabled == True)
        result = await db.execute(stmt)
        group = result.scalars().first()
        if not group:
            # Create a fallback default group if DB is completely empty
            group = FacebookGroup(
                group_id="lostandfoundegypt", # Just a placeholder fallback
                group_url="https://www.facebook.com/groups/lostandfoundegypt",
                group_name="Default Lost & Found"
            )
            db.add(group)
            await db.commit()
            await db.refresh(group)

    # 2. Trigger Scraper
    scraper = ApifyFacebookScraper()
    print(f"📡 Fetching posts from Apify for group: {group.group_id}")
    
    try:
        # We will use the custom group_url if provided, but the apify actor natively 
        # supports startUrls, so we'll just construct the generator using group.group_id
        # Wait, the scraper uses group_id to build the URL.
        # Let's temporarily override the scraper's URL building if we need to, but
        # the scraper uses: f"https://www.facebook.com/groups/{group_id}"
        # So passing our extracted group_id is correct.
        generator = scraper.scrape_group(group.group_id, limit=limit)
        
        # 3. Ingest and Process
        # dedup.py already handles inserting to raw_posts -> analyze -> processed_posts
        result_counts = await ingest_raw_posts(db, group.id, None, generator)
        
        group.last_scraped_at = datetime.now(timezone.utc)
        group.post_count += result_counts["processed"]
        await db.commit()
        
        print("✅ Scraping finished")
        
        scraped_count = result_counts["scraped"]
        if scraped_count == 0:
            return {
                "status": "success",
                "posts_scraped": 0,
                "posts_processed": 0,
                "skipped_duplicates": 0,
                "message": "No new posts found"
            }
            
        return {
            "status": "success",
            "posts_scraped": scraped_count,
            "posts_processed": result_counts["processed"],
            "skipped_duplicates": result_counts["skipped"]
        }

    except Exception as e:
        logger.error("manual_scrape_failed", error=str(e))
        print(f"❌ Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
