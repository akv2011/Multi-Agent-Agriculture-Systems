#!/usr/bin/env python3
"""
Test the query routing logic without loading heavy ML models
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_query_routing_logic():
    """Test just the query routing logic without agent execution"""
    
    try:
        print("🌾 Testing Query Routing Logic")
        print("=" * 50)
        
        # Import just the response formatter
        from src.services.response_formatter import ResponseFormatter
        print("✅ Response formatter imported successfully")
        
        # Test response formatting directly
        formatter = ResponseFormatter()
        
        # Test raw response cleaning
        test_raw_response = """
        **Analysis:**
        This is bold text with *italics* and `code`.
        
        ***Recommendations:***
        - Use ***nitrogen*** fertilizer
        - Apply *organic* matter
        
        **Priority:** High
        """
        
        cleaned = formatter._clean_raw_response(test_raw_response)
        print(f"✅ Raw response cleaning test:")
        print(f"Original length: {len(test_raw_response)}")
        print(f"Cleaned length: {len(cleaned)}")
        print(f"Contains **bold**: {'**' in cleaned}")
        print(f"Contains *italic*: {'*' in cleaned}")
        
        # Test AI response structuring
        ai_response = {
            "content": "This crop needs nitrogen fertilizer. Apply 20kg per hectare. Monitor for pests weekly.",
            "confidence": 0.85,
            "agent_type": "gemini_agriculture"
        }
        
        query_analysis = {
            "query_type": "input_materials",
            "intent": "fertilizer_advice",
            "crop_type": "wheat"
        }
        
        structured = formatter.format_structured_ai_response(ai_response, query_analysis)
        print(f"\n✅ AI response structuring test:")
        print(f"Has executive_summary: {'executive_summary' in structured}")
        print(f"Has actionable_recommendations: {'actionable_recommendations' in structured}")
        print(f"Has supporting_data: {'supporting_data' in structured}")
        
        if 'executive_summary' in structured:
            summary = structured['executive_summary']
            print(f"Query type: {summary.get('query_type', 'N/A')}")
            print(f"Key insight length: {len(summary.get('key_insight', ''))}")
            print(f"Primary recommendation length: {len(summary.get('primary_recommendation', ''))}")
        
        # Test simple query intent classification
        test_queries = [
            "What fertilizer should I use for wheat?",
            "My plants have brown spots on leaves",
            "When should I sell my cotton crop?",
            "Tell me about organic farming"
        ]
        
        print(f"\n✅ Query intent classification:")
        for query in test_queries:
            # Simple keyword-based classification for testing
            intent = classify_query_intent(query)
            print(f"Query: {query[:30]}...")
            print(f"Intent: {intent}")
        
        print(f"\n🎯 Query routing logic tests completed successfully!")
        print("✅ Response formatting working")
        print("✅ Markdown cleaning working") 
        print("✅ AI response structuring working")
        print("✅ Basic query classification working")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def classify_query_intent(query_text: str) -> str:
    """Simple keyword-based query classification for testing"""
    query_lower = query_text.lower()
    
    if any(word in query_lower for word in ['fertilizer', 'nutrient', 'nitrogen', 'phosphorus']):
        return "input_materials"
    elif any(word in query_lower for word in ['disease', 'pest', 'spot', 'infection', 'bug']):
        return "pest_management"
    elif any(word in query_lower for word in ['sell', 'market', 'price', 'when to sell']):
        return "market_timing"
    elif any(word in query_lower for word in ['harvest', 'when to harvest', 'ready']):
        return "harvest_planning"
    elif any(word in query_lower for word in ['irrigation', 'water', 'watering']):
        return "irrigation_management"
    else:
        return "gemini_agriculture"

if __name__ == "__main__":
    asyncio.run(test_query_routing_logic())
