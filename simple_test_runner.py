#!/usr/bin/env python3
"""
Simple Test Runner for Calculator Suite
Runs tests without requiring pytest or other dependencies
"""

import sys
import os
import time
import traceback

# Add the parent directory to sys.path to import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test_group(test_name, test_function):
    """Run a group of tests and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        passed, failed, total = test_function()
        execution_time = time.time() - start_time
        
        if failed == 0:
            print(f"✅ ALL PASSED in {execution_time:.2f}s ({passed}/{total} tests)")
            return True
        else:
            print(f"❌ SOME FAILED in {execution_time:.2f}s ({passed}/{total} tests passed)")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ ERROR in {execution_time:.2f}s: {e}")
        return False

def test_calculator_imports():
    """Test that all calculator classes can be imported"""
    print("Testing calculator imports...")
    passed = 0
    failed = 0
    total = 0
    
    try:
        from app_simple_fixed import (
            PercentageCalculator, LoanCalculator, BMICalculator, TipCalculator,
            MortgageCalculator, IncomeTaxCalculator, SalesTaxCalculator, 
            PropertyTaxCalculator, TaxRefundCalculator, GrossToNetCalculator,
            HourlyToSalaryCalculator, SalaryRaiseCalculator, CostOfLivingCalculator,
            CompoundInterestCalculator, RetirementCalculator, InvestmentReturnCalculator
        )
        
        calculators = [
            PercentageCalculator, LoanCalculator, BMICalculator, TipCalculator,
            MortgageCalculator, IncomeTaxCalculator, SalesTaxCalculator, 
            PropertyTaxCalculator, TaxRefundCalculator, GrossToNetCalculator,
            HourlyToSalaryCalculator, SalaryRaiseCalculator, CostOfLivingCalculator,
            CompoundInterestCalculator, RetirementCalculator, InvestmentReturnCalculator
        ]
        
        for calc_class in calculators:
            total += 1
            try:
                calc = calc_class()
                passed += 1
                print(f"✅ {calc_class.__name__}")
            except Exception as e:
                failed += 1
                print(f"❌ {calc_class.__name__}: {e}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        failed += 1
        total += 1
    
    return passed, failed, total

def test_basic_calculations():
    """Test basic calculator functionality"""
    print("Testing basic calculations...")
    passed = 0
    failed = 0
    total = 0
    
    tests = [
        {
            'name': 'Percentage Basic',
            'calc': 'PercentageCalculator',
            'inputs': {'operation': 'basic', 'x': '25', 'y': '100'},
            'expected': {'result': 25.0}
        },
        {
            'name': 'Percentage Increase',
            'calc': 'PercentageCalculator', 
            'inputs': {'operation': 'increase', 'original': '100', 'percent': '10'},
            'expected': {'result': 110.0}
        },
        {
            'name': 'BMI Metric',
            'calc': 'BMICalculator',
            'inputs': {'height': '175', 'weight': '70', 'unit_system': 'metric'},
            'expected': {'bmi': 22.86}
        },
        {
            'name': 'Tip Basic',
            'calc': 'TipCalculator',
            'inputs': {'bill_amount': '100', 'tip_percentage': '18', 'number_of_people': '1'},
            'expected': {'tip_amount': 18.0, 'total_amount': 118.0}
        },
        {
            'name': 'Loan Payment',
            'calc': 'LoanCalculator',
            'inputs': {'loan_amount': '100000', 'annual_rate': '5', 'loan_term_years': '30'},
            'expected': {'loan_amount': 100000.0}
        }
    ]
    
    try:
        from app_simple_fixed import (
            PercentageCalculator, LoanCalculator, BMICalculator, TipCalculator
        )
        
        calc_classes = {
            'PercentageCalculator': PercentageCalculator,
            'LoanCalculator': LoanCalculator,
            'BMICalculator': BMICalculator,
            'TipCalculator': TipCalculator
        }
        
        for test in tests:
            total += 1
            try:
                calc_class = calc_classes[test['calc']]
                calc = calc_class()
                result = calc.calculate(test['inputs'])
                
                # Check expected values
                test_passed = True
                for key, expected_val in test['expected'].items():
                    if key not in result:
                        test_passed = False
                        print(f"❌ {test['name']}: Missing key '{key}' in result")
                        break
                    
                    actual_val = result[key]
                    if isinstance(expected_val, float):
                        if abs(actual_val - expected_val) > 0.1:
                            test_passed = False
                            print(f"❌ {test['name']}: {key} = {actual_val}, expected {expected_val}")
                            break
                    else:
                        if actual_val != expected_val:
                            test_passed = False
                            print(f"❌ {test['name']}: {key} = {actual_val}, expected {expected_val}")
                            break
                
                if test_passed:
                    passed += 1
                    print(f"✅ {test['name']}")
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                print(f"❌ {test['name']}: {e}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        failed += len(tests)
        total += len(tests)
    
    return passed, failed, total

def test_input_validation():
    """Test input validation for calculators"""
    print("Testing input validation...")
    passed = 0
    failed = 0
    total = 0
    
    try:
        from app_simple_fixed import PercentageCalculator, LoanCalculator
        
        # Test validation that should pass
        total += 1
        try:
            calc = PercentageCalculator()
            valid = calc.validate_inputs({'operation': 'basic', 'x': '25', 'y': '100'})
            if valid:
                passed += 1
                print("✅ Valid inputs accepted")
            else:
                failed += 1
                print(f"❌ Valid inputs rejected: {calc.errors}")
        except Exception as e:
            failed += 1
            print(f"❌ Validation test error: {e}")
        
        # Test validation that should fail
        total += 1
        try:
            calc = PercentageCalculator()
            valid = calc.validate_inputs({'operation': 'basic', 'x': '25'})  # Missing 'y'
            if not valid and len(calc.errors) > 0:
                passed += 1
                print("✅ Invalid inputs rejected")
            else:
                failed += 1
                print("❌ Invalid inputs accepted")
        except Exception as e:
            failed += 1
            print(f"❌ Validation test error: {e}")
        
        # Test division by zero
        total += 1
        try:
            calc = PercentageCalculator()
            valid = calc.validate_inputs({'operation': 'basic', 'x': '25', 'y': '0'})
            if not valid:
                passed += 1
                print("✅ Division by zero rejected")
            else:
                failed += 1
                print("❌ Division by zero allowed")
        except Exception as e:
            failed += 1
            print(f"❌ Division by zero test error: {e}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        failed += 3
        total += 3
    
    return passed, failed, total

def test_meta_data():
    """Test that all calculators have proper meta data"""
    print("Testing calculator meta data...")
    passed = 0
    failed = 0
    total = 0
    
    try:
        from app_simple_fixed import (
            PercentageCalculator, LoanCalculator, BMICalculator, TipCalculator
        )
        
        calculators = [PercentageCalculator(), LoanCalculator(), BMICalculator(), TipCalculator()]
        
        for calc in calculators:
            total += 1
            try:
                meta = calc.get_meta_data()
                required_keys = ['title', 'description', 'keywords', 'canonical']
                
                if all(key in meta for key in required_keys):
                    if len(meta['description']) <= 160:  # SEO best practice
                        passed += 1
                        print(f"✅ {calc.__class__.__name__} meta data")
                    else:
                        failed += 1
                        print(f"❌ {calc.__class__.__name__}: Description too long ({len(meta['description'])} chars)")
                else:
                    failed += 1
                    missing = [key for key in required_keys if key not in meta]
                    print(f"❌ {calc.__class__.__name__}: Missing keys {missing}")
                    
            except Exception as e:
                failed += 1
                print(f"❌ {calc.__class__.__name__}: {e}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        failed += 4
        total += 4
    
    return passed, failed, total

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("Testing edge cases...")
    passed = 0
    failed = 0
    total = 0
    
    edge_tests = [
        {
            'name': 'Zero interest loan',
            'calc': 'LoanCalculator',
            'inputs': {'loan_amount': '12000', 'annual_rate': '0', 'loan_term_years': '1'},
            'check': lambda r: r['monthly_payment'] == 1000.0 and r['total_interest'] == 0.0
        },
        {
            'name': 'Very large loan',
            'calc': 'LoanCalculator', 
            'inputs': {'loan_amount': '10000000', 'annual_rate': '4', 'loan_term_years': '30'},
            'check': lambda r: r['monthly_payment'] > 40000
        },
        {
            'name': 'Extreme BMI - low',
            'calc': 'BMICalculator',
            'inputs': {'height': '180', 'weight': '30', 'unit_system': 'metric'},
            'check': lambda r: r['bmi'] < 15 and 'underweight' in r['category'].lower()
        },
        {
            'name': 'High tip percentage',
            'calc': 'TipCalculator',
            'inputs': {'bill_amount': '100', 'tip_percentage': '50', 'number_of_people': '1'},
            'check': lambda r: r['tip_amount'] == 50.0
        }
    ]
    
    try:
        from app_simple_fixed import LoanCalculator, BMICalculator, TipCalculator
        
        calc_classes = {
            'LoanCalculator': LoanCalculator,
            'BMICalculator': BMICalculator, 
            'TipCalculator': TipCalculator
        }
        
        for test in edge_tests:
            total += 1
            try:
                calc_class = calc_classes[test['calc']]
                calc = calc_class()
                result = calc.calculate(test['inputs'])
                
                if test['check'](result):
                    passed += 1
                    print(f"✅ {test['name']}")
                else:
                    failed += 1
                    print(f"❌ {test['name']}: Check failed")
                    
            except Exception as e:
                failed += 1
                print(f"❌ {test['name']}: {e}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        failed += len(edge_tests)
        total += len(edge_tests)
    
    return passed, failed, total

def main():
    """Run all test groups"""
    print("🚀 Calculator Suite Simple Test Runner")
    print("Running tests without external dependencies...")
    
    # Run test groups
    results = []
    
    results.append(("Calculator Imports", run_test_group("Calculator Imports", test_calculator_imports)))
    results.append(("Basic Calculations", run_test_group("Basic Calculations", test_basic_calculations)))
    results.append(("Input Validation", run_test_group("Input Validation", test_input_validation)))
    results.append(("Meta Data", run_test_group("Meta Data Generation", test_meta_data)))
    results.append(("Edge Cases", run_test_group("Edge Cases", test_edge_cases)))
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed_groups = sum(1 for _, success in results if success)
    total_groups = len(results)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {description}")
    
    print(f"\n🎯 OVERALL: {passed_groups}/{total_groups} test groups passed")
    
    if passed_groups == total_groups:
        print("🎉 All tests passed! Calculator Suite is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)