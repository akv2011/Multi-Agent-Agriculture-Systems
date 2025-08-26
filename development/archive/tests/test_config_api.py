"""
Integration test for the configuration API endpoints.
"""

import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the main FastAPI application
from src.api.app import app
from src.config.frontend import generate_frontend_config


class TestConfigAPI(unittest.TestCase):
    """Integration tests for the configuration API"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
        # Set test environment
        os.environ["APP_ENV"] = "testing"
        os.environ["REGION"] = "maharashtra"  # Use an existing region
    
    def test_get_frontend_config(self):
        """Test the frontend configuration endpoint"""
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("apiUrl", data)
        self.assertIn("wsUrl", data)
        self.assertIn("environment", data)
        self.assertEqual(data["environment"], "testing")
    
    def test_get_regions(self):
        """Test listing available regions"""
        response = self.client.get("/api/config/regions")
        self.assertEqual(response.status_code, 200)
        
        regions = response.json()
        self.assertIsInstance(regions, list)
        # There should be at least the regions we've added
        self.assertGreaterEqual(len(regions), 3)
    
    def test_get_region_config(self):
        """Test getting a specific region configuration"""
        response = self.client.get("/api/config/regions/maharashtra")
        self.assertEqual(response.status_code, 200)
        
        region_data = response.json()
        self.assertEqual(region_data["region_name"], "Maharashtra")
        self.assertIn("agriculture_data", region_data)
        self.assertIn("major_crops", region_data["agriculture_data"])
    
    def test_set_region(self):
        """Test setting the current region"""
        # First verify current region
        initial_response = self.client.get("/api/config")
        initial_data = initial_response.json()
        
        # Try changing to a different region
        response = self.client.put("/api/config/regions/punjab")
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertEqual(result["region"], "punjab")
        
        # Verify config reflects the change
        updated_response = self.client.get("/api/config")
        updated_data = updated_response.json()
        self.assertEqual(updated_data["currentRegion"], "punjab")
    
    def test_generate_frontend_config(self):
        """Test the generate_frontend_config function"""
        config = generate_frontend_config("testing")
        
        self.assertIn("apiUrl", config)
        self.assertIn("wsUrl", config)
        self.assertEqual(config["environment"], "testing")
        self.assertIsInstance(config["regions"], list)


if __name__ == "__main__":
    unittest.main()
