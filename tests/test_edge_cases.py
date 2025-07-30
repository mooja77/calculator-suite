#!/usr/bin/env python3
"""
Edge case tests for Calculator Suite
Tests boundary conditions, extreme values, and error scenarios
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_simple_fixed import (
    PercentageCalculator, LoanCalculator, BMICalculator, MortgageCalculator,
    IncomeTaxCalculator, RetirementCalculator, CompoundInterestCalculator,
    InvestmentReturnCalculator, SalaryRaiseCalculator
)


class TestPercentageCalculatorEdgeCases:
    """Test edge cases for percentage calculator"""
    
    def test_percentage_change_from_zero(self):
        calc = PercentageCalculator()
        inputs = {'operation': 'change', 'original': '0', 'new_value': '10'}
        
        # Should not validate because original cannot be zero for percentage change
        assert calc.validate_inputs(inputs) == False
        assert any('zero' in error.lower() for error in calc.errors)
    
    def test_percentage_very_large_numbers(self):
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '999999999', 'y': '1000000000'}
        
        result = calc.calculate(inputs)
        assert abs(result['result'] - 99.9999999) < 0.0001
    
    def test_percentage_negative_numbers(self):
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '-50', 'y': '100'}
        
        result = calc.calculate(inputs)
        assert result['result'] == -50.0
    
    def test_percentage_decimal_precision(self):
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '1', 'y': '3'}
        
        result = calc.calculate(inputs)
        # Should be rounded to 2 decimal places
        assert result['result'] == 33.33


class TestLoanCalculatorEdgeCases:
    """Test edge cases for loan calculator"""
    
    def test_loan_zero_interest_rate(self):
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '12000',
            'annual_rate': '0',
            'loan_term_years': '1'
        }
        
        result = calc.calculate(inputs)
        assert result['monthly_payment'] == 1000.0
        assert result['total_interest'] == 0.0
    
    def test_loan_very_high_interest_rate(self):
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '10000',
            'annual_rate': '50',  # 50% APR
            'loan_term_years': '1'
        }
        
        result = calc.calculate(inputs)
        assert result['total_interest'] > result['loan_amount']  # More interest than principal
    
    def test_loan_very_short_term(self):
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '1000',
            'annual_rate': '5',
            'loan_term_years': '0.1'  # 1.2 months
        }
        
        result = calc.calculate(inputs)
        assert result['monthly_payment'] > 800  # Should be high for short term
    
    def test_loan_maximum_values(self):
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '10000000',  # 10 million
            'annual_rate': '3',
            'loan_term_years': '30'
        }
        
        result = calc.calculate(inputs)
        assert result['loan_amount'] == 10000000.0
        assert result['monthly_payment'] > 0


class TestBMICalculatorEdgeCases:
    """Test edge cases for BMI calculator"""
    
    def test_bmi_extreme_underweight(self):
        calc = BMICalculator()
        inputs = {
            'height': '180',
            'weight': '30',  # Extremely low weight
            'unit_system': 'metric',
            'age': '25',
            'gender': 'male'
        }
        
        result = calc.calculate(inputs)
        assert result['bmi'] < 15
        assert result['category'] == 'Underweight'
    
    def test_bmi_extreme_obesity(self):
        calc = BMICalculator()
        inputs = {
            'height': '160',
            'weight': '200',  # Very high weight for height
            'unit_system': 'metric',
            'age': '30',
            'gender': 'female'
        }
        
        result = calc.calculate(inputs)
        assert result['bmi'] > 40
        assert 'Obese' in result['category']
    
    def test_bmi_very_tall_person(self):
        calc = BMICalculator()
        inputs = {
            'height_feet': '7',
            'height_inches': '6',  # 7'6" - very tall
            'weight': '300',
            'unit_system': 'imperial',
            'age': '25',
            'gender': 'male'
        }
        
        result = calc.calculate(inputs)
        assert result['height_cm'] > 220
        assert result['bmi'] > 0
    
    def test_bmi_minimum_valid_inputs(self):
        calc = BMICalculator()
        inputs = {
            'height': '100',  # 1 meter - minimum realistic height
            'weight': '20',   # 20 kg - minimum realistic weight
            'unit_system': 'metric'
        }
        
        result = calc.calculate(inputs)
        assert result['bmi'] == 20.0  # 20 / (1.0)^2


class TestMortgageCalculatorEdgeCases:
    """Test edge cases for mortgage calculator"""
    
    def test_mortgage_100_percent_financing(self):
        calc = MortgageCalculator()
        inputs = {
            'home_price': '300000',
            'down_payment_percent': '0',  # No down payment
            'annual_rate': '7',
            'loan_term_years': '30'
        }
        
        result = calc.calculate(inputs)
        assert result['down_payment'] == 0
        assert result['loan_amount'] == 300000
        assert result['pmi_monthly'] > 0  # Should have PMI
    
    def test_mortgage_large_down_payment(self):
        calc = MortgageCalculator()
        inputs = {
            'home_price': '500000',
            'down_payment_percent': '50',  # 50% down payment
            'annual_rate': '6',
            'loan_term_years': '15'
        }
        
        result = calc.calculate(inputs)
        assert result['down_payment'] == 250000
        assert result['loan_amount'] == 250000
        assert result['pmi_monthly'] == 0  # No PMI needed
    
    def test_mortgage_very_high_price(self):
        calc = MortgageCalculator()
        inputs = {
            'home_price': '5000000',  # 5 million dollar home
            'down_payment_percent': '20',
            'annual_rate': '5',
            'loan_term_years': '30'
        }
        
        result = calc.calculate(inputs)
        assert result['home_price'] == 5000000
        assert result['monthly_principal_interest'] > 15000


class TestRetirementCalculatorEdgeCases:
    """Test edge cases for retirement calculator"""
    
    def test_retirement_late_starter(self):
        calc = RetirementCalculator()
        inputs = {
            'current_age': '55',
            'retirement_age': '65',
            'current_savings': '10000',  # Low savings for age
            'monthly_contribution': '2000',  # High contributions to catch up
            'annual_return': '6'
        }
        
        result = calc.calculate(inputs)
        assert result['years_to_retirement'] == 10
        assert result['readiness_score'] < 100  # Likely not fully ready
        assert any('catch' in rec['message'].lower() for rec in result['recommendations'])
    
    def test_retirement_very_early_starter(self):
        calc = RetirementCalculator()
        inputs = {
            'current_age': '22',
            'retirement_age': '65',
            'current_savings': '5000',
            'monthly_contribution': '500',
            'annual_return': '8'
        }
        
        result = calc.calculate(inputs)
        assert result['years_to_retirement'] == 43
        assert result['total_retirement_savings'] > 1000000  # Power of compounding
    
    def test_retirement_zero_return(self):
        calc = RetirementCalculator()
        inputs = {
            'current_age': '30',
            'retirement_age': '65',
            'current_savings': '20000',
            'monthly_contribution': '1000',
            'annual_return': '0'  # No growth
        }
        
        result = calc.calculate(inputs)
        # Should equal current savings plus contributions
        expected = 20000 + (1000 * 12 * 35)  # 35 years of contributions
        assert abs(result['total_retirement_savings'] - expected) < 100
    
    def test_retirement_age_validation(self):
        calc = RetirementCalculator()
        inputs = {
            'current_age': '65',
            'retirement_age': '60',  # Retirement age before current age
            'annual_return': '7'
        }
        
        with pytest.raises(ValueError, match="Retirement age must be greater than current age"):
            calc.calculate(inputs)


class TestCompoundInterestEdgeCases:
    """Test edge cases for compound interest calculator"""
    
    def test_compound_interest_negative_return(self):
        calc = CompoundInterestCalculator()
        inputs = {
            'principal': '10000',
            'annual_rate': '-5',  # Market crash scenario
            'years': '5',
            'compound_frequency': '12'
        }
        
        result = calc.calculate(inputs)
        assert result['total_value'] < result['principal']
        assert result['total_interest'] < 0
    
    def test_compound_interest_very_high_frequency(self):
        calc = CompoundInterestCalculator()
        inputs = {
            'principal': '10000',
            'annual_rate': '5',
            'years': '10',
            'compound_frequency': '365'  # Daily compounding
        }
        
        result = calc.calculate(inputs)
        assert result['compound_frequency_text'] == 'Daily'
        assert result['total_value'] > 16000  # Should be higher than annual compounding
    
    def test_compound_interest_zero_principal(self):
        calc = CompoundInterestCalculator()
        inputs = {
            'principal': '0',
            'annual_rate': '7',
            'years': '10',
            'monthly_contribution': '1000'
        }
        
        # Should not validate because principal must be at least 1
        assert calc.validate_inputs(inputs) == False
    
    def test_compound_interest_very_long_term(self):
        calc = CompoundInterestCalculator()
        inputs = {
            'principal': '1000',
            'annual_rate': '8',
            'years': '50',  # 50 years
            'compound_frequency': '12'
        }
        
        result = calc.calculate(inputs)
        assert result['total_value'] > 50000  # Significant growth over 50 years


class TestInvestmentReturnEdgeCases:
    """Test edge cases for investment return calculator"""
    
    def test_investment_required_return_impossible_target(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'required_return',
            'initial_investment': '1000',
            'target_value': '1000000',  # 1000x return
            'years': '5'  # In only 5 years
        }
        
        result = calc.calculate(inputs)
        assert result['required_return'] > 100  # Extremely high required return
        assert result['risk_assessment']['level'] == 'Very High Risk'
        assert result['risk_assessment']['feasibility'] == 'Unlikely'
    
    def test_investment_time_needed_with_zero_return(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'time_needed',
            'initial_investment': '10000',
            'target_value': '20000',
            'annual_return': '0'  # No return
        }
        
        result = calc.calculate(inputs)
        assert result['feasible'] == False  # Cannot reach target with 0% return
    
    def test_investment_portfolio_analysis_losses(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'portfolio_analysis',
            'investment_1_name': 'Stock A',
            'investment_1_initial': '10000',
            'investment_1_current': '8000',  # 20% loss
            'investment_2_name': 'Stock B',
            'investment_2_initial': '5000',
            'investment_2_current': '3000'   # 40% loss
        }
        
        result = calc.calculate(inputs)
        assert result['total_gain_loss'] < 0
        assert result['portfolio_return'] < 0
        assert all(inv['return_pct'] < 0 for inv in result['investments'])
    
    def test_investment_future_value_with_huge_contributions(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'future_value',
            'initial_investment': '1000',
            'annual_return': '5',
            'years': '10',
            'additional_contributions': '10000',  # Huge monthly contributions
            'contribution_frequency': 'monthly'
        }
        
        result = calc.calculate(inputs)
        # Contributions should dominate the final value
        assert result['fv_contributions'] > result['fv_initial']
        assert result['total_value'] > 1200000  # 10k * 12 * 10 = 1.2M in contributions alone


class TestSalaryRaiseEdgeCases:
    """Test edge cases for salary raise calculator"""
    
    def test_salary_raise_massive_percentage(self):
        calc = SalaryRaiseCalculator()
        inputs = {
            'calculation_type': 'raise_percentage',
            'current_salary': '50000',
            'raise_percentage': '100'  # 100% raise (doubling salary)
        }
        
        result = calc.calculate(inputs)
        assert result['new_salary'] == 100000
        assert result['raise_amount'] == 50000
        assert result['performance_context']['category'] == 'Major Career Change'
    
    def test_salary_raise_tiny_amount(self):
        calc = SalaryRaiseCalculator()
        inputs = {
            'calculation_type': 'raise_amount',
            'current_salary': '100000',
            'raise_amount': '100'  # $100 raise on 100k salary
        }
        
        result = calc.calculate(inputs)
        assert result['raise_percentage'] == 0.1  # 0.1%
        assert result['performance_context']['category'] == 'No Raise'
    
    def test_salary_raise_target_lower_than_current(self):
        calc = SalaryRaiseCalculator()
        inputs = {
            'calculation_type': 'target_salary',
            'current_salary': '80000',
            'target_salary': '70000'  # Pay cut
        }
        
        result = calc.calculate(inputs)
        assert result['raise_amount'] == -10000  # Negative raise
        assert result['raise_percentage'] == -12.5  # -12.5%


class TestValidationBoundaries:
    """Test validation at boundary conditions"""
    
    def test_number_validation_boundaries(self):
        calc = PercentageCalculator()
        
        # Test minimum boundary
        result = calc.validate_number('0', 'Test', min_val=0)
        assert result == 0.0
        
        # Test maximum boundary
        calc.clear_errors()
        result = calc.validate_number('100', 'Test', max_val=100)
        assert result == 100.0
        
        # Test just outside boundaries
        calc.clear_errors()
        result = calc.validate_number('-1', 'Test', min_val=0)
        assert result is None
        assert len(calc.errors) > 0
        
        calc.clear_errors()
        result = calc.validate_number('101', 'Test', max_val=100)
        assert result is None
        assert len(calc.errors) > 0
    
    def test_empty_string_validation(self):
        calculators = [
            PercentageCalculator(),
            LoanCalculator(),
            BMICalculator(),
            MortgageCalculator()
        ]
        
        for calc in calculators:
            calc.clear_errors()
            result = calc.validate_number('', 'Test Field')
            assert result is None
            assert len(calc.errors) > 0
    
    def test_extreme_decimal_precision(self):
        calc = PercentageCalculator()
        inputs = {
            'operation': 'basic',
            'x': '1.23456789012345',
            'y': '3.45678901234567'
        }
        
        result = calc.calculate(inputs)
        # Should handle high precision and round appropriately
        assert isinstance(result['result'], float)
        assert result['result'] != float('inf')
        assert result['result'] != float('-inf')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])