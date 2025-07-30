"""
401k Retirement Calculator with employer matching and inflation adjustment.
Helps users plan for retirement savings and income projection.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service
import math

@register_calculator
class Retirement401kCalculator(BaseCalculator):
    """Calculate 401k retirement savings and income projections."""
    
    # IRS limits for 2024
    IRS_LIMITS = {
        '2024': {
            'contribution_limit': 23000,
            'catch_up_age': 50,
            'catch_up_amount': 7500,
            'compensation_limit': 345000
        },
        '2023': {
            'contribution_limit': 22500,
            'catch_up_age': 50,
            'catch_up_amount': 7500,
            'compensation_limit': 330000
        }
    }
    
    # Safe withdrawal rates for retirement
    WITHDRAWAL_RATES = {
        'conservative': 3.5,  # Very safe
        'moderate': 4.0,     # Traditional 4% rule
        'aggressive': 4.5    # Higher risk
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate 401k projections and retirement income."""
        # Extract inputs
        current_age = int(inputs.get('current_age', 30))
        retirement_age = int(inputs.get('retirement_age', 65))
        current_salary = Decimal(str(inputs.get('current_salary', 50000)))
        current_401k_balance = Decimal(str(inputs.get('current_401k_balance', 0)))
        
        # Contribution inputs
        employee_contribution_percent = Decimal(str(inputs.get('employee_contribution_percent', 6))) / 100
        employer_match_percent = Decimal(str(inputs.get('employer_match_percent', 3))) / 100
        employer_match_limit = Decimal(str(inputs.get('employer_match_limit', 6))) / 100
        
        # Growth and inflation inputs
        expected_return = Decimal(str(inputs.get('expected_return', 7))) / 100
        salary_growth_rate = Decimal(str(inputs.get('salary_growth_rate', 3))) / 100
        inflation_rate = Decimal(str(inputs.get('inflation_rate', 2.5))) / 100
        
        # Optional inputs
        withdrawal_strategy = inputs.get('withdrawal_strategy', 'moderate')
        catch_up_contributions = inputs.get('catch_up_contributions', True)
        
        # Calculate years to retirement
        years_to_retirement = retirement_age - current_age
        if years_to_retirement <= 0:
            raise ValueError("Retirement age must be greater than current age")
        
        # Get current IRS limits
        limits = self.IRS_LIMITS['2024']
        
        # Calculate projections
        projections = self._calculate_retirement_projections(
            current_salary, current_401k_balance, employee_contribution_percent,
            employer_match_percent, employer_match_limit, expected_return,
            salary_growth_rate, years_to_retirement, limits, catch_up_contributions,
            current_age
        )
        
        # Calculate retirement income scenarios
        income_scenarios = self._calculate_retirement_income(
            projections['final_balance'], withdrawal_strategy, inflation_rate,
            years_to_retirement
        )
        
        # Calculate replacement ratio
        final_salary = current_salary * ((1 + salary_growth_rate) ** years_to_retirement)
        replacement_ratio = (income_scenarios['annual_income'] / final_salary * 100) if final_salary > 0 else Decimal('0')
        
        results = {
            'current_age': current_age,
            'retirement_age': retirement_age,
            'years_to_retirement': years_to_retirement,
            'current_salary': current_salary,
            'final_salary': final_salary.quantize(Decimal('0.01')),
            'current_401k_balance': current_401k_balance,
            'expected_return': expected_return * 100,
            'total_contributions': projections['total_employee_contributions'],
            'total_employer_match': projections['total_employer_contributions'],
            'total_invested': projections['total_contributions'],
            'investment_growth': projections['investment_growth'],
            'final_balance': projections['final_balance'],
            'annual_retirement_income': income_scenarios['annual_income'],
            'monthly_retirement_income': income_scenarios['monthly_income'],
            'replacement_ratio': replacement_ratio.quantize(Decimal('0.1')),
            'withdrawal_rate': income_scenarios['withdrawal_rate'],
            'inflation_adjusted_income': income_scenarios['inflation_adjusted_income'],
            'currency': 'USD'
        }
        
        # Add contribution limits analysis
        results['contribution_analysis'] = self._analyze_contribution_limits(
            current_salary, employee_contribution_percent, current_age, limits
        )
        
        # Add year-by-year projection
        results['yearly_projection'] = self._calculate_yearly_projection(
            current_salary, current_401k_balance, employee_contribution_percent,
            employer_match_percent, employer_match_limit, expected_return,
            salary_growth_rate, min(years_to_retirement, 20), limits,
            catch_up_contributions, current_age
        )
        
        # Add scenarios with different contribution rates
        results['contribution_scenarios'] = self._calculate_contribution_scenarios(
            current_salary, current_401k_balance, employer_match_percent,
            employer_match_limit, expected_return, salary_growth_rate,
            years_to_retirement, limits, catch_up_contributions, current_age
        )
        
        # Add formatted values
        results['formatted'] = self._format_results(results, 'USD')
        
        return results
    
    def _calculate_retirement_projections(self, salary: Decimal, current_balance: Decimal,
                                        contribution_rate: Decimal, match_rate: Decimal,
                                        match_limit: Decimal, return_rate: Decimal,
                                        salary_growth: Decimal, years: int,
                                        limits: Dict, catch_up: bool, current_age: int) -> Dict[str, Decimal]:
        """Calculate retirement account projections."""
        balance = current_balance
        total_employee = Decimal('0')
        total_employer = Decimal('0')
        current_salary = salary
        
        for year in range(years):
            age = current_age + year
            
            # Calculate annual contribution
            annual_contribution = current_salary * contribution_rate
            
            # Apply IRS limits
            contribution_limit = Decimal(str(limits['contribution_limit']))
            if catch_up and age >= limits['catch_up_age']:
                contribution_limit += Decimal(str(limits['catch_up_amount']))
            
            annual_contribution = min(annual_contribution, contribution_limit)
            
            # Calculate employer match
            match_contribution = min(
                current_salary * match_rate,
                min(current_salary * match_limit, annual_contribution)
            )
            
            # Add contributions
            total_contributions = annual_contribution + match_contribution
            balance += total_contributions
            
            # Apply investment growth
            balance *= (1 + return_rate)
            
            # Track totals
            total_employee += annual_contribution
            total_employer += match_contribution
            
            # Increase salary for next year
            current_salary *= (1 + salary_growth)
        
        return {
            'final_balance': balance.quantize(Decimal('0.01')),
            'total_employee_contributions': total_employee.quantize(Decimal('0.01')),
            'total_employer_contributions': total_employer.quantize(Decimal('0.01')),
            'total_contributions': (total_employee + total_employer).quantize(Decimal('0.01')),
            'investment_growth': (balance - current_balance - total_employee - total_employer).quantize(Decimal('0.01'))
        }
    
    def _calculate_retirement_income(self, balance: Decimal, strategy: str,
                                   inflation: Decimal, years_to_retirement: int) -> Dict[str, Decimal]:
        """Calculate retirement income based on withdrawal strategy."""
        withdrawal_rate = Decimal(str(self.WITHDRAWAL_RATES.get(strategy, 4.0))) / 100
        
        # Annual income
        annual_income = balance * withdrawal_rate
        monthly_income = annual_income / 12
        
        # Inflation-adjusted income (purchasing power today)
        inflation_factor = (1 + inflation) ** years_to_retirement
        inflation_adjusted = annual_income / inflation_factor
        
        return {
            'withdrawal_rate': withdrawal_rate * 100,
            'annual_income': annual_income.quantize(Decimal('0.01')),
            'monthly_income': monthly_income.quantize(Decimal('0.01')),
            'inflation_adjusted_income': inflation_adjusted.quantize(Decimal('0.01'))
        }
    
    def _analyze_contribution_limits(self, salary: Decimal, contribution_rate: Decimal,
                                   age: int, limits: Dict) -> Dict[str, Any]:
        """Analyze contribution limits and optimization."""
        annual_contribution = salary * contribution_rate
        contribution_limit = Decimal(str(limits['contribution_limit']))
        
        if age >= limits['catch_up_age']:
            contribution_limit += Decimal(str(limits['catch_up_amount']))
        
        return {
            'current_contribution': annual_contribution.quantize(Decimal('0.01')),
            'contribution_limit': contribution_limit,
            'is_maxed_out': annual_contribution >= contribution_limit,
            'room_for_increase': max(Decimal('0'), contribution_limit - annual_contribution).quantize(Decimal('0.01')),
            'max_contribution_rate': min(Decimal('100'), contribution_limit / salary * 100).quantize(Decimal('0.1')),
            'catch_up_eligible': age >= limits['catch_up_age']
        }
    
    def _calculate_yearly_projection(self, salary: Decimal, current_balance: Decimal,
                                   contribution_rate: Decimal, match_rate: Decimal,
                                   match_limit: Decimal, return_rate: Decimal,
                                   salary_growth: Decimal, years: int, limits: Dict,
                                   catch_up: bool, current_age: int) -> List[Dict]:
        """Calculate year-by-year projections."""
        projections = []
        balance = current_balance
        current_salary = salary
        
        for year in range(1, min(years + 1, 21)):  # Limit to 20 years for display
            age = current_age + year - 1
            
            # Calculate contributions
            annual_contribution = current_salary * contribution_rate
            contribution_limit = Decimal(str(limits['contribution_limit']))
            if catch_up and age >= limits['catch_up_age']:
                contribution_limit += Decimal(str(limits['catch_up_amount']))
            
            annual_contribution = min(annual_contribution, contribution_limit)
            
            # Employer match
            match_contribution = min(
                current_salary * match_rate,
                min(current_salary * match_limit, annual_contribution)
            )
            
            # Beginning balance
            beginning_balance = balance
            
            # Add contributions
            balance += annual_contribution + match_contribution
            
            # Apply growth
            balance *= (1 + return_rate)
            
            projections.append({
                'year': year,
                'age': age,
                'salary': current_salary.quantize(Decimal('0.01')),
                'employee_contribution': annual_contribution.quantize(Decimal('0.01')),
                'employer_match': match_contribution.quantize(Decimal('0.01')),
                'beginning_balance': beginning_balance.quantize(Decimal('0.01')),
                'ending_balance': balance.quantize(Decimal('0.01')),
                'growth': (balance - beginning_balance - annual_contribution - match_contribution).quantize(Decimal('0.01'))
            })
            
            # Increase salary
            current_salary *= (1 + salary_growth)
        
        return projections
    
    def _calculate_contribution_scenarios(self, salary: Decimal, current_balance: Decimal,
                                        match_rate: Decimal, match_limit: Decimal,
                                        return_rate: Decimal, salary_growth: Decimal,
                                        years: int, limits: Dict, catch_up: bool,
                                        current_age: int) -> List[Dict]:
        """Calculate scenarios with different contribution rates."""
        scenarios = []
        contribution_rates = [0.03, 0.06, 0.10, 0.15, 0.20]  # 3%, 6%, 10%, 15%, 20%
        
        for rate in contribution_rates:
            projections = self._calculate_retirement_projections(
                salary, current_balance, Decimal(str(rate)), match_rate,
                match_limit, return_rate, salary_growth, years,
                limits, catch_up, current_age
            )
            
            # Calculate retirement income
            income = self._calculate_retirement_income(
                projections['final_balance'], 'moderate', Decimal('0.025'), years
            )
            
            scenarios.append({
                'contribution_rate': rate * 100,
                'annual_contribution': (salary * Decimal(str(rate))).quantize(Decimal('0.01')),
                'final_balance': projections['final_balance'],
                'total_contributions': projections['total_contributions'],
                'investment_growth': projections['investment_growth'],
                'monthly_retirement_income': income['monthly_income']
            })
        
        return scenarios
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        currency_fields = [
            'current_salary', 'final_salary', 'current_401k_balance',
            'total_contributions', 'total_employer_match', 'total_invested',
            'investment_growth', 'final_balance', 'annual_retirement_income',
            'monthly_retirement_income', 'inflation_adjusted_income'
        ]
        
        for field in currency_fields:
            if field in results and isinstance(results[field], Decimal):
                formatted[field] = currency_service.format_currency(results[field], currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate current age
        current_age = self.validate_number(
            inputs.get('current_age', 30),
            'Current age',
            min_val=18,
            max_val=75
        )
        if current_age is None:
            return False
        
        # Validate retirement age
        retirement_age = self.validate_number(
            inputs.get('retirement_age', 65),
            'Retirement age',
            min_val=current_age + 1 if current_age else 50,
            max_val=85
        )
        if retirement_age is None:
            return False
        
        # Validate current salary
        current_salary = self.validate_number(
            inputs.get('current_salary', 50000),
            'Current salary',
            min_val=10000,
            max_val=1000000
        )
        if current_salary is None:
            return False
        
        # Validate current 401k balance
        if inputs.get('current_401k_balance'):
            self.validate_number(
                inputs['current_401k_balance'],
                'Current 401k balance',
                min_val=0,
                max_val=10000000
            )
        
        # Validate contribution percentages
        employee_contribution = self.validate_number(
            inputs.get('employee_contribution_percent', 6),
            'Employee contribution percentage',
            min_val=0,
            max_val=100
        )
        if employee_contribution is None:
            return False
        
        # Validate employer match
        if inputs.get('employer_match_percent'):
            self.validate_number(
                inputs['employer_match_percent'],
                'Employer match percentage',
                min_val=0,
                max_val=25
            )
        
        if inputs.get('employer_match_limit'):
            self.validate_number(
                inputs['employer_match_limit'],
                'Employer match limit',
                min_val=0,
                max_val=100
            )
        
        # Validate return rates
        expected_return = self.validate_number(
            inputs.get('expected_return', 7),
            'Expected return',
            min_val=1,
            max_val=20
        )
        if expected_return is None:
            return False
        
        # Validate growth rates
        if inputs.get('salary_growth_rate'):
            self.validate_number(
                inputs['salary_growth_rate'],
                'Salary growth rate',
                min_val=0,
                max_val=10
            )
        
        if inputs.get('inflation_rate'):
            self.validate_number(
                inputs['inflation_rate'],
                'Inflation rate',
                min_val=0,
                max_val=10
            )
        
        # Validate withdrawal strategy
        strategy = inputs.get('withdrawal_strategy', 'moderate')
        if strategy not in self.WITHDRAWAL_RATES:
            self.add_error(f"Invalid withdrawal strategy: {strategy}")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': '401k Calculator 2024 - Retirement Calculator with Employer Match | Free',
            'description': 'Free 401k retirement calculator with employer match. Calculate your retirement savings, income projection, and see how much you need to retire comfortably.',
            'keywords': '401k calculator, retirement calculator, 401k retirement calculator, employer match calculator, retirement savings calculator, 401k projection calculator',
            'canonical': '/calculators/401k/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "401k Retirement Calculator",
            "description": "Calculate your 401k retirement savings and income projections with employer matching",
            "url": "https://yourcalcsite.com/calculators/401k/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "401k balance projection",
                "Employer match calculation",
                "Retirement income estimation",
                "Contribution limit analysis",
                "Multiple withdrawal strategies",
                "Inflation adjustment",
                "Year-by-year projections",
                "Contribution scenarios comparison"
            ]
        }