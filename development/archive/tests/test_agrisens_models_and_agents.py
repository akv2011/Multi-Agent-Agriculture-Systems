"""
Test AgriSens Models and Agents Functionality

This script tests the following AgriSens components:
1. Disease Prediction Agent
2. Crop Recommendation Agent
3. Weather Forecast Functionality
4. Irrigation Model Integration
5. Market Timing Model Integration

It validates that each component is correctly initialized, processes queries,
and returns meaningful results using the setup data and models.
"""

import sys
import os
import unittest
import asyncio
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.disease_identification_agent import DiseaseIdentificationAgent
from src.agents.crop_selection_agent import CropSelectionAgent
from src.agents.weather_forecast_agent import WeatherForecastAgent
from src.agents.irrigation_agent import IrrigationAgent
from src.agents.market_timing_agent import MarketTimingAgent

from src.core.agriculture_models import (
    AgricultureQuery, CropType, SoilType, Location, WeatherData, AgentResponse
)


class TestAgriSensModelsAndAgents(unittest.TestCase):
    """Test functionality of the main AgriSens models and agents"""

    def setUp(self):
        """Set up test environment with agent instances and sample queries"""
        # Initialize agents
        self.disease_agent = DiseaseIdentificationAgent("disease-test-agent", "Disease Test Agent")
        self.crop_agent = CropSelectionAgent("crop-test-agent", "Crop Test Agent")
        self.weather_agent = WeatherForecastAgent("weather-test-agent", "Weather Test Agent")
        self.irrigation_agent = IrrigationAgent("irrigation-test-agent", "Irrigation Test Agent")
        self.market_agent = MarketTimingAgent("market-test-agent", "Market Test Agent")
        
        # Sample location for queries
        self.test_location = Location(
            latitude=28.6139,  # New Delhi
            longitude=77.2090,
            country="India",
            state="Delhi",
            district="New Delhi"
        )
        
        # Prepare sample queries for each agent
        self.disease_query = AgricultureQuery(
            query_id="test-disease-01",
            query_text="My tomato plants have yellow spots on leaves and are wilting.",
            query_domain="disease_identification",
            location=self.test_location,
            crop_type=CropType.TOMATO
        )
        
        self.crop_query = AgricultureQuery(
            query_id="test-crop-01",
            query_text="What crops should I plant in my farm?",
            query_domain="crop_selection",
            location=self.test_location,
            soil_type=SoilType.CLAY_LOAM
        )
        
        self.weather_query = AgricultureQuery(
            query_id="test-weather-01",
            query_text="What's the weather forecast for my location?",
            query_domain="weather_forecast",
            location=self.test_location
        )
        
        self.irrigation_query = AgricultureQuery(
            query_id="test-irrigation-01",
            query_text="How should I irrigate my wheat crop?",
            query_domain="irrigation_scheduling",
            location=self.test_location,
            crop_type=CropType.WHEAT,
            soil_type=SoilType.SANDY_LOAM
        )
        
        self.market_query = AgricultureQuery(
            query_id="test-market-01",
            query_text="When is the best time to sell rice?",
            query_domain="market_timing",
            location=self.test_location,
            crop_type=CropType.RICE
        )

    async def run_agent_query(self, agent, query):
        """Helper method to run a query against an agent and validate response"""
        try:
            response = await agent.process_query(query)
            self.assertIsInstance(response, AgentResponse)
            self.assertIsNotNone(response.message)
            return response
        except Exception as e:
            self.fail(f"Agent query failed with error: {str(e)}")
            return None

    @patch('src.models.agrisens_disease_identification.identify_disease_from_text')
    async def test_disease_prediction_agent(self, mock_identify):
        """Test disease prediction agent with text-based identification"""
        print("\n===== Testing Disease Prediction Agent =====")
        
        # Mock the disease identification result
        mock_identify.return_value = {
            "disease": "Late Blight",
            "confidence": 0.92,
            "crop": "Tomato",
            "treatment": "Apply copper-based fungicide..."
        }
        
        response = await self.run_agent_query(self.disease_agent, self.disease_query)
        print(f"Disease prediction result: {response.message}")
        print(f"Data: {response.data}")
        
        self.assertTrue(response.success)
        self.assertIn("Blight", str(response.data))
    
    @patch('src.models.agrisens_crop_recommendation.AgriSensCropModel.get_model')
    async def test_crop_recommendation_agent(self, mock_get_model):
        """Test crop recommendation agent"""
        print("\n===== Testing Crop Recommendation Agent =====")
        
        # Mock the crop recommendation model
        mock_model = MagicMock()
        mock_model.predict.return_value = [
            {"crop": "rice", "probability": 0.95},
            {"crop": "maize", "probability": 0.85},
            {"crop": "cotton", "probability": 0.78}
        ]
        mock_get_model.return_value = mock_model
        
        response = await self.run_agent_query(self.crop_agent, self.crop_query)
        print(f"Crop recommendation result: {response.message}")
        print(f"Data: {response.data}")
        
        self.assertTrue(response.success)
    
    @patch('src.agents.weather_forecast_agent.WeatherForecastAgent._get_weather_forecast')
    async def test_weather_forecast_agent(self, mock_get_forecast):
        """Test weather forecast functionality"""
        print("\n===== Testing Weather Forecast Agent =====")
        
        # Mock weather forecast data
        mock_forecast_data = {
            "current": {
                "temperature": 28,
                "humidity": 65,
                "conditions": "Partly Cloudy"
            },
            "daily": [
                {
                    "date": (datetime.now()).strftime("%Y-%m-%d"),
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
        mock_get_forecast.return_value = mock_forecast_data
        
        response = await self.run_agent_query(self.weather_agent, self.weather_query)
        print(f"Weather forecast result: {response.message}")
        print(f"Data: {response.data}")
        
        self.assertTrue(response.success)
        self.assertIn("temperature", str(response.data))
    
    @patch('src.models.agrisens_irrigation_scheduling.IrrigationModel.get_model')
    async def test_irrigation_model(self, mock_get_model):
        """Test irrigation model integration"""
        print("\n===== Testing Irrigation Model Integration =====")
        
        # Mock the irrigation model
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
        
        response = await self.run_agent_query(self.irrigation_agent, self.irrigation_query)
        print(f"Irrigation model result: {response.message}")
        print(f"Data: {response.data}")
        
        self.assertTrue(response.success)
        self.assertIn("water", str(response.data).lower())
    
    @patch('src.models.agrisens_market_timing.MarketTimingModel.get_model')
    async def test_market_timing_model(self, mock_get_model):
        """Test market timing model integration"""
        print("\n===== Testing Market Timing Model Integration =====")
        
        # Mock the market timing model
        mock_model = MagicMock()
        mock_model.predict_prices.return_value = {
            "current_price": 1850,
            "forecast": [
                {"month": "Sep", "price": 1950, "trend": "up"},
                {"month": "Oct", "price": 2100, "trend": "up"},
                {"month": "Nov", "price": 2050, "trend": "down"}
            ],
            "optimal_selling_period": "October",
            "confidence": 0.85,
            "factors": ["Monsoon season ending", "Festival demand"]
        }
        mock_get_model.return_value = mock_model
        
        response = await self.run_agent_query(self.market_agent, self.market_query)
        print(f"Market timing model result: {response.message}")
        print(f"Data: {response.data}")
        
        self.assertTrue(response.success)
        self.assertIn("price", str(response.data).lower())


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAgriSensModelsAndAgents)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    # Run tests asynchronously
    asyncio.run(unittest.main())
