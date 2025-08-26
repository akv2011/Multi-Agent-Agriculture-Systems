"""
Simple test for Gemini Agriculture Agent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agriculture_models import AgricultureQuery, Language
from src.agents.gemini_agriculture_agent import GeminiAgricultureAgent
import asyncio

async def test_gemini_setup():
    print("🧪 Testing Gemini Agriculture Agent Setup...")
    
    try:
        # Test 1: Check if we can import everything
        print("1. ✓ All imports successful")
        
        # Test 2: Try to create agent (will show API key guidance if missing)
        print("2. Testing agent initialization...")
        
        try:
            agent = GeminiAgricultureAgent()
            print("✓ Gemini agent initialized successfully!")
            
            # Test 3: Get agent info
            info = agent.get_agent_info()
            print(f"✓ Agent Info: {info['agent_id']} using {info['model']}")
            
            # Test 4: Test a simple query
            print("3. Testing simple agriculture query...")
            
            query = AgricultureQuery(
                query_text="What is the best season to grow wheat in India?",
                query_language=Language.ENGLISH,
                user_id="test_setup"
            )
            
            response = await agent.process_query(query)
            
            if response.status == "completed":
                print(f"✓ Query processed successfully!")
                print(f"  - Confidence: {response.confidence:.2f}")
                print(f"  - Processing time: {response.processing_time:.2f}s")
                print(f"  - Response length: {len(response.response_text)} characters")
                print(f"  - Recommendations: {len(response.recommendations)}")
                print("🎉 Gemini Agriculture Agent is fully functional!")
                return True
            else:
                print(f"✗ Query failed: {response.response_text}")
                return False
                
        except ValueError as e:
            if "API key not found" in str(e):
                print("⚠️  Gemini API key not configured.")
                print("\nTo enable Gemini AI functionality:")
                print("1. Get your API key from: https://aistudio.google.com/apikey")
                print("2. Set environment variable: GOOGLE_API_KEY=your_api_key")
                print("3. Or create a .env file with: GOOGLE_API_KEY=your_api_key")
                print("\nThe system will work with basic functionality without Gemini.")
                return False
            else:
                raise e
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_setup())
    if success:
        print("\n✅ Gemini integration is ready!")
    else:
        print("\n⚠️  Gemini integration requires API key configuration")
    
    exit(0 if success else 1)
