#!/usr/bin/env python3
"""
Simple agent import test
"""

import sys
import os
sys.path.append('/home/hari/Music/Multi-Agent-Agriculture-Systems')

def test_agent_availability():
    """Test if agent files exist and basic imports work"""
    print("🔍 Testing agent availability...")
    
    agents = {
        "Crop Selection Agent": "src/agents/crop_selection_agent.py",
        "Irrigation Agent": "src/agents/irrigation_agent.py", 
        "Pest Management Agent": "src/agents/pest_management_agent.py",
        "Finance Policy Agent": "src/agents/finance_policy_agent.py",
        "Market Timing Agent": "src/agents/market_timing_agent.py",
        "Harvest Planning Agent": "src/agents/harvest_planning_agent.py",
        "Input Materials Agent": "src/agents/input_materials_agent.py",
    }
    
    base_path = "/home/hari/Music/Multi-Agent-Agriculture-Systems"
    
    for name, file_path in agents.items():
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {name}: File exists")
        else:
            print(f"❌ {name}: File missing")
    
    # Test core models
    try:
        from src.core.agriculture_models import QueryDomain
        required_domains = ["CROP_SELECTION", "IRRIGATION", "PEST_MANAGEMENT", 
                          "FINANCE_POLICY", "MARKET_TIMING", "HARVEST_PLANNING", "INPUT_MATERIALS"]
        
        print("\n🎯 Query domains:")
        for domain in required_domains:
            if hasattr(QueryDomain, domain):
                print(f"✅ {domain}")
            else:
                print(f"❌ {domain} missing")
                
    except Exception as e:
        print(f"❌ Core models error: {e}")
    
    print("\n🎉 Basic agent integration check complete!")

if __name__ == "__main__":
    test_agent_availability()
