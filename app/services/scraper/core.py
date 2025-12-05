import logging
import json
from bs4 import BeautifulSoup
from typing import Optional
from redis.asyncio import Redis

from app.services.scraper.driver import PlaywrightDriver
from app.services.scraper.parsers.heuristics import ContentParser
from app.services.scraper.schemas import NormalizedProduct
from app.services.wardrobe import wardrobe_service, GarmentItemCreate
from app.db.session import AsyncSessionLocal
from app.core.config import settings

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.driver = PlaywrightDriver()
        self.parser = ContentParser()
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.cache_ttl = 86400 # 24 hours

    async def scrape_product(self, url: str) -> Optional[NormalizedProduct]:
        # 1. Check Cache
        cache_key = f"scraper:{url}"
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {url}")
            return NormalizedProduct(**json.loads(cached_data))

        # 2. Scrape
        html_content = await self.driver.get_page_content(url)
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Heuristic Extraction (Simplified for scaffolding)
        # 1. Title
        title_tag = soup.find("h1") or soup.find("title")
        name = title_tag.get_text(strip=True) if title_tag else "Unknown Product"
        
        # 2. Images
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and src.startswith("http") and "icon" not in src:
                images.append(src)
        
        # 3. Description / Materials
        description_text = soup.get_text()
        material = self.parser.extract_materials(description_text)
        stretchiness = self.parser.estimate_stretchiness(description_text)
        
        # 4. Sizes (Mocked selector - real world requires specific selectors per site or ML)
        # Looking for common size dropdowns or lists
        raw_sizes = [] # Implementation specific
        normalized_sizes = self.parser.normalize_sizes(raw_sizes)

        product = NormalizedProduct(
            name=name,
            url=url,
            images=images[:5], # Top 5 images
            material=material,
            stretchiness_score=stretchiness,
            normalized_sizes=normalized_sizes
        )
        
        # 3. Persist to DB (Garment Item)
        await self._persist_result(product)

        # 4. Cache Result
        await self.redis.set(cache_key, product.model_dump_json(), ex=self.cache_ttl)
        
        return product

    async def _persist_result(self, product: NormalizedProduct):
        """
        Saves the scraped result to Postgres via WardrobeService.
        """
        try:
            async with AsyncSessionLocal() as db:
                garment_in = GarmentItemCreate(
                    category="unknown", # Needs classifier
                    image_url=str(product.images[0]) if product.images else "",
                    texture_data={
                        "material": product.material, 
                        "stretchiness": product.stretchiness_score
                    },
                    is_active=True
                )
                await wardrobe_service.garments.create(db, garment_in)
                logger.info(f"Persisted product: {product.name}")
        except Exception as e:
            logger.error(f"Failed to persist product: {e}")

scraper_service = ScraperService()
