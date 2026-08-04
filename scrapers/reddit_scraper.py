"""
Reddit Scraper Module

Collects customer discussions from Reddit about Blinkit
using PRAW library and existing raw data files.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
import praw

from scrapers.base import BaseScraper
from database.models import SourceType
from config.settings import get_settings
from config.constants import DATA_SOURCES


class RedditScraper(BaseScraper):
    """
    Scraper for Reddit discussions about Blinkit.
    Collects posts and comments from relevant subreddits.
    """
    
    def __init__(self):
        """Initialize Reddit scraper."""
        super().__init__(SourceType.REDDIT)
        self.settings = get_settings()
        self.search_queries = DATA_SOURCES["reddit"]["search_queries"]
    
    def collect_from_raw_data(self, raw_data_path: str = "data/raw") -> List[Dict[str, Any]]:
        """
        Collect discussions from existing raw data JSON files.
        
        Args:
            raw_data_path: Path to raw data directory
            
        Returns:
            List[Dict[str, Any]]: Raw discussion data from files
        """
        raw_discussions = []
        data_path = Path(raw_data_path)
        
        # Find all Reddit JSON files
        reddit_files = list(data_path.glob("reddit*.json"))
        
        logger.info(f"Found {len(reddit_files)} Reddit data files")
        
        for file_path in reddit_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract discussions from different file formats
                if isinstance(data, dict) and "reviews" in data:
                    file_discussions = data["reviews"]
                elif isinstance(data, list):
                    file_discussions = data
                else:
                    logger.warning(f"Unexpected format in {file_path.name}")
                    continue
                
                # Normalize discussion format
                for discussion in file_discussions:
                    normalized = self._normalize_raw_discussion(discussion)
                    if normalized:
                        raw_discussions.append(normalized)
                
                logger.info(f"Loaded {len(file_discussions)} discussions from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        logger.info(f"Total raw discussions from files: {len(raw_discussions)}")
        return raw_discussions
    
    def collect_live(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Collect live discussions from Reddit using PRAW.
        
        Args:
            count: Number of discussions to collect
            
        Returns:
            List[Dict[str, Any]]: Raw discussion data from Reddit
        """
        try:
            if not all([self.settings.REDDIT_CLIENT_ID, self.settings.REDDIT_CLIENT_SECRET]):
                logger.warning("Reddit API credentials not configured. Using raw data instead.")
                return self.collect_from_raw_data()
            
            # Initialize Reddit instance
            reddit = praw.Reddit(
                client_id=self.settings.REDDIT_CLIENT_ID,
                client_secret=self.settings.REDDIT_CLIENT_SECRET,
                user_agent=self.settings.REDDIT_USER_AGENT
            )
            
            logger.info(f"Collecting {count} live discussions from Reddit")
            
            discussions = []
            
            # Search for each query
            for query in self.search_queries:
                try:
                    search_results = reddit.subreddit("all").search(query, limit=count // len(self.search_queries))
                    
                    for submission in search_results:
                        normalized = {
                            "id": f"reddit_{submission.id}",
                            "text": f"{submission.title}\n\n{submission.selftext}",
                            "author": str(submission.author) if submission.author else "[deleted]",
                            "date": submission.created_utc,
                            "url": f"https://reddit.com{submission.permalink}",
                            "upvotes": submission.score,
                            "subreddit": str(submission.subreddit),
                            "language": "en"
                        }
                        discussions.append(normalized)
                    
                    logger.info(f"Collected {len(search_results)} discussions for query: {query}")
                    
                except Exception as e:
                    logger.error(f"Error searching Reddit for query '{query}': {e}")
            
            logger.info(f"Total live discussions collected: {len(discussions)}")
            return discussions
            
        except Exception as e:
            logger.error(f"Error collecting live Reddit discussions: {e}")
            return []
    
    def _normalize_raw_discussion(self, raw_discussion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize raw discussion data from JSON files to standard format.
        
        Args:
            raw_discussion: Raw discussion data from JSON file
            
        Returns:
            Optional[Dict[str, Any]]: Normalized discussion or None
        """
        try:
            # Handle different JSON structures
            normalized = {
                "id": raw_discussion.get("id"),
                "text": raw_discussion.get("text", ""),
                "author": raw_discussion.get("author"),
                "date": raw_discussion.get("date"),
                "url": raw_discussion.get("url"),
                "upvotes": raw_discussion.get("upvotes", 0),
                "subreddit": raw_discussion.get("subreddit"),
                "language": raw_discussion.get("language", "en")
            }
            
            # Validate required fields
            if not normalized["text"] or len(normalized["text"].strip()) < 10:
                return None
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing raw discussion: {e}")
            return None
    
    def collect(self, use_live: bool = False, count: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect discussions from Reddit.
        
        Args:
            use_live: Whether to use live collection or raw data files
            count: Number of discussions to collect (for live collection)
            **kwargs: Additional parameters
            
        Returns:
            List[Dict[str, Any]]: Raw discussion data
        """
        if use_live:
            return self.collect_live(count=count)
        else:
            return self.collect_from_raw_data(kwargs.get("raw_data_path", "data/raw"))
