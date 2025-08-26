#!/usr/bin/env python3
"""
Test script for AgriSens model integration in harvest planning agent
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.agriculture_models import AgricultureQuery, Location, CropType
from src.agents.harvest_planning_agent import HarvestPlanningAgent
from src.models.agrisens_harvest_planning import get_agrisens_harvest_model

async def test_harvest_planning_integration():
    """Test harvest planning agent with AgriSens model integration"""
    print("🌾 Testing AgriSens Model Integration in Harvest Planning Agent")
    print("=" * 70)
    
    try:
        # Initialize the agent
        agent = HarvestPlanningAgent()
        print(f"✅ Agent created: {agent.name}")
        
        # Test location (Punjab, India - major agricultural region)
        test_location = Location(
            state="Punjab",
            district="Ludhiana",
            latitude=30.901,
            longitude=75.857
        )
        
        # Create test query for wheat crop
        wheat_query = AgricultureQuery(
            query_id="test-harvest-001",
            query_text="When should I harvest my wheat crop? It was planted about 4 months ago.",
            location=test_location,
            context={
                "crop_type": "wheat",
                "crop_variety": "HD-3086",
                "growth_stage": "grain_filling",
                "field_size": 8.5,
                "has_mechanized_equipment": True
            },
            query_type="harvest_planning",
            domain="harvest_planning"
        )
        
        print(f"📍 Location: {test_location.state}, {test_location.district}")
        print(f"🌾 Query: {wheat_query.query_text}")
        print(f"🌱 Context: {wheat_query.context}")
        print("\n" + "-" * 70)
        
        # Process query
        print("Processing wheat harvest query...")
        wheat_response = await agent.process_query(wheat_query)
        print("\n🔍 RESPONSE FOR WHEAT:")
        print(wheat_response.response_text)
        print("\n📊 Confidence:", wheat_response.confidence)
        print("📋 Metadata:", wheat_response.metadata)
        
        # Verify if we're getting actual model data
        if "days_to_harvest" in wheat_response.metadata:
            days = wheat_response.metadata["days_to_harvest"]
            print(f"✅ Model integration successful: {days} days to harvest")
        else:
            print("❌ Missing harvest days metadata - model may not be integrated properly")
            
        print("\n" + "-" * 70)
        
        # Create test query for rice crop
        rice_query = AgricultureQuery(
            query_id="test-harvest-002",
            query_text="My rice field looks like it's almost ready for harvest. When is the best time to harvest?",
            location=test_location,
            context={
                "crop_type": "rice",
                "crop_variety": "basmati",
                "growth_stage": "maturity",
                "field_size": 5.0,
                "has_mechanized_equipment": False
            },
            query_type="harvest_planning",
            domain="harvest_planning"
        )
        
        print("Processing rice harvest query...")
        rice_response = await agent.process_query(rice_query)
        print("\n🔍 RESPONSE FOR RICE:")
        print(rice_response.response_text)
        print("\n📊 Confidence:", rice_response.confidence)
        print("📋 Metadata:", rice_response.metadata)
        
        # Check if model initialization worked properly
        harvest_model = get_agrisens_harvest_model()
        print(f"\n🔧 AgriSens Harvest Model has {len(harvest_model.crop_maturity_models)} crop models loaded")
        
        # Test satellite data integration mention
        if "satellite" in rice_response.response_text.lower():
            print("✅ Satellite data integration detected in response")
        else:
            print("⚠️ No satellite data integration detected in response")
            
        print("\n" + "-" * 70)
        print("✅ Harvest Planning Agent Integration Test Complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_harvest_planning_integration())
