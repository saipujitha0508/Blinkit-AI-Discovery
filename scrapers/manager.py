"""
Scraper Manager Module

Coordinates all data scrapers and provides a unified interface
for data collection from multiple sources for the Blinkit AI Discovery Engine.
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from scrapers.google_play_scraper import GooglePlayScraper
from scrapers.reddit_scraper import RedditScraper
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.news_scraper import NewsScraper
from scrapers.app_store_scraper import AppStoreScraper
from scrapers.apify_scraper import ApifyScraper
from scrapers.base import BaseScraper
from database.models import ReviewModel, SourceType
from config.settings import get_settings
from config.constants import DATA_SOURCES


class ScraperManager:
    """
    Manager class for coordinating all data scrapers.
    Provides unified interface for multi-source data collection.
    """
    
    def __init__(self):
        """Initialize scraper manager with all available scrapers."""
        self.settings = get_settings()
        self.scrapers = {
            SourceType.GOOGLE_PLAY: GooglePlayScraper(),
            SourceType.REDDIT: RedditScraper(),
            SourceType.YOUTUBE: YouTubeScraper(),
            SourceType.NEWS: NewsScraper(),
            SourceType.APP_STORE: AppStoreScraper(),
            SourceType.APIFY: ApifyScraper()
        }
    
    def collect_from_source(
        self, 
        source: SourceType, 
        use_live: bool = False, 
        count: int = 100,
        **kwargs
    ) -> List[ReviewModel]:
        """
        Collect reviews from a specific source.
        
        Args:
            source: Source type to collect from
            use_live: Whether to use live collection or raw data files
            count: Number of reviews to collect
            **kwargs: Additional source-specific parameters
            
        Returns:
            List[ReviewModel]: Collected and processed reviews
        """
        if source not in self.scrapers:
            logger.error(f"Unknown source: {source}")
            return []
        
        scraper = self.scrapers[source]
        logger.info(f"Collecting from {source} (live={use_live}, count={count})")
        
        # Collect raw data
        raw_data = scraper.collect(use_live=use_live, count=count, **kwargs)
        
        # Process using base scraper methods
        processed_reviews = scraper.collect_and_process(use_live=use_live, count=count, **kwargs)
        
        return processed_reviews
    
    def collect_from_all_sources(
        self,
        use_live: bool = False,
        count_per_source: int = 100,
        enabled_sources: Optional[List[SourceType]] = None,
        **kwargs
    ) -> Dict[SourceType, List[ReviewModel]]:
        """
        Collect reviews from all enabled sources.
        
        Args:
            use_live: Whether to use live collection or raw data files
            count_per_source: Number of reviews to collect per source
            enabled_sources: List of sources to collect from (None = all enabled)
            **kwargs: Additional source-specific parameters
            
        Returns:
            Dict[SourceType, List[ReviewModel]]: Reviews by source
        """
        # Determine which sources to use
        if enabled_sources is None:
            enabled_sources = [
                source for source, config in DATA_SOURCES.items()
                if config.get("enabled", False)
            ]
            # Convert string source names to SourceType enums
            enabled_sources = [SourceType(source) for source in enabled_sources]
        
        logger.info(f"Collecting from {len(enabled_sources)} sources")
        
        all_reviews = {}
        
        for source in enabled_sources:
            try:
                reviews = self.collect_from_source(
                    source=source,
                    use_live=use_live,
                    count=count_per_source,
                    **kwargs
                )
                all_reviews[source] = reviews
                logger.info(f"Collected {len(reviews)} reviews from {source}")
                
            except Exception as e:
                logger.error(f"Error collecting from {source}: {e}")
                all_reviews[source] = []
        
        total_reviews = sum(len(reviews) for reviews in all_reviews.values())
        logger.info(f"Total reviews collected from all sources: {total_reviews}")
        
        return all_reviews
    
    def collect_balanced(
        self,
        total_count: int = 1000,
        use_live: bool = False,
        enabled_sources: Optional[List[SourceType]] = None,
        **kwargs
    ) -> List[ReviewModel]:
        """
        Collect a balanced set of reviews across all sources.
        
        Args:
            total_count: Total number of reviews to collect
            use_live: Whether to use live collection or raw data files
            enabled_sources: List of sources to collect from (None = all enabled)
            **kwargs: Additional source-specific parameters
            
        Returns:
            List[ReviewModel]: Combined and balanced reviews
        """
        # Determine which sources to use
        if enabled_sources is None:
            enabled_sources = [
                source for source, config in DATA_SOURCES.items()
                if config.get("enabled", False)
            ]
            enabled_sources = [SourceType(source) for source in enabled_sources]
        
        if not enabled_sources:
            logger.warning("No enabled sources found")
            return []
        
        # Calculate count per source
        count_per_source = max(1, total_count // len(enabled_sources))
        
        logger.info(f"Collecting balanced dataset: {count_per_source} per source from {len(enabled_sources)} sources")
        
        # Collect from all sources
        reviews_by_source = self.collect_from_all_sources(
            use_live=use_live,
            count_per_source=count_per_source,
            enabled_sources=enabled_sources,
            **kwargs
        )
        
        # Combine all reviews
        all_reviews = []
        for source, reviews in reviews_by_source.items():
            all_reviews.extend(reviews)
        
        logger.info(f"Total balanced reviews collected: {len(all_reviews)}")
        return all_reviews
    
    def get_source_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all data sources.
        
        Returns:
            Dict[str, Dict[str, Any]]: Source status information
        """
        status = {}
        
        for source_name, config in DATA_SOURCES.items():
            source_type = SourceType(source_name)
            status[source_name] = {
                "enabled": config.get("enabled", False),
                "priority": config.get("priority", 0),
                "scraper_available": source_type in self.scrapers,
                "live_collection_available": self._check_live_collection_available(source_type)
            }
        
        return status
    
    def _check_live_collection_available(self, source: SourceType) -> bool:
        """
        Check if live collection is available for a source.
        
        Args:
            source: Source type to check
            
        Returns:
            bool: True if live collection is available
        """
        if source == SourceType.GOOGLE_PLAY:
            return True  # Google Play scraper always available
        elif source == SourceType.REDDIT:
            return bool(self.settings.REDDIT_CLIENT_ID and self.settings.REDDIT_CLIENT_SECRET)
        elif source == SourceType.YOUTUBE:
            return False  # YouTube API requires additional setup
        elif source == SourceType.NEWS:
            return True  # RSS feeds are always available
        elif source == SourceType.APP_STORE:
            return False  # App Store collection is file-based only
        elif source == SourceType.APIFY:
            return bool(self.settings.APIFY_API_TOKEN)
        return False
