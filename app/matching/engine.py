import structlog
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.models.post import ProcessedPost, PostType
from app.db.models.match import Match, MatchStatus
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

async def find_candidates_for_post(session: AsyncSession, post: ProcessedPost, limit: int = 10) -> List[Tuple[ProcessedPost, float, dict]]:
    """
    Find matching candidates for a given post.
    If the post is LOST, searches FOUND posts.
    If the post is FOUND, searches LOST posts.
    """
    target_type = PostType.FOUND if post.post_type == PostType.LOST else PostType.LOST
    
    # Start basic query targeting opposite post type
    stmt = select(ProcessedPost).where(ProcessedPost.post_type == target_type)
    
    # Order by vector similarity if embeddings are available
    if post.embedding is not None:
        stmt = stmt.order_by(ProcessedPost.embedding.cosine_distance(post.embedding))
        
    stmt = stmt.limit(limit)
    
    result = await session.execute(stmt)
    candidates = result.scalars().all()
    
    matches_found = []
    
    for candidate in candidates:
        match_score = 0.0
        reasons = {}
        
        # 1. Item Type Match (0.40)
        if post.item_type and candidate.item_type:
            post_item = post.item_type.strip().lower()
            cand_item = candidate.item_type.strip().lower()
            if post_item in cand_item or cand_item in post_item:
                match_score += 0.40
                reasons["item_match"] = True
                
        # 2. Location Match (0.35)
        if post.location_raw and candidate.location_raw:
            post_loc = post.location_raw.strip().lower()
            cand_loc = candidate.location_raw.strip().lower()
            if post_loc in cand_loc or cand_loc in post_loc:
                match_score += 0.35
                reasons["location_match"] = True
                
        # 3. Person Name Match (0.10)
        if post.person_name and candidate.person_name:
             if post.person_name.strip().lower() == candidate.person_name.strip().lower():
                 match_score += 0.10
                 reasons["person_match"] = True
                 
        # 4. Temporal Proximity (0.15)
        diff = abs((post.extracted_at - candidate.extracted_at).total_seconds())
        if diff < 14 * 86400: # within 14 days
            # Decaying score within 14 days
            match_score += 0.15 * (1.0 - (diff / (14 * 86400))) 
            reasons["temporal_match"] = True
            
        if match_score >= 0.50: # Candidate matched threshold
             matches_found.append((candidate, match_score, reasons))
             
    # Sort by score descending
    matches_found.sort(key=lambda x: x[1], reverse=True)
    return matches_found

async def generate_matches_for_post(session: AsyncSession, post: ProcessedPost) -> int:
    """Generate and save match candidates for a newly processed post."""
    if post.post_type == PostType.IRRELEVANT:
        return 0
        
    candidates = await find_candidates_for_post(session, post)
    
    new_matches_count = 0
    for candidate, score, reasons in candidates:
        lost_post_id = post.id if post.post_type == PostType.LOST else candidate.id
        found_post_id = post.id if post.post_type == PostType.FOUND else candidate.id
        
        # Check if match already exists
        exist_stmt = select(Match).where(
            and_(
                Match.lost_post_id == lost_post_id,
                Match.found_post_id == found_post_id
            )
        )
        existing = (await session.execute(exist_stmt)).scalars().first()
        
        if not existing:
            new_match = Match(
                lost_post_id=lost_post_id,
                found_post_id=found_post_id,
                match_score=score,
                match_reasons=reasons,
                status=MatchStatus.PENDING
            )
            session.add(new_match)
            new_matches_count += 1
            
    if new_matches_count > 0:
        await session.commit()
    
    logger.info("matches_generated", post_id=str(post.id), matches=new_matches_count)
    return new_matches_count
