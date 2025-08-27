#!/usr/bin/env python3
"""
Current test for the unified agricultural API system.
This replaces all the old scattered test files.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

class TestUnifiedAgriculturalAPI:
    """Test suite for the unified agricultural API."""
    
    def test_health_check(self):
        """Test API health check endpoint."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_marketplace_endpoints(self):
        """Test marketplace functionality."""
        # Test get products
        response = requests.get(f"{BASE_URL}/marketplace/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
    
    def test_farmer_profile_endpoints(self):
        """Test farmer profile functionality."""
        # Test farmer leaderboard
        response = requests.get(f"{BASE_URL}/farmer-leaderboard")
        assert response.status_code == 200
        leaderboard = response.json()
        assert isinstance(leaderboard, list)

if __name__ == "__main__":
    print("Running unified API tests...")
    test_instance = TestUnifiedAgriculturalAPI()
    test_instance.test_health_check()
    test_instance.test_marketplace_endpoints()
    test_instance.test_farmer_profile_endpoints()
    print("All tests passed!")
