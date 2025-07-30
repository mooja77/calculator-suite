"""
Paycheck/Take-Home Pay Calculator with multi-country support.
Supports US, UK, Canada, and Australia tax systems.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class PaycheckCalculator(BaseCalculator):
    """Calculate take-home pay after taxes and deductions."""
    
    # Tax rates and thresholds for 2024
    TAX_SYSTEMS = {
        'US': {
            'federal_brackets': [
                (10700, 0.10),
                (41775, 0.12),
                (90750, 0.22),
                (191750, 0.24),
                (434200, 0.32),
                (539900, 0.35),
                (float('inf'), 0.37)
            ],
            'standard_deduction': 13850,
            'social_security_rate': 0.062,
            'social_security_cap': 160200,
            'medicare_rate': 0.0145,
            'medicare_additional_rate': 0.009,
            'medicare_additional_threshold': 200000,
            'states': {
                'CA': {'brackets': [(10099, 0.01), (23942, 0.02), (37788, 0.04), (52455, 0.06), (66295, 0.08), (338639, 0.093), (406364, 0.103), (677275, 0.113), (float('inf'), 0.123)]},
                'NY': {'brackets': [(8500, 0.04), (11700, 0.045), (13900, 0.0525), (80650, 0.0585), (215400, 0.0625), (1077550, 0.0685), (5000000, 0.0965), (25000000, 0.103), (float('inf'), 0.109)]},
                'TX': {'brackets': [(float('inf'), 0.0)]},  # No state income tax
                'FL': {'brackets': [(float('inf'), 0.0)]},  # No state income tax
                'WA': {'brackets': [(float('inf'), 0.0)]},  # No state income tax
            }
        },
        'UK': {
            'tax_brackets': [
                (12570, 0.0),   # Personal allowance
                (50270, 0.20),  # Basic rate
                (125140, 0.40), # Higher rate
                (float('inf'), 0.45)  # Additional rate
            ],
            'ni_brackets': [  # National Insurance
                (12570, 0.0),
                (50270, 0.12),
                (float('inf'), 0.02)
            ],
            'personal_allowance_reduction_threshold': 100000,
            'personal_allowance_reduction_rate': 0.5,
            'currency': 'GBP'
        },
        'Canada': {
            'federal_brackets': [
                (53359, 0.15),
                (106717, 0.205),
                (165430, 0.26),
                (235675, 0.29),
                (float('inf'), 0.33)
            ],
            'basic_personal_amount': 15000,
            'cpp_rate': 0.0595,  # Canada Pension Plan
            'cpp_max': 71300,
            'cpp_exemption': 3500,
            'ei_rate': 0.0163,   # Employment Insurance
            'ei_max': 63200,
            'provinces': {
                'ON': {'brackets': [(49231, 0.0505), (98463, 0.0915), (150000, 0.1116), (220000, 0.1216), (float('inf'), 0.1316)]},
                'BC': {'brackets': [(47937, 0.0506), (95875, 0.077), (110076, 0.105), (133664, 0.1229), (181232, 0.147), (252752, 0.168), (float('inf'), 0.205)]},
                'QC': {'brackets': [(49275, 0.15), (98540, 0.20), (119910, 0.24), (float('inf'), 0.2575)]},
                'AB': {'brackets': [(float('inf'), 0.10)]},  # Flat rate
            },
            'currency': 'CAD'
        },
        'Australia': {
            'tax_brackets': [
                (18200, 0.0),    # Tax-free threshold
                (45000, 0.19),   # 19%
                (120000, 0.325), # 32.5%
                (180000, 0.37),  # 37%
                (float('inf'), 0.45)  # 45%
            ],
            'medicare_levy': 0.02,
            'medicare_levy_threshold': 23365,
            'superannuation_rate': 0.11,  # 11% in 2024
            'currency': 'AUD'
        }
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate take-home pay based on country-specific tax rules."""
        # Extract inputs
        gross_salary = Decimal(str(inputs.get('gross_salary', 0)))
        pay_frequency = inputs.get('pay_frequency', 'annual')
        country = inputs.get('country', 'US')
        state_province = inputs.get('state_province', '')
        
        # Convert to annual if needed
        annual_salary = self._convert_to_annual(gross_salary, pay_frequency)
        
        # Calculate based on country
        if country == 'US':
            result = self._calculate_us_taxes(annual_salary, state_province, inputs)
        elif country == 'UK':
            result = self._calculate_uk_taxes(annual_salary, inputs)
        elif country == 'Canada':
            result = self._calculate_canada_taxes(annual_salary, state_province, inputs)
        elif country == 'Australia':
            result = self._calculate_australia_taxes(annual_salary, inputs)
        else:
            raise ValueError(f"Unsupported country: {country}")
        
        # Convert back to requested frequency
        result = self._convert_from_annual(result, pay_frequency)
        
        # Add currency formatting
        currency_code = self.TAX_SYSTEMS.get(country, {}).get('currency', 'USD')
        result['currency'] = currency_code
        result['formatted'] = self._format_results(result, currency_code)
        
        return result
    
    def _calculate_us_taxes(self, annual_salary: Decimal, state: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate US federal and state taxes."""
        system = self.TAX_SYSTEMS['US']
        
        # Federal income tax
        taxable_income = max(Decimal('0'), annual_salary - Decimal(str(system['standard_deduction'])))
        federal_tax = self._calculate_progressive_tax(taxable_income, system['federal_brackets'])
        
        # Social Security
        ss_taxable = min(annual_salary, Decimal(str(system['social_security_cap'])))
        social_security = ss_taxable * Decimal(str(system['social_security_rate']))
        
        # Medicare
        medicare = annual_salary * Decimal(str(system['medicare_rate']))
        if annual_salary > system['medicare_additional_threshold']:
            medicare += (annual_salary - Decimal(str(system['medicare_additional_threshold']))) * Decimal(str(system['medicare_additional_rate']))
        
        # State tax
        state_tax = Decimal('0')
        if state and state in system['states']:
            state_brackets = system['states'][state]['brackets']
            state_tax = self._calculate_progressive_tax(annual_salary, state_brackets)
        
        # Additional deductions
        retirement_401k = Decimal(str(inputs.get('retirement_401k', 0)))
        health_insurance = Decimal(str(inputs.get('health_insurance', 0))) * 12  # Monthly to annual
        other_deductions = Decimal(str(inputs.get('other_deductions', 0))) * 12
        
        # Calculate totals
        total_tax = federal_tax + state_tax + social_security + medicare
        total_deductions = retirement_401k + health_insurance + other_deductions
        net_pay = annual_salary - total_tax - total_deductions
        
        return {
            'gross_pay': annual_salary,
            'federal_tax': federal_tax,
            'state_tax': state_tax,
            'social_security': social_security,
            'medicare': medicare,
            'retirement_401k': retirement_401k,
            'health_insurance': health_insurance,
            'other_deductions': other_deductions,
            'total_tax': total_tax,
            'total_deductions': total_deductions,
            'net_pay': net_pay,
            'effective_tax_rate': (total_tax / annual_salary * 100).quantize(Decimal('0.01'))
        }
    
    def _calculate_uk_taxes(self, annual_salary: Decimal, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate UK income tax and National Insurance."""
        system = self.TAX_SYSTEMS['UK']
        
        # Adjust personal allowance for high earners
        personal_allowance = Decimal('12570')
        if annual_salary > system['personal_allowance_reduction_threshold']:
            reduction = (annual_salary - Decimal(str(system['personal_allowance_reduction_threshold']))) * Decimal(str(system['personal_allowance_reduction_rate']))
            personal_allowance = max(Decimal('0'), personal_allowance - reduction)
        
        # Income tax
        taxable_income = max(Decimal('0'), annual_salary - personal_allowance)
        income_tax = self._calculate_progressive_tax_with_allowance(annual_salary, system['tax_brackets'], personal_allowance)
        
        # National Insurance
        ni_contributions = self._calculate_progressive_tax(annual_salary, system['ni_brackets'])
        
        # Pension contributions (auto-enrollment minimum 5% employee)
        pension = annual_salary * Decimal(str(inputs.get('pension_rate', 0.05)))
        
        # Calculate totals
        total_tax = income_tax + ni_contributions
        net_pay = annual_salary - total_tax - pension
        
        return {
            'gross_pay': annual_salary,
            'income_tax': income_tax,
            'national_insurance': ni_contributions,
            'pension': pension,
            'total_tax': total_tax,
            'net_pay': net_pay,
            'effective_tax_rate': (total_tax / annual_salary * 100).quantize(Decimal('0.01'))
        }
    
    def _calculate_canada_taxes(self, annual_salary: Decimal, province: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Canadian federal and provincial taxes."""
        system = self.TAX_SYSTEMS['Canada']
        
        # Federal tax
        federal_taxable = max(Decimal('0'), annual_salary - Decimal(str(system['basic_personal_amount'])))
        federal_tax = self._calculate_progressive_tax(federal_taxable, system['federal_brackets'])
        
        # Provincial tax
        provincial_tax = Decimal('0')
        if province and province in system['provinces']:
            provincial_brackets = system['provinces'][province]['brackets']
            provincial_tax = self._calculate_progressive_tax(annual_salary, provincial_brackets)
        
        # CPP (Canada Pension Plan)
        cpp_pensionable = min(annual_salary, Decimal(str(system['cpp_max']))) - Decimal(str(system['cpp_exemption']))
        cpp_pensionable = max(Decimal('0'), cpp_pensionable)
        cpp = cpp_pensionable * Decimal(str(system['cpp_rate']))
        
        # EI (Employment Insurance)
        ei_insurable = min(annual_salary, Decimal(str(system['ei_max'])))
        ei = ei_insurable * Decimal(str(system['ei_rate']))
        
        # RRSP contributions
        rrsp = Decimal(str(inputs.get('rrsp_contribution', 0)))
        
        # Calculate totals
        total_tax = federal_tax + provincial_tax
        total_deductions = cpp + ei + rrsp
        net_pay = annual_salary - total_tax - total_deductions
        
        return {
            'gross_pay': annual_salary,
            'federal_tax': federal_tax,
            'provincial_tax': provincial_tax,
            'cpp': cpp,
            'ei': ei,
            'rrsp': rrsp,
            'total_tax': total_tax,
            'total_deductions': total_deductions,
            'net_pay': net_pay,
            'effective_tax_rate': (total_tax / annual_salary * 100).quantize(Decimal('0.01'))
        }
    
    def _calculate_australia_taxes(self, annual_salary: Decimal, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Australian income tax and Medicare levy."""
        system = self.TAX_SYSTEMS['Australia']
        
        # Income tax
        income_tax = self._calculate_progressive_tax(annual_salary, system['tax_brackets'])
        
        # Medicare levy
        medicare_levy = Decimal('0')
        if annual_salary > system['medicare_levy_threshold']:
            medicare_levy = annual_salary * Decimal(str(system['medicare_levy']))
        
        # Superannuation (employer pays on top, but can be salary sacrifice)
        super_rate = Decimal(str(inputs.get('super_rate', system['superannuation_rate'])))
        superannuation = annual_salary * super_rate
        
        # Calculate totals
        total_tax = income_tax + medicare_levy
        net_pay = annual_salary - total_tax - superannuation
        
        return {
            'gross_pay': annual_salary,
            'income_tax': income_tax,
            'medicare_levy': medicare_levy,
            'superannuation': superannuation,
            'total_tax': total_tax,
            'net_pay': net_pay,
            'effective_tax_rate': (total_tax / annual_salary * 100).quantize(Decimal('0.01'))
        }
    
    def _calculate_progressive_tax(self, income: Decimal, brackets: List[tuple]) -> Decimal:
        """Calculate tax using progressive brackets."""
        tax = Decimal('0')
        previous_threshold = Decimal('0')
        
        for threshold, rate in brackets:
            threshold = Decimal(str(threshold)) if threshold != float('inf') else income
            if income > previous_threshold:
                taxable_in_bracket = min(income, threshold) - previous_threshold
                tax += taxable_in_bracket * Decimal(str(rate))
            previous_threshold = threshold
            
            if income <= threshold:
                break
        
        return tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _calculate_progressive_tax_with_allowance(self, income: Decimal, brackets: List[tuple], allowance: Decimal) -> Decimal:
        """Calculate tax with personal allowance considered."""
        taxable_income = max(Decimal('0'), income - allowance)
        return self._calculate_progressive_tax(taxable_income, brackets[1:])  # Skip the 0% bracket
    
    def _convert_to_annual(self, amount: Decimal, frequency: str) -> Decimal:
        """Convert amount to annual based on frequency."""
        multipliers = {
            'annual': 1,
            'monthly': 12,
            'biweekly': 26,
            'weekly': 52,
            'daily': 260  # Assuming 5 work days per week
        }
        return amount * Decimal(str(multipliers.get(frequency, 1)))
    
    def _convert_from_annual(self, results: Dict[str, Any], frequency: str) -> Dict[str, Any]:
        """Convert annual amounts back to requested frequency."""
        divisors = {
            'annual': 1,
            'monthly': 12,
            'biweekly': 26,
            'weekly': 52,
            'daily': 260
        }
        
        divisor = Decimal(str(divisors.get(frequency, 1)))
        
        # Convert all monetary values
        for key, value in results.items():
            if isinstance(value, Decimal) and key not in ['effective_tax_rate']:
                results[key] = (value / divisor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        results['pay_frequency'] = frequency
        return results
    
    def _format_results(self, results: Dict[str, Any], currency_code: str) -> Dict[str, str]:
        """Format all monetary values with currency symbols."""
        formatted = {}
        for key, value in results.items():
            if isinstance(value, Decimal) and key not in ['effective_tax_rate']:
                formatted[key] = currency_service.format_currency(value, currency_code)
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate gross salary
        gross_salary = self.validate_number(
            inputs.get('gross_salary', 0),
            'Gross salary',
            min_val=0,
            max_val=10000000
        )
        if gross_salary is None:
            return False
        
        # Validate country
        country = inputs.get('country', 'US')
        if country not in self.TAX_SYSTEMS:
            self.add_error(f"Unsupported country: {country}")
            return False
        
        # Validate state/province for countries that require it
        if country in ['US', 'Canada']:
            state_province = inputs.get('state_province', '')
            if country == 'US' and state_province and state_province not in self.TAX_SYSTEMS['US']['states']:
                self.add_error(f"Invalid US state: {state_province}")
            elif country == 'Canada' and state_province and state_province not in self.TAX_SYSTEMS['Canada']['provinces']:
                self.add_error(f"Invalid Canadian province: {state_province}")
        
        # Validate pay frequency
        valid_frequencies = ['annual', 'monthly', 'biweekly', 'weekly', 'daily']
        if inputs.get('pay_frequency', 'annual') not in valid_frequencies:
            self.add_error("Invalid pay frequency")
        
        # Validate optional deductions
        if inputs.get('retirement_401k'):
            self.validate_number(inputs['retirement_401k'], '401k contribution', min_val=0, max_val=22500)
        
        if inputs.get('health_insurance'):
            self.validate_number(inputs['health_insurance'], 'Health insurance', min_val=0, max_val=5000)
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Paycheck Calculator - Take-Home Pay Calculator 2024 | US, UK, Canada, Australia',
            'description': 'Free paycheck calculator to calculate take-home pay after taxes. Supports US (federal & state), UK, Canada, and Australia tax systems. Include 401k, pension, and insurance deductions.',
            'keywords': 'paycheck calculator, take home pay calculator, salary calculator, tax calculator, net pay calculator, gross to net, 401k calculator, payroll calculator',
            'canonical': '/calculators/paycheck/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Paycheck Calculator - Take-Home Pay Calculator",
            "description": "Calculate your take-home pay after taxes and deductions for US, UK, Canada, and Australia",
            "url": "https://yourcalcsite.com/calculators/paycheck/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "US federal and state tax calculation",
                "UK income tax and National Insurance",
                "Canadian federal and provincial taxes",
                "Australian income tax and Medicare levy",
                "401k and pension contributions",
                "Health insurance deductions",
                "Multi-currency support"
            ]
        }