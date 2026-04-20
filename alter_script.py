import asyncio
from sqlalchemy import text
from app.db.session import get_engine

async def main():
    async with get_engine().begin() as conn:
        # Reset posts that exhausted retries due to the stale text-embedding-004 error.
        # Now that batch.py is fixed, these posts need to be re-queued.
        result = await conn.execute(text("""
            UPDATE raw_posts
            SET processing_attempts = 0,
                processing_error = NULL
            WHERE processing_error LIKE '%text-embedding-004%'
               OR processing_error LIKE '%models/text-embedding-004%'
               OR processing_error LIKE '%gemini-embedding-exp-03-07%'
        """))
        print(f"Reset {result.rowcount} stuck posts (embedding error) back to processing_attempts=0")

if __name__ == "__main__":
    asyncio.run(main())
