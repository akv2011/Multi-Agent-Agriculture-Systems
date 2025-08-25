"""
Configuration Service for Multi-Agent Agriculture Systems
Provides access to centralized configuration settings
"""

import os
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional, List

from .core import Settings, Environment, load_environment_settings
from .settings import settings as legacy_settings

logger = logging.getLogger(__name__)

class ConfigService:
    """Service to access centralized application configuration
    
    This service provides a unified interface to access:
    1. Environment-based settings (dev/prod)
    2. Regional data (state-specific agricultural constants)
    3. Application-specific configuration
    """
    
    _instance = None
    _settings = None
    _environment_config = None
    _region_config = None
    _current_region = None
    
    def __new__(cls):
        """Ensure only one instance of ConfigService exists."""
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the configuration service"""
        # Load both new and legacy settings
        self._settings = Settings()
        self.legacy_settings = legacy_settings
        
        # Load environment-specific configuration
        self._environment_config = load_environment_settings(self._settings.APP_ENV)
        
        # Set default region (can be changed at runtime)
        self._current_region = os.getenv("REGION", "maharashtra")
        self._load_region_config()
        
        logger.info(f"Configuration service initialized with {self._settings.APP_ENV} environment")
    
    def _load_region_config(self):
        """Load region-specific configuration."""
        region_file = Path(__file__).parent / "regions" / f"{self._current_region}.json"
        
        if region_file.exists():
            try:
                with open(region_file, "r") as f:
                    self._region_config = json.load(f)
                logger.debug(f"Loaded configuration for region: {self._current_region}")
            except Exception as e:
                logger.error(f"Failed to load region config: {e}")
                self._region_config = {}
        else:
            logger.warning(f"No configuration found for region: {self._current_region}")
            self._region_config = {}
            
    @property
    def settings(self) -> Settings:
        """Get the base settings."""
        return self._settings
            
    def get_database_url(self) -> str:
        """Get the database URL for the current environment"""
        return self.legacy_settings.DATABASE_URL
    
    def get_cors_origins(self) -> List[str]:
        """Get the list of allowed CORS origins"""
        return self.legacy_settings.CORS_ORIGINS
    
    def get_api_settings(self) -> dict:
        """Get API server settings"""
        return {
            "host": self.get("API_HOST", self.legacy_settings.HOST),
            "port": self.get("API_PORT", self.legacy_settings.PORT),
            "debug": self.get("DEBUG", self.legacy_settings.DEBUG),
            "environment": self._settings.APP_ENV,
        }
    
    def get_financial_limits(self) -> dict:
        """Get financial constants"""
        return {
            "loan_max": self.legacy_settings.LOAN_AMOUNT_MAX,
            "crop_cost_min": self.legacy_settings.CROP_COST_MIN,
            "crop_cost_max": self.legacy_settings.CROP_COST_MAX,
            "pest_treatment_cost": self.legacy_settings.PEST_TREATMENT_COST,
        }
    
    def get_system_thresholds(self) -> dict:
        """Get system threshold values"""
        return {
            "agent_timeout": self.legacy_settings.AGENT_TIMEOUT_SECONDS,
            "confidence_threshold": self.legacy_settings.CONFIDENCE_THRESHOLD,
        }
    
    def is_development_mode(self) -> bool:
        """Check if application is running in development mode"""
        return self._settings.APP_ENV == Environment.DEVELOPMENT
    
    def is_production_mode(self) -> bool:
        """Check if application is running in production mode"""
        return self._settings.APP_ENV == Environment.PRODUCTION
    
    def is_staging_mode(self) -> bool:
        """Check if application is running in staging mode"""
        return self._settings.APP_ENV == Environment.STAGING
        
    @property
    def environment(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        return self._environment_config
    
    @property
    def region(self) -> Dict[str, Any]:
        """Get region-specific configuration."""
        return self._region_config
    
    def get_region_name(self) -> str:
        """Get the current region name."""
        return self._current_region
    
    def set_region(self, region_name: str) -> bool:
        """Change the current region."""
        old_region = self._current_region
        self._current_region = region_name
        self._load_region_config()
        logger.info(f"Changed region from {old_region} to {region_name}")
        return True
    
    def get_available_regions(self) -> list:
        """Get list of available regions."""
        regions_dir = Path(__file__).parent / "regions"
        return [f.stem for f in regions_dir.glob("*.json")]
    
    def get(self, key: str, default=None) -> Any:
        """Get a configuration value, checking in order: environment, base settings."""
        # First check environment config
        if key in self._environment_config:
            return self._environment_config[key]
        
        # Then check base settings
        if hasattr(self._settings, key):
            return getattr(self._settings, key)
        
        # Return default if not found
        return default
    
    def get_region_data(self, path: str = None, default=None) -> Any:
        """
        Get data from the region configuration.
        
        Args:
            path: Dot-notation path to the nested value (e.g. "agriculture_data.major_crops")
            default: Default value if path not found
            
        Returns:
            The configuration value or default
        """
        if not path:
            return self._region_config
            
        current = self._region_config
        for part in path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def get_api_url(self) -> str:
        """Get the full API URL."""
        return self._settings.get_api_url()
    
    def get_ws_url(self) -> str:
        """Get the full WebSocket URL."""
        return self._settings.get_ws_url()


# Create global instance of config service
config_service = ConfigService()

@lru_cache()
def get_config() -> ConfigService:
    """Get the global configuration service instance"""
    return config_service
