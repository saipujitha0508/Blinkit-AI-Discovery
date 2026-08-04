"""
Apify Play Store scraper.

Collects Google Play Store reviews using the Apify cloud scraping service.
"""

from datetime import datetime
from typing import Any, List, Optional

from loguru import logger

from scrapers.base import BaseScraper
from database.models import ReviewModel, SourceType
from config.settings import get_settings
from src.collectors.apify_play_store import collect_with_apify_play_store


class ApifyScraper(BaseScraper):
    """Scraper for Apify Play Store reviews."""

    def __init__(self):
        """Initialize Apify scraper."""
        super().__init__(SourceType.APIFY)

    def _parse_date(self, raw_date: Any) -> Optional[datetime]:
        """Parse a date string into a datetime object."""
        if not raw_date:
            return None
        try:
            return datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
        except Exception:
            return None

    def _to_float(self, raw: Any) -> Optional[float]:
        """Convert a rating value to float."""
        if raw is None:
            return None
        try:
            return float(raw)
        except Exception:
            return None

    def collect(self, use_live: bool = True, count: int = 100, **kwargs) -> List[ReviewModel]:
        """
        Collect Play Store reviews via Apify.

        Args:
            use_live: Always uses live Apify collection.
            count: Number of reviews to collect.

        Returns:
            List[ReviewModel]: Collected reviews.
        """
        logger.info(f"Collecting up to {count} reviews via Apify")

        settings = get_settings()
        try:
            raw_reviews = collect_with_apify_play_store(
                app_id="com.grofers.customerapp",
                max_reviews=count,
                token=settings.APIFY_API_TOKEN,
            )
        except Exception as e:
            logger.error(f"Error collecting Apify reviews: {e}")
            return []

        reviews = []
        for data in raw_reviews:
            try:
                review = ReviewModel(
                    id=data.get("id"),
                    source=SourceType.APIFY,
                    text=data.get("text", ""),
                    rating=self._to_float(data.get("rating")),
                    author=data.get("author"),
                    date=self._parse_date(data.get("date")),
                    url=data.get("url"),
                    language=data.get("language", "en"),
                    collected_at=datetime.utcnow(),
                )
                reviews.append(review)
            except Exception as e:
                logger.error(f"Error normalizing Apify review: {e}")

        logger.info(f"Collected {len(reviews)} Apify reviews")
        return reviews
