"""
Config Module for Multi-Agent Agriculture Systems
Provides centralized access to application configuration

This module exports:
1. ConfigService - The main configuration service singleton
2. get_config - Function to get the ConfigService instance
3. Settings - The base settings class with environment support
4. Environment - Enum of available environments
"""

from .settings import settings
from .core import Settings, Environment, load_environment_settings
from .service import get_config, config_service, ConfigService

__all__ = [
    # Legacy exports
    "settings", 
    "get_config", 
    "config_service",
    
    # New exports
    "Settings",
    "Environment",
    "ConfigService",
    "load_environment_settings"
]
