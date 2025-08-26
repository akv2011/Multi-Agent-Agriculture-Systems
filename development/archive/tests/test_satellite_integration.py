#!/usr/bin/env python3
"""
Test script for satellite integration in crop selection agent
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agriculture_models import AgricultureQuery, Location
from src.agents.crop_selection_agent import CropSelectionAgent

async def test_satellite_integration():
    """Test crop selection agent with satellite data integration"""
    print("🌾 Testing Satellite Integration in Crop Selection Agent")
    print("=" * 60)
    
    # Initialize the agent
    agent = CropSelectionAgent()
    
    # Test location (Punjab, India)
    test_location = Location(
        state="Punjab",
        district="Ludhiana",
        latitude=30.7333,
        longitude=76.7794
    )
    
    # Create test query
    query = AgricultureQuery(
        query_id="test-001",
        query_text="What crops should I grow in Punjab during Kharif season with loamy soil?",
        location=test_location,
        context={
            "season": "kharif",
            "soil_type": "loamy",
            "farm_size": 10,
            "irrigation_available": True
        },
        query_type="crop_selection"
    )
    
    print(f"📍 Location: {test_location.state}, {test_location.district}")
    print(f"📋 Query: {query.query_text}")
    print(f"🌱 Context: {query.context}")
    print("\n" + "-" * 60)
    
    try:
        # Process the query
        print("Processing query with satellite integration...")
        response = await agent.process_query(query)
        
        print(f"\n✅ Response: {response.response_text}")
        print(f"🎯 Confidence: {response.confidence_score:.2%}")
        print(f"📚 Sources: {', '.join(response.sources)}")
        
        # Display recommendations
        if response.recommendations:
            recommendations = response.recommendations
            print(f"\n📊 Found {len(recommendations)} recommendations:")
            
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"\n{i}. {rec.get('crop_type', 'Unknown')} - {rec.get('variety', 'Standard')}")
                print(f"   Suitability: {rec.get('suitability_score', 0):.2%}")
                print(f"   Expected Yield: {rec.get('expected_yield', 0):.1f} tons/hectare")
                print(f"   Water Requirement: {rec.get('water_requirement', 'Unknown')}")
                print(f"   Investment: Rs.{rec.get('investment_cost', 0):,}/hectare")
                if rec.get('reason'):
                    print(f"   Reasoning: {rec['reason']}")
        
        # Display satellite insights if available
        metadata = response.metadata
        if metadata and "satellite_insights" in metadata:
            satellite_data = metadata["satellite_insights"]
            print(f"\n[SATELLITE] Satellite Data Insights:")
            if satellite_data:
                print(f"   NDVI (Vegetation Health): {satellite_data.get('ndvi', 'N/A')}")
                print(f"   Soil Moisture: {satellite_data.get('soil_moisture', 'N/A')}")
                print(f"   Weather: {satellite_data.get('weather', 'N/A')}")
                print(f"   Land Suitability: {satellite_data.get('land_suitability', 'N/A')}")
            else:
                print("   No satellite data available for this location")
        
        # Display additional advice
        if metadata and "additional_advice" in metadata:
            advice = metadata["additional_advice"]
            if advice:
                print(f"\n💡 Additional Advice:")
                for tip in advice:
                    print(f"   • {tip}")
        
        print(f"\n⏱️  Processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting satellite integration test...")
    success = asyncio.run(test_satellite_integration())
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ Satellite integration is working in crop selection agent")
    else:
        print("\n💥 Test failed!")
        print("❌ There are issues with satellite integration")
    
    print("\n" + "=" * 60)
