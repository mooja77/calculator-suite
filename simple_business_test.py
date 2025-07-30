#!/usr/bin/env python3
"""
Simple test for business calculators
"""
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Testing Business Calculators...")

try:
    # Test Break-Even Calculator
    from app.calculators.breakeven import BreakevenCalculator
    
    calc = BreakevenCalculator()
    print(f"✅ Break-even calculator created: {calc.slug}")
    
    # Simple test
    test_data = {
        'fixed_costs': 1000,
        'price_per_unit': 20,
        'variable_cost_per_unit': 10,
    }
    
    result = calc.calculate(test_data)
    
    if 'errors' in result:
        print(f"❌ Break-even test failed: {result['errors']}")
    else:
        print(f"✅ Break-even calculation successful:")
        print(f"   Break-even units: {result['breakeven_units']}")
        print(f"   Break-even revenue: ${result['breakeven_revenue']}")
        
except Exception as e:
    print(f"❌ Break-even calculator error: {e}")

try:
    # Test Freelance Rate Calculator  
    from app.calculators.freelancerate import FreelancerateCalculator
    
    calc2 = FreelancerateCalculator()
    print(f"✅ Freelance rate calculator created: {calc2.slug}")
    
    # Simple test
    test_data2 = {
        'desired_salary': 60000,
        'billable_hours_per_week': 30,
    }
    
    result2 = calc2.calculate(test_data2)
    
    if 'errors' in result2:
        print(f"❌ Freelance rate test failed: {result2['errors']}")
    else:
        print(f"✅ Freelance rate calculation successful:")
        print(f"   Recommended rate: ${result2['recommended_rate']:.2f}/hour")
        print(f"   Annual revenue: ${result2['annual_revenue']:,.2f}")
        
except Exception as e:
    print(f"❌ Freelance rate calculator error: {e}")

print("\nTest completed!")