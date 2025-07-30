"""
Budget Calculator with 50/30/20 Rule
Helps users plan monthly budgets using the popular 50/30/20 budgeting method
with customizable categories and overspending warnings.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class BudgetCalculator(BaseCalculator):
    """Calculate monthly budget using 50/30/20 rule with custom categories."""
    
    # Default budget category allocations
    DEFAULT_CATEGORIES = {
        'needs': {
            'percentage': 50,
            'categories': [
                {'name': 'Housing', 'percentage': 65, 'description': 'Rent/mortgage, utilities, insurance'},
                {'name': 'Transportation', 'percentage': 15, 'description': 'Car payment, fuel, maintenance, transit'},
                {'name': 'Groceries', 'percentage': 12, 'description': 'Essential food shopping'},
                {'name': 'Healthcare', 'percentage': 5, 'description': 'Insurance premiums, medications'},
                {'name': 'Minimum Debt Payments', 'percentage': 3, 'description': 'Required loan/credit card payments'}
            ]
        },
        'wants': {
            'percentage': 30,
            'categories': [
                {'name': 'Dining Out', 'percentage': 25, 'description': 'Restaurants, takeout, delivery'},
                {'name': 'Entertainment', 'percentage': 20, 'description': 'Movies, streaming, hobbies'},
                {'name': 'Shopping', 'percentage': 20, 'description': 'Clothing, electronics, non-essentials'},
                {'name': 'Personal Care', 'percentage': 15, 'description': 'Haircuts, cosmetics, gym memberships'},
                {'name': 'Travel', 'percentage': 10, 'description': 'Vacations, weekend trips'},
                {'name': 'Miscellaneous', 'percentage': 10, 'description': 'Other discretionary spending'}
            ]
        },
        'savings': {
            'percentage': 20,
            'categories': [
                {'name': 'Emergency Fund', 'percentage': 40, 'description': '3-6 months of expenses'},
                {'name': 'Retirement', 'percentage': 35, 'description': '401k, IRA contributions'},
                {'name': 'Short-term Savings', 'percentage': 15, 'description': 'Vacation, major purchases'},
                {'name': 'Debt Payoff', 'percentage': 10, 'description': 'Extra payments beyond minimums'}
            ]
        }
    }
    
    # National averages for comparison (US data)
    NATIONAL_AVERAGES = {
        'needs': {
            'housing': 28.0,
            'transportation': 16.0,
            'groceries': 12.0,
            'healthcare': 8.0,
            'utilities': 6.0
        },
        'wants': {
            'dining_out': 13.0,
            'entertainment': 5.0,
            'shopping': 7.0,
            'personal_care': 3.0
        },
        'savings_rate': 13.0  # National average savings rate
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget allocation using 50/30/20 rule."""
        # Extract basic inputs
        monthly_income = Decimal(str(inputs.get('monthly_income', 5000)))
        currency = inputs.get('currency', 'USD')
        
        # Custom allocations (optional overrides)
        needs_percentage = Decimal(str(inputs.get('needs_percentage', 50))) / 100
        wants_percentage = Decimal(str(inputs.get('wants_percentage', 30))) / 100
        savings_percentage = Decimal(str(inputs.get('savings_percentage', 20))) / 100
        
        # Validate total percentage
        total_percentage = needs_percentage + wants_percentage + savings_percentage
        if abs(total_percentage - 1) > Decimal('0.01'):
            # Auto-adjust to 100%
            adjustment_factor = Decimal('1') / total_percentage
            needs_percentage *= adjustment_factor
            wants_percentage *= adjustment_factor
            savings_percentage *= adjustment_factor
        
        # Calculate main budget allocations
        needs_budget = (monthly_income * needs_percentage).quantize(Decimal('0.01'))
        wants_budget = (monthly_income * wants_percentage).quantize(Decimal('0.01'))
        savings_budget = (monthly_income * savings_percentage).quantize(Decimal('0.01'))
        
        # Process custom category inputs
        custom_categories = inputs.get('custom_categories', {})
        
        # Calculate detailed category breakdowns
        needs_breakdown = self._calculate_category_breakdown(
            needs_budget, 'needs', custom_categories.get('needs', {})
        )
        wants_breakdown = self._calculate_category_breakdown(
            wants_budget, 'wants', custom_categories.get('wants', {})
        )
        savings_breakdown = self._calculate_category_breakdown(
            savings_budget, 'savings', custom_categories.get('savings', {})
        )
        
        # Calculate spending analysis if actual spending provided
        spending_analysis = None
        if inputs.get('actual_spending'):
            spending_analysis = self._analyze_actual_spending(
                inputs['actual_spending'], 
                {
                    'needs': needs_budget,
                    'wants': wants_budget,
                    'savings': savings_budget
                },
                monthly_income
            )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            monthly_income, needs_percentage, wants_percentage, 
            savings_percentage, spending_analysis
        )
        
        # Compare with national averages
        national_comparison = self._compare_with_national_averages(
            monthly_income, needs_budget, wants_budget, savings_budget
        )
        
        results = {
            'monthly_income': monthly_income,
            'currency': currency,
            'budget_rule': f"{int(needs_percentage * 100)}/{int(wants_percentage * 100)}/{int(savings_percentage * 100)}",
            'allocations': {
                'needs': {
                    'amount': needs_budget,
                    'percentage': needs_percentage * 100,
                    'breakdown': needs_breakdown
                },
                'wants': {
                    'amount': wants_budget,
                    'percentage': wants_percentage * 100,
                    'breakdown': wants_breakdown
                },
                'savings': {
                    'amount': savings_budget,
                    'percentage': savings_percentage * 100,
                    'breakdown': savings_breakdown
                }
            },
            'annual_projections': {
                'needs': (needs_budget * 12).quantize(Decimal('0.01')),
                'wants': (wants_budget * 12).quantize(Decimal('0.01')),
                'savings': (savings_budget * 12).quantize(Decimal('0.01')),
                'total_savings': (savings_budget * 12).quantize(Decimal('0.01'))
            },
            'recommendations': recommendations,
            'national_comparison': national_comparison
        }
        
        # Add spending analysis if provided
        if spending_analysis:
            results['spending_analysis'] = spending_analysis
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        return results
    
    def _calculate_category_breakdown(self, total_budget: Decimal, category_type: str, 
                                    custom_allocations: Dict[str, float]) -> List[Dict]:
        """Calculate detailed breakdown for a budget category."""
        default_categories = self.DEFAULT_CATEGORIES[category_type]['categories']
        breakdown = []
        
        for category in default_categories:
            category_name = category['name']
            
            # Use custom allocation if provided, otherwise use default
            if category_name in custom_allocations:
                percentage = Decimal(str(custom_allocations[category_name])) / 100
            else:
                percentage = Decimal(str(category['percentage'])) / 100
            
            amount = (total_budget * percentage).quantize(Decimal('0.01'))
            
            breakdown.append({
                'name': category_name,
                'amount': amount,
                'percentage': percentage * 100,
                'description': category['description'],
                'annual_amount': (amount * 12).quantize(Decimal('0.01'))
            })
        
        return breakdown
    
    def _analyze_actual_spending(self, actual_spending: Dict[str, float], 
                               budget_allocations: Dict[str, Decimal],
                               monthly_income: Decimal) -> Dict[str, Any]:
        """Analyze actual spending vs budget allocations."""
        analysis = {
            'categories': {},
            'total_spent': Decimal('0'),
            'total_over_under': Decimal('0'),
            'warnings': [],
            'achievements': []
        }
        
        for category, budgeted in budget_allocations.items():
            spent = Decimal(str(actual_spending.get(category, 0)))
            difference = spent - budgeted
            percentage_difference = ((difference / budgeted * 100) if budgeted > 0 else 0)
            
            analysis['categories'][category] = {
                'budgeted': budgeted,
                'spent': spent,
                'difference': difference,
                'percentage_difference': percentage_difference.quantize(Decimal('0.1')),
                'status': 'over' if difference > 0 else 'under' if difference < 0 else 'on_track'
            }
            
            analysis['total_spent'] += spent
            analysis['total_over_under'] += difference
            
            # Generate warnings for overspending
            if difference > budgeted * Decimal('0.1'):  # 10% over budget
                analysis['warnings'].append({
                    'category': category,
                    'message': f"You're spending {percentage_difference:.1f}% over budget in {category}",
                    'severity': 'high' if percentage_difference > 25 else 'medium'
                })
            
            # Generate achievements for staying under budget
            if difference < -budgeted * Decimal('0.05') and category != 'savings':  # 5% under budget
                analysis['achievements'].append({
                    'category': category,
                    'message': f"Great job staying {abs(percentage_difference):.1f}% under budget in {category}!",
                    'savings': abs(difference)
                })
        
        # Overall analysis
        total_budget = sum(budget_allocations.values())
        analysis['overall'] = {
            'total_budgeted': total_budget,
            'total_spent': analysis['total_spent'],
            'remaining': monthly_income - analysis['total_spent'],
            'savings_rate': ((monthly_income - analysis['total_spent']) / monthly_income * 100).quantize(Decimal('0.1'))
        }
        
        return analysis
    
    def _generate_recommendations(self, income: Decimal, needs_pct: Decimal, 
                                wants_pct: Decimal, savings_pct: Decimal,
                                spending_analysis: Dict = None) -> List[Dict]:
        """Generate personalized budget recommendations."""
        recommendations = []
        
        # Basic rule compliance
        if savings_pct < Decimal('0.2'):
            recommendations.append({
                'type': 'savings',
                'priority': 'high',
                'title': 'Increase Your Savings Rate',
                'message': f"Your savings rate is {savings_pct * 100:.0f}%. Try to reach 20% for better financial security.",
                'action': 'Review your wants category for potential cuts'
            })
        
        if needs_pct > Decimal('0.6'):
            recommendations.append({
                'type': 'needs',
                'priority': 'high',
                'title': 'Reduce Fixed Expenses',
                'message': f"Your needs are {needs_pct * 100:.0f}% of income. Consider ways to reduce fixed costs.",
                'action': 'Look into refinancing, moving, or switching providers'
            })
        
        # Income-based recommendations
        if income < 3000:
            recommendations.append({
                'type': 'income',
                'priority': 'high',
                'title': 'Focus on Increasing Income',
                'message': 'With limited income, prioritize emergency fund before other savings goals.',
                'action': 'Consider side hustles or skill development for better-paying jobs'
            })
        elif income > 8000:
            recommendations.append({
                'type': 'investment',
                'priority': 'medium',
                'title': 'Maximize Tax-Advantaged Accounts',
                'message': 'You have good income. Make sure to maximize 401k and IRA contributions.',
                'action': 'Consider increasing retirement savings beyond 20%'
            })
        
        # Spending analysis recommendations
        if spending_analysis:
            total_warnings = len(spending_analysis.get('warnings', []))
            if total_warnings > 2:
                recommendations.append({
                    'type': 'spending',
                    'priority': 'high',
                    'title': 'Multiple Budget Overruns Detected',
                    'message': f"You're overspending in {total_warnings} categories.",
                    'action': 'Review and prioritize your most important expenses'
                })
            
            savings_rate = spending_analysis.get('overall', {}).get('savings_rate', 0)
            if savings_rate < 10:
                recommendations.append({
                    'type': 'emergency',
                    'priority': 'critical',
                    'title': 'Low Savings Rate Alert',
                    'message': f"Your actual savings rate is only {savings_rate:.1f}%.",
                    'action': 'Immediately identify areas to cut spending'
                })
        
        return recommendations
    
    def _compare_with_national_averages(self, income: Decimal, needs: Decimal, 
                                      wants: Decimal, savings: Decimal) -> Dict[str, Any]:
        """Compare user's budget with national averages."""
        user_needs_pct = (needs / income * 100).quantize(Decimal('0.1'))
        user_wants_pct = (wants / income * 100).quantize(Decimal('0.1'))
        user_savings_pct = (savings / income * 100).quantize(Decimal('0.1'))
        
        # National averages (approximate)
        avg_needs = Decimal('50')
        avg_wants = Decimal('30')
        avg_savings = Decimal('13')  # Actual US average is lower than recommended 20%
        
        return {
            'needs': {
                'user_percentage': user_needs_pct,
                'national_average': avg_needs,
                'comparison': 'higher' if user_needs_pct > avg_needs else 'lower' if user_needs_pct < avg_needs else 'similar',
                'difference': user_needs_pct - avg_needs
            },
            'wants': {
                'user_percentage': user_wants_pct,
                'national_average': avg_wants,
                'comparison': 'higher' if user_wants_pct > avg_wants else 'lower' if user_wants_pct < avg_wants else 'similar',
                'difference': user_wants_pct - avg_wants
            },
            'savings': {
                'user_percentage': user_savings_pct,
                'national_average': avg_savings,
                'comparison': 'higher' if user_savings_pct > avg_savings else 'lower' if user_savings_pct < avg_savings else 'similar',
                'difference': user_savings_pct - avg_savings
            }
        }
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Format main amounts
        formatted['monthly_income'] = currency_service.format_currency(results['monthly_income'], currency)
        
        # Format allocations
        for category in ['needs', 'wants', 'savings']:
            allocation = results['allocations'][category]
            formatted[f'{category}_amount'] = currency_service.format_currency(allocation['amount'], currency)
            
            # Format breakdown amounts
            for item in allocation['breakdown']:
                item['formatted_amount'] = currency_service.format_currency(item['amount'], currency)
                item['formatted_annual'] = currency_service.format_currency(item['annual_amount'], currency)
        
        # Format annual projections
        for key, value in results['annual_projections'].items():
            formatted[f'annual_{key}'] = currency_service.format_currency(value, currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate monthly income
        monthly_income = self.validate_number(
            inputs.get('monthly_income', 5000),
            'Monthly income',
            min_val=500,
            max_val=100000
        )
        if monthly_income is None:
            return False
        
        # Validate custom percentages if provided
        if 'needs_percentage' in inputs:
            needs_pct = self.validate_number(
                inputs['needs_percentage'],
                'Needs percentage',
                min_val=30,
                max_val=80
            )
            if needs_pct is None:
                return False
        
        if 'wants_percentage' in inputs:
            wants_pct = self.validate_number(
                inputs['wants_percentage'],
                'Wants percentage',
                min_val=5,
                max_val=50
            )
            if wants_pct is None:
                return False
        
        if 'savings_percentage' in inputs:
            savings_pct = self.validate_number(
                inputs['savings_percentage'],
                'Savings percentage',
                min_val=5,
                max_val=50
            )
            if savings_pct is None:
                return False
        
        # Validate that percentages sum to approximately 100%
        if all(key in inputs for key in ['needs_percentage', 'wants_percentage', 'savings_percentage']):
            total = inputs['needs_percentage'] + inputs['wants_percentage'] + inputs['savings_percentage']
            if abs(total - 100) > 5:  # Allow 5% tolerance
                self.add_error("Budget percentages should sum to approximately 100%")
                return False
        
        # Validate actual spending amounts if provided
        if 'actual_spending' in inputs:
            spending = inputs['actual_spending']
            for category, amount in spending.items():
                if not isinstance(amount, (int, float)) or amount < 0:
                    self.add_error(f"Invalid spending amount for {category}")
                    return False
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Budget Calculator 2024 - 50/30/20 Rule Budget Planner | Free',
            'description': 'Free budget calculator using the 50/30/20 rule. Plan your monthly budget, track spending, and get personalized recommendations for better money management.',
            'keywords': 'budget calculator, 50/30/20 rule, budget planner, monthly budget calculator, personal budget calculator, budget tracker',
            'canonical': '/calculators/budget/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Budget Calculator",
            "description": "Plan your monthly budget using the 50/30/20 rule with customizable categories and spending analysis",
            "url": "https://yourcalcsite.com/calculators/budget/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "50/30/20 budget rule calculator",
                "Custom budget category allocation",
                "Spending analysis and tracking",
                "Overspending warnings and alerts",
                "National average comparisons",
                "Personalized budget recommendations",
                "Annual budget projections",
                "Multi-currency support"
            ]
        }