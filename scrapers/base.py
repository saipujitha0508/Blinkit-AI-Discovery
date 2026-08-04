"""
Base Scraper Module

Defines the abstract base class for all data scrapers with common functionality,
error handling, and data validation for the Blinkit AI Discovery Engine.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from database.models import ReviewModel, SourceType


class BaseScraper(ABC):
    """
    Abstract base class for all data scrapers.
    Provides common functionality for data collection and validation.
    """
    
    def __init__(self, source_type: SourceType):
        """
        Initialize base scraper.
        
        Args:
            source_type: Type of data source
        """
        self.source_type = source_type
        self.collected_at = datetime.utcnow()
    
    @abstractmethod
    def collect(self, **kwargs) -> List[ReviewModel]:
        """
        Collect data from the source.
        
        Args:
            **kwargs: Source-specific parameters
            
        Returns:
            List[ReviewModel]: List of collected reviews
        """
        pass
    
    def _validate_review(self, review_data: Dict[str, Any]) -> bool:
        """
        Validate review data structure.
        
        Args:
            review_data: Raw review data dictionary
            
        Returns:
            bool: True if valid
        """
        required_fields = ["text"]
        return all(field in review_data for field in required_fields)
    
    def _normalize_review(self, raw_data: Dict[str, Any]) -> ReviewModel:
        """
        Normalize raw data to ReviewModel format.
        
        Args:
            raw_data: Raw review data from source
            
        Returns:
            ReviewModel: Normalized review model
        """
        # Base fields that should be present in all sources
        normalized = {
            "source": self.source_type,
            "text": raw_data.get("text", ""),
            "rating": raw_data.get("rating"),
            "author": raw_data.get("author"),
            "date": self._parse_date(raw_data.get("date")),
            "url": raw_data.get("url"),
            "language": raw_data.get("language", "en"),
            "collected_at": self.collected_at
        }
        
        # Add source-specific fields
        if self.source_type == SourceType.GOOGLE_PLAY:
            normalized.update({
                "version": raw_data.get("version"),
                "developer_reply": raw_data.get("reply_content")
            })
        elif self.source_type == SourceType.REDDIT:
            normalized.update({
                "upvotes": raw_data.get("upvotes"),
                "subreddit": raw_data.get("subreddit")
            })
        elif self.source_type == SourceType.YOUTUBE:
            normalized.update({
                "video_title": raw_data.get("video_title"),
                "likes": raw_data.get("likes")
            })
        elif self.source_type == SourceType.NEWS:
            normalized.update({
                "headline": raw_data.get("headline")
            })
        elif self.source_type == SourceType.APP_STORE:
            normalized.update({
                "upvotes": raw_data.get("upvotes"),
                "version": raw_data.get("version")
            })
        
        return ReviewModel(**normalized)
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Optional[datetime]: Parsed datetime or None
        """
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            try:
                # Try common formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            except Exception:
                pass
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _filter_empty_reviews(self, reviews: List[ReviewModel]) -> List[ReviewModel]:
        """
        Filter out reviews with empty or invalid text.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[ReviewModel]: Filtered list
        """
        valid_reviews = []
        for review in reviews:
            if review.text and len(review.text.strip()) > 10:
                valid_reviews.append(review)
            else:
                logger.debug(f"Filtered out empty review from {review.author}")
        
        logger.info(f"Filtered {len(reviews) - len(valid_reviews)} empty reviews")
        return valid_reviews
    
    def _deduplicate_reviews(self, reviews: List[ReviewModel]) -> List[ReviewModel]:
        """
        Remove duplicate reviews based on text content.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[ReviewModel]: Deduplicated list
        """
        seen_texts = set()
        unique_reviews = []
        
        for review in reviews:
            text_lower = review.text.lower().strip()
            if text_lower not in seen_texts:
                seen_texts.add(text_lower)
                unique_reviews.append(review)
            else:
                logger.debug(f"Removed duplicate review from {review.author}")
        
        logger.info(f"Removed {len(reviews) - len(unique_reviews)} duplicate reviews")
        return unique_reviews
    
    def collect_and_process(self, **kwargs) -> List[ReviewModel]:
        """
        Collect and process data with validation and filtering.
        
        Args:
            **kwargs: Source-specific parameters
            
        Returns:
            List[ReviewModel]: Processed and validated reviews
        """
        try:
            logger.info(f"Starting data collection from {self.source_type}")
            
            # Collect raw data
            raw_reviews = self.collect(**kwargs)
            logger.info(f"Collected {len(raw_reviews)} raw reviews from {self.source_type}")
            
            # Normalize to ReviewModel
            normalized_reviews = []
            for raw_data in raw_reviews:
                try:
                    if self._validate_review(raw_data):
                        normalized = self._normalize_review(raw_data)
                        normalized_reviews.append(normalized)
                except Exception as e:
                    logger.error(f"Error normalizing review: {e}")
            
            # Filter empty reviews
            filtered_reviews = self._filter_empty_reviews(normalized_reviews)
            
            # Remove duplicates
            unique_reviews = self._deduplicate_reviews(filtered_reviews)
            
            logger.info(f"Final processed reviews: {len(unique_reviews)}")
            return unique_reviews
            
        except Exception as e:
            logger.error(f"Error in data collection from {self.source_type}: {e}")
            return []
