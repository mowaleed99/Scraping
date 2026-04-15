import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.api.dependencies import get_db
from app.db.models.group import FacebookGroup

router = APIRouter(prefix="/groups", tags=["Groups"])

class GroupCreate(BaseModel):
    group_id: str
    group_url: str
    group_name: str
    scrape_enabled: bool = True
    scrape_priority: int = 2

@router.get("/")
async def list_groups(db: AsyncSession = Depends(get_db)):
    stmt = select(FacebookGroup).order_by(FacebookGroup.scrape_priority.asc())
    result = await db.execute(stmt)
    groups = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "group_id": g.group_id,
            "group_name": g.group_name,
            "scrape_enabled": g.scrape_enabled,
            "post_count": g.post_count,
            "last_scraped_at": g.last_scraped_at
        } for g in groups
    ]

@router.post("/")
async def add_group(group: GroupCreate, db: AsyncSession = Depends(get_db)):
    # Check if exists
    stmt = select(FacebookGroup).where(FacebookGroup.group_id == group.group_id)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Group already exists")
        
    new_group = FacebookGroup(
        group_id=group.group_id,
        group_url=group.group_url,
        group_name=group.group_name,
        scrape_enabled=group.scrape_enabled,
        scrape_priority=group.scrape_priority
    )
    db.add(new_group)
    await db.commit()
    
    return {"id": str(new_group.id), "status": "created"}
