import time
import httpx
import structlog
import asyncio
from typing import Optional, Dict, Any, Tuple, List
from app.scraper.dotnet_client import DotNetClient

logger = structlog.get_logger(__name__)

class DotNetMetadataClient:
    _instance = None
    _cache: List[Dict[str, Any]] = []
    _last_fetched: float = 0
    _ttl: int = 3600  # 1 hour

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DotNetMetadataClient, cls).__new__(cls)
        return cls._instance

    async def fetch_subcategories(self) -> List[Dict[str, Any]]:
        """Fetch categories and subcategories from the .NET API with a 1-hour cache TTL."""
        now = time.time()
        if self._cache and (now - self._last_fetched) < self._ttl:
            return self._cache

        logger.info("fetching_categories_from_dotnet")
        dotnet_client = DotNetClient()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                await dotnet_client._authenticate(client)
                url = f"{dotnet_client.base_url}/api/SubCategories"
                headers = {"Authorization": f"Bearer {dotnet_client.token}"}
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                if data.get("success") and "data" in data:
                    self._cache = data["data"]
                    self._last_fetched = now
                    logger.info("categories_fetched_successfully", count=len(self._cache))
                    return self._cache
                else:
                    logger.error("dotnet_category_format_unexpected", payload=data)
                    return self._cache
                    
            except Exception as e:
                logger.error("failed_to_fetch_dotnet_categories", error=str(e))
                return self._cache

    async def get_category_mapping(self, item_name: str, is_person: bool) -> Tuple[int, int]:
        """
        Maps an AI-detected item name and person flag to a specific (CategoryId, SubCategoryId).
        Returns safe fallbacks if no precise match is found.
        """
        subcategories = await self.fetch_subcategories()
        
        # Safe fallback: If API completely failed and we have no cache
        if not subcategories:
            return 4, 26 # Emergency -> Important papers
            
        # 1. Immediate override for persons
        if is_person:
            for sub in subcategories:
                if sub["name"].lower() == "people":
                    return sub["categoryId"], sub["id"]
            return 4, 23 # Fallback hardcoded if we somehow missed it but have data
            
        # 2. Heuristic string matching for common items
        item_lower = str(item_name).lower()
        
        # Translation/Synonym dictionary to map raw text to .NET SubCategory Names
        custom_mappings = {
            "iphone": "mobiles",
            "samsung": "mobiles",
            "phone": "mobiles",
            "macbook": "laptops",
            "ipad": "tablets",
            "airpods": "ear buds & headphones",
            "headphone": "ear buds & headphones",
            "cash": "money",
            "visa": "debit/credit cards",
            "mastercard": "debit/credit cards",
            "credit card": "debit/credit cards",
            "id card": "national id card",
            "بطاقة": "national id card",
            "رقم قومي": "national id card",
            "محفظة": "wallet",
            "موبايل": "mobiles",
            "هاتف": "mobiles",
            "تليفون": "mobiles",
            "كلب": "dogs",
            "قطة": "cats",
            "مفتاح": "keys",
            "شنطة": "backpacks",
            "حقيبة": "handbags",
            "سيارة": "cars",
            "عربية": "cars",
            "موتوسيكل": "motorcycles",
            "جواز سفر": "identity documents",
            "passport": "identity documents",
            "فلوس": "money",
        }
        
        # Check custom synonyms first
        for key, target_subcat in custom_mappings.items():
            if key in item_lower:
                for sub in subcategories:
                    if sub["name"].lower() == target_subcat:
                        return sub["categoryId"], sub["id"]
                        
        # 3. Direct substring matching (e.g., if item is "Wallet black" -> matches "Wallet")
        for sub in subcategories:
            sub_name_lower = sub["name"].lower()
            if sub_name_lower in item_lower or item_lower in sub_name_lower:
                return sub["categoryId"], sub["id"]
                
        # 4. Final Fallback: use "Valuable items" as generic catch-all
        for sub in subcategories:
            if sub["name"].lower() == "valuable items":
                return sub["categoryId"], sub["id"]

        # Ultimate fallback: return the first available subcategory
        first = subcategories[0]
        return first["categoryId"], first["id"]
