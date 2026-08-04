"""
Analysis Type Classifier for Dynamic Question Routing

This module classifies user questions and determines the appropriate analysis types needed.
"""

from __future__ import annotations

from typing import Any


class AnalysisClassifier:
    """Classifier for determining required analysis types based on user questions."""

    def __init__(self) -> None:
        """Initialize the analysis classifier."""
        self.analysis_keywords = {
            "sentiment": {
                "keywords": ["sentiment", "opinion", "satisfied", "happy", "unhappy", "positive", "negative", "neutral", "feeling", "emotional", "mood", "overall", "feel"],
                "description": "Analyze customer opinions and emotional trends"
            },
            "theme": {
                "keywords": ["theme", "topic", "pattern", "subject", "category", "group", "recurring", "common", "frequent", "exploring", "new categories"],
                "description": "Identify recurring topics and patterns from reviews"
            },
            "complaint": {
                "keywords": ["complaint", "problem", "issue", "unhappy", "bad", "poor", "frustration", "dissatisfied", "wrong", "fail", "frustrations"],
                "description": "Detect common customer problems and issues"
            },
            "product": {
                "keywords": ["product", "item", "specific", "particular", "strength", "weakness", "improvement", "feature", "quality", "product quality", "feedback"],
                "description": "Analyze feedback for specific products/categories"
            },
            "rating": {
                "keywords": ["rating", "star", "score", "rate", "high-rated", "low-rated", "1-star", "5-star", "drop", "increase"],
                "description": "Analyze review ratings and rating patterns"
            },
            "trend": {
                "keywords": ["trend", "change", "over time", "increasing", "decreasing", "improving", "worsening", "recent", "time", "period"],
                "description": "Detect changes in customer opinions over time"
            },
            "recommendation": {
                "keywords": ["recommend", "suggest", "improve", "action", "solution", "fix", "better", "should", "advice"],
                "description": "Generate actionable business recommendations"
            },
            "delivery": {
                "keywords": ["delivery", "delivery times", "shipping", "arrived", "late", "fast", "slow", "time"],
                "description": "Analyze delivery-related feedback and timing"
            },
            "app_performance": {
                "keywords": ["app", "performance", "crash", "bug", "slow", "interface", "glitch", "user experience", "app performance"],
                "description": "Analyze app performance and user experience feedback"
            }
        }

    def classify_question(self, question: str) -> list[str]:
        """
        Classify a user question and determine required analysis types.

        Args:
            question: User's question

        Returns:
            List of analysis types needed
        """
        question_lower = question.lower()
        detected_analyses = []
        
        # Check for keywords in each analysis type
        for analysis_type, data in self.analysis_keywords.items():
            for keyword in data["keywords"]:
                if keyword in question_lower:
                    if analysis_type not in detected_analyses:
                        detected_analyses.append(analysis_type)
                    break
        
        # If no specific analysis detected, default to sentiment + theme
        if not detected_analyses:
            detected_analyses = ["sentiment", "theme"]
        
        return detected_analyses

    def get_analysis_description(self, analysis_type: str) -> str:
        """
        Get description for an analysis type.

        Args:
            analysis_type: Type of analysis

        Returns:
            Description of the analysis type
        """
        return self.analysis_keywords.get(analysis_type, {}).get("description", "Unknown analysis type")

    def determine_confidence(self, question: str, analysis_results: dict[str, Any]) -> str:
        """
        Determine confidence level based on question clarity and data availability.

        Args:
            question: User's question
            analysis_results: Results from analysis

        Returns:
            Confidence level: High, Medium, or Low
        """
        question_lower = question.lower()
        
        # High confidence if question is specific and has good data
        specific_keywords = ["what", "why", "how", "which", "specific", "particular"]
        question_specificity = any(keyword in question_lower for keyword in specific_keywords)
        
        # Check data availability
        data_quality = True
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict) and "count" in results:
                if results["count"] < 5:  # Low data points
                    data_quality = False
        
        if question_specificity and data_quality:
            return "High"
        elif question_specificity or data_quality:
            return "Medium"
        else:
            return "Low"
