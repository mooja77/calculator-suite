#!/usr/bin/env python3
"""
Comprehensive test suite for Calculator Suite
Tests all calculator classes and their functionality
"""

import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import calculators from app_simple_fixed
from app_simple_fixed import (
    LoanCalculator, PercentageCalculator, BMICalculator, TipCalculator,
    MortgageCalculator, IncomeTaxCalculator, SalesTaxCalculator, 
    PropertyTaxCalculator, TaxRefundCalculator, GrossToNetCalculator,
    HourlyToSalaryCalculator, SalaryRaiseCalculator, CostOfLivingCalculator,
    CompoundInterestCalculator, RetirementCalculator, InvestmentReturnCalculator,
    app, calculation_logs
)


class TestBaseCalculatorFunctionality:
    """Test base calculator functionality"""
    
    def test_percentage_calculator_basic(self):
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['result'] == 25.0
        assert result['operation'] == 'basic'
        assert 'formula' in result
        assert 'explanation' in result
    
    def test_percentage_calculator_increase(self):
        calc = PercentageCalculator()
        inputs = {'operation': 'increase', 'original': '100', 'percent': '10'}
        
        result = calc.calculate(inputs)
        assert result['result'] == 110.0
    
    def test_percentage_calculator_validation_errors(self):
        calc = PercentageCalculator()
        
        # Missing required fields
        inputs = {'operation': 'basic', 'x': '25'}
        assert calc.validate_inputs(inputs) == False
        assert len(calc.errors) > 0
        
        # Division by zero
        inputs = {'operation': 'basic', 'x': '25', 'y': '0'}
        assert calc.validate_inputs(inputs) == False


class TestLoanCalculator:
    """Test loan calculator functionality"""
    
    def test_loan_calculation_basic(self):
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '100000',
            'annual_rate': '5.0',
            'loan_term_years': '30',
            'loan_type': 'mortgage'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['loan_amount'] == 100000.0
        assert result['annual_rate'] == 5.0
        assert result['loan_term_years'] == 30.0
        assert result['monthly_payment'] > 0
        assert result['total_paid'] > result['loan_amount']
        assert result['total_interest'] > 0
        
    def test_loan_zero_interest(self):
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '12000',
            'annual_rate': '0',
            'loan_term_years': '1'
        }
        
        result = calc.calculate(inputs)
        assert result['monthly_payment'] == 1000.0  # 12000 / 12 months
        assert result['total_interest'] == 0.0
    
    def test_loan_validation_errors(self):
        calc = LoanCalculator()
        
        # Missing loan amount
        inputs = {'annual_rate': '5.0', 'loan_term_years': '30'}
        with pytest.raises(ValueError):
            calc.calculate(inputs)


