"""
Relevance Classifier Module

Provides AI-powered relevance classification using Gemini and Groq models
to filter reviews for product insights vs technical issues for the Blinkit AI Discovery Engine.
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from database.models import ReviewModel, RelevanceLevel
from config.settings import get_settings
from config.constants import IGNORE_TOPICS, KEEP_TOPICS, RELEVANCE_LEVELS


class RelevanceClassifier:
    """
    AI-powered relevance classifier for filtering customer reviews.
    Classifies reviews as HIGH, MEDIUM, or LOW relevance based on content.
    """
    
    def __init__(self):
        """Initialize relevance classifier."""
        self.settings = get_settings()
        self.ignore_topics = IGNORE_TOPICS
        self.keep_topics = KEEP_TOPICS
        self.relevance_thresholds = RELEVANCE_LEVELS
    
    def classify_by_keywords(self, review: ReviewModel) -> RelevanceLevel:
        """
        Classify review relevance using keyword matching (rule-based approach).
        
        Args:
            review: Review model to classify
            
        Returns:
            RelevanceLevel: Classified relevance level
        """
        text_lower = review.text.lower()
        
        # Check for ignore topics (technical issues)
        for topic in self.ignore_topics:
            if topic.lower() in text_lower:
                return RelevanceLevel.LOW
        
        # Check for keep topics (product insights)
        keep_topic_count = 0
        for topic in self.keep_topics:
            if topic.lower() in text_lower:
                keep_topic_count += 1
        
        # Classify based on keep topic count
        if keep_topic_count >= 2:
            return RelevanceLevel.HIGH
        elif keep_topic_count == 1:
            return RelevanceLevel.MEDIUM
        else:
            return RelevanceLevel.LOW
    
    def classify_by_ai(self, review: ReviewModel) -> RelevanceLevel:
        """
        Classify review relevance using AI models (Gemini/Groq).
        
        Args:
            review: Review model to classify
            
        Returns:
            RelevanceLevel: Classified relevance level
        """
        try:
            # Import AI clients here to avoid circular dependencies
            from src.analysis.gemini_client import GeminiClient
            from src.analysis.groq_client import GroqClient
            
            # Try primary AI model first
            if self.settings.AI_MODEL_PRIMARY == "gemini" and self.settings.GEMINI_API_KEY:
                return self._classify_with_gemini(review)
            elif self.settings.AI_MODEL_PRIMARY == "groq" and self.settings.GROQ_API_KEY:
                return self._classify_with_groq(review)
            else:
                # Fallback to keyword classification
                logger.warning("AI model not configured, using keyword classification")
                return self.classify_by_keywords(review)
                
        except Exception as e:
            logger.error(f"Error in AI classification: {e}")
            # Fallback to keyword classification
            return self.classify_by_keywords(review)
    
    def _classify_with_gemini(self, review: ReviewModel) -> RelevanceLevel:
        """
        Classify review using Gemini AI model.
        
        Args:
            review: Review model to classify
            
        Returns:
            RelevanceLevel: Classified relevance level
        """
        try:
            from src.analysis.gemini_client import GeminiClient
            
            client = GeminiClient(api_key=self.settings.GEMINI_API_KEY)
            
            prompt = f"""
            Classify this customer review for product insight relevance.
            
            Review: "{review.text[:500]}"
            
            Ignore topics: {', '.join(self.ignore_topics)}
            Keep topics: {', '.join(self.keep_topics)}
            
            Classify as:
            - HIGH: Discusses product insights, shopping behavior, recommendations, discovery
            - MEDIUM: Some relevant content but mixed with other topics
            - LOW: Technical issues, bugs, login problems, payment failures
            
            Return only one word: HIGH, MEDIUM, or LOW
            """
            
            response = client.generate_content(prompt)
            
            # Parse response
            response_upper = response.strip().upper()
            
            if "HIGH" in response_upper:
                return RelevanceLevel.HIGH
            elif "MEDIUM" in response_upper:
                return RelevanceLevel.MEDIUM
            else:
                return RelevanceLevel.LOW
                
        except Exception as e:
            logger.error(f"Error classifying with Gemini: {e}")
            return self.classify_by_keywords(review)
    
    def _classify_with_groq(self, review: ReviewModel) -> RelevanceLevel:
        """
        Classify review using Groq AI model.
        
        Args:
            review: Review model to classify
            
        Returns:
            RelevanceLevel: Classified relevance level
        """
        try:
            from src.analysis.groq_client import GroqClient
            
            client = GroqClient(api_key=self.settings.GROQ_API_KEY)
            
            prompt = f"""
            Classify this customer review for product insight relevance.
            
            Review: "{review.text[:500]}"
            
            Ignore topics: {', '.join(self.ignore_topics)}
            Keep topics: {', '.join(self.keep_topics)}
            
            Classify as:
            - HIGH: Discusses product insights, shopping behavior, recommendations, discovery
            - MEDIUM: Some relevant content but mixed with other topics
            - LOW: Technical issues, bugs, login problems, payment failures
            
            Return only one word: HIGH, MEDIUM, or LOW
            """
            
            response = client.generate_content(prompt)
            
            # Parse response
            response_upper = response.strip().upper()
            
            if "HIGH" in response_upper:
                return RelevanceLevel.HIGH
            elif "MEDIUM" in response_upper:
                return RelevanceLevel.MEDIUM
            else:
                return RelevanceLevel.LOW
                
        except Exception as e:
            logger.error(f"Error classifying with Groq: {e}")
            return self.classify_by_keywords(review)
    
    def classify_batch(
        self, 
        reviews: List[ReviewModel], 
        use_ai: bool = False,
        batch_size: int = 10
    ) -> List[ReviewModel]:
        """
        Classify a batch of reviews.
        
        Args:
            reviews: List of review models to classify
            use_ai: Whether to use AI models or keyword classification
            batch_size: Batch size for AI processing
            
        Returns:
            List[ReviewModel]: Reviews with relevance classification
        """
        logger.info(f"Classifying {len(reviews)} reviews (use_ai={use_ai})")
        
        classified_reviews = []
        
        for i, review in enumerate(reviews):
            try:
                if use_ai:
                    # Use AI classification with rate limiting
                    if i % batch_size == 0 and i > 0:
                        logger.info(f"Classified {i} reviews, pausing for rate limit...")
                    
                    review.relevance_level = self.classify_by_ai(review)
                else:
                    # Use keyword classification (faster)
                    review.relevance_level = self.classify_by_keywords(review)
                
                classified_reviews.append(review)
                
            except Exception as e:
                logger.error(f"Error classifying review {i}: {e}")
                # Fallback to keyword classification
                review.relevance_level = self.classify_by_keywords(review)
                classified_reviews.append(review)
        
        # Log classification statistics
        high_count = sum(1 for r in classified_reviews if r.relevance_level == RelevanceLevel.HIGH)
        medium_count = sum(1 for r in classified_reviews if r.relevance_level == RelevanceLevel.MEDIUM)
        low_count = sum(1 for r in classified_reviews if r.relevance_level == RelevanceLevel.LOW)
        
        logger.info(f"Classification complete: HIGH={high_count}, MEDIUM={medium_count}, LOW={low_count}")
        
        return classified_reviews
    
    def filter_by_relevance(
        self, 
        reviews: List[ReviewModel], 
        min_relevance: RelevanceLevel = RelevanceLevel.MEDIUM
    ) -> List[ReviewModel]:
        """
        Filter reviews by minimum relevance level.
        
        Args:
            reviews: List of review models
            min_relevance: Minimum relevance level to keep
            
        Returns:
            List[ReviewModel]: Filtered reviews
        """
        relevance_order = {
            RelevanceLevel.HIGH: 3,
            RelevanceLevel.MEDIUM: 2,
            RelevanceLevel.LOW: 1
        }
        
        min_score = relevance_order.get(min_relevance, 2)
        
        filtered_reviews = [
            review for review in reviews
            if relevance_order.get(review.relevance_level, 0) >= min_score
        ]
        
        removed_count = len(reviews) - len(filtered_reviews)
        logger.info(f"Filtered {removed_count} reviews below {min_relevance} relevance")
        
        return filtered_reviews
    
    def get_relevance_distribution(self, reviews: List[ReviewModel]) -> Dict[str, int]:
        """
        Get distribution of relevance levels in reviews.
        
        Args:
            reviews: List of review models
            
        Returns:
            Dict[str, int]: Count of reviews by relevance level
        """
        distribution = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "UNCHECKED": 0
        }
        
        for review in reviews:
            if review.relevance_level:
                distribution[review.relevance_level.value.upper()] += 1
            else:
                distribution["UNCHECKED"] += 1
        
        return distribution
