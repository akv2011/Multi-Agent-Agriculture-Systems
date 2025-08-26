"""
Comprehensive Integration Test for Multi-Agent Agriculture System
Tests the complete query processing pipeline from router to specialist agents.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any

# Setup test environment
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agriculture_models import (
    AgricultureQuery, QueryDomain, Language, Location, FarmProfile
)
from src.agents.agriculture_router import AgricultureRouter
from src.agents.crop_selection_agent import CropSelectionAgent
from src.agents.pest_management_agent import PestManagementAgent
from src.agents.irrigation_agent import IrrigationAgent

# Test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedSystemTester:
    """Comprehensive test suite for the integrated agriculture system"""
    
    def __init__(self):
        self.router = AgricultureRouter()
        self.crop_agent = CropSelectionAgent()
        self.pest_agent = PestManagementAgent()
        self.irrigation_agent = IrrigationAgent()
        self.test_results = []
    
    async def test_single_agent_queries(self):
        """Test individual agent capabilities"""
        logger.info("Testing individual agent capabilities...")
        
        test_cases = [
            {
                "name": "Crop Selection - Simple Query",
                "query": "What crop should I grow in Punjab during Rabi season?",
                "agent": self.crop_agent,
                "expected_domain": QueryDomain.CROP_SELECTION
            },
            {
                "name": "Pest Management - Hindi Query",
                "query": "मेरे गेहूं पर पीले धब्बे हैं, क्या करूं?",
                "agent": self.pest_agent,
                "expected_domain": QueryDomain.PEST_MANAGEMENT
            },
            {
                "name": "Irrigation - Technical Query",
                "query": "How much water does cotton need during flowering stage?",
                "agent": self.irrigation_agent,
                "expected_domain": QueryDomain.IRRIGATION
            }
        ]
        
        for case in test_cases:
            try:
                query = AgricultureQuery(
                    query_text=case["query"],
                    query_language=Language.ENGLISH if "Hindi" not in case["name"] else Language.HINDI,
                    user_id=f"test_{case['name'].lower().replace(' ', '_')}"
                )
                
                start_time = datetime.now()
                response = await case["agent"].process_query(query)
                end_time = datetime.now()
                
                processing_time = (end_time - start_time).total_seconds()
                
                success = (
                    response.status == "completed" and
                    response.confidence > 0.3 and
                    len(response.recommendations) > 0
                )
                
                result = {
                    "test": case["name"],
                    "status": "PASS" if success else "FAIL",
                    "query": case["query"],
                    "confidence": response.confidence,
                    "processing_time": processing_time,
                    "recommendations_count": len(response.recommendations),
                    "agent_id": response.agent_id
                }
                
                if not success:
                    result["error"] = f"Status: {response.status}, Confidence: {response.confidence}"
                
                self.test_results.append(result)
                logger.info(f"{'✓' if success else '✗'} {case['name']}: {processing_time:.2f}s")
                
            except Exception as e:
                result = {
                    "test": case["name"],
                    "status": "FAIL",
                    "error": str(e)
                }
                self.test_results.append(result)
                logger.error(f"✗ {case['name']}: {e}")
    
    async def test_router_classification(self):
        """Test router query classification accuracy"""
        logger.info("Testing router classification...")
        
        test_cases = [
            {
                "query": "What wheat variety is best for clay soil?",
                "expected_domain": QueryDomain.CROP_SELECTION,
                "language": Language.ENGLISH
            },
            {
                "query": "My rice crop has brown spots on leaves",
                "expected_domain": QueryDomain.PEST_MANAGEMENT,
                "language": Language.ENGLISH
            },
            {
                "query": "When should I irrigate my cotton crop?",
                "expected_domain": QueryDomain.IRRIGATION,
                "language": Language.ENGLISH
            },
            {
                "query": "Kisan loan कैसे मिलेगा?",
                "expected_domain": QueryDomain.FINANCE_POLICY,
                "language": Language.MIXED
            },
            {
                "query": "Market में wheat का भाव कब बढ़ेगा?",
                "expected_domain": QueryDomain.MARKET_TIMING,
                "language": Language.MIXED
            }
        ]
        
        correct_classifications = 0
        total_tests = len(test_cases)
        
        for i, case in enumerate(test_cases):
            try:
                query = AgricultureQuery(
                    query_text=case["query"],
                    query_language=case["language"],
                    user_id=f"test_router_{i}"
                )
                
                # Test pattern-based classification
                detected_domain = await self.router._classify_query_pattern_based(query)
                
                correct = detected_domain == case["expected_domain"]
                if correct:
                    correct_classifications += 1
                
                result = {
                    "test": f"Router Classification - {case['query'][:30]}...",
                    "status": "PASS" if correct else "FAIL",
                    "expected_domain": case["expected_domain"].value,
                    "detected_domain": detected_domain.value,
                    "query_language": case["language"].value
                }
                
                self.test_results.append(result)
                logger.info(f"{'✓' if correct else '✗'} {case['query'][:50]}... -> {detected_domain.value}")
                
            except Exception as e:
                result = {
                    "test": f"Router Classification Error - {case['query'][:30]}...",
                    "status": "FAIL",
                    "error": str(e)
                }
                self.test_results.append(result)
                logger.error(f"✗ Router error: {e}")
        
        accuracy = correct_classifications / total_tests if total_tests > 0 else 0
        logger.info(f"Router Classification Accuracy: {accuracy:.1%} ({correct_classifications}/{total_tests})")
        
        return accuracy
    
    async def test_multi_agent_coordination(self):
        """Test complex queries requiring multiple agents"""
        logger.info("Testing multi-agent coordination...")
        
        complex_queries = [
            {
                "query": "My wheat crop looks stressed with yellow leaves, should I water it more and what could be causing the yellowing?",
                "expected_agents": ["pest_management_agent", "irrigation_agent"],
                "description": "Pest + Irrigation coordination"
            },
            {
                "query": "I want to grow cotton in sandy soil in Rajasthan, what variety should I choose and how much water will it need?",
                "expected_agents": ["crop_selection_agent", "irrigation_agent"],
                "description": "Crop Selection + Irrigation coordination"
            },
            {
                "query": "Which crop is profitable for small farm with pest resistance and low water requirement?",
                "expected_agents": ["crop_selection_agent", "pest_management_agent", "irrigation_agent"],
                "description": "All three agents coordination"
            }
        ]
        
        for i, case in enumerate(complex_queries):
            try:
                query = AgricultureQuery(
                    query_text=case["query"],
                    query_language=Language.ENGLISH,
                    user_id=f"test_multi_{i}"
                )
                
                # Test routing decision
                routing_result = await self.router.route_query(query)
                
                if routing_result and "routing_decision" in routing_result:
                    routing_decision = routing_result["routing_decision"]
                    selected_agents = routing_decision.selected_agents
                    
                    # Check if expected agents are selected
                    agents_matched = any(
                        expected in selected_agents 
                        for expected in case["expected_agents"]
                    )
                    
                    result = {
                        "test": f"Multi-Agent - {case['description']}",
                        "status": "PASS" if agents_matched else "FAIL",
                        "query": case["query"],
                        "expected_agents": case["expected_agents"],
                        "selected_agents": selected_agents,
                        "routing_confidence": routing_decision.confidence
                    }
                    
                    logger.info(f"{'✓' if agents_matched else '✗'} {case['description']}: {selected_agents}")
                    
                else:
                    result = {
                        "test": f"Multi-Agent - {case['description']}",
                        "status": "FAIL",
                        "error": "No routing decision received"
                    }
                    logger.error(f"✗ {case['description']}: No routing decision")
                
                self.test_results.append(result)
                
            except Exception as e:
                result = {
                    "test": f"Multi-Agent - {case['description']}",
                    "status": "FAIL",
                    "error": str(e)
                }
                self.test_results.append(result)
                logger.error(f"✗ {case['description']}: {e}")
    
    async def test_end_to_end_processing(self):
        """Test complete end-to-end query processing"""
        logger.info("Testing end-to-end processing...")
        
        test_query = "I have 2 hectares of loamy soil in Punjab. What wheat variety should I grow and how should I manage irrigation?"
        
        try:
            # Create comprehensive query
            query = AgricultureQuery(
                query_text=test_query,
                query_language=Language.ENGLISH,
                user_id="test_e2e",
                farm_profile=FarmProfile(
                    farm_size=2.0,
                    soil_type="loamy",
                    location="Punjab",
                    irrigation_available=True
                )
            )
            
            # Step 1: Route the query
            routing_result = await self.router.route_query(query)
            
            if not routing_result or "routing_decision" not in routing_result:
                raise Exception("Routing failed")
            
            routing_decision = routing_result["routing_decision"]
            selected_agents = routing_decision.selected_agents
            
            # Step 2: Execute relevant agents
            agent_responses = []
            
            if "crop_selection_agent" in selected_agents:
                crop_response = await self.crop_agent.process_query(query)
                agent_responses.append(crop_response)
            
            if "irrigation_agent" in selected_agents:
                irrigation_response = await self.irrigation_agent.process_query(query)
                agent_responses.append(irrigation_response)
            
            # Step 3: Verify response quality
            success = (
                len(agent_responses) >= 2 and  # At least 2 agents responded
                all(resp.status == "completed" for resp in agent_responses) and
                all(resp.confidence > 0.3 for resp in agent_responses) and
                all(len(resp.recommendations) > 0 for resp in agent_responses)
            )
            
            result = {
                "test": "End-to-End Processing",
                "status": "PASS" if success else "FAIL",
                "query": test_query,
                "agents_executed": len(agent_responses),
                "avg_confidence": sum(r.confidence for r in agent_responses) / len(agent_responses) if agent_responses else 0,
                "total_recommendations": sum(len(r.recommendations) for r in agent_responses)
            }
            
            logger.info(f"{'✓' if success else '✗'} End-to-End: {len(agent_responses)} agents, {result['avg_confidence']:.2f} avg confidence")
            
        except Exception as e:
            result = {
                "test": "End-to-End Processing",
                "status": "FAIL",
                "error": str(e)
            }
            logger.error(f"✗ End-to-End: {e}")
        
        self.test_results.append(result)
    
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        logger.info("Starting Comprehensive Integration Tests...")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test suites
        await self.test_single_agent_queries()
        router_accuracy = await self.test_router_classification()
        await self.test_multi_agent_coordination()
        await self.test_end_to_end_processing()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        # Print comprehensive summary
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE TEST SUMMARY")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {passed_tests/total_tests:.1%}")
        logger.info(f"Router Accuracy: {router_accuracy:.1%}")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        # Categorize results
        logger.info("\nTEST RESULTS BY CATEGORY:")
        
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0] if " - " in result["test"] else "General"
            if category not in categories:
                categories[category] = {"pass": 0, "fail": 0}
            categories[category][result["status"].lower()] += 1
        
        for category, stats in categories.items():
            total = stats["pass"] + stats["fail"]
            success_rate = stats["pass"] / total if total > 0 else 0
            logger.info(f"  {category}: {stats['pass']}/{total} ({success_rate:.1%})")
        
        # List failures
        failures = [r for r in self.test_results if r["status"] == "FAIL"]
        if failures:
            logger.info("\nFAILED TESTS:")
            for failure in failures:
                logger.info(f"  ✗ {failure['test']}")
                if "error" in failure:
                    logger.info(f"    Error: {failure['error']}")
        
        # Save detailed results
        results_file = f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": passed_tests/total_tests,
                    "router_accuracy": router_accuracy,
                    "duration_seconds": duration,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results,
                "categories": categories
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\nDetailed results saved to: {results_file}")
        
        # Final verdict
        if passed_tests == total_tests and router_accuracy > 0.7:
            logger.info("\n🎉 ALL TESTS PASSED! Multi-Agent Agriculture System is fully functional.")
            return True
        elif passed_tests / total_tests > 0.8:
            logger.info("\n✅ MOSTLY SUCCESSFUL! System is functional with minor issues.")
            return True
        else:
            logger.error("\n❌ SIGNIFICANT ISSUES FOUND! Review failed tests before deployment.")
            return False


async def main():
    """Main test execution function"""
    tester = IntegratedSystemTester()
    success = await tester.run_all_tests()
    
    return success


if __name__ == "__main__":
    # Run the comprehensive integration tests
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest execution interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        exit(1)
