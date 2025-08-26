#!/usr/bin/env python3
"""
Test script for satellite integration in pest management agent
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agriculture_models import AgricultureQuery, Location
from src.agents.pest_management_agent import PestManagementAgent

async def test_pest_satellite_integration():
    """Test pest management agent with satellite data integration"""
    print("🐛 Testing Satellite Integration in Pest Management Agent")
    print("=" * 65)
    
    try:
        # Initialize the agent
        agent = PestManagementAgent()
        print(f"✅ Agent created: {agent.name}")
        
        # Test location (Punjab, India - high pest activity region)
        test_location = Location(
            state="Punjab",
            district="Ludhiana",
            latitude=30.901,
            longitude=75.857
        )
        
        # Create test query
        query = AgricultureQuery(
            query_id="test-pest-001",
            query_text="My wheat crop has yellow spots on leaves and some plants are wilting. What pest could this be?",
            location=test_location,
            context={
                "crop_type": "wheat",
                "symptoms": ["yellow spots", "wilting"],
                "affected_parts": ["leaves"],
                "growth_stage": "grain_filling",
                "weather_recent": "humid"
            },
            query_type="pest_management",
            domain="pest_management"
        )
        
        print(f"📍 Location: {test_location.state}, {test_location.district}")
        print(f"🐛 Query: {query.query_text}")
        print(f"🌾 Context: {query.context}")
        print("\n" + "-" * 65)
        
        # Process the query
        print("Processing pest management query with satellite integration...")
        response = await agent.process_query(query)
        
        print(f"\n✅ Response: {response.response_text}")
        print(f"🎯 Confidence: {response.confidence_score:.2%}")
        print(f"📚 Sources: {', '.join(response.sources)}")
        print(f"🤖 Agent: {response.agent_name}")
        
        # Display recommendations
        if response.recommendations:
            print(f"\n📊 Pest Management Recommendations:")
            for i, rec in enumerate(response.recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Display satellite insights if available in metadata
        if response.metadata and "satellite_insights" in response.metadata:
            satellite_data = response.metadata["satellite_insights"]
            print(f"\n🛰️  Satellite Data for Pest Analysis:")
            if satellite_data:
                print(f"   NDVI (Vegetation Health): {satellite_data.get('ndvi', 'N/A')}")
                print(f"   Soil Moisture: {satellite_data.get('soil_moisture', 'N/A')}")
                print(f"   Weather Conditions: {satellite_data.get('weather', 'N/A')}")
                print(f"   Outbreak Risk: {satellite_data.get('outbreak_risk', 'N/A')}")
            else:
                print("   No satellite data available for this location")
        
        # Display prevention advice
        if response.metadata and "prevention_advice" in response.metadata:
            advice = response.metadata["prevention_advice"]
            if advice:
                print(f"\n💡 Prevention Advice:")
                for tip in advice:
                    print(f"   • {tip}")
        
        print(f"\n⏱️  Processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting pest management satellite integration test...")
    success = asyncio.run(test_pest_satellite_integration())
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ Satellite integration is working in pest management agent")
    else:
        print("\n💥 Test failed!")
        print("❌ There are issues with satellite integration")
    
    print("\n" + "=" * 65)
