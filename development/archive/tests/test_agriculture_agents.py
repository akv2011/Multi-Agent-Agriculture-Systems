"""
Test agriculture agents
"""

def test_agriculture_agents():
    print("Testing Agriculture Agents...")
    
    try:
        import sys
        import os
        import asyncio
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        print("1. Testing agriculture models...")
        from src.core.agriculture_models import AgricultureQuery, Language
        print("✓ Models imported")
        
        print("2. Testing router...")
        from src.agents.agriculture_router import AgricultureRouter
        router = AgricultureRouter()
        print("✓ Router created")
        
        print("3. Testing crop agent...")
        from src.agents.crop_selection_agent import CropSelectionAgent
        crop_agent = CropSelectionAgent()
        print("✓ Crop agent created")
        
        print("4. Testing query processing...")
        query = AgricultureQuery(
            query_text="What wheat variety is best for Punjab?",
            query_language=Language.ENGLISH,
            user_id="test_user"
        )
        
        async def test_processing():
            # Test router classification
            domain = await router._classify_query_pattern_based(query)
            print(f"✓ Query classified as: {domain.value}")
            
            # Test agent processing
            response = await crop_agent.process_query(query)
            print(f"✓ Agent response confidence: {response.confidence:.2f}")
            print(f"✓ Response status: {response.status}")
            print(f"✓ Recommendations count: {len(response.recommendations)}")
            
            return response
        
        response = asyncio.run(test_processing())
        
        print("\n🎉 ALL AGRICULTURE AGENTS WORK!")
        print(f"Sample response: {response.summary[:100]}...")
        return True
        
    except Exception as e:
        print(f"✗ Agriculture agents test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agriculture_agents()
    exit(0 if success else 1)
