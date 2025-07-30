#\!/usr/bin/env python3
"""
Test script for new money management calculators
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("🧪 Testing New Money Management Calculators")
print("=" * 50)

# Test 1: Basic import test
print("\n=== Test 1: Import Test ===")
try:
    from app.calculators.budget import BudgetCalculator
    from app.calculators.emergencyfund import EmergencyFundCalculator
    from app.calculators.debtpayoff import DebtPayoffCalculator
    from app.calculators.creditcardpayoff import CreditCardPayoffCalculator
    print("✅ All calculator imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Calculator instantiation
print("\n=== Test 2: Instantiation Test ===")
try:
    budget_calc = BudgetCalculator()
    emergency_calc = EmergencyFundCalculator()
    debt_calc = DebtPayoffCalculator()
    cc_calc = CreditCardPayoffCalculator()
    print("✅ All calculators instantiated successfully")
    print(f"   Budget slug: {budget_calc.slug}")
    print(f"   Emergency slug: {emergency_calc.slug}")
    print(f"   Debt slug: {debt_calc.slug}")
    print(f"   Credit card slug: {cc_calc.slug}")
except Exception as e:
    print(f"❌ Instantiation failed: {e}")
    sys.exit(1)

# Test 3: Registry test
print("\n=== Test 3: Registry Test ===")
try:
    from app.calculators.registry import calculator_registry
    from app.calculators import *
    
    expected = ['budget', 'emergencyfund', 'debtpayoff', 'creditcardpayoff']
    registered = calculator_registry.list_slugs()
    
    for calc_slug in expected:
        if calc_slug in registered:
            print(f"✅ {calc_slug} registered successfully")
        else:
            print(f"❌ {calc_slug} not registered")
    
    print(f"   Total registered calculators: {len(registered)}")
except Exception as e:
    print(f"❌ Registry test failed: {e}")

# Test 4: Basic functionality
print("\n=== Test 4: Basic Functionality Test ===")

# Budget Calculator test
try:
    calc = BudgetCalculator()
    inputs = {'monthly_income': 5000}
    if calc.validate_inputs(inputs):
        result = calc.calculate(inputs)
        print(f"✅ Budget Calculator: Income ${result['monthly_income']}, Needs ${result['allocations']['needs']['amount']}")
    else:
        print(f"❌ Budget validation failed: {calc.errors}")
except Exception as e:
    print(f"❌ Budget Calculator failed: {e}")

# Emergency Fund Calculator test
try:
    calc = EmergencyFundCalculator()
    inputs = {
        'monthly_expenses': 3000,
        'current_emergency_fund': 5000,
        'monthly_savings_capacity': 300,
        'job_security': 'stable'
    }
    if calc.validate_inputs(inputs):
        result = calc.calculate(inputs)
        print(f"✅ Emergency Fund Calculator: Recommended ${result['fund_recommendations']['recommended_amount']}")
    else:
        print(f"❌ Emergency fund validation failed: {calc.errors}")
except Exception as e:
    print(f"❌ Emergency Fund Calculator failed: {e}")

print("\n" + "=" * 50)
print("🎉 Tests completed\! Check results above.")
EOF < /dev/null
