import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import get_db
from app.db.models.post import ProcessedPost, PostType

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/")
async def list_posts(
    post_type: Optional[PostType] = None,
    item_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ProcessedPost)
    if post_type:
        stmt = stmt.where(ProcessedPost.post_type == post_type)
    if item_type:
        stmt = stmt.where(ProcessedPost.item_type.ilike(f"%{item_type}%"))
        
    stmt = stmt.order_by(ProcessedPost.extracted_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    # Normally we would use a Pydantic schema here to serialize, but for brevity:
    return [
        {
            "id": str(p.id),
            "post_type": p.post_type,
            "item_type": p.item_type,
            "person_name": p.person_name,
            "location": p.location_raw,
            "confidence": p.confidence_score,
            "extracted_at": p.extracted_at
        } for p in posts
    ]

@router.get("/{post_id}")
async def get_post(post_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(ProcessedPost).where(ProcessedPost.id == post_id)
    result = await db.execute(stmt)
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    return {
        "id": str(post.id),
        "post_type": post.post_type,
        "item_type": post.item_type,
        "person_name": post.person_name,
        "location": post.location_raw,
        "contact_info": post.contact_info,
        "confidence": post.confidence_score,
        "extracted_at": post.extracted_at
    }
