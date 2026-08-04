"""
Data Cleaner Module

Provides comprehensive data cleaning functionality including text normalization,
deduplication, quality filtering, and preprocessing for the Blinkit AI Discovery Engine.
"""

import re
from typing import List, Dict, Any, Optional, Set
from loguru import logger
from datetime import datetime
from database.models import ReviewModel
from config.constants import IGNORE_TOPICS


class DataCleaner:
    """
    Data cleaner for processing and normalizing customer reviews.
    Handles text cleaning, deduplication, and quality filtering.
    """
    
    def __init__(self):
        """Initialize data cleaner."""
        self.seen_hashes: Set[str] = set()
        self.seen_texts: Set[str] = set()
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4}', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison (lowercase, remove punctuation).
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def calculate_text_hash(self, text: str) -> str:
        """
        Calculate hash of normalized text for deduplication.
        
        Args:
            text: Text to hash
            
        Returns:
            str: Hash value
        """
        normalized = self.normalize_text(text)
        return str(hash(normalized))
    
    def is_technical_issue(self, text: str) -> bool:
        """
        Check if text discusses technical issues to be ignored.
        
        Args:
            text: Review text
            
        Returns:
            bool: True if discusses technical issues
        """
        text_lower = text.lower()
        
        for topic in IGNORE_TOPICS:
            if topic.lower() in text_lower:
                return True
        
        return False
    
    def has_minimum_quality(self, review: ReviewModel, min_length: int = 20) -> bool:
        """
        Check if review meets minimum quality standards.
        
        Args:
            review: Review model
            min_length: Minimum text length
            
        Returns:
            bool: True if meets quality standards
        """
        # Check text length
        if not review.text or len(review.text.strip()) < min_length:
            return False
        
        # Check for meaningful content (not just emojis or special chars)
        meaningful_chars = sum(1 for c in review.text if c.isalnum())
        if meaningful_chars < min_length / 2:
            return False
        
        # Check if it's a technical issue
        if self.is_technical_issue(review.text):
            return False
        
        return True
    
    def remove_duplicates(self, reviews: List[ReviewModel]) -> List[ReviewModel]:
        """
        Remove duplicate reviews based on text content.
        
        Args:
            reviews: List of review models
            
        Returns:
            List[ReviewModel]: Deduplicated reviews
        """
        unique_reviews = []
        duplicates_removed = 0
        
        for review in reviews:
            text_hash = self.calculate_text_hash(review.text)
            
            if text_hash not in self.seen_hashes:
                self.seen_hashes.add(text_hash)
                unique_reviews.append(review)
            else:
                duplicates_removed += 1
        
        logger.info(f"Removed {duplicates_removed} duplicate reviews")
        return unique_reviews
    
    def remove_similar_reviews(self, reviews: List[ReviewModel], similarity_threshold: float = 0.9) -> List[ReviewModel]:
        """
        Remove reviews that are very similar (near-duplicates).
        
        Args:
            reviews: List of review models
            similarity_threshold: Threshold for similarity (0-1)
            
        Returns:
            List[ReviewModel]: Reviews with near-duplicates removed
        """
        unique_reviews = []
        similar_removed = 0
        
        for review in reviews:
            normalized_text = self.normalize_text(review.text)
            
            # Check for similarity with existing reviews
            is_similar = False
            for existing_review in unique_reviews:
                existing_normalized = self.normalize_text(existing_review.text)
                
                # Simple similarity check based on overlap
                similarity = self._calculate_similarity(normalized_text, existing_normalized)
                
                if similarity >= similarity_threshold:
                    is_similar = True
                    similar_removed += 1
                    break
            
            if not is_similar:
                unique_reviews.append(review)
        
        logger.info(f"Removed {similar_removed} similar reviews")
        return unique_reviews
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Jaccard similarity.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def filter_by_quality(self, reviews: List[ReviewModel], min_length: int = 20) -> List[ReviewModel]:
        """
        Filter reviews by quality standards.
        
        Args:
            reviews: List of review models
            min_length: Minimum text length
            
        Returns:
            List[ReviewModel]: Filtered reviews
        """
        quality_reviews = []
        filtered_count = 0
        
        for review in reviews:
            if self.has_minimum_quality(review, min_length):
                quality_reviews.append(review)
            else:
                filtered_count += 1
        
        logger.info(f"Filtered {filtered_count} low-quality reviews")
        return quality_reviews
    
    def clean_reviews(self, reviews: List[ReviewModel], remove_duplicates: bool = True, filter_quality: bool = True) -> List[ReviewModel]:
        """
        Perform complete cleaning pipeline on reviews.
        
        Args:
            reviews: List of review models
            remove_duplicates: Whether to remove duplicates
            filter_quality: Whether to filter by quality
            
        Returns:
            List[ReviewModel]: Cleaned reviews
        """
        logger.info(f"Starting cleaning pipeline for {len(reviews)} reviews")
        
        # Clean text content
        for review in reviews:
            review.text = self.clean_text(review.text)
        
        # Filter by quality
        if filter_quality:
            reviews = self.filter_by_quality(reviews)
        
        # Remove exact duplicates only (skip expensive near-duplicate detection)
        if remove_duplicates:
            reviews = self.remove_duplicates(reviews)
        
        logger.info(f"Cleaning complete. Final count: {len(reviews)} reviews")
        return reviews
    
    def get_cleaning_stats(self, original_count: int, final_count: int) -> Dict[str, Any]:
        """
        Get statistics about the cleaning process.
        
        Args:
            original_count: Original number of reviews
            final_count: Final number of reviews
            
        Returns:
            Dict[str, Any]: Cleaning statistics
        """
        removed_count = original_count - final_count
        removal_rate = (removed_count / original_count * 100) if original_count > 0 else 0
        
        return {
            "original_count": original_count,
            "final_count": final_count,
            "removed_count": removed_count,
            "removal_rate": f"{removal_rate:.1f}%",
            "retention_rate": f"{100 - removal_rate:.1f}%"
        }
