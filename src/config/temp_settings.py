"""
Temporary simplified settings to fix the Pydantic configuration error.
"""

from pathlib import Path

# Simple configuration without Pydantic
class Settings:
    """Simple settings class without Pydantic to avoid configuration conflicts."""
    
    # Application Information
    APP_NAME = "Multi-Agent Agriculture Systems API"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Satellite-Enhanced AI Agricultural Advisory System"
    
    # Environment
    ENVIRONMENT = "development"
    DEBUG = True
    
    # API Server
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Database
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL = f"sqlite:///{BASE_DIR}/data/agriculture.db"
    
    # CORS Settings
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
    
    # Security
    API_KEY_HEADER = "X-API-Key"
    API_KEY = None
    
    # Gemini AI
    GEMINI_API_KEY = None
    
    # Redis Settings
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # Paths
    DATA_DIR = BASE_DIR / "data"
    CACHE_DIR = DATA_DIR / "local_cache"
    
    # Logging
    LOG_LEVEL = "INFO"

# Create a global settings instance
settings = Settings()
