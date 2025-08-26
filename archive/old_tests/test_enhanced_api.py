#!/usr/bin/env python3
"""
Test Script for Enhanced Agriculture API
Tests the comprehensive query processing and dashboard updates
"""

import requests
import json
import time

def test_enhanced_api():
    """Test the enhanced agriculture API"""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing Enhanced Agriculture API")
    print("=" * 50)
    
    # Test 1: Check API health
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{base_url}/demo/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health: {health_data['status']}")
            print(f"   System Components: {health_data['system_components']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Check dashboard metrics
    print("\n2. Testing Dashboard Metrics...")
    try:
        response = requests.get(f"{base_url}/demo/dashboard")
        if response.status_code == 200:
            dashboard_data = response.json()
            print(f"✅ Dashboard Data Retrieved")
            print(f"   Total Queries: {dashboard_data['total_queries_processed']}")
            print(f"   Success Rate: {dashboard_data['success_rate']:.2%}")
            print(f"   Avg Response Time: {dashboard_data['average_response_time']:.2f}s")
        else:
            print(f"❌ Dashboard check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # Test 3: Test system capabilities
    print("\n3. Testing System Capabilities...")
    try:
        response = requests.get(f"{base_url}/demo/capabilities")
        if response.status_code == 200:
            caps_data = response.json()
            print(f"✅ Capabilities Retrieved")
            print(f"   System: {caps_data['system_name']}")
            print(f"   Completion: {caps_data['completion_percentage']}%")
            print(f"   Agents: {len(caps_data['operational_agents'])}")
        else:
            print(f"❌ Capabilities check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Capabilities error: {e}")
    
    # Test 4: Test query processing with different languages
    test_queries = [
        {
            "query_text": "पंजाब में गेहूं की सबसे अच्छी किस्म कौन सी है?",
            "language": "hindi",
            "description": "Hindi crop selection query"
        },
        {
            "query_text": "Meri cotton crop mein पीले पत्ते दिख रहे हैं। Satellite data से क्या पता चल सकता है?",
            "language": "hinglish", 
            "description": "Hinglish disease identification with satellite request"
        },
        {
            "query_text": "When should I irrigate my wheat field? Current soil moisture is 30%.",
            "language": "english",
            "description": "English irrigation planning query"
        }
    ]
    
    print(f"\n4. Testing Query Processing ({len(test_queries)} queries)...")
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n   Test {i}: {test_query['description']}")
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/demo/query",
                json={
                    "query_text": test_query["query_text"],
                    "location": "punjab_ludhiana",
                    "include_satellite": True,
                    "priority_level": "normal"
                },
                headers={"Content-Type": "application/json"}
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Query processed successfully in {processing_time:.2f}s")
                print(f"      Status: {data['status']}")
                print(f"      Query ID: {data['query_id']}")
                print(f"      Language Detected: {data.get('query_analysis', {}).get('language', 'unknown')}")
                print(f"      Intent: {data.get('query_analysis', {}).get('intent', 'unknown')}")
                print(f"      Confidence: {data.get('confidence_metrics', {}).get('overall', 0):.2%}")
                print(f"      Processing Steps: {len(data.get('processing_timeline', []))}")
                print(f"      Agent Performance: {len(data.get('agent_performance', {}))}")
                
                # Check if we have a meaningful response
                answer = data.get('comprehensive_answer', {}).get('primary_response', '')
                if answer and len(answer) > 50:
                    print(f"      Response Preview: {answer[:100]}...")
                else:
                    print(f"      ⚠️ Response seems incomplete or missing")
                
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data}")
                except:
                    print(f"      Error: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    # Test 5: Test session info
    print("\n5. Testing Session Information...")
    try:
        response = requests.get(f"{base_url}/demo/session")
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Session Info Retrieved")
            print(f"   Session ID: {session_data['session_id']}")
            print(f"   Active Workflows: {session_data['active_workflows']}")
            print(f"   Total Queries: {session_data['total_queries_processed']}")
            print(f"   Demo Queries Available: {len(session_data['demo_queries'])}")
        else:
            print(f"❌ Session check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Session error: {e}")
    
    # Test 6: Test analytics
    print("\n6. Testing Analytics...")
    try:
        response = requests.get(f"{base_url}/demo/analytics")
        if response.status_code == 200:
            analytics_data = response.json()
            print(f"✅ Analytics Retrieved")
            print(f"   System Performance Available: {'system_performance' in analytics_data}")
            print(f"   Usage Patterns Available: {'usage_patterns' in analytics_data}")
            print(f"   Innovation Metrics Available: {'innovation_metrics' in analytics_data}")
        else:
            print(f"❌ Analytics check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Testing Complete!")
    print("\n💡 Next Steps:")
    print("   1. Start the enhanced API: python enhanced_demo_api.py")
    print("   2. Open frontend: http://localhost:8001/dashboard")
    print("   3. Test with sample queries")
    print("   4. Monitor real-time dashboard updates")
    
    return True

if __name__ == "__main__":
    print("Enhanced Agriculture API Tester")
    print("Make sure the API is running on localhost:8001")
    print("Press Enter to start testing...")
    input()
    
    test_enhanced_api()
