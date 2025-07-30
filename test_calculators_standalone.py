#!/usr/bin/env python3
"""
Standalone Test for Enhanced Calculator Classes
Tests all calculator logic without Flask dependencies
"""

import os
import json
import time
import math
from datetime import datetime, timedelta
from collections import defaultdict

# Enhanced Base Calculator Class (copied from main app)
class BaseCalculator:
    def __init__(self):
        self.slug = self.__class__.__name__.lower().replace('calculator', '')
        self.errors = []
        self.warnings = []
        self.tips = []
        self.related_calculators = []
        
    def clear_errors(self):
        self.errors = []
        self.warnings = []
        self.tips = []
    
    def add_error(self, message):
        self.errors.append(message)
    
    def add_warning(self, message):
        self.warnings.append(message)
        
    def add_tip(self, message):
        self.tips.append(message)
    
    def validate_number(self, value, field_name, min_val=None, max_val=None, allow_zero=True):
        try:
            if value == '' or value is None:
                self.add_error(f"{field_name} is required")
                return None
                
            num = float(value)
            
            if not allow_zero and num == 0:
                self.add_error(f"{field_name} cannot be zero")
                return None
                
            if min_val is not None and num < min_val:
                self.add_error(f"{field_name} must be at least {min_val}")
                return None
                
            if max_val is not None and num > max_val:
                self.add_error(f"{field_name} must be at most {max_val}")
                return None
                
            return num
        except (ValueError, TypeError):
            self.add_error(f"{field_name} must be a valid number")
            return None
    
    def validate_percentage(self, value, field_name, min_val=0, max_val=100):
        return self.validate_number(value, field_name, min_val, max_val)
    
    def validate_positive_number(self, value, field_name):
        return self.validate_number(value, field_name, min_val=0.01)
    
    def get_explanation(self):
        return "Calculator explanation not implemented"

