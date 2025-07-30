#!/usr/bin/env python3
"""
Test runner for Calculator Suite
Runs all test suites and generates coverage reports
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the parent directory to sys.path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """Run a command and display results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command.replace('python ', 'python3 '), shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ PASSED in {execution_time:.2f}s")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ FAILED in {execution_time:.2f}s")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all test suites"""
    print("🚀 Calculator Suite Test Runner")
    print("Running comprehensive test suite...")
    
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Change to project root directory
    os.chdir(project_root)
    
    # List of test commands to run
    test_commands = [
        {
            'command': 'python -m pytest tests/test_calculators.py -v',
            'description': 'Unit Tests for All Calculators'
        },
        {
            'command': 'python -m pytest tests/test_edge_cases.py -v',
            'description': 'Edge Cases and Boundary Condition Tests'
        },
        {
            'command': 'python -m pytest tests/test_performance.py -v',
            'description': 'Performance and Load Tests'
        },
        {
            'command': 'python -m pytest tests/ -v --tb=short',
            'description': 'Full Test Suite (All Tests)'
        }
    ]
    
    # Optional: Coverage analysis if coverage is available
    coverage_commands = [
        {
            'command': 'python -m pytest tests/ --cov=app_simple_fixed --cov-report=term-missing',
            'description': 'Test Coverage Analysis'
        },
        {
            'command': 'python -m pytest tests/ --cov=app_simple_fixed --cov-report=html',
            'description': 'Generate HTML Coverage Report'
        }
    ]
    
    results = []
    
    # Run basic tests first
    for test in test_commands:
        success = run_command(test['command'], test['description'])
        results.append((test['description'], success))
    
    # Try to run coverage analysis (optional)
    print(f"\n{'='*60}")
    print("📊 Attempting Coverage Analysis (optional)")
    print(f"{'='*60}")
    
    try:
        # Check if coverage is available
        subprocess.run(['python3', '-c', 'import coverage'], check=True, capture_output=True)
        
        for test in coverage_commands:
            success = run_command(test['command'], test['description'])
            results.append((test['description'], success))
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Coverage module not available. Install with: pip install coverage pytest-cov")
        print("   Skipping coverage analysis...")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {description}")
    
    print(f"\n🎯 OVERALL: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Calculator Suite is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)