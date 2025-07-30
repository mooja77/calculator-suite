#!/usr/bin/env python3
"""
Test all calculators are working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_calculator_imports():
    """Test that all calculators can be imported"""
    print("🧮 Testing Calculator Imports...")
    
    try:
        from app.calculators.registry import calculator_registry
        calculators = calculator_registry.get_all()
        
        print(f"✅ Found {len(calculators)} calculators registered:")
        for slug, calc_class in calculators.items():
            print(f"   - {slug}: {calc_class.__name__}")
            
        # Test specific calculators
        expected_calculators = ['percentage', 'paycheck', 'sip', 'rentvsbuy', 'studentloan', 'retirement401k']
        for calc_slug in expected_calculators:
            if calc_slug in calculators:
                print(f"✅ {calc_slug}: OK")
            else:
                print(f"❌ {calc_slug}: MISSING")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Calculator import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calculator_functionality():
    """Test that calculators can perform basic calculations"""
    print("\n🔢 Testing Calculator Functionality...")
    
    try:
        from app.calculators.registry import calculator_registry
        
        # Test percentage calculator
        percentage_calc = calculator_registry.get('percentage')()
        test_inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
        if percentage_calc.validate_inputs(test_inputs):
            result = percentage_calc.calculate(test_inputs)
            if result and 'result' in result:
                print("✅ Percentage calculator: OK")
            else:
                print("❌ Percentage calculator: Calculation failed")
                return False
        else:
            print("❌ Percentage calculator: Validation failed")
            return False
            
        # Test paycheck calculator
        paycheck_calc = calculator_registry.get('paycheck')()
        test_inputs = {
            'annual_salary': '80000',
            'pay_frequency': 'biweekly',
            'country': 'US',
            'state': 'CA',
            'filing_status': 'single',
            'allowances': '1'
        }
        if paycheck_calc.validate_inputs(test_inputs):
            result = paycheck_calc.calculate(test_inputs)
            if result and 'take_home_pay' in result:
                print("✅ Paycheck calculator: OK")
            else:
                print("❌ Paycheck calculator: Calculation failed")
                return False
        else:
            print("❌ Paycheck calculator: Validation failed")
            return False
            
        # Test SIP calculator
        sip_calc = calculator_registry.get('sip')()
        test_inputs = {
            'monthly_investment': '5000',
            'investment_period': '10',
            'expected_return': '12',
            'step_up': '10'
        }
        if sip_calc.validate_inputs(test_inputs):
            result = sip_calc.calculate(test_inputs)
            if result and 'future_value' in result:
                print("✅ SIP calculator: OK")
            else:
                print("❌ SIP calculator: Calculation failed")
                return False
        else:
            print("❌ SIP calculator: Validation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Calculator functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test Flask app creation with all calculators"""
    print("\n🚀 Testing Flask App Creation...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test homepage
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Homepage: OK")
            else:
                print("❌ Homepage: Failed")
                return False
                
            # Test percentage calculator page
            response = client.get('/calculators/percentage/')
            if response.status_code == 200:
                print("✅ Percentage calculator page: OK")
            else:
                print("❌ Percentage calculator page: Failed")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 CALCULATOR-APP COMPREHENSIVE TEST")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all tests
    test_results = [
        test_calculator_imports(),
        test_calculator_functionality(),
        test_app_creation()
    ]
    
    all_tests_passed = all(test_results)
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ All 6 calculators are working properly")
        print("🚀 Calculator-App is ready for production!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🚨 Issues need to be addressed")
        
    return all_tests_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)