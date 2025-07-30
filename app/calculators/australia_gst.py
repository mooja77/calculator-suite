"""
Australia GST Calculator

Calculates Goods and Services Tax for Australia with support for:
- 10% GST rate
- GST-free and input-taxed supplies
- Business Activity Statements (BAS)
- ABN validation consideration
- Different business scenarios
"""

from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class AustraliaGstCalculator(BaseCalculator):
    """Australia GST Calculator with comprehensive GST calculations"""
    
    # Australian GST rate
    GST_RATE = Decimal('0.10')  # 10%
    
    # GST registration threshold
    GST_REGISTRATION_THRESHOLD = Decimal('75000')  # $75,000 AUD annually
    
    # Supply types for GST
    SUPPLY_TYPES = {
        'taxable': {'rate': GST_RATE, 'description': 'Standard taxable supplies (10% GST)'},
        'gst_free': {'rate': Decimal('0'), 'description': 'GST-free supplies (0% GST, can claim credits)'},
        'input_taxed': {'rate': Decimal('0'), 'description': 'Input-taxed supplies (0% GST, cannot claim credits)'},
        'export': {'rate': Decimal('0'), 'description': 'Exports (0% GST, can claim credits)'}
    }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        self.clear_errors()
        
        # Validate amount
        amount = self.validate_number(inputs.get('amount', 0), 'Amount', min_val=0)
        if amount is None:
            return False
        
        # Validate calculation type
        calc_type = inputs.get('calculation_type', 'add_gst')
        if calc_type not in ['add_gst', 'remove_gst', 'gst_only', 'bas_calculation', 'registration_check']:
            self.add_error("Invalid calculation type")
        
        # Validate supply type
        supply_type = inputs.get('supply_type', 'taxable')
        if supply_type not in self.SUPPLY_TYPES:
            self.add_error("Invalid supply type")
        
        # Validate business type
        business_type = inputs.get('business_type', 'registered')
        if business_type not in ['registered', 'unregistered', 'small_business', 'non_profit']:
            self.add_error("Invalid business type")
        
        return len(self.errors) == 0
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform GST calculations"""
        
        if not self.validate_inputs(inputs):
            return {'error': self.errors}
        
        amount = Decimal(str(inputs.get('amount', 0)))
        calc_type = inputs.get('calculation_type', 'add_gst')
        supply_type = inputs.get('supply_type', 'taxable')
        business_type = inputs.get('business_type', 'registered')
        
        # Get GST rate for supply type
        gst_rate = self.SUPPLY_TYPES[supply_type]['rate']
        
        result = {
            'input_amount': float(amount),
            'supply_type': supply_type,
            'business_type': business_type,
            'calculation_type': calc_type,
            'gst_rate_percentage': float(gst_rate * 100)
        }
        
        if calc_type == 'add_gst':
            # Add GST to net amount
            net_amount = amount
            gst_amount = net_amount * gst_rate
            gross_amount = net_amount + gst_amount
            
            result.update({
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gst_amount': float(gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'description': f'Added {float(gst_rate * 100)}% GST to net amount of ${net_amount}'
            })
            
        elif calc_type == 'remove_gst':
            # Remove GST from gross amount
            gross_amount = amount
            net_amount = gross_amount / (1 + gst_rate) if gst_rate > 0 else gross_amount
            gst_amount = gross_amount - net_amount
            
            result.update({
                'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gst_amount': float(gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'description': f'Removed {float(gst_rate * 100)}% GST from gross amount of ${gross_amount}'
            })
            
        elif calc_type == 'gst_only':
            # Calculate GST amount only
            net_amount = amount
            gst_amount = net_amount * gst_rate
            
            result.update({
                'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gst_amount': float(gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'description': f'GST amount at {float(gst_rate * 100)}% on ${net_amount}'
            })
            
        elif calc_type == 'bas_calculation':
            # Business Activity Statement calculation
            sales_amount = amount
            purchases_amount = Decimal(str(inputs.get('purchases_amount', 0)))
            
            # GST collected on sales
            gst_collected = sales_amount * gst_rate
            
            # GST paid on purchases (credits)
            purchase_gst_rate = gst_rate if inputs.get('can_claim_credits', True) else Decimal('0')
            gst_credits = purchases_amount * purchase_gst_rate
            
            # Net GST liability
            net_gst = gst_collected - gst_credits
            
            result.update({
                'sales_amount': float(sales_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'purchases_amount': float(purchases_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gst_collected': float(gst_collected.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gst_credits': float(gst_credits.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'net_gst_liability': float(net_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'gst_refund_due': net_gst < 0,
                'description': f'BAS calculation: GST collected ${gst_collected} minus GST credits ${gst_credits}'
            })
            
        elif calc_type == 'registration_check':
            # Check GST registration requirements
            annual_turnover = amount
            
            result.update({
                'annual_turnover': float(annual_turnover),
                'registration_threshold': float(self.GST_REGISTRATION_THRESHOLD),
                'must_register': annual_turnover >= self.GST_REGISTRATION_THRESHOLD,
                'can_register_voluntarily': annual_turnover < self.GST_REGISTRATION_THRESHOLD,
                'description': self._get_registration_advice(annual_turnover, business_type)
            })
        
        # Add supply type information
        result['supply_info'] = self._get_supply_info(supply_type)
        
        # Add business information
        result['business_info'] = self._get_business_info(business_type)
        
        # Add BAS filing information
        if business_type == 'registered':
            result['bas_info'] = self._get_bas_info(amount if calc_type == 'registration_check' else Decimal('0'))
        
        return result
    
    def _get_registration_advice(self, turnover: Decimal, business_type: str) -> str:
        """Get GST registration advice based on turnover and business type"""
        if turnover >= self.GST_REGISTRATION_THRESHOLD:
            return f"You must register for GST as your turnover (${turnover:,.2f}) meets or exceeds the threshold of ${self.GST_REGISTRATION_THRESHOLD:,.2f}"
        elif turnover >= self.GST_REGISTRATION_THRESHOLD * Decimal('0.8'):
            return f"You're approaching the GST registration threshold. Consider voluntary registration."
        else:
            if business_type == 'small_business':
                return f"GST registration is voluntary for turnover of ${turnover:,.2f}. Consider the cash flow impact."
            else:
                return f"GST registration is not required for turnover of ${turnover:,.2f}"
    
    def _get_supply_info(self, supply_type: str) -> Dict[str, Any]:
        """Get information about supply type"""
        supply_info = self.SUPPLY_TYPES[supply_type].copy()
        
        # Add examples for each supply type
        examples = {
            'taxable': ['Most goods and services', 'Retail sales', 'Professional services', 'Manufacturing'],
            'gst_free': ['Basic food', 'Medical services', 'Education', 'Exports'],
            'input_taxed': ['Financial services', 'Insurance', 'Residential rent', 'Precious metals'],
            'export': ['Goods exported overseas', 'Services consumed outside Australia']
        }
        
        supply_info['examples'] = examples.get(supply_type, [])
        supply_info['can_claim_credits'] = supply_type in ['taxable', 'gst_free', 'export']
        
        return supply_info
    
    def _get_business_info(self, business_type: str) -> Dict[str, Any]:
        """Get business-specific GST information"""
        info = {
            'type': business_type,
            'can_claim_credits': business_type == 'registered',
            'must_charge_gst': business_type == 'registered',
            'bas_required': business_type == 'registered'
        }
        
        descriptions = {
            'registered': "Registered for GST - must charge GST on taxable supplies and can claim GST credits",
            'unregistered': "Not registered for GST - cannot charge GST or claim GST credits",
            'small_business': "Small business - may be eligible for simplified GST accounting methods",
            'non_profit': "Non-profit organization - may have special GST concessions available"
        }
        
        info['description'] = descriptions.get(business_type, "Standard business")
        
        return info
    
    def _get_bas_info(self, annual_turnover: Decimal) -> Dict[str, Any]:
        """Get Business Activity Statement filing information"""
        
        # Determine BAS frequency based on turnover
        if annual_turnover >= Decimal('20000000'):  # $20 million
            frequency = 'monthly'
            due_dates = ['21st of following month']
        elif annual_turnover >= Decimal('2000000'):  # $2 million
            frequency = 'quarterly'
            due_dates = ['28 April', '28 July', '28 October', '28 February']
        else:
            frequency = 'quarterly'
            due_dates = ['28 April', '28 July', '28 October', '28 February']
        
        return {
            'filing_frequency': frequency,
            'due_dates': due_dates,
            'penalties_apply': True,
            'electronic_lodgment': True,
            'description': f"BAS must be lodged {frequency} with the ATO"
        }
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO metadata"""
        return {
            'title': 'Australia GST Calculator - Calculate Australian GST | Free Online Tool',
            'description': 'Free Australian GST calculator. Calculate 10% GST, BAS calculations, registration thresholds, and handle GST-free supplies. ATO compliant.',
            'keywords': 'Australia GST calculator, Australian tax, BAS calculator, ATO, GST registration, business tax, 10% GST',
            'canonical': '/calculators/australia-gst'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Australia GST Calculator",
            "description": "Calculate Australian Goods and Services Tax with BAS support and registration guidance",
            "url": "https://calculatorapp.com/calculators/australia-gst",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "AUD"
            },
            "featureList": [
                "10% GST calculations",
                "GST-free supply calculations",
                "Input-taxed supply handling",
                "Business Activity Statement (BAS) calculations",
                "GST registration threshold checks",
                "Export calculations",
                "Small business support"
            ]
        }