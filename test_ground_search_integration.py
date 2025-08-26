#!/usr/bin/env python3
"""
Ground Search Service Integration Test

This script demonstrates the integration of the ground search service with different
agricultural agents to enhance their responses with up-to-date information from the web.
"""

import os
import sys
import asyncio
import argparse
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the core models
from src.core.agriculture_models import (
    AgricultureQuery, AgentResponse, QueryDomain, Language, 
    Location, SoilType, CropType
)

# Import the ground search service
from src.services.ground_search_service import (
    create_ground_search_service, GroundedInfo
)

# Import the enhancer
from src.agents.ground_search_enhancer import GroundSearchEnhancer

# Import agents that we'll enhance
from src.agents.crop_selection_agent import CropSelectionAgent
from src.agents.disease_identification_agent import DiseaseIdentificationAgent
from src.agents.weather_forecast_agent import WeatherForecastAgent
from src.agents.market_timing_agent import MarketTimingAgent
from src.agents.finance_policy_agent import FinancePolicyAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedAgent(GroundSearchEnhancer):
    """
    Simple wrapper to enhance any agent with ground search capabilities
    """
    
    def __init__(self, base_agent, gemini_api_key=None, google_search_api_key=None, google_search_cx=None):
        """Initialize the enhanced agent with a base agent"""
        self.base_agent = base_agent
        GroundSearchEnhancer.__init__(
            self,
            gemini_api_key=gemini_api_key,
            google_search_api_key=google_search_api_key,
            google_search_cx=google_search_cx,
            enable_grounding=True
        )
        
        logger.info(f"Enhanced agent created for {base_agent.__class__.__name__}")
    
    async def process_query(self, query: AgricultureQuery) -> AgentResponse:
        """Process a query with ground search enhancement"""
        logger.info(f"Processing query with enhanced agent: {query.query_text}")
        
        # Step 1: Get the base agent response
        base_response = await self.base_agent.process_query(query)
        logger.info("Base agent response generated")
        
        # Step 2: Ground the query using external sources
        logger.info("Grounding the query with external sources...")
        grounded_info = await self.ground_query(query)
        
        # Step 3: Enhance the response with grounded information
        if grounded_info:
            logger.info(f"Enhancing response with {len(grounded_info.sources)} sources")
            enhanced_response = self.enhance_response_with_grounding(base_response, grounded_info)
            return enhanced_response
        else:
            logger.warning("No grounded information available, returning base response")
            return base_response


# Test queries for each agent type
TEST_QUERIES = {
    "crop": [
        "What crops are suitable for growing in alkaline soil in Maharashtra?",
        "Which cotton variety should I plant in Punjab for higher yield?",
        "Best rice varieties for flood-prone areas in West Bengal"
    ],
    "disease": [
        "How to identify and treat powdery mildew on wheat?",
        "My tomato plants have yellow leaves with black spots, what disease is this?",
        "Prevention methods for rice blast disease in monsoon season"
    ],
    "weather": [
        "How will the upcoming monsoon affect wheat crops in Central India?",
        "Is the current weather suitable for planting soybeans in Madhya Pradesh?",
        "Weather forecast impact on mango harvesting in Andhra Pradesh"
    ],
    "market": [
        "When is the best time to sell wheat in Haryana this season?",
        "Current MSP for sugarcane and expected price trends",
        "How are pulse prices expected to change in the next three months?"
    ],
    "finance": [
        "What government subsidies are available for drip irrigation in Karnataka?",
        "Latest Kisan Credit Card scheme updates and benefits",
        "Agricultural loan waiver programs for small farmers in 2025"
    ]
}


