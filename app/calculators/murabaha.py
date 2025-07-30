"""
Murabaha Calculator (Islamic Home Finance)

Calculates Islamic home financing using Murabaha (cost-plus financing) with:
- Cost-plus financing structure (no interest/riba)
- Profit rate determination
- Payment schedules
- Comparison with conventional mortgages
- Sharia-compliant calculations
- Cultural sensitivity for Islamic finance
"""

from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class MurabahaCalculator(BaseCalculator):
    """Murabaha Calculator for Islamic home financing following Sharia principles"""
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        self.clear_errors()
        
        # Validate calculation type
        calc_type = inputs.get('calculation_type', 'monthly_payment')
        if calc_type not in ['monthly_payment', 'total_cost', 'payment_schedule', 'comparison']:
            self.add_error("Invalid calculation type")
        
        # Validate property price
        property_price = self.validate_number(inputs.get('property_price', 0), 'Property price', min_val=1000)
        if property_price is None:
            return False
        
        # Validate down payment
        down_payment = self.validate_number(inputs.get('down_payment', 0), 'Down payment', min_val=0)
        if down_payment is None:
            return False
        
        # Check down payment doesn't exceed property price
        if down_payment >= property_price:
            self.add_error("Down payment must be less than property price")
        
        # Validate financing term
        term_years = self.validate_number(inputs.get('term_years', 15), 'Financing term (years)', min_val=1, max_val=30)
        if term_years is None:
            return False
        
        # Validate profit rate
        profit_rate = self.validate_number(inputs.get('profit_rate', 5), 'Profit rate (%)', min_val=0.1, max_val=20)
        if profit_rate is None:
            return False
        
        # Validate murabaha structure type
        structure_type = inputs.get('structure_type', 'diminishing_musharaka')
        if structure_type not in ['diminishing_musharaka', 'direct_murabaha', 'ijara_muntahia']:
            self.add_error("Invalid Murabaha structure type")
        
        return len(self.errors) == 0
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Murabaha calculations"""
        
        if not self.validate_inputs(inputs):
            return {'error': self.errors}
        
        property_price = Decimal(str(inputs.get('property_price', 0)))
        down_payment = Decimal(str(inputs.get('down_payment', 0)))
        term_years = int(inputs.get('term_years', 15))
        profit_rate = Decimal(str(inputs.get('profit_rate', 5))) / 100  # Convert percentage
        structure_type = inputs.get('structure_type', 'diminishing_musharaka')
        calc_type = inputs.get('calculation_type', 'monthly_payment')
        
        # Calculate financing amount
        financing_amount = property_price - down_payment
        
        result = {
            'property_price': float(property_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'down_payment': float(down_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'financing_amount': float(financing_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'term_years': term_years,
            'profit_rate_percentage': float(profit_rate * 100),
            'structure_type': structure_type,
            'calculation_type': calc_type
        }
        
        if structure_type == 'diminishing_musharaka':
            # Most common Islamic home financing structure
            calculation_result = self._calculate_diminishing_musharaka(
                financing_amount, profit_rate, term_years, calc_type
            )
        elif structure_type == 'direct_murabaha':
            # Direct cost-plus sale
            calculation_result = self._calculate_direct_murabaha(
                financing_amount, profit_rate, term_years, calc_type
            )
        else:  # ijara_muntahia
            # Lease-to-own structure
            calculation_result = self._calculate_ijara_muntahia(
                financing_amount, profit_rate, term_years, calc_type
            )
        
        result.update(calculation_result)
        
        # Add Islamic finance information
        result['sharia_compliance'] = self._get_sharia_compliance_info(structure_type)
        result['structure_explanation'] = self._get_structure_explanation(structure_type)
        
        # Add comparison with conventional mortgage if requested
        if calc_type == 'comparison':
            conventional_rate = Decimal(str(inputs.get('conventional_rate', 4))) / 100
            result['conventional_comparison'] = self._calculate_conventional_comparison(
                financing_amount, conventional_rate, term_years
            )
        
        return result
    
    def _calculate_diminishing_musharaka(self, amount: Decimal, profit_rate: Decimal, years: int, calc_type: str) -> Dict[str, Any]:
        """Calculate Diminishing Musharaka (most common Islamic home finance)"""
        months = years * 12
        
        # In diminishing musharaka, the bank's share decreases monthly
        # Monthly payment = (Principal/months) + (Remaining bank share * monthly profit rate)
        monthly_profit_rate = profit_rate / 12
        
        # Calculate monthly payment (approximation using conventional formula adjusted for Islamic structure)
        if monthly_profit_rate > 0:
            monthly_payment = amount * (monthly_profit_rate * (1 + monthly_profit_rate)**months) / ((1 + monthly_profit_rate)**months - 1)
        else:
            monthly_payment = amount / months
        
        total_payment = monthly_payment * months
        total_profit = total_payment - amount
        
        result = {
            'monthly_payment': float(monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_payment': float(total_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_profit': float(total_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'effective_profit_rate': float((total_profit / amount).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)),
            'months': months
        }
        
        if calc_type == 'payment_schedule':
            result['payment_schedule'] = self._generate_diminishing_musharaka_schedule(
                amount, monthly_payment, monthly_profit_rate, months
            )
        
        return result
    
    def _calculate_direct_murabaha(self, amount: Decimal, profit_rate: Decimal, years: int, calc_type: str) -> Dict[str, Any]:
        """Calculate Direct Murabaha (cost-plus sale)"""
        months = years * 12
        
        # In direct murabaha, profit is fixed upfront
        total_profit = amount * profit_rate * years  # Simple profit calculation
        total_payment = amount + total_profit
        monthly_payment = total_payment / months
        
        result = {
            'monthly_payment': float(monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_payment': float(total_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_profit': float(total_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'effective_profit_rate': float((total_profit / amount).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)),
            'months': months
        }
        
        if calc_type == 'payment_schedule':
            result['payment_schedule'] = self._generate_direct_murabaha_schedule(
                monthly_payment, months, amount, total_profit
            )
        
        return result
    
    def _calculate_ijara_muntahia(self, amount: Decimal, profit_rate: Decimal, years: int, calc_type: str) -> Dict[str, Any]:
        """Calculate Ijara Muntahia Bittamleek (lease-to-own)"""
        months = years * 12
        
        # In Ijara, client pays rent + portion toward ownership
        monthly_rent = amount * profit_rate / 12  # Monthly rental
        monthly_ownership = amount / months  # Monthly ownership portion
        monthly_payment = monthly_rent + monthly_ownership
        
        total_payment = monthly_payment * months
        total_rent_paid = monthly_rent * months
        
        result = {
            'monthly_payment': float(monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'monthly_rent': float(monthly_rent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'monthly_ownership': float(monthly_ownership.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_payment': float(total_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'total_rent_paid': float(total_rent_paid.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'effective_profit_rate': float((total_rent_paid / amount).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)),
            'months': months
        }
        
        if calc_type == 'payment_schedule':
            result['payment_schedule'] = self._generate_ijara_schedule(
                monthly_rent, monthly_ownership, months
            )
        
        return result
    
    def _generate_diminishing_musharaka_schedule(self, amount: Decimal, monthly_payment: Decimal, 
                                               monthly_profit_rate: Decimal, months: int) -> List[Dict[str, float]]:
        """Generate payment schedule for Diminishing Musharaka"""
        schedule = []
        remaining_balance = amount
        bank_share = amount
        client_share = Decimal('0')
        
        for month in range(1, min(13, months + 1)):  # Show first 12 months
            # Calculate profit on bank's share
            monthly_profit = bank_share * monthly_profit_rate
            # Principal payment reduces bank's share
            principal_payment = monthly_payment - monthly_profit
            
            bank_share -= principal_payment
            client_share += principal_payment
            remaining_balance -= principal_payment
            
            schedule.append({
                'month': month,
                'payment': float(monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'profit': float(monthly_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'principal': float(principal_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'bank_share': float(bank_share.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'client_share': float(client_share.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'remaining_balance': float(remaining_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return schedule
    
    def _generate_direct_murabaha_schedule(self, monthly_payment: Decimal, months: int, 
                                         principal: Decimal, total_profit: Decimal) -> List[Dict[str, float]]:
        """Generate payment schedule for Direct Murabaha"""
        schedule = []
        remaining_balance = principal + total_profit
        monthly_principal = principal / months
        monthly_profit = total_profit / months
        
        for month in range(1, min(13, months + 1)):  # Show first 12 months
            remaining_balance -= monthly_payment
            
            schedule.append({
                'month': month,
                'payment': float(monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'profit_portion': float(monthly_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'principal_portion': float(monthly_principal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'remaining_balance': float(remaining_balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return schedule
    
    def _generate_ijara_schedule(self, monthly_rent: Decimal, monthly_ownership: Decimal, months: int) -> List[Dict[str, float]]:
        """Generate payment schedule for Ijara Muntahia"""
        schedule = []
        ownership_percentage = Decimal('0')
        monthly_ownership_percent = Decimal('100') / months
        
        for month in range(1, min(13, months + 1)):  # Show first 12 months
            ownership_percentage += monthly_ownership_percent
            
            schedule.append({
                'month': month,
                'rent_payment': float(monthly_rent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'ownership_payment': float(monthly_ownership.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'total_payment': float((monthly_rent + monthly_ownership).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'ownership_percentage': float(ownership_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            })
        
        return schedule
    
    def _calculate_conventional_comparison(self, amount: Decimal, interest_rate: Decimal, years: int) -> Dict[str, float]:
        """Calculate conventional mortgage for comparison"""
        months = years * 12
        monthly_rate = interest_rate / 12
        
        if monthly_rate > 0:
            monthly_payment = amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            monthly_payment = amount / months
        
        total_payment = monthly_payment * months
        total_interest = total_payment - amount
        
        return {
            'conventional_monthly': float(monthly_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'conventional_total': float(total_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'conventional_interest': float(total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'interest_rate_percentage': float(interest_rate * 100)
        }
    
    def _get_sharia_compliance_info(self, structure_type: str) -> Dict[str, Any]:
        """Get Sharia compliance information"""
        compliance_info = {
            'riba_free': True,
            'asset_backed': True,
            'risk_sharing': True,
            'gharar_minimal': True
        }
        
        structure_compliance = {
            'diminishing_musharaka': {
                'description': 'Partnership structure where bank\'s share decreases over time',
                'ownership': 'Shared ownership from day one',
                'risk_sharing': 'Both parties share property risks',
                'sharia_basis': 'Based on Musharaka (partnership) principles'
            },
            'direct_murabaha': {
                'description': 'Bank purchases and sells property at cost plus disclosed profit',
                'ownership': 'Client owns property immediately after purchase',
                'risk_sharing': 'Limited risk sharing, mainly credit risk',
                'sharia_basis': 'Based on Murabaha (cost-plus sale) principles'
            },
            'ijara_muntahia': {
                'description': 'Lease agreement with promise to transfer ownership',
                'ownership': 'Gradual ownership transfer through lease payments',
                'risk_sharing': 'Bank bears property ownership risks initially',
                'sharia_basis': 'Based on Ijara (leasing) principles'
            }
        }
        
        compliance_info.update(structure_compliance.get(structure_type, {}))
        return compliance_info
    
    def _get_structure_explanation(self, structure_type: str) -> Dict[str, Any]:
        """Get detailed explanation of the Islamic finance structure"""
        explanations = {
            'diminishing_musharaka': {
                'how_it_works': [
                    'Bank and client jointly purchase the property',
                    'Each monthly payment includes rental for bank\'s share',
                    'Part of payment increases client\'s ownership percentage',
                    'Bank\'s share and rental decrease over time',
                    'Client owns 100% at the end of the term'
                ],
                'advantages': [
                    'Shared ownership and risk from beginning',
                    'Decreasing payment structure possible',
                    'Widely accepted by Islamic scholars',
                    'Flexible early payment options'
                ],
                'considerations': [
                    'More complex documentation',
                    'May involve higher initial costs',
                    'Property insurance arrangements needed'
                ]
            },
            'direct_murabaha': {
                'how_it_works': [
                    'Bank purchases property at market price',
                    'Bank sells to client at cost plus agreed profit',
                    'Total price divided into monthly installments',
                    'Fixed payment amount throughout term',
                    'Client owns property from purchase date'
                ],
                'advantages': [
                    'Simpler structure and documentation',
                    'Fixed payment amounts',
                    'Immediate full ownership',
                    'Lower administrative costs'
                ],
                'considerations': [
                    'Less risk sharing compared to Musharaka',
                    'Fixed profit regardless of market changes',
                    'Early payment savings may be limited'
                ]
            },
            'ijara_muntahia': {
                'how_it_works': [
                    'Bank purchases and leases property to client',
                    'Monthly payment includes rent and ownership portion',
                    'Ownership percentage increases with each payment',
                    'Property maintenance responsibility varies',
                    'Full ownership transfers at end of lease'
                ],
                'advantages': [
                    'Lower initial payments possible',
                    'Flexible maintenance arrangements',
                    'Gradual ownership building',
                    'Can include property services'
                ],
                'considerations': [
                    'Complex ownership transfer process',
                    'Maintenance responsibility arrangements',
                    'Insurance and tax implications'
                ]
            }
        }
        
        return explanations.get(structure_type, {})
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO metadata"""
        return {
            'title': 'Murabaha Calculator - Islamic Home Finance | Sharia-Compliant Mortgage',
            'description': 'Free Islamic Murabaha calculator for home financing. Calculate payments for Diminishing Musharaka, Direct Murabaha, and Ijara structures. Riba-free mortgage alternative.',
            'keywords': 'Murabaha calculator, Islamic mortgage, Sharia compliant home finance, Diminishing Musharaka, Islamic home loan, riba-free financing',
            'canonical': '/calculators/murabaha'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Murabaha Calculator",
            "description": "Calculate Islamic home financing using Sharia-compliant Murabaha structures",
            "url": "https://calculatorapp.com/calculators/murabaha",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Diminishing Musharaka calculations",
                "Direct Murabaha calculations",
                "Ijara Muntahia calculations",
                "Payment schedule generation",
                "Conventional mortgage comparison",
                "Sharia compliance information",
                "Islamic finance principles",
                "Multi-currency support"
            ]
        }