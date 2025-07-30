#!/usr/bin/env python3
"""
Test script for Enhanced Calculator Suite
Tests all calculators to ensure they work properly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced calculators
from app_complete_enhanced import *

def test_percentage_calculator():
    """Test the enhanced percentage calculator"""
    print("Testing Percentage Calculator...")
    
    calc = PercentageCalculator()
    
    # Test basic percentage
    result = calc.calculate({
        'operation': 'basic',
        'x': '25',
        'y': '100'
    })
    
    assert result['result'] == 25.0, f"Expected 25.0, got {result['result']}"
    assert 'explanation' in result, "Missing explanation"
    assert 'step_by_step' in result, "Missing step-by-step"
    print("✅ Basic percentage test passed")
    
    # Test percentage increase
    result = calc.calculate({
        'operation': 'increase',
        'original': '100',
        'percent': '15'
    })
    
    assert result['result'] == 115.0, f"Expected 115.0, got {result['result']}"
    print("✅ Percentage increase test passed")
    
    print("✅ Percentage Calculator - All tests passed!\n")

def test_loan_calculator():
    """Test the enhanced loan calculator"""
    print("Testing Loan Calculator...")
    
    calc = LoanCalculator()
    
    result = calc.calculate({
        'loan_amount': '250000',
        'annual_rate': '6.5',
        'loan_term_years': '30',
        'extra_payment': '100',
        'loan_type': 'mortgage'
    })
    
    assert 'monthly_payment' in result, "Missing monthly payment"
    assert 'total_interest' in result, "Missing total interest"
    assert 'with_extra_payments' in result, "Missing extra payment analysis"
    assert 'amortization_sample' in result, "Missing amortization schedule"
    assert 'affordability_analysis' in result, "Missing affordability analysis"
    
    assert result['monthly_payment'] > 0, "Monthly payment should be positive"
    assert result['total_interest'] > 0, "Total interest should be positive"
    
    print("✅ Loan Calculator - All tests passed!\n")

def test_tip_calculator():
    """Test the enhanced tip calculator"""
    print("Testing Tip Calculator...")
    
    calc = TipCalculator()
    
    result = calc.calculate({
        'bill_amount': '85.50',
        'tip_percentage': '18',
        'number_of_people': '4',
        'tax_amount': '7.25',
        'service_quality': 'good',
        'restaurant_type': 'casual'
    })
    
    assert 'tip_amount' in result, "Missing tip amount"
    assert 'total_amount' in result, "Missing total amount"
    assert 'amount_per_person' in result, "Missing per person amount"
    assert 'tipping_guide' in result, "Missing tipping guide"
    assert 'tip_scenarios' in result, "Missing tip scenarios"
    assert 'cultural_info' in result, "Missing cultural info"
    
    # Verify calculations
    expected_tip = 85.50 * 0.18
    assert abs(result['tip_amount'] - expected_tip) < 0.01, f"Tip calculation error"
    
    print("✅ Tip Calculator - All tests passed!\n")

def test_bmi_calculator():
    """Test the enhanced BMI calculator"""
    print("Testing BMI Calculator...")
    
    calc = BMICalculator()
    
    # Test metric system
    result = calc.calculate({
        'height': '175',
        'weight': '70',
        'unit_system': 'metric',
        'age': '30',
        'gender': 'male'
    })
    
    assert 'bmi' in result, "Missing BMI"
    assert 'category' in result, "Missing BMI category"
    assert 'ideal_weight_range' in result, "Missing ideal weight range"
    assert 'health_recommendations' in result, "Missing health recommendations"
    
    # Verify BMI calculation: 70 / (1.75)^2 = 22.86
    expected_bmi = 70 / (1.75 ** 2)
    assert abs(result['bmi'] - expected_bmi) < 0.1, f"BMI calculation error"
    assert result['category'] == 'Normal weight', f"Wrong BMI category: {result['category']}"
    
    print("✅ BMI Calculator - All tests passed!\n")

def test_compound_interest_calculator():
    """Test the enhanced compound interest calculator"""
    print("Testing Compound Interest Calculator...")
    
    calc = CompoundInterestCalculator()
    
    result = calc.calculate({
        'principal': '10000',
        'annual_rate': '7',
        'years': '10',
        'compound_frequency': '12',
        'monthly_contribution': '500'
    })
    
    assert 'total_value' in result, "Missing total value"
    assert 'total_interest' in result, "Missing total interest"
    assert 'yearly_breakdown' in result, "Missing yearly breakdown"
    assert 'doubling_time' in result, "Missing doubling time"
    
    assert result['total_value'] > result['principal'], "Total should be greater than principal"
    assert result['total_interest'] > 0, "Interest should be positive"
    
    # Rule of 72 check: 72/7 ≈ 10.3 years to double
    expected_doubling_time = 72 / 7
    assert abs(result['doubling_time'] - expected_doubling_time) < 0.1, "Rule of 72 error"
    
    print("✅ Compound Interest Calculator - All tests passed!\n")

def test_mortgage_calculator():
    """Test the enhanced mortgage calculator"""
    print("Testing Mortgage Calculator...")
    
    calc = MortgageCalculator()
    
    result = calc.calculate({
        'home_price': '450000',
        'down_payment_percent': '20',
        'annual_rate': '7.0',
        'loan_term_years': '30',
        'property_tax_annual': '6000',
        'home_insurance_annual': '1200',
        'hoa_monthly': '150'
    })
    
    assert 'loan_amount' in result, "Missing loan amount"
    assert 'monthly_principal_interest' in result, "Missing P&I payment"
    assert 'total_monthly_payment' in result, "Missing total payment"
    assert 'loan_to_value' in result, "Missing LTV"
    assert 'affordability_analysis' in result, "Missing affordability analysis"
    
    # Verify down payment calculation
    expected_down_payment = 450000 * 0.20
    assert result['down_payment'] == expected_down_payment, "Down payment calculation error"
    
    # Verify LTV
    expected_ltv = 80.0  # 20% down = 80% LTV
    assert result['loan_to_value'] == expected_ltv, f"LTV calculation error: {result['loan_to_value']}"
    
    print("✅ Mortgage Calculator - All tests passed!\n")

def run_all_tests():
    """Run all calculator tests"""
    print("🧮 Testing Enhanced Calculator Suite")
    print("=" * 50)
    
    try:
        test_percentage_calculator()
        test_loan_calculator()
        test_tip_calculator()
        test_bmi_calculator()
        test_compound_interest_calculator()
        test_mortgage_calculator()
        
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced Calculator Suite is working perfectly!")
        print("\nYour calculators are ready for use:")
        print("- Run: python app_complete_enhanced.py")
        print("- Visit: http://localhost:5000")
        print("- API: http://localhost:5000/api/calculators")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)