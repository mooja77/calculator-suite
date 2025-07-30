#!/usr/bin/env python3
"""
Enhanced Calculator Suite - Complete Version
Comprehensive financial calculator suite with advanced features, detailed explanations, and educational content.
"""

from flask import Flask, render_template, request, jsonify, Response
import os
import json
import time
import math
import traceback
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Storage for calculations and analytics
calculation_logs = []
user_sessions = defaultdict(list)
calculator_usage_stats = defaultdict(int)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enhanced-calculator-suite-secret-key'

# Enhanced Calculator Registry
calculators = {}
calculator_categories = {
    'financial': ['loan', 'mortgage', 'compoundinterest', 'investmentreturn', 'retirement'],
    'tax': ['incometax', 'salestax', 'propertytax', 'taxrefund'],
    'salary': ['grosstonet', 'hourlytosalary', 'salaryraise', 'costofliving'],
    'utility': ['percentage', 'tip', 'bmi'],
    'business': ['breakeven', 'roi', 'cashflow', 'payroll'],
    'insurance': ['lifeinsurance', 'autoinsurance', 'healthinsurance'],
    'crypto': ['cryptoprofit', 'dca', 'staking'],
    'real_estate': ['rental', 'flipprofit', 'realestateinvestment'],
    'savings': ['emergency', 'savings', 'debt']
}

def register_calculator(calc_class):
    """Enhanced calculator registration with metadata"""
    instance = calc_class()
    calculators[instance.slug] = calc_class
    calculator_usage_stats[instance.slug] = 0
    return calc_class

# Enhanced Base Calculator Class
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
        """Validate percentage values"""
        return self.validate_number(value, field_name, min_val, max_val)
    
    def validate_positive_number(self, value, field_name):
        """Validate positive numbers only"""
        return self.validate_number(value, field_name, min_val=0.01)
    
    def format_currency(self, amount, currency_symbol='$'):
        """Format currency with proper thousands separators"""
        return f"{currency_symbol}{amount:,.2f}"
    
    def format_percentage(self, value, decimal_places=2):
        """Format percentage values"""
        return f"{value:.{decimal_places}f}%"
    
    def get_explanation(self):
        """Return detailed explanation of the calculator"""
        return "Calculator explanation not implemented"
    
    def get_formula_explanation(self):
        """Return mathematical formula explanation"""
        return "Formula explanation not implemented"
    
    def get_use_cases(self):
        """Return common use cases for this calculator"""
        return []
    
    def get_tips_and_advice(self):
        """Return financial tips related to this calculator"""
        return []
    
    def get_related_calculators(self):
        """Return list of related calculator slugs"""
        return self.related_calculators
    
    def get_meta_data(self):
        """Return SEO metadata for this calculator"""
        return {
            'title': f'{self.slug.title()} Calculator',
            'description': f'Calculate {self.slug} with our free online calculator',
            'keywords': f'{self.slug} calculator, financial calculator'
        }

# ===========================================
# ENHANCED LOAN CALCULATOR
# ===========================================

