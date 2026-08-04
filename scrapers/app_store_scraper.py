"""
Apple App Store Scraper Module

Collects reviews from existing App Store raw data files for the Blinkit app.
"""

import json
import glob
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

from scrapers.base import BaseScraper
from database.models import SourceType
from config.settings import get_settings


class AppStoreScraper(BaseScraper):
    """
    Scraper for Apple App Store reviews.
    Collects reviews from existing raw data files.
    """

    def __init__(self):
        """Initialize App Store scraper."""
        super().__init__(SourceType.APP_STORE)
        self.settings = get_settings()

    def collect_from_raw_data(self, raw_data_path: str = "data/raw") -> List[Dict[str, Any]]:
        """
        Collect reviews from existing App Store raw data JSON files.

        Args:
            raw_data_path: Path to raw data directory

        Returns:
            List[Dict[str, Any]]: Raw review data from files
        """
        raw_reviews = []
        data_path = Path(raw_data_path)

        app_store_files = list(data_path.glob("app_store*.json"))
        logger.info(f"Found {len(app_store_files)} App Store data files")

        for file_path in app_store_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict) and "reviews" in data:
                    file_reviews = data["reviews"]
                elif isinstance(data, list):
                    file_reviews = data
                else:
                    logger.warning(f"Unexpected format in {file_path.name}")
                    continue

                for review in file_reviews:
                    normalized = self._normalize_raw_review(review)
                    if normalized:
                        raw_reviews.append(normalized)

                logger.info(f"Loaded {len(file_reviews)} reviews from {file_path.name}")

            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

        logger.info(f"Total raw reviews from files: {len(raw_reviews)}")
        return raw_reviews

    def collect_live(self, count: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Live App Store collection is not supported.

        Returns:
            List[Dict[str, Any]]: Empty list
        """
        logger.warning("Live App Store collection is not supported")
        return []

    def _normalize_raw_review(self, raw_review: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize App Store raw review to standard format.

        Args:
            raw_review: Raw review data from JSON file

        Returns:
            Optional[Dict[str, Any]]: Normalized review or None
        """
        try:
            metadata = raw_review.get("metadata", {})
            upvotes = 0
            try:
                upvotes = int(metadata.get("vote_count", 0) or 0)
            except (ValueError, TypeError):
                upvotes = 0

            normalized = {
                "id": raw_review.get("id"),
                "text": raw_review.get("text", ""),
                "rating": raw_review.get("rating"),
                "author": raw_review.get("author"),
                "date": raw_review.get("date"),
                "url": raw_review.get("url"),
                "language": raw_review.get("language", "en"),
                "upvotes": upvotes,
            }

            if not normalized["text"] or len(normalized["text"].strip()) < 10:
                return None

            return normalized

        except Exception as e:
            logger.error(f"Error normalizing raw review: {e}")
            return None

    def collect(self, use_live: bool = False, count: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect App Store reviews.

        Args:
            use_live: Whether to use live collection (not supported)
            count: Number of reviews to collect (ignored for file-based collection)
            **kwargs: Additional parameters

        Returns:
            List[Dict[str, Any]]: Raw review data
        """
        if use_live:
            return self.collect_live(count=count)
        else:
            return self.collect_from_raw_data(kwargs.get("raw_data_path", "data/raw"))