async def test_agent_with_grounding(
    agent_type: str,
    query_text: str,
    gemini_api_key: str,
    google_search_api_key: str,
    google_search_cx: str
) -> Dict[str, Any]:
    """Test an agent with grounding enhancement"""
    
    # Create the appropriate base agent
    if agent_type == "crop":
        base_agent = CropSelectionAgent("crop-agent-1", "Crop Selection Agent")
        query_domain = QueryDomain.CROP_SELECTION
    elif agent_type == "disease":
        base_agent = DiseaseIdentificationAgent("disease-agent-1", "Disease Identification Agent")
        query_domain = QueryDomain.DISEASE_IDENTIFICATION
    elif agent_type == "weather":
        base_agent = WeatherForecastAgent("weather-agent-1", "Weather Forecast Agent")
        query_domain = QueryDomain.WEATHER_FORECAST
    elif agent_type == "market":
        base_agent = MarketTimingAgent("market-agent-1", "Market Timing Agent")
        query_domain = QueryDomain.MARKET_TIMING
    elif agent_type == "finance":
        base_agent = FinancePolicyAgent("finance-agent-1", "Finance Policy Agent")
        query_domain = QueryDomain.FINANCE_POLICY
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    # Create the enhanced agent
    enhanced_agent = EnhancedAgent(
        base_agent,
        gemini_api_key=gemini_api_key,
        google_search_api_key=google_search_api_key,
        google_search_cx=google_search_cx
    )
    
    # Create the query
    query = AgricultureQuery(
        query_id=f"test-{agent_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        query_text=query_text,
        query_domain=query_domain,
        query_language=Language.ENGLISH,
        location=Location(state="Maharashtra", district="Pune"),
        user_id="test-user",
        timestamp=datetime.now()
    )
    
    # Process with base agent (without grounding)
    logger.info(f"Processing with base {agent_type} agent: {query_text}")
    try:
        base_start_time = datetime.now()
        base_response = await base_agent.process_query(query)
        base_time = (datetime.now() - base_start_time).total_seconds()
        logger.info(f"Base agent response generated in {base_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error with base agent: {e}")
        base_response = AgentResponse(
            agent_id=base_agent.agent_id,
            agent_name=base_agent.name,
            query_id=query.query_id,
            response_text=f"Error with base agent: {str(e)}",
            confidence_score=0.0,
            timestamp=datetime.now()
        )
        base_time = 0
    
    # Process with enhanced agent (with grounding)
    logger.info(f"Processing with enhanced {agent_type} agent: {query_text}")
    try:
        enhanced_start_time = datetime.now()
        enhanced_response = await enhanced_agent.process_query(query)
        enhanced_time = (datetime.now() - enhanced_start_time).total_seconds()
        logger.info(f"Enhanced agent response generated in {enhanced_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error with enhanced agent: {e}")
        enhanced_response = AgentResponse(
            agent_id=enhanced_agent.base_agent.agent_id,
            agent_name=enhanced_agent.base_agent.name,
            query_id=query.query_id,
            response_text=f"Error with enhanced agent: {str(e)}",
            confidence_score=0.0,
            timestamp=datetime.now()
        )
        enhanced_time = 0
    
    # Prepare the result
    result = {
        "query": query_text,
        "agent_type": agent_type,
        "base_response": {
            "text": base_response.response_text,
            "confidence": base_response.confidence_score,
            "time_seconds": base_time
        },
        "enhanced_response": {
            "text": enhanced_response.response_text,
            "confidence": enhanced_response.confidence_score,
            "time_seconds": enhanced_time,
            "grounding_metadata": enhanced_response.metadata if enhanced_response.metadata else {}
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return result


async def run_tests(
    agent_types: List[str],
    gemini_api_key: str,
    google_search_api_key: str,
    google_search_cx: str,
    output_file: str,
    num_queries: int = 1
):
    """Run tests for specified agent types"""
    results = []
    
    for agent_type in agent_types:
        logger.info(f"Testing {agent_type} agent")
        
        # Get the test queries for this agent type
        queries = TEST_QUERIES.get(agent_type, [])
        if not queries:
            logger.warning(f"No test queries found for {agent_type} agent")
            continue
        
        # Use only the requested number of queries
        selected_queries = queries[:num_queries]
        
        for query_text in selected_queries:
            try:
                result = await test_agent_with_grounding(
                    agent_type=agent_type,
                    query_text=query_text,
                    gemini_api_key=gemini_api_key,
                    google_search_api_key=google_search_api_key,
                    google_search_cx=google_search_cx
                )
                
                results.append(result)
                
                # Print comparison
                print("\n" + "=" * 80)
                print(f"QUERY: {query_text}")
                print(f"AGENT TYPE: {agent_type}")
                print("-" * 80)
                print("BASE RESPONSE:")
                print(result["base_response"]["text"][:500] + "..." if len(result["base_response"]["text"]) > 500 else result["base_response"]["text"])
                print(f"Confidence: {result['base_response']['confidence']}, Time: {result['base_response']['time_seconds']:.2f}s")
                print("-" * 80)
                print("ENHANCED RESPONSE:")
                print(result["enhanced_response"]["text"][:500] + "..." if len(result["enhanced_response"]["text"]) > 500 else result["enhanced_response"]["text"])
                print(f"Confidence: {result['enhanced_response']['confidence']}, Time: {result['enhanced_response']['time_seconds']:.2f}s")
                print("=" * 80 + "\n")
                
            except Exception as e:
                logger.error(f"Error testing {agent_type} agent with query '{query_text}': {e}")
    
    # Save results to output file
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results to {output_file}: {e}")


def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description="Test ground search enhancement for agricultural agents")
    
    parser.add_argument("--agents", type=str, default="all",
                        help="Comma-separated list of agent types to test (crop,disease,weather,market,finance), or 'all'")
    parser.add_argument("--queries", type=int, default=1,
                        help="Number of queries to test per agent type (default: 1)")
    parser.add_argument("--output", type=str, default="ground_search_test_results.json",
                        help="Output file to save test results (default: ground_search_test_results.json)")
    
    args = parser.parse_args()
    
    # Get API keys from environment
    gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    google_search_api_key = os.environ.get("GOOGLE_SEARCH_API_KEY") or gemini_api_key
    google_search_cx = os.environ.get("GOOGLE_SEARCH_CX")
    
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")
        return 1
    
    if not google_search_cx:
        logger.error("GOOGLE_SEARCH_CX environment variable must be set")
        return 1
    
    # Determine which agents to test
    if args.agents.lower() == "all":
        agent_types = ["crop", "disease", "weather", "market", "finance"]
    else:
        agent_types = [agent_type.strip() for agent_type in args.agents.split(",")]
        # Validate agent types
        valid_types = ["crop", "disease", "weather", "market", "finance"]
        for agent_type in agent_types:
            if agent_type not in valid_types:
                logger.error(f"Unknown agent type: {agent_type}")
                return 1
    
    logger.info(f"Testing agents: {', '.join(agent_types)}")
    logger.info(f"Queries per agent: {args.queries}")
    
    # Run the tests
    asyncio.run(run_tests(
        agent_types=agent_types,
        gemini_api_key=gemini_api_key,
        google_search_api_key=google_search_api_key,
        google_search_cx=google_search_cx,
        output_file=args.output,
        num_queries=args.queries
    ))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
