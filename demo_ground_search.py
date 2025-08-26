#!/usr/bin/env python3
"""
Simple Ground Search Demo

This script demonstrates the ground search functionality working with agricultural queries
using just the Gemini API from your .env file.
"""

import os
import sys
import asyncio
import time

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.ground_search_service import create_ground_search_service

# Sample agricultural queries to test
SAMPLE_QUERIES = [
    {
        "query": "What crops are suitable for growing in alkaline soil in Maharashtra?",
        "context": {"location": "Maharashtra, India", "soil_type": "alkaline", "season": "kharif"}
    },
    {
        "query": "How to identify and treat powdery mildew on wheat?",
        "context": {"crop_type": "wheat", "disease": "powdery mildew", "location": "Punjab, India"}
    },
    {
        "query": "Current subsidies for drip irrigation in Karnataka 2025",
        "context": {"location": "Karnataka, India", "irrigation_type": "drip", "scheme": "government subsidy"}
    },
    {
        "query": "Best time to sell sugarcane crop for maximum profit",
        "context": {"crop_type": "sugarcane", "location": "Uttar Pradesh, India", "objective": "profit maximization"}
    },
    {
        "query": "Organic certification process for small farmers in India",
        "context": {"farming_type": "organic", "farmer_category": "small", "location": "India"}
    }
]

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}")

def print_query_result(i, query_data, result, execution_time):
    """Print the result of a query in a formatted way"""
    print(f"\n🌾 QUERY {i}: {query_data['query']}")
    print(f"📍 Context: {query_data['context']}")
    print(f"⏱️  Time: {execution_time:.2f}s | 📊 Confidence: {result.confidence_score:.2f} | 📚 Sources: {len(result.sources)}")
    print("-" * 80)
    
    # Print response (truncated if too long)
    response_text = result.content
    if len(response_text) > 600:
        print(f"{response_text[:600]}...")
        print(f"\n[Response truncated - full length: {len(response_text)} characters]")
    else:
        print(response_text)
    
    # Print sources
    if result.sources:
        print(f"\n📚 Sources:")
        for j, source in enumerate(result.sources[:3], 1):  # Show top 3 sources
            title = source.get('title', 'Unknown Source')
            link = source.get('link', 'No URL')
            print(f"  {j}. {title}")
            if link != 'No URL':
                print(f"     {link}")

async def run_demo():
    """Run the ground search demo"""
    print_header("Agricultural Ground Search Demo")
    print("This demo tests the ground search functionality with real agricultural queries.")
    print("Using Gemini API from your .env file for intelligent agricultural responses.")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ No Gemini API key found in .env file!")
        print("Please ensure GEMINI_API_KEY is set in your .env file.")
        return 1
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Create ground search service
    try:
        service = create_ground_search_service()
        print("✅ Ground search service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize ground search service: {e}")
        return 1
    
    # Test each query
    results = []
    total_start_time = time.time()
    
    for i, query_data in enumerate(SAMPLE_QUERIES, 1):
        try:
            start_time = time.time()
            
            result = await service.ground_query(
                query=query_data["query"],
                context=query_data["context"],
                num_search_results=3
            )
            
            execution_time = time.time() - start_time
            results.append({
                "query": query_data["query"],
                "success": True,
                "confidence": result.confidence_score,
                "sources": len(result.sources),
                "time": execution_time,
                "response_length": len(result.content)
            })
            
            print_query_result(i, query_data, result, execution_time)
            
        except Exception as e:
            print(f"\n❌ QUERY {i} FAILED: {query_data['query']}")
            print(f"Error: {e}")
            results.append({
                "query": query_data["query"],
                "success": False,
                "error": str(e)
            })
    
    total_time = time.time() - total_start_time
    
    # Print summary
    print_header("Demo Summary")
    
    successful_queries = [r for r in results if r.get("success", False)]
    failed_queries = [r for r in results if not r.get("success", False)]
    
    print(f"📊 Total Queries: {len(SAMPLE_QUERIES)}")
    print(f"✅ Successful: {len(successful_queries)}")
    print(f"❌ Failed: {len(failed_queries)}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    
    if successful_queries:
        avg_confidence = sum(r["confidence"] for r in successful_queries) / len(successful_queries)
        avg_time = sum(r["time"] for r in successful_queries) / len(successful_queries)
        avg_sources = sum(r["sources"] for r in successful_queries) / len(successful_queries)
        avg_length = sum(r["response_length"] for r in successful_queries) / len(successful_queries)
        
        print(f"📈 Average Confidence: {avg_confidence:.2f}")
        print(f"📈 Average Response Time: {avg_time:.2f}s")
        print(f"📈 Average Sources: {avg_sources:.1f}")
        print(f"📈 Average Response Length: {avg_length:.0f} characters")
    
    if failed_queries:
        print(f"\n❌ Failed Queries:")
        for r in failed_queries:
            print(f"  - {r['query']}: {r.get('error', 'Unknown error')}")
    
    print(f"\n🎉 Demo completed! Your ground search system is {'working well' if len(successful_queries) >= 4 else 'partially working'}.")
    
    if len(successful_queries) >= 4:
        print("\n✨ Next steps:")
        print("  1. Set up Google Custom Search for even better results")
        print("  2. Integrate ground search into your agents")
        print("  3. Use ground search for real-time agricultural queries")
    
    return 0 if len(successful_queries) >= 4 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(run_demo()))
