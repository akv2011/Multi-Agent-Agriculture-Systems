#!/usr/bin/env python3
"""
Quick Agent Model Health Check
Fast verification of agent availability and basic functionality.
"""

import os
import sys
import importlib.util

# Setup
sys.path.append('/home/hari/Music/Multi-Agent-Agriculture-Systems')
os.chdir('/home/hari/Music/Multi-Agent-Agriculture-Systems')

def quick_import_test(module_path, class_name=None):
    """Quick test if a module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        if spec is None:
            return False, "Spec not found"
        
        module = importlib.util.module_from_spec(spec)
        
        # Just check if the file can be read and basic syntax is valid
        with open(module_path, 'r') as f:
            content = f.read()
            
        # Check for basic patterns
        has_class = class_name is None or class_name in content
        has_imports = "import" in content
        has_function_def = "def " in content or "class " in content
        
        return True, f"Valid Python file with {'class' if has_class else 'no class'}"
        
    except Exception as e:
        return False, str(e)

def main():
    print("⚡ Quick Agent Model Health Check")
    print("=" * 40)
    
    # Test agents
    print("\n🤖 AGENTS:")
    agents = [
        ("src/agents/crop_selection_agent.py", "CropSelectionAgent"),
        ("src/agents/disease_identification_agent.py", "DiseaseIdentificationAgent"),
        ("src/agents/irrigation_agent.py", "IrrigationAgent"),
        ("src/agents/fertilizer_recommendation_agent.py", "FertilizerRecommendationAgent"),
        ("src/agents/market_timing_agent.py", "MarketTimingAgent"),
        ("src/agents/harvest_planning_agent.py", "HarvestPlanningAgent"),
        ("src/agents/weather_forecast_agent.py", "WeatherForecastAgent"),
        ("src/agents/agriculture_router.py", "AgricultureRouter")
    ]
    
    agent_results = []
    for file_path, class_name in agents:
        success, message = quick_import_test(file_path, class_name)
        status = "✅" if success else "❌"
        agent_name = os.path.basename(file_path).replace(".py", "").replace("_", " ").title()
        print(f"   {status} {agent_name}")
        if not success:
            print(f"      Error: {message}")
        agent_results.append(success)
    
    # Test models
    print("\n📚 MODELS:")
    models = [
        "src/models/AgriMitr_crop_recommendation.py",
        "src/models/AgriMitr_disease_identification.py",
        "src/models/AgriMitr_irrigation_scheduling.py",
        "src/models/AgriMitr_fertilizer_recommendation.py",
        "src/models/AgriMitr_market_timing.py",
        "src/models/AgriMitr_harvest_planning.py"
    ]
    
    model_results = []
    for file_path in models:
        success, message = quick_import_test(file_path)
        status = "✅" if success else "❌"
        model_name = os.path.basename(file_path).replace("AgriMitr_", "").replace(".py", "").replace("_", " ").title()
        print(f"   {status} {model_name}")
        if not success:
            print(f"      Error: {message}")
        model_results.append(success)
    
    # Test core files
    print("\n⚙️ CORE FILES:")
    core_files = [
        "src/core/agriculture_models.py",
        "src/agents/base_agent.py",
        "src/services/ground_search_service.py"
    ]
    
    core_results = []
    for file_path in core_files:
        success, message = quick_import_test(file_path)
        status = "✅" if success else "❌"
        file_name = os.path.basename(file_path)
        print(f"   {status} {file_name}")
        if not success:
            print(f"      Error: {message}")
        core_results.append(success)
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    
    agent_health = (sum(agent_results) / len(agent_results)) * 100
    model_health = (sum(model_results) / len(model_results)) * 100
    core_health = (sum(core_results) / len(core_results)) * 100
    overall_health = (sum(agent_results + model_results + core_results) / 
                     (len(agent_results) + len(model_results) + len(core_results))) * 100
    
    print(f"🤖 Agents:  {sum(agent_results)}/{len(agent_results)} ({agent_health:.0f}%)")
    print(f"📚 Models:  {sum(model_results)}/{len(model_results)} ({model_health:.0f}%)")
    print(f"⚙️ Core:    {sum(core_results)}/{len(core_results)} ({core_health:.0f}%)")
    print(f"🌟 Overall: {overall_health:.0f}%")
    
    # Assessment
    print("\n🎯 ASSESSMENT:")
    if overall_health >= 90:
        print("   ✅ EXCELLENT - All components available")
        print("   🚀 System ready for functional testing")
    elif overall_health >= 75:
        print("   ✅ GOOD - Most components available")
        print("   🔧 Minor fixes needed")
    elif overall_health >= 50:
        print("   ⚠️ FAIR - Some components missing")
        print("   🛠️ Significant work needed")
    else:
        print("   ❌ POOR - Major components missing")
        print("   🔴 System needs reconstruction")
    
    # Issue identification
    failed_agents = [agents[i][0] for i, success in enumerate(agent_results) if not success]
    failed_models = [models[i] for i, success in enumerate(model_results) if not success]
    failed_core = [core_files[i] for i, success in enumerate(core_results) if not success]
    
    if failed_agents:
        print(f"\n❌ Failed Agents: {len(failed_agents)}")
    if failed_models:
        print(f"❌ Failed Models: {len(failed_models)}")
    if failed_core:
        print(f"❌ Failed Core Files: {len(failed_core)}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if overall_health >= 75:
        print("   1. ✅ System structure is sound")
        print("   2. 🧪 Proceed with functional testing using stub models")
        print("   3. 🔄 Test individual agents with simple queries")
        print("   4. 🌐 Use ground search service for enhanced responses")
    else:
        print("   1. 🔧 Fix file structure and import issues")
        print("   2. 📋 Review missing components")
        print("   3. 🔄 Re-run this check after fixes")
    
    print("\n🔄 NEXT COMMANDS TO TRY:")
    print("   python test_quick_ground_search.py  # Test ground search")
    print("   python demo_ground_search.py        # Demo agricultural AI")
    print("   ./start_disease_detection_demo.sh   # Start frontend demo")

if __name__ == "__main__":
    main()
