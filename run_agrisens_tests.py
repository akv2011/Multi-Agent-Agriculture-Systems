#!/usr/bin/env python3
"""
AgriMitr Test Runner

This script runs tests for the key AgriMitr components:
1. Disease Prediction Agent
2. Crop Recommendation Agent  
3. Weather Forecast Functionality
4. Irrigation Model Integration
5. Market Timing Model Integration

Usage:
    python run_AgriMitr_tests.py
"""

import os
import sys
import unittest
import subprocess
import time

def print_section(title):
    """Print a section title with decoration"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def run_tests():
    """Run all AgriMitr integration tests"""
    print_section("Running AgriMitr Models and Agents Tests")
    
    # Define all test files to run
    test_files = [
        "tests/test_AgriMitr_integration.py",
        "tests/test_disease_identification_integration.py", 
        "tests/test_irrigation_model_integration.py",
        "tests/test_market_timing_model_integration.py",
        "tests/test_AgriMitr_models_and_agents.py"
    ]
    
    # Run each test file individually using subprocess
    results = []
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n🔄 Running tests from {test_file}")
            try:
                result = subprocess.run([sys.executable, test_file], 
                                        capture_output=True, 
                                        text=True)
                success = result.returncode == 0
                results.append((test_file, success, result.returncode))
                
                # Print output
                print(result.stdout)
                if result.stderr:
                    print(f"Errors from {test_file}:")
                    print(result.stderr)
                    
                status = "✅ Passed" if success else f"❌ Failed (code {result.returncode})"
                print(f"{status}: {test_file}")
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                results.append((test_file, False, -1))
        else:
            print(f"❌ Test file not found: {test_file}")
            results.append((test_file, False, -1))
    
    # Print test summary
    print("\n" + "-"*40)
    success_count = sum(1 for _, success, _ in results if success)
    fail_count = len(results) - success_count
    print(f"Ran {len(results)} tests")
    print(f"Passed: {success_count}")
    print(f"Failed: {fail_count}")
    print("-"*40)
    
    if fail_count == 0:
        print("\n✅ All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed or encountered errors.")
        return 1

def run_individual_test(test_name):
    """Run a specific test file"""
    if not test_name.endswith('.py'):
        test_name += '.py'
    
    test_path = os.path.join('tests', test_name)
    if not os.path.exists(test_path):
        print(f"❌ Test file not found: {test_path}")
        return 1
    
    print_section(f"Running {test_name}")
    result = subprocess.run([sys.executable, test_path])
    return result.returncode

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) > 1:
        # Run a specific test
        test_name = sys.argv[1]
        sys.exit(run_individual_test(test_name))
    else:
        # Run all tests
        sys.exit(run_tests())
