"""
<<<<<<< HEAD
Test file for the AgriMitr fertilizer recommendation integration
=======
Test file for the AgriSens fertilizer recommendation integration
>>>>>>> upstream/main
"""

import unittest
import os
import sys
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.fertilizer_recommendation_agent import FertilizerRecommendationAgent
<<<<<<< HEAD
from src.models.AgriMitr_fertilizer_recommendation import (
=======
from src.models.agrisens_fertilizer_recommendation import (
>>>>>>> upstream/main
    FertilizerRecommendationModel, FertilizerRecommendationData
)
from src.core.agriculture_models import AgricultureQuery, Location, SoilType, CropType


class TestFertilizerRecommendation(unittest.TestCase):
    """Test suite for fertilizer recommendation model and agent integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.model = FertilizerRecommendationModel()
        self.model.initialize()
        self.agent = FertilizerRecommendationAgent("fertilizer-agent-1", "Fertilizer Recommendation Agent")
        self.agent.initialize()
        
    def test_model_initialization(self):
        """Test that the model initializes correctly"""
        self.assertTrue(self.model.is_initialized)
        
    def test_model_prediction(self):
        """Test fertilizer recommendation prediction"""
        # Create test data
        test_data = FertilizerRecommendationData(
            temperature=28.0,
            humidity=65.0,
            moisture=45.0,
            soil_type="Loamy",
            crop_type="Wheat",
            nitrogen=40.0,
            phosphorus=30.0,
            potassium=25.0,
            ph=6.5
        )
        
        # Get prediction
        recommendation = self.model.predict(test_data)
        
        # Verify results
        self.assertIsNotNone(recommendation)
        self.assertIsNotNone(recommendation.fertilizer_name)
        self.assertIsNotNone(recommendation.npk_ratio)
        self.assertGreater(recommendation.application_rate, 0)
        self.assertGreater(recommendation.confidence, 0)
        
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent.model)
        
    def test_soil_type_mapping(self):
        """Test soil type mapping function"""
        mappings = {
            SoilType.SANDY.value: "Sandy",
            SoilType.LOAM.value: "Loamy",
            SoilType.CLAY.value: "Clayey",
            SoilType.BLACK_SOIL.value: "Black"
        }
        
        for soil_input, expected_output in mappings.items():
            result = self.agent._map_soil_type(soil_input)
            self.assertEqual(result, expected_output)
            
    def test_crop_type_mapping(self):
        """Test crop type mapping function"""
        mappings = {
            CropType.WHEAT.value: "Wheat",
            CropType.RICE.value: "Paddy",
            CropType.MAIZE.value: "Maize"
        }
        
        for crop_input, expected_output in mappings.items():
            result = self.agent._map_crop_type(crop_input)
            self.assertEqual(result, expected_output)
    
    def test_agent_process_query(self):
        """Test agent query processing"""
        # Create test query
        query = AgricultureQuery(
            query_id="test-fertilizer-1",
            query_text="What fertilizer should I use for my wheat crop?",
            query_domain="fertilizer",
            crop_type=CropType.WHEAT.value,
            soil_type=SoilType.LOAM.value,
            soil_data={
                "nitrogen": 40.0,
                "phosphorus": 30.0,
                "potassium": 25.0,
                "ph": 6.5
            }
        )
        
        # Process query
        response = asyncio.run(self.agent.process_query(query))
        
        # Verify response
        self.assertTrue(response.success)
        self.assertEqual(response.response_type, "fertilizer_recommendation")
        self.assertIn("recommendation", response.data)
        self.assertIn("soil_analysis", response.data)
        
        # Verify recommendation data
        recommendation = response.data["recommendation"]
        self.assertIn("fertilizer_name", recommendation)
        self.assertIn("npk_ratio", recommendation)
        self.assertIn("application_rate", recommendation)
        self.assertIn("cost_estimate", recommendation)
        self.assertIn("environmental_impact", recommendation)
        
    def test_agent_handle_message(self):
        """Test agent message handling"""
        # Create test message
        message = {
            "type": "fertilizer_request",
            "soil_data": {
                "nitrogen": 40.0,
                "phosphorus": 30.0,
                "potassium": 25.0,
                "ph": 6.5,
                "soil_type": "Loamy"
            },
            "crop_type": "Wheat"
        }
        
        # Handle message
        response = asyncio.run(self.agent.handle_message(message))
        
        # Verify response
        self.assertTrue(response["success"])
        self.assertIn("fertilizer_name", response)
        self.assertIn("application_rate", response)
        self.assertIn("npk_ratio", response)


if __name__ == "__main__":
    unittest.main()
