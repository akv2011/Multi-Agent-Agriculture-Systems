"""
Test script for Market Timing Agent
"""
import sys
import os
import asyncio
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

# Add parent directory to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock necessary classes for standalone testing
class Language(Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    MIXED = "mixed"

class CropType(Enum):
    WHEAT = "wheat"
    ONION = "onion"

@dataclass
class Location:
    state: str
    district: str

@dataclass
class AgricultureQuery:
    query_text: str
    query_language: Language
    user_id: str
    location: Optional[Location] = None

@dataclass
class AgentResponse:
    agent_id: str
    agent_name: str
    query_id: str
    response_text: str
    response_language: Language
    confidence_score: float
    reasoning: str = ""
    recommendations: List[Dict[str, Any]] = None
    sources: List[str] = None
    next_steps: List[str] = None
    timestamp: datetime = None
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = None
    warnings: List[str] = None

class BaseAgent:
    def __init__(self):
        self.agent_id = "base"
        self.capabilities = []

# Dynamically import the agent to test
from src.agents.market_timing_agent import MarketTimingAgent, Commodity

async def main():
    """Main function to run the test"""
    agent = MarketTimingAgent()
    
    print("📈 Testing Market Timing Agent")
    
    # Test 1: English query for Wheat
    query_en = AgricultureQuery(
        query_text="What is the price forecast for wheat?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_en",
        location=Location(state="Punjab", district="Amritsar")
    )
    
    print("\n🔄 Processing English query for Wheat...")
    response_en = await agent.process_query(query_en)
    print(f"✅ English Response: {response_en.response_text}")
    assert response_en.confidence_score > 0.7
    assert "Wheat" in response_en.response_text or "गेहूं" in response_en.response_text

    # Test 2: Hindi query for Onion
    query_hi = AgricultureQuery(
        query_text="प्याज का भाव क्या रहेगा?",
        query_language=Language.HINDI,
        user_id="test_farmer_hi",
        location=Location(state="Maharashtra", district="Nashik")
    )
    
    print("\n🔄 Processing Hindi query for Onion...")
    response_hi = await agent.process_query(query_hi)
    print(f"✅ Hindi Response: {response_hi.response_text}")
    assert response_hi.confidence_score > 0.7
    assert "प्याज" in response_hi.response_text

    # Test 3: General query with no commodity
    query_general = AgricultureQuery(
        query_text="What is the market trend?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_gen"
    )
    print("\n🔄 Processing general query...")
    response_gen = await agent.process_query(query_general)
    print(f"✅ General Response: {response_gen.response_text}")
    assert "Please specify a commodity" in response_gen.response_text

    # Test 4: Check internal forecast generation
    print("\n🔄 Testing internal forecast generation for Cotton...")
    forecast = agent._generate_price_forecast(Commodity.COTTON)
    print(f"✅ Forecast for Cotton: Current Price ₹{forecast.current_price}, 7D Forecast ₹{forecast.forecast_price_7d}")
    assert forecast.current_price > 0
    assert forecast.forecast_price_7d > 0

    print("\n🎉 Market Timing Agent working successfully!")

if __name__ == "__main__":
    # Mock the modules that the agent depends on
    import types
    
    # Mock agriculture_models
    agriculture_models_mock = types.ModuleType('src.core.agriculture_models')
    agriculture_models_mock.AgricultureQuery = AgricultureQuery
    agriculture_models_mock.AgentResponse = AgentResponse
    agriculture_models_mock.CropType = CropType
    agriculture_models_mock.Location = Location
    agriculture_models_mock.QueryDomain = None # Not used by this agent
    agriculture_models_mock.Language = Language
    sys.modules['src.core.agriculture_models'] = agriculture_models_mock
    
    # Mock base_agent
    base_agent_mock = types.ModuleType('src.agents.base_agent')
    base_agent_mock.BaseAgent = BaseAgent
    sys.modules['src.agents.base_agent'] = base_agent_mock
    sys.modules['..core'] = types.ModuleType('..core')
    sys.modules['..core.agriculture_models'] = agriculture_models_mock
    
    asyncio.run(main())
