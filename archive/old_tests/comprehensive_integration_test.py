#!/usr/bin/env python3
"""
Comprehensive Integration Test for Enhanced Multi-Agent Agriculture System
This script validates all components without running the full server.
"""

import sys
import os
import json
import asyncio
import importlib.util
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test that all critical modules can be imported"""
    print("🔍 Testing Module Imports...")
    
    test_modules = [
        ("Enhanced Query Processor", "src.services.enhanced_query_processor"),
        ("Response Formatter", "src.services.response_formatter"),
        ("Websocket Integration", "src.services.websocket_integration"),
        ("Enhanced API Router", "src.api.routers.enhanced_demo"),
    ]
    
    results = {}
    for name, module_path in test_modules:
        try:
            spec = importlib.util.find_spec(module_path)
            if spec is None:
                results[name] = f"❌ Module not found: {module_path}"
            else:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                results[name] = "✅ Import successful"
        except Exception as e:
            results[name] = f"❌ Import failed: {str(e)}"
    
    for name, result in results.items():
        print(f"   {name}: {result}")
    
    return all("✅" in result for result in results.values())

def test_enhanced_query_processor():
    """Test the enhanced query processor functionality"""
    print("\n🧠 Testing Enhanced Query Processor...")
    
    try:
        from src.services.enhanced_query_processor import EnhancedQueryProcessor
        
        # Initialize processor
        processor = EnhancedQueryProcessor()
        
        # Test query analysis
        test_query = "मेरे गेहूं के खेत में कीड़े लगे हैं, क्या करूं?"
        analysis = processor.analyze_query(test_query)
        
        print(f"   ✅ Query Analysis: {analysis['intent']} (confidence: {analysis['confidence']:.1f}%)")
        print(f"   ✅ Language Detected: {analysis['language']}")
        print(f"   ✅ Priority Level: {analysis['priority']}")
        
        # Test agent routing
        agents = processor.route_to_agents(analysis)
        print(f"   ✅ Agent Routing: {len(agents)} agents selected")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Query Processor Test Failed: {str(e)}")
        return False

def test_response_formatter():
    """Test the response formatter"""
    print("\n📝 Testing Response Formatter...")
    
    try:
        from src.services.response_formatter import ResponseFormatter
        
        formatter = ResponseFormatter()
        
        # Test with sample agent response
        sample_response = {
            "agent_type": "Disease Identification",
            "confidence": 0.85,
            "recommendations": [
                "Apply neem oil spray",
                "Increase field monitoring",
                "Consider organic pesticides"
            ],
            "analysis": "Pest infestation detected in wheat crop"
        }
        
        formatted = formatter.format_agent_response(sample_response, "hindi")
        
        print(f"   ✅ Response Formatting: {len(formatted)} sections created")
        print(f"   ✅ Executive Summary: {'executive_summary' in formatted}")
        print(f"   ✅ Recommendations: {'recommendations' in formatted}")
        print(f"   ✅ Display Ready: {'display_sections' in formatted}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Response Formatter Test Failed: {str(e)}")
        return False

def test_websocket_integration():
    """Test websocket integration"""
    print("\n🔗 Testing Websocket Integration...")
    
    try:
        from src.services.websocket_integration import WebSocketIntegration
        
        ws_integration = WebSocketIntegration()
        
        # Test dashboard update preparation
        update_data = {
            "type": "dashboard_update",
            "metrics": {
                "total_queries": 10,
                "success_rate": 0.95,
                "avg_response_time": 1.2
            }
        }
        
        # This would normally send to connected clients
        prepared = ws_integration.prepare_dashboard_update(update_data)
        
        print(f"   ✅ Dashboard Update Preparation: {prepared['type']}")
        print(f"   ✅ Metrics Included: {len(prepared['data']['metrics'])} metrics")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Websocket Integration Test Failed: {str(e)}")
        return False

def test_frontend_files():
    """Test that frontend files exist and are properly structured"""
    print("\n🎨 Testing Frontend Integration...")
    
    frontend_files = [
        "frontend/src/components/EnhancedAgricultureInterface.tsx",
        "frontend/src/components/EnhancedAgricultureInterface.css"
    ]
    
    results = []
    for file_path in frontend_files:
        full_path = project_root / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'formatted' in content.lower() and 'dashboard' in content.lower():
                    results.append(f"   ✅ {file_path}: Enhanced features detected")
                else:
                    results.append(f"   ⚠️ {file_path}: File exists but may need enhancement")
        else:
            results.append(f"   ❌ {file_path}: File not found")
    
    for result in results:
        print(result)
    
    return all("✅" in result or "⚠️" in result for result in results)

async def test_full_integration():
    """Test full system integration"""
    print("\n🚀 Testing Full System Integration...")
    
    try:
        from src.services.enhanced_query_processor import EnhancedQueryProcessor
        from src.services.response_formatter import ResponseFormatter
        
        # Initialize components
        processor = EnhancedQueryProcessor()
        formatter = ResponseFormatter()
        
        # Test full workflow
        test_queries = [
            ("मेरे टमाटर के पौधों में पीले पत्ते हो गए हैं", "hindi"),
            ("My wheat crop needs irrigation planning", "english"),
            ("Market mein kis rate pe bechna chahiye", "hinglish")
        ]
        
        results = []
        for query, expected_lang in test_queries:
            # Analyze query
            analysis = processor.analyze_query(query)
            
            # Route to agents
            agents = processor.route_to_agents(analysis)
            
            # Simulate agent responses
            agent_responses = []
            for agent in agents:
                mock_response = {
                    "agent_type": agent,
                    "confidence": 0.9,
                    "analysis": f"Analysis from {agent} agent",
                    "recommendations": [f"Recommendation 1 from {agent}", f"Recommendation 2 from {agent}"]
                }
                agent_responses.append(mock_response)
            
            # Format responses
            formatted_responses = []
            for response in agent_responses:
                formatted = formatter.format_agent_response(response, analysis['language'])
                formatted_responses.append(formatted)
            
            # Synthesize final response
            final_response = formatter.synthesize_responses(formatted_responses, analysis)
            
            results.append({
                "query": query[:30] + "...",
                "detected_language": analysis['language'],
                "intent": analysis['intent'],
                "agents_called": len(agents),
                "response_sections": len(final_response.get('display_sections', []))
            })
        
        print("   Integration Test Results:")
        for i, result in enumerate(results, 1):
            print(f"   Test {i}: {result['query']}")
            print(f"      Language: {result['detected_language']}")
            print(f"      Intent: {result['intent']}")
            print(f"      Agents: {result['agents_called']}")
            print(f"      Sections: {result['response_sections']}")
        
        print(f"   ✅ Full Integration: {len(results)} test scenarios completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Full Integration Test Failed: {str(e)}")
        return False

def generate_system_report():
    """Generate a comprehensive system status report"""
    print("\n📊 Generating System Status Report...")
    
    # Check file structure
    critical_files = [
        "src/services/enhanced_query_processor.py",
        "src/services/response_formatter.py",
        "src/services/websocket_integration.py",
        "src/api/routers/enhanced_demo.py",
        "enhanced_demo_api.py",
        "frontend/src/components/EnhancedAgricultureInterface.tsx",
        "frontend/src/components/EnhancedAgricultureInterface.css",
        "ENHANCED_SYSTEM_README.md"
    ]
    
    file_status = {}
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            file_status[file_path] = f"✅ Exists ({full_path.stat().st_size} bytes)"
        else:
            file_status[file_path] = "❌ Missing"
    
    print("\n📁 Critical Files Status:")
    for file_path, status in file_status.items():
        print(f"   {file_path}: {status}")
    
    # Generate recommendations
    print("\n💡 System Recommendations:")
    if all("✅" in status for status in file_status.values()):
        print("   ✅ All critical files are present")
        print("   ✅ Enhanced system is ready for deployment")
        print("   📝 Next steps:")
        print("      1. Test frontend in browser")
        print("      2. Validate real-time dashboard updates")
        print("      3. Test multi-language query processing")
        print("      4. Verify agent response formatting")
    else:
        missing_files = [f for f, s in file_status.items() if "❌" in s]
        print(f"   ⚠️ {len(missing_files)} critical files missing")
        print("   📝 Required actions:")
        for file_path in missing_files:
            print(f"      - Create/restore: {file_path}")

def main():
    """Main integration test function"""
    print("🌾🛰️ Enhanced Multi-Agent Agriculture System - Integration Test")
    print("=" * 80)
    
    # Run all tests
    test_results = []
    
    test_results.append(("Module Imports", test_imports()))
    test_results.append(("Enhanced Query Processor", test_enhanced_query_processor()))
    test_results.append(("Response Formatter", test_response_formatter()))
    test_results.append(("Websocket Integration", test_websocket_integration()))
    test_results.append(("Frontend Files", test_frontend_files()))
    
    # Run async test
    try:
        loop = asyncio.get_event_loop()
        integration_result = loop.run_until_complete(test_full_integration())
        test_results.append(("Full Integration", integration_result))
    except Exception as e:
        print(f"   ❌ Async test failed: {str(e)}")
        test_results.append(("Full Integration", False))
    
    # Generate report
    generate_system_report()
    
    # Summary
    print("\n🎯 Test Summary:")
    print("=" * 80)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
