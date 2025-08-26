"""
Test Irrigation Model Integration

This test validates the integration of the AgriSens Irrigation Scheduling ML model 
with the Irrigation Agent, ensuring that it correctly generates irrigation schedules,
water requirement calculations, and method recommendations.
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

from src.agents.irrigation_agent import IrrigationAgent
from src.models.agrisens_irrigation_scheduling import IrrigationModel
from src.core.agriculture_models import (
    AgricultureQuery, CropType, SoilType, Location, WeatherData
)


class TestIrrigationModelIntegration(unittest.TestCase):
    """Test the integration of AgriSens irrigation model with the Irrigation Agent"""

    def setUp(self):
        """Set up test environment"""
        self.agent = IrrigationAgent()
        
        # Sample query with necessary data for irrigation scheduling
        self.sample_query = AgricultureQuery(
            query_id="test-irrigation-integration-01",
            query_text="I need an irrigation schedule for my wheat crop in sandy loam soil. The field size is 2 hectares.",
            query_domain="irrigation_scheduling",
            crop_type=CropType.WHEAT,
            soil_type=SoilType.SANDY_LOAM,
            location=Location(
                latitude=28.6139,
                longitude=77.2090,
                state="Uttar Pradesh",
                district="Mathura"
            ),
            weather=WeatherData(
                temperature=32,
                humidity=65,
                rainfall=5,
                forecast=[
                    {"date": "2025-08-26", "temperature": 33, "humidity": 62, "precipitation": 0},
                    {"date": "2025-08-27", "temperature": 32, "humidity": 65, "precipitation": 10},
                    {"date": "2025-08-28", "temperature": 31, "humidity": 70, "precipitation": 15},
                    {"date": "2025-08-29", "temperature": 30, "humidity": 65, "precipitation": 0},
                    {"date": "2025-08-30", "temperature": 31, "humidity": 60, "precipitation": 0}
                ]
            )
        )
        
        # Mock satellite data
        self.mock_satellite_data = {
            "soil_moisture": {
                "values": [45, 43, 48, 46],
                "date": "2025-08-25"
            },
            "ndvi": {
                "values": [0.65, 0.68, 0.62, 0.64],
                "date": "2025-08-25"
            },
            "land_surface_temperature": {
                "values": [32, 31, 33, 32.5],
                "date": "2025-08-25"
            },
            "metrics": {
                "confidence_score": 0.8,
                "update_frequency": "daily"
            }
        }
        
    @patch('src.agents.satellite_integration.get_satellite_data_for_location')
    @patch('src.models.agrisens_irrigation_scheduling.get_irrigation_model')
    async def test_irrigation_schedule_generation_with_model(self, mock_get_model, mock_get_satellite):
        """Test that irrigation schedules are correctly generated with ML model integration"""
        # Set up mocks
        mock_model = MagicMock(spec=IrrigationModel)
        mock_get_model.return_value = mock_model
        mock_get_satellite.return_value = self.mock_satellite_data
        
        # Mock model output
        mock_model.generate_satellite_enhanced_irrigation_plan.return_value = {
            "crop": "wheat",
            "soil": "sandy_loam",
            "growth_stage": "mid_season",
            "root_depth_m": 0.5,
            "total_available_water_mm": 150.0,
            "readily_available_water_mm": 105.0,
            "initial_depletion_mm": 52.5,
            "irrigation_method": "sprinkler",
            "field_size_ha": 2.0,
            "schedule": [
                {
                    "date": "2025-08-26",
                    "etc_mm": 5.2,
                    "rainfall_mm": 0,
                    "depletion_mm": 57.7,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-08-27",
                    "etc_mm": 5.2,
                    "rainfall_mm": 10,
                    "depletion_mm": 52.9,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-08-28",
                    "etc_mm": 5.2,
                    "rainfall_mm": 15,
                    "depletion_mm": 43.1,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-08-29",
                    "etc_mm": 5.2,
                    "rainfall_mm": 0,
                    "depletion_mm": 48.3,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-08-30",
                    "etc_mm": 5.2,
                    "rainfall_mm": 0,
                    "depletion_mm": 53.5,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-08-31",
                    "etc_mm": 5.2,
                    "rainfall_mm": 0,
                    "depletion_mm": 58.7,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-09-01",
                    "etc_mm": 5.2,
                    "rainfall_mm": 0,
                    "depletion_mm": 63.9,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                },
                {
                    "date": "2025-09-02",
                    "etc_mm": 5.2,
                    "rainfall_mm": 0,
                    "depletion_mm": 105.0,
                    "irrigate": True,
                    "irrigation_mm": 105.0,
                    "water_volume_m3": 280.0
                }
            ],
            "satellite_insights": {
                "soil_moisture": {
                    "moisture_level": "adequate",
                    "moisture_percent": 45.5,
                    "field_capacity_percent": 56.88,
                    "temporal_variation": 1.8
                },
                "water_stress": {
                    "water_stress_index": 0.28,
                    "stress_level": "low",
                    "contributing_factors": {
                        "ndvi": 0.65,
                        "temperature": 32.1
                    },
                    "confidence": "medium"
                }
            },
            "water_savings_potential": 25.0,
            "recommendations": [
                "Consider applying water during early morning or evening to minimize evaporation losses",
                "Based on satellite data, soil moisture is adequate for the next 3-4 days"
            ]
        }
        
        # Process query
        response = await self.agent.process_query(self.sample_query)
        
        # Verify that the model was called with correct parameters
        mock_model.generate_satellite_enhanced_irrigation_plan.assert_called_once()
        args = mock_model.generate_satellite_enhanced_irrigation_plan.call_args[1]
        
        self.assertEqual(args["crop_data"]["crop_type"], "wheat")
        self.assertEqual(args["soil_data"]["soil_type"], "sandy_loam")
        
        # Verify model data integration in the response
        self.assertIn("agrisens_model_output", response.metadata)
        self.assertIn("agrisens_irrigation_ml_model", response.sources)
        
        # Verify enhanced confidence score
        self.assertGreater(response.confidence_score, 0.7)
        
        # Verify irrigation schedule uses model data
        for recommendation in response.recommendations:
            if "irrigation schedule" in recommendation.lower():
                self.assertTrue(any("model" in line.lower() for line in response.metadata.get("efficiency_tips", [])))
                
    @patch('src.agents.satellite_integration.get_satellite_data_for_location')
    @patch('src.models.agrisens_irrigation_scheduling.get_irrigation_model')
    async def test_water_requirement_calculation_with_model(self, mock_get_model, mock_get_satellite):
        """Test that water requirements are correctly calculated using ML model"""
        # Set up mocks
        mock_model = MagicMock(spec=IrrigationModel)
        mock_get_model.return_value = mock_model
        mock_get_satellite.return_value = self.mock_satellite_data
        
        # Mock model output with first day water requirement
        mock_model.generate_satellite_enhanced_irrigation_plan.return_value = {
            "schedule": [
                {
                    "date": "2025-08-26",
                    "etc_mm": 4.8,
                    "rainfall_mm": 0,
                    "depletion_mm": 57.7,
                    "irrigate": False,
                    "irrigation_mm": 0,
                    "water_volume_m3": 0
                }
            ],
            "satellite_insights": {
                "soil_moisture": {
                    "moisture_level": "adequate",
                    "moisture_percent": 45.5
                }
            }
        }
        
        # Process query
        response = await self.agent.process_query(self.sample_query)
        
        # Verify water requirements in response
        self.assertTrue(len(response.metadata["water_requirements"]) > 0)
        water_req = response.metadata["water_requirements"][0]
        
        # Check model data was used
        self.assertAlmostEqual(water_req["etc_mm"], 4.8, delta=0.1)
        
        # Verify model was called
        mock_model.generate_satellite_enhanced_irrigation_plan.assert_called_once()
        
    @patch('src.agents.satellite_integration.get_satellite_data_for_location')
    @patch('src.models.agrisens_irrigation_scheduling.get_irrigation_model')
    async def test_irrigation_method_recommendation_with_model(self, mock_get_model, mock_get_satellite):
        """Test irrigation method recommendations are correctly enhanced using ML model"""
        # Set up mocks
        mock_model = MagicMock(spec=IrrigationModel)
        mock_get_model.return_value = mock_model
        mock_get_satellite.return_value = self.mock_satellite_data
        
        # Mock model output with irrigation method recommendation
        mock_model.generate_satellite_enhanced_irrigation_plan.return_value = {
            "irrigation_method": "sprinkler",
            "water_savings_potential": 25.0,
            "recommendations": [
                "Consider upgrading to a more efficient irrigation system like drip or micro-sprinkler to reduce water usage and increase efficiency."
            ],
            "schedule": [{}],  # Minimal schedule to avoid errors
            "satellite_insights": {
                "soil_moisture": {
                    "moisture_level": "adequate",
                    "moisture_percent": 45.5
                }
            }
        }
        
        # Process query
        response = await self.agent.process_query(self.sample_query)
        
        # Verify method recommendation in response
        method_rec = response.metadata["method_recommendation"]
        self.assertIn("model_recommendation", method_rec)
        self.assertEqual(method_rec["current_method"], "sprinkler")
        self.assertIn("water_savings_potential", method_rec)
        
        # Check efficiency tips include model recommendations
        efficiency_tips = response.metadata["efficiency_tips"]
        self.assertTrue(any("[AgriSens Model]" in tip for tip in efficiency_tips))
        
        # Verify model was called
        mock_model.generate_satellite_enhanced_irrigation_plan.assert_called_once()


if __name__ == '__main__':
    unittest.main()