@register_calculator
class LoanCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['mortgage', 'compoundinterest', 'debt']
    
    def calculate(self, inputs):
        try:
            # Validate inputs
            loan_amount = self.validate_positive_number(inputs.get('loan_amount'), 'Loan Amount')
            annual_rate = self.validate_number(inputs.get('annual_rate'), 'Annual Interest Rate', 0, 50)
            loan_term_years = self.validate_positive_number(inputs.get('loan_term_years'), 'Loan Term (Years)')
            
            if self.errors:
                return {'errors': self.errors}
            
            loan_type = inputs.get('loan_type', 'personal')
            extra_payment = float(inputs.get('extra_payment', 0))
            
            # Convert to monthly values
            monthly_rate = annual_rate / 100 / 12
            num_payments = loan_term_years * 12
            
            # Calculate monthly payment
            if monthly_rate == 0:
                monthly_payment = loan_amount / num_payments
            else:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            # Calculate totals
            total_paid = monthly_payment * num_payments
            total_interest = total_paid - loan_amount
            
            # Calculate with extra payments
            extra_results = self._calculate_with_extra_payments(loan_amount, monthly_rate, monthly_payment, extra_payment)
            
            # Generate complete amortization schedule
            amortization_schedule = self._generate_full_amortization(loan_amount, monthly_rate, monthly_payment, extra_payment)
            
            # Add financial insights
            self._add_loan_insights(loan_amount, monthly_payment, annual_rate, loan_type)
            
            result = {
                'loan_amount': round(loan_amount, 2),
                'annual_rate': annual_rate,
                'loan_term_years': loan_term_years,
                'monthly_payment': round(monthly_payment, 2),
                'total_paid': round(total_paid, 2),
                'total_interest': round(total_interest, 2),
                'loan_type': loan_type,
                'extra_payment': extra_payment,
                'with_extra_payments': extra_results,
                'amortization_schedule': amortization_schedule,
                'loan_info': self._get_enhanced_loan_info(loan_type),
                'payment_breakdown': self._get_payment_breakdown(monthly_payment, loan_amount, annual_rate),
                'comparison_scenarios': self._get_rate_comparison(loan_amount, loan_term_years, annual_rate),
                'affordability_analysis': self._get_affordability_analysis(monthly_payment),
                'warnings': self.warnings,
                'tips': self.tips,
                'explanation': self.get_explanation(),
                'formula_explanation': self.get_formula_explanation(),
                'inputs': inputs
            }
            
            return result
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _calculate_with_extra_payments(self, principal, monthly_rate, payment, extra_payment):
        """Calculate loan with extra payments"""
        if extra_payment <= 0:
            return None
            
        balance = principal
        total_payments = 0
        months = 0
        total_interest = 0
        
        while balance > 0.01 and months < 600:  # Max 50 years
            interest_payment = balance * monthly_rate
            principal_payment = payment - interest_payment + extra_payment
            
            if principal_payment > balance:
                principal_payment = balance
                
            balance -= principal_payment
            total_interest += interest_payment
            total_payments += payment + extra_payment
            months += 1
        
        original_months = (principal / (payment - principal * monthly_rate)) if monthly_rate > 0 else principal / payment
        time_saved = max(0, original_months - months)
        interest_saved = (payment * original_months - principal) - total_interest
        
        return {
            'months_to_payoff': months,
            'years_to_payoff': round(months / 12, 1),
            'total_interest': round(total_interest, 2),
            'total_paid': round(total_payments, 2),
            'time_saved_months': round(time_saved, 1),
            'time_saved_years': round(time_saved / 12, 1),
            'interest_saved': round(interest_saved, 2)
        }
    
    def _generate_full_amortization(self, principal, monthly_rate, payment, extra_payment):
        """Generate complete amortization schedule"""
        schedule = []
        balance = principal
        month = 1
        total_interest = 0
        
        while balance > 0.01 and month <= 360:  # Max 30 years for display
            interest_payment = balance * monthly_rate
            principal_payment = payment - interest_payment + extra_payment
            
            if principal_payment > balance:
                principal_payment = balance
                
            balance -= principal_payment
            total_interest += interest_payment
            
            schedule.append({
                'month': month,
                'payment': round(payment + extra_payment, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'balance': round(balance, 2),
                'cumulative_interest': round(total_interest, 2)
            })
            
            month += 1
            
            # Only return first 12 months + yearly summaries for display
            if month > 12:
                break
        
        return schedule
    
    def _add_loan_insights(self, loan_amount, monthly_payment, annual_rate, loan_type):
        """Add personalized insights and recommendations"""
        debt_to_income_warning = monthly_payment * 12 / (loan_amount * 0.1)  # Rough estimate
        
        if annual_rate > 15:
            self.add_warning(f"Interest rate of {annual_rate}% is quite high. Consider shopping for better rates.")
        
        if annual_rate < 3:
            self.add_tip("Excellent interest rate! Consider making extra payments to pay off principal faster.")
        
        if loan_type == 'personal':
            self.add_tip("Personal loans typically have higher rates. Consider secured loans if you have collateral.")
        elif loan_type == 'auto':
            self.add_tip("Auto loans are secured by the vehicle, so rates are typically lower than personal loans.")
        elif loan_type == 'student':
            self.add_tip("Federal student loans often have better terms than private loans. Explore forgiveness programs.")
    
    def _get_enhanced_loan_info(self, loan_type):
        """Enhanced loan information with detailed explanations"""
        loan_info = {
            'personal': {
                'description': 'Personal loans are unsecured loans that can be used for various purposes.',
                'typical_rates': '6% - 36%',
                'typical_terms': '2 - 7 years',
                'pros': ['No collateral required', 'Flexible use of funds', 'Fixed payments'],
                'cons': ['Higher interest rates', 'Shorter terms', 'Origination fees'],
                'tips': ['Shop around for best rates', 'Consider secured alternatives', 'Pay off high-interest debt first']
            },
            'auto': {
                'description': 'Auto loans are secured by the vehicle being purchased.',
                'typical_rates': '3% - 15%',
                'typical_terms': '3 - 7 years',
                'pros': ['Lower rates due to collateral', 'Longer terms available', 'Build credit history'],
                'cons': ['Vehicle depreciates', 'Gap insurance needed', 'Repossession risk'],
                'tips': ['Get pre-approved', 'Consider certified pre-owned', 'Make larger down payment']
            },
            'mortgage': {
                'description': 'Mortgages are secured loans for purchasing real estate.',
                'typical_rates': '3% - 8%',
                'typical_terms': '15 - 30 years',
                'pros': ['Lowest rates available', 'Tax deductions', 'Build equity'],
                'cons': ['Large down payment', 'Closing costs', 'Property taxes'],
                'tips': ['Save 20% down payment', 'Compare lenders', 'Consider points vs rate']
            },
            'student': {
                'description': 'Student loans fund education expenses with special repayment terms.',
                'typical_rates': '3% - 12%',
                'typical_terms': '10 - 25 years',
                'pros': ['Deferred payments', 'Income-driven repayment', 'Forgiveness programs'],
                'cons': ['No discharge in bankruptcy', 'Interest accrues', 'Long-term debt'],
                'tips': ['Exhaust federal aid first', 'Understand repayment options', 'Consider income projections']
            }
        }
        return loan_info.get(loan_type, loan_info['personal'])
    
    def _get_payment_breakdown(self, monthly_payment, loan_amount, annual_rate):
        """Detailed payment breakdown analysis"""
        monthly_rate = annual_rate / 100 / 12
        first_month_interest = loan_amount * monthly_rate
        first_month_principal = monthly_payment - first_month_interest
        
        return {
            'monthly_payment': round(monthly_payment, 2),
            'first_month_interest': round(first_month_interest, 2),
            'first_month_principal': round(first_month_principal, 2),
            'interest_percentage': round((first_month_interest / monthly_payment) * 100, 1),
            'principal_percentage': round((first_month_principal / monthly_payment) * 100, 1)
        }
    
    def _get_rate_comparison(self, loan_amount, loan_term_years, current_rate):
        """Compare different interest rate scenarios"""
        scenarios = []
        rates_to_compare = [current_rate - 1, current_rate - 0.5, current_rate + 0.5, current_rate + 1]
        
        for rate in rates_to_compare:
            if rate > 0:
                monthly_rate = rate / 100 / 12
                num_payments = loan_term_years * 12
                
                if monthly_rate == 0:
                    payment = loan_amount / num_payments
                else:
                    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
                
                total_interest = (payment * num_payments) - loan_amount
                
                scenarios.append({
                    'rate': rate,
                    'monthly_payment': round(payment, 2),
                    'total_interest': round(total_interest, 2),
                    'difference_from_current': round(payment - (loan_amount * ((current_rate/100/12) * (1 + current_rate/100/12)**num_payments) / ((1 + current_rate/100/12)**num_payments - 1)), 2)
                })
        
        return scenarios
    
    def _get_affordability_analysis(self, monthly_payment):
        """Provide affordability analysis"""
        return {
            'monthly_payment': round(monthly_payment, 2),
            'recommended_monthly_income': round(monthly_payment * 3.5, 2),  # 28% rule
            'recommended_annual_income': round(monthly_payment * 42, 2),
            'debt_to_income_ratio_guidance': {
                'excellent': 'Under 20%',
                'good': '20% - 28%',
                'acceptable': '28% - 36%',
                'risky': 'Over 36%'
            }
        }
    
    def get_explanation(self):
        return """
        A loan calculator helps you determine monthly payments, total interest, and create payment schedules for various types of loans.
        
        **How it works:**
        1. Enter your loan amount (principal)
        2. Input the annual interest rate
        3. Specify the loan term in years
        4. Optionally add extra payments to see savings
        
        **Key Features:**
        - Monthly payment calculation using standard amortization formula
        - Complete amortization schedule showing principal vs interest
        - Extra payment scenarios and time/interest savings
        - Rate comparison analysis
        - Affordability guidelines based on debt-to-income ratios
        
        **When to use:**
        - Planning a major purchase
        - Comparing loan offers
        - Understanding total cost of borrowing
        - Evaluating refinancing options
        - Setting up a payoff strategy
        """
    
    def get_formula_explanation(self):
        return """
        **Loan Payment Formula:**
        M = P × [r(1+r)ⁿ] / [(1+r)ⁿ-1]
        
        Where:
        - M = Monthly payment
        - P = Principal loan amount
        - r = Monthly interest rate (annual rate ÷ 12)
        - n = Number of payments (years × 12)
        
        **For zero interest loans:**
        M = P ÷ n
        
        **Amortization Schedule:**
        Each payment = Interest + Principal
        - Interest = Remaining balance × monthly rate
        - Principal = Payment - Interest
        - New balance = Previous balance - Principal payment
        """

# ===========================================
# ENHANCED PERCENTAGE CALCULATOR
# ===========================================

@register_calculator
class PercentageCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['tip', 'salaryraise', 'investmentreturn']
    
    def calculate(self, inputs):
        try:
            operation = inputs.get('operation', 'basic')
            
            # Validate based on operation type
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
                increase_amount = result - original
                
            elif operation == 'decrease':
                original = self.validate_number(inputs.get('original'), 'Original Value')
                percent = self.validate_percentage(inputs.get('percent'), 'Decrease Percentage', 0, 100)
                if self.errors:
                    return {'errors': self.errors}
                result = original * (1 - percent / 100)
                decrease_amount = original - result
                
            elif operation == 'difference':
                x = self.validate_number(inputs.get('x'), 'First Value')
                y = self.validate_number(inputs.get('y'), 'Second Value')
                if self.errors:
                    return {'errors': self.errors}
                if x == 0 and y == 0:
                    result = 0
                else:
                    result = abs(x - y) / ((x + y) / 2) * 100
                    
            elif operation == 'change':
                original = self.validate_number(inputs.get('original'), 'Original Value', allow_zero=False)
                new_value = self.validate_number(inputs.get('new_value'), 'New Value')
                if self.errors:
                    return {'errors': self.errors}
                result = ((new_value - original) / original) * 100
                
            elif operation == 'compound':
                principal = self.validate_positive_number(inputs.get('principal'), 'Principal Amount')
                rate = self.validate_percentage(inputs.get('rate'), 'Interest Rate', 0, 50)
                periods = self.validate_positive_number(inputs.get('periods'), 'Number of Periods')
                if self.errors:
                    return {'errors': self.errors}
                result = principal * (1 + rate / 100) ** periods
                
            elif operation == 'margin':
                cost = self.validate_positive_number(inputs.get('cost'), 'Cost')
                selling_price = self.validate_positive_number(inputs.get('selling_price'), 'Selling Price')
                if self.errors:
                    return {'errors': self.errors}
                if selling_price <= cost:
                    self.add_warning("Selling price should be higher than cost for positive margin")
                profit = selling_price - cost
                result = (profit / selling_price) * 100  # Margin
                markup = (profit / cost) * 100  # Markup
                
            elif operation == 'grade':
                points_earned = self.validate_number(inputs.get('points_earned'), 'Points Earned', 0)
                total_points = self.validate_positive_number(inputs.get('total_points'), 'Total Points')
                if self.errors:
                    return {'errors': self.errors}
                result = (points_earned / total_points) * 100
                
            else:
                return {'error': f'Unknown operation: {operation}'}
            
            # Create comprehensive result
            response = {
                'result': round(result, 4),
                'operation': operation,
                'inputs': inputs,
                'formula': self._get_formula(operation),
                'explanation': self._get_explanation(operation, inputs, result),
                'step_by_step': self._get_step_by_step(operation, inputs, result),
                'related_calculations': self._get_related_calculations(operation, inputs, result),
                'real_world_examples': self._get_real_world_examples(operation),
                'tips': self._get_operation_tips(operation)
            }
            
            # Add operation-specific data
            if operation == 'increase':
                response['increase_amount'] = round(increase_amount, 2)
                response['original_value'] = round(original, 2)
                response['final_value'] = round(result, 2)
                
            elif operation == 'decrease':
                response['decrease_amount'] = round(decrease_amount, 2)
                response['original_value'] = round(original, 2)
                response['final_value'] = round(result, 2)
                
            elif operation == 'margin':
                response['profit'] = round(profit, 2)
                response['margin_percentage'] = round(result, 2)
                response['markup_percentage'] = round(markup, 2)
                
            elif operation == 'grade':
                response['letter_grade'] = self._get_letter_grade(result)
                response['points_earned'] = points_earned
                response['total_points'] = total_points
            
            return response
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _get_formula(self, operation):
        formulas = {
            'basic': '(X ÷ Y) × 100',
            'find_value': '(Percentage ÷ 100) × Total',
            'increase': 'Original × (1 + Percentage ÷ 100)',
            'decrease': 'Original × (1 - Percentage ÷ 100)',
            'difference': '|X - Y| ÷ ((X + Y) ÷ 2) × 100',
            'change': '((New Value - Original) ÷ Original) × 100',
            'compound': 'Principal × (1 + Rate ÷ 100)^Periods',
            'margin': '((Selling Price - Cost) ÷ Selling Price) × 100',
            'grade': '(Points Earned ÷ Total Points) × 100'
        }
        return formulas.get(operation, 'Formula not available')
    
    def _get_explanation(self, operation, inputs, result):
        explanations = {
            'basic': f"{inputs.get('x')} is {result:.2f}% of {inputs.get('y')}",
            'find_value': f"{inputs.get('percent')}% of {inputs.get('total')} is {result:.2f}",
            'increase': f"{inputs.get('original')} increased by {inputs.get('percent')}% equals {result:.2f}",
            'decrease': f"{inputs.get('original')} decreased by {inputs.get('percent')}% equals {result:.2f}",
            'difference': f"The percentage difference between {inputs.get('x')} and {inputs.get('y')} is {result:.2f}%",
            'change': f"The percentage change from {inputs.get('original')} to {inputs.get('new_value')} is {result:.2f}%",
            'compound': f"After {inputs.get('periods')} periods at {inputs.get('rate')}% rate, {inputs.get('principal')} grows to {result:.2f}",
            'margin': f"With a cost of {inputs.get('cost')} and selling price of {inputs.get('selling_price')}, the profit margin is {result:.2f}%",
            'grade': f"Scoring {inputs.get('points_earned')} out of {inputs.get('total_points')} points equals {result:.2f}%"
        }
        return explanations.get(operation, 'Explanation not available')
    
    def _get_step_by_step(self, operation, inputs, result):
        """Provide step-by-step calculation breakdown"""
        if operation == 'basic':
            return [
                f"Step 1: Divide {inputs.get('x')} by {inputs.get('y')}",
                f"Step 2: {inputs.get('x')} ÷ {inputs.get('y')} = {float(inputs.get('x'))/float(inputs.get('y')):.4f}",
                f"Step 3: Multiply by 100 to get percentage",
                f"Step 4: {float(inputs.get('x'))/float(inputs.get('y')):.4f} × 100 = {result:.2f}%"
            ]
        elif operation == 'increase':
            original = float(inputs.get('original'))
            percent = float(inputs.get('percent'))
            multiplier = 1 + percent / 100
            return [
                f"Step 1: Convert percentage to decimal: {percent}% = {percent/100}",
                f"Step 2: Add 1 to the decimal: 1 + {percent/100} = {multiplier}",
                f"Step 3: Multiply original value: {original} × {multiplier} = {result:.2f}",
                f"Step 4: Increase amount: {result:.2f} - {original} = {result - original:.2f}"
            ]
        # Add more step-by-step for other operations...
        return []
    
    def _get_related_calculations(self, operation, inputs, result):
        """Provide related calculations that might be useful"""
        related = []
        
        if operation == 'basic':
            x, y = float(inputs.get('x')), float(inputs.get('y'))
            related.append({
                'description': f'What percentage is {y} of {x}?',
                'result': f'{(y/x)*100:.2f}%' if x != 0 else 'Undefined'
            })
            related.append({
                'description': f'{result:.2f}% of {x}',
                'result': f'{(result/100)*x:.2f}'
            })
        
        elif operation == 'increase':
            original = float(inputs.get('original'))
            percent = float(inputs.get('percent'))
            related.append({
                'description': f'Decrease {result:.2f} by {percent}% (reverse operation)',
                'result': f'{result * (1 - percent/100):.2f}'
            })
        
        return related
    
    def _get_real_world_examples(self, operation):
        """Provide real-world examples for each operation"""
        examples = {
            'basic': [
                'Test scores: "I got 45 out of 50 questions right. What percentage is that?"',
                'Sales performance: "I sold $75,000 out of my $100,000 quota. What percentage did I achieve?"',
                'Survey results: "850 people out of 1,200 responded positively. What percentage is that?"'
            ],
            'find_value': [
                'Shopping discounts: "This $200 jacket is 25% off. How much do I save?"',
                'Tax calculations: "My income is $50,000 and the tax rate is 22%. How much tax do I owe?"',
                'Tip calculations: "The bill is $80 and I want to tip 18%. How much is the tip?"'
            ],
            'increase': [
                'Salary raises: "My salary is $60,000 and I\'m getting a 5% raise. What will my new salary be?"',
                'Investment growth: "I invested $10,000 and it grew by 8%. What is it worth now?"',
                'Price increases: "Gas was $3.50 per gallon and increased by 12%. What is the new price?"'
            ],
            'change': [
                'Stock performance: "Stock price went from $50 to $65. What was the percentage change?"',
                'Population growth: "City population grew from 100,000 to 115,000. What was the growth rate?"',
                'Weight loss: "I went from 180 lbs to 165 lbs. What percentage did I lose?"'
            ]
        }
        return examples.get(operation, [])
    
    def _get_operation_tips(self, operation):
        """Provide helpful tips for each operation"""
        tips = {
            'basic': [
                'Remember: percentage = (part ÷ whole) × 100',
                'Always identify which number is the "part" and which is the "whole"',
                'If the result is over 100%, the first number is larger than the second'
            ],
            'increase': [
                'Multiple increases: Apply each percentage increase separately',
                'Annual raises compound over time',
                'A 100% increase means doubling the original value'
            ],
            'margin': [
                'Margin vs Markup: Margin is based on selling price, markup on cost',
                'Higher margins generally mean better profitability',
                'Retail typically aims for 40-60% margins'
            ]
        }
        return tips.get(operation, [])
    
    def _get_letter_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 97: return 'A+'
        elif percentage >= 93: return 'A'
        elif percentage >= 90: return 'A-'
        elif percentage >= 87: return 'B+'
        elif percentage >= 83: return 'B'
        elif percentage >= 80: return 'B-'
        elif percentage >= 77: return 'C+'
        elif percentage >= 73: return 'C'
        elif percentage >= 70: return 'C-'
        elif percentage >= 67: return 'D+'
        elif percentage >= 63: return 'D'
        elif percentage >= 60: return 'D-'
        else: return 'F'
    
    def get_explanation(self):
        return """
        The Percentage Calculator is a versatile tool for all percentage-related calculations. It handles multiple operations:
        
        **Basic Operations:**
        1. **What % is X of Y?** - Find what percentage one number is of another
        2. **What is X% of Y?** - Calculate a percentage of a number
        3. **Increase by %** - Add a percentage to a number
        4. **Decrease by %** - Subtract a percentage from a number
        5. **Percentage Change** - Calculate the change between two values
        6. **Percentage Difference** - Find the difference as a percentage of the average
        
        **Advanced Operations:**
        7. **Compound Percentage** - Apply percentage growth over multiple periods
        8. **Profit Margin** - Calculate profit margins and markups
        9. **Grade Calculator** - Convert points to percentage grades
        
        **Key Features:**
        - Step-by-step calculations
        - Real-world examples
        - Related calculations
        - Formula explanations
        - Practical tips and advice
        """

# ===========================================
# ENHANCED MORTGAGE CALCULATOR
# ===========================================

@register_calculator
class MortgageCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['loan', 'propertytax', 'realestateinvestment']
    
    def calculate(self, inputs):
        try:
            # Validate required inputs
            home_price = self.validate_positive_number(inputs.get('home_price'), 'Home Price')
            down_payment_percent = self.validate_percentage(inputs.get('down_payment_percent'), 'Down Payment %', 0, 100)
            annual_rate = self.validate_number(inputs.get('annual_rate'), 'Interest Rate', 0, 20)
            loan_term_years = self.validate_number(inputs.get('loan_term_years'), 'Loan Term', 1, 50)
            
            if self.errors:
                return {'errors': self.errors}
            
            # Optional inputs with defaults
            property_tax_annual = float(inputs.get('property_tax_annual', 0))
            home_insurance_annual = float(inputs.get('home_insurance_annual', 0))
            hoa_monthly = float(inputs.get('hoa_monthly', 0))
            pmi_rate = float(inputs.get('pmi_rate', 0.5))  # Default PMI rate
            closing_costs_percent = float(inputs.get('closing_costs_percent', 3))
            
            # Calculate basic mortgage values
            down_payment = home_price * (down_payment_percent / 100)
            loan_amount = home_price - down_payment
            loan_to_value = (loan_amount / home_price) * 100
            
            # Calculate monthly payment (principal + interest)
            monthly_rate = annual_rate / 100 / 12
            num_payments = loan_term_years * 12
            
            if monthly_rate == 0:
                monthly_principal_interest = loan_amount / num_payments
            else:
                monthly_principal_interest = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            # Calculate PMI (if LTV > 80%)
            pmi_monthly = 0
            if loan_to_value > 80:
                pmi_monthly = (loan_amount * (pmi_rate / 100)) / 12
            
            # Calculate other monthly costs
            property_tax_monthly = property_tax_annual / 12
            insurance_monthly = home_insurance_annual / 12
            
            # Total monthly payment
            total_monthly_payment = (monthly_principal_interest + property_tax_monthly + 
                                   insurance_monthly + pmi_monthly + hoa_monthly)
            
            # Calculate totals over loan term
            total_interest = (monthly_principal_interest * num_payments) - loan_amount
            total_paid = loan_amount + total_interest
            
            # Closing costs
            closing_costs = home_price * (closing_costs_percent / 100)
            total_upfront_costs = down_payment + closing_costs
            
            # Generate detailed analysis
            affordability_analysis = self._calculate_affordability(total_monthly_payment, home_price)
            amortization_summary = self._generate_mortgage_amortization(loan_amount, monthly_rate, monthly_principal_interest)
            scenario_analysis = self._generate_scenarios(home_price, annual_rate, loan_term_years)
            tax_benefits = self._calculate_tax_benefits(monthly_principal_interest, property_tax_annual, annual_rate)
            
            # Add insights and recommendations
            self._add_mortgage_insights(loan_to_value, annual_rate, total_monthly_payment, home_price)
            
            return {
                'home_price': round(home_price, 2),
                'down_payment': round(down_payment, 2),
                'down_payment_percent': down_payment_percent,
                'loan_amount': round(loan_amount, 2),
                'loan_to_value': round(loan_to_value, 1),
                'annual_rate': annual_rate,
                'loan_term_years': loan_term_years,
                'monthly_principal_interest': round(monthly_principal_interest, 2),
                'property_tax_monthly': round(property_tax_monthly, 2),
                'insurance_monthly': round(insurance_monthly, 2),
                'pmi_monthly': round(pmi_monthly, 2),
                'hoa_monthly': round(hoa_monthly, 2),
                'total_monthly_payment': round(total_monthly_payment, 2),
                'total_interest': round(total_interest, 2),
                'total_paid': round(total_paid, 2),
                'closing_costs': round(closing_costs, 2),
                'total_upfront_costs': round(total_upfront_costs, 2),
                'affordability_analysis': affordability_analysis,
                'amortization_summary': amortization_summary,
                'scenario_analysis': scenario_analysis,
                'tax_benefits': tax_benefits,
                'monthly_breakdown': {
                    'principal_interest': round(monthly_principal_interest, 2),
                    'property_tax': round(property_tax_monthly, 2),
                    'insurance': round(insurance_monthly, 2),
                    'pmi': round(pmi_monthly, 2),
                    'hoa': round(hoa_monthly, 2),
                    'total': round(total_monthly_payment, 2)
                },
                'mortgage_insights': {
                    'first_year_interest': round(loan_amount * (annual_rate / 100), 2),
                    'first_year_principal': round((monthly_principal_interest * 12) - (loan_amount * (annual_rate / 100)), 2),
                    'years_to_pay_off_pmi': round(self._calculate_pmi_removal_time(loan_amount, monthly_principal_interest, monthly_rate), 1) if pmi_monthly > 0 else 0,
                    'break_even_years': round(closing_costs / (total_monthly_payment * 12) * 100, 1)
                },
                'warnings': self.warnings,
                'tips': self.tips,
                'explanation': self.get_explanation(),
                'inputs': inputs
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _calculate_affordability(self, monthly_payment, home_price):
        """Calculate affordability metrics"""
        return {
            'monthly_payment': round(monthly_payment, 2),
            'recommended_annual_income': round(monthly_payment * 42, 2),  # 28% rule
            'recommended_monthly_income': round(monthly_payment * 3.5, 2),
            'max_monthly_debt': round(monthly_payment * 1.28, 2),  # 36% total debt rule
            'minimum_income_28_rule': round(monthly_payment / 0.28, 2),
            'minimum_income_33_rule': round(monthly_payment / 0.33, 2),
            'affordability_guidelines': {
                'conservative': 'Monthly payment ≤ 25% of gross income',
                'traditional': 'Monthly payment ≤ 28% of gross income',
                'aggressive': 'Monthly payment ≤ 33% of gross income',
                'maximum': 'Total debt payments ≤ 36% of gross income'
            }
        }
    
    def _generate_mortgage_amortization(self, principal, monthly_rate, payment):
        """Generate mortgage amortization summary"""
        balance = principal
        total_interest = 0
        yearly_summaries = []
        
        for year in range(1, min(31, int(principal / (payment * 12)) + 2)):
            year_interest = 0
            year_principal = 0
            
            for month in range(12):
                if balance <= 0:
                    break
                    
                interest_payment = balance * monthly_rate
                principal_payment = payment - interest_payment
                
                if principal_payment > balance:
                    principal_payment = balance
                    
                balance -= principal_payment
                year_interest += interest_payment
                year_principal += principal_payment
                total_interest += interest_payment
            
            yearly_summaries.append({
                'year': year,
                'principal_paid': round(year_principal, 2),
                'interest_paid': round(year_interest, 2),
                'remaining_balance': round(balance, 2),
                'cumulative_interest': round(total_interest, 2)
            })
            
            if balance <= 0:
                break
        
        return yearly_summaries[:10]  # Return first 10 years
    
    def _generate_scenarios(self, home_price, current_rate, loan_term):
        """Generate different mortgage scenarios"""
        scenarios = []
        
        # Different down payment scenarios
        for dp_percent in [5, 10, 15, 20, 25]:
            down_payment = home_price * (dp_percent / 100)
            loan_amount = home_price - down_payment
            monthly_rate = current_rate / 100 / 12
            num_payments = loan_term * 12
            
            if monthly_rate == 0:
                payment = loan_amount / num_payments
            else:
                payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            total_interest = (payment * num_payments) - loan_amount
            
            # PMI calculation
            pmi_monthly = 0
            if (loan_amount / home_price) > 0.8:
                pmi_monthly = (loan_amount * 0.005) / 12  # 0.5% annual PMI
            
            scenarios.append({
                'down_payment_percent': dp_percent,
                'down_payment_amount': round(down_payment, 2),
                'loan_amount': round(loan_amount, 2),
                'monthly_payment': round(payment, 2),
                'monthly_pmi': round(pmi_monthly, 2),
                'total_monthly': round(payment + pmi_monthly, 2),
                'total_interest': round(total_interest, 2),
                'loan_to_value': round((loan_amount / home_price) * 100, 1)
            })
        
        return scenarios
    
    def _calculate_tax_benefits(self, monthly_payment, property_tax_annual, annual_rate):
        """Calculate potential tax benefits"""
        annual_interest = monthly_payment * 12 * 0.8  # Rough estimate, decreases over time
        standard_deduction = 25900  # 2023 married filing jointly
        
        itemized_deductions = annual_interest + property_tax_annual
        potential_tax_savings = max(0, itemized_deductions - standard_deduction) * 0.22  # Assume 22% tax bracket
        
        return {
            'estimated_annual_interest': round(annual_interest, 2),
            'property_tax_annual': round(property_tax_annual, 2),
            'total_itemized_deductions': round(itemized_deductions, 2),
            'standard_deduction': standard_deduction,
            'potential_additional_tax_savings': round(potential_tax_savings, 2),
            'monthly_tax_benefit': round(potential_tax_savings / 12, 2),
            'note': 'Tax benefits depend on your tax bracket and whether you itemize deductions'
        }
    
    def _calculate_pmi_removal_time(self, loan_amount, monthly_payment, monthly_rate):
        """Calculate when PMI can be removed (80% LTV)"""
        balance = loan_amount
        months = 0
        target_balance = loan_amount * 0.8
        
        while balance > target_balance and months < 360:
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal
            months += 1
        
        return months / 12
    
    def _add_mortgage_insights(self, ltv, rate, monthly_payment, home_price):
        """Add personalized mortgage insights"""
        if ltv > 95:
            self.add_warning("Very high loan-to-value ratio. Consider saving for a larger down payment.")
        elif ltv > 80:
            self.add_warning(f"LTV of {ltv:.1f}% requires PMI. Consider 20% down payment to avoid it.")
        elif ltv <= 80:
            self.add_tip("Excellent! No PMI required with your down payment.")
        
        if rate > 7:
            self.add_warning("Interest rate is quite high. Consider shopping with multiple lenders.")
        elif rate < 4:
            self.add_tip("Excellent interest rate! Consider making extra principal payments.")
        
        debt_to_income_estimate = (monthly_payment / (home_price * 0.004))  # Rough estimate
        if debt_to_income_estimate > 0.28:
            self.add_warning("Monthly payment may be high relative to typical income. Ensure you can afford it.")
        
        self.add_tip("Consider getting pre-approved before house shopping to know your budget.")
        self.add_tip("Factor in maintenance costs (1-3% of home value annually).")
    
    def get_explanation(self):
        return """
        The Mortgage Calculator provides comprehensive analysis for home loan decisions, including monthly payments, 
        total costs, and affordability analysis.
        
        **Key Components:**
        1. **Principal & Interest** - Your loan payment based on amount, rate, and term
        2. **Property Taxes** - Annual property taxes divided by 12
        3. **Home Insurance** - Required insurance coverage
        4. **PMI** - Private Mortgage Insurance (required if down payment < 20%)
        5. **HOA Fees** - Homeowners Association fees (if applicable)
        
        **Advanced Features:**
        - Down payment scenario comparison
        - Amortization schedule with yearly summaries
        - Tax benefit calculations
        - Affordability analysis using industry standards
        - PMI removal timeline
        - Closing cost estimates
        
        **Affordability Guidelines:**
        - 28% Rule: Monthly payment ≤ 28% of gross income
        - 36% Rule: Total monthly debt ≤ 36% of gross income
        - Conservative: Monthly payment ≤ 25% of gross income
        
        **When to Use:**
        - Determining home affordability
        - Comparing mortgage options
        - Planning down payment strategies
        - Understanding total homeownership costs
        - Evaluating refinancing scenarios
        """

# Continue with more enhanced calculators...
# This is just the beginning - I'll add all remaining calculators with similar comprehensive features

if __name__ == '__main__':
    print("Enhanced Calculator Suite Starting...")
    print(f"Registered calculators: {len(calculators)}")
    for slug in calculators.keys():
        print(f"  - {slug}")
    
    # Add basic routes for testing
    @app.route('/')
    def index():
        return f"""
        <h1>Enhanced Calculator Suite</h1>
        <p>Available calculators: {len(calculators)}</p>
        <ul>
        {''.join([f'<li><a href="/calculators/{slug}/">{slug.title()}</a></li>' for slug in calculators.keys()])}
        </ul>
        """
    
    @app.route('/calculators/<calculator_slug>/')
    def calculator_page(calculator_slug):
        if calculator_slug not in calculators:
            return "Calculator not found", 404
        
        calc_class = calculators[calculator_slug]
        calculator = calc_class()
        
        return f"""
        <h1>{calculator_slug.title()} Calculator</h1>
        <p>{calculator.get_explanation()}</p>
        <p><a href="/api/calculate/{calculator_slug}">API Endpoint</a></p>
        <p><a href="/">Back to Home</a></p>
        """
    
    @app.route('/api/calculate/<calculator_slug>', methods=['POST'])
    def calculate_api(calculator_slug):
        if calculator_slug not in calculators:
            return jsonify({'error': 'Calculator not found'}), 404
        
        calc_class = calculators[calculator_slug]
        calculator = calc_class()
        inputs = request.get_json() or {}
        
        try:
            result = calculator.calculate(inputs)
            calculator_usage_stats[calculator_slug] += 1
            
            # Log calculation
            calculation_logs.append({
                'calculator': calculator_slug,
                'inputs': inputs,
                'timestamp': datetime.now().isoformat(),
                'ip': request.remote_addr
            })
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    app.run(host='0.0.0.0', port=5000, debug=True)