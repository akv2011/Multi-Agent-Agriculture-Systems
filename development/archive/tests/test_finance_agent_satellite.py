#!/usr/bin/env python3
"""
Test Finance Policy Agent with Satellite Integration
Tests the enhanced finance agent's satellite-based risk assessment capabilities
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.finance_policy_agent import FinancePolicyAgent
from src.core.agriculture_models import (
    AgricultureQuery, CropType, SoilType, Location, 
    FarmProfile, Language
)


async def test_finance_agent_satellite_integration():
    """Test finance agent with satellite-enhanced loan assessment"""
    print("🚀 Testing Finance Policy Agent with Satellite Integration")
    print("=" * 60)
    
    try:
        # Initialize agent
        agent = FinancePolicyAgent()
        print(f"✅ Agent initialized: {agent.agent_id}")
        print(f"📡 Satellite integrator ready: {agent.satellite_integrator is not None}")
        
        # Create test query for loan eligibility
        test_query = AgricultureQuery(
            query_text="मुझे ट्रैक्टर खरीदने के लिए 5 लाख का लोन चाहिए। मैं योग्य हूं?",
            query_language=Language.MIXED,
            user_id="test_farmer_finance",
            location=Location(state="Punjab", district="Ludhiana"),
            farm_profile=FarmProfile(
                farm_id="test_finance_001",
                farmer_name="Satellite Test Farmer",
                location=Location(state="Punjab", district="Ludhiana"),
                total_area=5.0,
                soil_type=SoilType.ALLUVIAL,
                current_crops=[CropType.WHEAT],
                irrigation_type="tube_well",
                farm_type="small"
            )
        )
        
        print(f"📋 Test Query: {test_query.query_text}")
        print(f"📍 Location: {test_query.location.state}, {test_query.location.district}")
        
        # Process query with satellite enhancement
        print("\n🔄 Processing loan query with satellite analysis...")
        response = await agent.process_query(test_query)
        
        # Display results
        print("\n✅ FINANCE AGENT RESPONSE:")
        print(f"Agent: {response.agent_name}")
        print(f"Confidence: {response.confidence_score:.2f}")
        print(f"Satellite Enhanced: {response.metadata.get('satellite_enhanced', False)}")
        print(f"Environmental Risk: {response.metadata.get('environmental_risk_level', 'N/A')}")
        
        print(f"\n📄 Response Summary:")
        print(response.response_text[:300] + "..." if len(response.response_text) > 300 else response.response_text)
        
        print(f"\n💡 Sources: {', '.join(response.sources)}")
        
        if response.recommendations:
            print(f"\n🔧 Recommendations ({len(response.recommendations)}):")
            for i, rec in enumerate(response.recommendations[:3], 1):
                if isinstance(rec, dict):
                    print(f"  {i}. {rec.get('title', 'General')}: {rec.get('description', str(rec))}")
                else:
                    print(f"  {i}. {str(rec)}")
        
        # Test execute method compatibility
        print("\n🧪 Testing execute method compatibility...")
        
        from src.core.models import Task, TaskStatus
        
        # Create a simple task
        task = type('Task', (), {
            'query': test_query,
            'status': TaskStatus.PENDING
        })()
        
        context = {'query': test_query}
        result = agent.execute(task, context)
        
        print(f"✅ Execute method result: {result['status']}")
        print(f"🛰️ Satellite Enhanced: {result.get('satellite_enhanced', False)}")
        
        print("\n🎉 Finance Policy Agent satellite integration test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing finance agent: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_finance_agent_satellite_integration())
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
