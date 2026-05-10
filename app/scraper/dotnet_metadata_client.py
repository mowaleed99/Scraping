import time
import httpx
import structlog
import asyncio
import re
from typing import Optional, Dict, Any, Tuple, List
from rapidfuzz import process, fuzz
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

    def normalize_text(self, text: str) -> str:
        """
        Normalize Arabic and English text for better matching.
        """
        if not text:
            return ""
        
        text = str(text).lower().strip()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Arabic normalization
        text = re.sub(r'[أإآ]', 'ا', text)
        text = re.sub(r'ة', 'ه', text)
        text = re.sub(r'ى', 'ي', text)
        
        # Remove common stopwords/noise
        noise_words = ["انا", "عندي", "لقيت", "ضيعت", "مين", "يا", "في", "على", "من", "عن", "لو", "حد", "مفقود", "موجود", "الرجاء", "ياجماعه", "اللى", "اللي"]
        for word in noise_words:
            # use regex boundaries for whole word match
            text = re.sub(rf'\b{word}\b', '', text)
            
        return " ".join(text.split())

    async def get_category_mapping(self, item_name: str, is_person: bool) -> Tuple[int, int]:
        """
        Maps an AI-detected item name and person flag to a specific (CategoryId, SubCategoryId)
        using a deterministic mapping engine with rapidfuzz.
        """
        subcategories = await self.fetch_subcategories()
        
        # Safe fallback: If API completely failed and we have no cache
        if not subcategories:
            logger.warning("mapping_api_failed_using_hardcoded_fallback")
            return 4, 26 # Emergency -> Important papers
            
        # 1. Person Detection Priority
        if is_person:
            logger.info("mapping_person_detected", item=item_name)
            for sub in subcategories:
                if sub["name"].lower() == "people":
                    return sub["categoryId"], sub["id"]
            return 4, 23
            
        # 2. Normalization
        norm_item = self.normalize_text(item_name)
        
        # 3. Synonym Engine
        synonyms = {
            "iphone": "mobiles", "samsung": "mobiles", "phone": "mobiles", "موبايل": "mobiles", "تليفون": "mobiles", "هاتف": "mobiles", "فون": "mobiles", "جوال": "mobiles",
            "macbook": "laptops", "لاب": "laptops", "لابتوب": "laptops",
            "ipad": "tablets", "تابلت": "tablets", "ايباد": "tablets",
            "airpods": "ear buds & headphones", "headphone": "ear buds & headphones", "سماعه": "ear buds & headphones", "ايربودز": "ear buds & headphones",
            "cash": "money", "فلوس": "money", "مبلغ": "money", "نقود": "money",
            "visa": "debit/credit cards", "mastercard": "debit/credit cards", "credit card": "debit/credit cards", "فيزا": "debit/credit cards", "كارت": "debit/credit cards",
            "id card": "national id card", "بطاقه": "national id card", "رقم قومي": "national id card",
            "محفظه": "wallet", "بوك": "wallet",
            "كلب": "dogs", "قطة": "cats", "قطه": "cats",
            "مفتاح": "keys", "مفاتيح": "keys",
            "شنطه": "backpacks", "حقيبه": "handbags",
            "سياره": "cars", "عربيه": "cars",
            "موتوسيكل": "motorcycles", "موتسكل": "motorcycles", "دبابه": "motorcycles",
            "جواز سفر": "identity documents", "passport": "identity documents", "باسبور": "identity documents",
            "ورق": "important papers", "اوراق": "important papers", "مستندات": "important papers",
            "رخصه": "driving license"
        }
        
        target_subcat_name = None
        
        for key, target in synonyms.items():
            if key in norm_item:
                target_subcat_name = target
                logger.info("mapping_synonym_match", item=item_name, norm=norm_item, synonym=key, mapped_to=target)
                break
                
        # 4. Fuzzy Matching
        subcat_names = [sub["name"] for sub in subcategories]
        
        if target_subcat_name:
            # We found a synonym, match the target against actual subcategory names
            match = process.extractOne(target_subcat_name, subcat_names, scorer=fuzz.ratio)
        else:
            # Try to fuzzy match the normalized item directly against subcategory names
            match = process.extractOne(norm_item, subcat_names, scorer=fuzz.partial_ratio)
            
        best_match_name = None
        score = 0
        
        if match:
            best_match_name, score, _ = match
            
        # 5. Confidence & Safe Fallbacks
        confidence_threshold = 70
        
        if score >= confidence_threshold:
            logger.info("mapping_fuzzy_success", item=item_name, norm=norm_item, match=best_match_name, score=score)
            for sub in subcategories:
                if sub["name"] == best_match_name:
                    return sub["categoryId"], sub["id"]
        else:
            logger.warning("mapping_fuzzy_weak", item=item_name, norm=norm_item, best_match=best_match_name, score=score)
            
            # Safe Fallback to "Important papers" or "Identity Documents"
            for sub in subcategories:
                if sub["name"].lower() in ["important papers", "identity documents"]:
                    return sub["categoryId"], sub["id"]
            
            # Ultimate fallback to whatever is first, ideally something harmless
            first = subcategories[0]
            return first["categoryId"], first["id"]
