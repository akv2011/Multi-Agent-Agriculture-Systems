#!/usr/bin/env python3
"""
Quick test to verify that the new agents are properly integrated
"""

import sys
import os
sys.path.append('/home/hari/Music/Multi-Agent-Agriculture-Systems')
os.chdir('/home/hari/Music/Multi-Agent-Agriculture-Systems')

def test_agent_imports():
    """Test that all agents can be imported"""
    print("🔍 Testing agent imports...")
    
    agents_to_test = [
        ("Crop Selection Agent", "src.agents.crop_selection_agent", "CropSelectionAgent"),
        ("Irrigation Agent", "src.agents.irrigation_agent", "IrrigationAgent"),
        ("Pest Management Agent", "src.agents.pest_management_agent", "PestManagementAgent"),
        ("Finance Policy Agent", "src.agents.finance_policy_agent", "FinancePolicyAgent"),
        ("Market Timing Agent", "src.agents.market_timing_agent", "MarketTimingAgent"),
        ("Harvest Planning Agent", "src.agents.harvest_planning_agent", "HarvestPlanningAgent"),
        ("Input Materials Agent", "src.agents.input_materials_agent", "InputMaterialsAgent"),
    ]
    
    results = {}
    
    for name, module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            # Try to instantiate
            agent = agent_class()
            results[name] = "✅ SUCCESS"
            print(f"✅ {name}: Imported and instantiated successfully")
        except Exception as e:
            results[name] = f"❌ ERROR: {str(e)}"
            print(f"❌ {name}: {str(e)}")
    
    return results

def test_agriculture_service():
    """Test the agriculture integration service"""
    print("\n🔧 Testing agriculture service integration...")
    
    try:
        from src.services.agriculture_integration import AgricultureIntegrationService
        from src.orchestration.supervisor import SupervisorNode
        
        # Create supervisor and service
        supervisor = SupervisorNode()
        service = AgricultureIntegrationService(supervisor)
        
        # Check if agents are registered
        agent_count = len(service.specialist_agents)
        print(f"✅ Agriculture service initialized with {agent_count} specialist agents")
        
        # List registered agents
        print("📋 Registered specialist agents:")
        for agent_id, agent_info in service.specialist_agents.items():
            domains = [domain.value for domain in agent_info['domains']]
            print(f"   - {agent_id}: {domains}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agriculture service error: {str(e)}")
        return False

def test_query_domains():
    """Test that all required query domains exist"""
    print("\n🎯 Testing query domains...")
    
    try:
        from src.core.agriculture_models import QueryDomain
        
        required_domains = [
            "CROP_SELECTION",
            "IRRIGATION", 
            "PEST_MANAGEMENT",
            "FINANCE_POLICY",
            "MARKET_TIMING",
            "HARVEST_PLANNING",
            "INPUT_MATERIALS"
        ]
        
        for domain in required_domains:
            if hasattr(QueryDomain, domain):
                print(f"✅ {domain}: Available")
            else:
                print(f"❌ {domain}: Missing")
                
        return True
        
    except Exception as e:
        print(f"❌ Query domains error: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print("🌾 Multi-Agent Agriculture Systems - Integration Test")
    print("=" * 60)
    
    # Test agent imports
    import_results = test_agent_imports()
    
    # Test agriculture service
    service_success = test_agriculture_service()
    
    # Test query domains
    domains_success = test_query_domains()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    successful_imports = sum(1 for result in import_results.values() if "SUCCESS" in result)
    total_agents = len(import_results)
    
    print(f"Agent Imports: {successful_imports}/{total_agents} successful")
    print(f"Agriculture Service: {'✅ Working' if service_success else '❌ Failed'}")
    print(f"Query Domains: {'✅ Available' if domains_success else '❌ Missing'}")
    
    overall_success = (successful_imports == total_agents and service_success and domains_success)
    print(f"\nOverall Status: {'🎉 ALL SYSTEMS GO!' if overall_success else '⚠️  Issues Found'}")
    
    return overall_success

if __name__ == "__main__":
    main()
