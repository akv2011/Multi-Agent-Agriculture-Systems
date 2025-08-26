#!/usr/bin/env python3
"""
Quick Ground Search Test

This script tests the ground search functionality with your current API keys.
It will work even without a Google Custom Search Engine by using Gemini directly.
"""

import os
import sys
import asyncio
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_gemini_direct():
    """Test Gemini API directly for agricultural queries"""
    print("🚀 Testing Gemini API for Agricultural Queries")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No Gemini API key found in environment")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Test queries
        test_queries = [
            "What is the current MSP (Minimum Support Price) for wheat in India for 2025?",
            "Best practices for organic farming in Maharashtra",
            "How to identify late blight disease in tomatoes?",
            "Government subsidies for drip irrigation systems in Karnataka"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 60)
            
            # Enhanced prompt for better agricultural responses
            prompt = f"""You are an expert agricultural advisor for Indian farmers with deep knowledge of:
- Current agricultural policies and MSP rates
- Crop cultivation practices across different Indian states
- Plant disease identification and treatment
- Government schemes and subsidies
- Market trends and farming technologies

Farmer's Question: {query}

Provide a detailed, practical response that includes:
1. Direct answer to the question
2. Specific details (numbers, dates, varieties, etc.)
3. Regional considerations for India
4. Actionable recommendations
5. Any relevant government schemes or policies

Be specific and factual. If you mention prices or dates, indicate the timeframe of your information."""

            try:
                response = model.generate_content(prompt)
                print(f"✅ Response: {response.text[:400]}...")
                print(f"📊 Response length: {len(response.text)} characters")
                
            except Exception as e:
                print(f"❌ Error generating response: {e}")
        
        print("\n🎉 Gemini API test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False

async def test_ground_search_service():
    """Test the ground search service"""
    print("\n🔍 Testing Ground Search Service")
    print("=" * 60)
    
    try:
        from src.services.ground_search_service import create_ground_search_service
        
        # Create service
        service = create_ground_search_service()
        
        # Test query
        query = "What is the current wheat MSP in India?"
        context = {
            "location": "Punjab, India",
            "crop_type": "wheat",
            "season": "rabi"
        }
        
        print(f"📝 Testing query: {query}")
        print(f"📍 Context: {context}")
        
        result = await service.ground_query(
            query=query,
            context=context,
            num_search_results=3
        )
        
        print(f"\n✅ Ground search completed!")
        print(f"📊 Confidence: {result.confidence_score}")
        print(f"📚 Sources: {len(result.sources)}")
        print(f"📝 Response preview: {result.content[:300]}...")
        
        if result.sources:
            print(f"\n🔗 Top sources:")
            for i, source in enumerate(result.sources[:3], 1):
                title = source.get('title', 'Unknown')
                link = source.get('link', 'No URL')
                print(f"  {i}. {title}")
                print(f"     {link}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ground search service: {e}")
        logger.exception("Ground search test error")
        return False

async def main():
    """Main test function"""
    print("🌾 AGRICULTURAL AI GROUND SEARCH TEST")
    print("=" * 80)
    
    # Test 1: Direct Gemini API
    gemini_success = await test_gemini_direct()
    
    # Test 2: Ground Search Service
    if gemini_success:
        ground_search_success = await test_ground_search_service()
    else:
        ground_search_success = False
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Gemini API: {'Working' if gemini_success else 'Failed'}")
    print(f"✅ Ground Search: {'Working' if ground_search_success else 'Failed'}")
    
    if gemini_success and ground_search_success:
        print("\n🎉 All tests passed! Your ground search is ready to use.")
        print("\nYou can now:")
        print("  1. Run: ./ground_search_example.py 'Your agricultural question'")
        print("  2. Run: ./test_ground_search_integration.py --agents crop --queries 1")
        print("  3. Integrate ground search into your agents")
    elif gemini_success:
        print("\n⚠️  Gemini works, but ground search needs Google Search CX setup.")
        print("   Run: python setup_google_search.py for detailed instructions")
    else:
        print("\n❌ Tests failed. Please check your API configuration.")
    
    return 0 if (gemini_success and ground_search_success) else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
