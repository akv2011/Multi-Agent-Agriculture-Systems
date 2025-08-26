"""
Test Market Timing Model Integration

This test validates the integration of the AgriSens Market Timing ML model 
with the Market Timing Agent, ensuring that it correctly generates price forecasts,
market recommendations, and optimal selling strategies.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import asyncio
from datetime import datetime, timedelta
import json

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.market_timing_agent import MarketTimingAgent, Commodity
from src.models.agrisens_market_timing import MarketTimingModel
from src.core.agriculture_models import (
    AgricultureQuery, CropType, Location, WeatherData
)


class TestMarketTimingModelIntegration(unittest.TestCase):
    """Test the integration of AgriSens market timing model with the Market Timing Agent"""

    def setUp(self):
        """Set up test environment"""
        self.agent = MarketTimingAgent()
        
        # Sample query with necessary data for market timing analysis
        self.sample_query = AgricultureQuery(
            query_id="test-market-integration-01",
            query_text="When should I sell my wheat crop for the best price?",
            query_domain="market_timing",
            crop_type=CropType.WHEAT,
            location=Location(
                latitude=28.6139,
                longitude=77.2090,
                state="Punjab",
                district="Ludhiana"
            ),
            weather=WeatherData(
                temperature=30,
                humidity=65,
                rainfall=0,
                forecast=[
                    {"date": "2025-08-26", "temperature": 31, "humidity": 62, "precipitation": 0},
                    {"date": "2025-08-27", "temperature": 30, "humidity": 65, "precipitation": 0},
                    {"date": "2025-08-28", "temperature": 29, "humidity": 70, "precipitation": 5},
                    {"date": "2025-08-29", "temperature": 30, "humidity": 65, "precipitation": 0},
                    {"date": "2025-08-30", "temperature": 31, "humidity": 60, "precipitation": 0}
                ]
            )
        )
        
        # Mock satellite data
        self.mock_satellite_data = {
            "soil_moisture": {
                "values": [35, 33, 38, 36],
                "date": "2025-08-25"
            },
            "ndvi": {
                "values": [0.72, 0.75, 0.70, 0.73],
                "date": "2025-08-25"
            },
            "metrics": {
                "confidence_score": 0.8,
                "update_frequency": "daily"
            }
        }
        
    @patch('src.services.satellite_service.SatelliteService.get_current_data')
    @patch('src.models.agrisens_market_timing.get_market_timing_model')
    async def test_price_forecast_with_model(self, mock_get_model, mock_get_satellite):
        """Test that price forecasts are correctly generated with ML model integration"""
        # Set up mocks
        mock_model = MagicMock(spec=MarketTimingModel)
        mock_get_model.return_value = mock_model
        mock_get_satellite.return_value = self.mock_satellite_data
        
        # Mock current date
        current_date = datetime.now()
        
        # Mock model output
        mock_model.generate_satellite_enhanced_market_timing.return_value = {
            "price_forecast": {
                "crop": "wheat",
                "current_price": 2200,
                "forecasts": [
                    {
                        "month": current_date.strftime("%Y-%m"),
                        "expected_price": 2200,
                        "lower_bound": 2100,
                        "upper_bound": 2300,
                        "confidence": "medium"
                    },
                    {
                        "month": (current_date + timedelta(days=30)).strftime("%Y-%m"),
                        "expected_price": 2250,
                        "lower_bound": 2130,
                        "upper_bound": 2370,
                        "confidence": "medium"
                    },
                    {
                        "month": (current_date + timedelta(days=60)).strftime("%Y-%m"),
                        "expected_price": 2350,
                        "lower_bound": 2180,
                        "upper_bound": 2520,
                        "confidence": "medium"
                    }
                ],
                "price_trend": "increasing"
            },
            "supply_demand_analysis": {
                "crop": "wheat",
                "region": "Punjab",
                "supply_demand_balance": -0.3,
                "market_outlook": "bullish",
                "market_signals": ["Regional supply shortage possible"]
            },
            "selling_strategy": {
                "crop": "wheat",
                "current_price": 2200,
                "optimal_selling_month": (current_date + timedelta(days=60)).strftime("%Y-%m"),
                "expected_optimal_price": 2350,
                "recommendation": "hold_for_future_sale"
            },
            "satellite_yield_assessment": {
                "yield_estimate": "above_average",
                "yield_deviation": "15.0%",
                "confidence": "medium",
                "market_impact": "bearish",
                "ndvi_average": 0.73
            },
            "recommendations": [
                "Consider holding your produce until October 2025 when prices are expected to reach ₹2350 per quintal, if storage facilities are available.",
                "Regional supply indicators suggest potential shortages which may drive prices higher in the coming weeks. Consider a staged selling approach to benefit from potential price increases."
            ]
        }
        
        # Process query
        response = await self.agent.process_query(self.sample_query)
        
        # Verify that the model was called with correct parameters
        mock_model.generate_satellite_enhanced_market_timing.assert_called_once()
        args = mock_model.generate_satellite_enhanced_market_timing.call_args[1]
        
        self.assertEqual(args["crop_type"], "wheat")
        self.assertEqual(args["location_data"]["region"], "Punjab")
        
        # Check for model data integration in response
        self.assertEqual(response.agent_name, "Market Timing Agent")
        self.assertIn("hold", response.response_text.lower()) 
        
        # Verify model recommendations in response
        self.assertTrue(any("[AgriSens Model]" in rec for rec in response.recommendations))
        
    @patch('src.services.satellite_service.SatelliteService.get_current_data')
    @patch('src.models.agrisens_market_timing.get_market_timing_model')
    async def test_selling_recommendation_with_model(self, mock_get_model, mock_get_satellite):
        """Test that selling recommendations are correctly generated with ML model integration"""
        # Set up mocks
        mock_model = MagicMock(spec=MarketTimingModel)
        mock_get_model.return_value = mock_model
        mock_get_satellite.return_value = self.mock_satellite_data
        
        # Mock model output recommending immediate sale
        mock_model.generate_satellite_enhanced_market_timing.return_value = {
            "price_forecast": {
                "crop": "wheat",
                "current_price": 2200,
                "forecasts": [
                    {
                        "month": datetime.now().strftime("%Y-%m"),
                        "expected_price": 2200
                    },
                    {
                        "month": (datetime.now() + timedelta(days=30)).strftime("%Y-%m"),
                        "expected_price": 2150
                    }
                ],
                "price_trend": "decreasing"
            },
            "supply_demand_analysis": {
                "crop": "wheat",
                "region": "Punjab",
                "market_outlook": "bearish"
            },
            "selling_strategy": {
                "crop": "wheat",
                "current_price": 2200,
                "recommendation": "sell_immediately"
            },
            "satellite_yield_assessment": {
                "yield_estimate": "excellent",
                "yield_deviation": "30.0%",
                "market_impact": "strongly_bearish"
            },
            "recommendations": [
                "Current market conditions are favorable for selling. Consider selling your produce now to maximize returns.",
                "Regional supply indicators suggest possible oversupply which may put downward pressure on prices. If you need to sell, consider doing so sooner rather than later."
            ]
        }
        
        # Process query
        response = await self.agent.process_query(self.sample_query)
        
        # Verify model recommendations in response
        self.assertTrue(any("sell" in rec.lower() for rec in response.recommendations))
        self.assertIn("sell", response.response_text.lower())
        
        # Verify model was called with correct crop type
        mock_model.generate_satellite_enhanced_market_timing.assert_called_once()
        args = mock_model.generate_satellite_enhanced_market_timing.call_args[1]
        self.assertEqual(args["crop_type"], "wheat")
        
    @patch('src.services.satellite_service.SatelliteService.get_current_data')
    @patch('src.models.agrisens_market_timing.get_market_timing_model')
    async def test_fallback_to_basic_forecast(self, mock_get_model, mock_get_satellite):
        """Test that the agent falls back to basic forecasting if model fails"""
        # Set up mocks
        mock_model = MagicMock(spec=MarketTimingModel)
        mock_get_model.return_value = mock_model
        mock_get_satellite.return_value = self.mock_satellite_data
        
        # Simulate model failure
        mock_model.generate_satellite_enhanced_market_timing.side_effect = Exception("Model error")
        
        # Process query - should not raise exception
        response = await self.agent.process_query(self.sample_query)
        
        # Verify agent responded despite model failure
        self.assertEqual(response.agent_name, "Market Timing Agent")
        self.assertIsNotNone(response.response_text)
        
        # Check that model was called but basic forecasting was used
        mock_model.generate_satellite_enhanced_market_timing.assert_called_once()
        
        # There should be recommendations despite the model failure
        self.assertTrue(len(response.recommendations) > 0)


if __name__ == '__main__':
    unittest.main()