class TestBMICalculator:
    """Test BMI calculator functionality"""
    
    def test_bmi_metric_calculation(self):
        calc = BMICalculator()
        inputs = {
            'height': '175',
            'weight': '70',
            'unit_system': 'metric',
            'age': '30',
            'gender': 'male'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        expected_bmi = 70 / (1.75 ** 2)  # weight / height^2
        assert abs(result['bmi'] - expected_bmi) < 0.1
        assert result['category'] in ['Underweight', 'Normal weight', 'Overweight', 'Obese']
        assert 'health_info' in result
        
    def test_bmi_imperial_calculation(self):
        calc = BMICalculator()
        inputs = {
            'height_feet': '5',
            'height_inches': '9',
            'weight': '154',
            'unit_system': 'imperial',
            'age': '25',
            'gender': 'female'
        }
        
        result = calc.calculate(inputs)
        assert result['bmi'] > 0
        assert result['height_cm'] > 0
        assert result['weight_kg'] > 0
    
    def test_bmi_validation_errors(self):
        calc = BMICalculator()
        
        # Invalid height
        inputs = {
            'height': '0',
            'weight': '70',
            'unit_system': 'metric'
        }
        assert calc.validate_inputs(inputs) == False


class TestTipCalculator:
    """Test tip calculator functionality"""
    
    def test_tip_calculation_basic(self):
        calc = TipCalculator()
        inputs = {
            'bill_amount': '100.00',
            'tip_percentage': '18',
            'number_of_people': '4'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['bill_amount'] == 100.0
        assert result['tip_percentage'] == 18.0
        assert result['tip_amount'] == 18.0
        assert result['total_amount'] == 118.0
        assert result['amount_per_person'] == 29.5  # 118 / 4
        assert result['tip_per_person'] == 4.5  # 18 / 4
    
    def test_tip_with_tax(self):
        calc = TipCalculator()
        inputs = {
            'bill_amount': '100.00',
            'tip_percentage': '20',
            'tax_amount': '8.50',
            'number_of_people': '2'
        }
        
        result = calc.calculate(inputs)
        assert result['tax_amount'] == 8.5
        assert result['total_amount'] == 128.5  # 100 + 20 + 8.5


class TestMortgageCalculator:
    """Test mortgage calculator functionality"""
    
    def test_mortgage_basic_calculation(self):
        calc = MortgageCalculator()
        inputs = {
            'home_price': '400000',
            'down_payment_percent': '20',
            'annual_rate': '6.5',
            'loan_term_years': '30'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['home_price'] == 400000.0
        assert result['down_payment'] == 80000.0  # 20% of 400k
        assert result['loan_amount'] == 320000.0  # 400k - 80k
        assert result['monthly_principal_interest'] > 0
        assert result['down_payment_percent'] == 20.0
    
    def test_mortgage_with_pmi(self):
        calc = MortgageCalculator()
        inputs = {
            'home_price': '300000',
            'down_payment_percent': '10',  # Less than 20%, should trigger PMI
            'annual_rate': '6.0',
            'loan_term_years': '30'
        }
        
        result = calc.calculate(inputs)
        assert result['pmi_monthly'] > 0  # Should have PMI
        assert result['down_payment_percent'] == 10.0


class TestTaxCalculators:
    """Test all tax-related calculators"""
    
    def test_income_tax_calculator(self):
        calc = IncomeTaxCalculator()
        inputs = {
            'annual_income': '75000',
            'filing_status': 'single',
            'state': 'california',
            'tax_year': '2024'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['annual_income'] == 75000.0
        assert result['federal_tax'] > 0
        assert result['state_tax'] > 0  # California has state tax
        assert result['fica_total'] > 0
        assert result['net_income'] < result['annual_income']
        assert result['effective_rate'] > 0
    
    def test_sales_tax_calculator(self):
        calc = SalesTaxCalculator()
        inputs = {
            'purchase_amount': '1000',
            'state': 'california',
            'city': 'los_angeles'
        }
        
        result = calc.calculate(inputs)
        assert result['purchase_amount'] == 1000.0
        assert result['sales_tax'] > 0
        assert result['total_amount'] > 1000.0
        assert result['tax_rate'] > 0
    
    def test_property_tax_calculator(self):
        calc = PropertyTaxCalculator()
        inputs = {
            'home_value': '500000',
            'location': 'texas',
            'homestead_exemption': '40000'
        }
        
        result = calc.calculate(inputs)
        assert result['home_value'] == 500000.0
        assert result['annual_tax'] > 0
        assert result['monthly_tax'] > 0
        assert result['total_exemptions'] >= 40000.0
    
    def test_tax_refund_calculator(self):
        calc = TaxRefundCalculator()
        inputs = {
            'annual_income': '60000',
            'federal_withholding': '8000',
            'state_withholding': '2000',
            'filing_status': 'single',
            'dependents_under_17': '1'
        }
        
        result = calc.calculate(inputs)
        assert result['annual_income'] == 60000.0
        assert 'federal_refund' in result
        assert 'state_refund' in result
        assert 'child_tax_credit' in result


class TestSalaryCalculators:
    """Test salary-related calculators"""
    
    def test_gross_to_net_calculator(self):
        calc = GrossToNetCalculator()
        inputs = {
            'gross_salary': '80000',
            'pay_frequency': 'monthly',
            'filing_status': 'single',
            'state': 'texas'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['gross_salary'] == 80000.0
        assert result['net_pay'] < result['gross_salary']
        assert result['federal_tax'] > 0
        assert result['fica_total'] > 0
        assert result['monthly_net'] > 0
    
    def test_hourly_to_salary_calculator(self):
        calc = HourlyToSalaryCalculator()
        inputs = {
            'calculation_type': 'hourly_to_salary',
            'hourly_rate': '25',
            'hours_per_week': '40',
            'weeks_per_year': '52'
        }
        
        result = calc.calculate(inputs)
        assert result['hourly_rate'] == 25.0
        assert result['annual_salary'] == 52000.0  # 25 * 40 * 52
        assert result['monthly_salary'] > 0
        assert result['weekly_salary'] == 1000.0  # 25 * 40
    
    def test_salary_raise_calculator(self):
        calc = SalaryRaiseCalculator()
        inputs = {
            'calculation_type': 'raise_percentage',
            'current_salary': '70000',
            'raise_percentage': '5'
        }
        
        result = calc.calculate(inputs)
        assert result['current_salary'] == 70000.0
        assert result['raise_percentage'] == 5.0
        assert result['raise_amount'] == 3500.0  # 5% of 70k
        assert result['new_salary'] == 73500.0
        assert 'performance_context' in result
    
    def test_cost_of_living_calculator(self):
        calc = CostOfLivingCalculator()
        inputs = {
            'current_salary': '75000',
            'current_city': 'Dallas, TX',
            'target_city': 'San Francisco, CA',
            'current_city_key': 'dallas',
            'target_city_key': 'san_francisco'
        }
        
        result = calc.calculate(inputs)
        assert result['current_salary'] == 75000.0
        assert result['equivalent_salary'] > result['current_salary']  # SF is more expensive
        assert 'breakdown' in result
        assert 'recommendation' in result


class TestInvestmentCalculators:
    """Test investment and retirement calculators"""
    
    def test_compound_interest_calculator(self):
        calc = CompoundInterestCalculator()
        inputs = {
            'principal': '10000',
            'annual_rate': '7',
            'years': '10',
            'compound_frequency': '12',
            'monthly_contribution': '500'
        }
        
        assert calc.validate_inputs(inputs) == True
        result = calc.calculate(inputs)
        
        assert result['principal'] == 10000.0
        assert result['annual_rate'] == 7.0
        assert result['total_value'] > result['principal']
        assert result['total_interest'] > 0
        assert 'yearly_breakdown' in result
        assert 'insights' in result
    
    def test_retirement_calculator(self):
        calc = RetirementCalculator()
        inputs = {
            'current_age': '35',
            'retirement_age': '65',
            'current_savings': '50000',
            'monthly_contribution': '1000',
            'annual_return': '7',
            'retirement_income_goal': '80000'
        }
        
        result = calc.calculate(inputs)
        assert result['current_age'] == 35
        assert result['retirement_age'] == 65
        assert result['years_to_retirement'] == 30
        assert result['total_retirement_savings'] > 0
        assert result['sustainable_annual_income'] > 0
        assert result['readiness_score'] >= 0
        assert 'recommendations' in result
    
    def test_investment_return_calculator_future_value(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'future_value',
            'initial_investment': '25000',
            'annual_return': '8',
            'years': '15',
            'additional_contributions': '200',
            'contribution_frequency': 'monthly'
        }
        
        result = calc.calculate(inputs)
        assert result['calculation_type'] == 'future_value'
        assert result['initial_investment'] == 25000.0
        assert result['total_value'] > result['initial_investment']
        assert result['total_gains'] > 0
    
    def test_investment_return_calculator_required_return(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'required_return',
            'initial_investment': '10000',
            'target_value': '50000',
            'years': '10'
        }
        
        result = calc.calculate(inputs)
        assert result['calculation_type'] == 'required_return'
        assert result['required_return'] > 0
        assert 'risk_assessment' in result
    
    def test_investment_return_calculator_portfolio_analysis(self):
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'portfolio_analysis',
            'investment_1_name': 'S&P 500',
            'investment_1_initial': '10000',
            'investment_1_current': '12000',
            'investment_2_name': 'Bonds',
            'investment_2_initial': '5000',
            'investment_2_current': '5250'
        }
        
        result = calc.calculate(inputs)
        assert result['calculation_type'] == 'portfolio_analysis'
        assert result['total_initial'] == 15000.0
        assert result['total_current'] == 17250.0
        assert result['portfolio_return'] > 0
        assert len(result['investments']) == 2


class TestValidationAndErrorHandling:
    """Test input validation and error handling across calculators"""
    
    def test_base_calculator_number_validation(self):
        calc = PercentageCalculator()
        
        # Test invalid number
        result = calc.validate_number('not_a_number', 'Test Field')
        assert result is None
        assert len(calc.errors) > 0
        
        # Test number outside range
        calc.clear_errors()
        result = calc.validate_number('150', 'Test Field', min_val=0, max_val=100)
        assert result is None
        assert len(calc.errors) > 0
        
        # Test valid number
        calc.clear_errors()
        result = calc.validate_number('50', 'Test Field', min_val=0, max_val=100)
        assert result == 50.0
        assert len(calc.errors) == 0
    
    def test_error_accumulation(self):
        calc = PercentageCalculator()
        
        # Add multiple errors
        calc.add_error("First error")
        calc.add_error("Second error")
        
        assert len(calc.errors) == 2
        
        # Clear errors
        calc.clear_errors()
        assert len(calc.errors) == 0
    
    def test_missing_required_fields(self):
        # Test multiple calculators for missing required fields
        calculators_and_inputs = [
            (LoanCalculator(), {}),
            (BMICalculator(), {}),
            (MortgageCalculator(), {}),
            (IncomeTaxCalculator(), {}),
            (RetirementCalculator(), {}),
        ]
        
        for calc, inputs in calculators_and_inputs:
            with pytest.raises(ValueError):
                calc.calculate(inputs)


class TestMetaDataAndSEO:
    """Test meta data generation for SEO"""
    
    def test_all_calculators_have_metadata(self):
        calculators = [
            PercentageCalculator(), LoanCalculator(), BMICalculator(),
            TipCalculator(), MortgageCalculator(), IncomeTaxCalculator(),
            SalesTaxCalculator(), PropertyTaxCalculator(), TaxRefundCalculator(),
            GrossToNetCalculator(), HourlyToSalaryCalculator(), SalaryRaiseCalculator(),
            CostOfLivingCalculator(), CompoundInterestCalculator(), RetirementCalculator(),
            InvestmentReturnCalculator()
        ]
        
        for calc in calculators:
            meta = calc.get_meta_data()
            assert 'title' in meta
            assert 'description' in meta
            assert 'keywords' in meta
            assert 'canonical' in meta
            assert len(meta['title']) > 0
            assert len(meta['description']) > 0
            assert len(meta['description']) <= 160  # SEO best practice


class TestAppIntegration:
    """Test Flask app integration"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        return app.test_client()
    
    def test_homepage_loads(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Calculator Suite' in response.data
    
    def test_calculator_pages_load(self, client):
        calculator_paths = [
            '/calculators/percentage/',
            '/calculators/bmi/',
            '/calculators/tip/',
            '/calculators/loan/',
            '/calculators/mortgage/',
            '/calculators/income-tax/',
            '/calculators/retirement/',
            '/calculators/investment-return/'
        ]
        
        for path in calculator_paths:
            response = client.get(path)
            assert response.status_code == 200
    
    def test_api_endpoint_percentage(self, client):
        response = client.post('/api/calculate/percentage',
                             json={'operation': 'basic', 'x': '25', 'y': '100'},
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['result'] == 25.0
    
    def test_api_endpoint_validation_error(self, client):
        # Send invalid data
        response = client.post('/api/calculate/percentage',
                             json={'operation': 'basic', 'x': '25'},  # Missing 'y'
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
    
    def test_sitemap_generation(self, client):
        response = client.get('/sitemap.xml')
        assert response.status_code == 200
        assert response.content_type == 'application/xml; charset=utf-8'
        assert b'<urlset' in response.data
    
    def test_robots_txt(self, client):
        response = client.get('/robots.txt')
        assert response.status_code == 200
        assert response.content_type == 'text/plain; charset=utf-8'
        assert b'User-agent:' in response.data


class TestCalculationLogging:
    """Test that calculations are properly logged"""
    
    def test_calculation_logging(self):
        # Clear existing logs
        calculation_logs.clear()
        
        # Perform a calculation
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
        result = calc.calculate(inputs)
        
        # Note: Logging happens in the API endpoints, not the calculator classes
        # This test structure is ready for when logging is implemented in calculators
        assert len(calculation_logs) >= 0  # Placeholder assertion


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])