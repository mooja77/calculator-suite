"""
Canada GST/HST Calculator

Calculates Goods and Services Tax and Harmonized Sales Tax for Canada with support for:
- GST (5%) for all provinces
- HST provinces (13-15%)
- PST calculations for BC, SK, MB, QC
- Business vs consumer calculations
- Provincial tax variations
"""

from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class CanadaGstCalculator(BaseCalculator):
    """Canada GST/HST Calculator with comprehensive tax calculations"""
    
    # Canadian tax rates by province/territory (as of 2024)
    PROVINCIAL_TAX_RATES = {
        # HST Provinces (combined GST+PST)
        'ON': {'gst': Decimal('0'), 'pst': Decimal('0'), 'hst': Decimal('0.13'), 'name': 'Ontario'},
        'NB': {'gst': Decimal('0'), 'pst': Decimal('0'), 'hst': Decimal('0.15'), 'name': 'New Brunswick'},
        'NL': {'gst': Decimal('0'), 'pst': Decimal('0'), 'hst': Decimal('0.15'), 'name': 'Newfoundland and Labrador'},
        'NS': {'gst': Decimal('0'), 'pst': Decimal('0'), 'hst': Decimal('0.15'), 'name': 'Nova Scotia'},
        'PE': {'gst': Decimal('0'), 'pst': Decimal('0'), 'hst': Decimal('0.15'), 'name': 'Prince Edward Island'},
        
        # GST + PST Provinces
        'BC': {'gst': Decimal('0.05'), 'pst': Decimal('0.07'), 'hst': Decimal('0'), 'name': 'British Columbia'},
        'SK': {'gst': Decimal('0.05'), 'pst': Decimal('0.06'), 'hst': Decimal('0'), 'name': 'Saskatchewan'},
        'MB': {'gst': Decimal('0.05'), 'pst': Decimal('0.07'), 'hst': Decimal('0'), 'name': 'Manitoba'},
        'QC': {'gst': Decimal('0.05'), 'pst': Decimal('0.09975'), 'hst': Decimal('0'), 'name': 'Quebec'},  # QST
        
        # GST Only (No Provincial Tax)
        'AB': {'gst': Decimal('0.05'), 'pst': Decimal('0'), 'hst': Decimal('0'), 'name': 'Alberta'},
        'YT': {'gst': Decimal('0.05'), 'pst': Decimal('0'), 'hst': Decimal('0'), 'name': 'Yukon'},
        'NT': {'gst': Decimal('0.05'), 'pst': Decimal('0'), 'hst': Decimal('0'), 'name': 'Northwest Territories'},
        'NU': {'gst': Decimal('0.05'), 'pst': Decimal('0'), 'hst': Decimal('0'), 'name': 'Nunavut'},
    }
    
    # GST registration threshold
    GST_REGISTRATION_THRESHOLD = Decimal('30000')  # $30,000 CAD over 4 consecutive quarters
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        self.clear_errors()
        
        # Validate amount
        amount = self.validate_number(inputs.get('amount', 0), 'Amount', min_val=0)
        if amount is None:
            return False
        
        # Validate province/territory
        province = inputs.get('province', 'ON')
        if province not in self.PROVINCIAL_TAX_RATES:
            self.add_error("Invalid province/territory code")
        
        # Validate calculation type
        calc_type = inputs.get('calculation_type', 'add_tax')
        if calc_type not in ['add_tax', 'remove_tax', 'tax_only', 'registration_check']:
            self.add_error("Invalid calculation type")
        
        # Validate customer type
        customer_type = inputs.get('customer_type', 'consumer')
        if customer_type not in ['consumer', 'business', 'registered_business']:
            self.add_error("Invalid customer type")
        
        return len(self.errors) == 0
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform GST/HST calculations"""
        
        if not self.validate_inputs(inputs):
            return {'error': self.errors}
        
        amount = Decimal(str(inputs.get('amount', 0)))
        province = inputs.get('province', 'ON')
        calc_type = inputs.get('calculation_type', 'add_tax')
        customer_type = inputs.get('customer_type', 'consumer')
        
        # Get tax rates for province
        tax_info = self.PROVINCIAL_TAX_RATES[province]
        
        result = {
            'input_amount': float(amount),
            'province': province,
            'province_name': tax_info['name'],
            'customer_type': customer_type,
            'calculation_type': calc_type
        }
        
        if calc_type == 'add_tax':
            # Add taxes to net amount
            net_amount = amount
            
            if tax_info['hst'] > 0:
                # HST province
                hst_amount = net_amount * tax_info['hst']
                total_tax = hst_amount
                gross_amount = net_amount + total_tax
                
                result.update({
                    'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'hst_rate': float(tax_info['hst'] * 100),
                    'hst_amount': float(hst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gst_amount': 0,
                    'pst_amount': 0,
                    'total_tax': float(total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'tax_type': 'HST'
                })
            else:
                # GST + PST province
                gst_amount = net_amount * tax_info['gst']
                
                if tax_info['pst'] > 0:
                    if province == 'QC':
                        # Quebec PST (QST) is calculated on net + GST
                        pst_base = net_amount + gst_amount
                        pst_amount = pst_base * tax_info['pst']
                    else:
                        # Other provinces: PST on net amount only
                        pst_amount = net_amount * tax_info['pst']
                else:
                    pst_amount = Decimal('0')
                
                total_tax = gst_amount + pst_amount
                gross_amount = net_amount + total_tax
                
                result.update({
                    'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gst_rate': float(tax_info['gst'] * 100),
                    'gst_amount': float(gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'pst_rate': float(tax_info['pst'] * 100) if tax_info['pst'] > 0 else 0,
                    'pst_amount': float(pst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'hst_amount': 0,
                    'total_tax': float(total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'tax_type': 'GST+PST' if tax_info['pst'] > 0 else 'GST'
                })
        
        elif calc_type == 'remove_tax':
            # Remove taxes from gross amount
            gross_amount = amount
            
            if tax_info['hst'] > 0:
                # HST province
                net_amount = gross_amount / (1 + tax_info['hst'])
                hst_amount = gross_amount - net_amount
                
                result.update({
                    'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'hst_rate': float(tax_info['hst'] * 100),
                    'hst_amount': float(hst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gst_amount': 0,
                    'pst_amount': 0,
                    'total_tax': float(hst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'tax_type': 'HST'
                })
            else:
                # GST + PST province - more complex calculation
                if province == 'QC' and tax_info['pst'] > 0:
                    # Quebec: PST is on net + GST, so we need to solve backwards
                    # gross = net + (net * gst) + ((net + net*gst) * pst)
                    # gross = net * (1 + gst + pst + gst*pst)
                    multiplier = 1 + tax_info['gst'] + tax_info['pst'] + (tax_info['gst'] * tax_info['pst'])
                    net_amount = gross_amount / multiplier
                    gst_amount = net_amount * tax_info['gst']
                    pst_amount = (net_amount + gst_amount) * tax_info['pst']
                else:
                    # Other provinces: both taxes on net amount
                    total_rate = tax_info['gst'] + tax_info['pst']
                    net_amount = gross_amount / (1 + total_rate)
                    gst_amount = net_amount * tax_info['gst']
                    pst_amount = net_amount * tax_info['pst']
                
                total_tax = gst_amount + pst_amount
                
                result.update({
                    'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gst_rate': float(tax_info['gst'] * 100),
                    'gst_amount': float(gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'pst_rate': float(tax_info['pst'] * 100) if tax_info['pst'] > 0 else 0,
                    'pst_amount': float(pst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'hst_amount': 0,
                    'total_tax': float(total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'tax_type': 'GST+PST' if tax_info['pst'] > 0 else 'GST'
                })
        
        elif calc_type == 'tax_only':
            # Calculate tax amounts only
            net_amount = amount
            
            if tax_info['hst'] > 0:
                hst_amount = net_amount * tax_info['hst']
                result.update({
                    'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'hst_amount': float(hst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'total_tax': float(hst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'tax_type': 'HST'
                })
            else:
                gst_amount = net_amount * tax_info['gst']
                if province == 'QC' and tax_info['pst'] > 0:
                    pst_amount = (net_amount + gst_amount) * tax_info['pst']
                else:
                    pst_amount = net_amount * tax_info['pst']
                
                total_tax = gst_amount + pst_amount
                
                result.update({
                    'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'gst_amount': float(gst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'pst_amount': float(pst_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'total_tax': float(total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'tax_type': 'GST+PST' if tax_info['pst'] > 0 else 'GST'
                })
        
        elif calc_type == 'registration_check':
            # Check GST registration requirements
            annual_revenue = amount
            
            result.update({
                'annual_revenue': float(annual_revenue),
                'registration_threshold': float(self.GST_REGISTRATION_THRESHOLD),
                'must_register': annual_revenue > self.GST_REGISTRATION_THRESHOLD,
                'voluntary_registration': annual_revenue <= self.GST_REGISTRATION_THRESHOLD,
                'description': self._get_registration_advice(annual_revenue)
            })
        
        # Add business information
        result['business_info'] = self._get_business_info(customer_type, province)
        
        # Add provincial tax explanation
        result['tax_explanation'] = self._get_tax_explanation(province)
        
        return result
    
    def _get_registration_advice(self, revenue: Decimal) -> str:
        """Get GST registration advice based on revenue"""
        if revenue > self.GST_REGISTRATION_THRESHOLD:
            return f"You must register for GST/HST as your revenue (${revenue:,.2f}) exceeds ${self.GST_REGISTRATION_THRESHOLD:,.2f} over 4 consecutive quarters"
        else:
            return f"GST/HST registration is voluntary for revenue of ${revenue:,.2f}"
    
    def _get_business_info(self, customer_type: str, province: str) -> Dict[str, Any]:
        """Get business-specific tax information"""
        info = {
            'customer_type': customer_type,
            'can_claim_itc': customer_type == 'registered_business',  # Input Tax Credits
            'filing_frequency': 'quarterly' if customer_type == 'registered_business' else 'not_required'
        }
        
        if customer_type == 'registered_business':
            info['description'] = "Registered businesses can claim Input Tax Credits (ITCs) on business purchases"
        elif customer_type == 'business':
            info['description'] = "Unregistered businesses cannot claim ITCs but may register voluntarily"
        else:
            info['description'] = "Consumers pay full tax amount and cannot claim ITCs"
        
        return info
    
    def _get_tax_explanation(self, province: str) -> str:
        """Get explanation for provincial tax system"""
        tax_info = self.PROVINCIAL_TAX_RATES[province]
        
        if tax_info['hst'] > 0:
            return f"{tax_info['name']} uses HST ({float(tax_info['hst'] * 100)}%) - a combined federal and provincial tax"
        elif tax_info['pst'] > 0:
            if province == 'QC':
                return f"{tax_info['name']} uses GST (5%) + QST ({float(tax_info['pst'] * 100)}%) where QST is calculated on the GST-inclusive amount"
            else:
                return f"{tax_info['name']} uses GST (5%) + PST ({float(tax_info['pst'] * 100)}%) calculated separately on the net amount"
        else:
            return f"{tax_info['name']} only charges GST (5%) - no provincial sales tax"
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO metadata"""
        return {
            'title': 'Canada GST/HST Calculator - Calculate Canadian Sales Tax | Free Tool',
            'description': 'Free Canadian GST/HST calculator. Calculate taxes for all provinces including HST, GST, PST, and QST. Support for business and consumer calculations.',
            'keywords': 'Canada GST calculator, HST calculator, provincial sales tax, Canadian tax, business tax, CRA, Quebec QST',
            'canonical': '/calculators/canada-gst'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication", 
            "name": "Canada GST/HST Calculator",
            "description": "Calculate Canadian Goods and Services Tax and Harmonized Sales Tax for all provinces and territories",
            "url": "https://calculatorapp.com/calculators/canada-gst",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "CAD"
            },
            "featureList": [
                "GST calculations (5%)",
                "HST calculations (13-15%)",
                "Provincial sales tax (PST)",
                "Quebec sales tax (QST)", 
                "Business vs consumer calculations",
                "Registration threshold checks",
                "All Canadian provinces and territories"
            ]
        }