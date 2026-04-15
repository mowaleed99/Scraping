from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseScraper(ABC):
    """Abstract base class for all Facebook group scrapers."""

    @abstractmethod
    async def scrape_group(self, group_id: str, limit: int = 100) -> AsyncGenerator[dict, None]:
        """
        Scrape posts from a Facebook group.
        
        Args:
            group_id: The ID or URL handle of the Facebook group.
            limit: Maximum number of posts to scrape.

        Yields:
            dict: Raw post dictionary as returned by the scraping provider.
        """
        pass