# Enhanced Percentage Calculator
class PercentageCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['tip', 'salaryraise', 'investmentreturn']
    
    def calculate(self, inputs):
        try:
            operation = inputs.get('operation', 'basic')
            
            if operation == 'basic':
                x = self.validate_number(inputs.get('x'), 'First Number')
                y = self.validate_number(inputs.get('y'), 'Second Number', allow_zero=False)
                if self.errors:
                    return {'errors': self.errors}
                result = (x / y) * 100
                
            elif operation == 'find_value':
                percent = self.validate_percentage(inputs.get('percent'), 'Percentage', 0, 1000)
                total = self.validate_number(inputs.get('total'), 'Total Value')
                if self.errors:
                    return {'errors': self.errors}
                result = (percent / 100) * total
                
            elif operation == 'increase':
                original = self.validate_number(inputs.get('original'), 'Original Value')
                percent = self.validate_percentage(inputs.get('percent'), 'Increase Percentage', 0, 1000)
                if self.errors:
                    return {'errors': self.errors}
                result = original * (1 + percent / 100)
                
            elif operation == 'decrease':
                original = self.validate_number(inputs.get('original'), 'Original Value')
                percent = self.validate_percentage(inputs.get('percent'), 'Decrease Percentage', 0, 100)
                if self.errors:
                    return {'errors': self.errors}
                result = original * (1 - percent / 100)
                
            elif operation == 'change':
                original = self.validate_number(inputs.get('original'), 'Original Value', allow_zero=False)
                new_value = self.validate_number(inputs.get('new_value'), 'New Value')
                if self.errors:
                    return {'errors': self.errors}
                result = ((new_value - original) / original) * 100
                
            else:
                return {'error': f'Unknown operation: {operation}'}
            
            return {
                'result': round(result, 4),
                'operation': operation,
                'inputs': inputs,
                'formula': self._get_formula(operation),
                'explanation': self._get_explanation(operation, inputs, result),
                'step_by_step': self._get_step_by_step(operation, inputs, result)
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _get_formula(self, operation):
        formulas = {
            'basic': '(X ÷ Y) × 100',
            'find_value': '(Percentage ÷ 100) × Total',
            'increase': 'Original × (1 + Percentage ÷ 100)',
            'decrease': 'Original × (1 - Percentage ÷ 100)',
            'change': '((New Value - Original) ÷ Original) × 100'
        }
        return formulas.get(operation, 'Formula not available')
    
    def _get_explanation(self, operation, inputs, result):
        explanations = {
            'basic': f"{inputs.get('x')} is {result:.2f}% of {inputs.get('y')}",
            'find_value': f"{inputs.get('percent')}% of {inputs.get('total')} is {result:.2f}",
            'increase': f"{inputs.get('original')} increased by {inputs.get('percent')}% equals {result:.2f}",
            'decrease': f"{inputs.get('original')} decreased by {inputs.get('percent')}% equals {result:.2f}",
            'change': f"The percentage change from {inputs.get('original')} to {inputs.get('new_value')} is {result:.2f}%"
        }
        return explanations.get(operation, 'Explanation not available')
    
    def _get_step_by_step(self, operation, inputs, result):
        if operation == 'basic':
            x_val = float(inputs.get('x'))
            y_val = float(inputs.get('y'))
            division_result = x_val / y_val
            return [
                f"Step 1: Divide {x_val} by {y_val}",
                f"Step 2: {x_val} ÷ {y_val} = {division_result:.4f}",
                f"Step 3: Multiply by 100 to get percentage",
                f"Step 4: {division_result:.4f} × 100 = {result:.2f}%"
            ]
        return []

# Enhanced Loan Calculator
class LoanCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['mortgage', 'compoundinterest']
    
    def calculate(self, inputs):
        try:
            loan_amount = self.validate_positive_number(inputs.get('loan_amount'), 'Loan Amount')
            annual_rate = self.validate_number(inputs.get('annual_rate'), 'Annual Interest Rate', 0, 50)
            loan_term_years = self.validate_positive_number(inputs.get('loan_term_years'), 'Loan Term (Years)')
            
            if self.errors:
                return {'errors': self.errors}
            
            loan_type = inputs.get('loan_type', 'personal')
            extra_payment = float(inputs.get('extra_payment', 0))
            
            monthly_rate = annual_rate / 100 / 12
            num_payments = loan_term_years * 12
            
            if monthly_rate == 0:
                monthly_payment = loan_amount / num_payments
            else:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            total_paid = monthly_payment * num_payments
            total_interest = total_paid - loan_amount
            
            # Add insights
            if annual_rate > 15:
                self.add_warning(f"Interest rate of {annual_rate}% is quite high.")
            if annual_rate < 3:
                self.add_tip("Excellent interest rate! Consider extra payments.")
            
            return {
                'loan_amount': round(loan_amount, 2),
                'annual_rate': annual_rate,
                'loan_term_years': loan_term_years,
                'monthly_payment': round(monthly_payment, 2),
                'total_paid': round(total_paid, 2),
                'total_interest': round(total_interest, 2),
                'loan_type': loan_type,
                'extra_payment': extra_payment,
                'warnings': self.warnings,
                'tips': self.tips,
                'inputs': inputs
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}

# Enhanced Tip Calculator
class TipCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['percentage', 'salestax']
    
    def calculate(self, inputs):
        try:
            bill_amount = self.validate_positive_number(inputs.get('bill_amount'), 'Bill Amount')
            tip_percentage = self.validate_percentage(inputs.get('tip_percentage'), 'Tip Percentage', 0, 100)
            number_of_people = int(self.validate_positive_number(inputs.get('number_of_people', 1), 'Number of People'))
            
            if self.errors:
                return {'errors': self.errors}
            
            tax_amount = float(inputs.get('tax_amount', 0))
            
            tip_amount = bill_amount * (tip_percentage / 100)
            total_amount = bill_amount + tip_amount + tax_amount
            amount_per_person = total_amount / number_of_people
            tip_per_person = tip_amount / number_of_people
            
            return {
                'bill_amount': round(bill_amount, 2),
                'tip_percentage': tip_percentage,
                'tip_amount': round(tip_amount, 2),
                'tax_amount': round(tax_amount, 2),
                'total_amount': round(total_amount, 2),
                'number_of_people': number_of_people,
                'amount_per_person': round(amount_per_person, 2),
                'tip_per_person': round(tip_per_person, 2),
                'inputs': inputs
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}

# Test Functions
def test_percentage_calculator():
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
    print("✅ Basic percentage: 25 is 25% of 100")
    
    # Test percentage increase
    result = calc.calculate({
        'operation': 'increase',
        'original': '100',
        'percent': '15'
    })
    
    assert result['result'] == 115.0, f"Expected 115.0, got {result['result']}"
    print("✅ Percentage increase: 100 + 15% = 115")
    
    # Test error handling
    result = calc.calculate({
        'operation': 'basic',
        'x': '25',
        'y': '0'  # Division by zero
    })
    
    assert 'errors' in result, "Should have validation errors"
    print("✅ Error handling: Division by zero properly caught")
    
    print("✅ Percentage Calculator - All tests passed!\n")

def test_loan_calculator():
    print("Testing Loan Calculator...")
    calc = LoanCalculator()
    
    result = calc.calculate({
        'loan_amount': '250000',
        'annual_rate': '6.5',
        'loan_term_years': '30',
        'loan_type': 'mortgage'
    })
    
    assert 'monthly_payment' in result, "Missing monthly payment"
    assert 'total_interest' in result, "Missing total interest"
    assert result['monthly_payment'] > 0, "Monthly payment should be positive"
    assert result['total_interest'] > 0, "Total interest should be positive"
    
    # Verify the payment is reasonable for a 30-year $250k loan at 6.5%
    # Should be around $1580
    expected_payment = 1580
    actual_payment = result['monthly_payment']
    assert abs(actual_payment - expected_payment) < 50, f"Payment seems wrong: {actual_payment}"
    
    print(f"✅ Loan calculation: ${result['loan_amount']:,.2f} at {result['annual_rate']}% = ${result['monthly_payment']:,.2f}/month")
    print("✅ Loan Calculator - All tests passed!\n")

def test_tip_calculator():
    print("Testing Tip Calculator...")
    calc = TipCalculator()
    
    result = calc.calculate({
        'bill_amount': '85.50',
        'tip_percentage': '18',
        'number_of_people': '4',
        'tax_amount': '7.25'
    })
    
    assert 'tip_amount' in result, "Missing tip amount"
    assert 'total_amount' in result, "Missing total amount"
    assert 'amount_per_person' in result, "Missing per person amount"
    
    # Verify calculations
    expected_tip = 85.50 * 0.18  # 15.39
    assert abs(result['tip_amount'] - expected_tip) < 0.01, f"Tip calculation error"
    
    expected_total = 85.50 + expected_tip + 7.25  # 108.14
    assert abs(result['total_amount'] - expected_total) < 0.01, f"Total calculation error"
    
    print(f"✅ Tip calculation: ${result['bill_amount']:.2f} + {result['tip_percentage']}% tip = ${result['total_amount']:.2f}")
    print(f"✅ Per person: ${result['amount_per_person']:.2f} each for {result['number_of_people']} people")
    print("✅ Tip Calculator - All tests passed!\n")

def run_all_tests():
    print("🧮 Testing Enhanced Calculator Logic")
    print("=" * 50)
    
    try:
        test_percentage_calculator()
        test_loan_calculator()
        test_tip_calculator()
        
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced Calculator logic is working perfectly!")
        print("\nThe calculators are ready for use in your Flask application.")
        print("\nTo run the full web application:")
        print("1. Install Flask: pip install flask")
        print("2. Run: python app_complete_enhanced.py")
        print("3. Visit: http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)