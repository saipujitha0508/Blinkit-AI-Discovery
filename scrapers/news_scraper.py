"""
News Scraper Module

Collects news articles about Blinkit from RSS feeds
using Feedparser and existing raw data files.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
import feedparser

from scrapers.base import BaseScraper
from database.models import SourceType
from config.settings import get_settings
from config.constants import DATA_SOURCES


class NewsScraper(BaseScraper):
    """
    Scraper for news articles about Blinkit.
    Collects articles from RSS feeds of major business publications.
    """
    
    def __init__(self):
        """Initialize News scraper."""
        super().__init__(SourceType.NEWS)
        self.settings = get_settings()
        self.news_sources = DATA_SOURCES["news"]["sources"]
        
        # RSS feed URLs for major Indian business publications
        self.rss_feeds = {
            "Moneycontrol": "https://www.moneycontrol.com/rss/news.xml",
            "Economic Times": "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
            "Inc42": "https://inc42.com/feed/",
            "YourStory": "https://yourstory.com/feed/",
            "Mint": "https://www.livemint.com/rss/news"
        }
    
    def collect_from_raw_data(self, raw_data_path: str = "data/raw") -> List[Dict[str, Any]]:
        """
        Collect articles from existing raw data JSON files.
        
        Args:
            raw_data_path: Path to raw data directory
            
        Returns:
            List[Dict[str, Any]]: Raw article data from files
        """
        raw_articles = []
        data_path = Path(raw_data_path)
        
        # Find all News JSON files (if any)
        news_files = list(data_path.glob("news*.json"))
        
        logger.info(f"Found {len(news_files)} News data files")
        
        for file_path in news_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract articles from different file formats
                if isinstance(data, dict) and "reviews" in data:
                    file_articles = data["reviews"]
                elif isinstance(data, list):
                    file_articles = data
                else:
                    logger.warning(f"Unexpected format in {file_path.name}")
                    continue
                
                # Normalize article format
                for article in file_articles:
                    normalized = self._normalize_raw_article(article)
                    if normalized:
                        raw_articles.append(normalized)
                
                logger.info(f"Loaded {len(file_articles)} articles from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        logger.info(f"Total raw articles from files: {len(raw_articles)}")
        return raw_articles
    
    def collect_live(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Collect live articles from RSS feeds.
        
        Args:
            count: Number of articles to collect per source
            
        Returns:
            List[Dict[str, Any]]: Raw article data from RSS feeds
        """
        try:
            logger.info(f"Collecting live articles from RSS feeds")
            
            articles = []
            
            # Collect from each RSS feed
            for source_name, feed_url in self.rss_feeds.items():
                try:
                    if source_name not in self.news_sources:
                        continue
                    
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:count]:
                        # Check if article mentions Blinkit or related terms
                        title = entry.get('title', '').lower()
                        description = entry.get('description', '').lower()
                        
                        blinkit_keywords = ['blinkit', 'grofers', 'quick commerce', 'instant delivery']
                        
                        if any(keyword in title or keyword in description for keyword in blinkit_keywords):
                            normalized = {
                                "id": f"news_{source_name}_{hash(entry.get('link', ''))}",
                                "text": f"{entry.get('title', '')}\n\n{entry.get('description', '')}",
                                "author": entry.get('author', source_name),
                                "date": entry.get('published'),
                                "url": entry.get('link'),
                                "headline": entry.get('title'),
                                "language": "en"
                            }
                            articles.append(normalized)
                    
                    headline_count = sum(1 for a in articles if a.get('headline'))
                    logger.info(f"Collected {headline_count} articles from {source_name}")
                    
                except Exception as e:
                    logger.error(f"Error collecting from {source_name}: {e}")
            
            logger.info(f"Total live articles collected: {len(articles)}")
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting live news articles: {e}")
            return []
    
    def _normalize_raw_article(self, raw_article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize raw article data from JSON files to standard format.
        
        Args:
            raw_article: Raw article data from JSON file
            
        Returns:
            Optional[Dict[str, Any]]: Normalized article or None
        """
        try:
            # Handle different JSON structures
            normalized = {
                "id": raw_article.get("id"),
                "text": raw_article.get("text", ""),
                "author": raw_article.get("author"),
                "date": raw_article.get("date"),
                "url": raw_article.get("url"),
                "headline": raw_article.get("headline"),
                "language": raw_article.get("language", "en")
            }
            
            # Validate required fields
            if not normalized["text"] or len(normalized["text"].strip()) < 10:
                return None
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing raw article: {e}")
            return None
    
    def collect(self, use_live: bool = False, count: int = 50, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect articles from news sources.
        
        Args:
            use_live: Whether to use live collection or raw data files
            count: Number of articles to collect (for live collection)
            **kwargs: Additional parameters
            
        Returns:
            List[Dict[str, Any]]: Raw article data
        """
        if use_live:
            return self.collect_live(count=count)
        else:
            return self.collect_from_raw_data(kwargs.get("raw_data_path", "data/raw"))
