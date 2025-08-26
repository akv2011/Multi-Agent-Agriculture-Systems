"""
Test Google Search Service Integration
"""

import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.google_search_service import GoogleSearchService, SearchResult


class TestGoogleSearchIntegration(unittest.TestCase):
    """Test integration of Google Search Service"""
    
    def setUp(self):
        """Set up test environment"""
        # Use mock API key and CX for testing
        self.search_service = GoogleSearchService(
            api_key="mock_api_key",
            cx="mock_cx_id"
        )
    
    @patch('aiohttp.ClientSession.get')
    async def test_search_functionality(self, mock_get):
        """Test basic search functionality"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {
            "items": [
                {
                    "title": "Current MSP Rates for Wheat - Govt of India",
                    "snippet": "The Minimum Support Price for wheat crop has been fixed at Rs. 2015 per quintal for the marketing season 2022-23.",
                    "link": "https://farmer.gov.in/mspstatements.aspx"
                },
                {
                    "title": "Agriculture Price Policy - Ministry of Agriculture",
                    "snippet": "MSP rates for Kharif and Rabi crops announced for the 2022-23 season with increases across all major crops.",
                    "link": "https://agriculture.gov.in/prices"
                }
            ]
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Perform search
        results = await self.search_service.search("current wheat MSP price India")
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Current MSP Rates for Wheat - Govt of India")
        self.assertTrue(any("MSP" in result.snippet for result in results))
        
        # Verify correct parameters were used in API call
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['q'], "current wheat MSP price India")
        self.assertEqual(kwargs['params']['gl'], "in")  # Country set to India
    
    @patch('aiohttp.ClientSession.get')
    async def test_search_filtering(self, mock_get):
        """Test search result filtering and relevance scoring"""
        # Setup mock response with varied results
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {
            "items": [
                {
                    "title": "Random Website - Blog Post",
                    "snippet": "Some article mentioning farming in passing",
                    "link": "https://example.com/blog"
                },
                {
                    "title": "ICAR - Research on Agricultural Practices",
                    "snippet": "Official research on modern farming techniques by ICAR",
                    "link": "https://icar.org.in/research"
                },
                {
                    "title": "Agricultural Ministry - Official Guidelines",
                    "snippet": "Government guidelines for farmers on sustainable practices",
                    "link": "https://agriculture.gov.in/guidelines"
                }
            ]
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Perform search with domain filtering
        results = await self.search_service.search(
            "sustainable farming practices",
            filter_domains=["gov.in", "icar.org.in"]
        )
        
        # Assertions - government sites should be scored higher
        self.assertEqual(len(results), 3)  # All results returned
        
        # Check if government sites have higher relevance scores
        govt_sites = [r for r in results if ".gov.in" in r.source or "icar.org.in" in r.source]
        non_govt_sites = [r for r in results if ".gov.in" not in r.source and "icar.org.in" not in r.source]
        
        if govt_sites and non_govt_sites:  # Only compare if we have both types
            self.assertGreater(govt_sites[0].relevance_score, non_govt_sites[0].relevance_score)
    
    @patch('aiohttp.ClientSession.get')
    async def test_search_error_handling(self, mock_get):
        """Test error handling in search service"""
        # Setup mock response for API error
        mock_response = MagicMock()
        mock_response.status = 403
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Perform search
        results = await self.search_service.search("test query")
        
        # Should return empty list on error
        self.assertEqual(results, [])
    
    def test_search_cache(self):
        """Test search result caching"""
        # Prepare mock search results
        mock_results = [
            SearchResult(
                title="Test Result",
                snippet="Test snippet",
                link="https://example.com",
                source="example.com",
                relevance_score=0.8
            )
        ]
        
        # Manually set cache entry
        self.search_service.cache["test query:en:in:5"] = {
            "timestamp": self.search_service.cache_ttl.seconds,
            "results": mock_results
        }
        
        # Check if cache retrieval works
        cache_key = "test query:en:in:5"
        self.assertIn(cache_key, self.search_service.cache)
        
        # Test cache clearing
        self.search_service.clear_cache()
        self.assertEqual(len(self.search_service.cache), 0)
    
    @patch('src.services.google_search_service.GoogleSearchService.search')
    async def test_agriculture_router_fallback(self, mock_search):
        """Test agriculture router fallback to Google search for financial queries"""
        from src.agents.agriculture_router import AgricultureRouter
        from src.core.agriculture_models import AgricultureTask, TaskPriority
        
        # Setup mock
        mock_search.return_value = [
            SearchResult(
                title="Latest MSP Rates for Wheat",
                snippet="Government announces new MSP rates for wheat crop.",
                link="https://agriculture.gov.in/msp",
                source="agriculture.gov.in",
                relevance_score=0.9
            )
        ]
        
        # Create router
        router = AgricultureRouter()
        
        # Monkey-patch the router to use our mock search service
        router.search_service = self.search_service
        
        # Create a financial query task
        task = AgricultureTask(
            task_id="test_task",
            description="What is the current MSP for wheat?",
            task_type="query",
            priority=TaskPriority.MEDIUM
        )
        
        # Process the task
        result = await router.execute(task, {})
        
        # Check if finance agent was selected for this query
        self.assertTrue("finance_policy_agent" in result.get("selected_agents", []))


if __name__ == '__main__':
    unittest.main()
