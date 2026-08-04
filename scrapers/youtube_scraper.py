"""
YouTube Scraper Module

Collects comments from YouTube videos about Blinkit
using YouTube Transcript API and existing raw data files.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

from scrapers.base import BaseScraper
from database.models import SourceType
from config.settings import get_settings
from config.constants import DATA_SOURCES


class YouTubeScraper(BaseScraper):
    """
    Scraper for YouTube comments about Blinkit.
    Collects comments from relevant videos.
    """
    
    def __init__(self):
        """Initialize YouTube scraper."""
        super().__init__(SourceType.YOUTUBE)
        self.settings = get_settings()
        self.search_queries = DATA_SOURCES["youtube"]["search_queries"]
    
    def collect_from_raw_data(self, raw_data_path: str = "data/raw") -> List[Dict[str, Any]]:
        """
        Collect comments from existing raw data JSON files.
        
        Args:
            raw_data_path: Path to raw data directory
            
        Returns:
            List[Dict[str, Any]]: Raw comment data from files
        """
        raw_comments = []
        data_path = Path(raw_data_path)
        
        # Find all YouTube JSON files (if any)
        youtube_files = list(data_path.glob("youtube*.json"))
        
        logger.info(f"Found {len(youtube_files)} YouTube data files")
        
        for file_path in youtube_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract comments from different file formats
                if isinstance(data, dict) and "reviews" in data:
                    file_comments = data["reviews"]
                elif isinstance(data, list):
                    file_comments = data
                else:
                    logger.warning(f"Unexpected format in {file_path.name}")
                    continue
                
                # Normalize comment format
                for comment in file_comments:
                    normalized = self._normalize_raw_comment(comment)
                    if normalized:
                        raw_comments.append(normalized)
                
                logger.info(f"Loaded {len(file_comments)} comments from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        logger.info(f"Total raw comments from files: {len(raw_comments)}")
        return raw_comments
    
    def collect_live(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Collect live comments from YouTube using API.
        
        Args:
            count: Number of comments to collect
            
        Returns:
            List[Dict[str, Any]]: Raw comment data from YouTube
        """
        try:
            logger.info(f"Collecting {count} live comments from YouTube")
            
            # YouTube API integration would go here
            # For now, return empty list as this requires YouTube Data API credentials
            logger.warning("YouTube API integration requires additional setup. Using raw data instead.")
            return self.collect_from_raw_data()
            
        except Exception as e:
            logger.error(f"Error collecting live YouTube comments: {e}")
            return []
    
    def _normalize_raw_comment(self, raw_comment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize raw comment data from JSON files to standard format.
        
        Args:
            raw_comment: Raw comment data from JSON file
            
        Returns:
            Optional[Dict[str, Any]]: Normalized comment or None
        """
        try:
            # Handle different JSON structures
            normalized = {
                "id": raw_comment.get("id"),
                "text": raw_comment.get("text", ""),
                "author": raw_comment.get("author"),
                "date": raw_comment.get("date"),
                "url": raw_comment.get("url"),
                "likes": raw_comment.get("likes", 0),
                "video_title": raw_comment.get("video_title"),
                "language": raw_comment.get("language", "en")
            }
            
            # Validate required fields
            if not normalized["text"] or len(normalized["text"].strip()) < 10:
                return None
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing raw comment: {e}")
            return None
    
    def collect(self, use_live: bool = False, count: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect comments from YouTube.
        
        Args:
            use_live: Whether to use live collection or raw data files
            count: Number of comments to collect (for live collection)
            **kwargs: Additional parameters
            
        Returns:
            List[Dict[str, Any]]: Raw comment data
        """
        if use_live:
            return self.collect_live(count=count)
        else:
            return self.collect_from_raw_data(kwargs.get("raw_data_path", "data/raw"))
