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
    latitude: Optional[float] = None
    longitude: Optional[float] = None

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
    
    print("�️ Testing Satellite-Enhanced Market Timing Agent")
    
    # Test 1: English query for Wheat with satellite data
    query_en = AgricultureQuery(
        query_text="What is the price forecast for wheat? Should I sell now?",
        query_language=Language.ENGLISH,
        user_id="test_farmer_en",
        location=Location(state="Punjab", district="Amritsar", latitude=31.6340, longitude=74.8723)
    )
    
    print("\n🔄 Processing English query for Wheat with satellite data...")
    response_en = await agent.process_query(query_en)
    print(f"✅ English Response: {response_en.response_text}")
    print(f"🛰️ Satellite Enhanced: {response_en.metadata.get('satellite_enhanced', False)}")
    if response_en.metadata and response_en.metadata.get('satellite_enhanced'):
        print(f"   📊 Environmental Score: {response_en.metadata.get('environmental_score', 'N/A')}")
        print(f"   🌱 NDVI: {response_en.metadata.get('ndvi', 'N/A')}")
        print(f"   💧 Soil Moisture: {response_en.metadata.get('soil_moisture', 'N/A')}%")
        print(f"   📈 Yield Forecast: {response_en.metadata.get('yield_forecast', 'N/A')} tonnes/ha")
    assert response_en.confidence_score > 0.7
    assert "Wheat" in response_en.response_text or "गेहूं" in response_en.response_text

    # Test 2: Hindi query for Onion with satellite data
    query_hi = AgricultureQuery(
        query_text="प्याज का भाव क्या रहेगा? अभी बेचना चाहिए?",
        query_language=Language.HINDI,
        user_id="test_farmer_hi",
        location=Location(state="Maharashtra", district="Nashik", latitude=19.9975, longitude=73.7898)
    )
    
    print("\n🔄 Processing Hindi query for Onion with satellite data...")
    response_hi = await agent.process_query(query_hi)
    print(f"✅ Hindi Response: {response_hi.response_text}")
    print(f"🛰️ Satellite Enhanced: {response_hi.metadata.get('satellite_enhanced', False)}")
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

    # Test 4: Traditional analysis without location
    query_no_location = AgricultureQuery(
        query_text="Cotton market forecast please",
        query_language=Language.ENGLISH,
        user_id="test_farmer_basic"
    )
    print("\n🔄 Processing query without location (traditional analysis)...")
    response_basic = await agent.process_query(query_no_location)
    print(f"✅ Traditional Response: {response_basic.response_text}")
    print(f"🛰️ Satellite Enhanced: {response_basic.metadata.get('satellite_enhanced', False) if response_basic.metadata else False}")
    assert response_basic.confidence_score > 0.7

    # Test 5: Check satellite-enhanced forecast generation
    print("\n🔄 Testing satellite-enhanced forecast generation for Rice...")
    
    # Mock satellite data for testing
    from types import SimpleNamespace
    mock_satellite_data = SimpleNamespace()
    mock_satellite_data.metrics = SimpleNamespace()
    mock_satellite_data.metrics.ndvi = 0.75
    mock_satellite_data.metrics.soil_moisture = 45.0
    mock_satellite_data.metrics.temperature = 28.5
    mock_satellite_data.metrics.confidence_score = 0.9
    
    forecast = await agent._generate_satellite_enhanced_forecast(Commodity.RICE, mock_satellite_data)
    print(f"✅ Satellite Forecast for Rice:")
    print(f"   💰 Current Price: ₹{forecast.current_price}")
    print(f"   📈 7D Forecast: ₹{forecast.forecast_price_7d}")
    print(f"   📊 Environmental Score: {forecast.environmental_score}")
    print(f"   🌾 Yield Forecast: {forecast.yield_forecast} tonnes/ha")
    print(f"   ⚠️ Supply Risk: {forecast.supply_risk}")
    print(f"   🎯 Confidence: {forecast.confidence:.1%}")
    
    assert forecast.current_price > 0
    assert forecast.forecast_price_7d > 0
    assert forecast.environmental_score > 0
    assert forecast.yield_forecast > 0
    assert forecast.supply_risk in ["low", "moderate", "high", "very_high"]

    print("\n🎉 Satellite-Enhanced Market Timing Agent working successfully!")
    print("\n📊 Key Features Tested:")
    print("   ✅ Satellite-based yield forecasting")
    print("   ✅ Environmental risk assessment")
    print("   ✅ NDVI-enhanced price predictions")
    print("   ✅ Multilingual support with satellite data")
    print("   ✅ Graceful fallback to traditional analysis")
    print("   ✅ Supply-demand modeling with satellite insights")

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
    
    # Create BaseWorkerAgent class
    class BaseWorkerAgent:
        def __init__(self, name="base", capabilities=None, agent_type="base"):
            self.agent_id = f"{agent_type}_agent"
            self.name = name
            self.capabilities = capabilities or []
            self.agent_type = agent_type
        
        def execute(self, task, context):
            return {"error": "Base implementation"}
    
    base_agent_mock.BaseWorkerAgent = BaseWorkerAgent
    sys.modules['src.agents.base_agent'] = base_agent_mock
    
    # Mock models
    models_mock = types.ModuleType('src.core.models')
    
    class AgentCapability:
        ANALYSIS = "analysis"
        DATA_PROCESSING = "data_processing"
        PLANNING = "planning"
    
    class Task:
        def __init__(self, query=None):
            self.query = query
    
    models_mock.AgentCapability = AgentCapability
    models_mock.Task = Task
    sys.modules['src.core.models'] = models_mock
    
    # Mock satellite service
    satellite_service_mock = types.ModuleType('src.services.satellite_service')
    
    class MockSatelliteService:
        async def get_current_data(self, location_data):
            # Return mock satellite data
            from types import SimpleNamespace
            data = SimpleNamespace()
            data.metrics = SimpleNamespace()
            data.metrics.ndvi = 0.7 + (hash(location_data.location_name) % 100) / 1000  # Vary by location
            data.metrics.soil_moisture = 40 + (hash(location_data.region) % 30)
            data.metrics.temperature = 25 + (hash(location_data.location_name) % 15)
            data.metrics.confidence_score = 0.85 + (hash(location_data.region) % 15) / 100
            return data
    
    class LocationData:
        def __init__(self, latitude, longitude, location_name, region):
            self.latitude = latitude
            self.longitude = longitude
            self.location_name = location_name
            self.region = region
    
    satellite_service_mock.SatelliteService = MockSatelliteService
    satellite_service_mock.LocationData = LocationData
    sys.modules['src.services.satellite_service'] = satellite_service_mock
    
    # Set up module hierarchy
    sys.modules['..core'] = types.ModuleType('..core')
    sys.modules['..core.agriculture_models'] = agriculture_models_mock
    sys.modules['..services'] = types.ModuleType('..services')
    sys.modules['..services.satellite_service'] = satellite_service_mock
    
    asyncio.run(main())
