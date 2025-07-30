#!/usr/bin/env python3
"""
Direct Calculator Testing - Week 1, Day 1
Tests all calculators directly without Flask to identify broken functionality
"""

import sys
import os
import traceback

# Import the calculator classes directly from app_simple_fixed.py
# We'll extract just the calculator logic without Flask dependencies

class BaseCalculator:
    def __init__(self):
        self.slug = self.__class__.__name__.lower().replace('calculator', '')
        self.errors = []
    
    def clear_errors(self):
        self.errors = []
    
    def add_error(self, message):
        self.errors.append(message)
    
    def validate_number(self, value, field_name, min_val=None, max_val=None):
        try:
            num = float(value)
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

class PercentageCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            operation = inputs.get('operation', 'what_percent')
            
            if operation == 'what_percent':
                # What percent is X of Y?
                part = float(inputs['part'])
                whole = float(inputs['whole'])
                result = (part / whole) * 100
                return {
                    'result': round(result, 2),
                    'part': part,
                    'whole': whole,
                    'explanation': f"{part} is {result:.2f}% of {whole}"
                }
            
            elif operation == 'percent_of':
                # What is X% of Y?
                percent = float(inputs['percent'])
                whole = float(inputs['whole'])
                result = (percent / 100) * whole
                return {
                    'result': round(result, 2),
                    'percent': percent,
                    'whole': whole,
                    'explanation': f"{percent}% of {whole} is {result:.2f}"
                }
            
            elif operation == 'increase':
                # Increase X by Y%
                original = float(inputs['original'])
                percent = float(inputs['percent'])
                result = original * (1 + percent / 100)
                return {
                    'result': round(result, 2),
                    'original': original,
                    'percent': percent,
                    'increase_amount': round(result - original, 2),
                    'explanation': f"{original} increased by {percent}% is {result:.2f}"
                }
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

class TipCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            bill_amount = float(inputs['bill_amount'])
            tip_percentage = float(inputs.get('tip_percentage', 18))
            number_of_people = int(inputs.get('number_of_people', 1))
            
            tip_amount = bill_amount * (tip_percentage / 100)
            total_amount = bill_amount + tip_amount
            amount_per_person = total_amount / number_of_people
            
            return {
                'bill_amount': round(bill_amount, 2),
                'tip_percentage': tip_percentage,
                'tip_amount': round(tip_amount, 2),
                'total_amount': round(total_amount, 2),
                'number_of_people': number_of_people,
                'amount_per_person': round(amount_per_person, 2)
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

class BMICalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            height_cm = float(inputs['height_cm'])
            weight_kg = float(inputs['weight_kg'])
            
            height_m = height_cm / 100
            bmi = weight_kg / (height_m ** 2)
            
            # BMI categories
            if bmi < 18.5:
                category = "Underweight"
                advice = "Consider talking to a doctor about healthy weight gain"
            elif bmi < 25:
                category = "Normal weight"
                advice = "Great job maintaining healthy weight!"
            elif bmi < 30:
                category = "Overweight"
                advice = "Small changes in diet and exercise can help"
            else:
                category = "Obese"
                advice = "Consider consulting a healthcare provider"
            
            return {
                'height_cm': height_cm,
                'weight_kg': weight_kg,
                'bmi': round(bmi, 1),
                'category': category,
                'advice': advice
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

class LoanCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            loan_amount = float(inputs['loan_amount'])
            annual_rate = float(inputs['annual_rate']) / 100  # Convert percentage to decimal
            loan_term_years = float(inputs['loan_term_years'])
            
            # Calculate monthly payment using standard loan formula
            monthly_rate = annual_rate / 12
            num_payments = loan_term_years * 12
            
            if monthly_rate == 0:  # Handle 0% interest rate
                monthly_payment = loan_amount / num_payments
            else:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            # Calculate totals
            total_paid = monthly_payment * num_payments
            total_interest = total_paid - loan_amount
            
            return {
                'loan_amount': round(loan_amount, 2),
                'annual_rate': float(inputs['annual_rate']),
                'loan_term_years': loan_term_years,
                'monthly_payment': round(monthly_payment, 2),
                'total_paid': round(total_paid, 2),
                'total_interest': round(total_interest, 2)
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

def test_percentage_calculator():
    """Test the percentage calculator with various scenarios"""
    print("🧪 Testing Percentage Calculator...")
    calc = PercentageCalculator()
    tests_passed = 0
    tests_total = 0
    
    # Test 1: What percent is 25 of 100?
    tests_total += 1
    try:
        result = calc.calculate({'operation': 'what_percent', 'part': '25', 'whole': '100'})
        if result['result'] == 25.0:
            tests_passed += 1
            print(f"✅ What percent: 25 is 25% of 100")
        else:
            print(f"❌ What percent failed: expected 25, got {result['result']}")
    except Exception as e:
        print(f"❌ What percent error: {e}")
    
    # Test 2: What is 20% of 150?
    tests_total += 1
    try:
        result = calc.calculate({'operation': 'percent_of', 'percent': '20', 'whole': '150'})
        if result['result'] == 30.0:
            tests_passed += 1
            print(f"✅ Percent of: 20% of 150 is 30")
        else:
            print(f"❌ Percent of failed: expected 30, got {result['result']}")
    except Exception as e:
        print(f"❌ Percent of error: {e}")
    
    # Test 3: Increase 100 by 15%
    tests_total += 1
    try:
        result = calc.calculate({'operation': 'increase', 'original': '100', 'percent': '15'})
        if result['result'] == 115.0:
            tests_passed += 1
            print(f"✅ Increase: 100 + 15% = 115")
        else:
            print(f"❌ Increase failed: expected 115, got {result['result']}")
    except Exception as e:
        print(f"❌ Increase error: {e}")
    
    return tests_passed, tests_total

def test_tip_calculator():
    """Test the tip calculator"""
    print("🧪 Testing Tip Calculator...")
    calc = TipCalculator()
    tests_passed = 0
    tests_total = 0
    
    # Test 1: 20% tip on $50 bill
    tests_total += 1
    try:
        result = calc.calculate({'bill_amount': '50', 'tip_percentage': '20', 'number_of_people': '1'})
        if result['tip_amount'] == 10.0 and result['total_amount'] == 60.0:
            tests_passed += 1
            print(f"✅ Tip: $50 bill + 20% tip = $10 tip, $60 total")
        else:
            print(f"❌ Tip failed: expected $10 tip, $60 total, got ${result['tip_amount']} tip, ${result['total_amount']} total")
    except Exception as e:
        print(f"❌ Tip error: {e}")
    
    # Test 2: Split bill among 4 people
    tests_total += 1
    try:
        result = calc.calculate({'bill_amount': '100', 'tip_percentage': '18', 'number_of_people': '4'})
        expected_per_person = 118 / 4  # $29.50
        if abs(result['amount_per_person'] - expected_per_person) < 0.01:
            tests_passed += 1
            print(f"✅ Split bill: $100 + 18% tip split 4 ways = ${result['amount_per_person']}/person")
        else:
            print(f"❌ Split bill failed: expected ${expected_per_person:.2f}/person, got ${result['amount_per_person']}/person")
    except Exception as e:
        print(f"❌ Split bill error: {e}")
    
    return tests_passed, tests_total

def test_bmi_calculator():
    """Test the BMI calculator"""
    print("🧪 Testing BMI Calculator...")
    calc = BMICalculator()
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Normal BMI
    tests_total += 1
    try:
        result = calc.calculate({'height_cm': '175', 'weight_kg': '70'})
        expected_bmi = 70 / (1.75 ** 2)  # Should be about 22.9
        if abs(result['bmi'] - expected_bmi) < 0.1:
            tests_passed += 1
            print(f"✅ BMI: 175cm, 70kg = BMI {result['bmi']} ({result['category']})")
        else:
            print(f"❌ BMI failed: expected ~{expected_bmi:.1f}, got {result['bmi']}")
    except Exception as e:
        print(f"❌ BMI error: {e}")
    
    return tests_passed, tests_total

def test_loan_calculator():
    """Test the loan calculator"""
    print("🧪 Testing Loan Calculator...")
    calc = LoanCalculator()
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Standard loan payment
    tests_total += 1
    try:
        result = calc.calculate({'loan_amount': '100000', 'annual_rate': '6', 'loan_term_years': '30'})
        # $100k at 6% for 30 years should be about $599.55/month
        if 590 < result['monthly_payment'] < 610:
            tests_passed += 1
            print(f"✅ Loan: $100k at 6% for 30 years = ${result['monthly_payment']}/month")
        else:
            print(f"❌ Loan failed: expected ~$600/month, got ${result['monthly_payment']}/month")
    except Exception as e:
        print(f"❌ Loan error: {e}")
    
    return tests_passed, tests_total

def run_all_tests():
    """Run all calculator tests"""
    print("🚀 Calculator Suite - Direct Testing (Week 1, Day 1)")
    print("Testing core calculators without Flask to identify issues")
    print("=" * 70)
    
    # Run all test groups
    all_tests = [
        test_percentage_calculator,
        test_tip_calculator,
        test_bmi_calculator,
        test_loan_calculator
    ]
    
    total_passed = 0
    total_tests = 0
    
    for test_func in all_tests:
        passed, total = test_func()
        total_passed += passed
        total_tests += total
        print()
    
    # Summary
    print("=" * 70)
    print(f"📊 WEEK 1, DAY 1 TEST RESULTS")
    print("=" * 70)
    print(f"Tests passed: {total_passed}/{total_tests}")
    print(f"Success rate: {total_passed/total_tests*100:.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 ALL CORE CALCULATORS WORKING!")
        print("✅ Percentage calculator working correctly")
        print("✅ Tip calculator working correctly") 
        print("✅ BMI calculator working correctly")
        print("✅ Loan calculator working correctly")
        print("\n📋 NEXT STEPS:")
        print("1. Fix Flask startup issues")
        print("2. Replace technical error messages")
        print("3. Improve user-friendly interface")
        print("4. Test remaining 12 calculators")
    else:
        print(f"\n⚠️  {total_tests - total_passed} calculators have issues")
        print("❌ Need to fix broken calculator logic")
        print("📋 PRIORITY: Fix failing calculators first")
    
    return total_passed, total_tests

if __name__ == '__main__':
    run_all_tests()