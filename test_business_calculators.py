#!/usr/bin/env python3
"""
Test suite for new business calculators
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.calculators.breakeven import BreakevenCalculator
from app.calculators.freelancerate import FreelancerateCalculator

def test_breakeven_calculator():
    """Test break-even calculator with realistic business scenarios"""
    print("🧮 Testing Break-Even Calculator...")
    
    calc = BreakevenCalculator()
    
    # Test Case 1: Small retail business
    test_data_1 = {
        'fixed_costs': 5000,  # Monthly rent, utilities, base salary
        'price_per_unit': 25,  # Product price
        'variable_cost_per_unit': 15,  # Materials, shipping
        'current_sales': 600,  # Current monthly sales
        'target_profit': 2000,  # Desired monthly profit
        'currency': 'USD'
    }
    
    result_1 = calc.calculate(test_data_1)
    
    if 'errors' in result_1:
        print(f"❌ Test 1 failed: {result_1['errors']}")
        return False
    
    print(f"✅ Test 1 - Small Retail Business:")
    print(f"   Break-even units: {result_1['breakeven_units']}")
    print(f"   Break-even revenue: ${result_1['breakeven_revenue']:,.2f}")
    print(f"   Contribution margin: {result_1['contribution_margin_ratio']:.1f}%")
    print(f"   Current profit: ${result_1['current_profit']:,.2f}")
    print(f"   Safety margin: {result_1['safety_margin_percentage']:.1f}%")
    
    # Test Case 2: Service business (consulting)
    test_data_2 = {
        'fixed_costs': 8000,  # Monthly overhead
        'price_per_unit': 150,  # Hourly rate
        'variable_cost_per_unit': 30,  # Direct costs per hour
        'current_sales': 80,  # Hours per month
        'currency': 'USD'
    }
    
    result_2 = calc.calculate(test_data_2)
    
    if 'errors' in result_2:
        print(f"❌ Test 2 failed: {result_2['errors']}")
        return False
    
    print(f"\n✅ Test 2 - Consulting Business:")
    print(f"   Break-even hours: {result_2['breakeven_units']:.1f}")
    print(f"   Break-even revenue: ${result_2['breakeven_revenue']:,.2f}")
    print(f"   Contribution margin: {result_2['contribution_margin_ratio']:.1f}%")
    
    # Test validation
    invalid_data = {
        'fixed_costs': 1000,
        'price_per_unit': 10,
        'variable_cost_per_unit': 15,  # Higher than price - should fail
    }
    
    result_invalid = calc.calculate(invalid_data)
    if 'errors' not in result_invalid:
        print("❌ Validation test failed - should have caught variable cost > price")
        return False
    
    print("✅ Validation test passed")
    return True

def test_freelance_rate_calculator():
    """Test freelance rate calculator with realistic scenarios"""
    print("\n💼 Testing Freelance Rate Calculator...")
    
    calc = FreelancerateCalculator()
    
    # Test Case 1: Mid-level developer
    test_data_1 = {
        'desired_salary': 75000,  # Annual target income
        'billable_hours_per_week': 30,  # Realistic billable hours
        'weeks_per_year': 50,  # 2 weeks vacation
        'business_expenses': 5000,  # Annual business costs
        'health_insurance': 6000,  # Annual health insurance
        'retirement_contribution': 7500,  # 10% of desired salary
        'tax_rate': 30,  # Conservative tax estimate
        'profit_margin': 20,  # 20% profit margin
        'currency': 'USD'
    }
    
    result_1 = calc.calculate(test_data_1)
    
    if 'errors' in result_1:
        print(f"❌ Test 1 failed: {result_1['errors']}")
        return False
    
    print(f"✅ Test 1 - Mid-Level Developer:")
    print(f"   Recommended rate: ${result_1['recommended_rate']:.2f}/hour")
    print(f"   Annual revenue: ${result_1['annual_revenue']:,.2f}")
    print(f"   Monthly revenue: ${result_1['monthly_revenue']:,.2f}")
    print(f"   Employee equivalent: ${result_1['employee_equivalent']:,.2f}")
    print(f"   Total billable hours: {result_1['total_billable_hours']}")
    
    # Test Case 2: New freelancer (conservative)
    test_data_2 = {
        'desired_salary': 45000,
        'billable_hours_per_week': 25,
        'weeks_per_year': 48,  # More time off as new freelancer
        'business_expenses': 2000,
        'health_insurance': 4800,
        'tax_rate': 25,
        'profit_margin': 15,
        'currency': 'USD'
    }
    
    result_2 = calc.calculate(test_data_2)
    
    if 'errors' in result_2:
        print(f"❌ Test 2 failed: {result_2['errors']}")
        return False
        
    print(f"\n✅ Test 2 - New Freelancer:")
    print(f"   Recommended rate: ${result_2['recommended_rate']:.2f}/hour")
    print(f"   Day rate (8 hours): ${result_2['payment_structures']['daily']['rate']:.2f}")
    print(f"   Weekly revenue: ${result_2['weekly_revenue']:,.2f}")
    
    # Test Case 3: High-end consultant
    test_data_3 = {
        'desired_salary': 150000,
        'billable_hours_per_week': 25,  # Less hours, higher value
        'business_expenses': 15000,
        'health_insurance': 8000,
        'retirement_contribution': 20000,
        'tax_rate': 35,
        'profit_margin': 25,
    }
    
    result_3 = calc.calculate(test_data_3)
    
    if 'errors' in result_3:
        print(f"❌ Test 3 failed: {result_3['errors']}")
        return False
        
    print(f"\n✅ Test 3 - High-End Consultant:")
    print(f"   Recommended rate: ${result_3['recommended_rate']:.2f}/hour")
    print(f"   Project rate (+15%): ${result_3['payment_structures']['project_multiplier']['rate']:.2f}/hour")
    
    # Test validation - too many billable hours
    high_hours_data = {
        'desired_salary': 60000,
        'billable_hours_per_week': 45,  # Should trigger warning
    }
    
    result_warning = calc.calculate(high_hours_data)
    if 'errors' not in result_warning:
        print("❌ Validation test failed - should warn about high hours")
        return False
        
    print("✅ High hours validation test passed")
    return True

def test_calculator_registration():
    """Test that calculators are properly registered"""
    print("\n🔗 Testing Calculator Registration...")
    
    from app.calculators.registry import calculator_registry
    
    # Import calculators to trigger registration
    import app.calculators.breakeven
    import app.calculators.freelancerate
    
    all_calculators = calculator_registry.get_all()
    
    if 'breakeven' not in all_calculators:
        print("❌ Break-even calculator not registered")
        return False
        
    if 'freelancerate' not in all_calculators:
        print("❌ Freelance rate calculator not registered")
        return False
    
    print("✅ Both calculators properly registered")
    
    # Test instantiation
    breakeven_calc = all_calculators['breakeven']()
    freelance_calc = all_calculators['freelancerate']()
    
    print(f"✅ Break-even calculator slug: {breakeven_calc.slug}")
    print(f"✅ Freelance rate calculator slug: {freelance_calc.slug}")
    
    return True

def main():
    """Run all business calculator tests"""
    print("🚀 Business Calculator Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    try:
        if test_breakeven_calculator():
            tests_passed += 1
            
        if test_freelance_rate_calculator():
            tests_passed += 1
            
        if test_calculator_registration():
            tests_passed += 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All business calculator tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)