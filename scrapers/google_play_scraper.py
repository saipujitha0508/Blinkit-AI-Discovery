"""
Google Play Store Scraper Module

Collects customer reviews from Google Play Store for the Blinkit app
using google-play-scraper library and existing raw data files.
"""

import json
import glob
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from google_play_scraper import Sort, reviews

from scrapers.base import BaseScraper
from database.models import SourceType
from config.settings import get_settings
from config.constants import BLINKIT_PACKAGE_ID


class GooglePlayScraper(BaseScraper):
    """
    Scraper for Google Play Store reviews.
    Collects reviews from both existing raw data files and live API.
    """
    
    def __init__(self):
        """Initialize Google Play Store scraper."""
        super().__init__(SourceType.GOOGLE_PLAY)
        self.package_id = BLINKIT_PACKAGE_ID
        self.settings = get_settings()
    
    def collect_from_raw_data(self, raw_data_path: str = "data/raw") -> List[Dict[str, Any]]:
        """
        Collect reviews from existing raw data JSON files.
        
        Args:
            raw_data_path: Path to raw data directory
            
        Returns:
            List[Dict[str, Any]]: Raw review data from files
        """
        raw_reviews = []
        data_path = Path(raw_data_path)
        
        # Find all Google Play JSON files
        google_play_files = list(data_path.glob("google_play*.json"))
        
        logger.info(f"Found {len(google_play_files)} Google Play data files")
        
        for file_path in google_play_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract reviews from different file formats
                if isinstance(data, dict) and "reviews" in data:
                    file_reviews = data["reviews"]
                elif isinstance(data, list):
                    file_reviews = data
                else:
                    logger.warning(f"Unexpected format in {file_path.name}")
                    continue
                
                # Normalize review format
                for review in file_reviews:
                    normalized = self._normalize_raw_review(review)
                    if normalized:
                        raw_reviews.append(normalized)
                
                logger.info(f"Loaded {len(file_reviews)} reviews from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        logger.info(f"Total raw reviews from files: {len(raw_reviews)}")
        return raw_reviews
    
    def collect_live(self, count: int = 100, sort: str = "newest") -> List[Dict[str, Any]]:
        """
        Collect live reviews from Google Play Store API with pagination.

        Args:
            count: Number of reviews to collect
            sort: Sort order (newest, rating_high, rating_low)

        Returns:
            List[Dict[str, Any]]: Raw review data from API
        """
        sort_mapping = {
            "newest": Sort.NEWEST,
            "most_relevant": Sort.MOST_RELEVANT,
            "relevance": Sort.MOST_RELEVANT,
            "rating": Sort.RATING,
            "rating_high": Sort.RATING,
            "rating_low": Sort.RATING,
        }
        sort_order = sort_mapping.get(sort, Sort.NEWEST)

        logger.info(f"Collecting {count} live reviews from Google Play Store")

        collected: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()
        token = None

        while len(collected) < count:
            batch_size = min(100, count - len(collected))
            try:
                result, token = reviews(
                    self.package_id,
                    lang="en",
                    country="in",
                    count=batch_size,
                    sort=sort_order,
                    filter_score_with=None,
                    continuation_token=token,
                )
            except Exception as e:
                logger.error(f"Error in live Google Play page: {e}")
                break

            if not result:
                break

            for review in result:
                review_id = str(review.get("reviewId", ""))
                text = str(review.get("content", "")).strip()
                if not review_id or not text:
                    continue
                if review_id in seen_ids:
                    continue
                seen_ids.add(review_id)

                at_value = review.get("at")
                date_str = at_value.isoformat() if hasattr(at_value, "isoformat") else str(at_value)

                collected.append({
                    "id": f"gp_live_{review_id}",
                    "text": text,
                    "rating": review.get("score"),
                    "author": review.get("userName"),
                    "date": date_str,
                    "url": f"https://play.google.com/store/apps/details?id={self.package_id}",
                    "language": review.get("language", "en"),
                    "version": review.get("appVersion"),
                    "developer_reply": review.get("replyContent"),
                    "thumbs_up": review.get("thumbsUpCount", 0),
                })

                if len(collected) >= count:
                    break

            if not token:
                break

        logger.info(f"Collected {len(collected)} live reviews")
        return collected
    
    def _normalize_raw_review(self, raw_review: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize raw review data from JSON files to standard format.
        
        Args:
            raw_review: Raw review data from JSON file
            
        Returns:
            Optional[Dict[str, Any]]: Normalized review or None
        """
        try:
            # Handle different JSON structures
            normalized = {
                "id": raw_review.get("id"),
                "text": raw_review.get("text", ""),
                "rating": raw_review.get("rating"),
                "author": raw_review.get("author"),
                "date": raw_review.get("date"),
                "url": raw_review.get("url"),
                "language": raw_review.get("language", "en"),
                "version": raw_review.get("version"),
                "developer_reply": raw_review.get("reply_content"),
                "thumbs_up": raw_review.get("thumbs_up", 0)
            }
            
            # Validate required fields
            if not normalized["text"] or len(normalized["text"].strip()) < 10:
                return None
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing raw review: {e}")
            return None
    
    def collect(self, use_live: bool = False, count: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect reviews from Google Play Store.
        
        Args:
            use_live: Whether to use live collection or raw data files
            count: Number of reviews to collect (for live collection)
            **kwargs: Additional parameters
            
        Returns:
            List[Dict[str, Any]]: Raw review data
        """
        if use_live:
            return self.collect_live(count=count)
        else:
            return self.collect_from_raw_data(kwargs.get("raw_data_path", "data/raw"))
