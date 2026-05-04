import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.db.models.post import ProcessedPost, PostType
from app.api.schemas import PostResponse
from app.api.dependencies import verify_api_key

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("", response_model=List[PostResponse])
async def list_posts(
    type: Optional[PostType] = None,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    # Uncomment next line to require API key
    # api_key: str = Depends(verify_api_key)
):
    if limit > 50:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 50")
    stmt = select(ProcessedPost)
    if type:
        stmt = stmt.where(ProcessedPost.post_type == type)
        
    stmt = stmt.order_by(ProcessedPost.extracted_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    return [
        {
            "id": str(p.id),
            "type": p.post_type.value,
            "item": p.item_type,
            "location": p.location_raw,
            "contact": p.contact_info.get("extracted") if p.contact_info else None,
            "created_at": p.extracted_at.isoformat(),
            "source": "facebook"
        } for p in posts
    ]
