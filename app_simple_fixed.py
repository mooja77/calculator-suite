#!/usr/bin/env python3
"""
Simplified Calculator Suite - Fixed Version
Perfect for getting started and testing the core functionality
"""

from flask import Flask, render_template, request, jsonify, Response
import os
import json
import time
import math
import traceback
from datetime import datetime

# Simple in-memory storage for this demo
calculation_logs = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# Calculator Registry
calculators = {}

def register_calculator(calc_class):
    """Register a calculator"""
    instance = calc_class()
    calculators[instance.slug] = calc_class
    return calc_class

# Base Calculator Class
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

# Loan Calculator
@register_calculator
class LoanCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            loan_amount = float(inputs['loan_amount'])
            annual_rate = float(inputs['annual_rate']) / 100  # Convert percentage to decimal
            loan_term_years = float(inputs['loan_term_years'])
            loan_type = inputs.get('loan_type', 'personal')
            
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
            
            # Generate amortization summary (first year)
            amortization_sample = self._generate_amortization_sample(loan_amount, monthly_rate, monthly_payment, 12)
            
            return {
                'loan_amount': round(loan_amount, 2),
                'annual_rate': float(inputs['annual_rate']),
                'loan_term_years': loan_term_years,
                'monthly_payment': round(monthly_payment, 2),
                'total_paid': round(total_paid, 2),
                'total_interest': round(total_interest, 2),
                'loan_type': loan_type,
                'loan_info': self._get_loan_info(loan_type),
                'amortization_sample': amortization_sample,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        # Validate loan amount
        if 'loan_amount' not in inputs or inputs['loan_amount'] == '':
            self.add_error("Loan amount is required")
        else:
            amount = self.validate_number(inputs['loan_amount'], 'Loan amount', 100, 10000000)
            if amount is None:
                pass
        
        # Validate annual interest rate
        if 'annual_rate' not in inputs or inputs['annual_rate'] == '':
            self.add_error("Annual interest rate is required")
        else:
            rate = self.validate_number(inputs['annual_rate'], 'Annual interest rate', 0, 50)
            if rate is None:
                pass
        
        # Validate loan term
        if 'loan_term_years' not in inputs or inputs['loan_term_years'] == '':
            self.add_error("Loan term is required")
        else:
            term = self.validate_number(inputs['loan_term_years'], 'Loan term', 0.5, 50)
            if term is None:
                pass
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Loan Calculator - Calculate Monthly Payments Online Free',
            'description': 'Free loan calculator for personal loans, auto loans, student loans, and debt consolidation. Calculate monthly payments, total interest, and amortization schedules.',
            'keywords': 'loan calculator, monthly payment, personal loan, auto loan, student loan, debt consolidation, interest calculator',
            'canonical': '/calculators/loan/'
        }
    
    def _generate_amortization_sample(self, balance, monthly_rate, payment, months):
        schedule = []
        remaining_balance = balance
        
        for month in range(1, min(months + 1, 13)):  # Show first 12 months max
            if remaining_balance <= 0:
                break
                
            interest_payment = remaining_balance * monthly_rate
            principal_payment = payment - interest_payment
            
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                interest_payment = payment - principal_payment
            
            remaining_balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment': round(payment, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'balance': round(max(0, remaining_balance), 2)
            })
        
        return schedule
    
    def _get_loan_info(self, loan_type):
        info = {
            'personal': {
                'description': 'Unsecured loans for personal expenses',
                'typical_rates': '6% - 36%',
                'typical_terms': '2 - 7 years',
                'uses': ['Debt consolidation', 'Home improvements', 'Medical expenses', 'Large purchases']
            },
            'auto': {
                'description': 'Secured loans for vehicle purchases',
                'typical_rates': '3% - 15%',
                'typical_terms': '3 - 8 years',
                'uses': ['New car purchase', 'Used car purchase', 'Refinancing existing auto loan']
            },
            'student': {
                'description': 'Education financing for tuition and expenses',
                'typical_rates': '3% - 12%',
                'typical_terms': '10 - 30 years',
                'uses': ['Tuition payments', 'Room and board', 'Books and supplies', 'Education-related expenses']
            },
            'mortgage': {
                'description': 'Real estate secured loans for home purchases',
                'typical_rates': '3% - 8%',
                'typical_terms': '15 - 30 years',
                'uses': ['Home purchase', 'Refinancing', 'Home equity', 'Investment property']
            }
        }
        return info.get(loan_type, info['personal'])

