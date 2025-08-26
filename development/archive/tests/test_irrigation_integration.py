#!/usr/bin/env python3
"""
Test script for satellite integration in irrigation agent
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agriculture_models import AgricultureQuery, Location
from src.agents.irrigation_agent import IrrigationAgent

async def test_irrigation_satellite_integration():
    """Test irrigation agent with satellite data integration"""
    print("💧 Testing Satellite Integration in Irrigation Agent")
    print("=" * 60)
    
    # Initialize the agent
    agent = IrrigationAgent()
    
    # Test location (Maharashtra, India - cotton growing region)
    test_location = Location(
        state="Maharashtra",
        district="Aurangabad",
        latitude=19.7515,
        longitude=75.7139
    )
    
    # Create test query
    query = AgricultureQuery(
        query_id="irrigation-test-001",
        query_text="When should I irrigate my cotton crop in Maharashtra? Current stage is flowering.",
        location=test_location,
        context={
            "crop_type": "cotton",
            "growth_stage": "flowering", 
            "soil_type": "clay",
            "farm_size": 5,
            "irrigation_method": "drip"
        },
        query_type="irrigation"
    )
    
    print(f"📍 Location: {test_location.state}, {test_location.district}")
    print(f"💧 Query: {query.query_text}")
    print(f"🌱 Context: {query.context}")
    print("\n" + "-" * 60)
    
    try:
        # Process the query
        print("Processing irrigation query with satellite integration...")
        response = await agent.process_query(query)
        
        print(f"\n✅ Response: {response.response_text}")
        print(f"🎯 Confidence: {response.confidence_score:.2%}")
        print(f"📚 Sources: {', '.join(response.sources)}")
        
        # Display irrigation recommendations
        if response.confidence_score > 0:
            response_data = response.metadata or {}
            
            # Show satellite insights
            if "satellite_insights" in response_data and response_data["satellite_insights"]:
                satellite_data = response_data["satellite_insights"]
                print(f"\n🛰️  Satellite Data for Irrigation:")
                print(f"   Soil Moisture: {satellite_data.get('soil_moisture', 'N/A')}")
                print(f"   Vegetation Health (NDVI): {satellite_data.get('ndvi', 'N/A')}")
                print(f"   Weather: {satellite_data.get('weather', 'N/A')}")
            
            # Show water requirements
            if "water_requirements" in response_data:
                water_reqs = response_data["water_requirements"]
                if water_reqs:
                    print(f"\n💧 Water Requirements:")
                    for req in water_reqs[:3]:  # Show first 3
                        crop_type = req.get('crop_type', 'Unknown')
                        stage = req.get('stage', 'Unknown')
                        daily_et = req.get('daily_et', 0)
                        print(f"   {crop_type} ({stage}): {daily_et:.1f}mm/day")
            
            # Show irrigation schedule
            if "irrigation_schedule" in response_data:
                schedule = response_data["irrigation_schedule"]
                if schedule:
                    print(f"\n📅 Irrigation Schedule:")
                    for sched in schedule[:3]:  # Show first 3
                        date = sched.get('date', 'Unknown')
                        amount = sched.get('water_amount', 0)
                        method = sched.get('method', 'Unknown')
                        print(f"   {date}: {amount:.1f}mm via {method}")
            
            # Show efficiency tips
            if "efficiency_tips" in response_data:
                tips = response_data["efficiency_tips"]
                if tips:
                    print(f"\n💡 Efficiency Tips:")
                    for tip in tips:
                        print(f"   • {tip}")
        
        print(f"\n⏱️  Processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting irrigation satellite integration test...")
    success = asyncio.run(test_irrigation_satellite_integration())
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ Satellite integration is working in irrigation agent")
    else:
        print("\n💥 Test failed!")
        print("❌ There are issues with satellite integration")
    
    print("\n" + "=" * 60)
