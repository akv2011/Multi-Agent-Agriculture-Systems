#!/usr/bin/env python
"""
Comprehensive AgriMitr Integration Test Runner
This script runs all the AgriMitr integration test scripts and reports their status.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root
project_root = Path(__file__).parent.absolute()

def run_test(test_script_name):
    """Run a test script and return status"""
    print(f"\n{'='*60}")
    print(f"Running {test_script_name}")
    print(f"{'='*60}")
    
    script_path = os.path.join(project_root, test_script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Test script not found: {script_path}")
        return False
    
    try:
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False  # Don't raise an exception on non-zero exit
        )
        
        # Print output
        print(result.stdout)
        
        if result.stderr:
            print("\nStderr output:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ {test_script_name} completed successfully")
            return True
        else:
            print(f"\n❌ {test_script_name} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {test_script_name}: {str(e)}")
        return False

def run_vscode_task(task_id):
    """Run a VS Code task"""
    print(f"\n{'='*60}")
    print(f"Running VS Code task: {task_id}")
    print(f"{'='*60}")
    
    try:
        # For VS Code tasks, we'll directly run the command
        # This is a simplified approach since we can't directly invoke VS Code tasks
        # from a script without the VS Code API
        
        # We know this task is for running integration tests
        cmd = "cd /home/hari/Music/Multi-Agent-Agriculture-Systems && python -m unittest tests/test_irrigation_model_integration.py tests/test_market_timing_model_integration.py tests/test_harvest_planning_integration.py"
        
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Print output
        print(result.stdout)
        
        if result.stderr:
            print("\nStderr output:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ Task '{task_id}' completed successfully")
            return True
        else:
            print(f"\n❌ Task '{task_id}' failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running task '{task_id}': {str(e)}")
        return False

def check_file_existence():
    """Check existence of key model and agent files"""
    print(f"\n{'='*60}")
    print("Checking existence of key files")
    print(f"{'='*60}")
    
    key_files = [
        # Agent files
        "src/agents/disease_identification_agent.py",
        "src/agents/crop_selection_agent.py",
        "src/agents/weather_forecast_agent.py",
        "src/agents/agriculture_router.py",
        "src/agents/irrigation_agent.py",
        "src/agents/fertilizer_recommendation_agent.py",
        "src/agents/smart_farming_guidance_agent.py",
        
        # Model files
        "src/models/AgriMitr_disease_identification.py",
        "src/models/AgriMitr_crop_recommendation.py",
        "src/models/AgriMitr_irrigation_scheduling.py",
        "src/models/AgriMitr_fertilizer_recommendation.py",
        
        # Service files
        "src/services/google_search_service.py",
        
        # Test files
        "tests/test_irrigation_model_integration.py",
        "tests/test_disease_identification_integration.py",
        "tests/test_smart_farming_guidance_integration.py",
        "tests/test_google_search_integration.py",
        "tests/test_agent_router_integration.py"
    ]
    
    missing_files = []
    found_files = []
    
    for file_path in key_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            found_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    # Print results
    print(f"\nFound {len(found_files)} files:")
    for file in found_files:
        print(f"✅ {file}")
    
    if missing_files:
        print(f"\nMissing {len(missing_files)} files:")
        for file in missing_files:
            print(f"❌ {file}")
    else:
        print("\n✅ All key files are present!")
    
    return len(missing_files) == 0

def create_report(results):
    """Create a test report"""
    report_path = os.path.join(project_root, "test_results", f"AgriMitr_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write("AgriMitr Integration Test Report\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        
        f.write("Test Results Summary:\n")
        f.write("-"*50 + "\n")
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r)
        
        f.write(f"Total tests:  {total_tests}\n")
        f.write(f"Passed tests: {passed_tests}\n")
        f.write(f"Failed tests: {total_tests - passed_tests}\n\n")
        
        f.write("Individual Test Results:\n")
        f.write("-"*50 + "\n")
        
        for test_name, status in results.items():
            f.write(f"{test_name}: {'✅ PASS' if status else '❌ FAIL'}\n")
    
    print(f"\nTest report generated: {report_path}")
    return report_path

if __name__ == "__main__":
    print("🔍 AgriMitr Integration Test Runner 🔍")
    print("======================================")
    
    # Dictionary to store test results
    test_results = {}
    
    # Check file existence
    test_results["file_check"] = check_file_existence()
    
    # List of test scripts to run
    test_scripts = [
        "test_AgriMitr_agents.py",
        "test_irrigation_manually.py",
        "test_market_timing_manually.py"
    ]
    
    # Run each test script
    for script in test_scripts:
        test_results[script] = run_test(script)
    
    # Run VS Code task
    test_results["vscode_integration_tests"] = run_vscode_task("Run AgriMitr Model Integration Tests")
    
    # Create report
    report_path = create_report(test_results)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results.values() if r)
    
    print(f"Total tests:  {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Failed tests: {total_tests - passed_tests}")
    
    print("\nIndividual Test Results:")
    for test_name, status in test_results.items():
        print(f"{test_name}: {'✅ PASS' if status else '❌ FAIL'}")
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Exit with status code
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed!")
        sys.exit(1)
