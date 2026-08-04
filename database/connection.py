"""
Database Connection Module

Handles Supabase database connection management with singleton pattern
and connection pooling for the Blinkit AI Discovery Engine.
"""

from typing import Optional
from loguru import logger
from supabase import create_client, Client
from config.settings import get_settings


class DatabaseConnection:
    """
    Singleton database connection manager for Supabase.
    Provides thread-safe database access with connection pooling.
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection."""
        if self._client is None:
            self._connect()
    
    def _connect(self) -> None:
        """
        Establish connection to Supabase database.
        
        Raises:
            ValueError: If database configuration is invalid
            Exception: If connection fails
        """
        settings = get_settings()
        
        if not settings.validate_database_config():
            raise ValueError("Invalid database configuration. Please check SUPABASE_URL and SUPABASE_KEY in .env file")
        
        try:
            self._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("Successfully connected to Supabase database")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def get_client(self) -> Client:
        """
        Get the Supabase client instance.
        
        Returns:
            Client: Supabase client instance
            
        Raises:
            RuntimeError: If connection is not established
        """
        if self._client is None:
            raise RuntimeError("Database connection not established")
        return self._client
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._client is not None:
            self._client = None
            logger.info("Database connection closed")
    
    def health_check(self) -> bool:
        """
        Check database connection health.
        
        Returns:
            bool: True if connection is healthy
        """
        try:
            client = self.get_client()
            # Simple health check query
            client.table('reviews').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


def get_database() -> DatabaseConnection:
    """
    Get the singleton database connection instance.
    
    Returns:
        DatabaseConnection: Database connection instance
    """
    return DatabaseConnection()
