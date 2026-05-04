import asyncio
import uuid
import sys
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db_session
from app.db.models.post import RawPost, ProcessedPost, PostType
from app.db.models.group import FacebookGroup

async def seed_data():
    print("🌱 Seeding Demo Data...")
    
    async with get_db_session() as session:
        # 1. Ensure we have a default group
        stmt = select(FacebookGroup).where(FacebookGroup.group_id == "demo-group")
        group = (await session.execute(stmt)).scalars().first()
        if not group:
            group = FacebookGroup(
                group_id="demo-group",
                group_name="Demo Lost & Found Group",
                group_url="https://facebook.com/groups/demo"
            )
            session.add(group)
            await session.commit()
            await session.refresh(group)
            
        # 2. Demo Posts
        demo_posts = [
            {
                "post_id": "demo_post_1",
                "text": "يا جماعة لقيت محفظة سودا في مدينة نصر امبارح بليل، اللي بتاعته يكلمني 01012345678",
                "type": PostType.FOUND,
                "item": "محفظة",
                "location": "مدينة نصر",
                "contact": "01012345678"
            },
            {
                "post_id": "demo_post_2",
                "text": "ابني محمد تاه مني في مول العرب امبارح لابس تيشرت احمر، ارجوكم لو حد شافه يكلمني بسرعة 01198765432",
                "type": PostType.LOST,
                "item": "طفل",
                "location": "مول العرب",
                "contact": "01198765432"
            },
            {
                "post_id": "demo_post_3",
                "text": "لقيت موبايل ايفون واقع في المعادي جنب محطة المترو، تواصل معايا لو بتاعك",
                "type": PostType.FOUND,
                "item": "موبايل",
                "location": "المعادي",
                "contact": "facebook profile"
            }
        ]
        
        inserted_count = 0
        for p in demo_posts:
            # Check if exists
            stmt = select(RawPost).where(RawPost.post_id == p["post_id"])
            existing = (await session.execute(stmt)).scalars().first()
            if existing:
                continue
                
            raw = RawPost(
                post_id=p["post_id"],
                group_id=group.id,
                text=p["text"],
                posted_at=datetime.now(timezone.utc),
                is_processed=True
            )
            session.add(raw)
            await session.flush()
            
            processed = ProcessedPost(
                raw_post_id=raw.id,
                post_type=p["type"],
                item_type=p["item"],
                location_raw=p["location"],
                contact_info={"extracted": p["contact"]}
            )
            session.add(processed)
            inserted_count += 1
            
        await session.commit()
        print(f"✅ Successfully seeded {inserted_count} new processed posts into the DB!")

if __name__ == "__main__":
    # Ensure correct asyncio loop policy for windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(seed_data())
