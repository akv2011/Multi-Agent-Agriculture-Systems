#!/usr/bin/env python3
"""
Simple test for irrigation agent process_query method
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agriculture_models import AgricultureQuery, Location
from src.agents.irrigation_agent import IrrigationAgent

async def test_irrigation_simple():
    """Simple test of irrigation agent"""
    print("💧 Simple Irrigation Agent Query Test")
    print("=" * 50)
    
    try:
        # Initialize the agent
        agent = IrrigationAgent()
        print(f"✅ Agent created: {agent.name}")
        
        # Test location
        test_location = Location(
            state="Maharashtra",
            district="Aurangabad",
            latitude=19.7515,
            longitude=75.7139
        )
        
        # Create simple query
        query = AgricultureQuery(
            query_id="test-irrigation-001",
            query_text="When should I irrigate cotton crop in Maharashtra?",
            location=test_location,
            context={
                "crop_type": "cotton",
                "growth_stage": "flowering",
                "soil_type": "black",
                "field_size": 5
            },
            query_type="irrigation",
            domain="irrigation"
        )
        
        print(f"📍 Location: {test_location.state}, {test_location.district}")
        print(f"📋 Query: {query.query_text}")
        print("\n" + "-" * 50)
        
        # Process the query
        print("Processing irrigation query...")
        response = await agent.process_query(query)
        
        print(f"\n✅ Status: {response.status}")
        print(f"🎯 Confidence: {response.confidence:.2%}")
        print(f"📚 Sources: {', '.join(response.sources)}")
        
        if hasattr(response, 'data') and response.data:
            print(f"\n📊 Response data available")
            
        print(f"\n⏱️  Processing completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_irrigation_simple())
    
    if success:
        print("\n🎉 Simple test passed!")
    else:
        print("\n💥 Test failed!")
