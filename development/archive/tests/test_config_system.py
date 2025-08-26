"""
Unit tests for the configuration management system
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment
os.environ["APP_ENV"] = "testing"

from src.config.core import Settings, Environment, load_environment_settings
from src.config.service import ConfigService, get_config


class TestConfigCore(unittest.TestCase):
    """Test the core configuration settings functionality"""
    
    def test_environment_enum(self):
        """Test Environment enum values"""
        self.assertEqual(Environment.DEVELOPMENT.value, "development")
        self.assertEqual(Environment.STAGING.value, "staging")
        self.assertEqual(Environment.PRODUCTION.value, "production")
        self.assertEqual(Environment.TESTING.value, "testing")
    
    def test_settings_default_values(self):
        """Test default values for Settings"""
        settings = Settings()
        self.assertEqual(settings.API_HOST, "localhost")
        self.assertEqual(settings.API_PORT, 8000)
        self.assertEqual(settings.API_PREFIX, "/api")
    
    def test_environment_specific_settings(self):
        """Test environment-specific settings loading"""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            env_dir = temp_path / "environments"
            env_dir.mkdir()
            
            # Create test environment file
            test_env = {
                "API_HOST": "test-server",
                "API_PORT": 9000,
                "LOG_LEVEL": "DEBUG"
            }
            
            with open(env_dir / "testing.json", "w") as f:
                json.dump(test_env, f)
            
            # Patch the environment file path
            original_path = Path
            
            try:
                # Mock the path to return our temp directory
                def mock_environment_path(*args, **kwargs):
                    if args and "environments" in str(args[0]):
                        return env_dir
                    return original_path(*args, **kwargs)
                
                Path = mock_environment_path  # type: ignore
                
                # Load environment settings
                env_settings = load_environment_settings(Environment.TESTING)
                
                # Verify settings were loaded
                self.assertEqual(env_settings["API_HOST"], "test-server")
                self.assertEqual(env_settings["API_PORT"], 9000)
                self.assertEqual(env_settings["LOG_LEVEL"], "DEBUG")
            
            finally:
                # Restore original Path
                Path = original_path  # type: ignore
    
    def test_get_api_url(self):
        """Test URL generation methods"""
        # Development environment
        settings = Settings(APP_ENV=Environment.DEVELOPMENT, API_HOST="dev-api", API_PORT=8000)
        self.assertEqual(settings.get_api_url(), "http://dev-api:8000/api")
        
        # Production environment
        settings = Settings(APP_ENV=Environment.PRODUCTION, API_HOST="prod-api", API_PORT=443)
        self.assertEqual(settings.get_api_url(), "https://prod-api:443/api")
    
    def test_get_ws_url(self):
        """Test WebSocket URL generation methods"""
        # Development environment
        settings = Settings(APP_ENV=Environment.DEVELOPMENT, WS_HOST="dev-ws", WS_PORT=8001)
        self.assertEqual(settings.get_ws_url(), "ws://dev-ws:8001/ws")
        
        # Production environment
        settings = Settings(APP_ENV=Environment.PRODUCTION, WS_HOST="prod-ws", WS_PORT=443)
        self.assertEqual(settings.get_ws_url(), "wss://prod-ws:443/ws")


class TestConfigService(unittest.TestCase):
    """Test the ConfigService functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create environment and region directories
        self.env_dir = self.temp_path / "environments"
        self.region_dir = self.temp_path / "regions"
        self.env_dir.mkdir()
        self.region_dir.mkdir()
        
        # Create test environment files
        self.testing_env = {
            "API_HOST": "test-server",
            "API_PORT": 9000,
            "LOG_LEVEL": "DEBUG"
        }
        
        with open(self.env_dir / "testing.json", "w") as f:
            json.dump(self.testing_env, f)
        
        # Create test region files
        self.test_region = {
            "region_name": "Test Region",
            "agriculture_data": {
                "major_crops": ["Test Crop 1", "Test Crop 2"],
                "irrigation_systems": ["Test System"]
            }
        }
        
        with open(self.region_dir / "test_region.json", "w") as f:
            json.dump(self.test_region, f)
        
        # Set environment variable
        os.environ["REGION"] = "test_region"
        
        # Store original paths
        self.original_config_service = ConfigService._instance
        ConfigService._instance = None
    
    def tearDown(self):
        """Clean up after tests"""
        # Clean up temp directory
        self.temp_dir.cleanup()
        
        # Restore original instance
        ConfigService._instance = self.original_config_service
    
    def test_singleton_pattern(self):
        """Test that ConfigService is a singleton"""
        config1 = ConfigService()
        config2 = ConfigService()
        self.assertIs(config1, config2)
    
    def test_get_config(self):
        """Test get_config function"""
        config1 = get_config()
        config2 = get_config()
        self.assertIs(config1, config2)
    
    def test_get_region_data(self):
        """Test accessing region-specific data"""
        # Create a ConfigService with mocked paths
        config = ConfigService()
        
        # Manually set the region config for testing
        config._region_config = self.test_region
        
        # Test accessing region data
        self.assertEqual(config.get_region_name(), "test_region")
        self.assertEqual(
            config.get_region_data("agriculture_data.major_crops"),
            ["Test Crop 1", "Test Crop 2"]
        )
        self.assertEqual(
            config.get_region_data("agriculture_data.irrigation_systems"),
            ["Test System"]
        )
        
        # Test default value for non-existent path
        self.assertEqual(
            config.get_region_data("non_existent_path", "default"),
            "default"
        )
    
    def test_environment_methods(self):
        """Test environment check methods"""
        config = ConfigService()
        
        # Set environment for testing
        config._settings._env_settings = {"APP_ENV": "development"}
        self.assertTrue(config.is_development_mode())
        self.assertFalse(config.is_production_mode())
        
        # Change environment
        config._settings._env_settings = {"APP_ENV": "production"}
        self.assertFalse(config.is_development_mode())
        self.assertTrue(config.is_production_mode())


if __name__ == "__main__":
    unittest.main()
