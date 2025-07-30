"""
UK VAT Calculator

Calculates Value Added Tax for the United Kingdom with support for:
- Standard rate (20%)
- Reduced rate (5%) 
- Zero rate (0%)
- Reverse VAT calculations (gross to net, net to gross)
- VAT registration thresholds
- Different business types
"""

from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class UkVatCalculator(BaseCalculator):
    """UK VAT Calculator with comprehensive VAT calculations"""
    
    # UK VAT rates (as of 2024)
    VAT_RATES = {
        'standard': Decimal('0.20'),      # 20% - most goods and services
        'reduced': Decimal('0.05'),       # 5% - domestic fuel, children's car seats, etc.
        'zero': Decimal('0.00'),          # 0% - books, food, children's clothes, etc.
    }
    
    # VAT registration thresholds (annual)
    VAT_REGISTRATION_THRESHOLD = Decimal('85000')  # £85,000 as of 2024
    VAT_DEREGISTRATION_THRESHOLD = Decimal('83000')  # £83,000 as of 2024
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        self.clear_errors()
        
        # Validate calculation type
        calc_type = inputs.get('calculation_type', 'add_vat')
        if calc_type not in ['add_vat', 'remove_vat', 'vat_only', 'registration_check']:
            self.add_error("Invalid calculation type")
            
        # Validate amount
        amount = self.validate_number(inputs.get('amount', 0), 'Amount', min_val=0)
        if amount is None:
            return False
            
        # Validate VAT rate
        vat_rate_type = inputs.get('vat_rate_type', 'standard')
        if vat_rate_type not in self.VAT_RATES:
            self.add_error("Invalid VAT rate type")
            
        # For custom rate, validate the custom_rate value
        if vat_rate_type == 'custom':
            custom_rate = self.validate_number(inputs.get('custom_rate', 0), 'Custom VAT rate', min_val=0, max_val=100)
            if custom_rate is None:
                return False
        
        return len(self.errors) == 0
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform VAT calculations"""
        
        if not self.validate_inputs(inputs):
            return {'error': self.errors}
        
        amount = Decimal(str(inputs.get('amount', 0)))
        calc_type = inputs.get('calculation_type', 'add_vat')
        vat_rate_type = inputs.get('vat_rate_type', 'standard')
        business_type = inputs.get('business_type', 'standard')
        
        # Get VAT rate
        if vat_rate_type == 'custom':
            vat_rate = Decimal(str(inputs.get('custom_rate', 0))) / 100
        else:
            vat_rate = self.VAT_RATES[vat_rate_type]
        
        result = {
            'input_amount': float(amount),
            'vat_rate_type': vat_rate_type,
            'vat_rate_percentage': float(vat_rate * 100),
            'business_type': business_type,
            'calculation_type': calc_type
        }
        
        if calc_type == 'add_vat':
            # Add VAT to net amount
            net_amount = amount
            vat_amount = net_amount * vat_rate
            gross_amount = net_amount + vat_amount
            
            result.update({
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'vat_amount': float(vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'description': f'Added {float(vat_rate * 100)}% VAT to net amount of £{net_amount}'
            })
            
        elif calc_type == 'remove_vat':
            # Remove VAT from gross amount
            gross_amount = amount
            net_amount = gross_amount / (1 + vat_rate)
            vat_amount = gross_amount - net_amount
            
            result.update({
                'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'vat_amount': float(vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'description': f'Removed {float(vat_rate * 100)}% VAT from gross amount of £{gross_amount}'
            })
            
        elif calc_type == 'vat_only':
            # Calculate VAT amount only
            net_amount = amount
            vat_amount = net_amount * vat_rate
            
            result.update({
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'vat_amount': float(vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'description': f'VAT amount at {float(vat_rate * 100)}% on £{net_amount}'
            })
            
        elif calc_type == 'registration_check':
            # Check VAT registration requirements
            annual_turnover = amount
            
            result.update({
                'annual_turnover': float(annual_turnover),
                'registration_threshold': float(self.VAT_REGISTRATION_THRESHOLD),
                'deregistration_threshold': float(self.VAT_DEREGISTRATION_THRESHOLD),
                'must_register': annual_turnover >= self.VAT_REGISTRATION_THRESHOLD,
                'can_deregister': annual_turnover <= self.VAT_DEREGISTRATION_THRESHOLD,
                'description': self._get_registration_advice(annual_turnover)
            })
        
        # Add business-specific information
        result['business_info'] = self._get_business_info(business_type, vat_rate_type)
        
        # Add rate explanation
        result['rate_explanation'] = self._get_rate_explanation(vat_rate_type)
        
        return result
    
    def _get_registration_advice(self, turnover: Decimal) -> str:
        """Get VAT registration advice based on turnover"""
        if turnover >= self.VAT_REGISTRATION_THRESHOLD:
            return f"You must register for VAT as your turnover (£{turnover:,.2f}) exceeds the threshold of £{self.VAT_REGISTRATION_THRESHOLD:,.2f}"
        elif turnover >= self.VAT_REGISTRATION_THRESHOLD * Decimal('0.8'):
            return f"You're approaching the VAT registration threshold. Consider registering voluntarily."
        else:
            return f"VAT registration is not required for turnover of £{turnover:,.2f}"
    
    def _get_business_info(self, business_type: str, vat_rate_type: str) -> Dict[str, Any]:
        """Get business-specific VAT information"""
        info = {
            'type': business_type,
            'can_reclaim_vat': business_type in ['standard', 'flat_rate'],
            'quarterly_returns': True,
            'annual_accounting': business_type == 'annual_accounting'
        }
        
        if business_type == 'flat_rate':
            info['flat_rate_percentage'] = 16.5  # Default flat rate percentage
            info['description'] = "Flat Rate Scheme simplifies VAT accounting but has different reclaim rules"
        elif business_type == 'cash_accounting':
            info['description'] = "Cash Accounting Scheme - pay VAT when you receive payment from customers"
        else:
            info['description'] = "Standard VAT accounting - pay VAT on invoice date"
        
        return info
    
    def _get_rate_explanation(self, rate_type: str) -> str:
        """Get explanation for VAT rate type"""
        explanations = {
            'standard': "Standard rate (20%) applies to most goods and services",
            'reduced': "Reduced rate (5%) applies to domestic fuel, energy-saving materials, children's car seats, etc.",
            'zero': "Zero rate (0%) applies to books, food, children's clothes, public transport, etc.",
            'custom': "Custom rate as specified"
        }
        return explanations.get(rate_type, "Standard rate")
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO metadata"""
        return {
            'title': 'UK VAT Calculator - Calculate Value Added Tax | Free Online Tool',
            'description': 'Free UK VAT calculator. Calculate VAT at 20%, 5%, or 0% rates. Add or remove VAT, check registration thresholds, and get business advice.',
            'keywords': 'UK VAT calculator, value added tax, VAT rates, UK tax, business VAT, VAT registration, HM Revenue Customs',
            'canonical': '/calculators/uk-vat'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "UK VAT Calculator",
            "description": "Calculate UK Value Added Tax with support for all VAT rates and business types",
            "url": "https://calculatorapp.com/calculators/uk-vat",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "GBP"
            },
            "featureList": [
                "Standard VAT rate (20%) calculations",
                "Reduced VAT rate (5%) calculations", 
                "Zero VAT rate (0%) calculations",
                "Reverse VAT calculations",
                "VAT registration threshold checks",
                "Business type guidance"
            ]
        }