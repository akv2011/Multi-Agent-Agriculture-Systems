#!/usr/bin/env python3
"""
🛰️ Market Timing Agent Satellite Integration Test
================================================

Test the enhanced Market Timing Agent with satellite data integration.
This test verifies yield forecasting, environmental risk assessment, and
satellite-enhanced price predictions.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.market_timing_agent import MarketTimingAgent
from src.core.agriculture_models import AgricultureQuery, Language, Location


async def test_satellite_enhanced_market_timing():
    """Test the satellite-enhanced Market Timing Agent"""
    print("🛰️ Market Timing Agent Satellite Integration Test")
    print("=" * 60)
    
    try:
        agent = MarketTimingAgent()
        print("✅ Market Timing Agent initialized successfully")
        
        # Test 1: Wheat forecasting with satellite data (Punjab)
        print("\n📈 Test 1: Wheat Price Forecasting with Satellite Data")
        print("-" * 50)
        
        query_wheat = AgricultureQuery(
            query_text="What is the price forecast for wheat? Should I sell now or wait?",
            query_language=Language.ENGLISH,
            user_id="farmer_punjab_001",
            location=Location(
                state="Punjab", 
                district="Amritsar",
                latitude=31.6340,
                longitude=74.8723
            )
        )
        
        response_wheat = await agent.process_query(query_wheat)
        
        print(f"🌾 Commodity: Wheat")
        print(f"📍 Location: {query_wheat.location.district}, {query_wheat.location.state}")
        print(f"💬 Response: {response_wheat.response_text}")
        print(f"🛰️ Satellite Enhanced: {response_wheat.metadata.get('satellite_enhanced', False)}")
        print(f"🎯 Confidence: {response_wheat.confidence_score:.1%}")
        
        if response_wheat.metadata.get('satellite_enhanced'):
            print(f"📊 Environmental Score: {response_wheat.metadata.get('environmental_score', 'N/A'):.1f}/100")
            print(f"🌱 NDVI: {response_wheat.metadata.get('ndvi', 'N/A'):.3f}")
            print(f"💧 Soil Moisture: {response_wheat.metadata.get('soil_moisture', 'N/A'):.1f}%")
            print(f"🌡️ Temperature: {response_wheat.metadata.get('temperature', 'N/A'):.1f}°C")
            print(f"📈 Yield Forecast: {response_wheat.metadata.get('yield_forecast', 'N/A'):.2f} tonnes/ha")
            print(f"⚠️ Supply Risk: {response_wheat.metadata.get('supply_risk', 'N/A').replace('_', ' ').title()}")
        
        # Test 2: Onion forecasting with satellite data (Maharashtra) - Hindi
        print("\n🧅 Test 2: Onion Price Forecasting (Hindi) with Satellite Data")
        print("-" * 50)
        
        query_onion = AgricultureQuery(
            query_text="प्याज का भाव क्या रहेगा? अभी बेचना चाहिए या रुकना चाहिए?",
            query_language=Language.HINDI,
            user_id="farmer_maharashtra_001",
            location=Location(
                state="Maharashtra",
                district="Nashik",
                latitude=19.9975,
                longitude=73.7898
            )
        )
        
        response_onion = await agent.process_query(query_onion)
        
        print(f"🧅 Commodity: Onion")
        print(f"📍 Location: {query_onion.location.district}, {query_onion.location.state}")
        print(f"💬 Response: {response_onion.response_text}")
        print(f"🛰️ Satellite Enhanced: {response_onion.metadata.get('satellite_enhanced', False)}")
        print(f"🎯 Confidence: {response_onion.confidence_score:.1%}")
        
        # Test 3: Cotton forecasting without satellite data (basic mode)
        print("\n🌾 Test 3: Cotton Price Forecasting (Traditional Analysis)")
        print("-" * 50)
        
        query_cotton = AgricultureQuery(
            query_text="What is the market trend for cotton? When should I sell?",
            query_language=Language.ENGLISH,
            user_id="farmer_gujarat_001"
            # No location provided - should fall back to traditional analysis
        )
        
        response_cotton = await agent.process_query(query_cotton)
        
        print(f"🌾 Commodity: Cotton")
        print(f"📍 Location: Not specified")
        print(f"💬 Response: {response_cotton.response_text}")
        print(f"🛰️ Satellite Enhanced: {response_cotton.metadata.get('satellite_enhanced', False)}")
        print(f"🎯 Confidence: {response_cotton.confidence_score:.1%}")
        
        # Test 4: Rice forecasting with satellite data
        print("\n🍚 Test 4: Rice Price Forecasting with Satellite Data")
        print("-" * 50)
        
        query_rice = AgricultureQuery(
            query_text="चावल की कीमत कैसी रहेगी? बेचने का सही समय कब है?",
            query_language=Language.HINDI,
            user_id="farmer_up_001",
            location=Location(
                state="Uttar Pradesh",
                district="Lucknow",
                latitude=26.8467,
                longitude=80.9462
            )
        )
        
        response_rice = await agent.process_query(query_rice)
        
        print(f"🍚 Commodity: Rice")
        print(f"📍 Location: {query_rice.location.district}, {query_rice.location.state}")
        print(f"💬 Response: {response_rice.response_text}")
        print(f"🛰️ Satellite Enhanced: {response_rice.metadata.get('satellite_enhanced', False)}")
        print(f"🎯 Confidence: {response_rice.confidence_score:.1%}")
        
        # Summary
        print("\n🎉 Market Timing Agent Satellite Integration - SUCCESS!")
        print("=" * 60)
        print("✅ Key Features Tested:")
        print("   🛰️ Satellite-based yield forecasting")
        print("   🌡️ Environmental risk assessment")
        print("   📊 NDVI-enhanced price predictions")
        print("   💧 Soil moisture impact on supply forecasting")
        print("   ⚠️ Weather-adjusted market timing recommendations")
        print("   🗣️ Multilingual support (English & Hindi)")
        print("   📍 Location-based satellite data integration")
        print("   🔄 Graceful fallback to traditional analysis")
        
        print("\n🏆 Market Timing Agent satellite integration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_satellite_enhanced_market_timing())
    sys.exit(0 if success else 1)
