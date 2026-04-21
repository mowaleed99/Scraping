import asyncio
import structlog
import dspy
import google.genai as genai

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.post import RawPost, ProcessedPost, PostType
from app.processing.pipeline import LostFoundPipeline
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

async def process_unprocessed_posts(session: AsyncSession, limit: int = 20) -> int:
    """
    Fetch unprocessed posts from DB, run DSPy pipeline, 
    generate embeddings, and save to ProcessedPosts.
    """
    settings = get_settings()

    # Query for unprocessed posts
    stmt = (
        select(RawPost)
        .where(RawPost.is_processed == False)
        .where(RawPost.processing_attempts < settings.max_retries)
        .limit(limit)
    )
    result = await session.execute(stmt)
    posts_to_process = result.scalars().all()
    
    if not posts_to_process:
        return 0
        
    # Configure DSPy with Groq via LiteLLM-style model string
    lm = dspy.LM(model=f"groq/{settings.llm_model}", api_key=settings.groq_api_key)
    dspy.configure(lm=lm)
    
    # Configure Google GenAI client for embeddings
    genai_client = genai.Client(api_key=settings.gemini_api_key)

    pipeline = LostFoundPipeline()
    processed_count = 0

    for i, post in enumerate(posts_to_process):
        try:
            # 1. Run DSPy inference (wrapped in thread to avoid blocking the async event loop)
            result_dict = await asyncio.to_thread(pipeline.forward, post.text)
            
            # 2. Get embeddings if not irrelevant
            # NOTE: using text-embedding-004, truncating to 768 dims to match DB vector column
            EMBED_MODEL = "text-embedding-004"
            embedding = None
            if result_dict["post_type"] != "irrelevant":
                embed_res = genai_client.models.embed_content(
                    model=EMBED_MODEL,
                    contents=post.text,
                    config=genai.types.EmbedContentConfig(output_dimensionality=768)
                )
                embedding = embed_res.embeddings[0].values[:768] # Slice just in case API ignores config
            
            # 3. Create ProcessedPost
            processed_post = ProcessedPost(
                raw_post_id=post.id,
                post_type=PostType(result_dict["post_type"]),
                confidence_score=result_dict["confidence"],
                item_type=result_dict["item_type"],
                person_name=result_dict["person_name"],
                location_raw=result_dict["location"],
                contact_info={"raw": result_dict["contact_info"]} if result_dict["contact_info"] else None,
                embedding=embedding,
                model_version=settings.llm_model,
            )
            
            session.add(processed_post)
            
            # Mark raw post as processed
            post.is_processed = True
            
            processed_count += 1
            
            # Commit each post individually to save partial progress
            await session.commit()
            
            # Rate-limit guard: ~1800 tokens/post, Groq free tier = 6000 TPM
            # Wait 2s between posts to stay well within limits
            if i < len(posts_to_process) - 1:
                await asyncio.sleep(2)
            
        except Exception as e:
            logger.error("processing_failed", post_id=str(post.id), error=str(e))
            post.processing_attempts += 1
            post.processing_error = str(e)
            await session.commit()
            # Back off on rate limit errors
            if "rate_limit" in str(e).lower() or "ratelimit" in str(e).lower():
                logger.warning("rate_limit_hit_backing_off", sleep_seconds=15)
                await asyncio.sleep(15)
            
    logger.info("batch_processing_complete", count=len(posts_to_process), successful=processed_count)
    return processed_count
