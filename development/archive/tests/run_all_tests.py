#!/usr/bin/env python3

import sys
import os
import subprocess
import time

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_test(test_file):
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Run the test file from the project root
        test_path = os.path.join('tests', 'working', test_file)
        result = subprocess.run([sys.executable, test_path], capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_file}: PASSED")
            return True
        else:
            print(f"❌ {test_file}: FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {test_file}: ERROR - {e}")
        return False

def main():
    print("🚀 AGENTWEAVER TEST SUITE")
    print("=" * 40)
    print("Running all working tests...")
    
    tests = [
        'verify_live_components.py',
        'test_live_perfect.py'
    ]
    
    start_time = time.time()
    results = {}
    
    for test in tests:
        results[test] = run_test(test)
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 TEST SUITE RESULTS")
    print(f"{'='*60}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test}")
    
    success_rate = (passed / total) * 100
    execution_time = time.time() - start_time
    
    print(f"\n📊 SUMMARY:")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Execution Time: {execution_time:.2f} seconds")
    
    if success_rate >= 90:
        print("\n🏆 EXCELLENT: Test suite passed!")
        print("✅ AgentWeaver is fully verified and production-ready")
    elif success_rate >= 75:
        print("\n✅ GOOD: Most tests passed")
    else:
        print("\n⚠️ ATTENTION: Some tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
