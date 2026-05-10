import asyncio
import json
from app.db.session import get_db_session
from app.db.models.post import RawPost
from sqlalchemy import select

async def get_latest_posts():
    async with get_db_session() as db:
        result = await db.execute(select(RawPost).order_by(RawPost.id.desc()).limit(4))
        posts = result.scalars().all()
        for p in posts:
            print(f"Post ID: {p.post_id}")
            print("Extracted images:", p.images)
            
            # Print parts of raw_json that contain 'images', 'attachments', 'media'
            rj = p.raw_json
            attachments = rj.get("attachments", [])
            print("Attachments:", json.dumps(attachments, indent=2, ensure_ascii=False))
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(get_latest_posts())
