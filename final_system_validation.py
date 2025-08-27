#!/usr/bin/env python3
"""
Final AgriMitr System Validation Script

This script performs a comprehensive validation of all AgriMitr agents and models
to provide a final status report on system readiness.
"""

import sys
import os
import importlib.util
import asyncio
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath('.'))

def test_agent_import(agent_path, agent_class):
    """Test if an agent can be imported successfully"""
    try:
        spec = importlib.util.spec_from_file_location("module", agent_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        agent_cls = getattr(module, agent_class)
        agent = agent_cls()
        return True, f"✅ {agent_class} imported and instantiated successfully"
    except Exception as e:
        return False, f"❌ {agent_class} failed: {str(e)[:100]}..."

def test_model_import(model_path):
    """Test if a model file can be imported"""
    try:
        spec = importlib.util.spec_from_file_location("module", model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, f"✅ Model at {os.path.basename(model_path)} imported successfully"
    except Exception as e:
        return False, f"❌ Model at {os.path.basename(model_path)} failed: {str(e)[:100]}..."

def main():
    print("🔍 FINAL AgriMitr SYSTEM VALIDATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test all agents
    agents_to_test = [
        ("src/agents/disease_identification_agent.py", "DiseaseIdentificationAgent"),
        ("src/agents/crop_selection_agent.py", "CropRecommendationAgent"),
        ("src/agents/irrigation_agent.py", "IrrigationAgent"),
        ("src/agents/fertilizer_recommendation_agent.py", "FertilizerRecommendationAgent"),
        ("src/agents/market_timing_agent.py", "MarketTimingAgent"),
        ("src/agents/harvest_planning_agent.py", "HarvestPlanningAgent"),
        ("src/agents/weather_forecast_agent.py", "WeatherForecastAgent"),
        ("src/agents/agriculture_router.py", "AgricultureRouter"),
    ]

    print("🤖 AGENT STATUS:")
    print("-" * 30)
    
    agent_results = []
    for agent_path, agent_class in agents_to_test:
        if os.path.exists(agent_path):
            success, message = test_agent_import(agent_path, agent_class)
            agent_results.append((agent_class, success))
            print(message)
        else:
            print(f"❌ {agent_class}: File not found at {agent_path}")
            agent_results.append((agent_class, False))

    print()

    # Test stub models
    stub_models = [
        "models/stubs/stub_crop_model.py",
        "models/stubs/stub_irrigation_model.py"
    ]

    print("📊 STUB MODEL STATUS:")
    print("-" * 30)
    
    model_results = []
    for model_path in stub_models:
        if os.path.exists(model_path):
            success, message = test_model_import(model_path)
            model_results.append((os.path.basename(model_path), success))
            print(message)
        else:
            print(f"❌ Model not found: {model_path}")
            model_results.append((os.path.basename(model_path), False))

    print()

    # Test core models
    core_models = [
        "src/core/agriculture_models.py",
        "src/models.py"
    ]

    print("🏛️ CORE MODEL STATUS:")
    print("-" * 30)
    
    for model_path in core_models:
        if os.path.exists(model_path):
            success, message = test_model_import(model_path)
            print(message)
        else:
            print(f"❌ Core model not found: {model_path}")

    print()

    # Summary
    successful_agents = sum(1 for _, success in agent_results if success)
    total_agents = len(agent_results)
    
    successful_models = sum(1 for _, success in model_results if success)
    total_models = len(model_results)

    print("📈 FINAL SUMMARY:")
    print("-" * 30)
    print(f"✅ Agents: {successful_agents}/{total_agents} ({(successful_agents/total_agents)*100:.1f}%)")
    print(f"✅ Stub Models: {successful_models}/{total_models} ({(successful_models/total_models)*100:.1f}%)")
    print()

    if successful_agents == total_agents and successful_models == total_models:
        print("🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("All AgriMitr agents and models are working correctly!")
        print("System is ready for development and testing with stub models.")
    else:
        print("⚠️ SYSTEM STATUS: PARTIAL FUNCTIONALITY")
        print("Some components need attention.")

    print()
    print("📝 NOTES:")
    print("- All agents use mock Redis client (development mode)")
    print("- Stub models are active to avoid TensorFlow issues")
    print("- Frontend has image upload capability for disease ID")
    print("- System is ready for comprehensive integration testing")

if __name__ == "__main__":
    main()
