"""
Database Repository Module

Provides CRUD operations for all data models with error handling,
logging, and data validation for the Blinkit AI Discovery Engine.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from supabase import Client

from database.models import (
    ReviewModel, ThemeModel, CustomerSegmentModel, 
    PainPointModel, OpportunityModel, AnalysisResultModel, BusinessInsightModel
)
from database.connection import get_database


class ReviewRepository:
    """Repository for review data operations."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_database()
        self.client = self.db.get_client()
        self.table_name = "reviews"
    
    def create(self, review: ReviewModel) -> Optional[str]:
        """
        Create a new review record.
        
        Args:
            review: Review model instance
            
        Returns:
            Optional[str]: Created record ID or None if failed
        """
        try:
            result = self.client.table(self.table_name).insert(review.dict(exclude_none=True)).execute()
            logger.info(f"Created review with ID: {result.data[0]['id']}")
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create review: {e}")
            return None
    
    def create_batch(self, reviews: List[ReviewModel]) -> int:
        """
        Create multiple review records in batch.
        
        Args:
            reviews: List of review models
            
        Returns:
            int: Number of successfully created records
        """
        try:
            data = [review.dict(exclude_none=True) for review in reviews]
            result = self.client.table(self.table_name).insert(data).execute()
            logger.info(f"Created {len(result.data)} reviews in batch")
            return len(result.data)
        except Exception as e:
            logger.error(f"Failed to create batch reviews: {e}")
            return 0
    
    def get_by_id(self, review_id: str) -> Optional[ReviewModel]:
        """
        Get a review by ID.
        
        Args:
            review_id: Review identifier
            
        Returns:
            Optional[ReviewModel]: Review model or None if not found
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("id", review_id).execute()
            if result.data:
                return ReviewModel(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get review {review_id}: {e}")
            return None
    
    def get_by_source(self, source: str, limit: int = 100) -> List[ReviewModel]:
        """
        Get reviews by source type.
        
        Args:
            source: Source type
            limit: Maximum number of records
            
        Returns:
            List[ReviewModel]: List of review models
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("source", source).limit(limit).execute()
            return [ReviewModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get reviews by source {source}: {e}")
            return []
    
    def get_by_relevance(self, relevance_level: str, limit: int = 100) -> List[ReviewModel]:
        """
        Get reviews by relevance level.
        
        Args:
            relevance_level: Relevance classification
            limit: Maximum number of records
            
        Returns:
            List[ReviewModel]: List of review models
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("relevance_level", relevance_level).limit(limit).execute()
            return [ReviewModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get reviews by relevance {relevance_level}: {e}")
            return []
    
    def get_all(self, limit: int = 1000, offset: int = 0) -> List[ReviewModel]:
        """
        Get all reviews with pagination.
        
        Args:
            limit: Maximum number of records
            offset: Offset for pagination
            
        Returns:
            List[ReviewModel]: List of review models
        """
        try:
            result = self.client.table(self.table_name).select("*").range(offset, offset + limit - 1).execute()
            return [ReviewModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get all reviews: {e}")
            return []
    
    def update_relevance(self, review_id: str, relevance_level: str) -> bool:
        """
        Update review relevance classification.
        
        Args:
            review_id: Review identifier
            relevance_level: New relevance level
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.table(self.table_name).update({"relevance_level": relevance_level}).eq("id", review_id).execute()
            logger.info(f"Updated relevance for review {review_id} to {relevance_level}")
            return True
        except Exception as e:
            logger.error(f"Failed to update relevance for review {review_id}: {e}")
            return False
    
    def update_sentiment(self, review_id: str, sentiment: str) -> bool:
        """
        Update review sentiment classification.
        
        Args:
            review_id: Review identifier
            sentiment: New sentiment classification
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.table(self.table_name).update({"sentiment": sentiment}).eq("id", review_id).execute()
            logger.info(f"Updated sentiment for review {review_id} to {sentiment}")
            return True
        except Exception as e:
            logger.error(f"Failed to update sentiment for review {review_id}: {e}")
            return False
    
    def delete(self, review_id: str) -> bool:
        """
        Delete a review by ID.
        
        Args:
            review_id: Review identifier
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.table(self.table_name).delete().eq("id", review_id).execute()
            logger.info(f"Deleted review {review_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete review {review_id}: {e}")
            return False


class ThemeRepository:
    """Repository for theme data operations."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_database()
        self.client = self.db.get_client()
        self.table_name = "themes"
    
    def create(self, theme: ThemeModel) -> Optional[str]:
        """Create a new theme record."""
        try:
            result = self.client.table(self.table_name).insert(theme.dict(exclude_none=True)).execute()
            logger.info(f"Created theme: {theme.theme}")
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create theme: {e}")
            return None
    
    def get_all(self) -> List[ThemeModel]:
        """Get all themes."""
        try:
            result = self.client.table(self.table_name).select("*").execute()
            return [ThemeModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get themes: {e}")
            return []


class AnalysisRepository:
    """Repository for analysis results operations."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_database()
        self.client = self.db.get_client()
        self.table_name = "analysis_results"
    
    def create(self, analysis: AnalysisResultModel) -> Optional[str]:
        """Create a new analysis result record."""
        try:
            result = self.client.table(self.table_name).insert(analysis.dict(exclude_none=True)).execute()
            logger.info(f"Created analysis result: {analysis.analysis_type}")
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create analysis result: {e}")
            return None
    
    def get_by_type(self, analysis_type: str) -> List[AnalysisResultModel]:
        """Get analysis results by type."""
        try:
            result = self.client.table(self.table_name).select("*").eq("analysis_type", analysis_type).execute()
            return [AnalysisResultModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get analysis results by type {analysis_type}: {e}")
            return []
    
    def get_latest(self, analysis_type: str) -> Optional[AnalysisResultModel]:
        """Get the latest analysis result by type."""
        try:
            result = self.client.table(self.table_name).select("*").eq("analysis_type", analysis_type).order("created_at", desc=True).limit(1).execute()
            if result.data:
                return AnalysisResultModel(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get latest analysis result: {e}")
            return None


class OpportunityRepository:
    """Repository for opportunity data operations."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_database()
        self.client = self.db.get_client()
        self.table_name = "opportunities"
    
    def create(self, opportunity: OpportunityModel) -> Optional[str]:
        """Create a new opportunity record."""
        try:
            result = self.client.table(self.table_name).insert(opportunity.dict(exclude_none=True)).execute()
            logger.info(f"Created opportunity: {opportunity.problem[:50]}...")
            return result.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create opportunity: {e}")
            return None
    
    def get_all(self) -> List[OpportunityModel]:
        """Get all opportunities."""
        try:
            result = self.client.table(self.table_name).select("*").order("confidence_score", desc=True).execute()
            return [OpportunityModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get opportunities: {e}")
            return []
    
    def get_by_priority(self, priority: str) -> List[OpportunityModel]:
        """Get opportunities by priority level."""
        try:
            result = self.client.table(self.table_name).select("*").eq("priority", priority).execute()
            return [OpportunityModel(**item) for item in result.data]
        except Exception as e:
            logger.error(f"Failed to get opportunities by priority {priority}: {e}")
            return []
