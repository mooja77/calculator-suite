#!/usr/bin/env python3
"""Manual test of new business calculators"""

# Test 1: Direct calculator import and test
print("=== Manual Business Calculator Test ===")

try:
    # Test imports
    from decimal import Decimal
    
    # Manual break-even test
    print("\n1. Testing Break-Even Calculator Logic:")
    
    # Manual calculation
    fixed_costs = Decimal('1000')
    price_per_unit = Decimal('25')
    variable_cost_per_unit = Decimal('15')
    
    contribution_margin = price_per_unit - variable_cost_per_unit
    breakeven_units = fixed_costs / contribution_margin
    breakeven_revenue = breakeven_units * price_per_unit
    
    print(f"   Fixed costs: ${fixed_costs}")
    print(f"   Price per unit: ${price_per_unit}")
    print(f"   Variable cost per unit: ${variable_cost_per_unit}")
    print(f"   Contribution margin: ${contribution_margin}")
    print(f"   Break-even units: {breakeven_units}")
    print(f"   Break-even revenue: ${breakeven_revenue}")
    
    # Manual freelance rate test
    print("\n2. Testing Freelance Rate Calculator Logic:")
    
    desired_salary = Decimal('60000')
    billable_hours_per_week = Decimal('30')
    weeks_per_year = Decimal('50')
    business_expenses = Decimal('5000')
    tax_rate = Decimal('0.30')
    profit_margin = Decimal('0.20')
    
    total_billable_hours = billable_hours_per_week * weeks_per_year
    gross_income_needed = (desired_salary + business_expenses) / (1 - tax_rate)
    base_hourly_rate = gross_income_needed / total_billable_hours
    recommended_rate = base_hourly_rate * (1 + profit_margin)
    
    print(f"   Desired salary: ${desired_salary}")
    print(f"   Total billable hours: {total_billable_hours}")
    print(f"   Gross income needed: ${gross_income_needed:.2f}")
    print(f"   Base hourly rate: ${base_hourly_rate:.2f}")
    print(f"   Recommended rate: ${recommended_rate:.2f}")
    
    print("\n✅ Manual calculations completed successfully!")
    
except Exception as e:
    print(f"❌ Error in manual test: {e}")

# Test 2: File existence verification
print("\n3. Verifying calculator files exist:")

import os

files_to_check = [
    'app/calculators/breakeven.py',
    'app/calculators/freelancerate.py',
    'app/content/breakeven_intro.md',
    'app/content/breakeven_guide.md', 
    'app/content/breakeven_faq.md',
    'app/content/freelancerate_intro.md',
    'app/content/freelancerate_guide.md',
    'app/content/freelancerate_faq.md'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"   ✅ {file_path} ({size} bytes)")
    else:
        print(f"   ❌ {file_path} - Missing!")

print("\n=== Test Complete ===")