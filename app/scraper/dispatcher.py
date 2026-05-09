import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.post import ProcessedPost, PostType
from app.scraper.dotnet_client import DotNetClient

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
    try:
        client = DotNetClient()
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
                
                title = f"[{processed.post_type.value.capitalize()}] {item} in {location}"
                desc = f"{raw.text}\n\nContact: {contact}\nSource: {raw.post_url}"
                
                report_data = {
                    "Title": title,
                    "Description": desc,
                    "Type": processed.post_type.value.capitalize(),
                    "SourceUrl": raw.post_url,
                }
                
                await client.push_report(report_data)
            
            # Mark as sent (even for irrelevant ones so we don't query them again)
            processed.sent_to_dotnet = True
            await session.commit()
            dispatched_count += 1
            
        except Exception as e:
            logger.error("dispatch_failed_for_post", error=str(e), processed_id=str(processed.id))
            # We rollback to preserve the transaction state and leave it as sent_to_dotnet=False
            await session.rollback()
            continue
            
    logger.info("dotnet_dispatch_phase_completed", dispatched_count=dispatched_count)
