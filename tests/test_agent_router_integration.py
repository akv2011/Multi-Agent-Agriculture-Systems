"""
Test Agriculture Router Integration
Tests the router's ability to correctly identify query domains and route to appropriate agents
"""

import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agriculture_router import AgricultureRouter
from src.core.agriculture_models import (
    AgricultureQuery, AgricultureTask, QueryDomain, Location, TaskPriority, Language
)


class TestAgentRouterIntegration(unittest.TestCase):
    """Test agriculture router query classification and agent selection"""
    
    def setUp(self):
        """Set up test environment"""
        self.router = AgricultureRouter()
    
    def test_domain_classification(self):
        """Test domain classification for different query types"""
        
        # Test crop selection queries
        crop_query = "What crop should I grow in Punjab?"
        domains, confidence = self.router.classify_domains(crop_query)
        self.assertIn(QueryDomain.CROP_SELECTION, domains)
        
        # Test disease identification queries
        disease_query = "My rice plants have brown spots on the leaves"
        domains, confidence = self.router.classify_domains(disease_query)
        self.assertIn(QueryDomain.DISEASE_IDENTIFICATION, domains)
        
        # Test disease identification with image
        disease_image_query = "Can you identify the disease in this image?"
        domains, confidence = self.router.classify_domains(disease_image_query, has_image=True)
        self.assertIn(QueryDomain.DISEASE_IDENTIFICATION, domains)
        
        # Test irrigation queries
        irrigation_query = "When should I water my cotton field?"
        domains, confidence = self.router.classify_domains(irrigation_query)
        self.assertIn(QueryDomain.IRRIGATION, domains)
        
        # Test fertilizer recommendation queries
        fertilizer_query = "What fertilizer should I use for N=40, P=20, K=10?"
        domains, confidence = self.router.classify_domains(fertilizer_query, npk_data=True)
        self.assertIn(QueryDomain.FERTILIZER_RECOMMENDATION, domains)
        
        # Test weather forecast queries
        weather_query = "What is the weather forecast for next week in Maharashtra?"
        domains, confidence = self.router.classify_domains(weather_query)
        self.assertIn(QueryDomain.WEATHER_FORECAST, domains)
        
        # Test smart farming guidance queries
        guidance_query = "What are sustainable farming techniques for rice?"
        domains, confidence = self.router.classify_domains(guidance_query)
        self.assertIn(QueryDomain.SMART_FARMING, domains)
        
        # Test market timing queries
        market_query = "When should I sell my wheat for best price?"
        domains, confidence = self.router.classify_domains(market_query)
        self.assertIn(QueryDomain.MARKET_TIMING, domains)
        
        # Test finance policy queries
        finance_query = "Are there any government subsidies for drip irrigation?"
        domains, confidence = self.router.classify_domains(finance_query)
        self.assertIn(QueryDomain.FINANCE_POLICY, domains)
        
    def test_language_detection(self):
        """Test language detection for English, Hindi and mixed queries"""
        
        # Test English queries
        english_query = "When should I harvest my wheat crop?"
        self.assertEqual(self.router.detect_language(english_query), Language.ENGLISH)
        
        # Test Hindi queries (Devanagari)
        hindi_query = "मुझे गेहूं की फसल कब काटनी चाहिए?"
        self.assertEqual(self.router.detect_language(hindi_query), Language.HINDI)
        
        # Test Hindi queries (Roman script)
        roman_hindi_query = "Mujhe gehu ki fasal kab katni chahiye?"
        self.assertEqual(self.router.detect_language(roman_hindi_query), Language.HINDI)
        
        # Test mixed language queries
        mixed_query = "Rice crop में pest control के लिए क्या spray करना चाहिए?"
        self.assertEqual(self.router.detect_language(mixed_query), Language.MIXED)
    
    @patch('src.agents.agriculture_router.AgricultureRouter.analyze_query_with_llm')
    async def test_agent_selection(self, mock_analyze):
        """Test agent selection for different query types"""
        
        # Setup mock
        mock_analyze.return_value = {}
        
        # Test crop selection agent selection
        crop_task = AgricultureTask(
            task_id="test_crop",
            description="What crop should I grow in Punjab?",
            task_type="query",
            priority=TaskPriority.MEDIUM
        )
        crop_result = await self.router.execute(crop_task, {})
        self.assertIn("crop_selection_agent", crop_result.get("routing_decision").selected_agents)
        
        # Test disease identification agent selection with image
        disease_task = AgricultureTask(
            task_id="test_disease",
            description="What disease is affecting my crop?",
            task_type="query",
            priority=TaskPriority.MEDIUM,
            query_data=AgricultureQuery(
                query_text="What disease is affecting my crop?",
                image_data="mock_image_data"
            )
        )
        disease_result = await self.router.execute(disease_task, {})
        self.assertIn("disease_specialist", disease_result.get("routing_decision").selected_agents)
        
        # Test fertilizer recommendation agent selection
        fertilizer_task = AgricultureTask(
            task_id="test_fertilizer",
            description="Recommend fertilizer for N=40, P=20, K=10",
            task_type="query",
            priority=TaskPriority.MEDIUM
        )
        fertilizer_result = await self.router.execute(fertilizer_task, {"soil_data": {"nitrogen": 40, "phosphorus": 20, "potassium": 10}})
        self.assertIn("fertilizer_recommendation_agent", fertilizer_result.get("routing_decision").selected_agents)
        
        # Test smart farming guidance agent selection
        guidance_task = AgricultureTask(
            task_id="test_guidance",
            description="What are sustainable farming practices for cotton?",
            task_type="query",
            priority=TaskPriority.MEDIUM
        )
        guidance_result = await self.router.execute(guidance_task, {})
        self.assertIn("smart_farming_guidance_agent", guidance_result.get("routing_decision").selected_agents)
    
    @patch('src.agents.agriculture_router.AgricultureRouter.analyze_query_with_llm')
    async def test_google_search_fallback(self, mock_analyze):
        """Test Google Search fallback for financial and general queries"""
        
        # Setup mock
        mock_analyze.return_value = {}
        
        # Test financial query with Google Search fallback
        finance_task = AgricultureTask(
            task_id="test_finance",
            description="What is the current MSP for wheat in India?",
            task_type="query",
            priority=TaskPriority.MEDIUM
        )
        finance_result = await self.router.execute(finance_task, {})
        self.assertIn("finance_policy_agent", finance_result.get("routing_decision").selected_agents)
        self.assertTrue(finance_result.get("use_google_search_fallback", False))
        
        # Test market query with Google Search fallback
        market_task = AgricultureTask(
            task_id="test_market",
            description="What are current soybean prices in Madhya Pradesh?",
            task_type="query",
            priority=TaskPriority.MEDIUM
        )
        market_result = await self.router.execute(market_task, {})
        self.assertTrue(market_result.get("use_google_search_fallback", False))
        
    async def test_location_extraction(self):
        """Test extraction of location from queries"""
        
        # Test query with direct state mention
        query_with_state = "What crops grow best in Punjab?"
        location = self.router.extract_location_info(query_with_state, {})
        self.assertIsNotNone(location)
        self.assertEqual(location.state, "Punjab")
        
        # Test query with location in context
        query_without_location = "What crops grow best here?"
        context_location = {"location": Location(state="Maharashtra", district="Pune")}
        location = self.router.extract_location_info(query_without_location, context_location)
        self.assertIsNotNone(location)
        self.assertEqual(location.state, "Maharashtra")
        self.assertEqual(location.district, "Pune")
        

if __name__ == '__main__':
    unittest.main()
