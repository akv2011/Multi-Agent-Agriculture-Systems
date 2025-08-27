#!/usr/bin/env python3
"""
AgriSens Agent & Model Status Check
Quick verification of agent and model availability without loading heavy dependencies.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path):
    """Check if a file exists and return its size"""
    path = Path(file_path)
    if path.exists():
        size_kb = path.stat().st_size / 1024
        return True, f"{size_kb:.1f} KB"
    return False, "Missing"

def main():
    print("🌱 AgriSens System Status Check")
    print("=" * 50)
    
    # Check core model files
    print("\n📚 AgriSens Model Files:")
    models = [
        "src/models/agrisens_crop_recommendation.py",
        "src/models/agrisens_disease_identification.py", 
        "src/models/agrisens_irrigation_scheduling.py",
        "src/models/agrisens_fertilizer_recommendation.py",
        "src/models/agrisens_market_timing.py",
        "src/models/agrisens_harvest_planning.py"
    ]
    
    model_status = {}
    for model in models:
        exists, size = check_file_exists(model)
        model_name = Path(model).stem.replace("agrisens_", "").replace("_", " ").title()
        status = "✅" if exists else "❌"
        model_status[model_name] = exists
        print(f"   {status} {model_name}: {size}")
    
    # Check agent files
    print("\n🤖 Agent Files:")
    agents = [
        "src/agents/crop_selection_agent.py",
        "src/agents/disease_identification_agent.py",
        "src/agents/irrigation_agent.py", 
        "src/agents/fertilizer_recommendation_agent.py",
        "src/agents/market_timing_agent.py",
        "src/agents/harvest_planning_agent.py",
        "src/agents/weather_forecast_agent.py",
        "src/agents/agriculture_router.py"
    ]
    
    agent_status = {}
    for agent in agents:
        exists, size = check_file_exists(agent)
        agent_name = Path(agent).stem.replace("_agent", "").replace("_", " ").title() + " Agent"
        status = "✅" if exists else "❌"
        agent_status[agent_name] = exists
        print(f"   {status} {agent_name}: {size}")
    
    # Check core files
    print("\n🎯 Core System Files:")
    core_files = [
        "src/core/agriculture_models.py",
        "src/agents/base_agent.py",
        "src/services/ground_search_service.py",
        ".env"
    ]
    
    core_status = {}
    for core_file in core_files:
        exists, size = check_file_exists(core_file)
        file_name = Path(core_file).name
        status = "✅" if exists else "❌"
        core_status[file_name] = exists
        print(f"   {status} {file_name}: {size}")
    
    # Check test data
    print("\n📊 Test Data:")
    test_files = [
        "data/agrisens/crop_recommendation_test.csv",
        "data/agrisens/irrigation_data_test.csv",
        "data/agrisens/market_prices_test.csv"
    ]
    
    test_status = {}
    for test_file in test_files:
        exists, size = check_file_exists(test_file)
        file_name = Path(test_file).name
        status = "✅" if exists else "❌"
        test_status[file_name] = exists
        print(f"   {status} {file_name}: {size}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    total_models = len(models)
    working_models = sum(model_status.values())
    model_health = (working_models / total_models) * 100
    
    total_agents = len(agents) 
    working_agents = sum(agent_status.values())
    agent_health = (working_agents / total_agents) * 100
    
    total_core = len(core_files)
    working_core = sum(core_status.values())
    core_health = (working_core / total_core) * 100
    
    print(f"🤖 Models: {working_models}/{total_models} ({model_health:.0f}%)")
    print(f"🎯 Agents: {working_agents}/{total_agents} ({agent_health:.0f}%)")
    print(f"⚙️  Core:   {working_core}/{total_core} ({core_health:.0f}%)")
    
    overall_health = (working_models + working_agents + working_core) / (total_models + total_agents + total_core) * 100
    print(f"\n🌟 Overall System Health: {overall_health:.0f}%")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if overall_health >= 90:
        print("   ✅ System is healthy and ready for testing")
        print("   🚀 You can proceed with agent functionality tests")
    elif overall_health >= 75:
        print("   ⚠️  System has minor issues but core functionality available")
        print("   🔧 Fix missing files before production use")
    else:
        print("   ❌ System needs attention before use")
        print("   📝 Check missing files and dependencies")
    
    # Specific missing components
    missing_models = [name for name, status in model_status.items() if not status]
    missing_agents = [name for name, status in agent_status.items() if not status]
    missing_core = [name for name, status in core_status.items() if not status]
    
    if missing_models:
        print(f"\n❌ Missing Models: {', '.join(missing_models)}")
    if missing_agents:
        print(f"❌ Missing Agents: {', '.join(missing_agents)}")
    if missing_core:
        print(f"❌ Missing Core Files: {', '.join(missing_core)}")
    
    # Next steps
    print("\n🔄 NEXT STEPS:")
    print("   1. Check dependencies: pip install -r requirements.txt")
    print("   2. Test basic imports: python -c 'from src.core.agriculture_models import CropType'")
    print("   3. Run individual agent tests with lightweight queries")
    print("   4. Consider using stub models to avoid TensorFlow issues")

if __name__ == "__main__":
    main()
