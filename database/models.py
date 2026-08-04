"""
Database Models Module

Defines Pydantic models for data validation and database schema definitions
for the Blinkit AI Discovery Engine.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SourceType(str, Enum):
    """Data source types."""
    GOOGLE_PLAY = "google_play"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    NEWS = "news"
    APP_STORE = "app_store"
    APIFY = "apify"


class RelevanceLevel(str, Enum):
    """Relevance classification levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Sentiment(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ReviewModel(BaseModel):
    """
    Review data model for customer feedback.
    Represents a single customer review from any source.
    """
    
    id: Optional[str] = Field(default=None, description="Unique review identifier")
    source: SourceType = Field(..., description="Data source type")
    text: str = Field(..., description="Review text content")
    rating: Optional[float] = Field(default=None, description="Review rating (1-5)")
    author: Optional[str] = Field(default=None, description="Review author")
    date: Optional[datetime] = Field(default=None, description="Review date")
    url: Optional[str] = Field(default=None, description="Source URL")
    language: Optional[str] = Field(default="en", description="Review language")
    
    # Source-specific fields
    version: Optional[str] = Field(default=None, description="App version (for app store reviews)")
    developer_reply: Optional[str] = Field(default=None, description="Developer response")
    upvotes: Optional[int] = Field(default=None, description="Upvotes (for Reddit)")
    subreddit: Optional[str] = Field(default=None, description="Subreddit (for Reddit)")
    video_title: Optional[str] = Field(default=None, description="Video title (for YouTube)")
    likes: Optional[int] = Field(default=None, description="Likes (for YouTube)")
    headline: Optional[str] = Field(default=None, description="Article headline (for News)")
    
    # Metadata
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="Collection timestamp")
    relevance_level: Optional[RelevanceLevel] = Field(default=None, description="Relevance classification")
    sentiment: Optional[Sentiment] = Field(default=None, description="Sentiment classification")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ThemeModel(BaseModel):
    """
    Theme model for recurring customer themes.
    """
    
    id: Optional[str] = Field(default=None, description="Unique theme identifier")
    theme: str = Field(..., description="Theme name")
    frequency: str = Field(..., description="Frequency level (High/Medium/Low)")
    priority: Optional[str] = Field(default=None, description="Business priority (High/Medium/Low)")
    confidence: Optional[str] = Field(default=None, description="Confidence level (High/Medium/Low)")
    percentage: Optional[str] = Field(default=None, description="Percentage of reviews/customers tied to this theme")
    average_rating: Optional[float] = Field(default=None, description="Average rating of reviews supporting this theme")
    customer_count: Optional[int] = Field(default=None, description="Estimated number of customers affected")
    metric: Optional[str] = Field(default=None, description="Key business/data metric (e.g. repeat-purchase rate, category-exploration rate)")
    transition_rate: Optional[str] = Field(default=None, description="Transition rate between old and new category behavior")
    behavior: Optional[str] = Field(default=None, description="Customer behavior description")
    root_cause: Optional[str] = Field(default=None, description="Root cause of the behavior")
    supporting_evidence: Optional[str] = Field(default=None, description="Supporting review themes and statistics")
    customer_quotes: Optional[str] = Field(default=None, description="Representative customer quotes")
    business_impact: Optional[str] = Field(default=None, description="Impact on new category purchase goal")
    product_opportunities: Optional[str] = Field(default=None, description="Product improvements or experiments")
    summary: str = Field(..., description="Theme summary")
    representative_quote: str = Field(..., description="Representative customer quote")
    evidence_count: int = Field(..., description="Number of reviews supporting this theme")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CustomerSegmentModel(BaseModel):
    """
    Customer segment model for behavioral segmentation.
    """
    
    id: Optional[str] = Field(default=None, description="Unique segment identifier")
    segment_name: str = Field(..., description="Segment name")
    description: str = Field(..., description="Segment description")
    goals: List[str] = Field(default_factory=list, description="Customer goals")
    pain_points: List[str] = Field(default_factory=list, description="Customer pain points")
    shopping_behavior: str = Field(..., description="Shopping behavior description")
    opportunity: str = Field(..., description="Business opportunity")
    size_percentage: Optional[float] = Field(default=None, description="Percentage of total customers")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PainPointModel(BaseModel):
    """
    Pain point model for customer complaints clustering.
    """
    
    id: Optional[str] = Field(default=None, description="Unique pain point identifier")
    category: str = Field(..., description="Pain point category")
    description: str = Field(..., description="Pain point description")
    frequency: int = Field(..., description="Number of mentions")
    severity: str = Field(..., description="Severity level (High/Medium/Low)")
    examples: List[str] = Field(default_factory=list, description="Example complaints")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OpportunityModel(BaseModel):
    """
    Product opportunity model for business opportunities.
    """
    
    id: Optional[str] = Field(default=None, description="Unique opportunity identifier")
    problem: str = Field(..., description="Problem statement")
    evidence: str = Field(..., description="Supporting evidence")
    need: str = Field(..., description="Customer need")
    ai_solution: str = Field(..., description="AI-generated solution")
    business_impact: str = Field(..., description="Business impact description")
    priority: str = Field(..., description="Priority level (High/Medium/Low)")
    confidence_score: float = Field(..., description="AI confidence score (0-1)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisResultModel(BaseModel):
    """
    Analysis result model for storing AI pipeline outputs.
    """
    
    id: Optional[str] = Field(default=None, description="Unique analysis identifier")
    analysis_type: str = Field(..., description="Type of analysis performed")
    stage: str = Field(..., description="AI pipeline stage")
    results: Dict[str, Any] = Field(default_factory=dict, description="Analysis results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BusinessInsightModel(BaseModel):
    """
    Business insight model for strategic recommendations.
    """
    
    id: Optional[str] = Field(default=None, description="Unique insight identifier")
    insight: str = Field(..., description="Insight statement")
    category: str = Field(..., description="Insight category")
    impact_area: str = Field(..., description="Business impact area")
    recommendation: str = Field(..., description="Actionable recommendation")
    priority: str = Field(..., description="Priority level")
    confidence: float = Field(..., description="Confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
