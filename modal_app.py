import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi",
    "uvicorn",
    "sqlalchemy[asyncio]",
    "asyncpg",
    "alembic",
    "pgvector",
    "dspy",
    "google-genai",
    "groq",
    "apify-client",
    "pydantic",
    "pydantic-settings",
    "structlog",
    "litellm",
).add_local_python_source("app")

app = modal.App("lost-found-backend", image=image)

# Secrets: Ensure we have .env configured via Modal Secrets
# e.g., modal secret create lost-found-secrets --from-dotenv

@app.function(
    schedule=modal.Cron("0 */6 * * *"),
    secrets=[modal.Secret.from_name("lost-found-secrets")],
    timeout=3600
)
async def run_scraper():
    import structlog
    from sqlalchemy import select
    from app.db.session import get_db_session
    from app.db.models.group import FacebookGroup
    from app.scraper.apify_client import ApifyFacebookScraper
    from app.scraper.dedup import ingest_raw_posts
    import uuid

    logger = structlog.get_logger(__name__)
    logger.info("cron_scraper_starting")

    async with get_db_session() as session:
        # Get enabled groups to scrape
        stmt = select(FacebookGroup).where(FacebookGroup.scrape_enabled == True)
        result = await session.execute(stmt)
        groups = result.scalars().all()
        
        scraper = ApifyFacebookScraper()
        
        for group in groups:
             job_id = uuid.uuid4()
             logger.info("scraping_group", group_id=group.group_id)
             try:
                 generator = scraper.scrape_group(group.group_id, limit=50) # Use smaller limits for frequenct runs
                 inserted = await ingest_raw_posts(session, group.id, job_id, generator)
                 logger.info("scraping_group_done", group_id=group.group_id, inserted=inserted)
                 
                 # Update last scraped
                 from datetime import datetime, timezone
                 group.last_scraped_at = datetime.now(timezone.utc)
                 group.post_count += inserted
                 await session.commit()
                 
             except Exception as e:
                 await session.rollback()
                 logger.error("scraping_group_failed", group_id=group.group_id, error=str(e))

@app.function(
    schedule=modal.Cron("*/15 * * * *"),
    secrets=[modal.Secret.from_name("lost-found-secrets")],
    timeout=1800
)
async def run_processor():
    import structlog
    from app.db.session import get_db_session
    from app.processing.batch import process_unprocessed_posts
    from app.matching.engine import generate_matches_for_post
    from app.db.models.post import ProcessedPost
    from sqlalchemy import select
    
    logger = structlog.get_logger(__name__)
    logger.info("cron_processor_starting")
    
    async with get_db_session() as session:
        # 1. Process Raw Posts
        processed = await process_unprocessed_posts(session, limit=20)
        
        # 2. Match newly processed posts
        if processed > 0:
             # Find recently processed posts that do not have matches checked.
             # Simple logic: we can just find posts that were recently processed.
             # A more robust solution uses another queue, but for now we query latest posts
             stmt = select(ProcessedPost).order_by(ProcessedPost.extracted_at.desc()).limit(processed)
             result = await session.execute(stmt)
             recent_posts = result.scalars().all()
             
             for rp in recent_posts:
                 await generate_matches_for_post(session, rp)
                 
    logger.info("cron_processor_done", processed=processed)

@app.function(secrets=[modal.Secret.from_name("lost-found-secrets")], min_containers=1)
@modal.asgi_app()
def fastapi_server():
    from app.api.main import app as fastapi_app
    return fastapi_app

