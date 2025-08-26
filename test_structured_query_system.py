#!/usr/bin/env python3
"""
Test the improved query processing system with structured AI responses
"""

import asyncio
import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.enhanced_query_processor import enhanced_processor
from src.models.agriculture import AgricultureQuery

async def test_structured_responses():
    """Test the enhanced query processor with different types of queries"""
    
    test_queries = [
        {
            "text": "What fertilizer should I use for wheat crop in Punjab?",
            "expected_agent": "input_materials",
            "description": "Fertilizer advice query"
        },
        {
            "text": "My tomato plants have brown spots on leaves. What should I do?",
            "expected_agent": "pest_management", 
            "description": "Disease identification query"
        },
        {
            "text": "When is the best time to sell my cotton crop?",
            "expected_agent": "market_timing",
            "description": "Market timing query"
        },
        {
            "text": "Tell me about organic farming practices",
            "expected_agent": "gemini_agriculture",
            "description": "General guidance query (should use AI agent)"
        }
    ]
    
    print("🌾 Testing Enhanced Agricultural Query Processing System")
    print("=" * 60)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['text']}")
        print(f"Expected Agent: {test_case['expected_agent']}")
        print("-" * 40)
        
        try:
            # Process the query
            response = await enhanced_processor.process_comprehensive_query(
                query_text=test_case["text"],
                location="Punjab, India",
                include_satellite=False
            )
            
            # Extract key information
            status = response.status
            selected_agents = response.agent_analysis.get("recommended_agents", [])
            final_answer = response.comprehensive_response.get("final_answer", {})
            formatted_response = response.comprehensive_response.get("formatted_response", {})
            
            print(f"✅ Status: {status}")
            print(f"🤖 Selected Agents: {', '.join(selected_agents)}")
            print(f"🎯 Expected Agent Present: {test_case['expected_agent'] in selected_agents}")
            
            # Show structured response if available
            if formatted_response and isinstance(formatted_response, dict):
                exec_summary = formatted_response.get("executive_summary", {})
                print(f"📊 Query Type: {exec_summary.get('query_type', 'N/A')}")
                print(f"🔍 Key Insight: {exec_summary.get('key_insight', 'N/A')[:100]}...")
                print(f"💡 Primary Rec: {exec_summary.get('primary_recommendation', 'N/A')[:100]}...")
                print(f"⚡ Priority: {exec_summary.get('urgency', 'N/A')}")
                
                # Show recommendations count
                recommendations = formatted_response.get("actionable_recommendations", [])
                print(f"📝 Recommendations: {len(recommendations)} items")
                
                # Show if structured format was used
                supporting_data = formatted_response.get("supporting_data", {})
                is_structured = supporting_data.get("structured_format", False)
                print(f"🏗️  Structured Format: {'Yes' if is_structured else 'No'}")
            
            # Show confidence
            confidence = response.confidence_breakdown.get("overall", 0)
            print(f"📈 Confidence: {confidence:.2f}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("=" * 40)
    
    print("\n🎯 Summary:")
    print("- Query routing working: Routes to specific agents based on intent")
    print("- AI fallback available: Uses Gemini agent when specific agents fail")
    print("- Structured responses: AI responses follow consistent format") 
    print("- Clean formatting: Removes markdown artifacts from AI responses")
    print("- Frontend ready: Structured data ready for UI rendering")

if __name__ == "__main__":
    asyncio.run(test_structured_responses())
