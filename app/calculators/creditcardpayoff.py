"""
Credit Card Payoff Calculator
Focused analysis of single credit card debt with detailed payoff scenarios,
balance transfer optimization, and true cost visualization.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service
import math

@register_calculator
class CreditCardPayoffCalculator(BaseCalculator):
    """Calculate credit card payoff scenarios with detailed analysis."""
    
    # Credit card types and typical characteristics
    CARD_TYPES = {
        'standard': {
            'typical_rate_range': (15.0, 25.0),
            'typical_limit_range': (1000, 10000),
            'description': 'Basic credit card'
        },
        'rewards': {
            'typical_rate_range': (16.0, 28.0),
            'typical_limit_range': (2000, 25000),
            'description': 'Cashback or rewards card'
        },
        'premium': {
            'typical_rate_range': (17.0, 29.0),
            'typical_limit_range': (5000, 50000),
            'description': 'Premium or travel rewards card'
        },
        'store': {
            'typical_rate_range': (22.0, 29.0),
            'typical_limit_range': (500, 5000),
            'description': 'Store-branded credit card'
        },
        'balance_transfer': {
            'typical_rate_range': (0.0, 21.0),
            'typical_limit_range': (2000, 15000),
            'description': 'Balance transfer promotional card'
        }
    }
    
    # Balance transfer fee structure
    BALANCE_TRANSFER_FEES = {
        'typical_fee_percentage': Decimal('3.0'),  # 3%
        'typical_min_fee': Decimal('5.0'),
        'typical_max_fee': Decimal('200.0'),
        'promotional_rates': [
            {'rate': Decimal('0.0'), 'duration_months': 12, 'description': '0% for 12 months'},
            {'rate': Decimal('0.0'), 'duration_months': 18, 'description': '0% for 18 months'},
            {'rate': Decimal('0.0'), 'duration_months': 21, 'description': '0% for 21 months'},
            {'rate': Decimal('1.9'), 'duration_months': 12, 'description': '1.9% for 12 months'}
        ]
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate credit card payoff scenarios and optimizations."""
        # Extract basic inputs
        balance = Decimal(str(inputs.get('balance', 5000)))
        interest_rate = Decimal(str(inputs.get('interest_rate', 18.0)))
        minimum_payment = Decimal(str(inputs.get('minimum_payment', 100)))
        credit_limit = Decimal(str(inputs.get('credit_limit', 10000)))
        currency = inputs.get('currency', 'USD')
        card_type = inputs.get('card_type', 'standard')
        
        # Optional inputs
        extra_payment = Decimal(str(inputs.get('extra_payment', 0)))
        current_monthly_charges = Decimal(str(inputs.get('current_monthly_charges', 0)))
        
        # Validate minimum payment adequacy
        minimum_payment = self._validate_minimum_payment(balance, interest_rate, minimum_payment)
        
        # Calculate current situation
        current_situation = self._calculate_current_situation(
            balance, interest_rate, minimum_payment, credit_limit, current_monthly_charges
        )
        
        # Calculate payoff scenarios
        payoff_scenarios = self._calculate_payoff_scenarios(balance, interest_rate, minimum_payment)
        
        # Calculate extra payment impact
        extra_payment_analysis = self._calculate_extra_payment_impact(
            balance, interest_rate, minimum_payment, extra_payment
        )
        
        # Calculate balance transfer scenarios
        balance_transfer_analysis = self._calculate_balance_transfer_scenarios(balance, interest_rate, minimum_payment)
        
        # Calculate monthly breakdown for visualization
        payment_breakdown = self._calculate_payment_breakdown(
            balance, interest_rate, minimum_payment + extra_payment
        )
        
        # Generate optimization recommendations
        recommendations = self._generate_recommendations(
            balance, interest_rate, minimum_payment, extra_payment,
            current_situation, balance_transfer_analysis
        )
        
        # Calculate credit utilization impact
        utilization_analysis = self._calculate_utilization_analysis(balance, credit_limit)
        
        results = {
            'balance': balance,
            'interest_rate': interest_rate,
            'minimum_payment': minimum_payment,
            'credit_limit': credit_limit,
            'extra_payment': extra_payment,
            'currency': currency,
            'card_type': card_type,
            'current_situation': current_situation,
            'payoff_scenarios': payoff_scenarios,
            'extra_payment_analysis': extra_payment_analysis,
            'balance_transfer_analysis': balance_transfer_analysis,
            'payment_breakdown': payment_breakdown,
            'utilization_analysis': utilization_analysis,
            'recommendations': recommendations
        }
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        return results
    
    def _validate_minimum_payment(self, balance: Decimal, interest_rate: Decimal, 
                                minimum_payment: Decimal) -> Decimal:
        """Validate and adjust minimum payment if necessary."""
        monthly_interest = balance * interest_rate / 100 / 12
        
        # Minimum payment should be at least interest + 1% of balance
        required_minimum = monthly_interest + (balance * Decimal('0.01'))
        
        if minimum_payment < required_minimum:
            return required_minimum.quantize(Decimal('0.01'))
        
        return minimum_payment
    
    def _calculate_current_situation(self, balance: Decimal, interest_rate: Decimal,
                                   minimum_payment: Decimal, credit_limit: Decimal,
                                   monthly_charges: Decimal) -> Dict[str, Any]:
        """Calculate current credit card situation."""
        monthly_interest_charge = (balance * interest_rate / 100 / 12).quantize(Decimal('0.01'))
        principal_payment = minimum_payment - monthly_interest_charge
        
        # Calculate utilization
        utilization_percentage = (balance / credit_limit * 100).quantize(Decimal('0.1')) if credit_limit > 0 else Decimal('0')
        
        # Calculate if new charges offset payments
        net_progress = principal_payment - monthly_charges
        
        # Calculate payoff time with minimum payments
        payoff_months = self._calculate_payoff_months(balance, interest_rate, minimum_payment)
        total_interest = self._calculate_total_interest(balance, interest_rate, minimum_payment)
        
        return {
            'monthly_interest_charge': monthly_interest_charge,
            'principal_payment': principal_payment,
            'utilization_percentage': utilization_percentage,
            'available_credit': (credit_limit - balance).quantize(Decimal('0.01')),
            'monthly_charges': monthly_charges,
            'net_monthly_progress': net_progress.quantize(Decimal('0.01')),
            'payoff_months': payoff_months,
            'payoff_years': round(float(payoff_months / 12), 1) if payoff_months < 999 else None,
            'total_interest': total_interest,
            'total_payments': (balance + total_interest).quantize(Decimal('0.01'))
        }
    
    def _calculate_payoff_scenarios(self, balance: Decimal, interest_rate: Decimal,
                                  minimum_payment: Decimal) -> List[Dict]:
        """Calculate payoff scenarios with different payment amounts."""
        scenarios = []
        
        # Calculate scenarios with different payment multiples
        payment_multiples = [
            {'multiplier': 1.0, 'description': 'Minimum payment only'},
            {'multiplier': 1.5, 'description': '50% more than minimum'},
            {'multiplier': 2.0, 'description': 'Double minimum payment'},
            {'multiplier': 3.0, 'description': 'Triple minimum payment'}
        ]
        
        # Add fixed payment scenarios
        fixed_payments = [200, 300, 500]
        
        for scenario in payment_multiples:
            payment = (minimum_payment * Decimal(str(scenario['multiplier']))).quantize(Decimal('0.01'))
            
            if payment >= minimum_payment:
                months = self._calculate_payoff_months(balance, interest_rate, payment)
                total_interest = self._calculate_total_interest(balance, interest_rate, payment)
                
                scenarios.append({
                    'payment_amount': payment,
                    'description': scenario['description'],
                    'payoff_months': months,
                    'payoff_years': round(float(months / 12), 1) if months < 999 else None,
                    'total_interest': total_interest,
                    'total_payments': (balance + total_interest).quantize(Decimal('0.01')),
                    'interest_savings': (self._calculate_total_interest(balance, interest_rate, minimum_payment) - total_interest).quantize(Decimal('0.01')),
                    'time_savings_months': self._calculate_payoff_months(balance, interest_rate, minimum_payment) - months
                })
        
        # Add fixed payment scenarios
        for fixed_payment in fixed_payments:
            payment = Decimal(str(fixed_payment))
            if payment > minimum_payment:
                months = self._calculate_payoff_months(balance, interest_rate, payment)
                total_interest = self._calculate_total_interest(balance, interest_rate, payment)
                
                scenarios.append({
                    'payment_amount': payment,
                    'description': f'${fixed_payment} per month',
                    'payoff_months': months,
                    'payoff_years': round(float(months / 12), 1) if months < 999 else None,
                    'total_interest': total_interest,
                    'total_payments': (balance + total_interest).quantize(Decimal('0.01')),
                    'interest_savings': (self._calculate_total_interest(balance, interest_rate, minimum_payment) - total_interest).quantize(Decimal('0.01')),
                    'time_savings_months': self._calculate_payoff_months(balance, interest_rate, minimum_payment) - months
                })
        
        return sorted(scenarios, key=lambda x: x['payment_amount'])
    
    def _calculate_extra_payment_impact(self, balance: Decimal, interest_rate: Decimal,
                                      minimum_payment: Decimal, extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate the impact of extra payments."""
        if extra_payment <= 0:
            return {
                'has_extra_payment': False,
                'message': 'No extra payment specified'
            }
        
        total_payment = minimum_payment + extra_payment
        
        # Calculate with and without extra payment
        without_extra = {
            'months': self._calculate_payoff_months(balance, interest_rate, minimum_payment),
            'total_interest': self._calculate_total_interest(balance, interest_rate, minimum_payment)
        }
        
        with_extra = {
            'months': self._calculate_payoff_months(balance, interest_rate, total_payment),
            'total_interest': self._calculate_total_interest(balance, interest_rate, total_payment)
        }
        
        interest_savings = without_extra['total_interest'] - with_extra['total_interest']
        time_savings = without_extra['months'] - with_extra['months']
        
        return {
            'has_extra_payment': True,
            'extra_payment': extra_payment,
            'total_monthly_payment': total_payment,
            'payoff_months': with_extra['months'],
            'payoff_years': round(float(with_extra['months'] / 12), 1),
            'total_interest': with_extra['total_interest'],
            'interest_savings': interest_savings.quantize(Decimal('0.01')),
            'time_savings_months': time_savings,
            'time_savings_years': round(float(time_savings / 12), 1),
            'break_even_analysis': self._calculate_break_even(balance, interest_rate, minimum_payment, extra_payment)
        }
    
    def _calculate_balance_transfer_scenarios(self, balance: Decimal, current_rate: Decimal,
                                            minimum_payment: Decimal) -> Dict[str, Any]:
        """Calculate balance transfer optimization scenarios."""
        scenarios = []
        
        for promo in self.BALANCE_TRANSFER_FEES['promotional_rates']:
            promo_rate = promo['rate']
            promo_duration = promo['duration_months']
            
            # Calculate transfer fee (typically 3%)
            transfer_fee = (balance * self.BALANCE_TRANSFER_FEES['typical_fee_percentage'] / 100).quantize(Decimal('0.01'))
            transfer_fee = max(transfer_fee, self.BALANCE_TRANSFER_FEES['typical_min_fee'])
            transfer_fee = min(transfer_fee, self.BALANCE_TRANSFER_FEES['typical_max_fee'])
            
            new_balance = balance + transfer_fee
            
            # Calculate payoff during promotional period
            promo_payment_months = min(promo_duration, self._calculate_payoff_months(new_balance, promo_rate, minimum_payment))
            
            if promo_payment_months <= promo_duration:
                # Paid off during promotional period
                total_interest = self._calculate_total_interest(new_balance, promo_rate, minimum_payment)
                total_cost = new_balance + total_interest
                payoff_months = promo_payment_months
            else:
                # Calculate mixed scenario (promo + regular rate)
                remaining_after_promo = self._calculate_remaining_balance(
                    new_balance, promo_rate, minimum_payment, promo_duration
                )
                
                # Assume regular rate returns to something reasonable (e.g., 15%)
                post_promo_rate = Decimal('15.0')
                remaining_months = self._calculate_payoff_months(remaining_after_promo, post_promo_rate, minimum_payment)
                
                promo_interest = self._calculate_interest_for_period(new_balance, promo_rate, minimum_payment, promo_duration)
                post_promo_interest = self._calculate_total_interest(remaining_after_promo, post_promo_rate, minimum_payment)
                
                total_interest = promo_interest + post_promo_interest
                total_cost = balance + transfer_fee + total_interest
                payoff_months = promo_duration + remaining_months
            
            # Compare with current situation
            current_total_interest = self._calculate_total_interest(balance, current_rate, minimum_payment)
            savings = current_total_interest - (total_interest + transfer_fee)
            
            scenarios.append({
                'promotional_rate': promo_rate,
                'promotional_duration_months': promo_duration,
                'transfer_fee': transfer_fee,
                'new_balance_after_fee': new_balance,
                'payoff_months': payoff_months,
                'payoff_years': round(float(payoff_months / 12), 1),
                'total_interest': total_interest,
                'total_cost': total_cost.quantize(Decimal('0.01')),
                'savings_vs_current': savings.quantize(Decimal('0.01')),
                'worthwhile': savings > 0,
                'description': promo['description']
            })
        
        # Find best scenario
        best_scenario = max(scenarios, key=lambda x: x['savings_vs_current']) if scenarios else None
        
        return {
            'scenarios': scenarios,
            'best_scenario': best_scenario,
            'recommendation': self._generate_balance_transfer_recommendation(best_scenario)
        }
    
    def _calculate_payment_breakdown(self, balance: Decimal, interest_rate: Decimal,
                                   monthly_payment: Decimal, max_months: int = 60) -> List[Dict]:
        """Calculate month-by-month payment breakdown."""
        breakdown = []
        remaining_balance = balance
        month = 0
        
        while remaining_balance > Decimal('0.01') and month < max_months:
            month += 1
            
            # Calculate interest charge
            interest_charge = (remaining_balance * interest_rate / 100 / 12).quantize(Decimal('0.01'))
            
            # Calculate principal payment
            if monthly_payment > remaining_balance + interest_charge:
                # Final payment
                payment = remaining_balance + interest_charge
                principal_payment = remaining_balance
            else:
                payment = monthly_payment
                principal_payment = payment - interest_charge
            
            # Update balance
            remaining_balance -= principal_payment
            
            breakdown.append({
                'month': month,
                'beginning_balance': remaining_balance + principal_payment,
                'payment': payment.quantize(Decimal('0.01')),
                'interest': interest_charge,
                'principal': principal_payment.quantize(Decimal('0.01')),
                'ending_balance': remaining_balance.quantize(Decimal('0.01'))
            })
            
            if remaining_balance <= Decimal('0.01'):
                break
        
        return breakdown
    
    def _calculate_utilization_analysis(self, balance: Decimal, credit_limit: Decimal) -> Dict[str, Any]:
        """Analyze credit utilization and its impact."""
        if credit_limit <= 0:
            return {'utilization_percentage': Decimal('0'), 'analysis': 'Credit limit not provided'}
        
        utilization = (balance / credit_limit * 100).quantize(Decimal('0.1'))
        
        # Credit score impact analysis
        if utilization > 90:
            impact = 'severe_negative'
            message = 'Extremely high utilization - major negative impact on credit score'
            recommendation = 'Pay down immediately or request credit limit increase'
        elif utilization > 50:
            impact = 'high_negative'
            message = 'High utilization - significant negative impact on credit score'
            recommendation = 'Reduce utilization below 30% for better credit score'
        elif utilization > 30:
            impact = 'moderate_negative'
            message = 'Moderate utilization - some negative impact on credit score'
            recommendation = 'Aim for utilization below 10% for optimal credit score'
        elif utilization > 10:
            impact = 'minimal_negative'
            message = 'Good utilization - minimal impact on credit score'
            recommendation = 'Consider paying down further for excellent credit score'
        else:
            impact = 'excellent'
            message = 'Excellent utilization - positive for credit score'
            recommendation = 'Maintain this low utilization for optimal credit health'
        
        # Calculate utilization reduction scenarios
        target_utilizations = [30, 20, 10, 5]
        reduction_scenarios = []
        
        for target in target_utilizations:
            if target < utilization:
                target_balance = (credit_limit * Decimal(str(target)) / 100).quantize(Decimal('0.01'))
                payment_needed = balance - target_balance
                
                reduction_scenarios.append({
                    'target_utilization': target,
                    'target_balance': target_balance,
                    'payment_needed': payment_needed,
                    'new_available_credit': (credit_limit - target_balance).quantize(Decimal('0.01'))
                })
        
        return {
            'current_utilization': utilization,
            'credit_limit': credit_limit,
            'available_credit': (credit_limit - balance).quantize(Decimal('0.01')),
            'impact_level': impact,
            'impact_message': message,
            'recommendation': recommendation,
            'reduction_scenarios': reduction_scenarios
        }
    
    def _generate_recommendations(self, balance: Decimal, interest_rate: Decimal,
                                minimum_payment: Decimal, extra_payment: Decimal,
                                current_situation: Dict, balance_transfer: Dict) -> List[Dict]:
        """Generate personalized credit card payoff recommendations."""
        recommendations = []
        
        # High interest rate warning
        if interest_rate > 20:
            recommendations.append({
                'type': 'urgent',
                'priority': 'critical',
                'title': 'High Interest Rate Alert',
                'message': f'Your {interest_rate}% interest rate is very high. This should be your top priority.',
                'action': 'Consider balance transfer or aggressive payoff strategy'
            })
        
        # Minimum payment warning
        if current_situation['principal_payment'] < balance * Decimal('0.02'):  # Less than 2% of balance
            recommendations.append({
                'type': 'payment',
                'priority': 'high',
                'title': 'Increase Monthly Payments',
                'message': 'Your minimum payment barely covers interest. You need higher payments.',
                'action': f"Try to pay at least ${(balance * Decimal('0.05')).quantize(Decimal('0.01'))} per month"
            })
        
        # Balance transfer recommendation
        if balance_transfer['best_scenario']['worthwhile']:
            savings = balance_transfer['best_scenario']['savings_vs_current']
            recommendations.append({
                'type': 'optimization',
                'priority': 'high',
                'title': 'Consider Balance Transfer',
                'message': f'A balance transfer could save you ${savings:.0f} in interest.',
                'action': 'Research 0% promotional balance transfer offers'
            })
        
        # Utilization recommendation
        utilization = (balance / current_situation.get('credit_limit', balance) * 100).quantize(Decimal('0.1'))
        if utilization > 30:
            recommendations.append({
                'type': 'credit_score',
                'priority': 'medium',
                'title': 'High Credit Utilization',
                'message': f'Your {utilization}% utilization is hurting your credit score.',
                'action': 'Pay down balance to improve credit utilization ratio'
            })
        
        # Extra payment encouragement
        if extra_payment == 0:
            recommendations.append({
                'type': 'strategy',
                'priority': 'medium',
                'title': 'Add Extra Payments',
                'message': 'Even small extra payments can save significant interest.',
                'action': 'Try adding $50-100 extra to your monthly payment'
            })
        
        # Stop using card recommendation
        if current_situation['monthly_charges'] > 0:
            recommendations.append({
                'type': 'behavior',
                'priority': 'high',
                'title': 'Stop Using This Card',
                'message': 'New charges are offsetting your payment progress.',
                'action': 'Use cash or debit until this card is paid off'
            })
        
        # Emergency fund warning
        recommendations.append({
            'type': 'emergency',
            'priority': 'medium',
            'title': 'Maintain Small Emergency Fund',
            'message': 'Keep a small emergency fund to avoid new credit card debt.',
            'action': 'Maintain $500-1000 emergency fund while paying off debt'
        })
        
        return recommendations
    
    def _calculate_payoff_months(self, balance: Decimal, annual_rate: Decimal, 
                               monthly_payment: Decimal) -> int:
        """Calculate months to pay off debt."""
        if monthly_payment <= 0 or balance <= 0:
            return 0
        
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            return math.ceil(float(balance / monthly_payment))
        
        monthly_interest = balance * monthly_rate
        if monthly_payment <= monthly_interest:
            return 999  # Never paid off
        
        try:
            months = -math.log(1 - (float(balance) * float(monthly_rate)) / float(monthly_payment)) / math.log(1 + float(monthly_rate))
            return math.ceil(months)
        except (ValueError, ZeroDivisionError):
            return 999
    
    def _calculate_total_interest(self, balance: Decimal, annual_rate: Decimal, 
                                monthly_payment: Decimal) -> Decimal:
        """Calculate total interest paid."""
        months = self._calculate_payoff_months(balance, annual_rate, monthly_payment)
        
        if months >= 999:
            return balance * 10  # Arbitrary large number
        
        total_payments = monthly_payment * months
        return (total_payments - balance).quantize(Decimal('0.01'))
    
    def _calculate_remaining_balance(self, balance: Decimal, annual_rate: Decimal,
                                   monthly_payment: Decimal, months: int) -> Decimal:
        """Calculate remaining balance after specified months."""
        remaining = balance
        monthly_rate = annual_rate / 100 / 12
        
        for _ in range(months):
            if remaining <= Decimal('0.01'):
                break
            
            interest = remaining * monthly_rate
            principal = min(monthly_payment - interest, remaining)
            remaining -= principal
        
        return remaining.quantize(Decimal('0.01'))
    
    def _calculate_interest_for_period(self, balance: Decimal, annual_rate: Decimal,
                                     monthly_payment: Decimal, months: int) -> Decimal:
        """Calculate total interest paid over specific period."""
        total_interest = Decimal('0')
        remaining = balance
        monthly_rate = annual_rate / 100 / 12
        
        for _ in range(months):
            if remaining <= Decimal('0.01'):
                break
            
            interest = remaining * monthly_rate
            principal = min(monthly_payment - interest, remaining)
            total_interest += interest
            remaining -= principal
        
        return total_interest.quantize(Decimal('0.01'))
    
    def _calculate_break_even(self, balance: Decimal, interest_rate: Decimal,
                            minimum_payment: Decimal, extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate break-even analysis for extra payments."""
        # This is a simplified analysis - in reality, you'd want to consider
        # opportunity cost of investing the extra payment elsewhere
        
        months_with_extra = self._calculate_payoff_months(balance, interest_rate, minimum_payment + extra_payment)
        total_extra_paid = extra_payment * months_with_extra
        interest_saved = (
            self._calculate_total_interest(balance, interest_rate, minimum_payment) -
            self._calculate_total_interest(balance, interest_rate, minimum_payment + extra_payment)
        )
        
        net_benefit = interest_saved - total_extra_paid
        
        return {
            'total_extra_payments': total_extra_paid.quantize(Decimal('0.01')),
            'interest_saved': interest_saved.quantize(Decimal('0.01')),
            'net_benefit': net_benefit.quantize(Decimal('0.01')),
            'roi_percentage': ((interest_saved / total_extra_paid * 100).quantize(Decimal('0.1')) 
                             if total_extra_paid > 0 else Decimal('0'))
        }
    
    def _generate_balance_transfer_recommendation(self, best_scenario: Dict) -> str:
        """Generate balance transfer recommendation text."""
        if not best_scenario or not best_scenario['worthwhile']:
            return "Balance transfer not recommended - savings are minimal or non-existent."
        
        savings = best_scenario['savings_vs_current']
        if savings > 1000:
            return f"Highly recommended - could save ${savings:.0f} in interest payments."
        elif savings > 500:
            return f"Recommended - could save ${savings:.0f} in interest payments."
        else:
            return f"Moderately beneficial - could save ${savings:.0f} in interest payments."
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Format basic values
        monetary_fields = ['balance', 'minimum_payment', 'credit_limit', 'extra_payment']
        for field in monetary_fields:
            formatted[field] = currency_service.format_currency(results[field], currency)
        
        # Format current situation
        current = results['current_situation']
        formatted['monthly_interest_charge'] = currency_service.format_currency(current['monthly_interest_charge'], currency)
        formatted['principal_payment'] = currency_service.format_currency(current['principal_payment'], currency)
        formatted['available_credit'] = currency_service.format_currency(current['available_credit'], currency)
        formatted['total_interest'] = currency_service.format_currency(current['total_interest'], currency)
        formatted['total_payments'] = currency_service.format_currency(current['total_payments'], currency)
        
        # Format extra payment analysis if present
        if results['extra_payment_analysis']['has_extra_payment']:
            extra = results['extra_payment_analysis']
            formatted['total_monthly_payment'] = currency_service.format_currency(extra['total_monthly_payment'], currency)
            formatted['interest_savings'] = currency_service.format_currency(extra['interest_savings'], currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate balance
        balance = self.validate_number(
            inputs.get('balance', 5000),
            'Credit card balance',
            min_val=1,
            max_val=100000
        )
        if balance is None:
            return False
        
        # Validate interest rate
        interest_rate = self.validate_number(
            inputs.get('interest_rate', 18.0),
            'Interest rate',
            min_val=0,
            max_val=50
        )
        if interest_rate is None:
            return False
        
        # Validate minimum payment
        minimum_payment = self.validate_number(
            inputs.get('minimum_payment', 100),
            'Minimum payment',
            min_val=1,
            max_val=10000
        )
        if minimum_payment is None:
            return False
        
        # Validate credit limit
        credit_limit = self.validate_number(
            inputs.get('credit_limit', 10000),
            'Credit limit',
            min_val=balance,  # Credit limit should be at least the balance
            max_val=100000
        )
        if credit_limit is None:
            return False
        
        # Validate extra payment if provided
        if inputs.get('extra_payment') is not None:
            extra_payment = self.validate_number(
                inputs['extra_payment'],
                'Extra payment',
                min_val=0,
                max_val=10000
            )
            if extra_payment is None:
                return False
        
        # Validate monthly charges if provided
        if inputs.get('current_monthly_charges') is not None:
            monthly_charges = self.validate_number(
                inputs['current_monthly_charges'],
                'Current monthly charges',
                min_val=0,
                max_val=5000
            )
            if monthly_charges is None:
                return False
        
        # Validate card type
        card_type = inputs.get('card_type', 'standard')
        if card_type not in self.CARD_TYPES:
            self.add_error(f"Invalid card type: {card_type}")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Credit Card Payoff Calculator 2024 - See True Cost of Credit Card Debt | Free',
            'description': 'Free credit card payoff calculator. See how much interest you\'ll pay, compare payoff scenarios, and find the best strategy to eliminate credit card debt.',
            'keywords': 'credit card payoff calculator, credit card debt calculator, credit card interest calculator, balance transfer calculator, credit card payment calculator',
            'canonical': '/calculators/credit-card-payoff/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Credit Card Payoff Calculator",
            "description": "Calculate credit card payoff scenarios with detailed interest analysis and balance transfer optimization",
            "url": "https://yourcalcsite.com/calculators/credit-card-payoff/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Credit card payoff timeline calculation",
                "Interest cost visualization",
                "Multiple payment scenario comparison",
                "Balance transfer optimization",
                "Credit utilization analysis",
                "Extra payment impact analysis",
                "Monthly payment breakdown",
                "Personalized payoff recommendations"
            ]
        }