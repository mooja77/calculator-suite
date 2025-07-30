"""
Debt Payoff Calculator with Snowball and Avalanche Methods
Strategic debt elimination planning with multiple debt management,
side-by-side method comparison, and extra payment impact analysis.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service
import math

@register_calculator
class DebtPayoffCalculator(BaseCalculator):
    """Calculate debt payoff strategies using snowball and avalanche methods."""
    
    # Debt type categories with typical interest rate ranges
    DEBT_TYPES = {
        'credit_card': {
            'typical_rate_range': (15.0, 29.0),
            'priority_score': 10,
            'description': 'High-interest revolving debt'
        },
        'personal_loan': {
            'typical_rate_range': (6.0, 36.0),
            'priority_score': 8,
            'description': 'Unsecured personal loans'
        },
        'student_loan': {
            'typical_rate_range': (3.0, 12.0),
            'priority_score': 5,
            'description': 'Educational debt (may have tax benefits)'
        },
        'auto_loan': {
            'typical_rate_range': (3.0, 10.0),
            'priority_score': 6,
            'description': 'Secured by vehicle'
        },
        'mortgage': {
            'typical_rate_range': (3.0, 8.0),
            'priority_score': 3,
            'description': 'Secured by real estate (tax deductible)'
        },
        'home_equity': {
            'typical_rate_range': (4.0, 12.0),
            'priority_score': 4,
            'description': 'Secured by home equity'
        },
        'medical_debt': {
            'typical_rate_range': (0.0, 15.0),
            'priority_score': 7,
            'description': 'Healthcare-related debt'
        },
        'other': {
            'typical_rate_range': (0.0, 30.0),
            'priority_score': 5,
            'description': 'Other types of debt'
        }
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate debt payoff strategies using both snowball and avalanche methods."""
        # Extract inputs
        debts = inputs.get('debts', [])
        extra_payment = Decimal(str(inputs.get('extra_payment', 0)))
        currency = inputs.get('currency', 'USD')
        
        if not debts:
            raise ValueError("At least one debt must be provided")
        
        # Process and validate debt data
        processed_debts = self._process_debt_data(debts)
        
        # Calculate current situation (minimum payments only)
        current_situation = self._calculate_current_situation(processed_debts)
        
        # Calculate snowball method payoff
        snowball_strategy = self._calculate_snowball_method(processed_debts, extra_payment)
        
        # Calculate avalanche method payoff
        avalanche_strategy = self._calculate_avalanche_method(processed_debts, extra_payment)
        
        # Compare strategies
        strategy_comparison = self._compare_strategies(snowball_strategy, avalanche_strategy)
        
        # Calculate extra payment impact scenarios
        payment_scenarios = self._calculate_payment_scenarios(processed_debts)
        
        # Generate debt optimization recommendations
        recommendations = self._generate_recommendations(
            processed_debts, snowball_strategy, avalanche_strategy, extra_payment
        )
        
        # Calculate debt-to-income ratio if income provided
        debt_ratios = None
        if inputs.get('monthly_income'):
            debt_ratios = self._calculate_debt_ratios(
                processed_debts, Decimal(str(inputs['monthly_income']))
            )
        
        results = {
            'total_debts': len(processed_debts),
            'currency': currency,
            'extra_payment': extra_payment,
            'current_situation': current_situation,
            'processed_debts': processed_debts,
            'snowball_strategy': snowball_strategy,
            'avalanche_strategy': avalanche_strategy,
            'strategy_comparison': strategy_comparison,
            'payment_scenarios': payment_scenarios,
            'recommendations': recommendations
        }
        
        # Add debt ratios if income provided
        if debt_ratios:
            results['debt_ratios'] = debt_ratios
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        return results
    
    def _process_debt_data(self, debts: List[Dict]) -> List[Dict]:
        """Process and validate debt data."""
        processed = []
        
        for i, debt in enumerate(debts):
            try:
                processed_debt = {
                    'id': i + 1,
                    'name': debt.get('name', f'Debt {i + 1}'),
                    'balance': Decimal(str(debt['balance'])),
                    'interest_rate': Decimal(str(debt['interest_rate'])),
                    'minimum_payment': Decimal(str(debt['minimum_payment'])),
                    'debt_type': debt.get('debt_type', 'other')
                }
                
                # Validate minimum payment covers interest
                monthly_interest = processed_debt['balance'] * processed_debt['interest_rate'] / 100 / 12
                if processed_debt['minimum_payment'] <= monthly_interest:
                    # Adjust minimum payment to cover interest plus 1% of balance
                    processed_debt['minimum_payment'] = monthly_interest + (processed_debt['balance'] * Decimal('0.01'))
                    processed_debt['adjusted_minimum'] = True
                else:
                    processed_debt['adjusted_minimum'] = False
                
                # Calculate payoff time with minimum payments only
                processed_debt['minimum_payoff_months'] = self._calculate_payoff_months(
                    processed_debt['balance'],
                    processed_debt['interest_rate'],
                    processed_debt['minimum_payment']
                )
                
                # Calculate total interest with minimum payments
                processed_debt['total_interest_minimum'] = self._calculate_total_interest(
                    processed_debt['balance'],
                    processed_debt['interest_rate'],
                    processed_debt['minimum_payment']
                )
                
                processed.append(processed_debt)
                
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"Invalid debt data for debt {i + 1}: {e}")
        
        return processed
    
    def _calculate_current_situation(self, debts: List[Dict]) -> Dict[str, Any]:
        """Calculate current debt situation with minimum payments only."""
        total_balance = sum(debt['balance'] for debt in debts)
        total_minimum_payment = sum(debt['minimum_payment'] for debt in debts)
        total_interest = sum(debt['total_interest_minimum'] for debt in debts)
        
        # Calculate weighted average interest rate
        if total_balance > 0:
            weighted_avg_rate = sum(
                debt['balance'] * debt['interest_rate'] for debt in debts
            ) / total_balance
        else:
            weighted_avg_rate = Decimal('0')
        
        # Find longest payoff time
        max_payoff_months = max(debt['minimum_payoff_months'] for debt in debts if debt['minimum_payoff_months'])
        
        return {
            'total_balance': total_balance.quantize(Decimal('0.01')),
            'total_minimum_payment': total_minimum_payment.quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'weighted_avg_rate': weighted_avg_rate.quantize(Decimal('0.01')),
            'payoff_months': max_payoff_months,
            'payoff_years': round(float(max_payoff_months / 12), 1) if max_payoff_months else 0
        }
    
    def _calculate_snowball_method(self, debts: List[Dict], extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate debt payoff using snowball method (smallest balance first)."""
        # Sort debts by balance (smallest first)
        sorted_debts = sorted(debts, key=lambda x: x['balance'])
        return self._simulate_payoff_strategy(sorted_debts, extra_payment, 'snowball')
    
    def _calculate_avalanche_method(self, debts: List[Dict], extra_payment: Decimal) -> Dict[str, Any]:
        """Calculate debt payoff using avalanche method (highest interest first)."""
        # Sort debts by interest rate (highest first)
        sorted_debts = sorted(debts, key=lambda x: x['interest_rate'], reverse=True)
        return self._simulate_payoff_strategy(sorted_debts, extra_payment, 'avalanche')
    
    def _simulate_payoff_strategy(self, sorted_debts: List[Dict], extra_payment: Decimal, 
                                method: str) -> Dict[str, Any]:
        """Simulate debt payoff strategy."""
        # Deep copy debts to avoid modifying original
        remaining_debts = []
        for debt in sorted_debts:
            remaining_debts.append({
                'id': debt['id'],
                'name': debt['name'],
                'balance': debt['balance'],
                'interest_rate': debt['interest_rate'],
                'minimum_payment': debt['minimum_payment'],
                'debt_type': debt['debt_type']
            })
        
        payoff_schedule = []
        total_payments = Decimal('0')
        total_interest = Decimal('0')
        month = 0
        available_extra = extra_payment
        
        while remaining_debts and month < 600:  # Safety limit of 50 years
            month += 1
            monthly_interest = Decimal('0')
            monthly_principal = Decimal('0')
            
            # Calculate interest and minimum payments for all debts
            for debt in remaining_debts[:]:
                interest_charge = debt['balance'] * debt['interest_rate'] / 100 / 12
                monthly_interest += interest_charge
                
                # Apply minimum payment
                payment = min(debt['minimum_payment'], debt['balance'] + interest_charge)
                principal_payment = payment - interest_charge
                
                debt['balance'] -= principal_payment
                monthly_principal += principal_payment
                total_payments += payment
                
                # Remove paid-off debts
                if debt['balance'] <= Decimal('0.01'):
                    # Add freed-up minimum payment to extra payment pool
                    available_extra += debt['minimum_payment']
                    payoff_schedule.append({
                        'month': month,
                        'debt_name': debt['name'],
                        'debt_id': debt['id'],
                        'final_payment': payment.quantize(Decimal('0.01')),
                        'freed_payment': debt['minimum_payment'].quantize(Decimal('0.01'))
                    })
                    remaining_debts.remove(debt)
            
            # Apply extra payment to target debt (first in sorted list)
            if remaining_debts and available_extra > 0:
                target_debt = remaining_debts[0]
                extra_applied = min(available_extra, target_debt['balance'])
                target_debt['balance'] -= extra_applied
                monthly_principal += extra_applied
                total_payments += extra_applied
                
                # Check if target debt is paid off
                if target_debt['balance'] <= Decimal('0.01'):
                    available_extra += target_debt['minimum_payment']
                    payoff_schedule.append({
                        'month': month,
                        'debt_name': target_debt['name'],
                        'debt_id': target_debt['id'],
                        'final_payment': (target_debt['minimum_payment'] + extra_applied).quantize(Decimal('0.01')),
                        'freed_payment': target_debt['minimum_payment'].quantize(Decimal('0.01'))
                    })
                    remaining_debts.remove(target_debt)
            
            total_interest += monthly_interest
        
        return {
            'method': method,
            'total_months': month,
            'total_years': round(float(month / 12), 1),
            'total_payments': total_payments.quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'payoff_schedule': payoff_schedule,
            'monthly_payment': (sum(debt['minimum_payment'] for debt in sorted_debts) + extra_payment).quantize(Decimal('0.01'))
        }
    
    def _compare_strategies(self, snowball: Dict, avalanche: Dict) -> Dict[str, Any]:
        """Compare snowball and avalanche strategies."""
        interest_savings = snowball['total_interest'] - avalanche['total_interest']
        time_savings = snowball['total_months'] - avalanche['total_months']
        
        # Determine better strategy
        if abs(interest_savings) < 100 and abs(time_savings) < 6:
            better_strategy = 'similar'
            recommendation = 'Both strategies are very similar. Choose based on your personality.'
        elif interest_savings > 500 or time_savings > 12:
            better_strategy = 'avalanche'
            recommendation = 'Avalanche method saves significantly more money and time.'
        elif interest_savings > 0:
            better_strategy = 'avalanche'
            recommendation = 'Avalanche method saves more money, but the difference is modest.'
        else:
            better_strategy = 'snowball'
            recommendation = 'Snowball method may provide better psychological motivation.'
        
        return {
            'better_strategy': better_strategy,
            'interest_difference': interest_savings.quantize(Decimal('0.01')),
            'time_difference_months': time_savings,
            'time_difference_years': round(float(time_savings / 12), 1),
            'recommendation': recommendation,
            'snowball_advantages': [
                'Provides quick wins and psychological motivation',
                'Builds momentum with early debt elimination',
                'Simpler to follow and maintain'
            ],
            'avalanche_advantages': [
                'Mathematically optimal - saves the most money',
                'Reduces total interest paid',
                'Fastest debt elimination timeline'
            ]
        }
    
    def _calculate_payment_scenarios(self, debts: List[Dict]) -> List[Dict]:
        """Calculate payoff scenarios with different extra payment amounts."""
        scenarios = []
        extra_payments = [Decimal('0'), Decimal('100'), Decimal('250'), Decimal('500'), Decimal('1000')]
        
        for extra in extra_payments:
            # Use avalanche method for scenarios (mathematically optimal)
            avalanche_result = self._calculate_avalanche_method(debts, extra)
            
            scenarios.append({
                'extra_payment': extra,
                'total_months': avalanche_result['total_months'],
                'total_years': avalanche_result['total_years'],
                'total_interest': avalanche_result['total_interest'],
                'monthly_payment': avalanche_result['monthly_payment'],
                'interest_savings': (avalanche_result['total_interest'] - 
                                   self._calculate_avalanche_method(debts, Decimal('0'))['total_interest']).quantize(Decimal('0.01')),
                'time_savings_months': (avalanche_result['total_months'] - 
                                      self._calculate_avalanche_method(debts, Decimal('0'))['total_months'])
            })
        
        return scenarios
    
    def _generate_recommendations(self, debts: List[Dict], snowball: Dict, 
                                avalanche: Dict, extra_payment: Decimal) -> List[Dict]:
        """Generate personalized debt payoff recommendations."""
        recommendations = []
        
        # Strategy selection recommendation
        interest_diff = snowball['total_interest'] - avalanche['total_interest']
        if interest_diff > 1000:
            recommendations.append({
                'type': 'strategy',
                'priority': 'high',
                'title': 'Use Avalanche Method',
                'message': f"The avalanche method will save you ${interest_diff:.0f} in interest payments.",
                'action': 'Focus extra payments on highest interest rate debts first'
            })
        elif len(debts) > 3:
            recommendations.append({
                'type': 'strategy',
                'priority': 'medium',
                'title': 'Consider Snowball Method',
                'message': 'With multiple debts, snowball method can provide psychological wins.',
                'action': 'Focus on paying off smallest balances first for motivation'
            })
        
        # High-interest debt warnings
        high_interest_debts = [d for d in debts if d['interest_rate'] > 18]
        if high_interest_debts:
            total_high_interest = sum(d['balance'] for d in high_interest_debts)
            recommendations.append({
                'type': 'urgent',
                'priority': 'critical',
                'title': 'Address High-Interest Debt Immediately',
                'message': f"You have ${total_high_interest:.0f} in debt with interest rates above 18%.",
                'action': 'Consider balance transfers, debt consolidation, or aggressive payoff'
            })
        
        # Extra payment recommendations
        if extra_payment == 0:
            recommendations.append({
                'type': 'payment',
                'priority': 'high',
                'title': 'Increase Monthly Payments',
                'message': 'Even $100 extra per month can save years of payments.',
                'action': 'Review your budget to find additional funds for debt payoff'
            })
        elif extra_payment < 200:
            recommendations.append({
                'type': 'payment',
                'priority': 'medium',
                'title': 'Consider Increasing Extra Payments',
                'message': 'You could significantly accelerate debt payoff with higher payments.',
                'action': 'Try to increase extra payments when possible'
            })
        
        # Debt consolidation recommendation
        if len(debts) > 4 or any(d['interest_rate'] > 15 for d in debts):
            recommendations.append({
                'type': 'consolidation',
                'priority': 'medium',
                'title': 'Explore Debt Consolidation',
                'message': 'Consolidation might simplify payments and reduce interest rates.',
                'action': 'Research personal loans, balance transfers, or HELOC options'
            })
        
        # Emergency fund warning
        recommendations.append({
            'type': 'emergency',
            'priority': 'medium',
            'title': 'Maintain Emergency Fund',
            'message': 'Keep a small emergency fund while paying off debt.',
            'action': 'Maintain $1,000-$2,000 emergency fund to avoid new debt'
        })
        
        return recommendations
    
    def _calculate_debt_ratios(self, debts: List[Dict], monthly_income: Decimal) -> Dict[str, Any]:
        """Calculate debt-to-income ratios."""
        total_minimum_payments = sum(debt['minimum_payment'] for debt in debts)
        total_debt_balance = sum(debt['balance'] for debt in debts)
        
        # Payment-to-income ratio
        payment_ratio = (total_minimum_payments / monthly_income * 100).quantize(Decimal('0.1'))
        
        # Total debt-to-monthly-income ratio
        debt_ratio = (total_debt_balance / monthly_income).quantize(Decimal('0.1'))
        
        # Annual debt-to-income
        annual_debt_ratio = (total_debt_balance / (monthly_income * 12) * 100).quantize(Decimal('0.1'))
        
        # Assessment
        if payment_ratio > 36:
            payment_assessment = 'critical'
            payment_message = 'Your debt payments are dangerously high'
        elif payment_ratio > 28:
            payment_assessment = 'concerning'
            payment_message = 'Your debt payments are above recommended levels'
        elif payment_ratio > 20:
            payment_assessment = 'elevated'
            payment_message = 'Your debt payments are manageable but elevated'
        else:
            payment_assessment = 'healthy'
            payment_message = 'Your debt payment ratio is healthy'
        
        return {
            'payment_to_income_ratio': payment_ratio,
            'total_debt_to_monthly_income': debt_ratio,
            'annual_debt_to_income_ratio': annual_debt_ratio,
            'payment_assessment': payment_assessment,
            'payment_message': payment_message,
            'monthly_income': monthly_income,
            'total_minimum_payments': total_minimum_payments,
            'available_income': monthly_income - total_minimum_payments
        }
    
    def _calculate_payoff_months(self, balance: Decimal, annual_rate: Decimal, 
                               monthly_payment: Decimal) -> int:
        """Calculate months to pay off a single debt."""
        if monthly_payment <= 0 or balance <= 0:
            return 0
        
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            # No interest case
            return math.ceil(float(balance / monthly_payment))
        
        # Check if payment covers interest
        monthly_interest = balance * monthly_rate
        if monthly_payment <= monthly_interest:
            return 999  # Will never be paid off
        
        # Calculate months using amortization formula
        numerator = math.log(1 + (float(balance) * float(monthly_rate)) / float(monthly_payment))
        denominator = math.log(1 + float(monthly_rate))
        
        try:
            months = -numerator / denominator
            return math.ceil(months)
        except (ValueError, ZeroDivisionError):
            return 999
    
    def _calculate_total_interest(self, balance: Decimal, annual_rate: Decimal, 
                                monthly_payment: Decimal) -> Decimal:
        """Calculate total interest paid over the life of a debt."""
        months = self._calculate_payoff_months(balance, annual_rate, monthly_payment)
        
        if months >= 999:
            return balance * 10  # Arbitrary large number for never-ending debt
        
        total_payments = monthly_payment * months
        return (total_payments - balance).quantize(Decimal('0.01'))
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Format current situation
        current = results['current_situation']
        formatted['total_balance'] = currency_service.format_currency(current['total_balance'], currency)
        formatted['total_minimum_payment'] = currency_service.format_currency(current['total_minimum_payment'], currency)
        formatted['total_interest'] = currency_service.format_currency(current['total_interest'], currency)
        
        # Format strategy results
        for strategy in ['snowball_strategy', 'avalanche_strategy']:
            strategy_data = results[strategy]
            formatted[f'{strategy}_total_payments'] = currency_service.format_currency(strategy_data['total_payments'], currency)
            formatted[f'{strategy}_total_interest'] = currency_service.format_currency(strategy_data['total_interest'], currency)
            formatted[f'{strategy}_monthly_payment'] = currency_service.format_currency(strategy_data['monthly_payment'], currency)
        
        # Format comparison
        comparison = results['strategy_comparison']
        formatted['interest_difference'] = currency_service.format_currency(abs(comparison['interest_difference']), currency)
        
        # Format debt ratios if present
        if 'debt_ratios' in results:
            ratios = results['debt_ratios']
            formatted['monthly_income'] = currency_service.format_currency(ratios['monthly_income'], currency)
            formatted['total_minimum_payments'] = currency_service.format_currency(ratios['total_minimum_payments'], currency)
            formatted['available_income'] = currency_service.format_currency(ratios['available_income'], currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate debts array
        debts = inputs.get('debts', [])
        if not isinstance(debts, list) or len(debts) == 0:
            self.add_error("At least one debt must be provided")
            return False
        
        if len(debts) > 20:
            self.add_error("Maximum 20 debts allowed")
            return False
        
        # Validate each debt
        for i, debt in enumerate(debts):
            debt_name = f"Debt {i + 1}"
            
            # Validate balance
            balance = self.validate_number(
                debt.get('balance', 0),
                f'{debt_name} balance',
                min_val=1,
                max_val=1000000
            )
            if balance is None:
                return False
            
            # Validate interest rate
            interest_rate = self.validate_number(
                debt.get('interest_rate', 0),
                f'{debt_name} interest rate',
                min_val=0,
                max_val=50
            )
            if interest_rate is None:
                return False
            
            # Validate minimum payment
            minimum_payment = self.validate_number(
                debt.get('minimum_payment', 0),
                f'{debt_name} minimum payment',
                min_val=1,
                max_val=50000
            )
            if minimum_payment is None:
                return False
            
            # Validate debt type
            debt_type = debt.get('debt_type', 'other')
            if debt_type not in self.DEBT_TYPES:
                self.add_error(f"Invalid debt type for {debt_name}: {debt_type}")
                return False
        
        # Validate extra payment
        if inputs.get('extra_payment') is not None:
            extra_payment = self.validate_number(
                inputs['extra_payment'],
                'Extra payment',
                min_val=0,
                max_val=50000
            )
            if extra_payment is None:
                return False
        
        # Validate monthly income if provided
        if inputs.get('monthly_income') is not None:
            monthly_income = self.validate_number(
                inputs['monthly_income'],
                'Monthly income',
                min_val=1000,
                max_val=100000
            )
            if monthly_income is None:
                return False
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Debt Payoff Calculator 2024 - Snowball vs Avalanche Method | Free',
            'description': 'Free debt payoff calculator with snowball and avalanche methods. Create a strategic plan to eliminate debt faster and save money on interest.',
            'keywords': 'debt payoff calculator, debt snowball calculator, debt avalanche calculator, debt elimination calculator, debt reduction planner',
            'canonical': '/calculators/debt-payoff/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Debt Payoff Calculator",
            "description": "Strategic debt elimination planning with snowball and avalanche methods comparison",
            "url": "https://yourcalcsite.com/calculators/debt-payoff/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Multiple debt management",
                "Snowball method calculation",
                "Avalanche method calculation",
                "Strategy comparison and recommendations",
                "Extra payment impact analysis",
                "Debt-to-income ratio analysis",
                "Payoff timeline projections",
                "Interest savings calculations"
            ]
        }