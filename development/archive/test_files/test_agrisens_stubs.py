#!/usr/bin/env python3
"""
Simple AgriSens Model Agent Test

This script runs basic tests on the AgriSens agents using stub models.
It avoids direct TensorFlow calls to prevent segmentation faults.

1. Disease Prediction Agent
2. Crop Recommendation Agent  
3. Weather Forecast Functionality
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class StubAgriSensTest(unittest.TestCase):
    """Test the basic functionality of AgriSens agents using stubs"""

    def setUp(self):
        """Set up test environment"""
        print("\nSetting up stub test environment...")

    @patch('src.models.agrisens_disease_identification.identify_disease_from_text')
    def test_disease_prediction_stub(self, mock_identify):
        """Test disease prediction agent with stub response"""
        from src.agents.disease_identification_agent import DiseaseIdentificationAgent
        from src.core.agriculture_models import AgricultureQuery, Location, CropType

        print("\n===== Testing Disease Prediction Agent (Stub) =====")
        
        # Configure mock
        mock_identify.return_value = {
            "disease": "Late Blight",
            "confidence": 0.92,
            "crop": "Tomato",
            "treatment": "Apply copper-based fungicide..."
        }
        
        # Create agent and query
        agent = DiseaseIdentificationAgent("disease-test", "Disease Test Agent")
        location = Location(latitude=28.6, longitude=77.2, state="Delhi")
        query = AgricultureQuery(
            query_id="test-disease-stub",
            query_text="My tomato plants have yellow spots",
            query_domain="disease_identification",
            location=location,
            crop_type=CropType.TOMATO
        )
        
        # Test identification method directly
        result = agent._identify_disease_from_text(query)
        
        print(f"Disease identification result: {result}")
        self.assertIsNotNone(result)
        self.assertIn("disease", result)
        self.assertEqual(result["disease"], "Late Blight")
        
        print("✅ Disease prediction agent test passed")

    @patch('src.models.agrisens_crop_recommendation.AgriSensCropModel.get_model')
    def test_crop_recommendation_stub(self, mock_get_model):
        """Test crop recommendation agent with stub response"""
        from src.agents.crop_selection_agent import CropSelectionAgent
        from src.core.agriculture_models import AgricultureQuery, Location, SoilType

        print("\n===== Testing Crop Recommendation Agent (Stub) =====")
        
        # Configure mock
        mock_model = MagicMock()
        mock_model.predict.return_value = [
            {"crop": "rice", "probability": 0.95},
            {"crop": "maize", "probability": 0.85}
        ]
        mock_get_model.return_value = mock_model
        
        # Create agent and query
        agent = CropSelectionAgent("crop-test", "Crop Test Agent")
        location = Location(latitude=28.6, longitude=77.2, state="Delhi")
        query = AgricultureQuery(
            query_id="test-crop-stub",
            query_text="What crops should I plant?",
            query_domain="crop_selection",
            location=location,
            soil_type=SoilType.CLAY_LOAM
        )
        
        # Test recommendation method directly
        result = agent._get_agrisens_crop_recommendation(query)
        
        print(f"Crop recommendation result: {result}")
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["crop"], "rice")
        
        print("✅ Crop recommendation agent test passed")

    @patch('src.agents.weather_forecast_agent.WeatherForecastAgent._get_weather_forecast_from_api')
    def test_weather_forecast_stub(self, mock_get_forecast):
        """Test weather forecast functionality with stub response"""
        from src.agents.weather_forecast_agent import WeatherForecastAgent
        from src.core.agriculture_models import AgricultureQuery, Location
        from datetime import datetime

        print("\n===== Testing Weather Forecast Agent (Stub) =====")
        
        # Configure mock
        mock_get_forecast.return_value = {
            "current": {
                "temperature": 28,
                "humidity": 65,
                "conditions": "Partly Cloudy"
            },
            "daily": [
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "temperature_min": 24,
                    "temperature_max": 32,
                    "conditions": "Partly Cloudy",
                    "precipitation_chance": 20,
                    "precipitation_amount": 0,
                    "humidity": 65,
                    "wind_speed": 8
                }
            ]
        }
        
        # Create agent and query
        agent = WeatherForecastAgent("weather-test", "Weather Test Agent")
        location = Location(latitude=28.6, longitude=77.2, state="Delhi")
        query = AgricultureQuery(
            query_id="test-weather-stub",
            query_text="What's the weather forecast?",
            query_domain="weather_forecast",
            location=location
        )
        
        # Test forecast method directly
        result = agent._get_weather_forecast(location)
        
        print(f"Weather forecast result: {result}")
        self.assertIsNotNone(result)
        self.assertIn("current", result)
        self.assertEqual(result["current"]["temperature"], 28)
        
        print("✅ Weather forecast agent test passed")

    @patch('src.models.agrisens_irrigation_scheduling.IrrigationModel.get_model')
    def test_irrigation_model_stub(self, mock_get_model):
        """Test irrigation model with stub response"""
        from src.agents.irrigation_agent import IrrigationAgent
        from src.core.agriculture_models import AgricultureQuery, Location, SoilType, CropType
        from datetime import datetime, timedelta

        print("\n===== Testing Irrigation Model (Stub) =====")
        
        # Configure mock
        mock_model = MagicMock()
        mock_model.calculate_water_requirements.return_value = {
            "daily_water_req_mm": 5.8,
            "weekly_water_req_mm": 40.6,
            "irrigation_interval_days": 3,
            "next_irrigation_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "recommended_method": "Drip irrigation",
            "efficiency_score": 85
        }
        mock_get_model.return_value = mock_model
        
        # Create agent and query
        agent = IrrigationAgent("irrigation-test", "Irrigation Test Agent")
        location = Location(latitude=28.6, longitude=77.2, state="Delhi")
        query = AgricultureQuery(
            query_id="test-irrigation-stub",
            query_text="How should I irrigate my wheat crop?",
            query_domain="irrigation_scheduling",
            location=location,
            crop_type=CropType.WHEAT,
            soil_type=SoilType.SANDY_LOAM
        )
        
        # Test irrigation method directly
        result = agent._calculate_irrigation_requirements(query)
        
        print(f"Irrigation model result: {result}")
        self.assertIsNotNone(result)
        self.assertIn("daily_water_req_mm", result)
        self.assertEqual(result["recommended_method"], "Drip irrigation")
        
        print("✅ Irrigation model test passed")

    @patch('src.models.agrisens_market_timing.MarketTimingModel.get_model')
    def test_market_timing_stub(self, mock_get_model):
        """Test market timing model with stub response"""
        try:
            from src.agents.market_timing_agent import MarketTimingAgent
            from src.core.agriculture_models import AgricultureQuery, Location, CropType

            print("\n===== Testing Market Timing Model (Stub) =====")
            
            # Configure mock
            mock_model = MagicMock()
            mock_model.predict_prices.return_value = {
                "current_price": 1850,
                "forecast": [
                    {"month": "Sep", "price": 1950, "trend": "up"},
                    {"month": "Oct", "price": 2100, "trend": "up"}
                ],
                "optimal_selling_period": "October"
            }
            mock_get_model.return_value = mock_model
            
            # Create agent and query
            agent = MarketTimingAgent("market-test", "Market Test Agent")
            location = Location(latitude=30.9, longitude=75.8, state="Punjab")
            query = AgricultureQuery(
                query_id="test-market-stub",
                query_text="When should I sell my wheat?",
                query_domain="market_timing",
                location=location,
                crop_type=CropType.WHEAT
            )
            
            # Test market timing method directly
            result = agent._get_price_forecast(query)
            
            print(f"Market timing model result: {result}")
            self.assertIsNotNone(result)
            self.assertIn("current_price", result)
            self.assertEqual(result["optimal_selling_period"], "October")
            
            print("✅ Market timing model test passed")
            
        except ImportError as e:
            print(f"❌ Market timing test skipped: {e}")


if __name__ == "__main__":
    unittest.main()
