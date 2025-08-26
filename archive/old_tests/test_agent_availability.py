#!/usr/bin/env python3
"""
Simple Agent Availability Test
Tests if all model-having agents can be imported and initialized without crashing.
"""

import sys
import os
import traceback

# Setup environment
sys.path.append('/home/hari/Music/Multi-Agent-Agriculture-Systems')
os.chdir('/home/hari/Music/Multi-Agent-Agriculture-Systems')

def test_agent_imports():
    """Test if all agents can be imported successfully"""
    print("🧪 Testing Agent Imports and Basic Functionality")
    print("=" * 55)
    
    agents_to_test = [
        ("Crop Selection Agent", "src.agents.crop_selection_agent", "CropSelectionAgent"),
        ("Disease Identification Agent", "src.agents.disease_identification_agent", "DiseaseIdentificationAgent"),
        ("Irrigation Agent", "src.agents.irrigation_agent", "IrrigationAgent"),
        ("Fertilizer Agent", "src.agents.fertilizer_recommendation_agent", "FertilizerRecommendationAgent"),
        ("Market Timing Agent", "src.agents.market_timing_agent", "MarketTimingAgent"),
        ("Harvest Planning Agent", "src.agents.harvest_planning_agent", "HarvestPlanningAgent"),
        ("Weather Forecast Agent", "src.agents.weather_forecast_agent", "WeatherForecastAgent"),
        ("Agriculture Router", "src.agents.agriculture_router", "AgricultureRouter"),
    ]
    
    results = {}
    
    for agent_name, module_path, class_name in agents_to_test:
        print(f"\n🔍 Testing {agent_name}...")
        try:
            # Try to import the module
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            
            # Try to create an instance (but don't call process_query to avoid model loading)
            agent = agent_class()
            
            # Check if it has the required attributes
            has_name = hasattr(agent, 'name')
            has_capabilities = hasattr(agent, 'capabilities')
            has_process_query = hasattr(agent, 'process_query')
            
            results[agent_name] = {
                "import": "✅ SUCCESS",
                "initialization": "✅ SUCCESS",
                "has_name": has_name,
                "has_capabilities": has_capabilities,
                "has_process_query": has_process_query,
                "agent_name": getattr(agent, 'name', 'Unknown'),
                "capabilities_count": len(getattr(agent, 'capabilities', []))
            }
            
            print(f"✅ {agent_name}: Import & Init successful")
            print(f"   Agent Name: {results[agent_name]['agent_name']}")
            print(f"   Capabilities: {results[agent_name]['capabilities_count']}")
            
        except Exception as e:
            results[agent_name] = {
                "import": "❌ FAILED",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"❌ {agent_name}: {str(e)}")
    
    return results

def test_model_imports():
    """Test if AgriSens model modules can be imported"""
    print("\n🤖 Testing AgriSens Model Imports")
    print("=" * 40)
    
    models_to_test = [
        ("Crop Recommendation Model", "src.models.agrisens_crop_recommendation"),
        ("Disease Identification Model", "src.models.agrisens_disease_identification"),
        ("Irrigation Scheduling Model", "src.models.agrisens_irrigation_scheduling"),
        ("Fertilizer Recommendation Model", "src.models.agrisens_fertilizer_recommendation"),
        ("Market Timing Model", "src.models.agrisens_market_timing"),
        ("Harvest Planning Model", "src.models.agrisens_harvest_planning"),
    ]
    
    model_results = {}
    
    for model_name, module_path in models_to_test:
        print(f"\n🔍 Testing {model_name}...")
        try:
            # Try to import the model module
            module = __import__(module_path, fromlist=[''])
            
            # Check for common functions/classes
            functions = [name for name in dir(module) if not name.startswith('_')]
            
            model_results[model_name] = {
                "import": "✅ SUCCESS",
                "functions_count": len(functions),
                "sample_functions": functions[:5]  # First 5 functions
            }
            
            print(f"✅ {model_name}: Import successful")
            print(f"   Available functions: {len(functions)}")
            print(f"   Sample functions: {', '.join(functions[:3])}")
            
        except Exception as e:
            model_results[model_name] = {
                "import": "❌ FAILED",
                "error": str(e)
            }
            print(f"❌ {model_name}: {str(e)}")
    
    return model_results

def generate_summary(agent_results, model_results):
    """Generate test summary"""
    print("\n" + "=" * 60)
    print("📊 AGENT & MODEL AVAILABILITY SUMMARY")
    print("=" * 60)
    
    # Agent summary
    total_agents = len(agent_results)
    successful_agents = sum(1 for r in agent_results.values() if "✅" in r["import"])
    agent_success_rate = (successful_agents / total_agents) * 100
    
    print(f"\n🤖 AGENTS:")
    print(f"   Total: {total_agents}")
    print(f"   ✅ Successful: {successful_agents}")
    print(f"   ❌ Failed: {total_agents - successful_agents}")
    print(f"   Success Rate: {agent_success_rate:.1f}%")
    
    # Model summary
    total_models = len(model_results)
    successful_models = sum(1 for r in model_results.values() if "✅" in r["import"])
    model_success_rate = (successful_models / total_models) * 100
    
    print(f"\n📚 MODELS:")
    print(f"   Total: {total_models}")
    print(f"   ✅ Successful: {successful_models}")
    print(f"   ❌ Failed: {total_models - successful_models}")
    print(f"   Success Rate: {model_success_rate:.1f}%")
    
    # Overall health
    overall_success = (successful_agents + successful_models) / (total_agents + total_models) * 100
    print(f"\n🎯 OVERALL SYSTEM HEALTH: {overall_success:.1f}%")
    
    # Failed components
    failed_agents = [name for name, result in agent_results.items() if "❌" in result["import"]]
    failed_models = [name for name, result in model_results.items() if "❌" in result["import"]]
    
    if failed_agents:
        print(f"\n❌ FAILED AGENTS:")
        for agent in failed_agents:
            print(f"   - {agent}: {agent_results[agent]['error']}")
    
    if failed_models:
        print(f"\n❌ FAILED MODELS:")
        for model in failed_models:
            print(f"   - {model}: {model_results[model]['error']}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if agent_success_rate < 100:
        print("   - Fix failed agent imports before proceeding")
    if model_success_rate < 100:
        print("   - Check AgriSens model dependencies")
    if overall_success >= 80:
        print("   - System is mostly healthy and ready for testing")
    elif overall_success >= 60:
        print("   - System has some issues but core functionality available")
    else:
        print("   - System needs significant fixes before use")

def main():
    """Main test function"""
    print("🌱 AgriSens Multi-Agent System - Component Availability Test")
    print("=" * 65)
    
    # Test agent imports
    agent_results = test_agent_imports()
    
    # Test model imports
    model_results = test_model_imports()
    
    # Generate summary
    generate_summary(agent_results, model_results)
    
    print("\n" + "=" * 60)
    print("✨ Test completed! Check summary above for system health.")

if __name__ == "__main__":
    main()
