"""
Application Configuration Module

Handles loading and validating configuration from environment variables
using Pydantic for type safety and validation.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Provides type-safe configuration management with validation.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ============================================
    # AI MODELS
    # ============================================
    
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for AI model access"
    )
    
    GROQ_API_KEY: Optional[str] = Field(
        default=None,
        description="Groq API key for Llama model access"
    )
    
    # ============================================
    # DATABASE
    # ============================================
    
    SUPABASE_URL: Optional[str] = Field(
        default=None,
        description="Supabase database URL"
    )
    
    SUPABASE_KEY: Optional[str] = Field(
        default=None,
        description="Supabase database API key"
    )
    
    # ============================================
    # DATA COLLECTION APIS
    # ============================================
    
    APIFY_API_TOKEN: Optional[str] = Field(
        default=None,
        description="Apify API token for web scraping"
    )
    
    REDDIT_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="Reddit API client ID"
    )
    
    REDDIT_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="Reddit API client secret"
    )
    
    REDDIT_USER_AGENT: Optional[str] = Field(
        default=None,
        description="Reddit API user agent string"
    )
    
    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    
    APP_NAME: str = Field(
        default="Blinkit AI Discovery Engine",
        description="Application name"
    )
    
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag"
    )
    
    # ============================================
    # DATA PROCESSING
    # ============================================
    
    MAX_REVIEWS_PER_SOURCE: int = Field(
        default=1000,
        description="Maximum reviews to collect per source"
    )
    
    BATCH_SIZE: int = Field(
        default=100,
        description="Batch size for data processing"
    )
    
    RELEVANCE_THRESHOLD: float = Field(
        default=0.7,
        description="Threshold for relevance classification"
    )
    
    # ============================================
    # AI PIPELINE
    # ============================================
    
    AI_MODEL_PRIMARY: str = Field(
        default="gemini",
        description="Primary AI model to use"
    )
    
    AI_MODEL_FALLBACK: str = Field(
        default="groq",
        description="Fallback AI model"
    )
    
    MAX_TOKENS: int = Field(
        default=4000,
        description="Maximum tokens for AI model responses"
    )
    
    TEMPERATURE: float = Field(
        default=0.7,
        description="Temperature for AI model generation"
    )
    
    # ============================================
    # DASHBOARD
    # ============================================
    
    REFRESH_INTERVAL: int = Field(
        default=300,
        description="Dashboard refresh interval in seconds"
    )
    
    CACHE_DURATION: int = Field(
        default=3600,
        description="Cache duration in seconds"
    )
    
    # ============================================
    # DATA PATHS
    # ============================================
    
    DATA_RAW_PATH: str = Field(
        default="data/raw",
        description="Path to raw data directory"
    )
    
    DATA_CLEANED_PATH: str = Field(
        default="data/cleaned",
        description="Path to cleaned data directory"
    )
    
    DATA_ANALYZED_PATH: str = Field(
        default="data/analyzed",
        description="Path to analyzed data directory"
    )
    
    def validate_ai_config(self) -> bool:
        """
        Validate that at least one AI model is configured.
        
        Returns:
            bool: True if AI configuration is valid
        """
        return bool(self.GEMINI_API_KEY or self.GROQ_API_KEY)
    
    def validate_database_config(self) -> bool:
        """
        Validate database configuration.
        
        Returns:
            bool: True if database configuration is valid
        """
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings: Application settings
    """
    return settings
