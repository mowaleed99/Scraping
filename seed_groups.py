import asyncio
from app.db.session import get_db_session
from app.db.models.group import FacebookGroup
from sqlalchemy.future import select

async def seed():
    groups_data = [
        {"group_id": "183936132092621", "group_url": "https://www.facebook.com/groups/183936132092621", "group_name": "Testing Group 1"},
        {"group_id": "963921254435411", "group_url": "https://www.facebook.com/groups/963921254435411", "group_name": "Testing Group 2"},
        {"group_id": "418970684954035", "group_url": "https://www.facebook.com/groups/418970684954035", "group_name": "Testing Group 3"},
        {"group_id": "430157701228953", "group_url": "https://www.facebook.com/groups/430157701228953", "group_name": "Testing Group 4"},
        {"group_id": "966636430703413", "group_url": "https://www.facebook.com/groups/966636430703413", "group_name": "Testing Group 5"},
    ]

    async with get_db_session() as session:
        for data in groups_data:
            stmt = select(FacebookGroup).where(FacebookGroup.group_id == data["group_id"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                new_group = FacebookGroup(**data, scrape_enabled=True, scrape_priority=1)
                session.add(new_group)
                print(f"Added {data['group_id']}")
            else:
                existing.scrape_enabled = True
                print(f"Group {data['group_id']} already exists, enabled scraping.")
                
        # get_db_session handles the commit
        
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
