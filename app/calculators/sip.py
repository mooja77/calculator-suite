"""
SIP (Systematic Investment Plan) Calculator.
Popular in India, Singapore, Malaysia for mutual fund investments.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service
import math

@register_calculator
class SipCalculator(BaseCalculator):
    """Calculate future value of systematic investment plans."""
    
    # Currency defaults by region
    REGIONAL_DEFAULTS = {
        'IN': {'currency': 'INR', 'symbol': '₹', 'avg_return': 12},
        'SG': {'currency': 'SGD', 'symbol': 'S$', 'avg_return': 8},
        'MY': {'currency': 'MYR', 'symbol': 'RM', 'avg_return': 10},
        'US': {'currency': 'USD', 'symbol': '$', 'avg_return': 10},
        'UK': {'currency': 'GBP', 'symbol': '£', 'avg_return': 8},
        'AE': {'currency': 'AED', 'symbol': 'د.إ', 'avg_return': 9}
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate SIP returns with optional step-up."""
        # Extract inputs
        monthly_investment = Decimal(str(inputs.get('monthly_investment', 0)))
        expected_return = Decimal(str(inputs.get('expected_return', 12))) / 100  # Convert to decimal
        investment_period = int(inputs.get('investment_period', 10))  # Years
        
        # Optional inputs
        step_up_percentage = Decimal(str(inputs.get('step_up_percentage', 0))) / 100
        existing_investment = Decimal(str(inputs.get('existing_investment', 0)))
        region = inputs.get('region', 'IN')
        inflation_rate = Decimal(str(inputs.get('inflation_rate', 6))) / 100
        
        # Get regional defaults
        regional_info = self.REGIONAL_DEFAULTS.get(region, self.REGIONAL_DEFAULTS['IN'])
        currency = regional_info['currency']
        
        # Calculate monthly rate
        monthly_rate = expected_return / 12
        total_months = investment_period * 12
        
        # Calculate future value without step-up
        if monthly_rate == 0:
            # Simple calculation if no returns
            future_value = monthly_investment * total_months + existing_investment
        else:
            # Standard SIP formula: FV = P × [(1 + r)^n - 1] / r × (1 + r)
            future_value = monthly_investment * (
                ((1 + monthly_rate) ** total_months - 1) / monthly_rate
            ) * (1 + monthly_rate)
            
            # Add existing investment with compound interest
            if existing_investment > 0:
                future_value += existing_investment * ((1 + monthly_rate) ** total_months)
        
        # Calculate with step-up if provided
        future_value_stepup = future_value
        total_invested_stepup = monthly_investment * total_months + existing_investment
        
        if step_up_percentage > 0:
            future_value_stepup = self._calculate_stepup_sip(
                monthly_investment, 
                monthly_rate, 
                investment_period, 
                step_up_percentage,
                existing_investment
            )
            total_invested_stepup = self._calculate_total_invested_stepup(
                monthly_investment,
                investment_period,
                step_up_percentage,
                existing_investment
            )
        
        # Calculate total invested (without returns)
        total_invested = monthly_investment * total_months + existing_investment
        
        # Calculate gains
        total_gains = future_value - total_invested
        total_gains_stepup = future_value_stepup - total_invested_stepup
        
        # Calculate inflation-adjusted values
        inflation_factor = (1 + inflation_rate) ** investment_period
        real_future_value = future_value / inflation_factor
        real_future_value_stepup = future_value_stepup / inflation_factor
        
        # Calculate XIRR (approximate annualized return)
        xirr = self._calculate_xirr(monthly_investment, future_value, investment_period)
        xirr_stepup = self._calculate_xirr_stepup(monthly_investment, future_value_stepup, investment_period, step_up_percentage) if step_up_percentage > 0 else xirr
        
        # Prepare results
        results = {
            'monthly_investment': monthly_investment,
            'investment_period': investment_period,
            'expected_return': expected_return * 100,  # Convert back to percentage
            'total_invested': total_invested.quantize(Decimal('0.01')),
            'future_value': future_value.quantize(Decimal('0.01')),
            'total_gains': total_gains.quantize(Decimal('0.01')),
            'currency': currency,
            'region': region,
            'real_future_value': real_future_value.quantize(Decimal('0.01')),
            'xirr': xirr,
            'gain_percentage': ((total_gains / total_invested) * 100).quantize(Decimal('0.01')) if total_invested > 0 else Decimal('0')
        }
        
        # Add step-up results if applicable
        if step_up_percentage > 0:
            results.update({
                'step_up_percentage': step_up_percentage * 100,
                'future_value_stepup': future_value_stepup.quantize(Decimal('0.01')),
                'total_invested_stepup': total_invested_stepup.quantize(Decimal('0.01')),
                'total_gains_stepup': total_gains_stepup.quantize(Decimal('0.01')),
                'real_future_value_stepup': real_future_value_stepup.quantize(Decimal('0.01')),
                'xirr_stepup': xirr_stepup,
                'additional_gains': (total_gains_stepup - total_gains).quantize(Decimal('0.01'))
            })
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        # Add year-wise breakdown
        results['yearly_breakdown'] = self._calculate_yearly_breakdown(
            monthly_investment, 
            monthly_rate, 
            investment_period, 
            step_up_percentage,
            existing_investment
        )
        
        return results
    
    def _calculate_stepup_sip(self, monthly_amount: Decimal, monthly_rate: Decimal, 
                             years: int, step_up_rate: Decimal, existing: Decimal) -> Decimal:
        """Calculate SIP with annual step-up."""
        future_value = existing * ((1 + monthly_rate) ** (years * 12)) if existing > 0 else Decimal('0')
        current_monthly = monthly_amount
        
        for year in range(years):
            # Calculate FV for this year's monthly investments
            months_remaining = (years - year) * 12
            
            for month in range(12):
                months_to_maturity = months_remaining - month
                if months_to_maturity > 0:
                    future_value += current_monthly * ((1 + monthly_rate) ** months_to_maturity)
            
            # Step up for next year
            if year < years - 1:
                current_monthly = current_monthly * (1 + step_up_rate)
        
        return future_value
    
    def _calculate_total_invested_stepup(self, monthly_amount: Decimal, years: int, 
                                       step_up_rate: Decimal, existing: Decimal) -> Decimal:
        """Calculate total amount invested with step-up."""
        total = existing
        current_monthly = monthly_amount
        
        for year in range(years):
            total += current_monthly * 12
            if year < years - 1:
                current_monthly = current_monthly * (1 + step_up_rate)
        
        return total
    
    def _calculate_xirr(self, monthly_amount: Decimal, future_value: Decimal, years: int) -> Decimal:
        """Calculate approximate XIRR (annualized return)."""
        try:
            # Simplified XIRR calculation
            total_invested = monthly_amount * years * 12
            if total_invested == 0:
                return Decimal('0')
            
            # Use compound annual growth rate formula
            cagr = ((future_value / total_invested) ** (Decimal('1') / Decimal(str(years))) - 1) * 100
            return cagr.quantize(Decimal('0.01'))
        except:
            return Decimal('0')
    
    def _calculate_xirr_stepup(self, monthly_amount: Decimal, future_value: Decimal, 
                              years: int, step_up_rate: Decimal) -> Decimal:
        """Calculate XIRR for step-up SIP."""
        try:
            total_invested = self._calculate_total_invested_stepup(
                monthly_amount, years, step_up_rate, Decimal('0')
            )
            if total_invested == 0:
                return Decimal('0')
            
            cagr = ((future_value / total_invested) ** (Decimal('1') / Decimal(str(years))) - 1) * 100
            return cagr.quantize(Decimal('0.01'))
        except:
            return Decimal('0')
    
    def _calculate_yearly_breakdown(self, monthly_amount: Decimal, monthly_rate: Decimal,
                                   years: int, step_up_rate: Decimal, existing: Decimal) -> List[Dict]:
        """Calculate year-wise investment breakdown."""
        breakdown = []
        cumulative_invested = existing
        cumulative_value = existing
        current_monthly = monthly_amount
        
        for year in range(1, years + 1):
            # This year's investment
            yearly_investment = current_monthly * 12
            cumulative_invested += yearly_investment
            
            # Calculate value at end of year
            # Existing amount grows
            if existing > 0:
                cumulative_value = existing * ((1 + monthly_rate) ** (year * 12))
            else:
                cumulative_value = Decimal('0')
            
            # Add SIP investments with their growth
            temp_monthly = monthly_amount
            for y in range(year):
                for m in range(12):
                    months_elapsed = y * 12 + m + 1
                    months_growth = year * 12 - months_elapsed
                    if months_growth >= 0:
                        cumulative_value += temp_monthly * ((1 + monthly_rate) ** months_growth)
                
                if y < year - 1 and step_up_rate > 0:
                    temp_monthly = temp_monthly * (1 + step_up_rate)
            
            breakdown.append({
                'year': year,
                'monthly_investment': current_monthly.quantize(Decimal('0.01')),
                'yearly_investment': yearly_investment.quantize(Decimal('0.01')),
                'cumulative_invested': cumulative_invested.quantize(Decimal('0.01')),
                'cumulative_value': cumulative_value.quantize(Decimal('0.01')),
                'gains': (cumulative_value - cumulative_invested).quantize(Decimal('0.01'))
            })
            
            # Step up for next year
            if step_up_rate > 0 and year < years:
                current_monthly = current_monthly * (1 + step_up_rate)
        
        return breakdown
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        currency_fields = [
            'monthly_investment', 'total_invested', 'future_value', 'total_gains',
            'real_future_value', 'future_value_stepup', 'total_invested_stepup',
            'total_gains_stepup', 'real_future_value_stepup', 'additional_gains'
        ]
        
        for field in currency_fields:
            if field in results and isinstance(results[field], Decimal):
                formatted[field] = currency_service.format_currency(results[field], currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate monthly investment
        monthly_investment = self.validate_number(
            inputs.get('monthly_investment', 0),
            'Monthly investment',
            min_val=100,
            max_val=10000000
        )
        if monthly_investment is None:
            return False
        
        # Validate expected return
        expected_return = self.validate_number(
            inputs.get('expected_return', 12),
            'Expected return',
            min_val=1,
            max_val=50
        )
        if expected_return is None:
            return False
        
        # Validate investment period
        investment_period = self.validate_number(
            inputs.get('investment_period', 10),
            'Investment period',
            min_val=1,
            max_val=50
        )
        if investment_period is None:
            return False
        
        # Validate optional fields
        if inputs.get('step_up_percentage'):
            self.validate_number(
                inputs['step_up_percentage'],
                'Step-up percentage',
                min_val=0,
                max_val=50
            )
        
        if inputs.get('existing_investment'):
            self.validate_number(
                inputs['existing_investment'],
                'Existing investment',
                min_val=0,
                max_val=100000000
            )
        
        if inputs.get('inflation_rate'):
            self.validate_number(
                inputs['inflation_rate'],
                'Inflation rate',
                min_val=0,
                max_val=20
            )
        
        # Validate region
        region = inputs.get('region', 'IN')
        if region not in self.REGIONAL_DEFAULTS:
            self.add_error(f"Unsupported region: {region}")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'SIP Calculator - Systematic Investment Plan Calculator 2024 | India, Singapore, Malaysia',
            'description': 'Free SIP calculator to calculate returns on your monthly systematic investment plan. Calculate future value with step-up SIP option. Popular in India, Singapore, and Malaysia.',
            'keywords': 'sip calculator, systematic investment plan calculator, mutual fund calculator, investment calculator, step up sip calculator, monthly investment calculator',
            'canonical': '/calculators/sip/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication", 
            "name": "SIP Calculator - Systematic Investment Plan Calculator",
            "description": "Calculate future value of your systematic investment plan with optional step-up feature",
            "url": "https://yourcalcsite.com/calculators/sip/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Monthly SIP calculation",
                "Step-up SIP option",
                "Multi-currency support",
                "Inflation-adjusted returns",
                "Year-wise breakdown",
                "XIRR calculation",
                "Regional defaults for India, Singapore, Malaysia"
            ]
        }