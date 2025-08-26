"""
Configuration Settings for Multi-Agent Agriculture Systems
Uses pydantic-settings for environment-based configuration
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

# Define the base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application Settings Configuration
    
    This class uses pydantic-settings to load configuration values from:
    1. Environment variables
    2. .env file (if present)
    3. Default values specified here
    """
    
    # Application Information
    APP_NAME: str = "Multi-Agent Agriculture Systems API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Satellite-Enhanced AI Agricultural Advisory System"
    
    # Environment
    ENVIRONMENT: str = "development"  # Options: development, staging, production
    DEBUG: bool = True
    
    # API Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/agriculture.db"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = None
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    
    # Demo Settings
    DEMO_MODE: bool = False
    USE_MOCK_SATELLITE_DATA: bool = True
    
    # Satellite Service
    SATELLITE_API_ENDPOINT: str = "mock"
    SATELLITE_UPDATE_INTERVAL: int = 3600  # In seconds
    
    # Financial Constants
    LOAN_AMOUNT_MAX: int = 300000  # Maximum loan amount in INR
    CROP_COST_MIN: int = 23000     # Minimum crop cost in INR
    CROP_COST_MAX: int = 38000     # Maximum crop cost in INR
    PEST_TREATMENT_COST: int = 3000  # Standard pest treatment cost in INR
    
    # System Thresholds
    AGENT_TIMEOUT_SECONDS: int = 30  # Max time for agent to respond
    CONFIDENCE_THRESHOLD: float = 0.75  # Minimum confidence score for recommendations
    
    # Redis (Optional for caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_ENABLED: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Define env file configuration
    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Create a global settings instance
settings = Settings()


# Verification function
def verify_settings() -> bool:
    """Verify critical settings and log warnings/errors"""
    if settings.ENVIRONMENT == "production":
        # Validate production settings
        if settings.DEBUG:
            print("WARNING: DEBUG mode is enabled in production environment")
        
        if settings.CORS_ORIGINS == ["*"]:
            print("WARNING: CORS is set to allow all origins in production environment")
            
        if "sqlite" in settings.DATABASE_URL:
            print("WARNING: Using SQLite in production environment")
    
    # For development environment
    if settings.ENVIRONMENT == "development" and not settings.DEBUG:
        print("INFO: DEBUG is disabled in development environment")
    
    return True


# Run validation when module is imported
verify_settings()
