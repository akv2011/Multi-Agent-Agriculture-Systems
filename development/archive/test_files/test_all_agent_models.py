#!/usr/bin/env python3
"""
Comprehensive Agent Model Integration Test
Tests all agents that use AgriSens models to ensure they're working properly.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Any
from datetime import datetime
import traceback

# Setup environment
sys.path.append('/home/hari/Music/Multi-Agent-Agriculture-Systems')
os.chdir('/home/hari/Music/Multi-Agent-Agriculture-Systems')

# Import agents and models
from src.core.agriculture_models import (
    AgricultureQuery, Location, FarmProfile, CropType, SoilType, SeasonType, QueryDomain
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AgentModelTester:
    """Comprehensive tester for all agents with models"""
    
    def __init__(self):
        self.test_results = {}
        self.sample_location = Location(
            latitude=28.6139,  # New Delhi
            longitude=77.2090,
            state="Delhi",
            district="New Delhi",
            village="Central Delhi"
        )
        self.sample_farm = FarmProfile(
            farm_id="test_farm_001",
            farmer_name="Test Farmer",
            location=self.sample_location,
            total_area=2.5,  # acres
            soil_type=SoilType.LOAMY,
            current_crops=[CropType.WHEAT],
            irrigation_type="drip",
            farm_type="small"
        )
    
    async def test_crop_selection_agent(self):
        """Test Crop Selection Agent with AgriSens model"""
        print("\n🌾 Testing Crop Selection Agent...")
        try:
            from src.agents.crop_selection_agent import CropSelectionAgent
            
            agent = CropSelectionAgent()
            
            query = AgricultureQuery(
                text="What crop should I grow this rabi season? I have loamy soil.",
                domain=QueryDomain.CROP_SELECTION,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "season": "rabi",
                    "soil_data": {
                        "nitrogen": 45.0,
                        "phosphorus": 23.0,
                        "potassium": 55.0,
                        "ph": 6.8,
                        "organic_matter": 3.2,
                        "moisture_content": 18.5
                    }
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["crop_selection"] = {
                "status": "✅ PASS",
                "has_model": True,
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Crop Selection Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["crop_selection"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Crop Selection Agent: {str(e)}")
    
    async def test_disease_identification_agent(self):
        """Test Disease Identification Agent"""
        print("\n🦠 Testing Disease Identification Agent...")
        try:
            from src.agents.disease_identification_agent import DiseaseIdentificationAgent
            
            agent = DiseaseIdentificationAgent()
            
            query = AgricultureQuery(
                text="My wheat crop has yellow spots on leaves. What disease could this be?",
                domain=QueryDomain.DISEASE_PEST_MANAGEMENT,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "crop_type": "wheat",
                    "symptoms": ["yellow spots", "leaf discoloration"],
                    "affected_area": "leaves"
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["disease_identification"] = {
                "status": "✅ PASS",
                "has_model": True,
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Disease Identification Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["disease_identification"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Disease Identification Agent: {str(e)}")
    
    async def test_irrigation_agent(self):
        """Test Irrigation Agent with AgriSens model"""
        print("\n💧 Testing Irrigation Agent...")
        try:
            from src.agents.irrigation_agent import IrrigationAgent
            
            agent = IrrigationAgent()
            
            query = AgricultureQuery(
                text="When should I water my wheat crop? Current soil moisture is low.",
                domain=QueryDomain.IRRIGATION_WATER_MANAGEMENT,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "crop_type": "wheat",
                    "soil_moisture": 15.0,
                    "weather_forecast": {"temperature": 25, "humidity": 60, "wind_speed": 10}
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["irrigation"] = {
                "status": "✅ PASS", 
                "has_model": True,
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Irrigation Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["irrigation"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Irrigation Agent: {str(e)}")
    
    async def test_fertilizer_agent(self):
        """Test Fertilizer Recommendation Agent"""
        print("\n🧪 Testing Fertilizer Recommendation Agent...")
        try:
            from src.agents.fertilizer_recommendation_agent import FertilizerRecommendationAgent
            
            agent = FertilizerRecommendationAgent()
            
            query = AgricultureQuery(
                text="What fertilizer should I use for my rice crop based on soil test?",
                domain=QueryDomain.FERTILIZER_SOIL_MANAGEMENT,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "crop_type": "rice",
                    "soil_data": {
                        "nitrogen": 35.0,
                        "phosphorus": 18.0,
                        "potassium": 42.0,
                        "ph": 6.5,
                        "organic_matter": 2.8
                    }
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["fertilizer"] = {
                "status": "✅ PASS",
                "has_model": True,
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Fertilizer Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["fertilizer"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Fertilizer Agent: {str(e)}")
    
    async def test_market_timing_agent(self):
        """Test Market Timing Agent"""
        print("\n📈 Testing Market Timing Agent...")
        try:
            from src.agents.market_timing_agent import MarketTimingAgent
            
            agent = MarketTimingAgent()
            
            query = AgricultureQuery(
                text="When is the best time to sell my wheat crop for maximum profit?",
                domain=QueryDomain.MARKET_FINANCIAL_PLANNING,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "crop_type": "wheat",
                    "harvest_ready": True,
                    "current_price": 2100,
                    "storage_capacity": "limited"
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["market_timing"] = {
                "status": "✅ PASS",
                "has_model": True,
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Market Timing Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["market_timing"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Market Timing Agent: {str(e)}")
    
    async def test_harvest_planning_agent(self):
        """Test Harvest Planning Agent"""
        print("\n🌾 Testing Harvest Planning Agent...")
        try:
            from src.agents.harvest_planning_agent import HarvestPlanningAgent
            
            agent = HarvestPlanningAgent()
            
            query = AgricultureQuery(
                text="When should I harvest my rice crop? It was planted 90 days ago.",
                domain=QueryDomain.HARVEST_POST_HARVEST,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "crop_type": "rice",
                    "planting_date": "2024-11-01",
                    "variety": "basmati",
                    "current_stage": "grain_filling"
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["harvest_planning"] = {
                "status": "✅ PASS",
                "has_model": True,
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Harvest Planning Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["harvest_planning"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Harvest Planning Agent: {str(e)}")
    
    async def test_weather_forecast_agent(self):
        """Test Weather Forecast Agent"""
        print("\n🌤️ Testing Weather Forecast Agent...")
        try:
            from src.agents.weather_forecast_agent import WeatherForecastAgent
            
            agent = WeatherForecastAgent()
            
            query = AgricultureQuery(
                text="What's the weather forecast for the next 7 days? Will it affect my cotton crop?",
                domain=QueryDomain.WEATHER_CLIMATE,
                location=self.sample_location,
                farm_profile=self.sample_farm,
                context={
                    "crop_type": "cotton",
                    "growth_stage": "flowering",
                    "forecast_days": 7
                }
            )
            
            response = await agent.process_query(query)
            
            self.test_results["weather_forecast"] = {
                "status": "✅ PASS",
                "has_model": False,  # Weather agent uses API, not ML model
                "response_length": len(response.content),
                "confidence": response.confidence
            }
            print(f"✅ Weather Forecast Agent: Working (confidence: {response.confidence})")
            print(f"   Response preview: {response.content[:100]}...")
            
        except Exception as e:
            self.test_results["weather_forecast"] = {
                "status": "❌ FAIL",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ Weather Forecast Agent: {str(e)}")
    
    async def run_all_tests(self):
        """Run all agent tests"""
        print("🚀 Starting Comprehensive Agent Model Integration Tests")
        print("=" * 60)
        
        # Test all agents
        await self.test_crop_selection_agent()
        await self.test_disease_identification_agent()
        await self.test_irrigation_agent()
        await self.test_fertilizer_agent()
        await self.test_market_timing_agent()
        await self.test_harvest_planning_agent()
        await self.test_weather_forecast_agent()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 AGENT MODEL INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        total_agents = len(self.test_results)
        passed_agents = sum(1 for result in self.test_results.values() if "✅" in result["status"])
        failed_agents = total_agents - passed_agents
        
        print(f"Total Agents Tested: {total_agents}")
        print(f"✅ Passed: {passed_agents}")
        print(f"❌ Failed: {failed_agents}")
        print(f"Success Rate: {(passed_agents/total_agents)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for agent_name, result in self.test_results.items():
            model_indicator = "🤖" if result.get("has_model", False) else "🌐"
            print(f"{model_indicator} {agent_name.replace('_', ' ').title()}: {result['status']}")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        print("\n🤖 = Uses AgriSens ML Model")
        print("🌐 = Uses API/External Service")
        
        # Failed tests details
        failed_tests = {k: v for k, v in self.test_results.items() if "❌" in v["status"]}
        if failed_tests:
            print("\n🔍 FAILED TESTS DETAILS:")
            for agent_name, result in failed_tests.items():
                print(f"\n❌ {agent_name.replace('_', ' ').title()}:")
                print(f"   Error: {result['error']}")
                if "traceback" in result:
                    print(f"   Traceback: {result['traceback'][:300]}...")
        
        print("\n" + "=" * 60)

async def main():
    """Main test function"""
    tester = AgentModelTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
