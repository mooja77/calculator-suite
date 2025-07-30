"""
Takaful Calculator (Islamic Insurance)

Calculates Islamic insurance (Takaful) with support for:
- Contribution calculations
- Surplus sharing (mudharabah model)
- Family vs general Takaful
- Coverage amount determination
- Wakalah and Mudharabah models
- Sharia-compliant insurance principles
"""

from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class TakafulCalculator(BaseCalculator):
    """Takaful Calculator for Islamic insurance following Sharia principles"""
    
    # Takaful contribution rates (varies by operator and coverage)
    CONTRIBUTION_RATES = {
        'family_life': {'rate': Decimal('0.015'), 'description': 'Family Takaful (Life) - typical rate'},
        'family_savings': {'rate': Decimal('0.025'), 'description': 'Family Takaful with savings - typical rate'},
        'general_motor': {'rate': Decimal('0.04'), 'description': 'Motor Takaful - typical rate'},
        'general_property': {'rate': Decimal('0.002'), 'description': 'Property Takaful - typical rate'},
        'general_health': {'rate': Decimal('0.08'), 'description': 'Health Takaful - typical rate'},
        'marine': {'rate': Decimal('0.003'), 'description': 'Marine Takaful - typical rate'}
    }
    
    # Surplus sharing ratios (participant : operator)
    SURPLUS_SHARING_RATIOS = {
        'mudharabah_90_10': {'participant': Decimal('0.90'), 'operator': Decimal('0.10')},
        'mudharabah_80_20': {'participant': Decimal('0.80'), 'operator': Decimal('0.20')},
        'mudharabah_70_30': {'participant': Decimal('0.70'), 'operator': Decimal('0.30')},
        'wakalah_100_0': {'participant': Decimal('1.00'), 'operator': Decimal('0.00')}  # Pure Wakalah
    }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        self.clear_errors()
        
        # Validate calculation type
        calc_type = inputs.get('calculation_type', 'contribution')
        if calc_type not in ['contribution', 'coverage', 'surplus_sharing', 'comparison']:
            self.add_error("Invalid calculation type")
        
        # Validate Takaful type
        takaful_type = inputs.get('takaful_type', 'family_life')
        if takaful_type not in self.CONTRIBUTION_RATES:
            self.add_error("Invalid Takaful type")
        
        # Validate coverage amount or sum covered
        if calc_type in ['contribution', 'surplus_sharing']:
            sum_covered = self.validate_number(inputs.get('sum_covered', 0), 'Sum covered/insured', min_val=1000)
            if sum_covered is None:
                return False
        
        # Validate contribution amount for coverage calculation
        if calc_type == 'coverage':
            contribution = self.validate_number(inputs.get('contribution_amount', 0), 'Contribution amount', min_val=10)
            if contribution is None:
                return False
        
        # Validate age for family Takaful
        if takaful_type.startswith('family'):
            age = self.validate_number(inputs.get('age', 25), 'Age', min_val=18, max_val=70)
            if age is None:
                return False
        
        # Validate term for family Takaful
        if takaful_type.startswith('family'):
            term = self.validate_number(inputs.get('term_years', 10), 'Term (years)', min_val=5, max_val=40)
            if term is None:
                return False
        
        # Validate Takaful model
        takaful_model = inputs.get('takaful_model', 'mudharabah')
        if takaful_model not in ['mudharabah', 'wakalah', 'hybrid']:
            self.add_error("Invalid Takaful model")
        
        return len(self.errors) == 0
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Takaful calculations"""
        
        if not self.validate_inputs(inputs):
            return {'error': self.errors}
        
        calc_type = inputs.get('calculation_type', 'contribution')
        takaful_type = inputs.get('takaful_type', 'family_life')
        takaful_model = inputs.get('takaful_model', 'mudharabah')
        currency = inputs.get('currency', 'USD')
        
        result = {
            'calculation_type': calc_type,
            'takaful_type': takaful_type,
            'takaful_model': takaful_model,
            'currency': currency
        }
        
        if calc_type == 'contribution':
            # Calculate contribution amount
            sum_covered = Decimal(str(inputs.get('sum_covered', 0)))
            age = inputs.get('age', 25) if takaful_type.startswith('family') else None
            term_years = inputs.get('term_years', 10) if takaful_type.startswith('family') else 1
            
            contribution_result = self._calculate_contribution(
                sum_covered, takaful_type, age, term_years, takaful_model
            )
            result.update(contribution_result)
            
        elif calc_type == 'coverage':
            # Calculate coverage amount based on contribution
            contribution_amount = Decimal(str(inputs.get('contribution_amount', 0)))
            age = inputs.get('age', 25) if takaful_type.startswith('family') else None
            term_years = inputs.get('term_years', 10) if takaful_type.startswith('family') else 1
            
            coverage_result = self._calculate_coverage(
                contribution_amount, takaful_type, age, term_years, takaful_model
            )
            result.update(coverage_result)
            
        elif calc_type == 'surplus_sharing':
            # Calculate surplus sharing
            sum_covered = Decimal(str(inputs.get('sum_covered', 0)))
            total_contributions = Decimal(str(inputs.get('total_contributions', 0)))
            total_claims = Decimal(str(inputs.get('total_claims', 0)))
            expenses = Decimal(str(inputs.get('expenses', 0)))
            sharing_ratio = inputs.get('sharing_ratio', 'mudharabah_90_10')
            
            surplus_result = self._calculate_surplus_sharing(
                total_contributions, total_claims, expenses, sharing_ratio
            )
            result.update(surplus_result)
            
        elif calc_type == 'comparison':
            # Compare with conventional insurance
            sum_covered = Decimal(str(inputs.get('sum_covered', 0)))
            conventional_premium = Decimal(str(inputs.get('conventional_premium', 0)))
            
            comparison_result = self._calculate_comparison(
                sum_covered, takaful_type, conventional_premium, takaful_model
            )
            result.update(comparison_result)
        
        # Add Takaful principles and model information
        result['takaful_principles'] = self._get_takaful_principles()
        result['model_explanation'] = self._get_model_explanation(takaful_model)
        result['type_explanation'] = self._get_type_explanation(takaful_type)
        
        return result
    
    def _calculate_contribution(self, sum_covered: Decimal, takaful_type: str, 
                               age: int, term_years: int, model: str) -> Dict[str, Any]:
        """Calculate Takaful contribution"""
        
        base_rate = self.CONTRIBUTION_RATES[takaful_type]['rate']
        
        # Apply age factor for family Takaful
        if takaful_type.startswith('family') and age:
            age_factor = self._get_age_factor(age)
            adjusted_rate = base_rate * age_factor
        else:
            adjusted_rate = base_rate
        
        # Calculate annual contribution
        annual_contribution = sum_covered * adjusted_rate
        
        # Apply model adjustments
        if model == 'wakalah':
            # Wakalah model typically has fixed fee structure
            wakalah_fee = annual_contribution * Decimal('0.20')  # 20% management fee
            net_contribution = annual_contribution - wakalah_fee
        else:
            wakalah_fee = Decimal('0')
            net_contribution = annual_contribution
        
        # Calculate periodic contributions
        monthly_contribution = annual_contribution / 12
        quarterly_contribution = annual_contribution / 4
        
        result = {
            'sum_covered': float(sum_covered.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'annual_contribution': float(annual_contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'monthly_contribution': float(monthly_contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'quarterly_contribution': float(quarterly_contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'base_rate_percentage': float(base_rate * 100),
            'net_contribution': float(net_contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }
        
        if takaful_type.startswith('family'):
            result.update({
                'age': age,
                'term_years': term_years,
                'age_factor': float(age_factor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'total_contributions_over_term': float((annual_contribution * term_years).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        if model == 'wakalah':
            result['wakalah_fee'] = float(wakalah_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
        return result
    
    def _calculate_coverage(self, contribution: Decimal, takaful_type: str, 
                           age: int, term_years: int, model: str) -> Dict[str, Any]:
        """Calculate coverage amount based on contribution"""
        
        base_rate = self.CONTRIBUTION_RATES[takaful_type]['rate']
        
        # Apply age factor for family Takaful
        if takaful_type.startswith('family') and age:
            age_factor = self._get_age_factor(age)
            adjusted_rate = base_rate * age_factor
        else:
            adjusted_rate = base_rate
        
        # Calculate coverage
        sum_covered = contribution / adjusted_rate
        
        result = {
            'contribution_amount': float(contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'sum_covered': float(sum_covered.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'effective_rate_percentage': float(adjusted_rate * 100)
        }
        
        if takaful_type.startswith('family'):
            result.update({
                'age': age,
                'term_years': term_years
            })
        
        return result
    
    def _calculate_surplus_sharing(self, contributions: Decimal, claims: Decimal, 
                                  expenses: Decimal, sharing_ratio: str) -> Dict[str, Any]:
        """Calculate surplus sharing in Mudharabah model"""
        
        # Calculate surplus
        total_expenses = expenses
        total_claims_and_expenses = claims + total_expenses
        surplus = contributions - total_claims_and_expenses
        
        # Get sharing ratio
        ratios = self.SURPLUS_SHARING_RATIOS.get(sharing_ratio, self.SURPLUS_SHARING_RATIOS['mudharabah_90_10'])
        
        if surplus > 0:
            participant_share = surplus * ratios['participant']
            operator_share = surplus * ratios['operator']
        else:
            # No surplus sharing if there's a deficit
            participant_share = Decimal('0')
            operator_share = Decimal('0')
        
        result = {
            'total_contributions': float(contributions.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_claims': float(claims.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_expenses': float(total_expenses.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'surplus_deficit': float(surplus.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'participant_share': float(participant_share.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'operator_share': float(operator_share.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'sharing_ratio': sharing_ratio,
            'participant_percentage': float(ratios['participant'] * 100),
            'operator_percentage': float(ratios['operator'] * 100),
            'has_surplus': surplus > 0
        }
        
        return result
    
    def _calculate_comparison(self, sum_covered: Decimal, takaful_type: str, 
                             conventional_premium: Decimal, model: str) -> Dict[str, Any]:
        """Compare Takaful with conventional insurance"""
        
        # Calculate equivalent Takaful contribution
        base_rate = self.CONTRIBUTION_RATES[takaful_type]['rate']
        takaful_contribution = sum_covered * base_rate
        
        # Calculate difference
        difference = conventional_premium - takaful_contribution
        percentage_difference = (difference / conventional_premium * 100) if conventional_premium > 0 else 0
        
        result = {
            'sum_covered': float(sum_covered.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'takaful_contribution': float(takaful_contribution.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'conventional_premium': float(conventional_premium.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'difference': float(difference.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'percentage_difference': float(Decimal(str(percentage_difference)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'takaful_more_expensive': takaful_contribution > conventional_premium,
            'savings_with_takaful': float(abs(difference).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) if difference > 0 else 0
        }
        
        return result
    
    def _get_age_factor(self, age: int) -> Decimal:
        """Calculate age factor for family Takaful"""
        # Simplified age factor calculation
        if age <= 30:
            return Decimal('0.8')
        elif age <= 40:
            return Decimal('1.0')
        elif age <= 50:
            return Decimal('1.5')
        elif age <= 60:
            return Decimal('2.0')
        else:
            return Decimal('3.0')
    
    def _get_takaful_principles(self) -> Dict[str, Any]:
        """Get Islamic insurance principles"""
        return {
            'mutual_guarantee': 'Participants mutually guarantee each other',
            'risk_sharing': 'Risks and losses are shared among participants',
            'sharia_compliance': 'Operates according to Islamic law principles',
            'prohibited_elements': {
                'gharar': 'Excessive uncertainty - minimized through clear contracts',
                'maysir': 'Gambling - avoided through mutual cooperation structure',
                'riba': 'Interest - no interest-based investments in fund management'
            },
            'core_concepts': [
                'Ta\'awun (mutual assistance)',
                'Takaful (mutual guarantee)', 
                'Tabarru\' (donation/contribution for mutual help)',
                'Halal investments only',
                'Transparency in operations'
            ]
        }
    
    def _get_model_explanation(self, model: str) -> Dict[str, Any]:
        """Get explanation of Takaful model"""
        explanations = {
            'mudharabah': {
                'description': 'Profit-sharing partnership between participants and operator',
                'operator_role': 'Manages the Takaful fund and shares in surplus',
                'participant_role': 'Contributes to fund and shares in surplus',
                'surplus_sharing': 'Surplus shared according to pre-agreed ratio',
                'deficit_handling': 'Operator may provide Qard Hasan (benevolent loan)',
                'advantages': ['Aligned interests', 'Profit sharing opportunity', 'Risk mitigation'],
                'considerations': ['Variable returns', 'Complex accounting', 'Regulatory oversight needed']
            },
            'wakalah': {
                'description': 'Agency model where operator acts as agent for participants',
                'operator_role': 'Manages fund for fixed fee, no share in surplus',
                'participant_role': 'Owns the fund, receives all surplus',
                'surplus_sharing': 'All surplus belongs to participants',
                'deficit_handling': 'Participants bear deficit or operator provides Qard Hasan',
                'advantages': ['Full surplus to participants', 'Transparent fee structure', 'Clear separation'],
                'considerations': ['Operator incentive alignment', 'Fee negotiation', 'Deficit management']
            },
            'hybrid': {
                'description': 'Combination of Mudharabah and Wakalah models',
                'operator_role': 'Receives management fee plus share of surplus',
                'participant_role': 'Pays fixed fee and shares remaining surplus',
                'surplus_sharing': 'Surplus shared after deducting Wakalah fee',
                'advantages': ['Balanced approach', 'Stable operator income', 'Participant benefits'],
                'considerations': ['More complex structure', 'Dual fee calculation', 'Regulatory complexity']
            }
        }
        
        return explanations.get(model, {})
    
    def _get_type_explanation(self, takaful_type: str) -> Dict[str, str]:
        """Get explanation of Takaful type"""
        explanations = {
            'family_life': 'Family Takaful for life coverage - provides financial protection for family in case of death',
            'family_savings': 'Family Takaful with savings component - combines protection with investment/savings',
            'general_motor': 'Motor Takaful - covers vehicles against accident, theft, and third-party liability',
            'general_property': 'Property Takaful - covers buildings and contents against fire, theft, and natural disasters',
            'general_health': 'Health Takaful - covers medical expenses and hospitalization costs',
            'marine': 'Marine Takaful - covers ships, cargo, and marine-related risks'
        }
        
        return {
            'type': takaful_type,
            'description': explanations.get(takaful_type, 'General Takaful coverage')
        }
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO metadata"""
        return {
            'title': 'Takaful Calculator - Islamic Insurance Calculator | Sharia-Compliant Coverage',
            'description': 'Free Takaful calculator for Islamic insurance. Calculate contributions for family and general Takaful, surplus sharing, and compare with conventional insurance. Sharia-compliant.',
            'keywords': 'Takaful calculator, Islamic insurance, Sharia compliant insurance, Mudharabah, Wakalah, family takaful, general takaful, surplus sharing',
            'canonical': '/calculators/takaful'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Takaful Calculator",
            "description": "Calculate Islamic insurance (Takaful) contributions and coverage following Sharia principles",
            "url": "https://calculatorapp.com/calculators/takaful",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Family Takaful calculations",
                "General Takaful calculations",
                "Mudharabah model support",
                "Wakalah model support",
                "Surplus sharing calculations",
                "Conventional insurance comparison",
                "Age-based adjustments",
                "Multi-currency support",
                "Sharia compliance information"
            ]
        }