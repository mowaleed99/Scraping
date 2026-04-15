import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db
from app.db.models.match import Match
from app.db.models.post import ProcessedPost

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.get("/")
async def list_matches(
    status: str = Query(None, description="Filter by status (pending, confirmed, rejected)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Match).options(selectinload(Match.lost_post), selectinload(Match.found_post))
    if status:
        stmt = stmt.where(Match.status == status)
        
    stmt = stmt.order_by(Match.match_score.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    matches = result.scalars().all()
    
    return [
        {
            "id": str(m.id),
            "match_score": m.match_score,
            "status": m.status,
            "reasons": m.match_reasons,
            "lost_post": {
                "id": str(m.lost_post.id),
                "item": m.lost_post.item_type
            } if m.lost_post else None,
            "found_post": {
                "id": str(m.found_post.id),
                "item": m.found_post.item_type
            } if m.found_post else None,
            "created_at": m.created_at
        } for m in matches
    ]