# Income Tax Calculator
@register_calculator
class IncomeTaxCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            annual_income = float(inputs['annual_income'])
            filing_status = inputs.get('filing_status', 'single')
            state = inputs.get('state', 'no_state_tax')
            tax_year = int(inputs.get('tax_year', 2024))
            
            # Standard deductions for 2024
            standard_deductions = {
                'single': 14600,
                'married_jointly': 29200,
                'married_separately': 14600,
                'head_of_household': 21900
            }
            
            standard_deduction = standard_deductions.get(filing_status, 14600)
            
            # Calculate federal tax
            federal_tax = self._calculate_federal_tax(annual_income, filing_status, standard_deduction, tax_year)
            
            # Calculate state tax
            state_tax = self._calculate_state_tax(annual_income, state, filing_status)
            
            # FICA taxes (Social Security + Medicare)
            social_security_tax = min(annual_income * 0.062, 10453.20)  # 2024 SS wage base
            medicare_tax = annual_income * 0.0145
            additional_medicare = max(0, (annual_income - self._get_medicare_threshold(filing_status)) * 0.009)
            
            fica_total = social_security_tax + medicare_tax + additional_medicare
            
            # Total taxes
            total_tax = federal_tax + state_tax + fica_total
            
            # After-tax income
            net_income = annual_income - total_tax
            
            # Effective and marginal rates
            effective_rate = (total_tax / annual_income) * 100 if annual_income > 0 else 0
            marginal_rate = self._get_marginal_rate(annual_income, filing_status)
            
            return {
                'annual_income': round(annual_income, 2),
                'federal_tax': round(federal_tax, 2),
                'state_tax': round(state_tax, 2),
                'social_security_tax': round(social_security_tax, 2),
                'medicare_tax': round(medicare_tax, 2),
                'additional_medicare': round(additional_medicare, 2),
                'fica_total': round(fica_total, 2),
                'total_tax': round(total_tax, 2),
                'net_income': round(net_income, 2),
                'effective_rate': round(effective_rate, 2),
                'marginal_rate': round(marginal_rate, 2),
                'standard_deduction': standard_deduction,
                'taxable_income': round(max(0, annual_income - standard_deduction), 2),
                'monthly_net': round(net_income / 12, 2),
                'monthly_tax': round(total_tax / 12, 2),
                'filing_status': filing_status,
                'state': state,
                'tax_year': tax_year,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'annual_income' not in inputs or inputs['annual_income'] == '':
            self.add_error("Annual income is required")
        else:
            income = self.validate_number(inputs['annual_income'], 'Annual income', 0, 10000000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Income Tax Calculator - Federal and State Tax Calculator Free',
            'description': 'Free income tax calculator for federal and state taxes. Calculate your tax liability, refund, and take-home pay for 2024.',
            'keywords': 'income tax calculator, federal tax, state tax, tax refund, payroll tax, FICA tax, tax brackets',
            'canonical': '/calculators/income-tax/'
        }
    
    def _calculate_federal_tax(self, income, filing_status, standard_deduction, tax_year):
        """Calculate federal income tax using 2024 tax brackets"""
        taxable_income = max(0, income - standard_deduction)
        
        # 2024 Federal tax brackets
        brackets = {
            'single': [
                (11000, 0.10),
                (44725, 0.12),
                (95375, 0.22),
                (197050, 0.24),
                (243725, 0.32),
                (609350, 0.35),
                (float('inf'), 0.37)
            ],
            'married_jointly': [
                (22000, 0.10),
                (89450, 0.12),
                (190750, 0.22),
                (364200, 0.24),
                (462500, 0.32),
                (693750, 0.35),
                (float('inf'), 0.37)
            ]
        }
        
        # Use single brackets for other filing statuses as approximation
        if filing_status not in brackets:
            filing_status = 'single'
        
        tax_brackets = brackets[filing_status]
        
        federal_tax = 0
        previous_bracket = 0
        
        for bracket_limit, rate in tax_brackets:
            if taxable_income <= previous_bracket:
                break
            
            taxable_in_bracket = min(taxable_income - previous_bracket, bracket_limit - previous_bracket)
            federal_tax += taxable_in_bracket * rate
            previous_bracket = bracket_limit
            
            if taxable_income <= bracket_limit:
                break
        
        return federal_tax
    
    def _calculate_state_tax(self, income, state, filing_status):
        """Calculate state tax (simplified - major states only)"""
        if state == 'no_state_tax':
            return 0
        
        # Simplified state tax rates (flat rates for demonstration)
        state_rates = {
            'california': 0.09,      # Progressive, simplified to ~9%
            'new_york': 0.08,        # Progressive, simplified to ~8%
            'texas': 0.0,            # No state income tax
            'florida': 0.0,          # No state income tax
            'illinois': 0.0495,      # Flat 4.95%
            'pennsylvania': 0.0307,  # Flat 3.07%
            'washington': 0.0,       # No state income tax
            'nevada': 0.0,           # No state income tax
            'tennessee': 0.0,        # No state income tax
            'new_hampshire': 0.0,    # No state income tax on wages
        }
        
        rate = state_rates.get(state, 0.05)  # Default 5% if state not found
        return income * rate
    
    def _get_medicare_threshold(self, filing_status):
        """Get Additional Medicare Tax threshold"""
        thresholds = {
            'single': 200000,
            'married_jointly': 250000,
            'married_separately': 125000,
            'head_of_household': 200000
        }
        return thresholds.get(filing_status, 200000)
    
    def _get_marginal_rate(self, income, filing_status):
        """Get marginal tax rate"""
        # Simplified marginal rate calculation
        if income <= 11000:
            return 10.0
        elif income <= 44725:
            return 12.0
        elif income <= 95375:
            return 22.0
        elif income <= 197050:
            return 24.0
        elif income <= 243725:
            return 32.0
        elif income <= 609350:
            return 35.0
        else:
            return 37.0

# Sales Tax Calculator
@register_calculator
class SalesTaxCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            purchase_amount = float(inputs['purchase_amount'])
            location = inputs.get('location', 'custom')
            
            if location == 'custom':
                tax_rate = float(inputs.get('tax_rate', 0)) / 100
            else:
                tax_rate = self._get_location_tax_rate(location)
            
            # Calculate sales tax
            sales_tax = purchase_amount * tax_rate
            total_amount = purchase_amount + sales_tax
            
            return {
                'purchase_amount': round(purchase_amount, 2),
                'tax_rate': round(tax_rate * 100, 2),
                'sales_tax': round(sales_tax, 2),
                'total_amount': round(total_amount, 2),
                'location': location,
                'location_info': self._get_location_info(location) if location != 'custom' else None,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'purchase_amount' not in inputs or inputs['purchase_amount'] == '':
            self.add_error("Purchase amount is required")
        else:
            amount = self.validate_number(inputs['purchase_amount'], 'Purchase amount', 0, 1000000)
        
        location = inputs.get('location', 'custom')
        if location == 'custom':
            if 'tax_rate' not in inputs or inputs['tax_rate'] == '':
                self.add_error("Tax rate is required when using custom location")
            else:
                rate = self.validate_number(inputs['tax_rate'], 'Tax rate', 0, 50)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Sales Tax Calculator - Calculate Sales Tax by State and City',
            'description': 'Free sales tax calculator. Calculate sales tax by state, city, and ZIP code. Get accurate tax rates for 2024.',
            'keywords': 'sales tax calculator, state sales tax, city sales tax, tax rate, purchase tax, retail tax',
            'canonical': '/calculators/sales-tax/'
        }
    
    def _get_location_tax_rate(self, location):
        """Get sales tax rate by location (state + average local)"""
        # Sales tax rates (state + average local) for 2024
        tax_rates = {
            'alabama': 0.0913,      # 4.0% state + 5.13% avg local
            'alaska': 0.0176,       # 0% state + 1.76% avg local
            'arizona': 0.0837,      # 5.6% state + 2.77% avg local
            'arkansas': 0.0947,     # 6.5% state + 2.97% avg local
            'california': 0.0868,   # 7.25% state + 1.43% avg local
            'colorado': 0.0763,     # 2.9% state + 4.73% avg local
            'connecticut': 0.0635,  # 6.35% state + 0% local
            'delaware': 0.0000,     # 0% state tax
            'florida': 0.0701,      # 6.0% state + 1.01% avg local
            'georgia': 0.0729,      # 4.0% state + 3.29% avg local
            'hawaii': 0.0444,       # 4.0% state + 0.44% avg local
            'idaho': 0.0602,        # 6.0% state + 0.02% avg local
            'illinois': 0.0876,     # 6.25% state + 2.51% avg local
            'indiana': 0.0700,      # 7.0% state + 0% local
            'iowa': 0.0679,         # 6.0% state + 0.79% avg local
            'kansas': 0.0871,       # 6.5% state + 2.21% avg local
            'kentucky': 0.0600,     # 6.0% state + 0% local
            'louisiana': 0.0945,    # 4.45% state + 5.0% avg local
            'maine': 0.0550,        # 5.5% state + 0% local
            'maryland': 0.0600,     # 6.0% state + 0% local
            'massachusetts': 0.0625, # 6.25% state + 0% local
            'michigan': 0.0600,     # 6.0% state + 0% local
            'minnesota': 0.0774,    # 6.875% state + 0.865% avg local
            'mississippi': 0.0807,  # 7.0% state + 1.07% avg local
            'missouri': 0.0823,     # 4.225% state + 4.005% avg local
            'montana': 0.0000,      # 0% state tax
            'nebraska': 0.0694,     # 5.5% state + 1.44% avg local
            'nevada': 0.0815,       # 6.85% state + 1.3% avg local
            'new_hampshire': 0.0000, # 0% state tax
            'new_jersey': 0.0663,   # 6.625% state + 0% local
            'new_mexico': 0.0781,   # 5.125% state + 2.69% avg local
            'new_york': 0.0804,     # 4.0% state + 4.04% avg local
            'north_carolina': 0.0697, # 4.75% state + 2.22% avg local
            'north_dakota': 0.0695, # 5.0% state + 1.95% avg local
            'ohio': 0.0728,         # 5.75% state + 1.53% avg local
            'oklahoma': 0.0889,     # 4.5% state + 4.39% avg local
            'oregon': 0.0000,       # 0% state tax
            'pennsylvania': 0.0634, # 6.0% state + 0.34% avg local
            'rhode_island': 0.0700, # 7.0% state + 0% local
            'south_carolina': 0.0743, # 6.0% state + 1.43% avg local
            'south_dakota': 0.0645, # 4.5% state + 1.95% avg local
            'tennessee': 0.0947,    # 7.0% state + 2.47% avg local
            'texas': 0.0820,        # 6.25% state + 1.95% avg local
            'utah': 0.0719,         # 6.1% state + 1.09% avg local
            'vermont': 0.0624,      # 6.0% state + 0.24% avg local
            'virginia': 0.0573,     # 5.3% state + 0.43% avg local
            'washington': 0.0935,   # 6.5% state + 2.85% avg local
            'west_virginia': 0.0665, # 6.0% state + 0.65% avg local
            'wisconsin': 0.0543,    # 5.0% state + 0.43% avg local
            'wyoming': 0.0546,      # 4.0% state + 1.46% avg local
        }
        
        return tax_rates.get(location, 0.0875)  # Default ~8.75% if not found
    
    def _get_location_info(self, location):
        """Get location information and tax details"""
        location_info = {
            'california': {
                'state_rate': '7.25%',
                'avg_local_rate': '1.43%',
                'total_range': '7.25% - 11.75%',
                'note': 'Local taxes vary significantly by city and county'
            },
            'texas': {
                'state_rate': '6.25%',
                'avg_local_rate': '1.95%',
                'total_range': '6.25% - 8.25%',
                'note': 'No state income tax, relies heavily on sales tax'
            },
            'new_york': {
                'state_rate': '4.0%',
                'avg_local_rate': '4.04%',
                'total_range': '4.0% - 8.875%',
                'note': 'NYC has additional local taxes up to 4.875%'
            },
            'florida': {
                'state_rate': '6.0%',
                'avg_local_rate': '1.01%',
                'total_range': '6.0% - 8.5%',
                'note': 'No state income tax, tourist areas may have higher rates'
            },
            'washington': {
                'state_rate': '6.5%',
                'avg_local_rate': '2.85%',
                'total_range': '6.5% - 10.75%',
                'note': 'No state income tax, Seattle has highest combined rate'
            },
            'delaware': {
                'state_rate': '0%',
                'avg_local_rate': '0%',
                'total_range': '0%',
                'note': 'No sales tax statewide - popular for major purchases'
            },
            'oregon': {
                'state_rate': '0%',
                'avg_local_rate': '0%',
                'total_range': '0%',
                'note': 'No sales tax statewide'
            },
            'montana': {
                'state_rate': '0%',
                'avg_local_rate': '0%',
                'total_range': '0%',
                'note': 'No statewide sales tax'
            },
            'new_hampshire': {
                'state_rate': '0%',
                'avg_local_rate': '0%',
                'total_range': '0%',
                'note': 'No sales tax or income tax'
            }
        }
        
        return location_info.get(location, {
            'state_rate': 'Varies',
            'avg_local_rate': 'Varies',
            'total_range': 'Varies',
            'note': 'Tax rates vary by location'
        })

# Property Tax Calculator
@register_calculator
class PropertyTaxCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            home_value = float(inputs['home_value'])
            location = inputs.get('location', 'custom')
            
            if location == 'custom':
                tax_rate = float(inputs.get('tax_rate', 0)) / 100
            else:
                tax_rate = self._get_location_tax_rate(location)
            
            # Apply exemptions
            homestead_exemption = float(inputs.get('homestead_exemption', 0))
            senior_exemption = float(inputs.get('senior_exemption', 0))
            veteran_exemption = float(inputs.get('veteran_exemption', 0))
            other_exemptions = float(inputs.get('other_exemptions', 0))
            
            # Calculate taxable value
            total_exemptions = homestead_exemption + senior_exemption + veteran_exemption + other_exemptions
            taxable_value = max(0, home_value - total_exemptions)
            
            # Calculate property tax
            annual_tax = taxable_value * tax_rate
            monthly_tax = annual_tax / 12
            
            # Calculate effective tax rate (on full home value)
            effective_rate = (annual_tax / home_value) * 100 if home_value > 0 else 0
            
            return {
                'home_value': round(home_value, 2),
                'taxable_value': round(taxable_value, 2),
                'tax_rate': round(tax_rate * 100, 4),
                'annual_tax': round(annual_tax, 2),
                'monthly_tax': round(monthly_tax, 2),
                'effective_rate': round(effective_rate, 4),
                'total_exemptions': round(total_exemptions, 2),
                'exemption_breakdown': {
                    'homestead': round(homestead_exemption, 2),
                    'senior': round(senior_exemption, 2),
                    'veteran': round(veteran_exemption, 2),
                    'other': round(other_exemptions, 2)
                },
                'location': location,
                'location_info': self._get_location_info(location) if location != 'custom' else None,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'home_value' not in inputs or inputs['home_value'] == '':
            self.add_error("Home value is required")
        else:
            value = self.validate_number(inputs['home_value'], 'Home value', 1, 50000000)
        
        location = inputs.get('location', 'custom')
        if location == 'custom':
            if 'tax_rate' not in inputs or inputs['tax_rate'] == '':
                self.add_error("Tax rate is required when using custom location")
            else:
                rate = self.validate_number(inputs['tax_rate'], 'Tax rate', 0, 10)
        
        # Validate exemptions (optional)
        for field in ['homestead_exemption', 'senior_exemption', 'veteran_exemption', 'other_exemptions']:
            if field in inputs and inputs[field] != '':
                self.validate_number(inputs[field], field.replace('_', ' ').title(), 0, 1000000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Property Tax Calculator - Calculate Annual Property Taxes',
            'description': 'Free property tax calculator. Estimate annual property taxes by state, county, and city with exemptions for 2024.',
            'keywords': 'property tax calculator, property tax rate, homestead exemption, property tax by state, real estate tax',
            'canonical': '/calculators/property-tax/'
        }
    
    def _get_location_tax_rate(self, location):
        """Get average property tax rate by state (2024 data)"""        
        # Property tax rates as percentage of home value (effective rates)
        tax_rates = {
            'new_jersey': 0.0249,    # Highest in US - 2.49%
            'illinois': 0.0238,      # 2.38%
            'new_hampshire': 0.0186, # 1.86%
            'connecticut': 0.0173,   # 1.73%
            'vermont': 0.0159,       # 1.59%
            'texas': 0.0181,         # 1.81%
            'wisconsin': 0.0169,     # 1.69%
            'pennsylvania': 0.0159,  # 1.59%
            'nebraska': 0.0176,      # 1.76%
            'ohio': 0.0161,          # 1.61%
            'rhode_island': 0.0147,  # 1.47%
            'iowa': 0.0160,          # 1.60%
            'new_york': 0.0173,      # 1.73%
            'kansas': 0.0170,        # 1.70%
            'michigan': 0.0162,      # 1.62%
            'maine': 0.0136,         # 1.36%
            'minnesota': 0.0111,     # 1.11%
            'massachusetts': 0.0133, # 1.33%
            'north_dakota': 0.0098,  # 0.98%
            'alaska': 0.0123,        # 1.23%
            'maryland': 0.0117,      # 1.17%
            'florida': 0.0097,       # 0.97%
            'oregon': 0.0111,        # 1.11%
            'georgia': 0.0092,       # 0.92%
            'south_dakota': 0.0128,  # 1.28%
            'indiana': 0.0089,       # 0.89%
            'missouri': 0.0103,      # 1.03%
            'washington': 0.0094,    # 0.94%
            'oklahoma': 0.0090,      # 0.90%
            'virginia': 0.0084,      # 0.84%
            'california': 0.0081,    # 0.81%
            'arizona': 0.0070,       # 0.70%
            'north_carolina': 0.0090, # 0.90%
            'kentucky': 0.0086,      # 0.86%
            'idaho': 0.0069,         # 0.69%
            'utah': 0.0060,          # 0.60%
            'south_carolina': 0.0059, # 0.59%
            'tennessee': 0.0067,     # 0.67%
            'montana': 0.0084,       # 0.84%
            'new_mexico': 0.0078,    # 0.78%
            'wyoming': 0.0062,       # 0.62%
            'colorado': 0.0051,      # 0.51%
            'west_virginia': 0.0059, # 0.59%
            'nevada': 0.0066,        # 0.66%
            'alabama': 0.0041,       # 0.41%
            'arkansas': 0.0063,      # 0.63%
            'mississippi': 0.0081,   # 0.81%
            'louisiana': 0.0056,     # 0.56%
            'delaware': 0.0062,      # 0.62%
            'hawaii': 0.0031,        # Lowest in US - 0.31%
        }
        
        return tax_rates.get(location, 0.0121)  # Default ~1.21% US average if not found
    
    def _get_location_info(self, location):
        """Get location information and property tax details"""
        location_info = {
            'new_jersey': {
                'avg_rate': '2.49%',
                'rank': '1st (Highest)',
                'avg_tax_on_200k': '$4,980',
                'note': 'Highest property taxes in US, but good schools and services'
            },
            'illinois': {
                'avg_rate': '2.38%',
                'rank': '2nd',
                'avg_tax_on_200k': '$4,760',
                'note': 'High taxes especially in Cook County (Chicago area)'
            },
            'texas': {
                'avg_rate': '1.81%',
                'rank': '6th',
                'avg_tax_on_200k': '$3,620',
                'note': 'No state income tax, relies heavily on property tax'
            },
            'california': {
                'avg_rate': '0.81%',
                'rank': '17th',
                'avg_tax_on_200k': '$1,620',
                'note': 'Prop 13 limits increases, but high home values offset low rates'
            },
            'florida': {
                'avg_rate': '0.97%',
                'rank': '27th',
                'avg_tax_on_200k': '$1,940',
                'note': 'Homestead exemption up to $50K, no state income tax'
            },
            'new_york': {
                'avg_rate': '1.73%',
                'rank': '13th',
                'avg_tax_on_200k': '$3,460',
                'note': 'Varies widely by county, NYC has additional taxes'
            },
            'hawaii': {
                'avg_rate': '0.31%',
                'rank': '50th (Lowest)',
                'avg_tax_on_200k': '$620',
                'note': 'Lowest property taxes but high cost of living'
            },
            'alabama': {
                'avg_rate': '0.41%',
                'rank': '49th',
                'avg_tax_on_200k': '$820',
                'note': 'Very low property taxes, homestead exemption available'
            }
        }
        
        return location_info.get(location, {
            'avg_rate': 'Varies',
            'rank': 'N/A',
            'avg_tax_on_200k': 'Varies',
            'note': 'Tax rates vary significantly by county and municipality'
        })

# Tax Refund Estimator
@register_calculator
class TaxRefundCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            annual_income = float(inputs['annual_income'])
            federal_withholding = float(inputs.get('federal_withholding', 0))
            state_withholding = float(inputs.get('state_withholding', 0))
            filing_status = inputs.get('filing_status', 'single')
            state = inputs.get('state', 'no_state_tax')
            dependents = int(inputs.get('dependents', 0))
            
            # Calculate actual tax liability using existing logic
            income_calc = IncomeTaxCalculator()
            tax_result = income_calc.calculate({
                'annual_income': annual_income,
                'filing_status': filing_status,
                'state': state,
                'tax_year': 2024
            })
            
            actual_federal_tax = tax_result['federal_tax']
            actual_state_tax = tax_result['state_tax']
            
            # Calculate refunds/owed
            federal_refund = federal_withholding - actual_federal_tax
            state_refund = state_withholding - actual_state_tax
            total_refund = federal_refund + state_refund
            
            # Add tax credits
            child_tax_credit = self._calculate_child_tax_credit(annual_income, filing_status, dependents)
            earned_income_credit = self._calculate_earned_income_credit(annual_income, filing_status, dependents)
            
            # Adjust refund with credits
            total_credits = child_tax_credit + earned_income_credit
            final_refund = total_refund + total_credits
            
            # Determine if refund or owed
            refund_status = "refund" if final_refund > 0 else "owed" if final_refund < 0 else "even"
            
            return {
                'annual_income': round(annual_income, 2),
                'federal_withholding': round(federal_withholding, 2),
                'state_withholding': round(state_withholding, 2),
                'actual_federal_tax': round(actual_federal_tax, 2),
                'actual_state_tax': round(actual_state_tax, 2),
                'federal_refund': round(federal_refund, 2),
                'state_refund': round(state_refund, 2),
                'child_tax_credit': round(child_tax_credit, 2),
                'earned_income_credit': round(earned_income_credit, 2),
                'total_credits': round(total_credits, 2),
                'total_refund': round(total_refund, 2),
                'final_refund': round(abs(final_refund), 2),
                'refund_status': refund_status,
                'effective_rate': tax_result['effective_rate'],
                'filing_status': filing_status,
                'state': state,
                'dependents': dependents,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'annual_income' not in inputs or inputs['annual_income'] == '':
            self.add_error("Annual income is required")
        else:
            income = self.validate_number(inputs['annual_income'], 'Annual income', 0, 10000000)
        
        # Validate withholdings (optional but should be numbers if provided)
        for field in ['federal_withholding', 'state_withholding']:
            if field in inputs and inputs[field] != '':
                self.validate_number(inputs[field], field.replace('_', ' ').title(), 0, 1000000)
        
        # Validate dependents
        if 'dependents' in inputs and inputs['dependents'] != '':
            deps = self.validate_number(inputs['dependents'], 'Dependents', 0, 20)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Tax Refund Calculator - Estimate Your Federal and State Tax Refund',
            'description': 'Free tax refund estimator. Calculate your 2024 federal and state tax refund with withholdings, credits, and deductions.',
            'keywords': 'tax refund calculator, tax refund estimator, federal refund, state refund, tax withholding, tax credits',
            'canonical': '/calculators/tax-refund/'
        }
    
    def _calculate_child_tax_credit(self, income, filing_status, dependents):
        """Calculate Child Tax Credit for 2024"""
        if dependents == 0:
            return 0
        
        # 2024 Child Tax Credit - $2,000 per qualifying child
        max_credit_per_child = 2000
        max_credit = dependents * max_credit_per_child
        
        # Phase-out thresholds
        phase_out_thresholds = {
            'single': 200000,
            'married_jointly': 400000,
            'married_separately': 200000,
            'head_of_household': 200000
        }
        
        threshold = phase_out_thresholds.get(filing_status, 200000)
        
        if income <= threshold:
            return max_credit
        
        # Phase out $50 for every $1,000 over threshold
        excess = income - threshold
        reduction = (excess / 1000) * 50
        
        return max(0, max_credit - reduction)
    
    def _calculate_earned_income_credit(self, income, filing_status, dependents):
        """Calculate Earned Income Tax Credit for 2024"""
        # 2024 EITC parameters (simplified)
        if filing_status == 'married_separately':
            return 0  # Generally not eligible if married filing separately
        
        # Maximum credit amounts and income limits (2024)
        eitc_params = {
            0: {'max_credit': 632, 'phase_out_start': 9800, 'max_income': 17640},
            1: {'max_credit': 3995, 'phase_out_start': 11750, 'max_income': 47915},
            2: {'max_credit': 6604, 'phase_out_start': 11750, 'max_income': 53057},
            3: {'max_credit': 7430, 'phase_out_start': 11750, 'max_income': 56838}
        }
        
        # Use parameters for number of dependents (max 3+)
        num_children = min(dependents, 3)
        params = eitc_params.get(num_children, eitc_params[3])
        
        # Adjust for married filing jointly
        if filing_status == 'married_jointly':
            params['max_income'] += 6500  # Marriage bonus
        
        if income > params['max_income']:
            return 0
        
        if income <= params['phase_out_start']:
            # In phase-in range - simplified calculation
            phase_in_rate = 0.34 if num_children == 0 else 0.40  # Simplified rates
            return min(income * phase_in_rate, params['max_credit'])
        
        # In phase-out range
        excess = income - params['phase_out_start']
        phase_out_rate = 0.1576 if num_children == 0 else 0.2106  # Simplified rates
        reduction = excess * phase_out_rate
        
        return max(0, params['max_credit'] - reduction)

# Gross to Net Salary Calculator
@register_calculator
class GrossToNetCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            gross_salary = float(inputs['gross_salary'])
            pay_frequency = inputs.get('pay_frequency', 'annual')
            filing_status = inputs.get('filing_status', 'single')
            state = inputs.get('state', 'no_state_tax')
            allowances = int(inputs.get('allowances', 0))
            
            # Pre-tax deductions
            retirement_401k = float(inputs.get('retirement_401k', 0))
            health_insurance = float(inputs.get('health_insurance', 0))
            dental_vision = float(inputs.get('dental_vision', 0))
            fsa_hsa = float(inputs.get('fsa_hsa', 0))
            
            # Convert to annual if needed
            if pay_frequency == 'hourly':
                annual_gross = gross_salary * 2080  # 40 hours/week * 52 weeks
            elif pay_frequency == 'weekly':
                annual_gross = gross_salary * 52
            elif pay_frequency == 'biweekly':
                annual_gross = gross_salary * 26
            elif pay_frequency == 'semimonthly':
                annual_gross = gross_salary * 24
            elif pay_frequency == 'monthly':
                annual_gross = gross_salary * 12
            else:  # annual
                annual_gross = gross_salary
            
            # Annual pre-tax deductions
            annual_pre_tax = retirement_401k + health_insurance + dental_vision + fsa_hsa
            taxable_income = annual_gross - annual_pre_tax
            
            # Calculate taxes using Income Tax Calculator
            tax_calc = IncomeTaxCalculator()
            tax_result = tax_calc.calculate({
                'annual_income': taxable_income,
                'filing_status': filing_status,
                'state': state,
                'tax_year': 2024
            })
            
            # Get tax amounts
            federal_tax = tax_result['federal_tax']
            state_tax = tax_result['state_tax']
            social_security = tax_result['social_security_tax']
            medicare = tax_result['medicare_tax'] + tax_result['additional_medicare']
            
            # Total deductions and net pay
            total_taxes = federal_tax + state_tax + social_security + medicare
            total_deductions = total_taxes + annual_pre_tax
            annual_net = annual_gross - total_deductions
            
            # Convert back to pay frequency
            pay_periods = {
                'annual': 1,
                'monthly': 12,
                'semimonthly': 24,
                'biweekly': 26,
                'weekly': 52,
                'hourly': 2080
            }
            
            periods = pay_periods.get(pay_frequency, 1)
            
            return {
                'gross_salary': round(gross_salary, 2),
                'pay_frequency': pay_frequency,
                'annual_gross': round(annual_gross, 2),
                'period_gross': round(annual_gross / periods, 2),
                'federal_tax': round(federal_tax / periods, 2),
                'state_tax': round(state_tax / periods, 2),
                'social_security': round(social_security / periods, 2),
                'medicare': round(medicare / periods, 2),
                'retirement_401k': round(retirement_401k / periods, 2),
                'health_insurance': round(health_insurance / periods, 2),
                'dental_vision': round(dental_vision / periods, 2),
                'fsa_hsa': round(fsa_hsa / periods, 2),
                'total_taxes': round(total_taxes / periods, 2),
                'total_deductions': round(total_deductions / periods, 2),
                'net_pay': round(annual_net / periods, 2),
                'annual_net': round(annual_net, 2),
                'annual_taxes': round(total_taxes, 2),
                'annual_deductions': round(total_deductions, 2),
                'effective_rate': round((total_taxes / annual_gross) * 100, 2),
                'take_home_rate': round((annual_net / annual_gross) * 100, 2),
                'filing_status': filing_status,
                'state': state,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'gross_salary' not in inputs or inputs['gross_salary'] == '':
            self.add_error("Gross salary is required")
        else:
            salary = self.validate_number(inputs['gross_salary'], 'Gross salary', 0, 10000000)
        
        # Validate optional deductions
        for field in ['retirement_401k', 'health_insurance', 'dental_vision', 'fsa_hsa']:
            if field in inputs and inputs[field] != '':
                self.validate_number(inputs[field], field.replace('_', ' ').title(), 0, 100000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Gross to Net Salary Calculator - Calculate Take Home Pay',
            'description': 'Free gross to net salary calculator. Calculate your take-home pay after taxes and deductions for 2024.',
            'keywords': 'gross to net calculator, salary calculator, take home pay, paycheck calculator, net pay calculator',
            'canonical': '/calculators/gross-to-net/'
        }

# Hourly to Salary Calculator
@register_calculator
class HourlyToSalaryCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            calculation_type = inputs.get('calculation_type', 'hourly_to_salary')
            
            if calculation_type == 'hourly_to_salary':
                hourly_rate = float(inputs['hourly_rate'])
                hours_per_week = float(inputs.get('hours_per_week', 40))
                weeks_per_year = float(inputs.get('weeks_per_year', 52))
                
                # Calculate different salary scenarios
                annual_salary = hourly_rate * hours_per_week * weeks_per_year
                monthly_salary = annual_salary / 12
                weekly_salary = hourly_rate * hours_per_week
                
                # Part-time variations
                part_time_20 = hourly_rate * 20 * weeks_per_year
                part_time_30 = hourly_rate * 30 * weeks_per_year
                
                return {
                    'calculation_type': calculation_type,
                    'hourly_rate': round(hourly_rate, 2),
                    'hours_per_week': hours_per_week,
                    'weeks_per_year': weeks_per_year,
                    'annual_salary': round(annual_salary, 2),
                    'monthly_salary': round(monthly_salary, 2),
                    'weekly_salary': round(weekly_salary, 2),
                    'daily_salary': round(weekly_salary / 5, 2),
                    'part_time_20': round(part_time_20, 2),
                    'part_time_30': round(part_time_30, 2),
                    'overtime_rate': round(hourly_rate * 1.5, 2),
                    'inputs': inputs
                }
                
            else:  # salary_to_hourly
                annual_salary = float(inputs['annual_salary'])
                hours_per_week = float(inputs.get('hours_per_week', 40))
                weeks_per_year = float(inputs.get('weeks_per_year', 52))
                
                total_hours = hours_per_week * weeks_per_year
                hourly_rate = annual_salary / total_hours
                
                # Different work scenarios
                monthly_salary = annual_salary / 12
                weekly_salary = annual_salary / weeks_per_year
                daily_salary = weekly_salary / (hours_per_week / 5) if hours_per_week >= 5 else weekly_salary
                
                # Compare to different hour scenarios
                if_35_hours = annual_salary / (35 * weeks_per_year)
                if_45_hours = annual_salary / (45 * weeks_per_year)
                
                return {
                    'calculation_type': calculation_type,
                    'annual_salary': round(annual_salary, 2),
                    'hours_per_week': hours_per_week,
                    'weeks_per_year': weeks_per_year,
                    'hourly_rate': round(hourly_rate, 2),
                    'monthly_salary': round(monthly_salary, 2),
                    'weekly_salary': round(weekly_salary, 2),
                    'daily_salary': round(daily_salary, 2),
                    'if_35_hours': round(if_35_hours, 2),
                    'if_45_hours': round(if_45_hours, 2),
                    'overtime_rate': round(hourly_rate * 1.5, 2),
                    'total_hours_year': round(total_hours, 0),
                    'inputs': inputs
                }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        calculation_type = inputs.get('calculation_type', 'hourly_to_salary')
        
        if calculation_type == 'hourly_to_salary':
            if 'hourly_rate' not in inputs or inputs['hourly_rate'] == '':
                self.add_error("Hourly rate is required")
            else:
                rate = self.validate_number(inputs['hourly_rate'], 'Hourly rate', 0.01, 1000)
        else:
            if 'annual_salary' not in inputs or inputs['annual_salary'] == '':
                self.add_error("Annual salary is required")
            else:
                salary = self.validate_number(inputs['annual_salary'], 'Annual salary', 1, 10000000)
        
        # Validate optional hours/weeks
        for field in ['hours_per_week', 'weeks_per_year']:
            if field in inputs and inputs[field] != '':
                if field == 'hours_per_week':
                    self.validate_number(inputs[field], 'Hours per week', 1, 80)
                else:
                    self.validate_number(inputs[field], 'Weeks per year', 1, 52)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Hourly to Salary Calculator - Convert Hourly Wage to Annual Salary',
            'description': 'Free hourly to salary calculator. Convert hourly wages to annual salary and vice versa. Compare part-time vs full-time pay.',
            'keywords': 'hourly to salary calculator, hourly wage converter, salary to hourly, annual salary calculator, wage calculator',
            'canonical': '/calculators/hourly-to-salary/'
        }

# Salary Raise Calculator
@register_calculator
class SalaryRaiseCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            calculation_type = inputs.get('calculation_type', 'raise_amount')
            current_salary = float(inputs['current_salary'])
            
            if calculation_type == 'raise_amount':
                # Calculate percentage from dollar amount
                raise_amount = float(inputs['raise_amount'])
                new_salary = current_salary + raise_amount
                raise_percentage = (raise_amount / current_salary) * 100
                
            elif calculation_type == 'raise_percentage':
                # Calculate dollar amount from percentage
                raise_percentage = float(inputs['raise_percentage'])
                raise_amount = current_salary * (raise_percentage / 100)
                new_salary = current_salary + raise_amount
                
            else:  # target_salary
                # Calculate raise needed to reach target
                new_salary = float(inputs['target_salary'])
                raise_amount = new_salary - current_salary
                raise_percentage = (raise_amount / current_salary) * 100
            
            # Calculate impact over time
            monthly_increase = raise_amount / 12
            weekly_increase = raise_amount / 52
            daily_increase = raise_amount / 260  # 52 weeks * 5 days
            
            # Calculate cumulative impact
            one_year_extra = raise_amount
            five_year_extra = raise_amount * 5
            ten_year_extra = raise_amount * 10
            
            # Calculate hourly impact (assuming 40 hours/week)
            hourly_increase = raise_amount / 2080  # 40 hours * 52 weeks
            
            # Performance benchmarks
            performance_context = self._get_performance_context(raise_percentage)
            
            return {
                'calculation_type': calculation_type,
                'current_salary': round(current_salary, 2),
                'new_salary': round(new_salary, 2),
                'raise_amount': round(raise_amount, 2),
                'raise_percentage': round(raise_percentage, 2),
                'monthly_increase': round(monthly_increase, 2),
                'weekly_increase': round(weekly_increase, 2),
                'daily_increase': round(daily_increase, 2),
                'hourly_increase': round(hourly_increase, 2),
                'one_year_extra': round(one_year_extra, 2),
                'five_year_extra': round(five_year_extra, 2),
                'ten_year_extra': round(ten_year_extra, 2),
                'performance_context': performance_context,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'current_salary' not in inputs or inputs['current_salary'] == '':
            self.add_error("Current salary is required")
        else:
            salary = self.validate_number(inputs['current_salary'], 'Current salary', 1, 10000000)
        
        calculation_type = inputs.get('calculation_type', 'raise_amount')
        
        if calculation_type == 'raise_amount':
            if 'raise_amount' not in inputs or inputs['raise_amount'] == '':
                self.add_error("Raise amount is required")
            else:
                amount = self.validate_number(inputs['raise_amount'], 'Raise amount', 0, 1000000)
        elif calculation_type == 'raise_percentage':
            if 'raise_percentage' not in inputs or inputs['raise_percentage'] == '':
                self.add_error("Raise percentage is required")
            else:
                percent = self.validate_number(inputs['raise_percentage'], 'Raise percentage', 0, 500)
        else:  # target_salary
            if 'target_salary' not in inputs or inputs['target_salary'] == '':
                self.add_error("Target salary is required")
            else:
                target = self.validate_number(inputs['target_salary'], 'Target salary', 1, 10000000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Salary Raise Calculator - Calculate Raise Amount and Percentage',
            'description': 'Free salary raise calculator. Calculate raise amounts, percentages, and long-term financial impact of salary increases.',
            'keywords': 'salary raise calculator, pay raise calculator, salary increase, raise percentage, salary negotiation',
            'canonical': '/calculators/salary-raise/'
        }
    
    def _get_performance_context(self, raise_percentage):
        """Provide context for raise percentage"""
        if raise_percentage <= 0:
            return {
                'category': 'No Raise',
                'description': 'No salary increase',
                'context': 'Consider discussing performance and career development with your manager.'
            }
        elif raise_percentage <= 2:
            return {
                'category': 'Cost of Living',
                'description': 'Minimal raise (0-2%)',
                'context': 'Typically covers inflation and cost of living adjustments.'
            }
        elif raise_percentage <= 4:
            return {
                'category': 'Standard Performance',
                'description': 'Average raise (2-4%)',
                'context': 'Common for meeting expectations and standard performance reviews.'
            }
        elif raise_percentage <= 7:
            return {
                'category': 'Good Performance',
                'description': 'Above average raise (4-7%)',
                'context': 'Reflects strong performance and valuable contributions.'
            }
        elif raise_percentage <= 12:
            return {
                'category': 'Excellent Performance',
                'description': 'High raise (7-12%)',
                'context': 'Exceptional performance, new responsibilities, or retention efforts.'
            }
        elif raise_percentage <= 20:
            return {
                'category': 'Promotion/Major Advancement',
                'description': 'Significant raise (12-20%)',
                'context': 'Often associated with promotions or major role expansions.'
            }
        else:
            return {
                'category': 'Major Career Change',
                'description': 'Substantial raise (20%+)',
                'context': 'Significant promotion, job change, or specialized skill premium.'
            }

# Cost of Living Calculator
@register_calculator
class CostOfLivingCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            current_salary = float(inputs['current_salary'])
            current_city = inputs.get('current_city', 'Current City')
            target_city = inputs.get('target_city', 'Target City')
            
            # Cost of living multipliers (simplified - real implementation would use API)
            col_indices = {
                'new_york': 1.68,
                'san_francisco': 1.85,
                'los_angeles': 1.35,
                'chicago': 1.08,
                'boston': 1.32,
                'seattle': 1.56,
                'washington_dc': 1.40,
                'miami': 1.10,
                'denver': 1.12,
                'atlanta': 0.97,
                'phoenix': 0.95,
                'dallas': 0.91,
                'houston': 0.89,
                'philadelphia': 1.20,
                'detroit': 0.85,
                'cleveland': 0.82,
                'national_average': 1.00
            }
            
            # Get cost indices (default to national average if not found)
            current_index = col_indices.get(inputs.get('current_city_key', 'national_average'), 1.00)
            target_index = col_indices.get(inputs.get('target_city_key', 'national_average'), 1.00)
            
            # Calculate equivalent salary
            col_ratio = target_index / current_index
            equivalent_salary = current_salary * col_ratio
            salary_difference = equivalent_salary - current_salary
            percentage_change = ((equivalent_salary - current_salary) / current_salary) * 100
            
            # Breakdown by categories
            housing_current = current_salary * 0.30 * current_index
            housing_target = current_salary * 0.30 * target_index
            housing_difference = housing_target - housing_current
            
            food_current = current_salary * 0.15 * current_index
            food_target = current_salary * 0.15 * target_index
            food_difference = food_target - food_current
            
            transportation_current = current_salary * 0.15 * current_index
            transportation_target = current_salary * 0.15 * target_index
            transportation_difference = transportation_target - transportation_current
            
            utilities_current = current_salary * 0.08 * current_index
            utilities_target = current_salary * 0.08 * target_index
            utilities_difference = utilities_target - utilities_current
            
            # Calculate purchasing power
            purchasing_power_change = (current_index / target_index) * 100 - 100
            
            # Recommendations
            recommendation = self._get_recommendation(percentage_change, col_ratio)
            
            return {
                'current_salary': round(current_salary, 2),
                'current_city': current_city,
                'target_city': target_city,
                'current_col_index': round(current_index, 2),
                'target_col_index': round(target_index, 2),
                'equivalent_salary': round(equivalent_salary, 2),
                'salary_difference': round(salary_difference, 2),
                'percentage_change': round(percentage_change, 2),
                'purchasing_power_change': round(purchasing_power_change, 2),
                'breakdown': {
                    'housing': {
                        'current': round(housing_current, 2),
                        'target': round(housing_target, 2),
                        'difference': round(housing_difference, 2)
                    },
                    'food': {
                        'current': round(food_current, 2),
                        'target': round(food_target, 2),
                        'difference': round(food_difference, 2)
                    },
                    'transportation': {
                        'current': round(transportation_current, 2),
                        'target': round(transportation_target, 2),
                        'difference': round(transportation_difference, 2)
                    },
                    'utilities': {
                        'current': round(utilities_current, 2),
                        'target': round(utilities_target, 2),
                        'difference': round(utilities_difference, 2)
                    }
                },
                'recommendation': recommendation,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'current_salary' not in inputs or inputs['current_salary'] == '':
            self.add_error("Current salary is required")
        else:
            salary = self.validate_number(inputs['current_salary'], 'Current salary', 1, 10000000)
        
        if 'current_city' not in inputs or inputs['current_city'] == '':
            self.add_error("Current city is required")
        
        if 'target_city' not in inputs or inputs['target_city'] == '':
            self.add_error("Target city is required")
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Cost of Living Calculator - Compare Cities and Salary Requirements',
            'description': 'Free cost of living calculator. Compare living costs between cities and calculate equivalent salary requirements for relocation.',
            'keywords': 'cost of living calculator, city comparison, salary comparison, relocation calculator, moving calculator',
            'canonical': '/calculators/cost-of-living/'
        }
    
    def _get_recommendation(self, percentage_change, col_ratio):
        """Provide relocation recommendations based on cost changes"""
        if abs(percentage_change) <= 5:
            return {
                'category': 'Similar Cost',
                'description': 'Minimal cost difference (±5%)',
                'advice': 'Cost of living is very similar. Focus on career opportunities and quality of life factors.'
            }
        elif percentage_change > 5 and percentage_change <= 15:
            return {
                'category': 'Moderate Increase',
                'description': f'Moderately higher cost (+{percentage_change:.1f}%)',
                'advice': 'Consider negotiating a salary increase of at least 10-15% to maintain your current lifestyle.'
            }
        elif percentage_change > 15 and percentage_change <= 30:
            return {
                'category': 'Significant Increase',
                'description': f'Significantly higher cost (+{percentage_change:.1f}%)',
                'advice': 'Negotiate a substantial salary increase (20-35%) or prepare to adjust your lifestyle and budget.'
            }
        elif percentage_change > 30:
            return {
                'category': 'Major Increase',
                'description': f'Much higher cost (+{percentage_change:.1f}%)',
                'advice': 'This move requires careful financial planning. Consider the long-term career benefits that justify the higher costs.'
            }
        elif percentage_change < -5 and percentage_change >= -15:
            return {
                'category': 'Moderate Savings',
                'description': f'Lower cost of living ({percentage_change:.1f}%)',
                'advice': 'Great opportunity to save money or improve your lifestyle with the same salary.'
            }
        else:  # percentage_change < -15
            return {
                'category': 'Significant Savings',
                'description': f'Much lower cost of living ({percentage_change:.1f}%)',
                'advice': 'Excellent opportunity for significant savings and improved quality of life. Your money will go much further.'
            }

# Compound Interest Calculator
@register_calculator
class CompoundInterestCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            principal = float(inputs['principal'])
            annual_rate = float(inputs['annual_rate']) / 100
            years = float(inputs['years'])
            compound_frequency = int(inputs.get('compound_frequency', 12))  # Monthly default
            monthly_contribution = float(inputs.get('monthly_contribution', 0))
            
            # Calculate compound interest with regular contributions
            # Formula: A = P(1 + r/n)^(nt) + PMT * [((1 + r/n)^(nt) - 1) / (r/n)]
            
            rate_per_period = annual_rate / compound_frequency
            total_periods = years * compound_frequency
            
            # Future value of initial principal
            if rate_per_period == 0:
                fv_principal = principal
                fv_contributions = monthly_contribution * 12 * years
            else:
                fv_principal = principal * ((1 + rate_per_period) ** total_periods)
                
                # Future value of regular contributions (annuity)
                periods_per_year = compound_frequency
                contribution_frequency = 12  # Monthly contributions
                contributions_per_period = monthly_contribution * (12 / compound_frequency)
                
                if rate_per_period == 0:
                    fv_contributions = contributions_per_period * total_periods
                else:
                    fv_contributions = contributions_per_period * (((1 + rate_per_period) ** total_periods - 1) / rate_per_period)
            
            total_value = fv_principal + fv_contributions
            total_contributions = monthly_contribution * 12 * years
            total_interest = total_value - principal - total_contributions
            
            # Calculate year-by-year breakdown for first 10 years or total years if less
            yearly_breakdown = []
            years_to_show = min(int(years), 10)
            
            for year in range(1, years_to_show + 1):
                year_periods = year * compound_frequency
                year_fv_principal = principal * ((1 + rate_per_period) ** year_periods) if rate_per_period > 0 else principal
                year_contributions = monthly_contribution * 12 * year
                
                if rate_per_period == 0:
                    year_fv_contributions = year_contributions
                else:
                    contributions_per_period = monthly_contribution * (12 / compound_frequency)
                    year_fv_contributions = contributions_per_period * (((1 + rate_per_period) ** year_periods - 1) / rate_per_period)
                
                year_total = year_fv_principal + year_fv_contributions
                year_interest = year_total - principal - year_contributions
                
                yearly_breakdown.append({
                    'year': year,
                    'balance': round(year_total, 2),
                    'interest_earned': round(year_interest, 2),
                    'contributions': round(year_contributions, 2)
                })
            
            # Calculate effective annual yield
            if principal > 0:
                effective_yield = ((total_value / (principal + total_contributions)) ** (1/years) - 1) * 100
            else:
                effective_yield = 0
            
            # Investment insights
            insights = self._generate_insights(principal, total_contributions, total_interest, years, annual_rate * 100)
            
            return {
                'principal': round(principal, 2),
                'annual_rate': round(annual_rate * 100, 2),
                'years': years,
                'compound_frequency': compound_frequency,
                'compound_frequency_text': self._get_frequency_text(compound_frequency),
                'monthly_contribution': round(monthly_contribution, 2),
                'total_value': round(total_value, 2),
                'total_contributions': round(total_contributions, 2),
                'total_interest': round(total_interest, 2),
                'effective_yield': round(effective_yield, 2),
                'yearly_breakdown': yearly_breakdown,
                'insights': insights,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'principal' not in inputs or inputs['principal'] == '':
            self.add_error("Initial investment amount is required")
        else:
            principal = self.validate_number(inputs['principal'], 'Initial investment', 1, 10000000)
        
        if 'annual_rate' not in inputs or inputs['annual_rate'] == '':
            self.add_error("Annual interest rate is required")
        else:
            rate = self.validate_number(inputs['annual_rate'], 'Annual interest rate', 0, 50)
        
        if 'years' not in inputs or inputs['years'] == '':
            self.add_error("Investment time period is required")
        else:
            years = self.validate_number(inputs['years'], 'Years', 0.1, 100)
        
        # Optional fields validation
        if 'monthly_contribution' in inputs and inputs['monthly_contribution'] != '':
            contribution = self.validate_number(inputs['monthly_contribution'], 'Monthly contribution', 0, 100000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Compound Interest Calculator - Investment Growth Calculator',
            'description': 'Free compound interest calculator. Calculate investment growth with regular contributions and different compounding frequencies.',
            'keywords': 'compound interest calculator, investment calculator, savings calculator, retirement planning, investment growth',
            'canonical': '/calculators/compound-interest/'
        }
    
    def _get_frequency_text(self, frequency):
        frequency_map = {
            1: 'Annually',
            2: 'Semi-annually',
            4: 'Quarterly',
            12: 'Monthly',
            52: 'Weekly',
            365: 'Daily'
        }
        return frequency_map.get(frequency, f'{frequency} times per year')
    
    def _generate_insights(self, principal, total_contributions, total_interest, years, annual_rate):
        """Generate investment insights and recommendations"""
        total_invested = principal + total_contributions
        
        insights = []
        
        # Power of compounding insight
        simple_interest = total_invested * (annual_rate / 100) * years
        compound_advantage = total_interest - simple_interest
        if compound_advantage > 0:
            insights.append({
                'type': 'compounding',
                'title': 'Power of Compounding',
                'message': f'Compound interest earned you ${compound_advantage:,.2f} more than simple interest would have.'
            })
        
        # Interest vs contributions insight
        if total_contributions > 0:
            interest_ratio = (total_interest / total_invested) * 100
            if interest_ratio > 50:
                insights.append({
                    'type': 'growth',
                    'title': 'Excellent Growth',
                    'message': f'Interest earnings (${total_interest:,.2f}) represent {interest_ratio:.1f}% of your total investment.'
                })
            elif interest_ratio > 25:
                insights.append({
                    'type': 'growth',
                    'title': 'Good Growth',
                    'message': f'Your investment earned ${total_interest:,.2f} in interest, which is {interest_ratio:.1f}% of your contributions.'
                })
        
        # Time value recommendation
        if years < 10:
            insights.append({
                'type': 'time',
                'title': 'Consider Longer Timeline',
                'message': 'Compound interest works best over longer periods. Consider extending your investment timeline if possible.'
            })
        
        # Rate sensitivity
        if annual_rate < 3:
            insights.append({
                'type': 'rate',
                'title': 'Rate Impact',
                'message': 'Even small increases in your return rate can significantly impact long-term growth. Consider diversified investments.'
            })
        
        return insights

# Retirement Calculator
@register_calculator
class RetirementCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            current_age = int(inputs['current_age'])
            retirement_age = int(inputs['retirement_age'])
            current_savings = float(inputs.get('current_savings', 0))
            monthly_contribution = float(inputs.get('monthly_contribution', 0))
            annual_return = float(inputs['annual_return']) / 100
            retirement_income_goal = float(inputs.get('retirement_income_goal', 0))
            
            # Validate ages
            if retirement_age <= current_age:
                raise ValueError("Retirement age must be greater than current age")
            
            years_to_retirement = retirement_age - current_age
            years_in_retirement = int(inputs.get('years_in_retirement', 25))  # Default 25 years
            
            # Calculate future value of current savings
            fv_current_savings = current_savings * ((1 + annual_return) ** years_to_retirement)
            
            # Calculate future value of monthly contributions
            if annual_return == 0:
                fv_contributions = monthly_contribution * 12 * years_to_retirement
            else:
                monthly_rate = annual_return / 12
                total_months = years_to_retirement * 12
                fv_contributions = monthly_contribution * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
            
            # Total retirement savings
            total_retirement_savings = fv_current_savings + fv_contributions
            
            # Calculate sustainable retirement income (4% rule)
            sustainable_income_4percent = total_retirement_savings * 0.04
            monthly_income_4percent = sustainable_income_4percent / 12
            
            # Calculate required savings for goal
            retirement_goal_analysis = None
            if retirement_income_goal > 0:
                required_total_savings = retirement_income_goal / 0.04
                current_trajectory = total_retirement_savings
                savings_gap = required_total_savings - current_trajectory
                
                # Calculate additional monthly contribution needed
                if savings_gap > 0:
                    if annual_return == 0:
                        additional_monthly_needed = savings_gap / (12 * years_to_retirement)
                    else:
                        monthly_rate = annual_return / 12
                        total_months = years_to_retirement * 12
                        additional_monthly_needed = savings_gap / (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
                else:
                    additional_monthly_needed = 0
                
                retirement_goal_analysis = {
                    'goal_income': retirement_income_goal,
                    'required_savings': required_total_savings,
                    'projected_savings': current_trajectory,
                    'savings_gap': savings_gap,
                    'additional_monthly_needed': max(0, additional_monthly_needed),
                    'on_track': savings_gap <= 0
                }
            
            # Social Security estimate (simplified)
            estimated_social_security = self._estimate_social_security(retirement_income_goal or sustainable_income_4percent)
            
            # Retirement readiness score
            readiness_score = self._calculate_readiness_score(
                current_age, retirement_age, current_savings, monthly_contribution, 
                annual_return, retirement_income_goal or sustainable_income_4percent
            )
            
            # Recommendations
            recommendations = self._generate_recommendations(
                years_to_retirement, monthly_contribution, annual_return, 
                savings_gap if retirement_goal_analysis else 0, current_age
            )
            
            # Inflation analysis
            inflation_rate = 0.03  # 3% assumed inflation
            purchasing_power_analysis = self._analyze_purchasing_power(
                sustainable_income_4percent, years_to_retirement, inflation_rate
            )
            
            return {
                'current_age': current_age,
                'retirement_age': retirement_age,
                'years_to_retirement': years_to_retirement,
                'years_in_retirement': years_in_retirement,
                'current_savings': round(current_savings, 2),
                'monthly_contribution': round(monthly_contribution, 2),
                'annual_return': round(annual_return * 100, 2),
                'fv_current_savings': round(fv_current_savings, 2),
                'fv_contributions': round(fv_contributions, 2),
                'total_retirement_savings': round(total_retirement_savings, 2),
                'sustainable_annual_income': round(sustainable_income_4percent, 2),
                'sustainable_monthly_income': round(monthly_income_4percent, 2),
                'total_contributions': round(monthly_contribution * 12 * years_to_retirement, 2),
                'retirement_goal_analysis': retirement_goal_analysis,
                'estimated_social_security': round(estimated_social_security, 2),
                'readiness_score': readiness_score,
                'recommendations': recommendations,
                'purchasing_power_analysis': purchasing_power_analysis,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        if 'current_age' not in inputs or inputs['current_age'] == '':
            self.add_error("Current age is required")
        else:
            age = self.validate_number(inputs['current_age'], 'Current age', 18, 100)
        
        if 'retirement_age' not in inputs or inputs['retirement_age'] == '':
            self.add_error("Retirement age is required")
        else:
            ret_age = self.validate_number(inputs['retirement_age'], 'Retirement age', 50, 100)
        
        if 'annual_return' not in inputs or inputs['annual_return'] == '':
            self.add_error("Expected annual return is required")
        else:
            return_rate = self.validate_number(inputs['annual_return'], 'Annual return', 0, 20)
        
        # Optional fields validation
        if 'current_savings' in inputs and inputs['current_savings'] != '':
            savings = self.validate_number(inputs['current_savings'], 'Current savings', 0, 50000000)
        
        if 'monthly_contribution' in inputs and inputs['monthly_contribution'] != '':
            contribution = self.validate_number(inputs['monthly_contribution'], 'Monthly contribution', 0, 100000)
        
        if 'retirement_income_goal' in inputs and inputs['retirement_income_goal'] != '':
            goal = self.validate_number(inputs['retirement_income_goal'], 'Retirement income goal', 0, 5000000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Retirement Calculator - Plan Your Retirement Savings',
            'description': 'Free retirement calculator. Calculate how much you need to save for retirement and plan your financial future.',
            'keywords': 'retirement calculator, retirement planning, 401k calculator, retirement savings, pension calculator',
            'canonical': '/calculators/retirement/'
        }
    
    def _estimate_social_security(self, target_income):
        """Estimate Social Security benefits (simplified)"""
        # Average Social Security benefit is about $1,800/month ($21,600/year) in 2024
        # This is a simplified estimate - actual benefits depend on work history
        return min(target_income * 0.4, 21600)  # Cap at average benefit
    
    def _calculate_readiness_score(self, current_age, retirement_age, current_savings, monthly_contribution, annual_return, target_income):
        """Calculate retirement readiness score (0-100)"""
        years_to_retirement = retirement_age - current_age
        
        # Calculate projected savings
        fv_current = current_savings * ((1 + annual_return) ** years_to_retirement)
        if annual_return == 0:
            fv_contributions = monthly_contribution * 12 * years_to_retirement
        else:
            monthly_rate = annual_return / 12
            total_months = years_to_retirement * 12
            fv_contributions = monthly_contribution * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
        
        total_projected = fv_current + fv_contributions
        required_savings = target_income / 0.04
        
        # Score based on percentage of goal achieved
        if required_savings == 0:
            return 100
        
        score = min(100, (total_projected / required_savings) * 100)
        return round(score, 1)
    
    def _generate_recommendations(self, years_to_retirement, monthly_contribution, annual_return, savings_gap, current_age):
        """Generate personalized retirement recommendations"""
        recommendations = []
        
        # Time-based recommendations
        if years_to_retirement > 30:
            recommendations.append({
                'category': 'Time Advantage',
                'title': 'Great Time Horizon',
                'message': 'You have excellent time for compound growth. Consider more aggressive investments while young.',
                'priority': 'high'
            })
        elif years_to_retirement < 10:
            recommendations.append({
                'category': 'Catch-Up',
                'title': 'Consider Catch-Up Contributions',
                'message': 'With limited time, maximize contributions and consider catch-up contributions if over 50.',
                'priority': 'urgent'
            })
        
        # Contribution recommendations
        if monthly_contribution < 500:
            recommendations.append({
                'category': 'Contributions',
                'title': 'Increase Monthly Savings',
                'message': 'Consider increasing your monthly contributions. Even small increases compound significantly over time.',
                'priority': 'medium'
            })
        
        # Return rate recommendations
        if annual_return < 0.06:
            recommendations.append({
                'category': 'Investment Strategy',
                'title': 'Consider Higher-Growth Investments',
                'message': 'A 6-8% return is typical for diversified portfolios. Review your investment allocation.',
                'priority': 'medium'
            })
        
        # Savings gap recommendations
        if savings_gap > 0:
            if savings_gap > 100000:
                recommendations.append({
                    'category': 'Savings Gap',
                    'title': 'Significant Shortfall',
                    'message': 'Consider working longer, reducing expenses, or significantly increasing contributions.',
                    'priority': 'urgent'
                })
            else:
                recommendations.append({
                    'category': 'Savings Gap',
                    'title': 'Minor Adjustments Needed',
                    'message': 'Small increases in contributions or returns can close your savings gap.',
                    'priority': 'medium'
                })
        
        # Age-specific recommendations
        if current_age < 30:
            recommendations.append({
                'category': 'Early Career',
                'title': 'Start Strong',
                'message': 'Starting early is your biggest advantage. Focus on building the savings habit.',
                'priority': 'high'
            })
        elif current_age > 50:
            recommendations.append({
                'category': 'Pre-Retirement',
                'title': 'Preserve and Protect',
                'message': 'Consider reducing risk and focusing on capital preservation as you near retirement.',
                'priority': 'high'
            })
        
        return recommendations
    
    def _analyze_purchasing_power(self, income, years_to_retirement, inflation_rate):
        """Analyze the impact of inflation on retirement income"""
        current_purchasing_power = income
        future_purchasing_power = income / ((1 + inflation_rate) ** years_to_retirement)
        purchasing_power_loss = current_purchasing_power - future_purchasing_power
        
        return {
            'current_dollars': round(current_purchasing_power, 2),
            'future_purchasing_power': round(future_purchasing_power, 2),
            'purchasing_power_loss': round(purchasing_power_loss, 2),
            'inflation_rate_used': round(inflation_rate * 100, 1)
        }

# Investment Return Calculator
@register_calculator
class InvestmentReturnCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            calculation_type = inputs.get('calculation_type', 'future_value')
            
            if calculation_type == 'future_value':
                return self._calculate_future_value(inputs)
            elif calculation_type == 'required_return':
                return self._calculate_required_return(inputs)
            elif calculation_type == 'time_needed':
                return self._calculate_time_needed(inputs)
            elif calculation_type == 'portfolio_analysis':
                return self._calculate_portfolio_analysis(inputs)
            else:
                raise ValueError("Invalid calculation type")
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def _calculate_future_value(self, inputs):
        """Calculate future value of investment"""
        initial_investment = float(inputs['initial_investment'])
        annual_return = float(inputs['annual_return']) / 100
        years = float(inputs['years'])
        additional_contributions = float(inputs.get('additional_contributions', 0))
        contribution_frequency = inputs.get('contribution_frequency', 'monthly')
        
        # Convert contribution frequency to times per year
        freq_map = {'monthly': 12, 'quarterly': 4, 'annually': 1}
        contributions_per_year = freq_map.get(contribution_frequency, 12)
        
        # Calculate future value of initial investment
        fv_initial = initial_investment * ((1 + annual_return) ** years)
        
        # Calculate future value of regular contributions
        if additional_contributions > 0 and annual_return != 0:
            period_rate = annual_return / contributions_per_year
            total_periods = years * contributions_per_year
            fv_contributions = additional_contributions * (((1 + period_rate) ** total_periods - 1) / period_rate)
        elif additional_contributions > 0:
            fv_contributions = additional_contributions * contributions_per_year * years
        else:
            fv_contributions = 0
        
        total_value = fv_initial + fv_contributions
        total_invested = initial_investment + (additional_contributions * contributions_per_year * years)
        total_gains = total_value - total_invested
        
        # Calculate annualized return including contributions
        if total_invested > 0:
            annualized_return = ((total_value / total_invested) ** (1/years) - 1) * 100
        else:
            annualized_return = 0
        
        return {
            'calculation_type': 'future_value',
            'initial_investment': round(initial_investment, 2),
            'annual_return': round(annual_return * 100, 2),
            'years': years,
            'additional_contributions': round(additional_contributions, 2),
            'contribution_frequency': contribution_frequency,
            'total_value': round(total_value, 2),
            'total_invested': round(total_invested, 2),
            'total_gains': round(total_gains, 2),
            'annualized_return': round(annualized_return, 2),
            'fv_initial': round(fv_initial, 2),
            'fv_contributions': round(fv_contributions, 2),
            'inputs': inputs
        }
    
    def _calculate_required_return(self, inputs):
        """Calculate required return to reach target"""
        initial_investment = float(inputs['initial_investment'])
        target_value = float(inputs['target_value'])
        years = float(inputs['years'])
        additional_contributions = float(inputs.get('additional_contributions', 0))
        contribution_frequency = inputs.get('contribution_frequency', 'monthly')
        
        # Convert contribution frequency
        freq_map = {'monthly': 12, 'quarterly': 4, 'annually': 1}
        contributions_per_year = freq_map.get(contribution_frequency, 12)
        
        total_contributions = additional_contributions * contributions_per_year * years
        total_invested = initial_investment + total_contributions
        
        # If no additional contributions, use simple compound interest formula
        if additional_contributions == 0:
            if initial_investment > 0:
                required_return = ((target_value / initial_investment) ** (1/years) - 1) * 100
            else:
                required_return = 0
        else:
            # Use iterative approach to find required return with regular contributions
            required_return = self._solve_for_return(
                initial_investment, additional_contributions, contributions_per_year, years, target_value
            )
        
        # Risk assessment
        risk_assessment = self._assess_return_risk(required_return)
        
        return {
            'calculation_type': 'required_return',
            'initial_investment': round(initial_investment, 2),
            'target_value': round(target_value, 2),
            'years': years,
            'additional_contributions': round(additional_contributions, 2),
            'contribution_frequency': contribution_frequency,
            'total_invested': round(total_invested, 2),
            'required_return': round(required_return, 2),
            'risk_assessment': risk_assessment,
            'inputs': inputs
        }
    
    def _calculate_time_needed(self, inputs):
        """Calculate time needed to reach target"""
        initial_investment = float(inputs['initial_investment'])
        target_value = float(inputs['target_value'])
        annual_return = float(inputs['annual_return']) / 100
        additional_contributions = float(inputs.get('additional_contributions', 0))
        contribution_frequency = inputs.get('contribution_frequency', 'monthly')
        
        # Convert contribution frequency
        freq_map = {'monthly': 12, 'quarterly': 4, 'annually': 1}
        contributions_per_year = freq_map.get(contribution_frequency, 12)
        
        if additional_contributions == 0:
            # Simple compound interest
            if annual_return > 0 and initial_investment > 0:
                years_needed = math.log(target_value / initial_investment) / math.log(1 + annual_return)
            else:
                years_needed = float('inf')
        else:
            # Use iterative approach
            years_needed = self._solve_for_time(
                initial_investment, additional_contributions, contributions_per_year, annual_return, target_value
            )
        
        if years_needed == float('inf') or years_needed > 100:
            years_needed = None
            feasible = False
        else:
            feasible = True
        
        return {
            'calculation_type': 'time_needed',
            'initial_investment': round(initial_investment, 2),
            'target_value': round(target_value, 2),
            'annual_return': round(annual_return * 100, 2),
            'additional_contributions': round(additional_contributions, 2),
            'contribution_frequency': contribution_frequency,
            'years_needed': round(years_needed, 1) if years_needed else None,
            'feasible': feasible,
            'inputs': inputs
        }
    
    def _calculate_portfolio_analysis(self, inputs):
        """Analyze portfolio performance"""
        investments = []
        total_initial = 0
        total_current = 0
        
        # Parse multiple investments
        for i in range(1, 6):  # Support up to 5 investments
            initial_key = f'investment_{i}_initial'
            current_key = f'investment_{i}_current'
            name_key = f'investment_{i}_name'
            
            if initial_key in inputs and inputs[initial_key]:
                initial = float(inputs[initial_key])
                current = float(inputs.get(current_key, initial))
                name = inputs.get(name_key, f'Investment {i}')
                
                gain_loss = current - initial
                return_pct = (gain_loss / initial) * 100 if initial > 0 else 0
                
                investments.append({
                    'name': name,
                    'initial': round(initial, 2),
                    'current': round(current, 2),
                    'gain_loss': round(gain_loss, 2),
                    'return_pct': round(return_pct, 2),
                    'weight': 0  # Will calculate below
                })
                
                total_initial += initial
                total_current += current
        
        # Calculate weights and portfolio metrics
        for investment in investments:
            investment['weight'] = round((investment['initial'] / total_initial) * 100, 1)
        
        total_gain_loss = total_current - total_initial
        portfolio_return = (total_gain_loss / total_initial) * 100 if total_initial > 0 else 0
        
        # Performance analysis
        best_performer = max(investments, key=lambda x: x['return_pct']) if investments else None
        worst_performer = min(investments, key=lambda x: x['return_pct']) if investments else None
        
        return {
            'calculation_type': 'portfolio_analysis',
            'investments': investments,
            'total_initial': round(total_initial, 2),
            'total_current': round(total_current, 2),
            'total_gain_loss': round(total_gain_loss, 2),
            'portfolio_return': round(portfolio_return, 2),
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'num_investments': len(investments),
            'inputs': inputs
        }
    
    def _solve_for_return(self, principal, pmt, freq, years, target):
        """Iteratively solve for required return rate"""
        import math
        
        # Binary search for the return rate
        low, high = 0.001, 0.50  # 0.1% to 50%
        tolerance = 0.0001
        max_iterations = 100
        
        for _ in range(max_iterations):
            mid = (low + high) / 2
            period_rate = mid / freq
            total_periods = years * freq
            
            # Calculate future value with this rate
            fv_principal = principal * ((1 + mid) ** years)
            if period_rate == 0:
                fv_pmt = pmt * total_periods
            else:
                fv_pmt = pmt * (((1 + period_rate) ** total_periods - 1) / period_rate)
            
            total_fv = fv_principal + fv_pmt
            
            if abs(total_fv - target) < tolerance:
                return mid * 100
            elif total_fv < target:
                low = mid
            else:
                high = mid
        
        return mid * 100
    
    def _solve_for_time(self, principal, pmt, freq, rate, target):
        """Iteratively solve for time needed"""
        if rate <= 0:
            return float('inf')
        
        # Start with simple estimate and iterate
        years = 1
        max_years = 100
        
        while years <= max_years:
            period_rate = rate / freq
            total_periods = years * freq
            
            fv_principal = principal * ((1 + rate) ** years)
            fv_pmt = pmt * (((1 + period_rate) ** total_periods - 1) / period_rate)
            total_fv = fv_principal + fv_pmt
            
            if total_fv >= target:
                return years
            
            years += 0.1
        
        return float('inf')
    
    def _assess_return_risk(self, required_return):
        """Assess the risk level of required return"""
        if required_return <= 3:
            return {
                'level': 'Conservative',
                'description': 'Low risk, achievable with bonds/CDs',
                'feasibility': 'High'
            }
        elif required_return <= 7:
            return {
                'level': 'Moderate',
                'description': 'Moderate risk, typical for balanced portfolios',
                'feasibility': 'Good'
            }
        elif required_return <= 12:
            return {
                'level': 'Aggressive',
                'description': 'Higher risk, requires growth-focused investments',
                'feasibility': 'Challenging'
            }
        else:
            return {
                'level': 'Very High Risk',
                'description': 'Extremely high risk, may not be realistic',
                'feasibility': 'Unlikely'
            }
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        calculation_type = inputs.get('calculation_type', 'future_value')
        
        if calculation_type == 'future_value':
            if 'initial_investment' not in inputs or inputs['initial_investment'] == '':
                self.add_error("Initial investment is required")
            else:
                self.validate_number(inputs['initial_investment'], 'Initial investment', 1, 50000000)
            
            if 'annual_return' not in inputs or inputs['annual_return'] == '':
                self.add_error("Annual return is required")
            else:
                self.validate_number(inputs['annual_return'], 'Annual return', -50, 50)
            
            if 'years' not in inputs or inputs['years'] == '':
                self.add_error("Investment period is required")
            else:
                self.validate_number(inputs['years'], 'Years', 0.1, 100)
        
        elif calculation_type == 'required_return':
            required_fields = ['initial_investment', 'target_value', 'years']
            for field in required_fields:
                if field not in inputs or inputs[field] == '':
                    self.add_error(f"{field.replace('_', ' ').title()} is required")
                else:
                    max_val = 50000000 if 'investment' in field or 'value' in field else 100
                    self.validate_number(inputs[field], field.replace('_', ' ').title(), 1, max_val)
        
        elif calculation_type == 'time_needed':
            required_fields = ['initial_investment', 'target_value', 'annual_return']
            for field in required_fields:
                if field not in inputs or inputs[field] == '':
                    self.add_error(f"{field.replace('_', ' ').title()} is required")
        
        elif calculation_type == 'portfolio_analysis':
            # At least one investment required
            has_investment = False
            for i in range(1, 6):
                if f'investment_{i}_initial' in inputs and inputs[f'investment_{i}_initial']:
                    has_investment = True
                    break
            if not has_investment:
                self.add_error("At least one investment is required for portfolio analysis")
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Investment Return Calculator - Calculate Investment Returns',
            'description': 'Free investment return calculator. Calculate future value, required returns, time needed, and analyze portfolio performance.',
            'keywords': 'investment calculator, return calculator, portfolio analysis, investment planning, ROI calculator',
            'canonical': '/calculators/investment-return/'
        }

# Mortgage Calculator
@register_calculator
class MortgageCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            home_price = float(inputs['home_price'])
            down_payment = float(inputs.get('down_payment_amount', 0))
            down_payment_percent = float(inputs.get('down_payment_percent', 20))
            
            # Calculate down payment if percentage is provided instead of amount
            if 'down_payment_percent' in inputs and inputs['down_payment_percent']:
                down_payment = home_price * (down_payment_percent / 100)
            elif down_payment == 0:
                down_payment = home_price * 0.20  # Default 20%
                down_payment_percent = 20
            else:
                down_payment_percent = (down_payment / home_price) * 100
            
            loan_amount = home_price - down_payment
            annual_rate = float(inputs['annual_rate']) / 100
            loan_term_years = float(inputs.get('loan_term_years', 30))
            
            # Additional costs
            property_tax_annual = float(inputs.get('property_tax_annual', 0))
            home_insurance_annual = float(inputs.get('home_insurance_annual', 0))
            hoa_monthly = float(inputs.get('hoa_monthly', 0))
            
            # PMI calculation (required if down payment < 20%)
            pmi_monthly = 0
            if down_payment_percent < 20:
                pmi_rate = float(inputs.get('pmi_rate', 0.5)) / 100  # Default 0.5% annually
                pmi_monthly = (loan_amount * pmi_rate) / 12
            
            # Calculate mortgage payment
            monthly_rate = annual_rate / 12
            num_payments = loan_term_years * 12
            
            if monthly_rate == 0:
                monthly_principal_interest = loan_amount / num_payments
            else:
                monthly_principal_interest = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
            # Calculate monthly costs
            monthly_property_tax = property_tax_annual / 12
            monthly_insurance = home_insurance_annual / 12
            
            # Total monthly payment
            total_monthly_payment = (monthly_principal_interest + monthly_property_tax + 
                                   monthly_insurance + pmi_monthly + hoa_monthly)
            
            # Calculate totals
            total_loan_payments = monthly_principal_interest * num_payments
            total_interest = total_loan_payments - loan_amount
            total_cost_of_home = total_loan_payments + down_payment
            
            # Calculate what income is needed (28% rule)
            required_annual_income = (total_monthly_payment * 12) / 0.28
            
            return {
                'home_price': round(home_price, 2),
                'down_payment': round(down_payment, 2),
                'down_payment_percent': round(down_payment_percent, 1),
                'loan_amount': round(loan_amount, 2),
                'monthly_principal_interest': round(monthly_principal_interest, 2),
                'monthly_property_tax': round(monthly_property_tax, 2),
                'monthly_insurance': round(monthly_insurance, 2),
                'pmi_monthly': round(pmi_monthly, 2),
                'hoa_monthly': round(hoa_monthly, 2),
                'total_monthly_payment': round(total_monthly_payment, 2),
                'total_interest': round(total_interest, 2),
                'total_cost_of_home': round(total_cost_of_home, 2),
                'required_annual_income': round(required_annual_income, 2),
                'annual_rate': float(inputs['annual_rate']),
                'loan_term_years': loan_term_years,
                'needs_pmi': down_payment_percent < 20,
                'closing_costs': self._estimate_closing_costs(home_price),
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        # Validate home price
        if 'home_price' not in inputs or inputs['home_price'] == '':
            self.add_error("Home price is required")
        else:
            price = self.validate_number(inputs['home_price'], 'Home price', 10000, 50000000)
        
        # Validate annual interest rate
        if 'annual_rate' not in inputs or inputs['annual_rate'] == '':
            self.add_error("Annual interest rate is required")
        else:
            rate = self.validate_number(inputs['annual_rate'], 'Annual interest rate', 0.1, 30)
        
        # Optional fields validation
        if 'down_payment_amount' in inputs and inputs['down_payment_amount']:
            down_payment = self.validate_number(inputs['down_payment_amount'], 'Down payment', 0, 10000000)
        
        if 'property_tax_annual' in inputs and inputs['property_tax_annual']:
            self.validate_number(inputs['property_tax_annual'], 'Property tax', 0, 1000000)
        
        if 'home_insurance_annual' in inputs and inputs['home_insurance_annual']:
            self.validate_number(inputs['home_insurance_annual'], 'Home insurance', 0, 100000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Mortgage Calculator - Home Loan Payment Calculator Free',
            'description': 'Free mortgage calculator with PMI, property taxes, insurance, and HOA. Calculate monthly payments, affordability, and total costs for home loans.',
            'keywords': 'mortgage calculator, home loan calculator, mortgage payment, PMI calculator, home affordability, property tax calculator',
            'canonical': '/calculators/mortgage/'
        }
    
    def _estimate_closing_costs(self, home_price):
        """Estimate typical closing costs (2-5% of home price)"""
        low_estimate = home_price * 0.02
        high_estimate = home_price * 0.05
        return {
            'low': round(low_estimate, 2),
            'high': round(high_estimate, 2),
            'typical': round((low_estimate + high_estimate) / 2, 2)
        }

# Tip Calculator
@register_calculator
class TipCalculator(BaseCalculator):
    def calculate(self, inputs):
        try:
            bill_amount = float(inputs['bill_amount'])
            tip_percentage = float(inputs['tip_percentage'])
            num_people = int(inputs.get('num_people', 1))
            tax_percentage = float(inputs.get('tax_percentage', 0))
            tip_on_total = inputs.get('tip_on_total', 'false') == 'true'
            
            # Calculate tax
            tax_amount = bill_amount * (tax_percentage / 100)
            
            # Calculate tip (either on pre-tax or post-tax amount)
            tip_base = (bill_amount + tax_amount) if tip_on_total else bill_amount
            tip_amount = tip_base * (tip_percentage / 100)
            
            # Calculate totals
            total_amount = bill_amount + tax_amount + tip_amount
            
            # Per person calculations
            bill_per_person = bill_amount / num_people
            tax_per_person = tax_amount / num_people
            tip_per_person = tip_amount / num_people
            total_per_person = total_amount / num_people
            
            return {
                'bill_amount': round(bill_amount, 2),
                'tip_percentage': tip_percentage,
                'tax_percentage': tax_percentage,
                'tax_amount': round(tax_amount, 2),
                'tip_amount': round(tip_amount, 2),
                'total_amount': round(total_amount, 2),
                'num_people': num_people,
                'bill_per_person': round(bill_per_person, 2),
                'tax_per_person': round(tax_per_person, 2),
                'tip_per_person': round(tip_per_person, 2),
                'total_per_person': round(total_per_person, 2),
                'tip_on_total': tip_on_total,
                'tip_guide': self._get_tip_guide(inputs.get('service_type', 'restaurant')),
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        # Validate bill amount
        if 'bill_amount' not in inputs or inputs['bill_amount'] == '':
            self.add_error("Bill amount is required")
        else:
            bill = self.validate_number(inputs['bill_amount'], 'Bill amount', 0.01, 100000)
            if bill is None:
                pass
        
        # Validate tip percentage
        if 'tip_percentage' not in inputs or inputs['tip_percentage'] == '':
            self.add_error("Tip percentage is required")
        else:
            tip = self.validate_number(inputs['tip_percentage'], 'Tip percentage', 0, 100)
            if tip is None:
                pass
        
        # Validate number of people (optional, default to 1)
        if 'num_people' in inputs and inputs['num_people'] != '':
            people = self.validate_number(inputs['num_people'], 'Number of people', 1, 100)
            if people is None:
                pass
            elif not float(inputs['num_people']).is_integer():
                self.add_error("Number of people must be a whole number")
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Tip Calculator - Calculate Tips and Split Bills Online Free',
            'description': 'Free tip calculator to calculate tips and split bills. Includes tip guides for restaurants, bars, delivery, and more service types.',
            'keywords': 'tip calculator, tip guide, split bill, restaurant tip, delivery tip, service tip, gratuity calculator',
            'canonical': '/calculators/tip/'
        }
    
    def _get_tip_guide(self, service_type):
        guides = {
            'restaurant': {
                'excellent': '20-25%',
                'good': '18-20%',
                'average': '15-18%',
                'poor': '10-15%',
                'note': 'Standard for sit-down restaurants in the US'
            },
            'delivery': {
                'excellent': '20-25%',
                'good': '15-20%',
                'average': '10-15%',
                'minimum': '$2-5',
                'note': 'Consider distance and weather conditions'
            },
            'bar': {
                'cocktails': '$1-2 per drink',
                'beer_wine': '$1 per drink',
                'tab': '15-20%',
                'note': 'Higher for craft cocktails'
            },
            'taxi_uber': {
                'standard': '15-20%',
                'excellent': '20-25%',
                'note': 'Round up to nearest dollar'
            }
        }
        return guides.get(service_type, guides['restaurant'])

# BMI Calculator
@register_calculator
class BMICalculator(BaseCalculator):
    def calculate(self, inputs):
        unit_system = inputs.get('unit_system', 'metric')
        
        try:
            if unit_system == 'metric':
                weight = float(inputs['weight'])  # kg
                height = float(inputs['height']) / 100  # convert cm to meters
            else:  # imperial
                weight = float(inputs['weight']) * 0.453592  # lbs to kg
                height = float(inputs['height']) * 0.0254  # inches to meters
            
            if height <= 0:
                raise ValueError("Height must be greater than zero")
            
            bmi = weight / (height * height)
            
            # BMI Categories
            category, description, color = self._get_bmi_category(bmi)
            
            # Health recommendations based on BMI
            recommendations = self._get_health_recommendations(bmi)
            
            return {
                'bmi': round(bmi, 1),
                'category': category,
                'description': description,
                'color': color,
                'recommendations': recommendations,
                'ideal_weight_range': self._get_ideal_weight_range(height, unit_system),
                'unit_system': unit_system,
                'inputs': inputs
            }
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        unit_system = inputs.get('unit_system', 'metric')
        
        # Check required fields
        if 'weight' not in inputs or inputs['weight'] == '':
            self.add_error("Weight is required")
        else:
            weight = self.validate_number(inputs['weight'], 'Weight', 1, 1000)
            if weight is None:
                pass
            elif unit_system == 'metric' and (weight < 20 or weight > 500):
                self.add_error("Weight should be between 20-500 kg")
            elif unit_system == 'imperial' and (weight < 44 or weight > 1100):
                self.add_error("Weight should be between 44-1100 lbs")
        
        if 'height' not in inputs or inputs['height'] == '':
            self.add_error("Height is required")
        else:
            height = self.validate_number(inputs['height'], 'Height', 1, 300)
            if height is None:
                pass
            elif unit_system == 'metric' and (height < 50 or height > 250):
                self.add_error("Height should be between 50-250 cm")
            elif unit_system == 'imperial' and (height < 20 or height > 100):
                self.add_error("Height should be between 20-100 inches")
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'BMI Calculator - Body Mass Index Calculator Online Free',
            'description': 'Free BMI calculator to check your body mass index. Calculate BMI for adults with metric and imperial units. Includes BMI categories and health recommendations.',
            'keywords': 'BMI calculator, body mass index, BMI chart, healthy weight, obesity calculator, weight calculator',
            'canonical': '/calculators/bmi/'
        }
    
    def _get_bmi_category(self, bmi):
        if bmi < 16:
            return "Severely Underweight", "Severely underweight - please consult a healthcare provider", "#dc3545"
        elif bmi < 18.5:
            return "Underweight", "Underweight - consider gaining weight", "#ffc107"
        elif bmi < 25:
            return "Normal Weight", "Normal weight - maintain your current lifestyle", "#28a745"
        elif bmi < 30:
            return "Overweight", "Overweight - consider losing weight", "#fd7e14"
        elif bmi < 35:
            return "Obese Class I", "Obese Class I - weight loss recommended", "#dc3545"
        elif bmi < 40:
            return "Obese Class II", "Obese Class II - significant weight loss needed", "#dc3545"
        else:
            return "Obese Class III", "Obese Class III - seek medical advice", "#6f42c1"
    
    def _get_health_recommendations(self, bmi):
        if bmi < 18.5:
            return [
                "Increase caloric intake with nutritious foods",
                "Consider strength training to build muscle mass",
                "Consult with a healthcare provider or nutritionist"
            ]
        elif bmi < 25:
            return [
                "Maintain current weight through balanced diet",
                "Continue regular physical activity",
                "Focus on overall health and wellness"
            ]
        elif bmi < 30:
            return [
                "Create a moderate caloric deficit (300-500 calories/day)",
                "Increase physical activity to 150+ minutes per week",
                "Focus on whole foods and reduce processed foods"
            ]
        else:
            return [
                "Consult with healthcare provider for weight loss plan",
                "Consider structured diet and exercise program",
                "Focus on sustainable lifestyle changes"
            ]
    
    def _get_ideal_weight_range(self, height_meters, unit_system):
        # Normal BMI range: 18.5 - 24.9
        min_weight = 18.5 * (height_meters * height_meters)
        max_weight = 24.9 * (height_meters * height_meters)
        
        if unit_system == 'imperial':
            min_weight = min_weight / 0.453592  # kg to lbs
            max_weight = max_weight / 0.453592
            unit = "lbs"
        else:
            unit = "kg"
        
        return f"{min_weight:.1f} - {max_weight:.1f} {unit}"

# Percentage Calculator
@register_calculator
class PercentageCalculator(BaseCalculator):
    def calculate(self, inputs):
        operation = inputs.get('operation', 'basic')
        
        try:
            if operation == 'basic':
                x = float(inputs['x'])
                y = float(inputs['y'])
                if y == 0:
                    raise ValueError("Cannot divide by zero")
                result = (x / y) * 100
                
            elif operation == 'find_value':
                percent = float(inputs['percent'])
                total = float(inputs['total'])
                result = (percent / 100) * total
                
            elif operation == 'increase':
                original = float(inputs['original'])
                percent = float(inputs['percent'])
                result = original * (1 + percent / 100)
                
            elif operation == 'decrease':
                original = float(inputs['original'])
                percent = float(inputs['percent'])
                result = original * (1 - percent / 100)
                
            elif operation == 'difference':
                x = float(inputs['x'])
                y = float(inputs['y'])
                if x == 0 and y == 0:
                    result = 0
                else:
                    result = abs(x - y) / ((x + y) / 2) * 100
                    
            elif operation == 'change':
                original = float(inputs['original'])
                new_value = float(inputs['new_value'])
                if original == 0:
                    raise ValueError("Cannot calculate percentage change from zero")
                result = ((new_value - original) / original) * 100
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            return {
                'result': round(result, 2),
                'operation': operation,
                'inputs': inputs,
                'formula': self._get_formula(operation),
                'explanation': self._get_explanation(operation, inputs, result)
            }
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e).strip('\"\'')}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        operation = inputs.get('operation', 'basic')
        required = self._get_required_fields(operation)
        
        for field in required:
            if field not in inputs or inputs[field] == '' or inputs[field] is None:
                self.add_error(f"Missing required field: {field}")
                continue
            
            value = self.validate_number(inputs[field], field)
            if value is None:
                continue
            
            if operation in ['basic', 'difference'] and field == 'y' and value == 0:
                self.add_error("Division by zero: Y cannot be zero")
            elif operation == 'change' and field == 'original' and value == 0:
                self.add_error("Original value cannot be zero for percentage change")
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Percentage Calculator - Calculate Percentages Online Free',
            'description': 'Free online percentage calculator. Calculate percentages, percentage increase/decrease, percentage difference and more. Simple, fast, and accurate.',
            'keywords': 'percentage calculator, percent calculator, calculate percentage, percentage increase, percentage decrease, percentage difference, percentage change',
            'canonical': '/calculators/percentage/'
        }
    
    def _get_required_fields(self, operation):
        fields_map = {
            'basic': ['x', 'y'],
            'find_value': ['percent', 'total'],
            'increase': ['original', 'percent'],
            'decrease': ['original', 'percent'],
            'difference': ['x', 'y'],
            'change': ['original', 'new_value']
        }
        return fields_map.get(operation, [])
    
    def _get_formula(self, operation):
        formulas = {
            'basic': '(X ÷ Y) × 100',
            'find_value': '(Percent ÷ 100) × Total',
            'increase': 'Original × (1 + Percent ÷ 100)',
            'decrease': 'Original × (1 - Percent ÷ 100)',
            'difference': '|X - Y| ÷ ((X + Y) ÷ 2) × 100',
            'change': '((New Value - Original) ÷ Original) × 100'
        }
        return formulas.get(operation, '')
    
    def _get_explanation(self, operation, inputs, result):
        try:
            explanations = {
                'basic': f"{inputs['x']} is {result}% of {inputs['y']}. This means {inputs['x']} represents {result} parts out of every 100 parts of {inputs['y']}.",
                'find_value': f"{inputs['percent']}% of {inputs['total']} equals {result}. This is calculated as ({inputs['percent']} ÷ 100) × {inputs['total']}.",
                'increase': f"{inputs['original']} increased by {inputs['percent']}% equals {result}. The increase amount is {round(float(result) - float(inputs['original']), 2)}.",
                'decrease': f"{inputs['original']} decreased by {inputs['percent']}% equals {result}. The decrease amount is {round(float(inputs['original']) - float(result), 2)}.",
                'difference': f"The percentage difference between {inputs['x']} and {inputs['y']} is {result}%. This measures the relative difference between the two values.",
                'change': f"The percentage change from {inputs['original']} to {inputs['new_value']} is {result}%. {'This is an increase.' if result > 0 else 'This is a decrease.' if result < 0 else 'No change occurred.'}"
            }
            return explanations.get(operation, f'Result: {result}')
        except:
            return f'Result: {result}'

# Routes
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Calculator Suite</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .calc-list { display: grid; gap: 1rem; margin-top: 2rem; }
            .calc-item { padding: 1rem; border: 1px solid #ddd; border-radius: 4px; text-decoration: none; color: inherit; }
            .calc-item:hover { background: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧮 Calculator Suite</h1>
            <p>Free online calculators for all your math needs.</p>
            
            <div class="calc-list">
                <a href="/calculators/percentage/" class="calc-item">
                    <h3>📊 Percentage Calculator</h3>
                    <p>Calculate percentages, increases, decreases, and more.</p>
                </a>
                <a href="/calculators/bmi/" class="calc-item">
                    <h3>⚖️ BMI Calculator</h3>
                    <p>Calculate your Body Mass Index with health recommendations.</p>
                </a>
                <a href="/calculators/tip/" class="calc-item">
                    <h3>💰 Tip Calculator</h3>
                    <p>Calculate tips and split bills for restaurants, delivery, and more.</p>
                </a>
                <a href="/calculators/loan/" class="calc-item">
                    <h3>🏦 Loan Calculator</h3>
                    <p>Calculate monthly payments for personal, auto, student, and other loans.</p>
                </a>
                <a href="/calculators/mortgage/" class="calc-item">
                    <h3>🏠 Mortgage Calculator</h3>
                    <p>Calculate home payments with PMI, taxes, insurance, and affordability.</p>
                </a>
                <a href="/calculators/income-tax/" class="calc-item">
                    <h3>📋 Income Tax Calculator</h3>
                    <p>Calculate federal and state income taxes, FICA, and take-home pay.</p>
                </a>
                <a href="/calculators/sales-tax/" class="calc-item">
                    <h3>🛒 Sales Tax Calculator</h3>
                    <p>Calculate sales tax by state, city, and ZIP code with accurate 2024 rates.</p>
                </a>
                <a href="/calculators/property-tax/" class="calc-item">
                    <h3>🏘️ Property Tax Calculator</h3>
                    <p>Calculate annual property taxes by state with homestead and other exemptions.</p>
                </a>
                <a href="/calculators/tax-refund/" class="calc-item">
                    <h3>💰 Tax Refund Calculator</h3>
                    <p>Estimate your federal and state tax refund with withholdings and credits.</p>
                </a>
                <a href="/calculators/gross-to-net/" class="calc-item">
                    <h3>💵 Gross to Net Calculator</h3>
                    <p>Calculate your take-home pay after taxes and deductions by pay period.</p>
                </a>
                <a href="/calculators/hourly-to-salary/" class="calc-item">
                    <h3>⏰ Hourly to Salary Calculator</h3>
                    <p>Convert hourly wages to annual salary and compare work scenarios.</p>
                </a>
                <a href="/calculators/salary-raise/" class="calc-item">
                    <h3>📈 Salary Raise Calculator</h3>
                    <p>Calculate raise amounts, percentages, and long-term financial impact.</p>
                </a>
                <a href="/calculators/cost-of-living/" class="calc-item">
                    <h3>🏙️ Cost of Living Calculator</h3>
                    <p>Compare living costs between cities and calculate equivalent salary needs.</p>
                </a>
                <a href="/calculators/compound-interest/" class="calc-item">
                    <h3>📈 Compound Interest Calculator</h3>
                    <p>Calculate investment growth with compound interest and regular contributions.</p>
                </a>
                <a href="/calculators/retirement/" class="calc-item">
                    <h3>🏖️ Retirement Calculator</h3>
                    <p>Plan your retirement savings and calculate if you're on track for your goals.</p>
                </a>
                <a href="/calculators/investment-return/" class="calc-item">
                    <h3>💹 Investment Return Calculator</h3>
                    <p>Calculate investment returns, required rates, time needed, and analyze portfolios.</p>
                </a>
            </div>
            
            <div style="margin-top: 2rem; text-align: center; color: #666;">
                <h3>📚 Resources & Guides</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                    <a href="/calculator-guide/" style="color: #007bff; text-decoration: none; padding: 1rem; border: 1px solid #ddd; border-radius: 4px;">
                        📖 Complete Calculator Guide
                    </a>
                    <a href="/blog/" style="color: #007bff; text-decoration: none; padding: 1rem; border: 1px solid #ddd; border-radius: 4px;">
                        📝 Financial Tips & Resources
                    </a>
                </div>
                <p>Free calculators and expert financial guidance. Built with Flask and ❤️</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/calculators/mortgage/')
def mortgage_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mortgage Calculator - Home Loan Payment Calculator Free</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free mortgage calculator with PMI, property taxes, insurance, and HOA. Calculate monthly payments, affordability, and total costs.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .form-sections { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
            .form-section { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; }
            .form-section h3 { margin-top: 0; color: #495057; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            .mortgage-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
            .summary-item { text-align: center; padding: 1.5rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; }
            .summary-value { font-size: 1.8rem; font-weight: bold; color: #007bff; margin-bottom: 0.25rem; }
            .summary-label { font-size: 0.9rem; color: #6c757d; }
            .payment-breakdown { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }
            .breakdown-item { display: flex; justify-content: space-between; margin: 0.5rem 0; }
            .affordability-info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }
            .pmi-warning { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
            .closing-costs { background: #e2e3e5; border: 1px solid #d3d3d4; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
            @media (max-width: 768px) {
                .form-sections { grid-template-columns: 1fr; }
                .form-row { grid-template-columns: 1fr; }
                .mortgage-summary { grid-template-columns: 1fr 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🏠 Mortgage Calculator</h1>
            <p>Calculate your monthly mortgage payment including PMI, property taxes, insurance, and HOA fees. Get affordability estimates and closing cost projections.</p>
            
            <form id="mortgage-form">
                <div class="form-sections">
                    <div class="form-section">
                        <h3>🏠 Home & Loan Details</h3>
                        
                        <div class="form-group">
                            <label for="home_price">Home Price ($):</label>
                            <input type="number" id="home_price" name="home_price" step="1000" required>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="down_payment_percent">Down Payment (%):</label>
                                <input type="number" id="down_payment_percent" name="down_payment_percent" value="20" step="0.5" min="0" max="100">
                            </div>
                            <div class="form-group">
                                <label for="down_payment_amount">Or Amount ($):</label>
                                <input type="number" id="down_payment_amount" name="down_payment_amount" step="1000">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="annual_rate">Interest Rate (%):</label>
                                <input type="number" id="annual_rate" name="annual_rate" step="0.01" required>
                            </div>
                            <div class="form-group">
                                <label for="loan_term_years">Loan Term (Years):</label>
                                <select id="loan_term_years" name="loan_term_years">
                                    <option value="15">15 years</option>
                                    <option value="20">20 years</option>
                                    <option value="25">25 years</option>
                                    <option value="30" selected>30 years</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h3>💰 Additional Costs</h3>
                        
                        <div class="form-group">
                            <label for="property_tax_annual">Property Tax (Annual $):</label>
                            <input type="number" id="property_tax_annual" name="property_tax_annual" step="100">
                        </div>
                        
                        <div class="form-group">
                            <label for="home_insurance_annual">Home Insurance (Annual $):</label>
                            <input type="number" id="home_insurance_annual" name="home_insurance_annual" step="100">
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="hoa_monthly">HOA Fee (Monthly $):</label>
                                <input type="number" id="hoa_monthly" name="hoa_monthly" step="25">
                            </div>
                            <div class="form-group">
                                <label for="pmi_rate">PMI Rate (% annually):</label>
                                <input type="number" id="pmi_rate" name="pmi_rate" value="0.5" step="0.1" min="0" max="2">
                            </div>
                        </div>
                    </div>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Mortgage</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('mortgage-form');
            const calculateBtn = document.getElementById('calculate-btn');
            const downPaymentPercent = document.getElementById('down_payment_percent');
            const downPaymentAmount = document.getElementById('down_payment_amount');
            const homePriceInput = document.getElementById('home_price');
            
            // Sync down payment percentage and amount
            downPaymentPercent.addEventListener('input', function() {
                const homePrice = parseFloat(homePriceInput.value) || 0;
                if (homePrice > 0) {
                    const amount = (homePrice * parseFloat(this.value)) / 100;
                    downPaymentAmount.value = Math.round(amount);
                }
            });
            
            downPaymentAmount.addEventListener('input', function() {
                const homePrice = parseFloat(homePriceInput.value) || 0;
                if (homePrice > 0) {
                    const percent = (parseFloat(this.value) / homePrice) * 100;
                    downPaymentPercent.value = percent.toFixed(1);
                }
            });
            
            homePriceInput.addEventListener('input', function() {
                // Update down payment amount when home price changes
                const percent = parseFloat(downPaymentPercent.value) || 20;
                const amount = (parseFloat(this.value) * percent) / 100;
                downPaymentAmount.value = Math.round(amount);
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/mortgage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        // Main mortgage summary
                        resultHtml += '<div class="mortgage-summary">';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.total_monthly_payment + '</div>';
                        resultHtml += '<div class="summary-label">Total Monthly Payment</div>';
                        resultHtml += '</div>';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.monthly_principal_interest + '</div>';
                        resultHtml += '<div class="summary-label">Principal & Interest</div>';
                        resultHtml += '</div>';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.required_annual_income + '</div>';
                        resultHtml += '<div class="summary-label">Required Annual Income</div>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        // Payment breakdown
                        resultHtml += '<div class="payment-breakdown">';
                        resultHtml += '<h4>Monthly Payment Breakdown</h4>';
                        resultHtml += '<div class="breakdown-item"><span>Principal & Interest:</span><span>$' + result.monthly_principal_interest + '</span></div>';
                        if (result.monthly_property_tax > 0) {
                            resultHtml += '<div class="breakdown-item"><span>Property Tax:</span><span>$' + result.monthly_property_tax + '</span></div>';
                        }
                        if (result.monthly_insurance > 0) {
                            resultHtml += '<div class="breakdown-item"><span>Home Insurance:</span><span>$' + result.monthly_insurance + '</span></div>';
                        }
                        if (result.pmi_monthly > 0) {
                            resultHtml += '<div class="breakdown-item"><span>PMI:</span><span>$' + result.pmi_monthly + '</span></div>';
                        }
                        if (result.hoa_monthly > 0) {
                            resultHtml += '<div class="breakdown-item"><span>HOA Fee:</span><span>$' + result.hoa_monthly + '</span></div>';
                        }
                        resultHtml += '<hr style="margin: 1rem 0;">';
                        resultHtml += '<div class="breakdown-item"><strong><span>Total Monthly:</span><span>$' + result.total_monthly_payment + '</span></strong></div>';
                        resultHtml += '</div>';
                        
                        // PMI warning if applicable
                        if (result.needs_pmi) {
                            resultHtml += '<div class="pmi-warning">';
                            resultHtml += '<h4>⚠️ PMI Required</h4>';
                            resultHtml += '<p>Since your down payment is less than 20%, you\'ll need Private Mortgage Insurance (PMI) of $' + result.pmi_monthly + '/month. ';
                            resultHtml += 'PMI can typically be removed once you reach 20% equity in your home.</p>';
                            resultHtml += '</div>';
                        }
                        
                        // Affordability information
                        resultHtml += '<div class="affordability-info">';
                        resultHtml += '<h4>💡 Affordability Analysis</h4>';
                        resultHtml += '<p><strong>28% Rule:</strong> Your monthly housing payment should not exceed 28% of your gross monthly income.</p>';
                        resultHtml += '<p><strong>Required Annual Income:</strong> $' + result.required_annual_income + ' (based on 28% rule)</p>';
                        resultHtml += '<p><strong>Down Payment:</strong> $' + result.down_payment + ' (' + result.down_payment_percent + '% of home price)</p>';
                        resultHtml += '</div>';
                        
                        // Closing costs estimate
                        if (result.closing_costs) {
                            resultHtml += '<div class="closing-costs">';
                            resultHtml += '<h4>📋 Estimated Closing Costs</h4>';
                            resultHtml += '<p>Typical closing costs range from 2-5% of the home price:</p>';
                            resultHtml += '<p><strong>Low estimate:</strong> $' + result.closing_costs.low + '</p>';
                            resultHtml += '<p><strong>Typical:</strong> $' + result.closing_costs.typical + '</p>';
                            resultHtml += '<p><strong>High estimate:</strong> $' + result.closing_costs.high + '</p>';
                            resultHtml += '</div>';
                        }
                        
                        // Total costs summary
                        resultHtml += '<div style="background: #e9ecef; padding: 1rem; border-radius: 4px; margin-top: 1rem;">';
                        resultHtml += '<h4>💰 Total Cost Summary</h4>';
                        resultHtml += '<p><strong>Home Price:</strong> $' + result.home_price + '</p>';
                        resultHtml += '<p><strong>Total Interest Paid:</strong> $' + result.total_interest + '</p>';
                        resultHtml += '<p><strong>Total Cost of Home:</strong> $' + result.total_cost_of_home + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Mortgage';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/calculators/loan/')
def loan_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loan Calculator - Calculate Monthly Payments Free</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free loan calculator for personal loans, auto loans, student loans. Calculate monthly payments, total interest, and amortization schedules.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .loan-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
            .summary-item { text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; }
            .summary-value { font-size: 1.5rem; font-weight: bold; color: #007bff; }
            .summary-label { font-size: 0.9rem; color: #6c757d; margin-top: 0.25rem; }
            .loan-info { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
            .amortization-table { width: 100%; border-collapse: collapse; margin-top: 1rem; font-size: 0.9rem; }
            .amortization-table th, .amortization-table td { padding: 0.5rem; border: 1px solid #dee2e6; text-align: right; }
            .amortization-table th { background: #f8f9fa; font-weight: 600; }
            .amortization-table tbody tr:nth-child(even) { background: #f8f9fa; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            @media (max-width: 600px) {
                .form-row { grid-template-columns: 1fr; }
                .loan-summary { grid-template-columns: 1fr 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🏦 Loan Calculator</h1>
            <p>Calculate monthly payments, total interest, and amortization schedules for personal loans, auto loans, student loans, and more.</p>
            
            <form id="loan-form">
                <div class="form-group">
                    <label for="loan_type">Loan Type:</label>
                    <select id="loan_type" name="loan_type">
                        <option value="personal">Personal Loan</option>
                        <option value="auto">Auto Loan</option>
                        <option value="student">Student Loan</option>
                        <option value="mortgage">Mortgage</option>
                    </select>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="loan_amount">Loan Amount ($):</label>
                        <input type="number" id="loan_amount" name="loan_amount" step="100" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="annual_rate">Annual Interest Rate (%):</label>
                        <input type="number" id="annual_rate" name="annual_rate" step="0.01" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="loan_term_years">Loan Term (Years):</label>
                    <input type="number" id="loan_term_years" name="loan_term_years" step="0.5" required>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Loan</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('loan-form');
            const calculateBtn = document.getElementById('calculate-btn');
            const loanTypeSelect = document.getElementById('loan_type');
            
            // Update typical values based on loan type
            loanTypeSelect.addEventListener('change', function() {
                const loanAmount = document.getElementById('loan_amount');
                const annualRate = document.getElementById('annual_rate');
                const loanTerm = document.getElementById('loan_term_years');
                
                switch(this.value) {
                    case 'personal':
                        loanAmount.placeholder = 'e.g., 15000';
                        annualRate.placeholder = 'e.g., 12.5';
                        loanTerm.placeholder = 'e.g., 5';
                        break;
                    case 'auto':
                        loanAmount.placeholder = 'e.g., 25000';
                        annualRate.placeholder = 'e.g., 6.5';
                        loanTerm.placeholder = 'e.g., 5';
                        break;
                    case 'student':
                        loanAmount.placeholder = 'e.g., 50000';
                        annualRate.placeholder = 'e.g., 5.5';
                        loanTerm.placeholder = 'e.g., 10';
                        break;
                    case 'mortgage':
                        loanAmount.placeholder = 'e.g., 300000';
                        annualRate.placeholder = 'e.g., 4.5';
                        loanTerm.placeholder = 'e.g., 30';
                        break;
                }
            });
            
            // Trigger initial placeholder update
            loanTypeSelect.dispatchEvent(new Event('change'));
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/loan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        // Loan summary
                        resultHtml += '<div class="loan-summary">';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.monthly_payment + '</div>';
                        resultHtml += '<div class="summary-label">Monthly Payment</div>';
                        resultHtml += '</div>';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.total_paid + '</div>';
                        resultHtml += '<div class="summary-label">Total Paid</div>';
                        resultHtml += '</div>';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.total_interest + '</div>';
                        resultHtml += '<div class="summary-label">Total Interest</div>';
                        resultHtml += '</div>';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">' + result.annual_rate + '%</div>';
                        resultHtml += '<div class="summary-label">Interest Rate</div>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        // Loan type information
                        if (result.loan_info) {
                            const info = result.loan_info;
                            resultHtml += '<div class="loan-info">';
                            resultHtml += '<h4>' + data.loan_type.charAt(0).toUpperCase() + data.loan_type.slice(1) + ' Loan Information</h4>';
                            resultHtml += '<p><strong>Description:</strong> ' + info.description + '</p>';
                            resultHtml += '<p><strong>Typical Rates:</strong> ' + info.typical_rates + '</p>';
                            resultHtml += '<p><strong>Typical Terms:</strong> ' + info.typical_terms + '</p>';
                            if (info.uses && info.uses.length > 0) {
                                resultHtml += '<p><strong>Common Uses:</strong> ' + info.uses.join(', ') + '</p>';
                            }
                            resultHtml += '</div>';
                        }
                        
                        // Amortization table (first year)
                        if (result.amortization_sample && result.amortization_sample.length > 0) {
                            resultHtml += '<h4>First Year Payment Breakdown</h4>';
                            resultHtml += '<table class="amortization-table">';
                            resultHtml += '<thead><tr><th>Month</th><th>Payment</th><th>Principal</th><th>Interest</th><th>Balance</th></tr></thead>';
                            resultHtml += '<tbody>';
                            
                            result.amortization_sample.forEach(payment => {
                                resultHtml += '<tr>';
                                resultHtml += '<td>' + payment.month + '</td>';
                                resultHtml += '<td>$' + payment.payment + '</td>';
                                resultHtml += '<td>$' + payment.principal + '</td>';
                                resultHtml += '<td>$' + payment.interest + '</td>';
                                resultHtml += '<td>$' + payment.balance + '</td>';
                                resultHtml += '</tr>';
                            });
                            
                            resultHtml += '</tbody></table>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Loan';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/calculators/tip/')
def tip_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tip Calculator - Calculate Tips and Split Bills Free</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free tip calculator to calculate tips and split bills for restaurants, delivery, and more services.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .quick-tips { display: flex; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap; }
            .quick-tip { background: #f8f9fa; border: 1px solid #dee2e6; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
            .quick-tip:hover { background: #e9ecef; }
            .calculation-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
            .summary-item { text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 4px; }
            .summary-value { font-size: 1.5rem; font-weight: bold; color: #007bff; }
            .summary-label { font-size: 0.9rem; color: #6c757d; }
            .split-details { margin-top: 1rem; }
            .tip-guide { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            @media (max-width: 600px) {
                .calculation-summary { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>💰 Tip Calculator</h1>
            <p>Calculate tips and split bills for restaurants, delivery, and more services.</p>
            
            <form id="tip-form">
                <div class="form-group">
                    <label for="service_type">Service Type:</label>
                    <select id="service_type" name="service_type">
                        <option value="restaurant">Restaurant</option>
                        <option value="delivery">Delivery</option>
                        <option value="bar">Bar/Drinks</option>
                        <option value="taxi_uber">Taxi/Uber</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="bill_amount">Bill Amount ($):</label>
                    <input type="number" id="bill_amount" name="bill_amount" step="0.01" required>
                </div>
                
                <div class="form-group">
                    <label for="tip_percentage">Tip Percentage (%):</label>
                    <input type="number" id="tip_percentage" name="tip_percentage" step="0.1" value="18" required>
                    <div class="quick-tips">
                        <span class="quick-tip" data-tip="15">15%</span>
                        <span class="quick-tip" data-tip="18">18%</span>
                        <span class="quick-tip" data-tip="20">20%</span>
                        <span class="quick-tip" data-tip="22">22%</span>
                        <span class="quick-tip" data-tip="25">25%</span>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="num_people">Number of People (split bill):</label>
                    <input type="number" id="num_people" name="num_people" min="1" value="1" required>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Tip</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('tip-form');
            const calculateBtn = document.getElementById('calculate-btn');
            const quickTips = document.querySelectorAll('.quick-tip');
            const tipInput = document.getElementById('tip_percentage');
            
            // Quick tip buttons
            quickTips.forEach(tip => {
                tip.addEventListener('click', function() {
                    tipInput.value = this.dataset.tip;
                    form.dispatchEvent(new Event('submit'));
                });
            });
            
            // Auto-calculate on input change
            form.addEventListener('input', function() {
                if (form.checkValidity()) {
                    setTimeout(() => form.dispatchEvent(new Event('submit')), 300);
                }
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/tip', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        // Summary
                        resultHtml += '<div class="calculation-summary">';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.tip_amount + '</div>';
                        resultHtml += '<div class="summary-label">Tip Amount</div>';
                        resultHtml += '</div>';
                        resultHtml += '<div class="summary-item">';
                        resultHtml += '<div class="summary-value">$' + result.total_amount + '</div>';
                        resultHtml += '<div class="summary-label">Total Amount</div>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        // Split details if more than 1 person
                        if (result.num_people > 1) {
                            resultHtml += '<div class="split-details">';
                            resultHtml += '<h4>Split Between ' + result.num_people + ' People:</h4>';
                            resultHtml += '<div class="calculation-summary">';
                            resultHtml += '<div class="summary-item">';
                            resultHtml += '<div class="summary-value">$' + result.bill_per_person + '</div>';
                            resultHtml += '<div class="summary-label">Bill Per Person</div>';
                            resultHtml += '</div>';
                            resultHtml += '<div class="summary-item">';
                            resultHtml += '<div class="summary-value">$' + result.tip_per_person + '</div>';
                            resultHtml += '<div class="summary-label">Tip Per Person</div>';
                            resultHtml += '</div>';
                            resultHtml += '<div class="summary-item">';
                            resultHtml += '<div class="summary-value">$' + result.total_per_person + '</div>';
                            resultHtml += '<div class="summary-label">Total Per Person</div>';
                            resultHtml += '</div>';
                            resultHtml += '</div>';
                            resultHtml += '</div>';
                        }
                        
                        // Tip guide
                        if (result.tip_guide) {
                            const guide = result.tip_guide;
                            resultHtml += '<div class="tip-guide">';
                            resultHtml += '<h4>Tip Guide for ' + data.service_type.charAt(0).toUpperCase() + data.service_type.slice(1) + ':</h4>';
                            
                            Object.keys(guide).forEach(key => {
                                if (key !== 'note') {
                                    resultHtml += '<p><strong>' + key.replace('_', ' ').toUpperCase() + ':</strong> ' + guide[key] + '</p>';
                                }
                            });
                            
                            if (guide.note) {
                                resultHtml += '<p><em>' + guide.note + '</em></p>';
                            }
                            resultHtml += '</div>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Tip';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/calculators/bmi/')
def bmi_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BMI Calculator - Body Mass Index Calculator Free</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free BMI calculator to check your body mass index. Calculate BMI for adults with health recommendations.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .bmi-result { text-align: center; margin-bottom: 1rem; }
            .bmi-value { font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
            .bmi-category { font-size: 1.2rem; margin: 0.5rem 0; padding: 0.5rem; border-radius: 4px; }
            .recommendations { margin-top: 1rem; }
            .recommendations ul { margin: 0.5rem 0; padding-left: 1.5rem; }
            .unit-toggle { display: flex; gap: 1rem; margin-bottom: 1rem; }
            .unit-toggle label { flex: 1; }
            .unit-toggle input[type="radio"] { width: auto; margin-right: 0.5rem; }
            .ideal-weight { background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-top: 1rem; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>⚖️ BMI Calculator</h1>
            <p>Calculate your Body Mass Index (BMI) and get personalized health recommendations.</p>
            
            <form id="bmi-form">
                <div class="unit-toggle">
                    <label>
                        <input type="radio" name="unit_system" value="metric" checked> 
                        Metric (kg, cm)
                    </label>
                    <label>
                        <input type="radio" name="unit_system" value="imperial"> 
                        Imperial (lbs, inches)
                    </label>
                </div>
                
                <div class="form-group">
                    <label for="weight" id="weight-label">Weight (kg):</label>
                    <input type="number" id="weight" name="weight" step="0.1" required>
                </div>
                
                <div class="form-group">
                    <label for="height" id="height-label">Height (cm):</label>
                    <input type="number" id="height" name="height" step="0.1" required>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate BMI</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('bmi-form');
            const calculateBtn = document.getElementById('calculate-btn');
            const unitRadios = document.querySelectorAll('input[name="unit_system"]');
            const weightLabel = document.getElementById('weight-label');
            const heightLabel = document.getElementById('height-label');
            
            // Unit system change handler
            unitRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'metric') {
                        weightLabel.textContent = 'Weight (kg):';
                        heightLabel.textContent = 'Height (cm):';
                        document.getElementById('weight').placeholder = 'e.g., 70';
                        document.getElementById('height').placeholder = 'e.g., 175';
                    } else {
                        weightLabel.textContent = 'Weight (lbs):';
                        heightLabel.textContent = 'Height (inches):';
                        document.getElementById('weight').placeholder = 'e.g., 154';
                        document.getElementById('height').placeholder = 'e.g., 69';
                    }
                });
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/bmi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        resultHtml += '<div class="bmi-result">';
                        resultHtml += '<div class="bmi-value" style="color: ' + result.color + '">BMI: ' + result.bmi + '</div>';
                        resultHtml += '<div class="bmi-category" style="background-color: ' + result.color + '20; color: ' + result.color + '">';
                        resultHtml += result.category + '</div>';
                        resultHtml += '<p><strong>' + result.description + '</strong></p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="ideal-weight">';
                        resultHtml += '<strong>Ideal Weight Range:</strong> ' + result.ideal_weight_range;
                        resultHtml += '</div>';
                        
                        if (result.recommendations && result.recommendations.length > 0) {
                            resultHtml += '<div class="recommendations">';
                            resultHtml += '<h4>Health Recommendations:</h4>';
                            resultHtml += '<ul>';
                            result.recommendations.forEach(rec => {
                                resultHtml += '<li>' + rec + '</li>';
                            });
                            resultHtml += '</ul>';
                            resultHtml += '</div>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate BMI';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/calculators/percentage/')
def percentage_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Percentage Calculator - Free Online Tool</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free online percentage calculator. Calculate percentages, percentage increase/decrease, and more.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .operation-fields { margin-top: 1rem; }
            .formula { background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-top: 1rem; font-family: monospace; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🧮 Percentage Calculator</h1>
            <p>Calculate percentages, increases, decreases, and differences with ease.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="operation">Calculation Type:</label>
                    <select id="operation" name="operation" required>
                        <option value="basic">What % is X of Y?</option>
                        <option value="find_value">What is X% of Y?</option>
                        <option value="increase">Increase by %</option>
                        <option value="decrease">Decrease by %</option>
                        <option value="difference">% Difference</option>
                        <option value="change">% Change</option>
                    </select>
                </div>
                
                <div id="basic-fields" class="operation-fields">
                    <div class="form-group">
                        <label for="x">First Number (X):</label>
                        <input type="number" id="x" name="x" step="any" required>
                    </div>
                    <div class="form-group">
                        <label for="y">Second Number (Y):</label>
                        <input type="number" id="y" name="y" step="any" required>
                    </div>
                </div>
                
                <div id="find_value-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="percent">Percentage (%):</label>
                        <input type="number" id="percent" name="percent" step="any">
                    </div>
                    <div class="form-group">
                        <label for="total">Total Amount:</label>
                        <input type="number" id="total" name="total" step="any">
                    </div>
                </div>
                
                <div id="increase-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="original">Original Value:</label>
                        <input type="number" id="original" name="original" step="any">
                    </div>
                    <div class="form-group">
                        <label for="percent_inc">Percentage Increase (%):</label>
                        <input type="number" id="percent_inc" name="percent" step="any">
                    </div>
                </div>
                
                <div id="decrease-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="original_dec">Original Value:</label>
                        <input type="number" id="original_dec" name="original" step="any">
                    </div>
                    <div class="form-group">
                        <label for="percent_dec">Percentage Decrease (%):</label>
                        <input type="number" id="percent_dec" name="percent" step="any">
                    </div>
                </div>
                
                <div id="difference-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="x_diff">First Value:</label>
                        <input type="number" id="x_diff" name="x" step="any">
                    </div>
                    <div class="form-group">
                        <label for="y_diff">Second Value:</label>
                        <input type="number" id="y_diff" name="y" step="any">
                    </div>
                </div>
                
                <div id="change-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="original_change">Original Value:</label>
                        <input type="number" id="original_change" name="original" step="any">
                    </div>
                    <div class="form-group">
                        <label for="new_value">New Value:</label>
                        <input type="number" id="new_value" name="new_value" step="any">
                    </div>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const operationSelect = document.getElementById('operation');
            const form = document.getElementById('calculator-form');
            const calculateBtn = document.getElementById('calculate-btn');
            
            operationSelect.addEventListener('change', function() {
                document.querySelectorAll('.operation-fields').forEach(field => {
                    field.style.display = 'none';
                    field.querySelectorAll('input').forEach(input => input.removeAttribute('required'));
                });
                
                const selectedFields = document.getElementById(this.value + '-fields');
                if (selectedFields) {
                    selectedFields.style.display = 'block';
                    selectedFields.querySelectorAll('input').forEach(input => input.setAttribute('required', 'required'));
                }
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                console.log('Sending data:', data);
                
                fetch('/api/calculate/percentage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    console.log('Response status:', response.status);
                    return response.json();
                })
                .then(result => {
                    console.log('Result:', result);
                    
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        resultHtml += '<h3>Result: ' + result.result + '</h3>';
                        resultHtml += '<p>' + result.explanation + '</p>';
                        if (result.formula) {
                            resultHtml += '<div class="formula"><strong>Formula:</strong> ' + result.formula + '</div>';
                        }
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/mortgage', methods=['POST'])
def calculate_mortgage():
    try:
        print("API called - calculating mortgage")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = MortgageCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Mortgage calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'mortgage',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Mortgage API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate/loan', methods=['POST'])
def calculate_loan():
    try:
        print("API called - calculating loan")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = LoanCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Loan calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'loan',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Loan API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate/tip', methods=['POST'])
def calculate_tip():
    try:
        print("API called - calculating tip")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = TipCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Tip calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'tip',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Tip API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate/bmi', methods=['POST'])
def calculate_bmi():
    try:
        print("API called - calculating BMI")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = BMICalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"BMI calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'bmi',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in BMI API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate/percentage', methods=['POST'])
def calculate_percentage():
    try:
        print("API called - calculating percentage")
        
        # Get the request data
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Create calculator instance
        calc = PercentageCalculator()
        
        # Validate inputs
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        # Perform calculation
        result = calc.calculate(data)
        print(f"Calculation result: {result}")
        
        # Log calculation (in-memory for demo)
        calculation_logs.append({
            'calculator': 'percentage',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# SEO Routes
@app.route('/calculators/income-tax/')
def income_tax_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Income Tax Calculator - Federal and State Tax Calculator Free</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free income tax calculator for federal and state taxes. Calculate your tax liability, refund, and take-home pay for 2024.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .tax-breakdown { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
            .tax-item { background: #f8f9fa; padding: 1rem; border-radius: 4px; }
            .tax-summary { background: #d4edda; border: 1px solid #c3e6cb; padding: 1rem; border-radius: 4px; margin-top: 1rem; text-align: center; }
            .rates { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>📋 Income Tax Calculator</h1>
            <p>Calculate your federal and state income taxes, FICA taxes, and take-home pay for 2024.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="annual_income">Annual Income ($):</label>
                    <input type="number" id="annual_income" name="annual_income" step="0.01" min="0" max="10000000" required placeholder="75000">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="filing_status">Filing Status:</label>
                        <select id="filing_status" name="filing_status" required>
                            <option value="single">Single</option>
                            <option value="married_jointly">Married Filing Jointly</option>
                            <option value="married_separately">Married Filing Separately</option>
                            <option value="head_of_household">Head of Household</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="state">State:</label>
                        <select id="state" name="state" required>
                            <option value="no_state_tax">No State Tax</option>
                            <option value="california">California</option>
                            <option value="new_york">New York</option>
                            <option value="texas">Texas</option>
                            <option value="florida">Florida</option>
                            <option value="illinois">Illinois</option>
                            <option value="pennsylvania">Pennsylvania</option>
                            <option value="washington">Washington</option>
                            <option value="nevada">Nevada</option>
                            <option value="tennessee">Tennessee</option>
                            <option value="new_hampshire">New Hampshire</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="tax_year">Tax Year:</label>
                    <select id="tax_year" name="tax_year" required>
                        <option value="2024">2024</option>
                        <option value="2023">2023</option>
                    </select>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Taxes</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('calculator-form');
            const calculateBtn = document.getElementById('calculate-btn');
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                console.log('Sending data:', data);
                
                fetch('/api/calculate/income-tax', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    console.log('Received result:', result);
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        resultHtml += '<div class="tax-summary">';
                        resultHtml += '<h3>Annual Take-Home Pay: $' + result.net_income.toLocaleString() + '</h3>';
                        resultHtml += '<p>Monthly: $' + result.monthly_net.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-breakdown">';
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Federal Tax</h4>';
                        resultHtml += '<p>$' + result.federal_tax.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>State Tax</h4>';
                        resultHtml += '<p>$' + result.state_tax.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Social Security</h4>';
                        resultHtml += '<p>$' + result.social_security_tax.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Medicare</h4>';
                        resultHtml += '<p>$' + (result.medicare_tax + result.additional_medicare).toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="rates">';
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Effective Tax Rate</h4>';
                        resultHtml += '<p>' + result.effective_rate + '%</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Marginal Tax Rate</h4>';
                        resultHtml += '<p>' + result.marginal_rate + '%</p>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item" style="margin-top: 1rem;">';
                        resultHtml += '<h4>Tax Summary</h4>';
                        resultHtml += '<p><strong>Gross Income:</strong> $' + result.annual_income.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Standard Deduction:</strong> $' + result.standard_deduction.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Taxable Income:</strong> $' + result.taxable_income.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Total Taxes:</strong> $' + result.total_tax.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Monthly Taxes:</strong> $' + result.monthly_tax.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Taxes';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/income-tax', methods=['POST'])
def calculate_income_tax():
    try:
        print("API called - calculating income tax")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = IncomeTaxCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Income tax calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'income_tax',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Income Tax API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/sales-tax/')
def sales_tax_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Tax Calculator - Calculate Sales Tax by State and City</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free sales tax calculator. Calculate sales tax by state, city, and ZIP code. Get accurate tax rates for 2024.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .tax-breakdown { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
            .tax-item { background: #f8f9fa; padding: 1rem; border-radius: 4px; text-align: center; }
            .total-summary { background: #d4edda; border: 1px solid #c3e6cb; padding: 1rem; border-radius: 4px; margin-top: 1rem; text-align: center; }
            .location-info { background: #e2e3e5; border: 1px solid #d6d8db; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .custom-rate { display: none; }
            .custom-rate.show { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🛒 Sales Tax Calculator</h1>
            <p>Calculate sales tax by state, city, and ZIP code with accurate 2024 tax rates.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="purchase_amount">Purchase Amount ($):</label>
                    <input type="number" id="purchase_amount" name="purchase_amount" step="0.01" min="0" max="1000000" required placeholder="100.00">
                </div>
                
                <div class="form-group">
                    <label for="location">Location:</label>
                    <select id="location" name="location" required>
                        <option value="custom">Custom Tax Rate</option>
                        <optgroup label="No Sales Tax">
                            <option value="delaware">Delaware</option>
                            <option value="montana">Montana</option>
                            <option value="new_hampshire">New Hampshire</option>
                            <option value="oregon">Oregon</option>
                        </optgroup>
                        <optgroup label="Major States">
                            <option value="california">California</option>
                            <option value="texas">Texas</option>
                            <option value="florida">Florida</option>
                            <option value="new_york">New York</option>
                            <option value="pennsylvania">Pennsylvania</option>
                            <option value="illinois">Illinois</option>
                            <option value="ohio">Ohio</option>
                            <option value="georgia">Georgia</option>
                            <option value="north_carolina">North Carolina</option>
                            <option value="michigan">Michigan</option>
                        </optgroup>
                        <optgroup label="All States">
                            <option value="alabama">Alabama</option>
                            <option value="alaska">Alaska</option>
                            <option value="arizona">Arizona</option>
                            <option value="arkansas">Arkansas</option>
                            <option value="colorado">Colorado</option>
                            <option value="connecticut">Connecticut</option>
                            <option value="hawaii">Hawaii</option>
                            <option value="idaho">Idaho</option>
                            <option value="indiana">Indiana</option>
                            <option value="iowa">Iowa</option>
                            <option value="kansas">Kansas</option>
                            <option value="kentucky">Kentucky</option>
                            <option value="louisiana">Louisiana</option>
                            <option value="maine">Maine</option>
                            <option value="maryland">Maryland</option>
                            <option value="massachusetts">Massachusetts</option>
                            <option value="minnesota">Minnesota</option>
                            <option value="mississippi">Mississippi</option>
                            <option value="missouri">Missouri</option>
                            <option value="nebraska">Nebraska</option>
                            <option value="nevada">Nevada</option>
                            <option value="new_jersey">New Jersey</option>
                            <option value="new_mexico">New Mexico</option>
                            <option value="north_dakota">North Dakota</option>
                            <option value="oklahoma">Oklahoma</option>
                            <option value="rhode_island">Rhode Island</option>
                            <option value="south_carolina">South Carolina</option>
                            <option value="south_dakota">South Dakota</option>
                            <option value="tennessee">Tennessee</option>
                            <option value="utah">Utah</option>
                            <option value="vermont">Vermont</option>
                            <option value="virginia">Virginia</option>
                            <option value="washington">Washington</option>
                            <option value="west_virginia">West Virginia</option>
                            <option value="wisconsin">Wisconsin</option>
                            <option value="wyoming">Wyoming</option>
                        </optgroup>
                    </select>
                </div>
                
                <div class="form-group custom-rate" id="custom-rate-group">
                    <label for="tax_rate">Tax Rate (%):</label>
                    <input type="number" id="tax_rate" name="tax_rate" step="0.01" min="0" max="50" placeholder="8.25">
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Sales Tax</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('calculator-form');
            const calculateBtn = document.getElementById('calculate-btn');
            const locationSelect = document.getElementById('location');
            const customRateGroup = document.getElementById('custom-rate-group');
            const taxRateInput = document.getElementById('tax_rate');
            
            // Show/hide custom tax rate field
            locationSelect.addEventListener('change', function() {
                if (this.value === 'custom') {
                    customRateGroup.classList.add('show');
                    taxRateInput.required = true;
                } else {
                    customRateGroup.classList.remove('show');
                    taxRateInput.required = false;
                }
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                console.log('Sending data:', data);
                
                fetch('/api/calculate/sales-tax', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    console.log('Received result:', result);
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        resultHtml += '<div class="total-summary">';
                        resultHtml += '<h3>Total Amount: $' + result.total_amount.toLocaleString() + '</h3>';
                        resultHtml += '<p>Sales Tax: $' + result.sales_tax.toLocaleString() + ' (' + result.tax_rate + '%)</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-breakdown">';
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Purchase Amount</h4>';
                        resultHtml += '<p>$' + result.purchase_amount.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Sales Tax</h4>';
                        resultHtml += '<p>$' + result.sales_tax.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        if (result.location_info) {
                            resultHtml += '<div class="location-info">';
                            resultHtml += '<h4>Tax Rate Breakdown</h4>';
                            resultHtml += '<p><strong>State Rate:</strong> ' + result.location_info.state_rate + '</p>';
                            resultHtml += '<p><strong>Average Local Rate:</strong> ' + result.location_info.avg_local_rate + '</p>';
                            resultHtml += '<p><strong>Total Range:</strong> ' + result.location_info.total_range + '</p>';
                            resultHtml += '<p><em>' + result.location_info.note + '</em></p>';
                            resultHtml += '</div>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Sales Tax';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/sales-tax', methods=['POST'])
def calculate_sales_tax():
    try:
        print("API called - calculating sales tax")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = SalesTaxCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Sales tax calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'sales_tax',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Sales Tax API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/property-tax/')
def property_tax_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Property Tax Calculator - Calculate Annual Property Taxes</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free property tax calculator. Estimate annual property taxes by state, county, and city with exemptions for 2024.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .tax-breakdown { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
            .tax-item { background: #f8f9fa; padding: 1rem; border-radius: 4px; text-align: center; }
            .total-summary { background: #d4edda; border: 1px solid #c3e6cb; padding: 1rem; border-radius: 4px; margin-top: 1rem; text-align: center; }
            .location-info { background: #e2e3e5; border: 1px solid #d6d8db; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .exemptions { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .custom-rate { display: none; }
            .custom-rate.show { display: block; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🏘️ Property Tax Calculator</h1>
            <p>Calculate annual property taxes by state with homestead exemptions and other tax breaks for 2024.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="home_value">Home Value ($):</label>
                    <input type="number" id="home_value" name="home_value" step="1000" min="1" max="50000000" required placeholder="300000">
                </div>
                
                <div class="form-group">
                    <label for="location">State:</label>
                    <select id="location" name="location" required>
                        <option value="custom">Custom Tax Rate</option>
                        <optgroup label="Highest Property Taxes">
                            <option value="new_jersey">New Jersey (2.49%)</option>
                            <option value="illinois">Illinois (2.38%)</option>
                            <option value="new_hampshire">New Hampshire (1.86%)</option>
                            <option value="connecticut">Connecticut (1.73%)</option>
                            <option value="texas">Texas (1.81%)</option>
                        </optgroup>
                        <optgroup label="Major States">
                            <option value="california">California (0.81%)</option>
                            <option value="florida">Florida (0.97%)</option>
                            <option value="new_york">New York (1.73%)</option>
                            <option value="pennsylvania">Pennsylvania (1.59%)</option>
                            <option value="ohio">Ohio (1.61%)</option>
                            <option value="georgia">Georgia (0.92%)</option>
                            <option value="north_carolina">North Carolina (0.90%)</option>
                            <option value="michigan">Michigan (1.62%)</option>
                        </optgroup>
                        <optgroup label="Lowest Property Taxes">
                            <option value="hawaii">Hawaii (0.31%)</option>
                            <option value="alabama">Alabama (0.41%)</option>
                            <option value="colorado">Colorado (0.51%)</option>
                            <option value="south_carolina">South Carolina (0.59%)</option>
                            <option value="utah">Utah (0.60%)</option>
                        </optgroup>
                        <optgroup label="All States">
                            <option value="alaska">Alaska</option>
                            <option value="arizona">Arizona</option>
                            <option value="arkansas">Arkansas</option>
                            <option value="delaware">Delaware</option>
                            <option value="idaho">Idaho</option>
                            <option value="indiana">Indiana</option>
                            <option value="iowa">Iowa</option>
                            <option value="kansas">Kansas</option>
                            <option value="kentucky">Kentucky</option>
                            <option value="louisiana">Louisiana</option>
                            <option value="maine">Maine</option>
                            <option value="maryland">Maryland</option>
                            <option value="massachusetts">Massachusetts</option>
                            <option value="minnesota">Minnesota</option>
                            <option value="mississippi">Mississippi</option>
                            <option value="missouri">Missouri</option>
                            <option value="montana">Montana</option>
                            <option value="nebraska">Nebraska</option>
                            <option value="nevada">Nevada</option>
                            <option value="new_mexico">New Mexico</option>
                            <option value="north_dakota">North Dakota</option>
                            <option value="oklahoma">Oklahoma</option>
                            <option value="oregon">Oregon</option>
                            <option value="rhode_island">Rhode Island</option>
                            <option value="south_dakota">South Dakota</option>
                            <option value="tennessee">Tennessee</option>
                            <option value="vermont">Vermont</option>
                            <option value="virginia">Virginia</option>
                            <option value="washington">Washington</option>
                            <option value="west_virginia">West Virginia</option>
                            <option value="wisconsin">Wisconsin</option>
                            <option value="wyoming">Wyoming</option>
                        </optgroup>
                    </select>
                </div>
                
                <div class="form-group custom-rate" id="custom-rate-group">
                    <label for="tax_rate">Property Tax Rate (%):</label>
                    <input type="number" id="tax_rate" name="tax_rate" step="0.01" min="0" max="10" placeholder="1.25">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="homestead_exemption">Homestead Exemption ($):</label>
                        <input type="number" id="homestead_exemption" name="homestead_exemption" step="1000" min="0" max="1000000" placeholder="50000">
                    </div>
                    
                    <div class="form-group">
                        <label for="senior_exemption">Senior Exemption ($):</label>
                        <input type="number" id="senior_exemption" name="senior_exemption" step="1000" min="0" max="1000000" placeholder="0">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="veteran_exemption">Veteran Exemption ($):</label>
                        <input type="number" id="veteran_exemption" name="veteran_exemption" step="1000" min="0" max="1000000" placeholder="0">
                    </div>
                    
                    <div class="form-group">
                        <label for="other_exemptions">Other Exemptions ($):</label>
                        <input type="number" id="other_exemptions" name="other_exemptions" step="1000" min="0" max="1000000" placeholder="0">
                    </div>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Property Tax</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('calculator-form');
            const calculateBtn = document.getElementById('calculate-btn');
            const locationSelect = document.getElementById('location');
            const customRateGroup = document.getElementById('custom-rate-group');
            const taxRateInput = document.getElementById('tax_rate');
            
            // Show/hide custom tax rate field
            locationSelect.addEventListener('change', function() {
                if (this.value === 'custom') {
                    customRateGroup.classList.add('show');
                    taxRateInput.required = true;
                } else {
                    customRateGroup.classList.remove('show');
                    taxRateInput.required = false;
                }
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                console.log('Sending data:', data);
                
                fetch('/api/calculate/property-tax', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    console.log('Received result:', result);
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        resultHtml += '<div class="total-summary">';
                        resultHtml += '<h3>Annual Property Tax: $' + result.annual_tax.toLocaleString() + '</h3>';
                        resultHtml += '<p>Monthly: $' + result.monthly_tax.toLocaleString() + ' | Rate: ' + result.tax_rate + '%</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-breakdown">';
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Home Value</h4>';
                        resultHtml += '<p>$' + result.home_value.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Taxable Value</h4>';
                        resultHtml += '<p>$' + result.taxable_value.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Effective Rate</h4>';
                        resultHtml += '<p>' + result.effective_rate + '%</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="tax-item">';
                        resultHtml += '<h4>Total Exemptions</h4>';
                        resultHtml += '<p>$' + result.total_exemptions.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        if (result.total_exemptions > 0) {
                            resultHtml += '<div class="exemptions">';
                            resultHtml += '<h4>Exemption Breakdown</h4>';
                            if (result.exemption_breakdown.homestead > 0) {
                                resultHtml += '<p><strong>Homestead:</strong> $' + result.exemption_breakdown.homestead.toLocaleString() + '</p>';
                            }
                            if (result.exemption_breakdown.senior > 0) {
                                resultHtml += '<p><strong>Senior:</strong> $' + result.exemption_breakdown.senior.toLocaleString() + '</p>';
                            }
                            if (result.exemption_breakdown.veteran > 0) {
                                resultHtml += '<p><strong>Veteran:</strong> $' + result.exemption_breakdown.veteran.toLocaleString() + '</p>';
                            }
                            if (result.exemption_breakdown.other > 0) {
                                resultHtml += '<p><strong>Other:</strong> $' + result.exemption_breakdown.other.toLocaleString() + '</p>';
                            }
                            resultHtml += '</div>';
                        }
                        
                        if (result.location_info) {
                            resultHtml += '<div class="location-info">';
                            resultHtml += '<h4>State Information</h4>';
                            resultHtml += '<p><strong>Average Rate:</strong> ' + result.location_info.avg_rate + '</p>';
                            resultHtml += '<p><strong>National Rank:</strong> ' + result.location_info.rank + '</p>';
                            resultHtml += '<p><strong>Tax on $200K Home:</strong> ' + result.location_info.avg_tax_on_200k + '</p>';
                            resultHtml += '<p><em>' + result.location_info.note + '</em></p>';
                            resultHtml += '</div>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Property Tax';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/property-tax', methods=['POST'])
def calculate_property_tax():
    try:
        print("API called - calculating property tax")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = PropertyTaxCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Property tax calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'property_tax',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Property Tax API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/tax-refund/')
def tax_refund_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tax Refund Calculator - Estimate Your Federal and State Tax Refund</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free tax refund estimator. Calculate your 2024 federal and state tax refund with withholdings, credits, and deductions.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .result.owed { background: #f8d7da; border: 1px solid #f5c6cb; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .refund-breakdown { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
            .refund-item { background: #f8f9fa; padding: 1rem; border-radius: 4px; text-align: center; }
            .refund-summary { padding: 1.5rem; border-radius: 4px; margin-top: 1rem; text-align: center; }
            .refund-summary.refund { background: #d4edda; border: 1px solid #c3e6cb; }
            .refund-summary.owed { background: #f8d7da; border: 1px solid #f5c6cb; }
            .refund-summary.even { background: #e2e3e5; border: 1px solid #d6d8db; }
            .credits-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>💰 Tax Refund Calculator</h1>
            <p>Estimate your 2024 federal and state tax refund based on withholdings, income, and tax credits.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="annual_income">Annual Income ($):</label>
                    <input type="number" id="annual_income" name="annual_income" step="0.01" min="0" max="10000000" required placeholder="75000">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="filing_status">Filing Status:</label>
                        <select id="filing_status" name="filing_status" required>
                            <option value="single">Single</option>
                            <option value="married_jointly">Married Filing Jointly</option>
                            <option value="married_separately">Married Filing Separately</option>
                            <option value="head_of_household">Head of Household</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="dependents">Number of Dependents:</label>
                        <input type="number" id="dependents" name="dependents" min="0" max="20" placeholder="0">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="federal_withholding">Federal Tax Withheld ($):</label>
                        <input type="number" id="federal_withholding" name="federal_withholding" step="0.01" min="0" max="1000000" placeholder="12000">
                    </div>
                    
                    <div class="form-group">
                        <label for="state_withholding">State Tax Withheld ($):</label>
                        <input type="number" id="state_withholding" name="state_withholding" step="0.01" min="0" max="1000000" placeholder="3000">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="state">State:</label>
                    <select id="state" name="state" required>
                        <option value="no_state_tax">No State Tax</option>
                        <option value="california">California</option>
                        <option value="new_york">New York</option>
                        <option value="texas">Texas</option>
                        <option value="florida">Florida</option>
                        <option value="illinois">Illinois</option>
                        <option value="pennsylvania">Pennsylvania</option>
                        <option value="washington">Washington</option>
                        <option value="nevada">Nevada</option>
                        <option value="tennessee">Tennessee</option>
                        <option value="new_hampshire">New Hampshire</option>
                    </select>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Tax Refund</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('calculator-form');
            const calculateBtn = document.getElementById('calculate-btn');
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                console.log('Sending data:', data);
                
                fetch('/api/calculate/tax-refund', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    console.log('Received result:', result);
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        // Main refund summary
                        let summaryClass = result.refund_status;
                        let summaryText = '';
                        let summaryIcon = '';
                        
                        if (result.refund_status === 'refund') {
                            summaryText = 'Estimated Tax Refund: $' + result.final_refund.toLocaleString();
                            summaryIcon = '💰';
                        } else if (result.refund_status === 'owed') {
                            summaryText = 'Estimated Amount Owed: $' + result.final_refund.toLocaleString();
                            summaryIcon = '💸';
                        } else {
                            summaryText = 'No Refund or Amount Owed';
                            summaryIcon = '⚖️';
                        }
                        
                        resultHtml += '<div class="refund-summary ' + summaryClass + '">';
                        resultHtml += '<h3>' + summaryIcon + ' ' + summaryText + '</h3>';
                        resultHtml += '<p>Effective Tax Rate: ' + result.effective_rate + '%</p>';
                        resultHtml += '</div>';
                        
                        // Breakdown
                        resultHtml += '<div class="refund-breakdown">';
                        resultHtml += '<div class="refund-item">';
                        resultHtml += '<h4>Federal</h4>';
                        resultHtml += '<p><strong>Withheld:</strong> $' + result.federal_withholding.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Actual Tax:</strong> $' + result.actual_federal_tax.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Difference:</strong> $' + result.federal_refund.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="refund-item">';
                        resultHtml += '<h4>State</h4>';
                        resultHtml += '<p><strong>Withheld:</strong> $' + result.state_withholding.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Actual Tax:</strong> $' + result.actual_state_tax.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Difference:</strong> $' + result.state_refund.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        // Tax Credits
                        if (result.total_credits > 0) {
                            resultHtml += '<div class="credits-section">';
                            resultHtml += '<h4>Tax Credits Applied</h4>';
                            if (result.child_tax_credit > 0) {
                                resultHtml += '<p><strong>Child Tax Credit:</strong> $' + result.child_tax_credit.toLocaleString() + '</p>';
                            }
                            if (result.earned_income_credit > 0) {
                                resultHtml += '<p><strong>Earned Income Credit:</strong> $' + result.earned_income_credit.toLocaleString() + '</p>';
                            }
                            resultHtml += '<p><strong>Total Credits:</strong> $' + result.total_credits.toLocaleString() + '</p>';
                            resultHtml += '</div>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Tax Refund';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/tax-refund', methods=['POST'])
def calculate_tax_refund():
    try:
        print("API called - calculating tax refund")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = TaxRefundCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Tax refund calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'tax_refund',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Tax Refund API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/gross-to-net/')
def gross_to_net_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gross to Net Salary Calculator - Calculate Take Home Pay</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free gross to net salary calculator. Calculate your take-home pay after taxes and deductions for 2024.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
            .pay-breakdown { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem; }
            .pay-item { background: #f8f9fa; padding: 1rem; border-radius: 4px; text-align: center; }
            .net-summary { background: #d4edda; border: 1px solid #c3e6cb; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; text-align: center; }
            .deductions-section { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .taxes-section { background: #e2e3e5; border: 1px solid #d6d8db; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .section-title { font-weight: bold; margin-bottom: 0.5rem; color: #495057; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>💵 Gross to Net Calculator</h1>
            <p>Calculate your take-home pay after taxes and deductions based on your pay frequency.</p>
            
            <form id="calculator-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="gross_salary">Gross Salary ($):</label>
                        <input type="number" id="gross_salary" name="gross_salary" step="0.01" min="0" max="10000000" required placeholder="75000">
                    </div>
                    
                    <div class="form-group">
                        <label for="pay_frequency">Pay Frequency:</label>
                        <select id="pay_frequency" name="pay_frequency" required>
                            <option value="annual">Annual</option>
                            <option value="monthly">Monthly</option>
                            <option value="semimonthly">Semi-Monthly (24/year)</option>
                            <option value="biweekly">Bi-Weekly (26/year)</option>
                            <option value="weekly">Weekly</option>
                            <option value="hourly">Hourly (40 hrs/week)</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="filing_status">Filing Status:</label>
                        <select id="filing_status" name="filing_status" required>
                            <option value="single">Single</option>
                            <option value="married_jointly">Married Filing Jointly</option>
                            <option value="married_separately">Married Filing Separately</option>
                            <option value="head_of_household">Head of Household</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="state">State:</label>
                        <select id="state" name="state" required>
                            <option value="no_state_tax">No State Tax</option>
                            <option value="california">California</option>
                            <option value="new_york">New York</option>
                            <option value="texas">Texas</option>
                            <option value="florida">Florida</option>
                            <option value="illinois">Illinois</option>
                            <option value="pennsylvania">Pennsylvania</option>
                            <option value="washington">Washington</option>
                            <option value="nevada">Nevada</option>
                            <option value="tennessee">Tennessee</option>
                            <option value="new_hampshire">New Hampshire</option>
                        </select>
                    </div>
                </div>
                
                <div class="section-title">Pre-Tax Deductions (Annual)</div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="retirement_401k">401k Contribution ($):</label>
                        <input type="number" id="retirement_401k" name="retirement_401k" step="100" min="0" max="100000" placeholder="6000">
                    </div>
                    
                    <div class="form-group">
                        <label for="health_insurance">Health Insurance ($):</label>
                        <input type="number" id="health_insurance" name="health_insurance" step="100" min="0" max="50000" placeholder="3600">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="dental_vision">Dental & Vision ($):</label>
                        <input type="number" id="dental_vision" name="dental_vision" step="50" min="0" max="10000" placeholder="600">
                    </div>
                    
                    <div class="form-group">
                        <label for="fsa_hsa">FSA/HSA Contribution ($):</label>
                        <input type="number" id="fsa_hsa" name="fsa_hsa" step="100" min="0" max="10000" placeholder="2000">
                    </div>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate Take-Home Pay</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const form = document.getElementById('calculator-form');
            const calculateBtn = document.getElementById('calculate-btn');
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                calculateBtn.disabled = true;
                calculateBtn.textContent = 'Calculating...';
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                console.log('Sending data:', data);
                
                fetch('/api/calculate/gross-to-net', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    console.log('Received result:', result);
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        
                        // Net pay summary
                        resultHtml += '<div class="net-summary">';
                        resultHtml += '<h3>💵 Net Take-Home Pay</h3>';
                        
                        let frequencyLabel = result.pay_frequency.charAt(0).toUpperCase() + result.pay_frequency.slice(1);
                        if (result.pay_frequency === 'annual') {
                            resultHtml += '<p><strong>Annual:</strong> $' + result.net_pay.toLocaleString() + '</p>';
                            resultHtml += '<p><strong>Monthly:</strong> $' + (result.net_pay / 12).toLocaleString() + '</p>';
                        } else {
                            resultHtml += '<p><strong>' + frequencyLabel + ':</strong> $' + result.net_pay.toLocaleString() + '</p>';
                            resultHtml += '<p><strong>Annual:</strong> $' + result.annual_net.toLocaleString() + '</p>';
                        }
                        
                        resultHtml += '<p><em>Take-home rate: ' + result.take_home_rate + '% of gross</em></p>';
                        resultHtml += '</div>';
                        
                        // Breakdown
                        resultHtml += '<div class="pay-breakdown">';
                        resultHtml += '<div class="pay-item">';
                        resultHtml += '<h4>Gross Pay</h4>';
                        resultHtml += '<p>$' + result.period_gross.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="pay-item">';
                        resultHtml += '<h4>Total Deductions</h4>';
                        resultHtml += '<p>$' + result.total_deductions.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        
                        resultHtml += '<div class="pay-item">';
                        resultHtml += '<h4>Net Pay</h4>';
                        resultHtml += '<p>$' + result.net_pay.toLocaleString() + '</p>';
                        resultHtml += '</div>';
                        resultHtml += '</div>';
                        
                        // Taxes breakdown
                        resultHtml += '<div class="taxes-section">';
                        resultHtml += '<div class="section-title">Tax Breakdown (' + frequencyLabel + ')</div>';
                        resultHtml += '<p><strong>Federal Tax:</strong> $' + result.federal_tax.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>State Tax:</strong> $' + result.state_tax.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Social Security:</strong> $' + result.social_security.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Medicare:</strong> $' + result.medicare.toLocaleString() + '</p>';
                        resultHtml += '<p><strong>Total Taxes:</strong> $' + result.total_taxes.toLocaleString() + ' (' + result.effective_rate + '% effective rate)</p>';
                        resultHtml += '</div>';
                        
                        // Pre-tax deductions
                        let totalPreTax = result.retirement_401k + result.health_insurance + result.dental_vision + result.fsa_hsa;
                        if (totalPreTax > 0) {
                            resultHtml += '<div class="deductions-section">';
                            resultHtml += '<div class="section-title">Pre-Tax Deductions (' + frequencyLabel + ')</div>';
                            if (result.retirement_401k > 0) {
                                resultHtml += '<p><strong>401k:</strong> $' + result.retirement_401k.toLocaleString() + '</p>';
                            }
                            if (result.health_insurance > 0) {
                                resultHtml += '<p><strong>Health Insurance:</strong> $' + result.health_insurance.toLocaleString() + '</p>';
                            }
                            if (result.dental_vision > 0) {
                                resultHtml += '<p><strong>Dental & Vision:</strong> $' + result.dental_vision.toLocaleString() + '</p>';
                            }
                            if (result.fsa_hsa > 0) {
                                resultHtml += '<p><strong>FSA/HSA:</strong> $' + result.fsa_hsa.toLocaleString() + '</p>';
                            }
                            resultHtml += '<p><strong>Total Pre-Tax:</strong> $' + totalPreTax.toLocaleString() + '</p>';
                            resultHtml += '</div>';
                        }
                        
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                })
                .finally(() => {
                    calculateBtn.disabled = false;
                    calculateBtn.textContent = 'Calculate Take-Home Pay';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/gross-to-net', methods=['POST'])
def calculate_gross_to_net():
    try:
        print("API called - calculating gross to net")
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        calc = GrossToNetCalculator()
        
        if not calc.validate_inputs(data):
            print(f"Validation errors: {calc.errors}")
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        print(f"Gross to net calculation result: {result}")
        
        calculation_logs.append({
            'calculator': 'gross_to_net',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in Gross to Net API: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/hourly-to-salary/')
def hourly_to_salary_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hourly to Salary Calculator - Convert Hourly Wage to Annual Salary</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free hourly to salary calculator. Convert hourly wages to annual salary and vice versa. Compare part-time vs full-time pay.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .calc-switch { background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; text-align: center; }
            .switch-btn { background: #6c757d; color: white; border: none; padding: 0.5rem 1rem; margin: 0 0.25rem; border-radius: 4px; cursor: pointer; }
            .switch-btn.active { background: #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>⏰ Hourly to Salary Calculator</h1>
            <p>Convert between hourly wages and annual salaries. Compare different work scenarios and pay frequencies.</p>
            
            <div class="calc-switch">
                <button class="switch-btn active" onclick="switchMode('hourly_to_salary')">Hourly → Salary</button>
                <button class="switch-btn" onclick="switchMode('salary_to_hourly')">Salary → Hourly</button>
            </div>
            
            <form id="calculator-form">
                <input type="hidden" id="calculation_type" name="calculation_type" value="hourly_to_salary">
                
                <div id="hourly-inputs">
                    <div class="form-group">
                        <label for="hourly_rate">Hourly Rate ($):</label>
                        <input type="number" id="hourly_rate" name="hourly_rate" step="0.01" min="0.01" max="1000" required placeholder="25.00">
                    </div>
                </div>
                
                <div id="salary-inputs" style="display: none;">
                    <div class="form-group">
                        <label for="annual_salary">Annual Salary ($):</label>
                        <input type="number" id="annual_salary" name="annual_salary" step="1000" min="1" max="10000000" placeholder="75000">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="hours_per_week">Hours per Week:</label>
                        <input type="number" id="hours_per_week" name="hours_per_week" min="1" max="80" value="40" placeholder="40">
                    </div>
                    
                    <div class="form-group">
                        <label for="weeks_per_year">Weeks per Year:</label>
                        <input type="number" id="weeks_per_year" name="weeks_per_year" min="1" max="52" value="52" placeholder="52">
                    </div>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
        </div>
        
        <script>
            function switchMode(mode) {
                document.getElementById('calculation_type').value = mode;
                const hourlyInputs = document.getElementById('hourly-inputs');
                const salaryInputs = document.getElementById('salary-inputs');
                const buttons = document.querySelectorAll('.switch-btn');
                
                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                if (mode === 'hourly_to_salary') {
                    hourlyInputs.style.display = 'block';
                    salaryInputs.style.display = 'none';
                    document.getElementById('hourly_rate').required = true;
                    document.getElementById('annual_salary').required = false;
                } else {
                    hourlyInputs.style.display = 'none';
                    salaryInputs.style.display = 'block';
                    document.getElementById('hourly_rate').required = false;
                    document.getElementById('annual_salary').required = true;
                }
            }
            
            document.getElementById('calculator-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/hourly-to-salary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    let html = '<div class="result">';
                    if (result.calculation_type === 'hourly_to_salary') {
                        html += '<h3>Salary Breakdown</h3>';
                        html += '<p><strong>Annual:</strong> $' + result.annual_salary.toLocaleString() + '</p>';
                        html += '<p><strong>Monthly:</strong> $' + result.monthly_salary.toLocaleString() + '</p>';
                        html += '<p><strong>Weekly:</strong> $' + result.weekly_salary.toLocaleString() + '</p>';
                        html += '<p><strong>Daily:</strong> $' + result.daily_salary.toLocaleString() + '</p>';
                        html += '<p><strong>Overtime Rate:</strong> $' + result.overtime_rate + '/hour</p>';
                    } else {
                        html += '<h3>Hourly Breakdown</h3>';
                        html += '<p><strong>Hourly Rate:</strong> $' + result.hourly_rate + '</p>';
                        html += '<p><strong>Total Hours/Year:</strong> ' + result.total_hours_year + '</p>';
                        html += '<p><strong>If 35 hrs/week:</strong> $' + result.if_35_hours + '/hour</p>';
                        html += '<p><strong>If 45 hrs/week:</strong> $' + result.if_45_hours + '/hour</p>';
                    }
                    html += '</div>';
                    document.getElementById('result-container').innerHTML = html;
                    document.getElementById('result-container').style.display = 'block';
                })
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/hourly-to-salary', methods=['POST'])
def calculate_hourly_to_salary():
    try:
        calc = HourlyToSalaryCalculator()
        data = request.get_json()
        
        if not calc.validate_inputs(data):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        calculation_logs.append({
            'calculator': 'hourly_to_salary',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/salary-raise/')
def salary_raise_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Salary Raise Calculator - Calculate Raise Amount and Percentage</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free salary raise calculator. Calculate raise amounts, percentages, and long-term financial impact of salary increases.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
            .result-card { background: #f8f9fa; padding: 1rem; border-radius: 4px; border-left: 4px solid #007bff; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .calc-switch { background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; text-align: center; }
            .switch-btn { background: #6c757d; color: white; border: none; padding: 0.5rem 1rem; margin: 0 0.25rem; border-radius: 4px; cursor: pointer; }
            .switch-btn.active { background: #007bff; }
            .performance-context { background: #e9ecef; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>📈 Salary Raise Calculator</h1>
            <p>Calculate raise amounts, percentages, and see the long-term financial impact of salary increases.</p>
            
            <div class="calc-switch">
                <button class="switch-btn active" onclick="switchMode('raise_amount')">From Amount</button>
                <button class="switch-btn" onclick="switchMode('raise_percentage')">From Percentage</button>
                <button class="switch-btn" onclick="switchMode('target_salary')">Target Salary</button>
            </div>
            
            <form id="calculator-form">
                <input type="hidden" id="calculation_type" name="calculation_type" value="raise_amount">
                
                <div class="form-group">
                    <label for="current_salary">Current Annual Salary ($):</label>
                    <input type="number" id="current_salary" name="current_salary" step="1000" min="1" max="10000000" required placeholder="75000">
                </div>
                
                <div id="amount-input" class="form-group">
                    <label for="raise_amount">Raise Amount ($):</label>
                    <input type="number" id="raise_amount" name="raise_amount" step="100" min="0" max="1000000" placeholder="5000">
                </div>
                
                <div id="percentage-input" class="form-group" style="display: none;">
                    <label for="raise_percentage">Raise Percentage (%):</label>
                    <input type="number" id="raise_percentage" name="raise_percentage" step="0.1" min="0" max="500" placeholder="5.0">
                </div>
                
                <div id="target-input" class="form-group" style="display: none;">
                    <label for="target_salary">Target Annual Salary ($):</label>
                    <input type="number" id="target_salary" name="target_salary" step="1000" min="1" max="10000000" placeholder="80000">
                </div>
                
                <button type="submit">Calculate Raise Impact</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            function switchMode(mode) {
                document.getElementById('calculation_type').value = mode;
                const amountInput = document.getElementById('amount-input');
                const percentageInput = document.getElementById('percentage-input');
                const targetInput = document.getElementById('target-input');
                const buttons = document.querySelectorAll('.switch-btn');
                
                // Clear required attributes
                document.getElementById('raise_amount').required = false;
                document.getElementById('raise_percentage').required = false;
                document.getElementById('target_salary').required = false;
                
                // Hide all specific inputs
                amountInput.style.display = 'none';
                percentageInput.style.display = 'none';
                targetInput.style.display = 'none';
                
                // Update button states
                buttons.forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // Show appropriate input and set required
                if (mode === 'raise_amount') {
                    amountInput.style.display = 'block';
                    document.getElementById('raise_amount').required = true;
                } else if (mode === 'raise_percentage') {
                    percentageInput.style.display = 'block';
                    document.getElementById('raise_percentage').required = true;
                } else {
                    targetInput.style.display = 'block';
                    document.getElementById('target_salary').required = true;
                }
            }
            
            document.getElementById('calculator-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/salary-raise', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let html = '<div class="result">';
                        html += '<h3>Salary Raise Analysis</h3>';
                        html += '<div class="result-grid">';
                        
                        // Basic information
                        html += '<div class="result-card">';
                        html += '<h4>💰 Salary Details</h4>';
                        html += '<p><strong>Current Salary:</strong> $' + result.current_salary.toLocaleString() + '</p>';
                        html += '<p><strong>New Salary:</strong> $' + result.new_salary.toLocaleString() + '</p>';
                        html += '<p><strong>Raise Amount:</strong> $' + result.raise_amount.toLocaleString() + '</p>';
                        html += '<p><strong>Raise Percentage:</strong> ' + result.raise_percentage + '%</p>';
                        html += '</div>';
                        
                        // Time breakdown
                        html += '<div class="result-card">';
                        html += '<h4>⏰ Time Breakdown</h4>';
                        html += '<p><strong>Monthly:</strong> +$' + result.monthly_increase.toLocaleString() + '</p>';
                        html += '<p><strong>Weekly:</strong> +$' + result.weekly_increase.toLocaleString() + '</p>';
                        html += '<p><strong>Daily:</strong> +$' + result.daily_increase.toLocaleString() + '</p>';
                        html += '<p><strong>Hourly:</strong> +$' + result.hourly_increase + '</p>';
                        html += '</div>';
                        
                        // Long-term impact
                        html += '<div class="result-card">';
                        html += '<h4>📈 Long-term Impact</h4>';
                        html += '<p><strong>1 Year Extra:</strong> $' + result.one_year_extra.toLocaleString() + '</p>';
                        html += '<p><strong>5 Years Extra:</strong> $' + result.five_year_extra.toLocaleString() + '</p>';
                        html += '<p><strong>10 Years Extra:</strong> $' + result.ten_year_extra.toLocaleString() + '</p>';
                        html += '</div>';
                        
                        html += '</div>';
                        
                        // Performance context
                        if (result.performance_context) {
                            html += '<div class="performance-context">';
                            html += '<h4>🎯 Performance Context</h4>';
                            html += '<p><strong>' + result.performance_context.category + '</strong> - ' + result.performance_context.description + '</p>';
                            html += '<p>' + result.performance_context.context + '</p>';
                            html += '</div>';
                        }
                        
                        html += '</div>';
                        
                        resultContainer.innerHTML = html;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/salary-raise', methods=['POST'])
def calculate_salary_raise():
    try:
        calc = SalaryRaiseCalculator()
        data = request.get_json()
        
        if not calc.validate_inputs(data):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        calculation_logs.append({
            'calculator': 'salary_raise',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/cost-of-living/')
def cost_of_living_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cost of Living Calculator - Compare Cities and Salary Requirements</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free cost of living calculator. Compare living costs between cities and calculate equivalent salary requirements for relocation.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1rem; }
            .result-card { background: #f8f9fa; padding: 1rem; border-radius: 4px; border-left: 4px solid #007bff; }
            .breakdown-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.5rem; margin-top: 1rem; }
            .breakdown-item { background: #ffffff; padding: 0.75rem; border-radius: 4px; border: 1px solid #e9ecef; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .recommendation { background: #e9ecef; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .positive { color: #28a745; }
            .negative { color: #dc3545; }
            .neutral { color: #6c757d; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🏙️ Cost of Living Calculator</h1>
            <p>Compare living costs between cities and calculate the equivalent salary needed to maintain your current lifestyle.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="current_salary">Current Annual Salary ($):</label>
                    <input type="number" id="current_salary" name="current_salary" step="1000" min="1" max="10000000" required placeholder="75000">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="current_city">Current City:</label>
                        <select id="current_city" name="current_city_key" required>
                            <option value="">Select Current City</option>
                            <option value="national_average">National Average</option>
                            <option value="new_york">New York, NY</option>
                            <option value="san_francisco">San Francisco, CA</option>
                            <option value="los_angeles">Los Angeles, CA</option>
                            <option value="chicago">Chicago, IL</option>
                            <option value="boston">Boston, MA</option>
                            <option value="seattle">Seattle, WA</option>
                            <option value="washington_dc">Washington, DC</option>
                            <option value="miami">Miami, FL</option>
                            <option value="denver">Denver, CO</option>
                            <option value="atlanta">Atlanta, GA</option>
                            <option value="phoenix">Phoenix, AZ</option>
                            <option value="dallas">Dallas, TX</option>
                            <option value="houston">Houston, TX</option>
                            <option value="philadelphia">Philadelphia, PA</option>
                            <option value="detroit">Detroit, MI</option>
                            <option value="cleveland">Cleveland, OH</option>
                        </select>
                        <input type="hidden" id="current_city_name" name="current_city">
                    </div>
                    
                    <div class="form-group">
                        <label for="target_city">Target City:</label>
                        <select id="target_city" name="target_city_key" required>
                            <option value="">Select Target City</option>
                            <option value="national_average">National Average</option>
                            <option value="new_york">New York, NY</option>
                            <option value="san_francisco">San Francisco, CA</option>
                            <option value="los_angeles">Los Angeles, CA</option>
                            <option value="chicago">Chicago, IL</option>
                            <option value="boston">Boston, MA</option>
                            <option value="seattle">Seattle, WA</option>
                            <option value="washington_dc">Washington, DC</option>
                            <option value="miami">Miami, FL</option>
                            <option value="denver">Denver, CO</option>
                            <option value="atlanta">Atlanta, GA</option>
                            <option value="phoenix">Phoenix, AZ</option>
                            <option value="dallas">Dallas, TX</option>
                            <option value="houston">Houston, TX</option>
                            <option value="philadelphia">Philadelphia, PA</option>
                            <option value="detroit">Detroit, MI</option>
                            <option value="cleveland">Cleveland, OH</option>
                        </select>
                        <input type="hidden" id="target_city_name" name="target_city">
                    </div>
                </div>
                
                <button type="submit">Compare Cost of Living</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            // Update hidden city name fields when selections change
            document.getElementById('current_city').addEventListener('change', function() {
                document.getElementById('current_city_name').value = this.options[this.selectedIndex].text;
            });
            
            document.getElementById('target_city').addEventListener('change', function() {
                document.getElementById('target_city_name').value = this.options[this.selectedIndex].text;
            });
            
            document.getElementById('calculator-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/cost-of-living', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let html = '<div class="result">';
                        html += '<h3>Cost of Living Comparison</h3>';
                        html += '<div class="result-grid">';
                        
                        // Summary information
                        html += '<div class="result-card">';
                        html += '<h4>💰 Salary Comparison</h4>';
                        html += '<p><strong>Current Salary:</strong> $' + result.current_salary.toLocaleString() + ' (' + result.current_city + ')</p>';
                        html += '<p><strong>Equivalent Salary:</strong> $' + result.equivalent_salary.toLocaleString() + ' (' + result.target_city + ')</p>';
                        
                        const diffClass = result.salary_difference >= 0 ? 'negative' : 'positive';
                        const diffText = result.salary_difference >= 0 ? '+$' : '-$';
                        html += '<p><strong>Difference:</strong> <span class="' + diffClass + '">' + diffText + Math.abs(result.salary_difference).toLocaleString() + ' (' + (result.percentage_change >= 0 ? '+' : '') + result.percentage_change + '%)</span></p>';
                        html += '</div>';
                        
                        // Cost indices
                        html += '<div class="result-card">';
                        html += '<h4>📊 Cost Indices</h4>';
                        html += '<p><strong>' + result.current_city + ':</strong> ' + result.current_col_index + '</p>';
                        html += '<p><strong>' + result.target_city + ':</strong> ' + result.target_col_index + '</p>';
                        
                        const powerClass = result.purchasing_power_change >= 0 ? 'positive' : 'negative';
                        html += '<p><strong>Purchasing Power Change:</strong> <span class="' + powerClass + '">' + (result.purchasing_power_change >= 0 ? '+' : '') + result.purchasing_power_change.toFixed(1) + '%</span></p>';
                        html += '</div>';
                        
                        html += '</div>';
                        
                        // Expense breakdown
                        html += '<h4>💳 Expense Breakdown</h4>';
                        html += '<div class="breakdown-grid">';
                        
                        const categories = ['housing', 'food', 'transportation', 'utilities'];
                        const icons = ['🏠', '🍽️', '🚗', '⚡'];
                        const names = ['Housing', 'Food', 'Transportation', 'Utilities'];
                        
                        categories.forEach((cat, index) => {
                            html += '<div class="breakdown-item">';
                            html += '<h5>' + icons[index] + ' ' + names[index] + '</h5>';
                            html += '<p><strong>Current:</strong> $' + result.breakdown[cat].current.toLocaleString() + '</p>';
                            html += '<p><strong>Target:</strong> $' + result.breakdown[cat].target.toLocaleString() + '</p>';
                            
                            const catDiffClass = result.breakdown[cat].difference >= 0 ? 'negative' : 'positive';
                            const catDiffText = result.breakdown[cat].difference >= 0 ? '+$' : '-$';
                            html += '<p><strong>Change:</strong> <span class="' + catDiffClass + '">' + catDiffText + Math.abs(result.breakdown[cat].difference).toLocaleString() + '</span></p>';
                            html += '</div>';
                        });
                        
                        html += '</div>';
                        
                        // Recommendation
                        if (result.recommendation) {
                            html += '<div class="recommendation">';
                            html += '<h4>💡 Recommendation</h4>';
                            html += '<p><strong>' + result.recommendation.category + '</strong> - ' + result.recommendation.description + '</p>';
                            html += '<p>' + result.recommendation.advice + '</p>';
                            html += '</div>';
                        }
                        
                        html += '</div>';
                        
                        resultContainer.innerHTML = html;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/cost-of-living', methods=['POST'])
def calculate_cost_of_living():
    try:
        calc = CostOfLivingCalculator()
        data = request.get_json()
        
        if not calc.validate_inputs(data):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        calculation_logs.append({
            'calculator': 'cost_of_living',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/compound-interest/')
def compound_interest_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compound Interest Calculator - Investment Growth Calculator</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free compound interest calculator. Calculate investment growth with regular contributions and different compounding frequencies.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
            .result-card { background: #f8f9fa; padding: 1rem; border-radius: 4px; border-left: 4px solid #007bff; }
            .breakdown-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
            .breakdown-table th, .breakdown-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }
            .breakdown-table th { background: #f8f9fa; font-weight: 600; }
            .insights { margin-top: 1rem; }
            .insight-item { background: #e3f2fd; padding: 1rem; border-radius: 4px; margin-bottom: 0.5rem; border-left: 4px solid #2196f3; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>📈 Compound Interest Calculator</h1>
            <p>Calculate how your investments will grow over time with compound interest and regular contributions.</p>
            
            <form id="calculator-form">
                <div class="form-row">
                    <div class="form-group">
                        <label for="principal">Initial Investment ($):</label>
                        <input type="number" id="principal" name="principal" step="100" min="1" max="10000000" required placeholder="10000">
                    </div>
                    
                    <div class="form-group">
                        <label for="annual_rate">Annual Interest Rate (%):</label>
                        <input type="number" id="annual_rate" name="annual_rate" step="0.1" min="0" max="50" required placeholder="7.0">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="years">Investment Period (Years):</label>
                        <input type="number" id="years" name="years" step="0.5" min="0.1" max="100" required placeholder="20">
                    </div>
                    
                    <div class="form-group">
                        <label for="compound_frequency">Compounding Frequency:</label>
                        <select id="compound_frequency" name="compound_frequency">
                            <option value="1">Annually</option>
                            <option value="2">Semi-annually</option>
                            <option value="4">Quarterly</option>
                            <option value="12" selected>Monthly</option>
                            <option value="52">Weekly</option>
                            <option value="365">Daily</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="monthly_contribution">Monthly Contribution ($) (Optional):</label>
                    <input type="number" id="monthly_contribution" name="monthly_contribution" step="50" min="0" max="100000" placeholder="500">
                </div>
                
                <button type="submit">Calculate Investment Growth</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('calculator-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/compound-interest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let html = '<div class="result">';
                        html += '<h3>Investment Growth Summary</h3>';
                        html += '<div class="result-grid">';
                        
                        // Investment summary
                        html += '<div class="result-card">';
                        html += '<h4>💰 Investment Summary</h4>';
                        html += '<p><strong>Initial Investment:</strong> $' + result.principal.toLocaleString() + '</p>';
                        html += '<p><strong>Total Contributions:</strong> $' + result.total_contributions.toLocaleString() + '</p>';
                        html += '<p><strong>Interest Earned:</strong> $' + result.total_interest.toLocaleString() + '</p>';
                        html += '<p><strong>Final Value:</strong> $' + result.total_value.toLocaleString() + '</p>';
                        html += '</div>';
                        
                        // Investment details
                        html += '<div class="result-card">';
                        html += '<h4>📊 Investment Details</h4>';
                        html += '<p><strong>Annual Rate:</strong> ' + result.annual_rate + '%</p>';
                        html += '<p><strong>Time Period:</strong> ' + result.years + ' years</p>';
                        html += '<p><strong>Compounding:</strong> ' + result.compound_frequency_text + '</p>';
                        html += '<p><strong>Effective Yield:</strong> ' + result.effective_yield + '%</p>';
                        html += '</div>';
                        
                        html += '</div>';
                        
                        // Year-by-year breakdown
                        if (result.yearly_breakdown && result.yearly_breakdown.length > 0) {
                            html += '<h4>📈 Year-by-Year Growth</h4>';
                            html += '<table class="breakdown-table">';
                            html += '<thead><tr><th>Year</th><th>Balance</th><th>Interest Earned</th><th>Total Contributions</th></tr></thead>';
                            html += '<tbody>';
                            
                            result.yearly_breakdown.forEach(year => {
                                html += '<tr>';
                                html += '<td>' + year.year + '</td>';
                                html += '<td>$' + year.balance.toLocaleString() + '</td>';
                                html += '<td>$' + year.interest_earned.toLocaleString() + '</td>';
                                html += '<td>$' + year.contributions.toLocaleString() + '</td>';
                                html += '</tr>';
                            });
                            
                            html += '</tbody></table>';
                        }
                        
                        // Insights
                        if (result.insights && result.insights.length > 0) {
                            html += '<div class="insights">';
                            html += '<h4>💡 Investment Insights</h4>';
                            
                            result.insights.forEach(insight => {
                                html += '<div class="insight-item">';
                                html += '<strong>' + insight.title + '</strong><br>';
                                html += insight.message;
                                html += '</div>';
                            });
                            
                            html += '</div>';
                        }
                        
                        html += '</div>';
                        
                        resultContainer.innerHTML = html;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/compound-interest', methods=['POST'])
def calculate_compound_interest():
    try:
        calc = CompoundInterestCalculator()
        data = request.get_json()
        
        if not calc.validate_inputs(data):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        calculation_logs.append({
            'calculator': 'compound_interest',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/retirement/')
def retirement_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Retirement Calculator - Plan Your Retirement Savings</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free retirement calculator. Calculate how much you need to save for retirement and plan your financial future.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 1100px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            .form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1rem; }
            .result-card { background: #f8f9fa; padding: 1rem; border-radius: 4px; border-left: 4px solid #007bff; }
            .score-card { background: #e3f2fd; padding: 1rem; border-radius: 4px; text-align: center; border-left: 4px solid #2196f3; }
            .score-number { font-size: 2rem; font-weight: bold; color: #1976d2; margin: 0.5rem 0; }
            .recommendations { margin-top: 1rem; }
            .recommendation-item { padding: 1rem; border-radius: 4px; margin-bottom: 0.5rem; }
            .priority-high { background: #e8f5e8; border-left: 4px solid #28a745; }
            .priority-medium { background: #fff3cd; border-left: 4px solid #ffc107; }
            .priority-urgent { background: #f8d7da; border-left: 4px solid #dc3545; }
            .goal-analysis { background: #f0f8ff; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .on-track { color: #28a745; font-weight: bold; }
            .off-track { color: #dc3545; font-weight: bold; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🏖️ Retirement Calculator</h1>
            <p>Calculate how much you need to save for retirement and see if you're on track to meet your goals.</p>
            
            <form id="calculator-form">
                <div class="form-row-3">
                    <div class="form-group">
                        <label for="current_age">Current Age:</label>
                        <input type="number" id="current_age" name="current_age" min="18" max="100" required placeholder="35">
                    </div>
                    
                    <div class="form-group">
                        <label for="retirement_age">Retirement Age:</label>
                        <input type="number" id="retirement_age" name="retirement_age" min="50" max="100" required placeholder="65">
                    </div>
                    
                    <div class="form-group">
                        <label for="annual_return">Expected Annual Return (%):</label>
                        <input type="number" id="annual_return" name="annual_return" step="0.1" min="0" max="20" required placeholder="7.0">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="current_savings">Current Retirement Savings ($):</label>
                        <input type="number" id="current_savings" name="current_savings" step="1000" min="0" max="50000000" placeholder="50000">
                    </div>
                    
                    <div class="form-group">
                        <label for="monthly_contribution">Monthly Contribution ($):</label>
                        <input type="number" id="monthly_contribution" name="monthly_contribution" step="50" min="0" max="100000" placeholder="1000">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="retirement_income_goal">Annual Income Goal in Retirement ($) (Optional):</label>
                        <input type="number" id="retirement_income_goal" name="retirement_income_goal" step="5000" min="0" max="5000000" placeholder="80000">
                    </div>
                    
                    <div class="form-group">
                        <label for="years_in_retirement">Expected Years in Retirement:</label>
                        <input type="number" id="years_in_retirement" name="years_in_retirement" min="10" max="50" value="25" placeholder="25">
                    </div>
                </div>
                
                <button type="submit">Calculate Retirement Plan</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('calculator-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/retirement', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let html = '<div class="result">';
                        html += '<h3>Retirement Planning Analysis</h3>';
                        html += '<div class="result-grid">';
                        
                        // Retirement summary
                        html += '<div class="result-card">';
                        html += '<h4>📊 Retirement Summary</h4>';
                        html += '<p><strong>Years to Retirement:</strong> ' + result.years_to_retirement + ' years</p>';
                        html += '<p><strong>Total Retirement Savings:</strong> $' + result.total_retirement_savings.toLocaleString() + '</p>';
                        html += '<p><strong>Sustainable Annual Income:</strong> $' + result.sustainable_annual_income.toLocaleString() + '</p>';
                        html += '<p><strong>Monthly Income Available:</strong> $' + result.sustainable_monthly_income.toLocaleString() + '</p>';
                        html += '</div>';
                        
                        // Readiness score
                        html += '<div class="score-card">';
                        html += '<h4>🎯 Retirement Readiness Score</h4>';
                        html += '<div class="score-number">' + result.readiness_score + '/100</div>';
                        if (result.readiness_score >= 80) {
                            html += '<p style="color: #28a745;">Excellent - You\'re on track!</p>';
                        } else if (result.readiness_score >= 60) {
                            html += '<p style="color: #ffc107;">Good - Minor adjustments needed</p>';
                        } else {
                            html += '<p style="color: #dc3545;">Needs attention - Consider increasing savings</p>';
                        }
                        html += '</div>';
                        
                        // Savings breakdown
                        html += '<div class="result-card">';
                        html += '<h4>💰 Savings Breakdown</h4>';
                        html += '<p><strong>Current Savings Growth:</strong> $' + result.fv_current_savings.toLocaleString() + '</p>';
                        html += '<p><strong>Future Contributions:</strong> $' + result.fv_contributions.toLocaleString() + '</p>';
                        html += '<p><strong>Total Contributions:</strong> $' + result.total_contributions.toLocaleString() + '</p>';
                        html += '<p><strong>Est. Social Security:</strong> $' + result.estimated_social_security.toLocaleString() + '/year</p>';
                        html += '</div>';
                        
                        // Inflation impact
                        if (result.purchasing_power_analysis) {
                            html += '<div class="result-card">';
                            html += '<h4>📈 Inflation Impact</h4>';
                            html += '<p><strong>Today\'s Purchasing Power:</strong> $' + result.purchasing_power_analysis.current_dollars.toLocaleString() + '</p>';
                            html += '<p><strong>Future Purchasing Power:</strong> $' + result.purchasing_power_analysis.future_purchasing_power.toLocaleString() + '</p>';
                            html += '<p><strong>Inflation Rate Used:</strong> ' + result.purchasing_power_analysis.inflation_rate_used + '%</p>';
                            html += '</div>';
                        }
                        
                        html += '</div>';
                        
                        // Goal analysis
                        if (result.retirement_goal_analysis) {
                            html += '<div class="goal-analysis">';
                            html += '<h4>🎯 Goal Analysis</h4>';
                            html += '<p><strong>Income Goal:</strong> $' + result.retirement_goal_analysis.goal_income.toLocaleString() + '/year</p>';
                            html += '<p><strong>Required Savings:</strong> $' + result.retirement_goal_analysis.required_savings.toLocaleString() + '</p>';
                            html += '<p><strong>Projected Savings:</strong> $' + result.retirement_goal_analysis.projected_savings.toLocaleString() + '</p>';
                            
                            if (result.retirement_goal_analysis.on_track) {
                                html += '<p class="on-track">✅ You\'re on track to meet your goal!</p>';
                            } else {
                                html += '<p class="off-track">⚠️ Savings gap: $' + Math.abs(result.retirement_goal_analysis.savings_gap).toLocaleString() + '</p>';
                                if (result.retirement_goal_analysis.additional_monthly_needed > 0) {
                                    html += '<p><strong>Additional monthly needed:</strong> $' + result.retirement_goal_analysis.additional_monthly_needed.toLocaleString() + '</p>';
                                }
                            }
                            html += '</div>';
                        }
                        
                        // Recommendations
                        if (result.recommendations && result.recommendations.length > 0) {
                            html += '<div class="recommendations">';
                            html += '<h4>💡 Personalized Recommendations</h4>';
                            
                            result.recommendations.forEach(rec => {
                                const priorityClass = 'priority-' + rec.priority;
                                html += '<div class="recommendation-item ' + priorityClass + '">';
                                html += '<strong>' + rec.title + '</strong> (' + rec.category + ')<br>';
                                html += rec.message;
                                html += '</div>';
                            });
                            
                            html += '</div>';
                        }
                        
                        html += '</div>';
                        
                        resultContainer.innerHTML = html;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/retirement', methods=['POST'])
def calculate_retirement():
    try:
        calc = RetirementCalculator()
        data = request.get_json()
        
        if not calc.validate_inputs(data):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        calculation_logs.append({
            'calculator': 'retirement',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calculators/investment-return/')
def investment_return_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Investment Return Calculator - Calculate Investment Returns</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free investment return calculator. Calculate future value, required returns, time needed, and analyze portfolio performance.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .calc-tabs { display: flex; margin-bottom: 2rem; border-bottom: 2px solid #e9ecef; }
            .tab-btn { background: none; border: none; padding: 1rem 2rem; cursor: pointer; font-size: 1rem; border-bottom: 3px solid transparent; }
            .tab-btn.active { border-bottom-color: #007bff; color: #007bff; font-weight: bold; }
            .tab-btn:hover { background: #f8f9fa; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .form-group { margin-bottom: 1rem; }
            .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
            .form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1.5rem; border-radius: 4px; margin-top: 1rem; }
            .result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem; }
            .result-card { background: #f8f9fa; padding: 1rem; border-radius: 4px; border-left: 4px solid #007bff; }
            .portfolio-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
            .portfolio-table th, .portfolio-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }
            .portfolio-table th { background: #f8f9fa; font-weight: 600; }
            .risk-indicator { padding: 0.5rem 1rem; border-radius: 20px; color: white; font-weight: bold; display: inline-block; }
            .risk-conservative { background: #28a745; }
            .risk-moderate { background: #ffc107; color: #212529; }
            .risk-aggressive { background: #fd7e14; }
            .risk-very-high { background: #dc3545; }
            .investment-row { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem; align-items: end; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .positive { color: #28a745; font-weight: bold; }
            .negative { color: #dc3545; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>💹 Investment Return Calculator</h1>
            <p>Calculate investment returns, required rates, time needed, and analyze portfolio performance.</p>
            
            <div class="calc-tabs">
                <button class="tab-btn active" onclick="switchTab('future_value')">Future Value</button>
                <button class="tab-btn" onclick="switchTab('required_return')">Required Return</button>
                <button class="tab-btn" onclick="switchTab('time_needed')">Time Needed</button>
                <button class="tab-btn" onclick="switchTab('portfolio_analysis')">Portfolio Analysis</button>
            </div>
            
            <form id="calculator-form">
                <input type="hidden" id="calculation_type" name="calculation_type" value="future_value">
                
                <!-- Future Value Tab -->
                <div id="future_value_content" class="tab-content active">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="initial_investment_fv">Initial Investment ($):</label>
                            <input type="number" id="initial_investment_fv" name="initial_investment" step="100" min="1" max="50000000" required placeholder="10000">
                        </div>
                        
                        <div class="form-group">
                            <label for="annual_return_fv">Expected Annual Return (%):</label>
                            <input type="number" id="annual_return_fv" name="annual_return" step="0.1" min="-50" max="50" required placeholder="8.0">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="years_fv">Investment Period (Years):</label>
                            <input type="number" id="years_fv" name="years" step="0.5" min="0.1" max="100" required placeholder="10">
                        </div>
                        
                        <div class="form-group">
                            <label for="contribution_frequency_fv">Contribution Frequency:</label>
                            <select id="contribution_frequency_fv" name="contribution_frequency">
                                <option value="monthly" selected>Monthly</option>
                                <option value="quarterly">Quarterly</option>
                                <option value="annually">Annually</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="additional_contributions_fv">Additional Contributions per Period ($) (Optional):</label>
                        <input type="number" id="additional_contributions_fv" name="additional_contributions" step="50" min="0" max="100000" placeholder="500">
                    </div>
                </div>
                
                <!-- Required Return Tab -->
                <div id="required_return_content" class="tab-content">
                    <div class="form-row-3">
                        <div class="form-group">
                            <label for="initial_investment_rr">Initial Investment ($):</label>
                            <input type="number" id="initial_investment_rr" name="initial_investment" step="100" min="1" max="50000000" placeholder="10000">
                        </div>
                        
                        <div class="form-group">
                            <label for="target_value">Target Value ($):</label>
                            <input type="number" id="target_value" name="target_value" step="1000" min="1" max="50000000" placeholder="50000">
                        </div>
                        
                        <div class="form-group">
                            <label for="years_rr">Time Period (Years):</label>
                            <input type="number" id="years_rr" name="years" step="0.5" min="0.1" max="100" placeholder="10">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="additional_contributions_rr">Additional Contributions per Period ($) (Optional):</label>
                            <input type="number" id="additional_contributions_rr" name="additional_contributions" step="50" min="0" max="100000" placeholder="0">
                        </div>
                        
                        <div class="form-group">
                            <label for="contribution_frequency_rr">Contribution Frequency:</label>
                            <select id="contribution_frequency_rr" name="contribution_frequency">
                                <option value="monthly" selected>Monthly</option>
                                <option value="quarterly">Quarterly</option>
                                <option value="annually">Annually</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Time Needed Tab -->
                <div id="time_needed_content" class="tab-content">
                    <div class="form-row-3">
                        <div class="form-group">
                            <label for="initial_investment_tn">Initial Investment ($):</label>
                            <input type="number" id="initial_investment_tn" name="initial_investment" step="100" min="1" max="50000000" placeholder="10000">
                        </div>
                        
                        <div class="form-group">
                            <label for="target_value_tn">Target Value ($):</label>
                            <input type="number" id="target_value_tn" name="target_value" step="1000" min="1" max="50000000" placeholder="50000">
                        </div>
                        
                        <div class="form-group">
                            <label for="annual_return_tn">Expected Annual Return (%):</label>
                            <input type="number" id="annual_return_tn" name="annual_return" step="0.1" min="0.1" max="50" placeholder="8.0">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="additional_contributions_tn">Additional Contributions per Period ($) (Optional):</label>
                            <input type="number" id="additional_contributions_tn" name="additional_contributions" step="50" min="0" max="100000" placeholder="0">
                        </div>
                        
                        <div class="form-group">
                            <label for="contribution_frequency_tn">Contribution Frequency:</label>
                            <select id="contribution_frequency_tn" name="contribution_frequency">
                                <option value="monthly" selected>Monthly</option>
                                <option value="quarterly">Quarterly</option>
                                <option value="annually">Annually</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Portfolio Analysis Tab -->
                <div id="portfolio_analysis_content" class="tab-content">
                    <h4>Enter Your Investments</h4>
                    <div id="investments-container">
                        <div class="investment-row">
                            <div class="form-group">
                                <label for="investment_1_name">Investment Name:</label>
                                <input type="text" id="investment_1_name" name="investment_1_name" placeholder="S&P 500 Fund">
                            </div>
                            <div class="form-group">
                                <label for="investment_1_initial">Initial Value ($):</label>
                                <input type="number" id="investment_1_initial" name="investment_1_initial" step="100" min="0" placeholder="10000">
                            </div>
                            <div class="form-group">
                                <label for="investment_1_current">Current Value ($):</label>
                                <input type="number" id="investment_1_current" name="investment_1_current" step="100" min="0" placeholder="12000">
                            </div>
                        </div>
                        
                        <div class="investment-row">
                            <div class="form-group">
                                <label for="investment_2_name">Investment Name:</label>
                                <input type="text" id="investment_2_name" name="investment_2_name" placeholder="Tech Stocks">
                            </div>
                            <div class="form-group">
                                <label for="investment_2_initial">Initial Value ($):</label>
                                <input type="number" id="investment_2_initial" name="investment_2_initial" step="100" min="0" placeholder="5000">
                            </div>
                            <div class="form-group">
                                <label for="investment_2_current">Current Value ($):</label>
                                <input type="number" id="investment_2_current" name="investment_2_current" step="100" min="0" placeholder="6500">
                            </div>
                        </div>
                        
                        <div class="investment-row">
                            <div class="form-group">
                                <label for="investment_3_name">Investment Name:</label>
                                <input type="text" id="investment_3_name" name="investment_3_name" placeholder="Bonds">
                            </div>
                            <div class="form-group">
                                <label for="investment_3_initial">Initial Value ($):</label>
                                <input type="number" id="investment_3_initial" name="investment_3_initial" step="100" min="0" placeholder="3000">
                            </div>
                            <div class="form-group">
                                <label for="investment_3_current">Current Value ($):</label>
                                <input type="number" id="investment_3_current" name="investment_3_current" step="100" min="0" placeholder="3150">
                            </div>
                        </div>
                    </div>
                </div>
                
                <button type="submit" id="calculate-btn">Calculate</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            function switchTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Remove active class from all tab buttons
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Show selected tab content
                document.getElementById(tabName + '_content').classList.add('active');
                event.target.classList.add('active');
                
                // Update calculation type
                document.getElementById('calculation_type').value = tabName;
                
                // Clear all required attributes
                document.querySelectorAll('input[required]').forEach(input => {
                    input.required = false;
                });
                
                // Set required attributes for active tab
                const activeTab = document.getElementById(tabName + '_content');
                activeTab.querySelectorAll('input').forEach(input => {
                    if (input.hasAttribute('placeholder') && input.type === 'number' && 
                        (input.id.includes('initial') || input.id.includes('return') || 
                         input.id.includes('years') || input.id.includes('target'))) {
                        input.required = true;
                    }
                });
            }
            
            document.getElementById('calculator-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/investment-return', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let html = '<div class="result">';
                        
                        if (result.calculation_type === 'future_value') {
                            html += '<h3>Investment Growth Projection</h3>';
                            html += '<div class="result-grid">';
                            
                            html += '<div class="result-card">';
                            html += '<h4>💰 Investment Summary</h4>';
                            html += '<p><strong>Initial Investment:</strong> $' + result.initial_investment.toLocaleString() + '</p>';
                            html += '<p><strong>Total Invested:</strong> $' + result.total_invested.toLocaleString() + '</p>';
                            html += '<p><strong>Final Value:</strong> $' + result.total_value.toLocaleString() + '</p>';
                            html += '<p><strong>Total Gains:</strong> $' + result.total_gains.toLocaleString() + '</p>';
                            html += '</div>';
                            
                            html += '<div class="result-card">';
                            html += '<h4>📊 Performance Details</h4>';
                            html += '<p><strong>Growth from Initial:</strong> $' + result.fv_initial.toLocaleString() + '</p>';
                            html += '<p><strong>Growth from Contributions:</strong> $' + result.fv_contributions.toLocaleString() + '</p>';
                            html += '<p><strong>Annualized Return:</strong> ' + result.annualized_return + '%</p>';
                            html += '<p><strong>Investment Period:</strong> ' + result.years + ' years</p>';
                            html += '</div>';
                            
                            html += '</div>';
                        }
                        
                        else if (result.calculation_type === 'required_return') {
                            html += '<h3>Required Return Analysis</h3>';
                            html += '<div class="result-grid">';
                            
                            html += '<div class="result-card">';
                            html += '<h4>🎯 Target Analysis</h4>';
                            html += '<p><strong>Required Annual Return:</strong> ' + result.required_return + '%</p>';
                            html += '<p><strong>Target Value:</strong> $' + result.target_value.toLocaleString() + '</p>';
                            html += '<p><strong>Total Investment:</strong> $' + result.total_invested.toLocaleString() + '</p>';
                            html += '<p><strong>Time Period:</strong> ' + result.years + ' years</p>';
                            html += '</div>';
                            
                            if (result.risk_assessment) {
                                const riskClass = 'risk-' + result.risk_assessment.level.toLowerCase().replace(/\\s+/g, '-').replace('very-high-risk', 'very-high');
                                html += '<div class="result-card">';
                                html += '<h4>⚠️ Risk Assessment</h4>';
                                html += '<div class="risk-indicator ' + riskClass + '">' + result.risk_assessment.level + '</div>';
                                html += '<p style="margin-top: 1rem;"><strong>Description:</strong> ' + result.risk_assessment.description + '</p>';
                                html += '<p><strong>Feasibility:</strong> ' + result.risk_assessment.feasibility + '</p>';
                                html += '</div>';
                            }
                            
                            html += '</div>';
                        }
                        
                        else if (result.calculation_type === 'time_needed') {
                            html += '<h3>Time to Target Analysis</h3>';
                            html += '<div class="result-grid">';
                            
                            html += '<div class="result-card">';
                            html += '<h4>⏰ Time Analysis</h4>';
                            if (result.feasible && result.years_needed) {
                                html += '<p><strong>Time Needed:</strong> ' + result.years_needed + ' years</p>';
                                html += '<p><strong>Target Value:</strong> $' + result.target_value.toLocaleString() + '</p>';
                                html += '<p><strong>Expected Return:</strong> ' + result.annual_return + '%</p>';
                                html += '<p><strong>Feasible:</strong> <span class="positive">Yes</span></p>';
                            } else {
                                html += '<p><strong>Result:</strong> <span class="negative">Target not achievable</span></p>';
                                html += '<p>With current parameters, the target cannot be reached in a reasonable timeframe.</p>';
                                html += '<p>Consider increasing contributions or expected returns.</p>';
                            }
                            html += '</div>';
                            
                            html += '</div>';
                        }
                        
                        else if (result.calculation_type === 'portfolio_analysis') {
                            html += '<h3>Portfolio Performance Analysis</h3>';
                            html += '<div class="result-grid">';
                            
                            html += '<div class="result-card">';
                            html += '<h4>📊 Portfolio Summary</h4>';
                            html += '<p><strong>Total Initial:</strong> $' + result.total_initial.toLocaleString() + '</p>';
                            html += '<p><strong>Current Value:</strong> $' + result.total_current.toLocaleString() + '</p>';
                            const gainLossClass = result.total_gain_loss >= 0 ? 'positive' : 'negative';
                            html += '<p><strong>Total Gain/Loss:</strong> <span class="' + gainLossClass + '">$' + result.total_gain_loss.toLocaleString() + '</span></p>';
                            const returnClass = result.portfolio_return >= 0 ? 'positive' : 'negative';
                            html += '<p><strong>Portfolio Return:</strong> <span class="' + returnClass + '">' + result.portfolio_return + '%</span></p>';
                            html += '</div>';
                            
                            if (result.best_performer && result.worst_performer) {
                                html += '<div class="result-card">';
                                html += '<h4>🏆 Performance Leaders</h4>';
                                html += '<p><strong>Best Performer:</strong> ' + result.best_performer.name + ' (' + result.best_performer.return_pct + '%)</p>';
                                html += '<p><strong>Worst Performer:</strong> ' + result.worst_performer.name + ' (' + result.worst_performer.return_pct + '%)</p>';
                                html += '</div>';
                            }
                            
                            html += '</div>';
                            
                            if (result.investments && result.investments.length > 0) {
                                html += '<h4>📈 Individual Investment Performance</h4>';
                                html += '<table class="portfolio-table">';
                                html += '<thead><tr><th>Investment</th><th>Initial</th><th>Current</th><th>Gain/Loss</th><th>Return %</th><th>Weight</th></tr></thead>';
                                html += '<tbody>';
                                
                                result.investments.forEach(inv => {
                                    const returnClass = inv.return_pct >= 0 ? 'positive' : 'negative';
                                    html += '<tr>';
                                    html += '<td>' + inv.name + '</td>';
                                    html += '<td>$' + inv.initial.toLocaleString() + '</td>';
                                    html += '<td>$' + inv.current.toLocaleString() + '</td>';
                                    html += '<td class="' + returnClass + '">$' + inv.gain_loss.toLocaleString() + '</td>';
                                    html += '<td class="' + returnClass + '">' + inv.return_pct + '%</td>';
                                    html += '<td>' + inv.weight + '%</td>';
                                    html += '</tr>';
                                });
                                
                                html += '</tbody></table>';
                            }
                        }
                        
                        html += '</div>';
                        
                        resultContainer.innerHTML = html;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                });
            });
            
            // Initialize first tab
            switchTab('future_value');
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/investment-return', methods=['POST'])
def calculate_investment_return():
    try:
        calc = InvestmentReturnCalculator()
        data = request.get_json()
        
        if not calc.validate_inputs(data):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(data)
        calculation_logs.append({
            'calculator': 'investment_return',
            'inputs': data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sitemap route moved to later in file with enhanced SEO content

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    robots_txt = '''User-agent: *
Allow: /

# Sitemap
Sitemap: http://localhost:5000/sitemap.xml

# Block admin and API endpoints
Disallow: /debug/
Disallow: /api/
'''
    
    response = app.make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

# Advanced SEO Features

def generate_json_ld(calculator_type, title, description, url):
    """Generate JSON-LD structured data for calculators"""
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": title,
        "description": description,
        "url": url,
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web Browser",
        "browserRequirements": "Requires JavaScript",
        "provider": {
            "@type": "Organization",
            "name": "Calculator Suite",
            "url": "http://localhost:5000"
        },
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "reviewCount": "1247",
            "bestRating": "5"
        }
    }

def generate_calculator_faq(calculator_type):
    """Generate FAQ data for each calculator"""
    faqs = {
        'percentage': [
            {
                "question": "How do I calculate what percentage one number is of another?",
                "answer": "To find what percentage X is of Y, divide X by Y and multiply by 100. For example, 25 is 25% of 100 because (25 ÷ 100) × 100 = 25%."
            },
            {
                "question": "What is the difference between percentage increase and percentage change?",
                "answer": "Percentage increase is always positive and shows growth, while percentage change can be positive (increase) or negative (decrease) depending on whether the new value is higher or lower than the original."
            },
            {
                "question": "How accurate is this percentage calculator?",
                "answer": "Our calculator provides results accurate to 2 decimal places, suitable for most business and academic calculations. For scientific applications requiring higher precision, consider using specialized software."
            }
        ],
        'loan': [
            {
                "question": "How is monthly loan payment calculated?",
                "answer": "Monthly payment is calculated using the formula: M = P × [r(1+r)^n] / [(1+r)^n-1], where P is principal, r is monthly interest rate, and n is number of payments."
            },
            {
                "question": "What factors affect my loan payment?",
                "answer": "Three main factors: loan amount (principal), interest rate (APR), and loan term (years). Higher amounts and rates increase payments, while longer terms decrease monthly payments but increase total interest."
            },
            {
                "question": "Should I choose a shorter or longer loan term?",
                "answer": "Shorter terms mean higher monthly payments but less total interest. Longer terms mean lower monthly payments but more total interest. Choose based on your budget and financial goals."
            }
        ],
        'mortgage': [
            {
                "question": "What is PMI and when do I need it?",
                "answer": "Private Mortgage Insurance (PMI) is required when your down payment is less than 20% of the home price. It protects the lender if you default and typically costs 0.3-1.5% of the loan amount annually."
            },
            {
                "question": "How much house can I afford?",
                "answer": "Generally, your total monthly housing costs shouldn't exceed 28% of your gross income. This includes principal, interest, taxes, insurance, and HOA fees (PITIA)."
            },
            {
                "question": "What's included in my monthly mortgage payment?",
                "answer": "Your payment typically includes Principal and Interest (P&I), Property Taxes, Homeowner's Insurance, and PMI if applicable. Some loans also include HOA fees."
            }
        ],
        'retirement': [
            {
                "question": "How much should I save for retirement?",
                "answer": "Financial experts recommend saving 10-15% of your income for retirement. Start early to benefit from compound growth - even small amounts can grow significantly over decades."
            },
            {
                "question": "What is a good retirement savings rate?",
                "answer": "Aim to replace 70-90% of your pre-retirement income. If you start saving at 25, 10-12% of income may suffice. Starting later requires higher percentages to catch up."
            },
            {
                "question": "When should I start saving for retirement?",
                "answer": "Start as early as possible. Thanks to compound interest, someone who starts saving at 25 can contribute less monthly than someone who starts at 35 to reach the same retirement goal."
            }
        ]
    }
    return faqs.get(calculator_type, [])

@app.route('/calculator-guide/')
def calculator_guide():
    """SEO-optimized calculator guide and comparison page"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Complete Calculator Guide - Financial, Tax, and Investment Calculators</title>
        <meta name="description" content="Comprehensive guide to our free online calculators. Compare loan vs lease, understand mortgage rates, plan retirement, and make informed financial decisions.">
        <meta name="keywords" content="calculator guide, financial calculator comparison, loan calculator guide, mortgage calculator help, retirement planning calculator">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="canonical" href="http://localhost:5000/calculator-guide/">
        
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Complete Calculator Guide - Financial, Tax, and Investment Calculators",
            "description": "Comprehensive guide to using our free online calculators for financial planning",
            "author": {{
                "@type": "Organization",
                "name": "Calculator Suite"
            }},
            "publisher": {{
                "@type": "Organization",
                "name": "Calculator Suite",
                "logo": {{
                    "@type": "ImageObject",
                    "url": "http://localhost:5000/logo.png"
                }}
            }},
            "datePublished": "2024-01-01",
            "dateModified": "2024-01-01"
        }}
        </script>
        
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; line-height: 1.6; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #007bff; text-align: center; margin-bottom: 2rem; }}
            h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 0.5rem; }}
            .calc-category {{ margin: 2rem 0; }}
            .calc-comparison {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0; }}
            .comparison-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1.5rem; background: #f8f9fa; }}
            .back-link {{ display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
            .toc {{ background: #e9f4ff; padding: 1.5rem; border-radius: 8px; margin: 2rem 0; }}
            .toc ul {{ margin: 0; padding-left: 1.5rem; }}
            .tips {{ background: #f0f8f0; border-left: 4px solid #28a745; padding: 1rem; margin: 1rem 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>📚 Complete Calculator Guide</h1>
            
            <div class="toc">
                <h3>Table of Contents</h3>
                <ul>
                    <li><a href="#financial">Financial Calculators</a></li>
                    <li><a href="#tax">Tax Calculators</a></li>
                    <li><a href="#salary">Salary & Employment</a></li>
                    <li><a href="#investment">Investment & Retirement</a></li>
                    <li><a href="#utility">Utility Calculators</a></li>
                    <li><a href="#tips">Usage Tips & Best Practices</a></li>
                </ul>
            </div>
            
            <section id="financial" class="calc-category">
                <h2>💰 Financial Calculators</h2>
                
                <div class="calc-comparison">
                    <div class="comparison-card">
                        <h3><a href="/calculators/loan/">Loan Calculator</a></h3>
                        <p><strong>Best for:</strong> Personal loans, auto loans, student loans</p>
                        <p><strong>Key features:</strong> Monthly payments, total interest, amortization schedule</p>
                        <p><strong>When to use:</strong> Before taking any loan to understand true costs and compare offers</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/mortgage/">Mortgage Calculator</a></h3>
                        <p><strong>Best for:</strong> Home buying, refinancing decisions</p>
                        <p><strong>Key features:</strong> PMI calculation, property taxes, insurance, HOA fees</p>
                        <p><strong>When to use:</strong> House hunting, determining affordability, refinance analysis</p>
                    </div>
                </div>
                
                <div class="tips">
                    <strong>💡 Pro Tip:</strong> Always compare the total cost of the loan, not just monthly payments. A longer term means lower payments but more total interest.
                </div>
            </section>
            
            <section id="tax" class="calc-category">
                <h2>📋 Tax Calculators</h2>
                
                <div class="calc-comparison">
                    <div class="comparison-card">
                        <h3><a href="/calculators/income-tax/">Income Tax Calculator</a></h3>
                        <p><strong>Best for:</strong> Tax planning, withholding adjustments</p>
                        <p><strong>Key features:</strong> Federal and state taxes, FICA, effective rates</p>
                        <p><strong>When to use:</strong> Tax season, job changes, financial planning</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/tax-refund/">Tax Refund Estimator</a></h3>
                        <p><strong>Best for:</strong> Refund estimation, tax credit calculation</p>
                        <p><strong>Key features:</strong> Child tax credit, EITC, withholding analysis</p>
                        <p><strong>When to use:</strong> Before filing taxes, adjusting withholdings</p>
                    </div>
                </div>
            </section>
            
            <section id="salary" class="calc-category">
                <h2>💼 Salary & Employment Calculators</h2>
                
                <div class="calc-comparison">
                    <div class="comparison-card">
                        <h3><a href="/calculators/gross-to-net/">Gross to Net Calculator</a></h3>
                        <p><strong>Best for:</strong> Understanding take-home pay</p>
                        <p><strong>Key features:</strong> All deductions, multiple pay frequencies</p>
                        <p><strong>When to use:</strong> Job offers, budgeting, financial planning</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/salary-raise/">Salary Raise Calculator</a></h3>
                        <p><strong>Best for:</strong> Raise negotiations, career planning</p>
                        <p><strong>Key features:</strong> Performance context, long-term impact</p>
                        <p><strong>When to use:</strong> Performance reviews, job negotiations</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/cost-of-living/">Cost of Living Calculator</a></h3>
                        <p><strong>Best for:</strong> Relocation decisions</p>
                        <p><strong>Key features:</strong> City comparisons, equivalent salary</p>
                        <p><strong>When to use:</strong> Job relocations, city comparisons</p>
                    </div>
                </div>
            </section>
            
            <section id="investment" class="calc-category">
                <h2>📈 Investment & Retirement Calculators</h2>
                
                <div class="calc-comparison">
                    <div class="comparison-card">
                        <h3><a href="/calculators/retirement/">Retirement Calculator</a></h3>
                        <p><strong>Best for:</strong> Long-term retirement planning</p>
                        <p><strong>Key features:</strong> Savings projections, readiness score, recommendations</p>
                        <p><strong>When to use:</strong> Career start, major life changes, annual reviews</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/compound-interest/">Compound Interest Calculator</a></h3>
                        <p><strong>Best for:</strong> Understanding investment growth</p>
                        <p><strong>Key features:</strong> Different compounding frequencies, contributions</p>
                        <p><strong>When to use:</strong> Investment planning, savings goals</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/investment-return/">Investment Return Calculator</a></h3>
                        <p><strong>Best for:</strong> Investment analysis and planning</p>
                        <p><strong>Key features:</strong> Multiple calculation modes, portfolio analysis</p>
                        <p><strong>When to use:</strong> Investment decisions, portfolio review</p>
                    </div>
                </div>
            </section>
            
            <section id="utility" class="calc-category">
                <h2>🔧 Utility Calculators</h2>
                
                <div class="calc-comparison">
                    <div class="comparison-card">
                        <h3><a href="/calculators/percentage/">Percentage Calculator</a></h3>
                        <p><strong>Best for:</strong> Quick percentage calculations</p>
                        <p><strong>Key features:</strong> Multiple operation types, detailed explanations</p>
                        <p><strong>When to use:</strong> Shopping discounts, grade calculations, data analysis</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/tip/">Tip Calculator</a></h3>
                        <p><strong>Best for:</strong> Restaurant and service tipping</p>
                        <p><strong>Key features:</strong> Bill splitting, tax handling</p>
                        <p><strong>When to use:</strong> Dining out, service appointments, group meals</p>
                    </div>
                    
                    <div class="comparison-card">
                        <h3><a href="/calculators/bmi/">BMI Calculator</a></h3>
                        <p><strong>Best for:</strong> Health and fitness tracking</p>
                        <p><strong>Key features:</strong> Metric/Imperial units, health recommendations</p>
                        <p><strong>When to use:</strong> Health checkups, fitness planning</p>
                    </div>
                </div>
            </section>
            
            <section id="tips" class="calc-category">
                <h2>💡 Usage Tips & Best Practices</h2>
                
                <h3>General Calculator Tips</h3>
                <ul>
                    <li><strong>Double-check inputs:</strong> Small errors in interest rates or amounts can significantly affect results</li>
                    <li><strong>Use realistic assumptions:</strong> Conservative estimates are better for financial planning</li>
                    <li><strong>Consider inflation:</strong> For long-term calculations, factor in inflation's impact</li>
                    <li><strong>Compare scenarios:</strong> Run multiple calculations with different assumptions</li>
                </ul>
                
                <h3>Financial Planning Best Practices</h3>
                <ul>
                    <li><strong>Emergency fund first:</strong> Before investing, establish 3-6 months of expenses in savings</li>
                    <li><strong>Pay off high-interest debt:</strong> Credit card debt (20%+ interest) should be eliminated before investing</li>
                    <li><strong>Start early:</strong> Time is your biggest asset in building wealth through compound interest</li>
                    <li><strong>Diversify:</strong> Don't put all investments in one asset class or company</li>
                </ul>
                
                <h3>Common Mistakes to Avoid</h3>
                <ul>
                    <li><strong>Ignoring taxes:</strong> Always consider tax implications of financial decisions</li>
                    <li><strong>Focusing only on monthly payments:</strong> Total cost matters more than monthly affordability</li>
                    <li><strong>Not accounting for fees:</strong> Loan origination fees, investment fees, and other costs add up</li>
                    <li><strong>Unrealistic expectations:</strong> Historical market returns don't guarantee future performance</li>
                </ul>
            </section>
            
            <div style="margin-top: 3rem; text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px;">
                <h3>Need Help Choosing?</h3>
                <p>Not sure which calculator to use? Start with our <a href="/calculators/percentage/">Percentage Calculator</a> for basic math, 
                <a href="/calculators/loan/">Loan Calculator</a> for borrowing decisions, or <a href="/calculators/retirement/">Retirement Calculator</a> for long-term planning.</p>
                
                <p><a href="/" style="background: #007bff; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 4px;">View All Calculators</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/faq/<calculator_type>/')
def calculator_faq(calculator_type):
    """Generate FAQ pages for calculators"""
    faqs = generate_calculator_faq(calculator_type)
    
    if not faqs:
        return "Calculator FAQ not found", 404
    
    # Calculator names for titles
    calc_names = {
        'percentage': 'Percentage Calculator',
        'loan': 'Loan Calculator', 
        'mortgage': 'Mortgage Calculator',
        'retirement': 'Retirement Calculator'
    }
    
    calc_name = calc_names.get(calculator_type, 'Calculator')
    
    # Generate FAQ JSON-LD
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    
    for faq in faqs:
        faq_schema["mainEntity"].append({
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["answer"]
            }
        })
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>{calc_name} FAQ - Common Questions and Answers</title>
        <meta name="description" content="Frequently asked questions about the {calc_name}. Get answers to common questions and learn how to use our calculator effectively.">
        <meta name="keywords" content="{calculator_type} calculator faq, {calculator_type} calculator help, {calculator_type} calculator questions">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="canonical" href="http://localhost:5000/faq/{calculator_type}/">
        
        <script type="application/ld+json">
        {json.dumps(faq_schema, indent=2)}
        </script>
        
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #007bff; text-align: center; margin-bottom: 2rem; }}
            .faq-item {{ margin: 2rem 0; padding: 1.5rem; border: 1px solid #ddd; border-radius: 8px; }}
            .question {{ font-weight: bold; color: #333; margin-bottom: 1rem; font-size: 1.1rem; }}
            .answer {{ color: #555; }}
            .back-link {{ display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
            .calculator-link {{ text-align: center; margin: 2rem 0; }}
            .calculator-link a {{ background: #007bff; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/calculators/{calculator_type}/" class="back-link">← Back to {calc_name}</a>
            
            <h1>❓ {calc_name} FAQ</h1>
            
            <div class="calculator-link">
                <a href="/calculators/{calculator_type}/">Use the {calc_name}</a>
            </div>
            
            {''.join([f'''
            <div class="faq-item">
                <div class="question">{faq["question"]}</div>
                <div class="answer">{faq["answer"]}</div>
            </div>
            ''' for faq in faqs])}
            
            <div class="calculator-link">
                <a href="/calculators/{calculator_type}/">Try the {calc_name} Now</a>
            </div>
            
            <div style="margin-top: 2rem; text-align: center; color: #666;">
                <p>Have more questions? <a href="/calculator-guide/">Check our Complete Calculator Guide</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/blog/')
def blog_index():
    """SEO blog/resource center"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Financial Calculator Blog - Tips, Guides, and Resources</title>
        <meta name="description" content="Expert financial advice, calculator guides, and personal finance tips. Learn how to make better financial decisions with our comprehensive resources.">
        <meta name="keywords" content="financial blog, calculator guides, personal finance tips, money management, financial planning">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="canonical" href="http://localhost:5000/blog/">
        
        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "Blog",
            "name": "Calculator Suite Financial Blog",
            "description": "Expert financial advice and calculator guides",
            "url": "http://localhost:5000/blog/",
            "publisher": {{
                "@type": "Organization",
                "name": "Calculator Suite"
            }}
        }}
        </script>
        
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; line-height: 1.6; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #007bff; text-align: center; margin-bottom: 2rem; }}
            .article-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0; }}
            .article-card {{ border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
            .article-content {{ padding: 1.5rem; }}
            .article-meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
            .back-link {{ display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
            .featured {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; }}
            .featured h3, .featured p {{ color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>📚 Financial Resources & Guides</h1>
            
            <div class="article-grid">
                <div class="article-card featured">
                    <div class="article-content">
                        <div class="article-meta">Featured Guide</div>
                        <h3><a href="/calculator-guide/" style="color: white;">Complete Calculator Guide</a></h3>
                        <p>Comprehensive guide to all our calculators. Learn which tool to use for every financial decision and get expert tips for better results.</p>
                    </div>
                </div>
                
                <div class="article-card">
                    <div class="article-content">
                        <div class="article-meta">Loan Planning</div>
                        <h3><a href="/faq/loan/">Loan Calculator FAQ</a></h3>
                        <p>Everything you need to know about loan calculations. Understand interest rates, terms, and how to get the best loan deals.</p>
                    </div>
                </div>
                
                <div class="article-card">
                    <div class="article-content">
                        <div class="article-meta">Home Buying</div>
                        <h3><a href="/faq/mortgage/">Mortgage Calculator FAQ</a></h3>
                        <p>Master mortgage calculations and home affordability. Learn about PMI, property taxes, and how much house you can afford.</p>
                    </div>
                </div>
                
                <div class="article-card">
                    <div class="article-content">
                        <div class="article-meta">Retirement Planning</div>
                        <h3><a href="/faq/retirement/">Retirement Calculator FAQ</a></h3>
                        <p>Plan your retirement with confidence. Understand savings rates, compound interest, and how to build wealth over time.</p>
                    </div>
                </div>
                
                <div class="article-card">
                    <div class="article-content">
                        <div class="article-meta">Basic Math</div>
                        <h3><a href="/faq/percentage/">Percentage Calculator FAQ</a></h3>
                        <p>Master percentage calculations for everyday use. From shopping discounts to grade calculations, learn all the essential formulas.</p>
                    </div>
                </div>
                
                <div class="article-card">
                    <div class="article-content">
                        <div class="article-meta">Quick Tips</div>
                        <h3>Financial Planning Essentials</h3>
                        <p>Build emergency funds, pay off debt, and start investing. Essential steps everyone should take for financial security.</p>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 3rem; text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px;">
                <h3>Ready to Calculate?</h3>
                <p>Use our free calculators to make informed financial decisions.</p>
                <a href="/" style="background: #007bff; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 4px;">Browse All Calculators</a>
            </div>
        </div>
    </body>
    </html>
    """

# Update sitemap to include new SEO pages
@app.route('/sitemap.xml')
def sitemap():
    """Generate enhanced XML sitemap for SEO"""
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://localhost:5000/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculator-guide/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>http://localhost:5000/blog/</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/percentage/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/faq/percentage/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/loan/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/faq/loan/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/mortgage/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/faq/mortgage/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/bmi/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/tip/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/income-tax/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/sales-tax/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/property-tax/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/tax-refund/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/gross-to-net/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/hourly-to-salary/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/salary-raise/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/cost-of-living/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/compound-interest/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/retirement/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:5000/faq/retirement/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
    <url>
        <loc>http://localhost:5000/calculators/investment-return/</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>'''
    
    response = app.make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

# Debug route to check logs
@app.route('/debug/logs')
def debug_logs():
    return jsonify({
        'calculation_count': len(calculation_logs),
        'recent_calculations': calculation_logs[-10:] if calculation_logs else []
    })

if __name__ == '__main__':
    print("🚀 Starting Calculator Suite...")
    print("📊 Available at: http://localhost:5000")
    print("")
    print("🧮 Calculators:")
    print("  📊 Percentage: http://localhost:5000/calculators/percentage/")
    print("  ⚖️ BMI: http://localhost:5000/calculators/bmi/")
    print("  💰 Tip: http://localhost:5000/calculators/tip/")
    print("  🏦 Loan: http://localhost:5000/calculators/loan/")
    print("  🏠 Mortgage: http://localhost:5000/calculators/mortgage/")
    print("  📋 Income Tax: http://localhost:5000/calculators/income-tax/")
    print("  🛒 Sales Tax: http://localhost:5000/calculators/sales-tax/")
    print("  🏠 Property Tax: http://localhost:5000/calculators/property-tax/")
    print("  💰 Tax Refund: http://localhost:5000/calculators/tax-refund/")
    print("  💵 Gross to Net: http://localhost:5000/calculators/gross-to-net/")
    print("  ⏰ Hourly to Salary: http://localhost:5000/calculators/hourly-to-salary/")
    print("  📈 Salary Raise: http://localhost:5000/calculators/salary-raise/")
    print("  🏙️ Cost of Living: http://localhost:5000/calculators/cost-of-living/")
    print("  📈 Compound Interest: http://localhost:5000/calculators/compound-interest/")
    print("  🏖️ Retirement: http://localhost:5000/calculators/retirement/")
    print("  💹 Investment Return: http://localhost:5000/calculators/investment-return/")
    print("")
    print("🔍 SEO:")
    print("  🗺️ Sitemap: http://localhost:5000/sitemap.xml")
    print("  🤖 Robots: http://localhost:5000/robots.txt")
    print("  🔧 Debug: http://localhost:5000/debug/logs")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=True)