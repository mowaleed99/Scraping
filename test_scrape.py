import asyncio
from app.db.session import get_db_session
from app.api.routes.scrape import trigger_scrape

async def run_test():
    async with get_db_session() as db:
        # Trigger scraping with limit 4
        result = await trigger_scrape(limit=4, group_url=None, db=db)
        print("Scrape Result:", result)

if __name__ == "__main__":
    asyncio.run(run_test())
