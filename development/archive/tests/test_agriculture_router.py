"""
Test the Agriculture Router System
Test the multi-agent router implementation for agricultural queries.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Setup test environment
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.agriculture_models import (
    AgricultureQuery, QueryDomain, Language, Location, FarmProfile
)
from src.agents.agriculture_router import AgricultureRouter
from src.services.agriculture_integration import AgricultureIntegrationService

# Test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAgricultureRouter:
    """Test suite for the agriculture router system"""
    
    def __init__(self):
        self.router = AgricultureRouter()
        self.integration_service = AgricultureIntegrationService()
        self.test_results = []
    
    async def test_router_initialization(self):
        """Test that the router initializes correctly"""
        try:
            logger.info("Testing router initialization...")
            
            # Test pattern loading
            assert len(self.router.domain_patterns) > 0, "Domain patterns not loaded"
            assert len(self.router.keywords) > 0, "Keywords not loaded"
            
            # Test domain coverage
            expected_domains = [
                QueryDomain.CROP_SELECTION,
                QueryDomain.PEST_MANAGEMENT,
                QueryDomain.IRRIGATION,
                QueryDomain.FINANCE_POLICY,
                QueryDomain.MARKET_TIMING,
                QueryDomain.HARVEST_PLANNING,
                QueryDomain.INPUT_MATERIALS
            ]
            
            for domain in expected_domains:
                assert domain in self.router.domain_patterns, f"Missing patterns for {domain}"
            
            result = {"test": "router_initialization", "status": "PASS", "message": "Router initialized successfully"}
            self.test_results.append(result)
            logger.info("✓ Router initialization test passed")
            
        except Exception as e:
            result = {"test": "router_initialization", "status": "FAIL", "error": str(e)}
            self.test_results.append(result)
            logger.error(f"✗ Router initialization test failed: {e}")
    
    async def test_pattern_based_classification(self):
        """Test pattern-based query classification"""
        try:
            logger.info("Testing pattern-based classification...")
            
            test_cases = [
                {
                    "query": "What crop should I grow in Punjab during Rabi season?",
                    "expected_domain": QueryDomain.CROP_SELECTION,
                    "language": Language.ENGLISH
                },
                {
                    "query": "My wheat has yellow spots, what spray should I use?",
                    "expected_domain": QueryDomain.PEST_MANAGEMENT,
                    "language": Language.ENGLISH
                },
                {
                    "query": "When should I water my cotton crop?",
                    "expected_domain": QueryDomain.IRRIGATION,
                    "language": Language.ENGLISH
                },
                {
                    "query": "गेहूं के लिए कौन सा खाद अच्छा है?",
                    "expected_domain": QueryDomain.INPUT_MATERIALS,
                    "language": Language.HINDI
                },
                {
                    "query": "Kisan loan kaise milega?",
                    "expected_domain": QueryDomain.FINANCE_POLICY,
                    "language": Language.MIXED
                }
            ]
            
            passed = 0
            total = len(test_cases)
            
            for i, case in enumerate(test_cases):
                query = AgricultureQuery(
                    query_text=case["query"],
                    query_language=case["language"],
                    user_id=f"test_user_{i}"
                )
                
                # Test pattern-based classification
                domain = await self.router._classify_query_pattern_based(query)
                
                if domain == case["expected_domain"]:
                    passed += 1
                    logger.info(f"✓ Query '{case['query']}' correctly classified as {domain.value}")
                else:
                    logger.warning(f"✗ Query '{case['query']}' classified as {domain.value}, expected {case['expected_domain'].value}")
            
            success_rate = passed / total
            result = {
                "test": "pattern_based_classification",
                "status": "PASS" if success_rate >= 0.7 else "FAIL",
                "passed": passed,
                "total": total,
                "success_rate": success_rate
            }
            self.test_results.append(result)
            logger.info(f"Pattern-based classification: {passed}/{total} tests passed ({success_rate:.1%})")
            
        except Exception as e:
            result = {"test": "pattern_based_classification", "status": "FAIL", "error": str(e)}
            self.test_results.append(result)
            logger.error(f"✗ Pattern-based classification test failed: {e}")
    
    async def test_multilingual_support(self):
        """Test multilingual query handling"""
        try:
            logger.info("Testing multilingual support...")
            
            multilingual_queries = [
                {
                    "query": "मेरी फसल में कीड़े लगे हैं। What should I spray?",
                    "language": Language.MIXED,
                    "expected_keywords": ["pest", "spray", "treatment"]
                },
                {
                    "query": "Cotton irrigation schedule kya hoga?",
                    "language": Language.MIXED,
                    "expected_keywords": ["irrigation", "water", "schedule"]
                },
                {
                    "query": "Market price कब बढ़ेगा? When to sell crop?",
                    "language": Language.MIXED,
                    "expected_keywords": ["market", "price", "sell"]
                }
            ]
            
            passed = 0
            total = len(multilingual_queries)
            
            for i, case in enumerate(multilingual_queries):
                query = AgricultureQuery(
                    query_text=case["query"],
                    query_language=case["language"],
                    user_id=f"test_multilingual_{i}"
                )
                
                # Test domain detection
                domain = await self.router._classify_query_pattern_based(query)
                
                # Test keyword detection
                detected_keywords = []
                for keyword_list in self.router.keywords.values():
                    for keyword in keyword_list:
                        if keyword.lower() in case["query"].lower():
                            detected_keywords.append(keyword)
                
                # Check if expected keywords are detected
                keywords_found = any(
                    expected in detected_keywords 
                    for expected in case["expected_keywords"]
                )
                
                if domain != QueryDomain.GENERAL and keywords_found:
                    passed += 1
                    logger.info(f"✓ Multilingual query '{case['query']}' handled correctly")
                else:
                    logger.warning(f"✗ Multilingual query '{case['query']}' not handled properly")
            
            success_rate = passed / total
            result = {
                "test": "multilingual_support",
                "status": "PASS" if success_rate >= 0.7 else "FAIL",
                "passed": passed,
                "total": total,
                "success_rate": success_rate
            }
            self.test_results.append(result)
            logger.info(f"Multilingual support: {passed}/{total} tests passed ({success_rate:.1%})")
            
        except Exception as e:
            result = {"test": "multilingual_support", "status": "FAIL", "error": str(e)}
            self.test_results.append(result)
            logger.error(f"✗ Multilingual support test failed: {e}")
    
    async def test_integration_service(self):
        """Test the agriculture integration service"""
        try:
            logger.info("Testing integration service...")
            
            # Test service initialization
            assert self.integration_service.agriculture_router is not None, "Router not initialized"
            
            # Test query handling pipeline
            test_query_data = {
                "query_text": "What is the best crop for sandy soil in Rajasthan?",
                "user_id": "test_integration",
                "query_language": Language.ENGLISH,
                "context": {"test": True}
            }
            
            # This would normally connect to WebSocket for real-time updates
            # For testing, we'll just verify the service can process the query
            query_result = await self.integration_service.handle_agriculture_query(test_query_data)
            
            assert "query_id" in query_result, "Query ID not generated"
            assert "status" in query_result, "Status not provided"
            
            result = {
                "test": "integration_service",
                "status": "PASS",
                "message": "Integration service working correctly"
            }
            self.test_results.append(result)
            logger.info("✓ Integration service test passed")
            
        except Exception as e:
            result = {"test": "integration_service", "status": "FAIL", "error": str(e)}
            self.test_results.append(result)
            logger.error(f"✗ Integration service test failed: {e}")
    
    async def test_response_synthesis(self):
        """Test multi-agent response synthesis"""
        try:
            logger.info("Testing response synthesis...")
            
            # Mock agent responses
            mock_responses = {
                "crop_selection": {
                    "agent_id": "crop_selection_agent",
                    "status": "completed",
                    "response": {
                        "recommendations": [
                            {"crop": "wheat", "suitability": 0.9},
                            {"crop": "mustard", "suitability": 0.7}
                        ]
                    },
                    "confidence": 0.85
                },
                "irrigation": {
                    "agent_id": "irrigation_agent", 
                    "status": "completed",
                    "response": {
                        "schedule": "Water every 7-10 days during growth stage"
                    },
                    "confidence": 0.78
                }
            }
            
            # Test response synthesis
            synthesized = await self.integration_service._synthesize_responses(mock_responses)
            
            assert "final_recommendation" in synthesized, "Final recommendation not generated"
            assert "sources" in synthesized, "Sources not included"
            assert "confidence" in synthesized, "Confidence not calculated"
            
            result = {
                "test": "response_synthesis",
                "status": "PASS",
                "message": "Response synthesis working correctly"
            }
            self.test_results.append(result)
            logger.info("✓ Response synthesis test passed")
            
        except Exception as e:
            result = {"test": "response_synthesis", "status": "FAIL", "error": str(e)}
            self.test_results.append(result)
            logger.error(f"✗ Response synthesis test failed: {e}")
    
    async def run_all_tests(self):
        """Run all router system tests"""
        logger.info("Starting Agriculture Router System Tests...")
        logger.info("=" * 50)
        
        start_time = datetime.now()
        
        # Run all tests
        await self.test_router_initialization()
        await self.test_pattern_based_classification()
        await self.test_multilingual_support()
        await self.test_integration_service()
        await self.test_response_synthesis()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        # Print summary
        logger.info("=" * 50)
        logger.info("TEST SUMMARY")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {passed_tests/total_tests:.1%}")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        # Print detailed results
        logger.info("\nDETAILED RESULTS:")
        for result in self.test_results:
            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            logger.info(f"{status_symbol} {result['test']}: {result['status']}")
            if "error" in result:
                logger.info(f"   Error: {result['error']}")
        
        # Save results to file
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": passed_tests/total_tests,
                    "duration_seconds": duration,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        logger.info(f"\nTest results saved to: {results_file}")
        
        return passed_tests == total_tests


async def main():
    """Main test function"""
    tester = TestAgricultureRouter()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All tests passed! Agriculture Router System is working correctly.")
    else:
        logger.error("\n❌ Some tests failed. Please review the results above.")
    
    return success


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    exit(0 if success else 1)
