"""
Test Smart Farming Guidance Agent Integration
"""

import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.smart_farming_guidance_agent import SmartFarmingGuidanceAgent
from src.core.agriculture_models import AgricultureQuery, Location, SoilType, CropType


class TestSmartFarmingGuidanceIntegration(unittest.TestCase):
    """Test integration of Smart Farming Guidance agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = SmartFarmingGuidanceAgent()
    
    def test_guidance_type_identification(self):
        """Test identification of guidance types from queries"""
        # Test crop rotation queries
        rotation_query = "What should I grow after wheat?"
        self.assertEqual(self.agent._identify_guidance_type(rotation_query), "crop_rotation")
        
        # Test water conservation queries
        water_query = "How can I reduce water usage in my rice field?"
        self.assertEqual(self.agent._identify_guidance_type(water_query), "water_conservation")
        
        # Test pest management queries
        pest_query = "What are sustainable ways to control pests in cotton?"
        self.assertEqual(self.agent._identify_guidance_type(pest_query), "sustainable_pest_management")
        
        # Test soil health queries
        soil_query = "How can I improve soil fertility naturally?"
        self.assertEqual(self.agent._identify_guidance_type(soil_query), "soil_health")
        
        # Test climate smart agriculture queries
        climate_query = "What farming practices help adapt to climate change?"
        self.assertEqual(self.agent._identify_guidance_type(climate_query), "climate_smart_agriculture")
        
        # Test general queries
        general_query = "What are the best farming practices?"
        self.assertEqual(self.agent._identify_guidance_type(general_query), "comprehensive")
    
    def test_crop_specific_guidance(self):
        """Test generation of crop-specific guidance"""
        # Test for rice
        rice_recommendations = self.agent._get_crop_specific_guidance("rice", "water_conservation")
        self.assertGreater(len(rice_recommendations), 0)
        self.assertTrue(any("AWD" in rec for rec in rice_recommendations))
        
        # Test for cotton
        cotton_recommendations = self.agent._get_crop_specific_guidance("cotton", "sustainable_pest_management")
        self.assertGreater(len(cotton_recommendations), 0)
        self.assertTrue(any("bollworm" in rec.lower() for rec in cotton_recommendations))
    
    def test_location_specific_guidance(self):
        """Test generation of location-specific guidance"""
        # Test for Punjab
        punjab_location = Location(state="Punjab", district="Ludhiana")
        punjab_recommendations = self.agent._get_location_specific_guidance(punjab_location, "water_conservation", None)
        self.assertGreater(len(punjab_recommendations), 0)
        self.assertTrue(any("groundwater" in rec.lower() for rec in punjab_recommendations))
        
        # Test for Rajasthan
        rajasthan_location = Location(state="Rajasthan", district="Jaipur")
        rajasthan_recommendations = self.agent._get_location_specific_guidance(rajasthan_location, "water_conservation", None)
        self.assertGreater(len(rajasthan_recommendations), 0)
        self.assertTrue(any("rainwater harvesting" in rec.lower() for rec in rajasthan_recommendations))
    
    @patch('src.agents.satellite_integration.get_satellite_data_for_location')
    async def test_process_query_with_location(self, mock_get_satellite):
        """Test processing a query with location information"""
        # Setup mock
        mock_get_satellite.return_value = {
            "soil_moisture": {"value": 25, "unit": "%"},
            "precipitation": {"recent_mm": 10, "forecast_mm": 5}
        }
        
        # Create query
        query = AgricultureQuery(
            query_text="How can I conserve water in my wheat field?",
            crop_type="wheat",
            soil_type=SoilType.LOAMY,
            location=Location(latitude=30.7333, longitude=76.7794, state="Punjab", district="Chandigarh")
        )
        
        # Process query
        response = await self.agent.process_query(query)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.data["guidance_type"], "water_conservation")
        self.assertGreater(len(response.data["recommendations"]), 3)
        self.assertTrue(response.data["crop_specific"])
        self.assertTrue(response.data["location_specific"])
    
    async def test_comprehensive_guidance(self):
        """Test generation of comprehensive guidance"""
        # Create query for comprehensive guidance
        query = AgricultureQuery(
            query_text="What are sustainable farming practices?",
            crop_type="cotton",
        )
        
        # Process query
        response = await self.agent.process_query(query)
        
        # Assertions
        self.assertTrue(response.success)
        self.assertEqual(response.data["guidance_type"], "comprehensive")
        self.assertGreater(len(response.data["recommendations"]), 5)
        self.assertTrue(response.data["crop_specific"])
        self.assertIn("categories", response.data)
    
    @patch('src.agents.agriculture_router.AgricultureRouter.classify_domains')
    def test_guidance_query_routing(self, mock_classify_domains):
        """Test that guidance queries are properly routed"""
        from src.agents.agriculture_router import AgricultureRouter
        from src.core.agriculture_models import QueryDomain
        
        # Setup mock
        mock_classify_domains.return_value = ([QueryDomain.SMART_FARMING], 0.9)
        
        # Create router
        router = AgricultureRouter()
        
        # Create test queries
        rotation_query = "What crops should I rotate with cotton?"
        water_query = "How can I reduce irrigation water in my farm?"
        
        # Test routing
        domains, _ = router.classify_domains(rotation_query)
        self.assertIn(QueryDomain.SMART_FARMING, domains)
        
        domains, _ = router.classify_domains(water_query)
        self.assertIn(QueryDomain.SMART_FARMING, domains)
        
        # Test agent selection
        agents = router.select_agents([QueryDomain.SMART_FARMING])
        self.assertIn("smart_farming_guidance_agent", agents)


if __name__ == '__main__':
    unittest.main()
