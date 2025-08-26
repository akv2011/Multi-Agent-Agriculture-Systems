"""
Core configuration module for Multi-Agent Agriculture Systems.
Provides the base Settings class and environment handling functionality.
"""
import os
import json
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Environment types for the application."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """Base settings class using pydantic-settings."""
    
    # Application environment
    APP_ENV: Environment = Environment.DEVELOPMENT
    
    # API Settings
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    API_PREFIX: str = "/api"
    
    # WebSocket Settings
    WS_HOST: str = "localhost"
    WS_PORT: int = 8001
    WS_PATH: str = "/ws"
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Database Settings
    DB_ENGINE: str = "sqlite"
    DB_NAME: str = "satellite_data.db"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = DATA_DIR / "local_cache"
    
    # Model Settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    GEMINI_MODEL: str = "gemini-pro"
    
    # Agent Settings
    MAX_AGENTS: int = 10
    AGENT_TIMEOUT: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        validate_assignment=True
    )
        
    def get_api_url(self) -> str:
        """Get the full API URL."""
        protocol = "https" if self.APP_ENV == Environment.PRODUCTION else "http"
        return f"{protocol}://{self.API_HOST}:{self.API_PORT}{self.API_PREFIX}"
    
    def get_ws_url(self) -> str:
        """Get the full WebSocket URL."""
        protocol = "wss" if self.APP_ENV == Environment.PRODUCTION else "ws"
        return f"{protocol}://{self.WS_HOST}:{self.WS_PORT}{self.WS_PATH}"


def load_environment_settings(env: Environment = None) -> Dict[str, Any]:
    """Load environment-specific settings from JSON file."""
    if env is None:
        env_name = os.getenv("APP_ENV", "development").lower()
        try:
            env = Environment(env_name)
        except ValueError:
            env = Environment.DEVELOPMENT
    
    env_file = Path(__file__).parent / "environments" / f"{env.value}.json"
    
    if env_file.exists():
        with open(env_file, "r") as f:
            return json.load(f)
    else:
        return {}
