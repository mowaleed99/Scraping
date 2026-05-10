import asyncio
from app.db.session import get_db_session
from app.scraper.apify_client import ApifyFacebookScraper
from app.scraper.dedup import ingest_raw_posts
from app.scraper.dispatcher import dispatch_pending_reports
from app.db.models.group import FacebookGroup
from sqlalchemy import select

# The group URL that had images
GROUP_URL = "https://www.facebook.com/groups/963921254435411"

async def run_test():
    async with get_db_session() as db:
        result = await db.execute(select(FacebookGroup).where(FacebookGroup.group_url == GROUP_URL))
        group = result.scalars().first()
        if not group:
            print("Group not found!")
            return

        scraper = ApifyFacebookScraper()
        print(f"Scraping group: {group.group_id}")
        generator = scraper.scrape_group(group.group_url, limit=4)
        result_counts = await ingest_raw_posts(db, group.id, None, generator)
        
        print("Result:", result_counts)
        
        new_ids = result_counts.get("new_processed_ids", [])
        print(f"Dispatching {len(new_ids)} new posts...")
        await dispatch_pending_reports(db, only_ids=new_ids)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(run_test())
