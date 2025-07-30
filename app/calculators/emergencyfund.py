"""
Emergency Fund Calculator
Helps users determine how much to save for emergencies based on monthly expenses,
job security, and family situation with timeline projections.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class EmergencyFundCalculator(BaseCalculator):
    """Calculate recommended emergency fund size and savings timeline."""
    
    # Job security risk factors
    JOB_SECURITY_FACTORS = {
        'very_stable': {
            'multiplier': 3,
            'description': 'Government job, tenured position, very stable industry',
            'risk_level': 'low'
        },
        'stable': {
            'multiplier': 4,
            'description': 'Stable employment, established company, good track record',
            'risk_level': 'medium'
        },
        'moderate': {
            'multiplier': 5,
            'description': 'Average job security, some industry volatility',
            'risk_level': 'medium'
        },
        'unstable': {
            'multiplier': 6,
            'description': 'Freelance, commission-based, volatile industry',
            'risk_level': 'high'
        },
        'very_unstable': {
            'multiplier': 8,
            'description': 'High-risk job, seasonal work, startup environment',
            'risk_level': 'very_high'
        }
    }
    
    # Family situation adjustments
    FAMILY_ADJUSTMENTS = {
        'single_no_dependents': 1.0,
        'single_with_dependents': 1.3,
        'dual_income_no_dependents': 0.8,
        'dual_income_with_dependents': 1.1,
        'single_income_family': 1.5
    }
    
    # Industry risk multipliers
    INDUSTRY_RISK = {
        'healthcare': 0.9,
        'education': 0.9,
        'government': 0.8,
        'utilities': 0.9,
        'technology': 1.1,
        'finance': 1.0,
        'retail': 1.2,
        'hospitality': 1.3,
        'construction': 1.2,
        'entertainment': 1.4,
        'startup': 1.5
    }
    
    # Expense categories for emergency fund calculation
    ESSENTIAL_EXPENSES = [
        'housing', 'utilities', 'groceries', 'transportation',
        'insurance', 'minimum_debt_payments', 'healthcare'
    ]
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate emergency fund recommendations and savings timeline."""
        # Extract basic inputs
        monthly_expenses = Decimal(str(inputs.get('monthly_expenses', 4000)))
        current_emergency_fund = Decimal(str(inputs.get('current_emergency_fund', 0)))
        monthly_savings_capacity = Decimal(str(inputs.get('monthly_savings_capacity', 500)))
        currency = inputs.get('currency', 'USD')
        
        # Risk assessment inputs
        job_security = inputs.get('job_security', 'stable')
        family_situation = inputs.get('family_situation', 'single_no_dependents')
        industry = inputs.get('industry', 'other')
        age = int(inputs.get('age', 35))
        
        # Optional detailed expense breakdown
        expense_breakdown = inputs.get('expense_breakdown', {})
        
        # Calculate essential monthly expenses if breakdown provided
        if expense_breakdown:
            essential_expenses = self._calculate_essential_expenses(expense_breakdown)
        else:
            # Use 80% of total monthly expenses as essential
            essential_expenses = (monthly_expenses * Decimal('0.8')).quantize(Decimal('0.01'))
        
        # Calculate recommended fund size
        fund_recommendations = self._calculate_fund_recommendations(
            essential_expenses, job_security, family_situation, industry, age
        )
        
        # Calculate savings timeline
        savings_timeline = self._calculate_savings_timeline(
            fund_recommendations, current_emergency_fund, monthly_savings_capacity
        )
        
        # Assess current fund adequacy
        adequacy_assessment = self._assess_fund_adequacy(
            current_emergency_fund, essential_expenses, fund_recommendations
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            fund_recommendations, current_emergency_fund, monthly_savings_capacity,
            adequacy_assessment, age
        )
        
        # Calculate high-yield savings projections
        savings_projections = self._calculate_savings_projections(
            current_emergency_fund, monthly_savings_capacity,
            fund_recommendations['recommended_amount']
        )
        
        results = {
            'monthly_expenses': monthly_expenses,
            'essential_monthly_expenses': essential_expenses,
            'current_emergency_fund': current_emergency_fund,
            'monthly_savings_capacity': monthly_savings_capacity,
            'currency': currency,
            'risk_assessment': {
                'job_security': job_security,
                'family_situation': family_situation,
                'industry': industry,
                'overall_risk': self._calculate_overall_risk(job_security, family_situation, industry)
            },
            'fund_recommendations': fund_recommendations,
            'savings_timeline': savings_timeline,
            'adequacy_assessment': adequacy_assessment,
            'recommendations': recommendations,
            'savings_projections': savings_projections,
            'emergency_scenarios': self._calculate_emergency_scenarios(essential_expenses, current_emergency_fund)
        }
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        return results
    
    def _calculate_essential_expenses(self, expense_breakdown: Dict[str, float]) -> Decimal:
        """Calculate essential monthly expenses from detailed breakdown."""
        essential_total = Decimal('0')
        
        for category, amount in expense_breakdown.items():
            if category.lower() in self.ESSENTIAL_EXPENSES:
                essential_total += Decimal(str(amount))
        
        return essential_total.quantize(Decimal('0.01'))
    
    def _calculate_fund_recommendations(self, essential_expenses: Decimal, job_security: str,
                                     family_situation: str, industry: str, age: int) -> Dict[str, Any]:
        """Calculate recommended emergency fund amounts."""
        # Base recommendation from job security
        base_months = self.JOB_SECURITY_FACTORS.get(job_security, self.JOB_SECURITY_FACTORS['stable'])['multiplier']
        
        # Apply family situation adjustment
        family_multiplier = self.FAMILY_ADJUSTMENTS.get(family_situation, 1.0)
        
        # Apply industry risk adjustment
        industry_multiplier = self.INDUSTRY_RISK.get(industry, 1.0)
        
        # Age-based adjustment (older workers may need more time to find new jobs)
        age_multiplier = 1.0
        if age >= 50:
            age_multiplier = 1.2
        elif age >= 40:
            age_multiplier = 1.1
        
        # Calculate final multiplier
        total_multiplier = base_months * family_multiplier * industry_multiplier * age_multiplier
        final_months = round(total_multiplier, 1)
        
        # Calculate amounts
        recommended_amount = (essential_expenses * Decimal(str(final_months))).quantize(Decimal('0.01'))
        minimum_amount = (essential_expenses * 3).quantize(Decimal('0.01'))
        conservative_amount = (essential_expenses * Decimal(str(final_months * 1.2))).quantize(Decimal('0.01'))
        
        return {
            'recommended_months': final_months,
            'recommended_amount': recommended_amount,
            'minimum_amount': minimum_amount,
            'conservative_amount': conservative_amount,
            'calculation_factors': {
                'base_months': base_months,
                'family_multiplier': family_multiplier,
                'industry_multiplier': industry_multiplier,
                'age_multiplier': age_multiplier,
                'final_multiplier': total_multiplier
            }
        }
    
    def _calculate_savings_timeline(self, fund_recommendations: Dict, current_fund: Decimal,
                                  monthly_savings: Decimal) -> Dict[str, Any]:
        """Calculate timeline to reach emergency fund goals."""
        recommended_amount = fund_recommendations['recommended_amount']
        conservative_amount = fund_recommendations['conservative_amount']
        
        if monthly_savings <= 0:
            return {
                'to_minimum': {'months': None, 'message': 'Cannot calculate without monthly savings'},
                'to_recommended': {'months': None, 'message': 'Cannot calculate without monthly savings'},
                'to_conservative': {'months': None, 'message': 'Cannot calculate without monthly savings'}
            }
        
        # Calculate months to reach each goal
        remaining_to_recommended = max(Decimal('0'), recommended_amount - current_fund)
        remaining_to_conservative = max(Decimal('0'), conservative_amount - current_fund)
        remaining_to_minimum = max(Decimal('0'), fund_recommendations['minimum_amount'] - current_fund)
        
        timeline = {}
        
        for goal, remaining in [
            ('minimum', remaining_to_minimum),
            ('recommended', remaining_to_recommended),
            ('conservative', remaining_to_conservative)
        ]:
            if remaining <= 0:
                timeline[f'to_{goal}'] = {
                    'months': 0,
                    'years': 0,
                    'message': 'Goal already achieved!',
                    'monthly_progress': Decimal('0')
                }
            else:
                months = (remaining / monthly_savings).__ceil__()
                years = months / 12
                
                timeline[f'to_{goal}'] = {
                    'months': months,
                    'years': round(float(years), 1),
                    'remaining_amount': remaining,
                    'monthly_progress': monthly_savings,
                    'completion_date': self._add_months_to_today(months)
                }
        
        return timeline
    
    def _assess_fund_adequacy(self, current_fund: Decimal, essential_expenses: Decimal,
                            fund_recommendations: Dict) -> Dict[str, Any]:
        """Assess the adequacy of current emergency fund."""
        if essential_expenses == 0:
            months_covered = Decimal('0')
        else:
            months_covered = (current_fund / essential_expenses).quantize(Decimal('0.1'))
        
        recommended_months = Decimal(str(fund_recommendations['recommended_months']))
        
        # Determine adequacy level
        if months_covered < 1:
            adequacy_level = 'critical'
            status_message = 'Your emergency fund is critically low'
        elif months_covered < 3:
            adequacy_level = 'insufficient'
            status_message = 'Your emergency fund needs immediate attention'
        elif months_covered < recommended_months:
            adequacy_level = 'partial'
            status_message = 'You have a good start but need to build more'
        elif months_covered >= recommended_months:
            adequacy_level = 'adequate'
            status_message = 'Your emergency fund meets recommendations'
        else:
            adequacy_level = 'excellent'
            status_message = 'Your emergency fund exceeds recommendations'
        
        return {
            'months_covered': months_covered,
            'adequacy_level': adequacy_level,
            'status_message': status_message,
            'percentage_of_goal': (months_covered / recommended_months * 100).quantize(Decimal('0.1')) if recommended_months > 0 else Decimal('0'),
            'gap_amount': max(Decimal('0'), fund_recommendations['recommended_amount'] - current_fund)
        }
    
    def _generate_recommendations(self, fund_recommendations: Dict, current_fund: Decimal,
                                monthly_savings: Decimal, adequacy: Dict, age: int) -> List[Dict]:
        """Generate personalized emergency fund recommendations."""
        recommendations = []
        
        # Fund size recommendations
        if adequacy['adequacy_level'] in ['critical', 'insufficient']:
            recommendations.append({
                'type': 'urgent',
                'priority': 'critical',
                'title': 'Build Emergency Fund Immediately',
                'message': f"You currently have {adequacy['months_covered']} months of expenses saved. Aim for at least 3 months.",
                'action': 'Cut discretionary spending and redirect money to emergency savings'
            })
        
        # Savings rate recommendations
        if monthly_savings < current_fund * Decimal('0.1'):  # Less than 10% of current fund per month
            recommendations.append({
                'type': 'savings_rate',
                'priority': 'high',
                'title': 'Increase Monthly Savings',
                'message': 'Your monthly savings rate is quite low relative to your goal.',
                'action': f"Try to save at least ${fund_recommendations['recommended_amount'] / 24:.0f} per month (2-year goal)"
            })
        
        # High-yield savings recommendation
        if current_fund > 1000:
            recommendations.append({
                'type': 'optimization',
                'priority': 'medium',
                'title': 'Optimize Emergency Fund Location',
                'message': 'Keep your emergency fund in a high-yield savings account.',
                'action': 'Look for accounts offering 4-5% APY while maintaining liquidity'
            })
        
        # Age-specific recommendations
        if age >= 50:
            recommendations.append({
                'type': 'age_specific',
                'priority': 'medium',
                'title': 'Consider Extended Job Search Timeline',
                'message': 'Older workers may face longer job search periods.',
                'action': 'Consider building 6-8 months of expenses for additional security'
            })
        elif age < 30:
            recommendations.append({
                'type': 'age_specific',
                'priority': 'low',
                'title': 'Start Building Good Habits',
                'message': 'Starting early gives you a huge advantage.',
                'action': 'Even $50/month will build significant savings over time'
            })
        
        # Goal achievement recommendations
        if adequacy['adequacy_level'] == 'adequate':
            recommendations.append({
                'type': 'maintenance',
                'priority': 'low',
                'title': 'Maintain and Protect Your Fund',
                'message': 'Great job reaching your emergency fund goal!',
                'action': 'Only use for true emergencies and replenish immediately after use'
            })
        
        return recommendations
    
    def _calculate_savings_projections(self, current_fund: Decimal, monthly_savings: Decimal,
                                     target_amount: Decimal) -> Dict[str, Any]:
        """Calculate projections with different savings rates and interest."""
        projections = {}
        interest_rates = [Decimal('0.01'), Decimal('0.03'), Decimal('0.045')]  # 1%, 3%, 4.5%
        savings_multipliers = [Decimal('0.5'), Decimal('1.0'), Decimal('1.5'), Decimal('2.0')]
        
        for rate in interest_rates:
            rate_projections = []
            for multiplier in savings_multipliers:
                adjusted_savings = monthly_savings * multiplier
                months_to_goal = self._calculate_months_with_interest(
                    current_fund, adjusted_savings, target_amount, rate
                )
                
                rate_projections.append({
                    'monthly_savings': adjusted_savings,
                    'months_to_goal': months_to_goal,
                    'years_to_goal': round(float(months_to_goal / 12), 1) if months_to_goal else None,
                    'total_interest_earned': self._calculate_interest_earned(
                        current_fund, adjusted_savings, months_to_goal, rate
                    ) if months_to_goal else Decimal('0')
                })
            
            projections[f'{int(rate * 100)}percent'] = rate_projections
        
        return projections
    
    def _calculate_emergency_scenarios(self, essential_expenses: Decimal, 
                                     current_fund: Decimal) -> List[Dict]:
        """Calculate how long current fund would last in different scenarios."""
        scenarios = []
        
        # Different expense reduction scenarios
        expense_scenarios = [
            {'name': 'Full Expenses', 'multiplier': 1.0, 'description': 'No expense reduction'},
            {'name': 'Reduced Expenses', 'multiplier': 0.8, 'description': '20% expense reduction'},
            {'name': 'Bare Minimum', 'multiplier': 0.6, 'description': '40% expense reduction'},
            {'name': 'Survival Mode', 'multiplier': 0.4, 'description': '60% expense reduction'}
        ]
        
        for scenario in expense_scenarios:
            adjusted_expenses = essential_expenses * Decimal(str(scenario['multiplier']))
            if adjusted_expenses > 0:
                months_coverage = (current_fund / adjusted_expenses).quantize(Decimal('0.1'))
            else:
                months_coverage = Decimal('999')  # Infinite if no expenses
            
            scenarios.append({
                'name': scenario['name'],
                'description': scenario['description'],
                'monthly_expenses': adjusted_expenses,
                'months_coverage': months_coverage,
                'coverage_assessment': self._assess_coverage_duration(months_coverage)
            })
        
        return scenarios
    
    def _calculate_overall_risk(self, job_security: str, family_situation: str, industry: str) -> str:
        """Calculate overall financial risk level."""
        job_risk = self.JOB_SECURITY_FACTORS.get(job_security, {}).get('risk_level', 'medium')
        family_risk = 'high' if 'dependents' in family_situation else 'medium'
        industry_multiplier = self.INDUSTRY_RISK.get(industry, 1.0)
        
        # Simple risk calculation
        risk_score = 0
        if job_risk == 'very_high':
            risk_score += 4
        elif job_risk == 'high':
            risk_score += 3
        elif job_risk == 'medium':
            risk_score += 2
        else:
            risk_score += 1
        
        if family_risk == 'high':
            risk_score += 2
        else:
            risk_score += 1
        
        if industry_multiplier >= 1.3:
            risk_score += 2
        elif industry_multiplier >= 1.1:
            risk_score += 1
        
        if risk_score >= 7:
            return 'very_high'
        elif risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_months_with_interest(self, current_amount: Decimal, monthly_savings: Decimal,
                                      target_amount: Decimal, annual_rate: Decimal) -> int:
        """Calculate months needed to reach target with compound interest."""
        if monthly_savings <= 0:
            return None
        
        monthly_rate = annual_rate / 12
        balance = current_amount
        months = 0
        
        while balance < target_amount and months < 600:  # Max 50 years
            balance *= (1 + monthly_rate)
            balance += monthly_savings
            months += 1
        
        return months if balance >= target_amount else None
    
    def _calculate_interest_earned(self, starting_amount: Decimal, monthly_savings: Decimal,
                                 months: int, annual_rate: Decimal) -> Decimal:
        """Calculate total interest earned over the savings period."""
        if not months:
            return Decimal('0')
        
        monthly_rate = annual_rate / 12
        balance = starting_amount
        total_deposits = starting_amount + (monthly_savings * months)
        
        for _ in range(months):
            balance *= (1 + monthly_rate)
            balance += monthly_savings
        
        return (balance - total_deposits).quantize(Decimal('0.01'))
    
    def _assess_coverage_duration(self, months: Decimal) -> str:
        """Assess the quality of coverage duration."""
        if months < 1:
            return 'critical'
        elif months < 3:
            return 'insufficient'
        elif months < 6:
            return 'adequate'
        else:
            return 'excellent'
    
    def _add_months_to_today(self, months: int) -> str:
        """Add months to current date and return formatted string."""
        from datetime import datetime, timedelta
        import calendar
        
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        target_month = current_month + months
        target_year = current_year + (target_month - 1) // 12
        target_month = ((target_month - 1) % 12) + 1
        
        return f"{calendar.month_name[target_month]} {target_year}"
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Format main amounts
        monetary_fields = [
            'monthly_expenses', 'essential_monthly_expenses', 
            'current_emergency_fund', 'monthly_savings_capacity'
        ]
        
        for field in monetary_fields:
            formatted[field] = currency_service.format_currency(results[field], currency)
        
        # Format fund recommendations
        fund_rec = results['fund_recommendations']
        formatted['recommended_amount'] = currency_service.format_currency(fund_rec['recommended_amount'], currency)
        formatted['minimum_amount'] = currency_service.format_currency(fund_rec['minimum_amount'], currency)
        formatted['conservative_amount'] = currency_service.format_currency(fund_rec['conservative_amount'], currency)
        
        # Format adequacy assessment
        adequacy = results['adequacy_assessment']
        formatted['gap_amount'] = currency_service.format_currency(adequacy['gap_amount'], currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate monthly expenses
        monthly_expenses = self.validate_number(
            inputs.get('monthly_expenses', 4000),
            'Monthly expenses',
            min_val=500,
            max_val=50000
        )
        if monthly_expenses is None:
            return False
        
        # Validate current emergency fund
        if inputs.get('current_emergency_fund') is not None:
            self.validate_number(
                inputs['current_emergency_fund'],
                'Current emergency fund',
                min_val=0,
                max_val=1000000
            )
        
        # Validate monthly savings capacity
        monthly_savings = self.validate_number(
            inputs.get('monthly_savings_capacity', 500),
            'Monthly savings capacity',
            min_val=0,
            max_val=10000
        )
        if monthly_savings is None:
            return False
        
        # Validate age
        if inputs.get('age'):
            age = self.validate_number(
                inputs['age'],
                'Age',
                min_val=18,
                max_val=80
            )
            if age is None:
                return False
        
        # Validate job security
        job_security = inputs.get('job_security', 'stable')
        if job_security not in self.JOB_SECURITY_FACTORS:
            self.add_error(f"Invalid job security level: {job_security}")
        
        # Validate family situation
        family_situation = inputs.get('family_situation', 'single_no_dependents')
        if family_situation not in self.FAMILY_ADJUSTMENTS:
            self.add_error(f"Invalid family situation: {family_situation}")
        
        # Validate expense breakdown if provided
        if 'expense_breakdown' in inputs:
            breakdown = inputs['expense_breakdown']
            if not isinstance(breakdown, dict):
                self.add_error("Expense breakdown must be a dictionary")
                return False
            
            for category, amount in breakdown.items():
                if not isinstance(amount, (int, float)) or amount < 0:
                    self.add_error(f"Invalid expense amount for {category}")
                    return False
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Emergency Fund Calculator 2024 - How Much Should You Save? | Free',
            'description': 'Free emergency fund calculator. Determine how much you need to save for emergencies based on your job security, family situation, and expenses.',
            'keywords': 'emergency fund calculator, emergency savings calculator, how much emergency fund, emergency fund size, financial emergency planning',
            'canonical': '/calculators/emergency-fund/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Emergency Fund Calculator",
            "description": "Calculate how much you should save for emergencies based on your job security and family situation",
            "url": "https://yourcalcsite.com/calculators/emergency-fund/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Personalized emergency fund recommendations",
                "Job security risk assessment",
                "Family situation analysis",
                "Savings timeline projections",
                "High-yield savings calculations",
                "Emergency scenario planning",
                "Fund adequacy assessment",
                "Multi-currency support"
            ]
        }