import asyncio
import json
from app.db.session import get_db_session
from app.db.models.post import RawPost
from sqlalchemy import select

async def inspect_raw():
    async with get_db_session() as db:
        result = await db.execute(select(RawPost).order_by(RawPost.id.desc()).limit(1))
        post = result.scalars().first()
        print(f"Post ID: {post.post_id}")
        print(f"Stored images: {post.images}")
        print("\n--- Full raw_json keys ---")
        rj = post.raw_json
        print("Top-level keys:", list(rj.keys()))
        
        # Print full raw_json (truncated)
        pretty = json.dumps(rj, indent=2, ensure_ascii=False)
        print(pretty[:5000])

asyncio.run(inspect_raw())
