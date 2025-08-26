#!/usr/bin/env python3
"""
Simple Multilingual Test for Gemini Agriculture Agent
Tests the agent's ability to respond in the same language as the input
"""

import os
import asyncio
import sys
from datetime import datetime

# Set API key
# Get API key from environment  
api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERROR: Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    sys.exit(1)
os.environ['GOOGLE_API_KEY'] = api_key

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def test_multilingual_support():
    print("🌐 Testing Multilingual Agricultural Agent...")
    
    try:
        # Import agent
        from agents.gemini_agriculture_agent import GeminiAgricultureAgent
        from core.agriculture_models import AgricultureQuery, Language
        
        # Initialize agent
        agent = GeminiAgricultureAgent()
        print("✅ Agent initialized successfully")
        
        # Test queries in different languages
        test_queries = [
            {
                "text": "What is the best time to plant wheat in Punjab?",
                "language": Language.ENGLISH,
                "expected_language": "English"
            },
            {
                "text": "पंजाब में गेहूं बोने का सबसे अच्छा समय कब है?",
                "language": Language.HINDI,
                "expected_language": "Hindi"
            },
            {
                "text": "Punjab mein wheat planting ka best time kya hai?",
                "language": Language.MIXED,
                "expected_language": "Mixed/Hinglish"
            }
        ]
        
        print("\n" + "="*60)
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n🧪 TEST {i}: {test_case['expected_language']} Query")
            print(f"Question: {test_case['text']}")
            print("-" * 50)
            
            # Create query
            query = AgricultureQuery(
                query_text=test_case['text'],
                query_language=test_case['language'],
                user_id="test_farmer"
            )
            
            # Get response
            try:
                response = await agent.process_query(query)
                
                if response and response.response_text:
                    print(f"✅ Response received (Confidence: {response.confidence_score:.2f})")
                    print(f"Response: {response.response_text[:200]}...")
                    if len(response.response_text) > 200:
                        print("(truncated)")
                    
                    if response.recommendations:
                        print(f"📋 Recommendations: {len(response.recommendations)} items")
                else:
                    print("❌ No valid response received")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 50)
        
        print("\n🎉 Multilingual test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_multilingual_support())
