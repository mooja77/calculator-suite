"""
Student Loan Calculator with multiple repayment plans.
Supports various repayment strategies and extra payment scenarios.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service
import math

@register_calculator
class StudentloanCalculator(BaseCalculator):
    """Calculate student loan repayment schedules and strategies."""
    
    # Repayment plan types
    REPAYMENT_PLANS = {
        'standard': {
            'name': 'Standard Repayment',
            'term_years': 10,
            'description': 'Fixed payments over 10 years'
        },
        'graduated': {
            'name': 'Graduated Repayment',
            'term_years': 10,
            'description': 'Payments start low and increase every 2 years'
        },
        'extended': {
            'name': 'Extended Repayment',
            'term_years': 25,
            'description': 'Fixed or graduated payments over 25 years'
        },
        'income_based': {
            'name': 'Income-Based Repayment (IBR)',
            'term_years': 20,  # 25 for new borrowers
            'payment_cap': 0.10,  # 10% of discretionary income
            'description': '10-15% of discretionary income'
        },
        'pay_as_you_earn': {
            'name': 'Pay As You Earn (PAYE)',
            'term_years': 20,
            'payment_cap': 0.10,  # 10% of discretionary income
            'description': '10% of discretionary income'
        },
        'revised_paye': {
            'name': 'Revised Pay As You Earn (REPAYE)',
            'term_years': 20,  # 25 for graduate loans
            'payment_cap': 0.10,  # 10% of discretionary income
            'description': '10% of discretionary income'
        },
        'income_contingent': {
            'name': 'Income-Contingent Repayment (ICR)',
            'term_years': 25,
            'payment_cap': 0.20,  # 20% of discretionary income
            'description': '20% of discretionary income or standard 12-year payment'
        }
    }
    
    # Federal poverty guidelines (2024)
    POVERTY_GUIDELINES = {
        1: 14580,
        2: 19720,
        3: 24860,
        4: 30000,
        5: 35140,
        6: 40280,
        7: 45420,
        8: 50560
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate student loan repayment based on selected plan."""
        # Extract inputs
        loan_amount = Decimal(str(inputs.get('loan_amount', 0)))
        interest_rate = Decimal(str(inputs.get('interest_rate', 5.5))) / 100
        repayment_plan = inputs.get('repayment_plan', 'standard')
        
        # Optional inputs
        extra_payment = Decimal(str(inputs.get('extra_payment', 0)))
        annual_income = Decimal(str(inputs.get('annual_income', 0)))
        family_size = int(inputs.get('family_size', 1))
        state = inputs.get('state', 'continental')  # For poverty guidelines
        loan_type = inputs.get('loan_type', 'federal')  # federal or private
        
        # Get repayment plan details
        plan = self.REPAYMENT_PLANS.get(repayment_plan, self.REPAYMENT_PLANS['standard'])
        
        # Calculate based on repayment plan
        if repayment_plan in ['income_based', 'pay_as_you_earn', 'revised_paye', 'income_contingent']:
            # Income-driven repayment plans
            results = self._calculate_income_driven(
                loan_amount, interest_rate, plan, annual_income, 
                family_size, state, extra_payment
            )
        elif repayment_plan == 'graduated':
            # Graduated repayment
            results = self._calculate_graduated(
                loan_amount, interest_rate, plan['term_years'], extra_payment
            )
        else:
            # Standard or extended repayment
            results = self._calculate_standard(
                loan_amount, interest_rate, plan['term_years'], extra_payment
            )
        
        # Add plan information
        results['repayment_plan'] = repayment_plan
        results['plan_name'] = plan['name']
        results['plan_description'] = plan['description']
        
        # Calculate savings with extra payments
        if extra_payment > 0:
            standard_results = self._calculate_standard(
                loan_amount, interest_rate, plan['term_years'], Decimal('0')
            )
            results['savings_from_extra'] = (standard_results['total_paid'] - results['total_paid']).quantize(Decimal('0.01'))
            results['time_saved_months'] = standard_results['total_months'] - results['total_months']
        
        # Add formatted values
        results['formatted'] = self._format_results(results, 'USD')
        
        # Add payment schedule (first 12 months and summary)
        results['payment_schedule'] = self._generate_payment_schedule(
            loan_amount, interest_rate, results['monthly_payment'], 
            extra_payment, repayment_plan
        )
        
        # Add comparison with other plans
        results['plan_comparison'] = self._compare_plans(
            loan_amount, interest_rate, annual_income, family_size, state
        )
        
        return results
    
    def _calculate_standard(self, principal: Decimal, rate: Decimal, 
                          years: int, extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate standard fixed payment loan."""
        if rate == 0:
            monthly_payment = principal / (years * 12)
            total_interest = Decimal('0')
            total_paid = principal
            actual_months = years * 12
        else:
            monthly_rate = rate / 12
            months = years * 12
            
            # Standard loan payment formula
            monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                            ((1 + monthly_rate) ** months - 1)
            
            # Calculate with extra payments
            if extra_payment > 0:
                results = self._calculate_with_extra_payments(
                    principal, monthly_rate, monthly_payment, extra_payment
                )
                total_interest = results['total_interest']
                total_paid = results['total_paid']
                actual_months = results['months']
            else:
                total_paid = monthly_payment * months
                total_interest = total_paid - principal
                actual_months = months
        
        return {
            'loan_amount': principal,
            'interest_rate': rate * 100,
            'monthly_payment': monthly_payment.quantize(Decimal('0.01')),
            'extra_payment': extra_payment,
            'total_payment': (monthly_payment + extra_payment).quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'total_paid': total_paid.quantize(Decimal('0.01')),
            'total_months': actual_months,
            'payoff_date_years': Decimal(actual_months / 12).quantize(Decimal('0.1'))
        }
    
    def _calculate_graduated(self, principal: Decimal, rate: Decimal, 
                           years: int, extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate graduated repayment plan."""
        # Graduated payments increase every 2 years
        # Start at interest-only, end at 3x initial payment
        
        if rate == 0:
            # No interest case
            return self._calculate_standard(principal, rate, years, extra_payment)
        
        monthly_rate = rate / 12
        months = years * 12
        
        # Calculate minimum and maximum payments
        interest_only = principal * monthly_rate
        standard_payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                         ((1 + monthly_rate) ** months - 1)
        
        # Graduated payments: start low, increase every 24 months
        # Ensure total pays off loan in time
        min_payment = max(interest_only, standard_payment * Decimal('0.5'))
        max_payment = min(standard_payment * Decimal('1.5'), min_payment * 3)
        
        # Calculate payment schedule
        payment_increases = years // 2  # Every 2 years
        if payment_increases > 0:
            payment_increment = (max_payment - min_payment) / payment_increases
        else:
            payment_increment = Decimal('0')
        
        # Simulate payments
        balance = principal
        total_paid = Decimal('0')
        total_interest = Decimal('0')
        current_payment = min_payment
        month = 0
        
        while balance > 0 and month < months * 2:  # Safety limit
            # Increase payment every 24 months
            if month > 0 and month % 24 == 0:
                current_payment = min(current_payment + payment_increment, max_payment)
            
            # Calculate interest
            interest = balance * monthly_rate
            principal_payment = current_payment - interest + extra_payment
            
            # Handle last payment
            if principal_payment >= balance:
                principal_payment = balance
                current_payment = principal_payment + interest
            
            balance -= principal_payment
            total_paid += current_payment + extra_payment
            total_interest += interest
            month += 1
        
        avg_payment = total_paid / month if month > 0 else Decimal('0')
        
        return {
            'loan_amount': principal,
            'interest_rate': rate * 100,
            'initial_payment': min_payment.quantize(Decimal('0.01')),
            'final_payment': current_payment.quantize(Decimal('0.01')),
            'average_payment': avg_payment.quantize(Decimal('0.01')),
            'monthly_payment': avg_payment.quantize(Decimal('0.01')),  # For compatibility
            'extra_payment': extra_payment,
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'total_paid': total_paid.quantize(Decimal('0.01')),
            'total_months': month,
            'payoff_date_years': Decimal(month / 12).quantize(Decimal('0.1'))
        }
    
    def _calculate_income_driven(self, principal: Decimal, rate: Decimal,
                               plan: Dict, income: Decimal, family_size: int,
                               state: str, extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate income-driven repayment plans."""
        # Calculate discretionary income
        poverty_guideline = Decimal(str(self.POVERTY_GUIDELINES.get(min(family_size, 8), 14580)))
        if family_size > 8:
            poverty_guideline += (family_size - 8) * 5140
        
        # Discretionary income = AGI - 150% of poverty guideline
        discretionary_income = max(Decimal('0'), income - poverty_guideline * Decimal('1.5'))
        
        # Calculate payment based on plan
        payment_rate = Decimal(str(plan['payment_cap']))
        annual_payment = discretionary_income * payment_rate
        monthly_payment = annual_payment / 12
        
        # Ensure payment covers at least interest
        monthly_rate = rate / 12
        interest_payment = principal * monthly_rate
        
        # Some plans have minimum payment requirements
        if plan['name'].startswith('Income-Contingent'):
            # ICR uses 20% of discretionary income OR standard 12-year payment
            standard_12_year = principal * (monthly_rate * (1 + monthly_rate) ** 144) / \
                              ((1 + monthly_rate) ** 144 - 1)
            monthly_payment = min(monthly_payment, standard_12_year)
        
        # Cap payment at standard 10-year amount
        standard_payment = principal * (monthly_rate * (1 + monthly_rate) ** 120) / \
                         ((1 + monthly_rate) ** 120 - 1) if rate > 0 else principal / 120
        monthly_payment = min(monthly_payment, standard_payment)
        
        # Simulate loan over term with forgiveness
        max_months = plan['term_years'] * 12
        balance = principal
        total_paid = Decimal('0')
        total_interest = Decimal('0')
        month = 0
        
        while balance > 0 and month < max_months:
            # Calculate interest
            interest = balance * monthly_rate
            
            # Apply payment
            if monthly_payment < interest:
                # Negative amortization (balance grows)
                principal_payment = Decimal('0')
                balance += (interest - monthly_payment)
            else:
                principal_payment = monthly_payment - interest + extra_payment
                if principal_payment > balance:
                    principal_payment = balance
                balance -= principal_payment
            
            total_paid += monthly_payment + extra_payment
            total_interest += interest
            month += 1
        
        # Calculate forgiven amount
        forgiven_amount = balance if month >= max_months else Decimal('0')
        
        return {
            'loan_amount': principal,
            'interest_rate': rate * 100,
            'annual_income': income,
            'discretionary_income': discretionary_income.quantize(Decimal('0.01')),
            'monthly_payment': monthly_payment.quantize(Decimal('0.01')),
            'extra_payment': extra_payment,
            'total_payment': (monthly_payment + extra_payment).quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'total_paid': total_paid.quantize(Decimal('0.01')),
            'total_months': month,
            'payoff_date_years': Decimal(month / 12).quantize(Decimal('0.1')),
            'forgiven_amount': forgiven_amount.quantize(Decimal('0.01')),
            'forgiveness_eligible': forgiven_amount > 0
        }
    
    def _calculate_with_extra_payments(self, principal: Decimal, monthly_rate: Decimal,
                                     min_payment: Decimal, extra: Decimal) -> Dict[str, Any]:
        """Calculate loan payoff with extra payments."""
        balance = principal
        total_paid = Decimal('0')
        total_interest = Decimal('0')
        months = 0
        
        while balance > 0 and months < 360:  # Max 30 years
            interest = balance * monthly_rate
            principal_payment = min_payment - interest + extra
            
            if principal_payment >= balance:
                total_paid += balance + interest
                total_interest += interest
                balance = Decimal('0')
            else:
                balance -= principal_payment
                total_paid += min_payment + extra
                total_interest += interest
            
            months += 1
        
        return {
            'total_paid': total_paid,
            'total_interest': total_interest,
            'months': months
        }
    
    def _generate_payment_schedule(self, principal: Decimal, rate: Decimal,
                                 payment: Decimal, extra: Decimal,
                                 plan_type: str) -> List[Dict]:
        """Generate payment schedule for first year."""
        schedule = []
        balance = principal
        monthly_rate = rate / 12
        
        for month in range(1, 13):
            interest = balance * monthly_rate
            principal_payment = payment - interest + extra
            
            if principal_payment > balance:
                principal_payment = balance
            
            balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment': (payment + extra).quantize(Decimal('0.01')),
                'principal': principal_payment.quantize(Decimal('0.01')),
                'interest': interest.quantize(Decimal('0.01')),
                'balance': max(Decimal('0'), balance).quantize(Decimal('0.01'))
            })
            
            if balance <= 0:
                break
        
        return schedule
    
    def _compare_plans(self, principal: Decimal, rate: Decimal,
                      income: Decimal, family_size: int, state: str) -> List[Dict]:
        """Compare different repayment plans."""
        comparison = []
        
        for plan_key, plan in self.REPAYMENT_PLANS.items():
            if plan_key in ['income_based', 'pay_as_you_earn', 'revised_paye', 'income_contingent']:
                if income > 0:
                    results = self._calculate_income_driven(
                        principal, rate, plan, income, family_size, state, Decimal('0')
                    )
                else:
                    continue  # Skip income-driven plans if no income provided
            elif plan_key == 'graduated':
                results = self._calculate_graduated(
                    principal, rate, plan['term_years'], Decimal('0')
                )
            else:
                results = self._calculate_standard(
                    principal, rate, plan['term_years'], Decimal('0')
                )
            
            comparison.append({
                'plan': plan['name'],
                'monthly_payment': results.get('monthly_payment', Decimal('0')).quantize(Decimal('0.01')),
                'total_paid': results['total_paid'].quantize(Decimal('0.01')),
                'total_interest': results['total_interest'].quantize(Decimal('0.01')),
                'payoff_years': results['payoff_date_years'],
                'forgiven': results.get('forgiven_amount', Decimal('0')).quantize(Decimal('0.01'))
            })
        
        # Sort by total paid
        comparison.sort(key=lambda x: x['total_paid'])
        
        return comparison
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        currency_fields = [
            'loan_amount', 'monthly_payment', 'total_payment', 'total_interest',
            'total_paid', 'forgiven_amount', 'savings_from_extra', 'annual_income',
            'discretionary_income', 'initial_payment', 'final_payment', 'average_payment'
        ]
        
        for field in currency_fields:
            if field in results and isinstance(results[field], Decimal):
                formatted[field] = currency_service.format_currency(results[field], currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate loan amount
        loan_amount = self.validate_number(
            inputs.get('loan_amount', 0),
            'Loan amount',
            min_val=1000,
            max_val=500000
        )
        if loan_amount is None:
            return False
        
        # Validate interest rate
        interest_rate = self.validate_number(
            inputs.get('interest_rate', 5.5),
            'Interest rate',
            min_val=0,
            max_val=20
        )
        if interest_rate is None:
            return False
        
        # Validate repayment plan
        plan = inputs.get('repayment_plan', 'standard')
        if plan not in self.REPAYMENT_PLANS:
            self.add_error(f"Invalid repayment plan: {plan}")
        
        # Validate extra payment
        if inputs.get('extra_payment'):
            self.validate_number(
                inputs['extra_payment'],
                'Extra payment',
                min_val=0,
                max_val=10000
            )
        
        # Validate income for income-driven plans
        if plan in ['income_based', 'pay_as_you_earn', 'revised_paye', 'income_contingent']:
            income = self.validate_number(
                inputs.get('annual_income', 0),
                'Annual income',
                min_val=0,
                max_val=1000000
            )
            if income is None or income == 0:
                self.add_error("Annual income required for income-driven repayment plans")
        
        # Validate family size
        if inputs.get('family_size'):
            self.validate_number(
                inputs['family_size'],
                'Family size',
                min_val=1,
                max_val=20
            )
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Student Loan Calculator 2024 - Federal & Private Loan Repayment Calculator',
            'description': 'Free student loan calculator with multiple repayment plans. Calculate standard, graduated, extended, and income-driven repayment options. See how extra payments save money.',
            'keywords': 'student loan calculator, loan repayment calculator, federal student loan calculator, income based repayment calculator, student loan payment calculator, extra payment calculator',
            'canonical': '/calculators/studentloan/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Student Loan Calculator",
            "description": "Calculate student loan repayment options including standard, graduated, and income-driven plans",
            "url": "https://yourcalcsite.com/calculators/studentloan/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Standard repayment calculation",
                "Graduated repayment plan",
                "Income-driven repayment options",
                "Extra payment scenarios",
                "Total interest calculation",
                "Loan forgiveness estimates",
                "Payment schedule generation",
                "Plan comparison tool"
            ]
        }