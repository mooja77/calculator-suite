"""
House Affordability Calculator with 28/36 rule and regional support.
Calculates maximum affordable home price based on income and debt obligations.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class HouseaffordabilityCalculator(BaseCalculator):
    """Calculate maximum affordable home price using the 28/36 rule."""
    
    # Regional defaults for mortgage and housing costs
    REGIONAL_DEFAULTS = {
        'US': {
            'currency': 'USD',
            'housing_ratio': 28,  # % of gross income
            'debt_ratio': 36,     # % of gross income for total debt
            'property_tax_rate': 1.2,  # % of home value annually
            'home_insurance_rate': 0.35,  # % of home value annually
            'pmi_threshold': 20,   # % down payment to avoid PMI
            'pmi_rate': 0.5,       # % of loan amount annually
            'avg_mortgage_rate': 7.0,  # % annual
            'min_down_payment': 3.0,   # % minimum down payment
            'closing_costs_rate': 2.5,  # % of home price
            'hoa_estimate': 200,   # Average monthly HOA
            'maintenance_rate': 1.0,  # % of home value annually
            'utilities_estimate': 200,  # Monthly utilities estimate
        },
        'UK': {
            'currency': 'GBP',
            'housing_ratio': 30,   # Slightly higher in UK
            'debt_ratio': 40,      # More lenient debt ratio
            'property_tax_rate': 0.0,  # Council tax separate
            'council_tax_monthly': 150,  # Average monthly council tax
            'home_insurance_rate': 0.2,   # Lower insurance costs
            'deposit_threshold': 10,   # % minimum deposit
            'avg_mortgage_rate': 5.5,
            'min_down_payment': 5.0,
            'closing_costs_rate': 1.5,
            'service_charge': 100,  # Leasehold service charges
            'maintenance_rate': 0.8,
            'utilities_estimate': 120,
        },
        'CA': {
            'currency': 'CAD',
            'housing_ratio': 32,   # CMHC guidelines
            'debt_ratio': 40,      # Total debt service ratio
            'property_tax_rate': 1.0,
            'home_insurance_rate': 0.3,
            'cmhc_threshold': 20,  # % down payment to avoid CMHC
            'cmhc_premium_rates': {  # Based on down payment %
                5: 4.0, 10: 3.1, 15: 2.8, 20: 0
            },
            'avg_mortgage_rate': 6.0,
            'min_down_payment': 5.0,
            'closing_costs_rate': 1.5,
            'condo_fees': 400,     # Average condo fees
            'maintenance_rate': 1.0,
            'utilities_estimate': 150,
        },
        'AU': {
            'currency': 'AUD',
            'housing_ratio': 30,
            'debt_ratio': 38,      # Australian standard
            'property_tax_rate': 0.5,  # Council rates
            'home_insurance_rate': 0.25,
            'lmi_threshold': 20,   # Lenders Mortgage Insurance
            'lmi_rate': 2.0,       # % of loan amount
            'avg_mortgage_rate': 6.5,
            'min_down_payment': 5.0,
            'closing_costs_rate': 2.0,
            'body_corporate': 300,  # Average body corporate fees
            'maintenance_rate': 1.0,
            'utilities_estimate': 180,
        }
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate maximum affordable home price using 28/36 rule."""
        # Extract inputs
        annual_income = Decimal(str(inputs.get('annual_income', 0)))
        monthly_debt = Decimal(str(inputs.get('monthly_debt', 0)))
        down_payment_amount = Decimal(str(inputs.get('down_payment_amount', 0)))
        down_payment_percent = inputs.get('down_payment_percent')
        mortgage_rate = Decimal(str(inputs.get('mortgage_rate', 0))) / 100
        mortgage_term = int(inputs.get('mortgage_term', 30))
        country = inputs.get('country', 'US')
        
        # Get regional defaults
        defaults = self.REGIONAL_DEFAULTS.get(country, self.REGIONAL_DEFAULTS['US'])
        currency = defaults['currency']
        
        # Optional overrides
        housing_ratio = Decimal(str(inputs.get('housing_ratio', defaults['housing_ratio']))) / 100
        debt_ratio = Decimal(str(inputs.get('debt_ratio', defaults['debt_ratio']))) / 100
        property_tax_rate = Decimal(str(inputs.get('property_tax_rate', defaults['property_tax_rate']))) / 100
        
        # Calculate monthly income
        monthly_income = annual_income / 12
        
        # Apply 28/36 rule
        max_housing_payment = monthly_income * housing_ratio
        max_total_debt_payment = monthly_income * debt_ratio
        
        # Check if existing debt allows for housing payment
        available_for_housing = max_total_debt_payment - monthly_debt
        
        # Use the more restrictive of the two limits
        max_monthly_housing = min(max_housing_payment, available_for_housing)
        
        if max_monthly_housing <= 0:
            return {
                'affordable_price': Decimal('0'),
                'max_monthly_payment': Decimal('0'),
                'error': 'Current debt obligations exceed the 36% debt-to-income ratio',
                'currency': currency
            }
        
        # Calculate affordable home price based on available monthly payment
        affordability_analysis = self._calculate_affordability(
            max_monthly_housing, down_payment_amount, down_payment_percent,
            mortgage_rate, mortgage_term, country, defaults
        )
        
        # Calculate detailed breakdown
        breakdown = self._calculate_payment_breakdown(
            affordability_analysis['home_price'], 
            affordability_analysis['down_payment'],
            affordability_analysis['loan_amount'],
            mortgage_rate, mortgage_term, country, defaults
        )
        
        # Calculate debt-to-income ratios
        ratios = self._calculate_ratios(
            monthly_income, monthly_debt, breakdown['total_monthly_payment']
        )
        
        # Calculate closing costs and cash needed
        cash_requirements = self._calculate_cash_requirements(
            affordability_analysis['home_price'], 
            affordability_analysis['down_payment'],
            country, defaults
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            ratios, cash_requirements, monthly_income, defaults
        )
        
        results = {
            'affordable_price': affordability_analysis['home_price'].quantize(Decimal('0.01')),
            'loan_amount': affordability_analysis['loan_amount'].quantize(Decimal('0.01')),
            'down_payment': affordability_analysis['down_payment'].quantize(Decimal('0.01')),
            'down_payment_percent': affordability_analysis['down_payment_percent'].quantize(Decimal('0.1')),
            'max_monthly_payment': max_monthly_housing.quantize(Decimal('0.01')),
            'monthly_income': monthly_income.quantize(Decimal('0.01')),
            'currency': currency,
            'payment_breakdown': breakdown,
            'debt_ratios': ratios,
            'cash_requirements': cash_requirements,
            'recommendations': recommendations,
            'inputs': {
                'annual_income': annual_income,
                'monthly_debt': monthly_debt,
                'mortgage_rate': mortgage_rate * 100,
                'mortgage_term': mortgage_term,
                'country': country
            }
        }
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        # Add mortgage scenarios
        results['scenarios'] = self._generate_scenarios(
            monthly_income, monthly_debt, down_payment_amount, 
            down_payment_percent, country, defaults
        )
        
        return results
    
    def _calculate_affordability(self, max_monthly_payment: Decimal, 
                               down_payment_amount: Decimal,
                               down_payment_percent: float,
                               mortgage_rate: Decimal, mortgage_term: int,
                               country: str, defaults: Dict) -> Dict[str, Decimal]:
        """Calculate affordable home price based on monthly payment capacity."""
        
        # Estimate other monthly costs as percentage of payment
        other_costs_ratio = self._estimate_other_costs_ratio(country, defaults)
        
        # Available for principal and interest
        available_pi = max_monthly_payment * (1 - other_costs_ratio)
        
        # Calculate maximum loan amount based on P&I capacity
        if mortgage_rate > 0:
            monthly_rate = mortgage_rate / 12
            num_payments = mortgage_term * 12
            max_loan_amount = available_pi * (
                ((1 + monthly_rate) ** num_payments - 1) /
                (monthly_rate * (1 + monthly_rate) ** num_payments)
            )
        else:
            max_loan_amount = available_pi * mortgage_term * 12
        
        # Calculate home price based on down payment
        if down_payment_amount > 0:
            # Fixed down payment amount
            home_price = max_loan_amount + down_payment_amount
            down_payment_pct = (down_payment_amount / home_price) * 100
        elif down_payment_percent:
            # Percentage down payment
            down_payment_pct = Decimal(str(down_payment_percent))
            home_price = max_loan_amount / (1 - down_payment_pct / 100)
            down_payment_amount = home_price * (down_payment_pct / 100)
        else:
            # Use minimum down payment for country
            min_down_pct = Decimal(str(defaults['min_down_payment']))
            home_price = max_loan_amount / (1 - min_down_pct / 100)
            down_payment_amount = home_price * (min_down_pct / 100)
            down_payment_pct = min_down_pct
        
        # Refine calculation iteratively to account for exact other costs
        refined_price = self._refine_affordability(
            max_monthly_payment, home_price, down_payment_amount,
            mortgage_rate, mortgage_term, country, defaults
        )
        
        return {
            'home_price': refined_price,
            'loan_amount': refined_price - down_payment_amount,
            'down_payment': down_payment_amount,
            'down_payment_percent': down_payment_pct
        }
    
    def _estimate_other_costs_ratio(self, country: str, defaults: Dict) -> Decimal:
        """Estimate other monthly costs as ratio of total housing payment."""
        # Rough estimates based on typical costs
        if country == 'US':
            return Decimal('0.25')  # ~25% for taxes, insurance, PMI, maintenance
        elif country == 'UK':
            return Decimal('0.20')  # Lower due to different tax structure
        elif country == 'CA':
            return Decimal('0.23')  # Similar to US
        elif country == 'AU':
            return Decimal('0.22')  # Moderate
        else:
            return Decimal('0.25')  # Default to US
    
    def _refine_affordability(self, max_payment: Decimal, initial_price: Decimal,
                            down_payment: Decimal, mortgage_rate: Decimal,
                            mortgage_term: int, country: str, defaults: Dict) -> Decimal:
        """Refine home price calculation through iteration."""
        current_price = initial_price
        tolerance = Decimal('100')  # $100 tolerance
        max_iterations = 10
        
        for _ in range(max_iterations):
            # Calculate exact monthly payment for current price
            loan_amount = current_price - down_payment
            breakdown = self._calculate_payment_breakdown(
                current_price, down_payment, loan_amount,
                mortgage_rate, mortgage_term, country, defaults
            )
            
            total_payment = breakdown['total_monthly_payment']
            
            # Check if within tolerance
            if abs(total_payment - max_payment) <= tolerance:
                break
            
            # Adjust price based on payment difference
            ratio = max_payment / total_payment
            current_price = current_price * ratio
            
            # Recalculate down payment if percentage-based
            if down_payment / initial_price > Decimal('0.01'):  # If significant down payment
                down_payment_ratio = down_payment / initial_price
                down_payment = current_price * down_payment_ratio
        
        return current_price
    
    def _calculate_payment_breakdown(self, home_price: Decimal, down_payment: Decimal,
                                   loan_amount: Decimal, mortgage_rate: Decimal,
                                   mortgage_term: int, country: str,
                                   defaults: Dict) -> Dict[str, Decimal]:
        """Calculate detailed monthly payment breakdown."""
        
        # Principal and Interest
        if mortgage_rate > 0:
            monthly_rate = mortgage_rate / 12
            num_payments = mortgage_term * 12
            principal_interest = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                               ((1 + monthly_rate) ** num_payments - 1)
        else:
            principal_interest = loan_amount / (mortgage_term * 12)
        
        # Property taxes (monthly)
        monthly_property_tax = (home_price * Decimal(str(defaults['property_tax_rate'])) / 100) / 12
        
        # Homeowners insurance (monthly)
        monthly_insurance = (home_price * Decimal(str(defaults['home_insurance_rate'])) / 100) / 12
        
        # Mortgage insurance (if applicable)
        monthly_mortgage_insurance = Decimal('0')
        down_payment_pct = (down_payment / home_price) * 100
        
        if country == 'US' and down_payment_pct < defaults['pmi_threshold']:
            # PMI
            monthly_mortgage_insurance = (loan_amount * Decimal(str(defaults['pmi_rate'])) / 100) / 12
        elif country == 'CA' and down_payment_pct < defaults['cmhc_threshold']:
            # CMHC premium (typically paid upfront, but calculate monthly equivalent)
            for pct_threshold, premium_rate in defaults['cmhc_premium_rates'].items():
                if down_payment_pct < pct_threshold:
                    monthly_mortgage_insurance = (loan_amount * Decimal(str(premium_rate)) / 100) / (mortgage_term * 12)
                    break
        elif country == 'AU' and down_payment_pct < defaults['lmi_threshold']:
            # LMI (typically paid upfront)
            monthly_mortgage_insurance = (loan_amount * Decimal(str(defaults['lmi_rate'])) / 100) / (mortgage_term * 12)
        
        # HOA/Maintenance fees
        monthly_hoa = Decimal('0')
        if country == 'US':
            monthly_hoa = Decimal(str(defaults['hoa_estimate']))
        elif country == 'UK':
            monthly_hoa = Decimal(str(defaults['service_charge']))
            monthly_property_tax = Decimal(str(defaults['council_tax_monthly']))  # Override with council tax
        elif country == 'CA':
            monthly_hoa = Decimal(str(defaults['condo_fees']))
        elif country == 'AU':
            monthly_hoa = Decimal(str(defaults['body_corporate']))
        
        # Utilities estimate
        monthly_utilities = Decimal(str(defaults['utilities_estimate']))
        
        # Maintenance reserve
        monthly_maintenance = (home_price * Decimal(str(defaults['maintenance_rate'])) / 100) / 12
        
        # Total monthly payment
        total_monthly = (principal_interest + monthly_property_tax + monthly_insurance +
                        monthly_mortgage_insurance + monthly_hoa + monthly_utilities +
                        monthly_maintenance)
        
        return {
            'principal_interest': principal_interest.quantize(Decimal('0.01')),
            'property_tax': monthly_property_tax.quantize(Decimal('0.01')),
            'home_insurance': monthly_insurance.quantize(Decimal('0.01')),
            'mortgage_insurance': monthly_mortgage_insurance.quantize(Decimal('0.01')),
            'hoa_fees': monthly_hoa.quantize(Decimal('0.01')),
            'utilities': monthly_utilities.quantize(Decimal('0.01')),
            'maintenance': monthly_maintenance.quantize(Decimal('0.01')),
            'total_monthly_payment': total_monthly.quantize(Decimal('0.01'))
        }
    
    def _calculate_ratios(self, monthly_income: Decimal, monthly_debt: Decimal,
                         monthly_housing: Decimal) -> Dict[str, Decimal]:
        """Calculate debt-to-income ratios."""
        housing_ratio = (monthly_housing / monthly_income) * 100
        total_debt_ratio = ((monthly_debt + monthly_housing) / monthly_income) * 100
        
        return {
            'housing_ratio': housing_ratio.quantize(Decimal('0.1')),
            'total_debt_ratio': total_debt_ratio.quantize(Decimal('0.1')),
            'housing_ratio_limit': Decimal('28.0'),
            'debt_ratio_limit': Decimal('36.0')
        }
    
    def _calculate_cash_requirements(self, home_price: Decimal, down_payment: Decimal,
                                   country: str, defaults: Dict) -> Dict[str, Decimal]:
        """Calculate total cash needed for purchase."""
        
        # Closing costs
        closing_costs = home_price * Decimal(str(defaults['closing_costs_rate'])) / 100
        
        # Moving and inspection costs
        inspection_costs = Decimal('500')  # Average
        moving_costs = Decimal('2000')    # Average
        
        # Emergency fund recommendation (3 months housing payments)
        monthly_payment_estimate = home_price * Decimal('0.006')  # Rough estimate
        emergency_fund = monthly_payment_estimate * 3
        
        total_cash_needed = down_payment + closing_costs + inspection_costs + moving_costs
        total_recommended = total_cash_needed + emergency_fund
        
        return {
            'down_payment': down_payment.quantize(Decimal('0.01')),
            'closing_costs': closing_costs.quantize(Decimal('0.01')),
            'inspection_costs': inspection_costs,
            'moving_costs': moving_costs,
            'emergency_fund': emergency_fund.quantize(Decimal('0.01')),
            'total_cash_needed': total_cash_needed.quantize(Decimal('0.01')),
            'total_recommended': total_recommended.quantize(Decimal('0.01'))
        }
    
    def _generate_recommendations(self, ratios: Dict, cash_req: Dict,
                                monthly_income: Decimal, defaults: Dict) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Debt ratio recommendations
        if ratios['total_debt_ratio'] > 30:
            recommendations.append(
                f"Your total debt ratio is {ratios['total_debt_ratio']}%. "
                f"Consider paying down existing debt before purchasing."
            )
        
        # Down payment recommendations
        down_payment_pct = (cash_req['down_payment'] / 
                           (cash_req['down_payment'] + cash_req['closing_costs'])) * 100
        
        if down_payment_pct < 20:
            recommendations.append(
                "Consider saving for a 20% down payment to avoid mortgage insurance."
            )
        
        # Emergency fund
        if cash_req['emergency_fund'] > monthly_income * 2:
            recommendations.append(
                "Ensure you have 3-6 months of expenses saved as an emergency fund."
            )
        
        # Income recommendations
        if monthly_income < 5000:
            recommendations.append(
                "Consider increasing your income before purchasing to improve affordability."
            )
        
        return recommendations
    
    def _generate_scenarios(self, monthly_income: Decimal, monthly_debt: Decimal,
                          down_payment_amount: Decimal, down_payment_percent: float,
                          country: str, defaults: Dict) -> List[Dict]:
        """Generate different affordability scenarios."""
        
        scenarios = []
        base_mortgage_rate = Decimal(str(defaults['avg_mortgage_rate'])) / 100
        
        # Scenario 1: Current debt reduced by 50%
        reduced_debt = monthly_debt * Decimal('0.5')
        scenario1 = self._calculate_scenario(
            monthly_income, reduced_debt, down_payment_amount,
            down_payment_percent, base_mortgage_rate, country, defaults
        )
        scenario1['name'] = "Reduced Debt (50%)"
        scenario1['description'] = "If you reduce existing debt by half"
        scenarios.append(scenario1)
        
        # Scenario 2: Higher down payment (25%)
        scenario2 = self._calculate_scenario(
            monthly_income, monthly_debt, down_payment_amount,
            25.0, base_mortgage_rate, country, defaults
        )
        scenario2['name'] = "Higher Down Payment (25%)"
        scenario2['description'] = "With a 25% down payment"
        scenarios.append(scenario2)
        
        # Scenario 3: Lower interest rate
        lower_rate = base_mortgage_rate - Decimal('1.0') / 100
        scenario3 = self._calculate_scenario(
            monthly_income, monthly_debt, down_payment_amount,
            down_payment_percent, lower_rate, country, defaults
        )
        scenario3['name'] = "Lower Interest Rate (-1%)"
        scenario3['description'] = "With a 1% lower mortgage rate"
        scenarios.append(scenario3)
        
        return scenarios
    
    def _calculate_scenario(self, monthly_income: Decimal, monthly_debt: Decimal,
                          down_payment_amount: Decimal, down_payment_percent: float,
                          mortgage_rate: Decimal, country: str,
                          defaults: Dict) -> Dict[str, Any]:
        """Calculate a specific affordability scenario."""
        
        # Simplified calculation for scenarios
        housing_ratio = Decimal(str(defaults['housing_ratio'])) / 100
        debt_ratio = Decimal(str(defaults['debt_ratio'])) / 100
        
        max_housing_payment = monthly_income * housing_ratio
        available_for_housing = (monthly_income * debt_ratio) - monthly_debt
        max_monthly_housing = min(max_housing_payment, available_for_housing)
        
        if max_monthly_housing <= 0:
            return {
                'affordable_price': Decimal('0'),
                'monthly_payment': Decimal('0')
            }
        
        # Simple affordability calculation
        other_costs_ratio = self._estimate_other_costs_ratio(country, defaults)
        available_pi = max_monthly_housing * (1 - other_costs_ratio)
        
        if mortgage_rate > 0:
            monthly_rate = mortgage_rate / 12
            num_payments = 30 * 12  # 30-year term
            max_loan_amount = available_pi * (
                ((1 + monthly_rate) ** num_payments - 1) /
                (monthly_rate * (1 + monthly_rate) ** num_payments)
            )
        else:
            max_loan_amount = available_pi * 30 * 12
        
        # Calculate home price
        if down_payment_amount > 0:
            home_price = max_loan_amount + down_payment_amount
        elif down_payment_percent:
            down_payment_pct = Decimal(str(down_payment_percent)) / 100
            home_price = max_loan_amount / (1 - down_payment_pct)
        else:
            min_down_pct = Decimal(str(defaults['min_down_payment'])) / 100
            home_price = max_loan_amount / (1 - min_down_pct)
        
        return {
            'affordable_price': home_price.quantize(Decimal('0.01')),
            'monthly_payment': max_monthly_housing.quantize(Decimal('0.01'))
        }
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Main results
        main_fields = ['affordable_price', 'loan_amount', 'down_payment', 'max_monthly_payment', 'monthly_income']
        for field in main_fields:
            if field in results and isinstance(results[field], Decimal):
                formatted[field] = currency_service.format_currency(results[field], currency)
        
        # Payment breakdown
        if 'payment_breakdown' in results:
            formatted['payment_breakdown'] = {}
            for key, value in results['payment_breakdown'].items():
                formatted['payment_breakdown'][key] = currency_service.format_currency(value, currency)
        
        # Cash requirements
        if 'cash_requirements' in results:
            formatted['cash_requirements'] = {}
            for key, value in results['cash_requirements'].items():
                formatted['cash_requirements'][key] = currency_service.format_currency(value, currency)
        
        # Scenarios
        if 'scenarios' in results:
            formatted['scenarios'] = []
            for scenario in results['scenarios']:
                formatted_scenario = scenario.copy()
                formatted_scenario['affordable_price_formatted'] = currency_service.format_currency(
                    scenario['affordable_price'], currency
                )
                formatted_scenario['monthly_payment_formatted'] = currency_service.format_currency(
                    scenario['monthly_payment'], currency
                )
                formatted['scenarios'].append(formatted_scenario)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate annual income
        annual_income = self.validate_number(
            inputs.get('annual_income', 0),
            'Annual income',
            min_val=20000,
            max_val=10000000
        )
        if annual_income is None:
            return False
        
        # Validate monthly debt
        monthly_debt = self.validate_number(
            inputs.get('monthly_debt', 0),
            'Monthly debt',
            min_val=0,
            max_val=50000
        )
        if monthly_debt is None:
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
        
        # Validate down payment (either amount or percentage)
        down_payment_amount = inputs.get('down_payment_amount', 0)
        down_payment_percent = inputs.get('down_payment_percent')
        
        if down_payment_amount:
            down_amount = self.validate_number(
                down_payment_amount,
                'Down payment amount',
                min_val=0,
                max_val=2000000
            )
            if down_amount is None:
                return False
        
        if down_payment_percent:
            down_percent = self.validate_number(
                down_payment_percent,
                'Down payment percentage',
                min_val=0,
                max_val=80
            )
            if down_percent is None:
                return False
        
        # Validate country
        country = inputs.get('country', 'US')
        if country not in self.REGIONAL_DEFAULTS:
            self.add_error(f"Unsupported country: {country}")
        
        # Validate debt-to-income ratio
        if annual_income and monthly_debt:
            monthly_income = float(annual_income) / 12
            debt_ratio = (float(monthly_debt) / monthly_income) * 100
            if debt_ratio > 50:
                self.add_error("Monthly debt exceeds 50% of income. Consider debt reduction before home purchase.")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'House Affordability Calculator 2024 - How Much House Can I Afford? | 28/36 Rule',
            'description': 'Free house affordability calculator using the 28/36 rule. Calculate maximum home price based on income and debt. Includes PMI, taxes, and insurance for US, UK, Canada, Australia.',
            'keywords': 'house affordability calculator, home affordability calculator, how much house can I afford, 28/36 rule, mortgage calculator, home price calculator, house payment calculator',
            'canonical': '/calculators/houseaffordability/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "House Affordability Calculator",
            "description": "Calculate maximum affordable home price using the 28/36 debt-to-income rule",
            "url": "https://yourcalcsite.com/calculators/houseaffordability/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "28/36 debt-to-income rule calculation",
                "Multi-country support (US, UK, Canada, Australia)",
                "PMI/CMHC/LMI calculation",
                "Property tax and insurance estimates",
                "Detailed monthly payment breakdown",
                "Cash requirements analysis",
                "Affordability scenarios",
                "Personalized recommendations"
            ]
        }