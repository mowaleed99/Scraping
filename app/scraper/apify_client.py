import asyncio
from typing import AsyncGenerator
import structlog
from apify_client import ApifyClientAsync

from app.core.config import get_settings
from app.scraper.base import BaseScraper

logger = structlog.get_logger(__name__)

class ApifyFacebookScraper(BaseScraper):
    """
    Implementation of the BaseScraper using Apify's platform
    and their popular Facebook scraper actors.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = ApifyClientAsync(self.settings.apify_api_token)

    async def scrape_group(self, group_url_or_id: str, limit: int = 100) -> AsyncGenerator[dict, None]:
        """
        Scrape posts from a specific Facebook group using Apify.
        
        Args:
            group_id: Facebook Group ID (numeric or textual handle)
            limit: Maximum number of posts to fetch
            
        Yields:
            dict: Raw dictionary data from the Apify actor.
        """
        logger.info("apify_scrape_started", target=group_url_or_id, limit=limit)
        
        # Build the start URL
        if group_url_or_id.startswith("http"):
            target_url = group_url_or_id
        else:
            target_url = f"https://www.facebook.com/groups/{group_url_or_id}"
            
        # Select appropriate Apify actor based on URL type (Group vs Page)
        if "/groups/" in target_url:
            actor_id = "apify/facebook-groups-scraper"
        else:
            actor_id = "apify/facebook-posts-scraper"
        
        run_input = {
            "startUrls": [{"url": target_url}],
            "resultsLimit": limit,
        }
        
        try:
            # Run the actor and wait for it to finish
            logger.debug("apify_actor_calling", actor_id=actor_id)
            run = await asyncio.wait_for(
                self.client.actor(actor_id).call(run_input=run_input),
                timeout=300.0  # Apify actor needs up to 2-3 minutes to complete
            )
            
            logger.info("apify_actor_finished", run_id=run.get("id"), dataset_id=run.get("defaultDatasetId"))
            
            # Fetch and yield results from the default dataset
            dataset_id = run["defaultDatasetId"]
            async for item in self.client.dataset(dataset_id).iterate_items():
                # Yield raw dictionaries as they arrive
                yield item
                
        except Exception as e:
            logger.error("apify_scrape_failed", group_id=group_id, error=str(e))
            raise
