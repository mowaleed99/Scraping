import asyncio
from app.db.session import get_db_session
from app.db.models.post import ProcessedPost, RawPost
from app.scraper.dispatcher import dispatch_pending_reports
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

async def redispatch():
    async with get_db_session() as db:
        # Get the 4 most recently processed posts
        result = await db.execute(
            select(ProcessedPost)
            .options(selectinload(ProcessedPost.raw_post))
            .order_by(ProcessedPost.id.desc())
            .limit(4)
        )
        posts = result.scalars().all()
        ids = [p.id for p in posts]
        
        print(f"Re-dispatching {len(ids)} posts:")
        for p in posts:
            print(f"  - {p.id} | raw images: {p.raw_post.images}")
        
        # Reset sent_to_dotnet so dispatcher will pick them up
        await db.execute(
            update(ProcessedPost)
            .where(ProcessedPost.id.in_(ids))
            .values(sent_to_dotnet=False)
        )
        await db.commit()
        
        # Dispatch
        print("\nDispatching...")
        await dispatch_pending_reports(db, only_ids=ids)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(redispatch())
