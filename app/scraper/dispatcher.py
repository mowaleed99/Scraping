import structlog
import httpx
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.post import ProcessedPost, PostType
from app.scraper.dotnet_client import DotNetClient
from app.scraper.dotnet_metadata_client import DotNetMetadataClient

logger = structlog.get_logger(__name__)

async def dispatch_pending_reports(session: AsyncSession):
    """
    Fetch all processed_posts where sent_to_dotnet = false,
    send them to the .NET backend one by one, and update the flag.
    """
    logger.info("starting_dotnet_dispatch_phase")
    
    # We use selectinload to get the raw_post so we can access text and post_url
    stmt = (
        select(ProcessedPost)
        .options(selectinload(ProcessedPost.raw_post))
        .where(ProcessedPost.sent_to_dotnet == False)
    )
    result = await session.execute(stmt)
    pending_posts = result.scalars().all()
    
    if not pending_posts:
        logger.info("no_pending_posts_to_dispatch")
        return
        
    client = None
    metadata_client = None
    try:
        client = DotNetClient()
        metadata_client = DotNetMetadataClient()
    except Exception as e:
        logger.error("failed_to_initialize_dotnet_client", error=str(e))
        return

    dispatched_count = 0
    for processed in pending_posts:
        try:
            # We only want to send LOST and FOUND to .NET
            if processed.post_type in (PostType.LOST, PostType.FOUND):
                raw = processed.raw_post
                item = processed.item_type or "Item"
                location = processed.location_raw or "Unknown Location"
                contact = "None provided"
                if processed.contact_info and "extracted" in processed.contact_info:
                    contact = processed.contact_info["extracted"]
                
                title = f"[{processed.post_type.value.capitalize()}] {item} - {location}"
                desc = f"{raw.text}\n\nللتواصل: {contact}\nالمصدر: {raw.post_url}"
                
                # Ensure description meets .NET validation limits
                if len(desc) < 10:
                    desc = desc.ljust(10, ' ')
                if len(desc) > 2000:
                    desc = desc[:1997] + "..."
                
                is_person = any(w in str(item).lower() for w in ["person", "child", "boy", "girl", "man", "woman", "kid", "baby", "طفل", "بنت", "ولد", "رجل", "امراة", "شخص", "شاب", "فتاة", "عجوز"])
                type_prefix = processed.post_type.value.capitalize()
                final_type = f"{type_prefix}Person" if is_person else f"{type_prefix}Item"
                
                cat_id, subcat_id = await metadata_client.get_category_mapping(item, is_person)
                
                report_data = {
                    "Title": title,
                    "Description": desc,
                    "Type": final_type,
                    "SourceUrl": raw.post_url,
                    "CategoryId": str(cat_id),
                    "SubCategoryId": str(subcat_id),
                }
                
                # Download images
                image_files = []
                if raw.images:
                    async with httpx.AsyncClient(timeout=15.0) as img_client:
                        for idx, img_info in enumerate(raw.images):
                            img_url = img_info.get("url")
                            if img_url:
                                try:
                                    img_resp = await img_client.get(img_url)
                                    if img_resp.status_code == 200:
                                        content_type = img_resp.headers.get("content-type", "image/jpeg")
                                        ext = "jpg"
                                        if "png" in content_type: ext = "png"
                                        elif "webp" in content_type: ext = "webp"
                                        filename = f"image_{idx}.{ext}"
                                        image_files.append((filename, img_resp.content, content_type))
                                except Exception as e:
                                    logger.warning("failed_to_download_image", url=img_url, error=str(e))
                
                await client.push_report(report_data, image_files=image_files)
            
            # Mark as sent (even for irrelevant ones so we don't query them again)
            processed.sent_to_dotnet = True
            await session.commit()
            dispatched_count += 1
            
            # Polite delay to avoid hitting .NET rate limits
            await asyncio.sleep(1)
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limited — wait 5 seconds and leave for next run
                logger.warning("dotnet_rate_limited_pausing", processed_id=str(processed.id))
                await asyncio.sleep(5)
                await session.rollback()
            else:
                logger.error("dispatch_failed_for_post", error=str(e), processed_id=str(processed.id))
                await session.rollback()
            continue
        except Exception as e:
            logger.error("dispatch_failed_for_post", error=str(e), processed_id=str(processed.id))
            await session.rollback()
            continue
            
    logger.info("dotnet_dispatch_phase_completed", dispatched_count=dispatched_count)
