"""
Rent vs Buy Calculator with multi-country support.
Helps users decide between renting and buying property.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class RentvsbuyCalculator(BaseCalculator):
    """Calculate whether it's better to rent or buy property."""
    
    # Regional defaults for mortgage and property costs
    REGIONAL_DEFAULTS = {
        'US': {
            'currency': 'USD',
            'property_tax_rate': 1.2,  # % of home value annually
            'mortgage_insurance_threshold': 20,  # % down payment to avoid PMI
            'mortgage_insurance_rate': 0.5,  # % of loan annually
            'closing_costs_rate': 2.5,  # % of home price
            'avg_mortgage_rate': 7.0,  # % annual
            'avg_rent_increase': 3.0,  # % annual
            'avg_home_appreciation': 3.5,  # % annual
            'capital_gains_exemption': 250000,  # Single filer
            'maintenance_rate': 1.0  # % of home value annually
        },
        'UK': {
            'currency': 'GBP',
            'property_tax_rate': 0.0,  # Council tax separate
            'council_tax_annual': 1500,  # Average
            'stamp_duty_thresholds': [(125000, 0), (250000, 0.02), (925000, 0.05), (1500000, 0.10), (float('inf'), 0.12)],
            'closing_costs_rate': 1.5,
            'avg_mortgage_rate': 5.5,
            'avg_rent_increase': 2.5,
            'avg_home_appreciation': 4.0,
            'capital_gains_exemption': 0,  # Primary residence exempt
            'maintenance_rate': 1.0
        },
        'Canada': {
            'currency': 'CAD',
            'property_tax_rate': 1.0,
            'cmhc_thresholds': [(5, 4.0), (10, 3.1), (15, 2.8), (20, 0)],  # Down payment %, insurance %
            'land_transfer_tax': 1.5,  # % varies by province
            'closing_costs_rate': 1.5,
            'avg_mortgage_rate': 6.0,
            'avg_rent_increase': 2.0,
            'avg_home_appreciation': 5.0,
            'capital_gains_exemption': 0,  # Primary residence exempt
            'maintenance_rate': 1.0
        },
        'Australia': {
            'currency': 'AUD',
            'property_tax_rate': 0.5,  # Council rates
            'stamp_duty_rate': 4.5,  # Varies by state
            'lmi_threshold': 20,  # Lenders Mortgage Insurance
            'lmi_rate': 2.0,  # % of loan
            'closing_costs_rate': 2.0,
            'avg_mortgage_rate': 6.5,
            'avg_rent_increase': 2.5,
            'avg_home_appreciation': 6.0,
            'capital_gains_discount': 50,  # % discount after 1 year
            'maintenance_rate': 1.0
        }
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate rent vs buy comparison over specified period."""
        # Extract inputs
        home_price = Decimal(str(inputs.get('home_price', 0)))
        down_payment_percent = Decimal(str(inputs.get('down_payment_percent', 20)))
        mortgage_rate = Decimal(str(inputs.get('mortgage_rate', 7.0))) / 100
        mortgage_term = int(inputs.get('mortgage_term', 30))
        monthly_rent = Decimal(str(inputs.get('monthly_rent', 0)))
        investment_return = Decimal(str(inputs.get('investment_return', 7))) / 100
        time_period = int(inputs.get('time_period', 10))  # Years to analyze
        country = inputs.get('country', 'US')
        
        # Get regional defaults
        defaults = self.REGIONAL_DEFAULTS.get(country, self.REGIONAL_DEFAULTS['US'])
        currency = defaults['currency']
        
        # Optional inputs with defaults
        property_tax_rate = Decimal(str(inputs.get('property_tax_rate', defaults['property_tax_rate']))) / 100
        home_appreciation = Decimal(str(inputs.get('home_appreciation', defaults['avg_home_appreciation']))) / 100
        rent_increase = Decimal(str(inputs.get('rent_increase', defaults['avg_rent_increase']))) / 100
        hoa_fees = Decimal(str(inputs.get('hoa_fees', 0)))
        maintenance_rate = Decimal(str(inputs.get('maintenance_rate', defaults['maintenance_rate']))) / 100
        
        # Calculate down payment and loan amount
        down_payment = home_price * (down_payment_percent / 100)
        loan_amount = home_price - down_payment
        
        # Calculate monthly mortgage payment
        if mortgage_rate > 0:
            monthly_rate = mortgage_rate / 12
            num_payments = mortgage_term * 12
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                            ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / (mortgage_term * 12)
        
        # Calculate buying costs
        buying_costs = self._calculate_buying_costs(
            home_price, down_payment, loan_amount, monthly_payment,
            property_tax_rate, hoa_fees, maintenance_rate, 
            time_period, home_appreciation, country, defaults
        )
        
        # Calculate renting costs
        renting_costs = self._calculate_renting_costs(
            monthly_rent, rent_increase, down_payment,
            investment_return, time_period
        )
        
        # Calculate net worth difference
        buy_net_worth = buying_costs['home_equity'] + buying_costs['investment_value'] - buying_costs['remaining_mortgage']
        rent_net_worth = renting_costs['investment_value']
        net_worth_difference = buy_net_worth - rent_net_worth
        
        # Determine recommendation
        total_buy_cost = buying_costs['total_cost'] - buying_costs['home_equity']
        total_rent_cost = renting_costs['total_cost'] - renting_costs['investment_value']
        
        if total_buy_cost < total_rent_cost:
            recommendation = 'buy'
            savings = total_rent_cost - total_buy_cost
        else:
            recommendation = 'rent'
            savings = total_buy_cost - total_rent_cost
        
        # Calculate break-even point
        break_even = self._calculate_break_even(
            home_price, down_payment, loan_amount, monthly_payment,
            property_tax_rate, hoa_fees, maintenance_rate,
            monthly_rent, rent_increase, investment_return,
            home_appreciation, country, defaults
        )
        
        results = {
            'recommendation': recommendation,
            'savings_amount': savings.quantize(Decimal('0.01')),
            'buy_total_cost': total_buy_cost.quantize(Decimal('0.01')),
            'rent_total_cost': total_rent_cost.quantize(Decimal('0.01')),
            'buy_net_worth': buy_net_worth.quantize(Decimal('0.01')),
            'rent_net_worth': rent_net_worth.quantize(Decimal('0.01')),
            'net_worth_difference': net_worth_difference.quantize(Decimal('0.01')),
            'break_even_years': break_even,
            'currency': currency,
            'buying_details': buying_costs,
            'renting_details': renting_costs,
            'inputs': {
                'home_price': home_price,
                'down_payment': down_payment,
                'monthly_payment': monthly_payment.quantize(Decimal('0.01')),
                'monthly_rent': monthly_rent,
                'time_period': time_period
            }
        }
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        # Add year-by-year comparison
        results['yearly_comparison'] = self._calculate_yearly_comparison(
            home_price, down_payment, loan_amount, monthly_payment,
            property_tax_rate, hoa_fees, maintenance_rate,
            monthly_rent, rent_increase, investment_return,
            home_appreciation, time_period, country, defaults
        )
        
        return results
    
    def _calculate_buying_costs(self, home_price: Decimal, down_payment: Decimal,
                               loan_amount: Decimal, monthly_payment: Decimal,
                               property_tax_rate: Decimal, hoa_fees: Decimal,
                               maintenance_rate: Decimal, years: int,
                               appreciation_rate: Decimal, country: str,
                               defaults: Dict) -> Dict[str, Decimal]:
        """Calculate total costs and equity for buying."""
        # Initial costs
        closing_costs = home_price * Decimal(str(defaults['closing_costs_rate'])) / 100
        
        # Country-specific costs
        if country == 'UK':
            # Calculate stamp duty
            stamp_duty = self._calculate_uk_stamp_duty(home_price, defaults)
            closing_costs += stamp_duty
        elif country == 'Canada':
            # Land transfer tax
            land_transfer = home_price * Decimal(str(defaults['land_transfer_tax'])) / 100
            closing_costs += land_transfer
        elif country == 'Australia':
            # Stamp duty
            stamp_duty = home_price * Decimal(str(defaults['stamp_duty_rate'])) / 100
            closing_costs += stamp_duty
        
        # Calculate mortgage insurance if applicable
        mortgage_insurance_total = Decimal('0')
        if country == 'US' and down_payment / home_price < Decimal('0.2'):
            # PMI for US
            annual_pmi = loan_amount * Decimal(str(defaults['mortgage_insurance_rate'])) / 100
            mortgage_insurance_total = annual_pmi * min(years, 7)  # Typically removed after 7 years
        elif country == 'Canada':
            # CMHC insurance
            down_payment_ratio = (down_payment / home_price) * 100
            for threshold, rate in defaults['cmhc_thresholds']:
                if down_payment_ratio < threshold:
                    mortgage_insurance_total = loan_amount * Decimal(str(rate)) / 100
                    break
        elif country == 'Australia' and down_payment / home_price < Decimal('0.2'):
            # LMI for Australia
            mortgage_insurance_total = loan_amount * Decimal(str(defaults['lmi_rate'])) / 100
        
        # Ongoing costs
        total_mortgage_payments = monthly_payment * 12 * years
        total_property_tax = home_price * property_tax_rate * years
        total_hoa = hoa_fees * 12 * years
        total_maintenance = home_price * maintenance_rate * years
        
        # UK council tax
        if country == 'UK':
            total_property_tax += Decimal(str(defaults['council_tax_annual'])) * years
        
        # Calculate home value after appreciation
        future_home_value = home_price * ((1 + appreciation_rate) ** years)
        
        # Calculate remaining mortgage balance
        months_paid = years * 12
        total_months = int(defaults.get('mortgage_term', 30)) * 12
        
        if months_paid >= total_months:
            remaining_balance = Decimal('0')
        else:
            # Calculate remaining balance
            monthly_rate = Decimal(str(defaults['avg_mortgage_rate'])) / 100 / 12
            if monthly_rate > 0:
                remaining_balance = loan_amount * (
                    ((1 + monthly_rate) ** total_months - (1 + monthly_rate) ** months_paid) /
                    ((1 + monthly_rate) ** total_months - 1)
                )
            else:
                remaining_balance = loan_amount * (1 - months_paid / total_months)
        
        # Calculate equity
        home_equity = future_home_value - remaining_balance
        
        # Total cost
        total_cost = (down_payment + closing_costs + total_mortgage_payments +
                     total_property_tax + total_hoa + total_maintenance +
                     mortgage_insurance_total)
        
        # Interest paid
        total_interest = total_mortgage_payments - (loan_amount - remaining_balance)
        
        return {
            'total_cost': total_cost.quantize(Decimal('0.01')),
            'down_payment': down_payment.quantize(Decimal('0.01')),
            'closing_costs': closing_costs.quantize(Decimal('0.01')),
            'total_mortgage_payments': total_mortgage_payments.quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'total_property_tax': total_property_tax.quantize(Decimal('0.01')),
            'total_hoa': total_hoa.quantize(Decimal('0.01')),
            'total_maintenance': total_maintenance.quantize(Decimal('0.01')),
            'mortgage_insurance': mortgage_insurance_total.quantize(Decimal('0.01')),
            'future_home_value': future_home_value.quantize(Decimal('0.01')),
            'remaining_mortgage': remaining_balance.quantize(Decimal('0.01')),
            'home_equity': home_equity.quantize(Decimal('0.01')),
            'investment_value': Decimal('0')  # Buyer has no investment fund
        }
    
    def _calculate_renting_costs(self, monthly_rent: Decimal, rent_increase: Decimal,
                                initial_investment: Decimal, investment_return: Decimal,
                                years: int) -> Dict[str, Decimal]:
        """Calculate total costs for renting and investing the difference."""
        total_rent = Decimal('0')
        current_rent = monthly_rent
        
        # Calculate total rent with annual increases
        for year in range(years):
            annual_rent = current_rent * 12
            total_rent += annual_rent
            current_rent = current_rent * (1 + rent_increase)
        
        # Calculate investment growth (down payment invested)
        if investment_return > 0:
            investment_value = initial_investment * ((1 + investment_return) ** years)
        else:
            investment_value = initial_investment
        
        return {
            'total_cost': total_rent.quantize(Decimal('0.01')),
            'total_rent_paid': total_rent.quantize(Decimal('0.01')),
            'investment_value': investment_value.quantize(Decimal('0.01')),
            'final_monthly_rent': current_rent.quantize(Decimal('0.01'))
        }
    
    def _calculate_uk_stamp_duty(self, price: Decimal, defaults: Dict) -> Decimal:
        """Calculate UK stamp duty."""
        duty = Decimal('0')
        thresholds = defaults.get('stamp_duty_thresholds', [])
        prev_threshold = Decimal('0')
        
        for threshold, rate in thresholds:
            threshold = Decimal(str(threshold)) if threshold != float('inf') else price
            if price > prev_threshold:
                taxable = min(price, threshold) - prev_threshold
                duty += taxable * Decimal(str(rate))
            prev_threshold = threshold
            if price <= threshold:
                break
        
        return duty
    
    def _calculate_break_even(self, home_price: Decimal, down_payment: Decimal,
                             loan_amount: Decimal, monthly_payment: Decimal,
                             property_tax_rate: Decimal, hoa_fees: Decimal,
                             maintenance_rate: Decimal, monthly_rent: Decimal,
                             rent_increase: Decimal, investment_return: Decimal,
                             appreciation_rate: Decimal, country: str,
                             defaults: Dict) -> int:
        """Calculate break-even point in years."""
        for year in range(1, 31):  # Check up to 30 years
            buying = self._calculate_buying_costs(
                home_price, down_payment, loan_amount, monthly_payment,
                property_tax_rate, hoa_fees, maintenance_rate, year,
                appreciation_rate, country, defaults
            )
            
            renting = self._calculate_renting_costs(
                monthly_rent, rent_increase, down_payment,
                investment_return, year
            )
            
            buy_net = buying['home_equity'] - (buying['total_cost'] - buying['home_equity'])
            rent_net = renting['investment_value'] - renting['total_cost']
            
            if buy_net > rent_net:
                return year
        
        return 30  # Max out at 30 years
    
    def _calculate_yearly_comparison(self, home_price: Decimal, down_payment: Decimal,
                                   loan_amount: Decimal, monthly_payment: Decimal,
                                   property_tax_rate: Decimal, hoa_fees: Decimal,
                                   maintenance_rate: Decimal, monthly_rent: Decimal,
                                   rent_increase: Decimal, investment_return: Decimal,
                                   appreciation_rate: Decimal, years: int,
                                   country: str, defaults: Dict) -> List[Dict]:
        """Calculate year-by-year comparison."""
        comparison = []
        
        for year in range(1, min(years + 1, 11)):  # Up to 10 years
            buying = self._calculate_buying_costs(
                home_price, down_payment, loan_amount, monthly_payment,
                property_tax_rate, hoa_fees, maintenance_rate, year,
                appreciation_rate, country, defaults
            )
            
            renting = self._calculate_renting_costs(
                monthly_rent, rent_increase, down_payment,
                investment_return, year
            )
            
            buy_net_worth = buying['home_equity'] + buying['investment_value'] - buying['remaining_mortgage']
            rent_net_worth = renting['investment_value']
            
            comparison.append({
                'year': year,
                'buy_total_cost': buying['total_cost'].quantize(Decimal('0.01')),
                'rent_total_cost': renting['total_cost'].quantize(Decimal('0.01')),
                'buy_net_worth': buy_net_worth.quantize(Decimal('0.01')),
                'rent_net_worth': rent_net_worth.quantize(Decimal('0.01')),
                'difference': (buy_net_worth - rent_net_worth).quantize(Decimal('0.01'))
            })
        
        return comparison
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        currency_fields = [
            'savings_amount', 'buy_total_cost', 'rent_total_cost',
            'buy_net_worth', 'rent_net_worth', 'net_worth_difference'
        ]
        
        for field in currency_fields:
            if field in results and isinstance(results[field], Decimal):
                formatted[field] = currency_service.format_currency(results[field], currency)
        
        # Format input values
        if 'inputs' in results:
            for key, value in results['inputs'].items():
                if isinstance(value, Decimal):
                    formatted[f'input_{key}'] = currency_service.format_currency(value, currency)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate home price
        home_price = self.validate_number(
            inputs.get('home_price', 0),
            'Home price',
            min_val=50000,
            max_val=10000000
        )
        if home_price is None:
            return False
        
        # Validate down payment percentage
        down_payment_percent = self.validate_number(
            inputs.get('down_payment_percent', 20),
            'Down payment percentage',
            min_val=0,
            max_val=100
        )
        if down_payment_percent is None:
            return False
        
        # Validate mortgage rate
        mortgage_rate = self.validate_number(
            inputs.get('mortgage_rate', 7),
            'Mortgage rate',
            min_val=0,
            max_val=20
        )
        if mortgage_rate is None:
            return False
        
        # Validate mortgage term
        mortgage_term = self.validate_number(
            inputs.get('mortgage_term', 30),
            'Mortgage term',
            min_val=5,
            max_val=40
        )
        if mortgage_term is None:
            return False
        
        # Validate monthly rent
        monthly_rent = self.validate_number(
            inputs.get('monthly_rent', 0),
            'Monthly rent',
            min_val=100,
            max_val=50000
        )
        if monthly_rent is None:
            return False
        
        # Validate time period
        time_period = self.validate_number(
            inputs.get('time_period', 10),
            'Time period',
            min_val=1,
            max_val=30
        )
        if time_period is None:
            return False
        
        # Validate investment return
        investment_return = self.validate_number(
            inputs.get('investment_return', 7),
            'Investment return',
            min_val=0,
            max_val=30
        )
        if investment_return is None:
            return False
        
        # Validate country
        country = inputs.get('country', 'US')
        if country not in self.REGIONAL_DEFAULTS:
            self.add_error(f"Unsupported country: {country}")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Rent vs Buy Calculator 2024 - Should You Rent or Buy? | US, UK, Canada, Australia',
            'description': 'Free rent vs buy calculator to help you decide whether to rent or buy a home. Compare costs, equity, and investment returns for US, UK, Canada, and Australia.',
            'keywords': 'rent vs buy calculator, rent or buy calculator, home buying calculator, property calculator, real estate calculator, mortgage calculator, investment calculator',
            'canonical': '/calculators/rentvsbuy/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Rent vs Buy Calculator",
            "description": "Calculate whether it's better to rent or buy property based on your financial situation",
            "url": "https://yourcalcsite.com/calculators/rentvsbuy/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Multi-country support (US, UK, Canada, Australia)",
                "Mortgage calculation with regional rates",
                "Property tax and maintenance costs",
                "Investment opportunity cost analysis",
                "Break-even analysis",
                "Year-by-year comparison",
                "Net worth projection"
            ]
        }