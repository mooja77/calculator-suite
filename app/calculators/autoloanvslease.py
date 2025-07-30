"""
Auto Loan vs Lease Calculator with comprehensive comparison.
Compares the financial implications of financing vs leasing a vehicle.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class AutoloanvsleaseCalculator(BaseCalculator):
    """Compare auto loan vs lease options with comprehensive analysis."""
    
    # Regional defaults for loan and lease terms
    REGIONAL_DEFAULTS = {
        'US': {
            'currency': 'USD',
            'avg_loan_rate': 7.5,      # % annual
            'avg_lease_rate': 4.5,     # Money factor equivalent
            'sales_tax_rate': 8.5,     # Average US sales tax
            'registration_fee': 150,   # Annual
            'typical_loan_terms': [36, 48, 60, 72, 84],
            'typical_lease_terms': [24, 36, 39, 48],
            'lease_acquisition_fee': 695,
            'lease_disposition_fee': 395,
            'gap_insurance': 500,      # Annual
            'excess_mileage_penalty': 0.25,  # Per mile
            'wear_tear_limit': 3000,   # Maximum wear/tear charges
            'lease_tax_on_payment': True,  # Tax on lease payment vs full price
        },
        'UK': {
            'currency': 'GBP',
            'avg_loan_rate': 6.5,
            'avg_lease_rate': 3.8,
            'vat_rate': 20,            # VAT on lease payments
            'road_tax_annual': 165,
            'typical_loan_terms': [24, 36, 48, 60],
            'typical_lease_terms': [24, 36, 48],
            'lease_acquisition_fee': 250,
            'lease_disposition_fee': 150,
            'gap_insurance': 300,
            'excess_mileage_penalty': 0.15,  # Per mile (pence)
            'wear_tear_limit': 2000,
            'lease_tax_on_payment': True,
        },
        'CA': {
            'currency': 'CAD',
            'avg_loan_rate': 6.9,
            'avg_lease_rate': 4.2,
            'sales_tax_rate': 12,      # HST average
            'registration_fee': 120,
            'typical_loan_terms': [36, 48, 60, 72, 84],
            'typical_lease_terms': [24, 36, 39, 48],
            'lease_acquisition_fee': 800,
            'lease_disposition_fee': 450,
            'gap_insurance': 600,
            'excess_mileage_penalty': 0.20,
            'wear_tear_limit': 3500,
            'lease_tax_on_payment': True,
        },
        'AU': {
            'currency': 'AUD',
            'avg_loan_rate': 8.5,
            'avg_lease_rate': 5.2,
            'gst_rate': 10,
            'registration_fee': 250,
            'typical_loan_terms': [36, 48, 60, 72],
            'typical_lease_terms': [24, 36, 48],
            'lease_acquisition_fee': 990,
            'lease_disposition_fee': 550,
            'gap_insurance': 800,
            'excess_mileage_penalty': 0.30,  # AUD per km
            'wear_tear_limit': 4000,
            'lease_tax_on_payment': False,  # GST on full vehicle price
        }
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Compare auto loan vs lease with comprehensive analysis."""
        
        # Extract inputs
        vehicle_price = Decimal(str(inputs.get('vehicle_price', 0)))
        down_payment = Decimal(str(inputs.get('down_payment', 0)))
        trade_in_value = Decimal(str(inputs.get('trade_in_value', 0)))
        
        # Loan parameters
        loan_rate = Decimal(str(inputs.get('loan_rate', 0))) / 100
        loan_term = int(inputs.get('loan_term', 60))
        
        # Lease parameters
        lease_term = int(inputs.get('lease_term', 36))
        annual_mileage = int(inputs.get('annual_mileage', 12000))
        residual_percent = inputs.get('residual_percent')  # Optional, will estimate if not provided
        money_factor = inputs.get('money_factor')  # Optional, will use rate if not provided
        
        # Analysis period
        analysis_years = int(inputs.get('analysis_years', 6))  # Total comparison period
        country = inputs.get('country', 'US')
        
        # Get regional defaults
        defaults = self.REGIONAL_DEFAULTS.get(country, self.REGIONAL_DEFAULTS['US'])
        currency = defaults['currency']
        
        # Use defaults if not provided
        if money_factor is None:
            # Convert lease rate to money factor (rate/2400 for US, different for others)
            lease_rate = Decimal(str(inputs.get('lease_rate', defaults['avg_lease_rate']))) / 100
            money_factor = lease_rate / 2400 if country == 'US' else lease_rate / 100
        else:
            money_factor = Decimal(str(money_factor))
        
        # Estimate residual value if not provided
        if residual_percent is None:
            residual_percent = self._estimate_residual_value(lease_term, vehicle_price)
        else:
            residual_percent = Decimal(str(residual_percent))
        
        # Calculate loan scenario
        loan_analysis = self._calculate_loan_scenario(
            vehicle_price, down_payment, trade_in_value, loan_rate, loan_term,
            analysis_years, country, defaults
        )
        
        # Calculate lease scenario
        lease_analysis = self._calculate_lease_scenario(
            vehicle_price, down_payment, trade_in_value, lease_term,
            money_factor, residual_percent, annual_mileage,
            analysis_years, country, defaults
        )
        
        # Compare scenarios
        comparison = self._compare_scenarios(loan_analysis, lease_analysis, analysis_years)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            loan_analysis, lease_analysis, comparison, inputs, defaults
        )
        
        # Calculate break-even analysis
        break_even = self._calculate_break_even_analysis(
            vehicle_price, down_payment, trade_in_value, loan_rate, loan_term,
            lease_term, money_factor, residual_percent, annual_mileage,
            country, defaults
        )
        
        results = {
            'vehicle_price': vehicle_price.quantize(Decimal('0.01')),
            'loan_analysis': loan_analysis,
            'lease_analysis': lease_analysis,
            'comparison': comparison,
            'recommendations': recommendations,
            'break_even': break_even,
            'currency': currency,
            'inputs': {
                'vehicle_price': vehicle_price,
                'down_payment': down_payment,
                'trade_in_value': trade_in_value,
                'loan_rate': loan_rate * 100,
                'loan_term': loan_term,
                'lease_term': lease_term,
                'annual_mileage': annual_mileage,
                'residual_percent': residual_percent,
                'analysis_years': analysis_years,
                'country': country
            }
        }
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        # Add scenario variations
        results['scenarios'] = self._generate_scenario_variations(
            vehicle_price, down_payment, trade_in_value, loan_rate,
            loan_term, lease_term, money_factor, residual_percent,
            annual_mileage, analysis_years, country, defaults
        )
        
        return results
    
    def _calculate_loan_scenario(self, vehicle_price: Decimal, down_payment: Decimal,
                               trade_in_value: Decimal, loan_rate: Decimal, loan_term: int,
                               analysis_years: int, country: str, defaults: Dict) -> Dict[str, Any]:
        """Calculate comprehensive loan scenario analysis."""
        
        # Calculate loan amount
        net_loan_amount = vehicle_price - down_payment - trade_in_value
        
        # Add taxes and fees to loan if financed
        sales_tax_rate = Decimal(str(defaults.get('sales_tax_rate', defaults.get('vat_rate', defaults.get('gst_rate', 0)))))
        sales_tax = vehicle_price * (sales_tax_rate / 100)
        loan_fees = Decimal('500')  # Documentation, origination fees
        
        total_loan_amount = net_loan_amount + sales_tax + loan_fees
        
        # Calculate monthly payment
        if loan_rate > 0:
            monthly_rate = loan_rate / 12
            num_payments = loan_term
            monthly_payment = total_loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                            ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = total_loan_amount / loan_term
        
        # Calculate interest paid
        total_payments = monthly_payment * loan_term
        total_interest = total_payments - total_loan_amount
        
        # Calculate ownership costs during analysis period
        months_in_period = analysis_years * 12
        loan_payments_in_period = min(loan_term, months_in_period)
        
        # After loan is paid off, no monthly payments but still own the car
        total_loan_payments_in_period = monthly_payment * loan_payments_in_period
        
        # Calculate vehicle value at end of analysis period
        end_value = self._calculate_vehicle_depreciation(vehicle_price, analysis_years)
        
        # Insurance and maintenance costs (assume same for loan and lease)
        monthly_insurance = Decimal('150')  # Estimated
        monthly_maintenance = Decimal('100')  # Estimated
        annual_registration = Decimal(str(defaults['registration_fee']))
        
        total_insurance = monthly_insurance * months_in_period
        total_maintenance = monthly_maintenance * months_in_period
        total_registration = annual_registration * analysis_years
        
        # Total cost of ownership
        total_cost = (down_payment + trade_in_value + total_loan_payments_in_period +
                     total_insurance + total_maintenance + total_registration)
        
        # Net cost (total cost minus end value)
        net_cost = total_cost - end_value
        
        # Equity built
        if loan_term <= months_in_period:
            # Loan is paid off, equity equals vehicle value
            equity = end_value
        else:
            # Calculate remaining loan balance
            remaining_payments = loan_term - loan_payments_in_period
            if loan_rate > 0:
                remaining_balance = monthly_payment * (
                    ((1 + monthly_rate) ** remaining_payments - 1) /
                    (monthly_rate * (1 + monthly_rate) ** remaining_payments)
                )
            else:
                remaining_balance = monthly_payment * remaining_payments
            equity = max(Decimal('0'), end_value - remaining_balance)
        
        return {
            'loan_amount': total_loan_amount.quantize(Decimal('0.01')),
            'monthly_payment': monthly_payment.quantize(Decimal('0.01')),
            'total_interest': total_interest.quantize(Decimal('0.01')),
            'total_payments': total_payments.quantize(Decimal('0.01')),
            'payments_in_period': total_loan_payments_in_period.quantize(Decimal('0.01')),
            'insurance_cost': total_insurance.quantize(Decimal('0.01')),
            'maintenance_cost': total_maintenance.quantize(Decimal('0.01')),
            'registration_cost': total_registration.quantize(Decimal('0.01')),
            'total_cost': total_cost.quantize(Decimal('0.01')),
            'end_value': end_value.quantize(Decimal('0.01')),
            'equity': equity.quantize(Decimal('0.01')),
            'net_cost': net_cost.quantize(Decimal('0.01')),
            'cost_per_month': (net_cost / months_in_period).quantize(Decimal('0.01'))
        }
    
    def _calculate_lease_scenario(self, vehicle_price: Decimal, down_payment: Decimal,
                                trade_in_value: Decimal, lease_term: int,
                                money_factor: Decimal, residual_percent: Decimal,
                                annual_mileage: int, analysis_years: int,
                                country: str, defaults: Dict) -> Dict[str, Any]:
        """Calculate comprehensive lease scenario analysis."""
        
        # Calculate lease values
        residual_value = vehicle_price * (residual_percent / 100)
        depreciation_amount = vehicle_price - residual_value
        
        # Capitalized cost (net price after down payment and trade-in)
        cap_cost = vehicle_price - down_payment - trade_in_value
        
        # Monthly depreciation
        monthly_depreciation = depreciation_amount / lease_term
        
        # Monthly finance charge (rent charge)
        monthly_finance_charge = (cap_cost + residual_value) * money_factor
        
        # Base monthly payment
        base_monthly_payment = monthly_depreciation + monthly_finance_charge
        
        # Add taxes
        if defaults['lease_tax_on_payment']:
            # Tax on monthly payment
            tax_rate = Decimal(str(defaults.get('sales_tax_rate', defaults.get('vat_rate', defaults.get('gst_rate', 0)))))
            monthly_tax = base_monthly_payment * (tax_rate / 100)
        else:
            # Tax on full vehicle price (spread over lease term)
            tax_rate = Decimal(str(defaults.get('gst_rate', 0)))
            total_tax = vehicle_price * (tax_rate / 100)
            monthly_tax = total_tax / lease_term
        
        monthly_lease_payment = base_monthly_payment + monthly_tax
        
        # Lease fees
        acquisition_fee = Decimal(str(defaults['lease_acquisition_fee']))
        disposition_fee = Decimal(str(defaults['lease_disposition_fee']))
        gap_insurance_annual = Decimal(str(defaults['gap_insurance']))
        
        # Calculate costs for analysis period
        months_in_period = analysis_years * 12
        lease_cycles = months_in_period / lease_term
        full_lease_cycles = int(lease_cycles)
        remaining_months = months_in_period % lease_term
        
        # Total lease payments
        total_lease_payments = Decimal('0')
        total_acquisition_fees = Decimal('0')
        total_disposition_fees = Decimal('0')
        
        for cycle in range(full_lease_cycles):
            total_lease_payments += monthly_lease_payment * lease_term
            total_acquisition_fees += acquisition_fee
            if cycle < full_lease_cycles - 1 or remaining_months > 0:  # Not the last cycle
                total_disposition_fees += disposition_fee
        
        # Partial lease cycle
        if remaining_months > 0:
            total_lease_payments += monthly_lease_payment * remaining_months
            total_acquisition_fees += acquisition_fee
            
            # Early termination fee (estimated)
            early_termination_fee = monthly_lease_payment * (lease_term - remaining_months) * Decimal('0.5')
            total_disposition_fees += early_termination_fee
        
        # GAP insurance
        total_gap_insurance = gap_insurance_annual * analysis_years
        
        # Excess mileage charges (estimated)
        total_lease_miles = annual_mileage * analysis_years
        allowed_miles = (annual_mileage * lease_term / 12) * full_lease_cycles
        if remaining_months > 0:
            allowed_miles += (annual_mileage * remaining_months / 12)
        
        excess_miles = max(0, total_lease_miles - allowed_miles)
        excess_mileage_charges = excess_miles * Decimal(str(defaults['excess_mileage_penalty']))
        
        # Wear and tear charges (estimated)
        wear_tear_charges = Decimal(str(defaults['wear_tear_limit'])) * full_lease_cycles
        if remaining_months > 0:
            wear_tear_charges += Decimal(str(defaults['wear_tear_limit'])) * Decimal('0.5')
        
        # Insurance and maintenance (same as loan scenario)
        monthly_insurance = Decimal('150')
        monthly_maintenance = Decimal('80')  # Slightly lower for lease (warranty coverage)
        annual_registration = Decimal(str(defaults['registration_fee']))
        
        total_insurance = monthly_insurance * months_in_period
        total_maintenance = monthly_maintenance * months_in_period
        total_registration = annual_registration * analysis_years
        
        # Total lease cost
        total_cost = (down_payment + trade_in_value + total_lease_payments +
                     total_acquisition_fees + total_disposition_fees + total_gap_insurance +
                     excess_mileage_charges + wear_tear_charges + total_insurance +
                     total_maintenance + total_registration)
        
        # No equity built with leasing
        equity = Decimal('0')
        net_cost = total_cost  # No residual value to subtract
        
        return {
            'monthly_payment': monthly_lease_payment.quantize(Decimal('0.01')),
            'monthly_depreciation': monthly_depreciation.quantize(Decimal('0.01')),
            'monthly_finance_charge': monthly_finance_charge.quantize(Decimal('0.01')),
            'monthly_tax': monthly_tax.quantize(Decimal('0.01')),
            'total_lease_payments': total_lease_payments.quantize(Decimal('0.01')),
            'acquisition_fees': total_acquisition_fees.quantize(Decimal('0.01')),
            'disposition_fees': total_disposition_fees.quantize(Decimal('0.01')),
            'gap_insurance': total_gap_insurance.quantize(Decimal('0.01')),
            'excess_mileage_charges': excess_mileage_charges.quantize(Decimal('0.01')),
            'wear_tear_charges': wear_tear_charges.quantize(Decimal('0.01')),
            'insurance_cost': total_insurance.quantize(Decimal('0.01')),
            'maintenance_cost': total_maintenance.quantize(Decimal('0.01')),
            'registration_cost': total_registration.quantize(Decimal('0.01')),
            'total_cost': total_cost.quantize(Decimal('0.01')),
            'equity': equity,
            'net_cost': net_cost.quantize(Decimal('0.01')),
            'cost_per_month': (net_cost / months_in_period).quantize(Decimal('0.01')),
            'residual_value': residual_value.quantize(Decimal('0.01')),
            'lease_cycles': lease_cycles
        }
    
    def _compare_scenarios(self, loan: Dict, lease: Dict, analysis_years: int) -> Dict[str, Any]:
        """Compare loan vs lease scenarios."""
        
        # Cost comparison
        loan_advantage = lease['net_cost'] - loan['net_cost']
        
        if loan_advantage > 0:
            better_option = 'loan'
            savings = loan_advantage
        else:
            better_option = 'lease'
            savings = abs(loan_advantage)
        
        # Monthly payment comparison
        monthly_difference = loan['monthly_payment'] - lease['monthly_payment']
        
        # Total cash flow comparison
        loan_total_cash = loan['total_cost']
        lease_total_cash = lease['total_cost']
        cash_flow_difference = loan_total_cash - lease_total_cash
        
        # Ownership benefits
        ownership_benefit = loan['equity']
        
        # Cost per month comparison
        monthly_cost_difference = loan['cost_per_month'] - lease['cost_per_month']
        
        return {
            'better_option': better_option,
            'savings': savings.quantize(Decimal('0.01')),
            'monthly_payment_difference': monthly_difference.quantize(Decimal('0.01')),
            'cash_flow_difference': cash_flow_difference.quantize(Decimal('0.01')),
            'ownership_benefit': ownership_benefit.quantize(Decimal('0.01')),
            'monthly_cost_difference': monthly_cost_difference.quantize(Decimal('0.01')),
            'loan_total_cost': loan['net_cost'],
            'lease_total_cost': lease['net_cost']
        }
    
    def _generate_recommendations(self, loan: Dict, lease: Dict, comparison: Dict,
                                inputs: Dict, defaults: Dict) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Primary recommendation
        if comparison['better_option'] == 'loan':
            recommendations.append(
                f"Financing is recommended. You save {currency_service.format_currency(comparison['savings'], defaults['currency'])} "
                f"over {inputs.get('analysis_years', 6)} years and build {currency_service.format_currency(loan['equity'], defaults['currency'])} in equity."
            )
        else:
            recommendations.append(
                f"Leasing is recommended. You save {currency_service.format_currency(comparison['savings'], defaults['currency'])} "
                f"over {inputs.get('analysis_years', 6)} years with lower monthly payments."
            )
        
        # Monthly payment analysis
        if abs(comparison['monthly_payment_difference']) > 100:
            if comparison['monthly_payment_difference'] > 0:
                recommendations.append(
                    f"Lease payments are {currency_service.format_currency(abs(comparison['monthly_payment_difference']), defaults['currency'])} "
                    f"lower per month, improving cash flow."
                )
            else:
                recommendations.append(
                    f"Loan payments are only {currency_service.format_currency(abs(comparison['monthly_payment_difference']), defaults['currency'])} "
                    f"higher per month but you build equity."
                )
        
        # High mileage warning
        if inputs.get('annual_mileage', 12000) > 15000:
            recommendations.append(
                "High mileage usage makes leasing less attractive due to excess mileage penalties. Consider financing."
            )
        
        # Equity building
        if loan['equity'] > Decimal('10000'):
            recommendations.append(
                f"Financing builds significant equity ({currency_service.format_currency(loan['equity'], defaults['currency'])}) "
                f"which can be used for your next vehicle purchase."
            )
        
        # Cash flow considerations
        if comparison['monthly_payment_difference'] > Decimal('200'):
            recommendations.append(
                "Leasing offers significantly lower monthly payments, freeing up cash for other investments."
            )
        
        # Long-term ownership
        if inputs.get('analysis_years', 6) > 6:
            recommendations.append(
                "For long-term ownership (>6 years), financing typically becomes more cost-effective."
            )
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_break_even_analysis(self, vehicle_price: Decimal, down_payment: Decimal,
                                     trade_in_value: Decimal, loan_rate: Decimal, loan_term: int,
                                     lease_term: int, money_factor: Decimal, residual_percent: Decimal,
                                     annual_mileage: int, country: str, defaults: Dict) -> Dict[str, Any]:
        """Calculate break-even analysis between loan and lease."""
        
        # Find break-even point in months
        break_even_months = None
        for months in range(12, 121, 6):  # Check every 6 months up to 10 years
            years = months / 12
            
            loan_analysis = self._calculate_loan_scenario(
                vehicle_price, down_payment, trade_in_value, loan_rate, loan_term,
                int(years), country, defaults
            )
            
            lease_analysis = self._calculate_lease_scenario(
                vehicle_price, down_payment, trade_in_value, lease_term,
                money_factor, residual_percent, annual_mileage,
                int(years), country, defaults
            )
            
            if loan_analysis['net_cost'] <= lease_analysis['net_cost']:
                break_even_months = months
                break
        
        # Calculate mileage break-even
        mileage_break_even = None
        base_mileage = 12000  # Standard lease mileage
        
        for mileage in range(base_mileage, 30001, 1000):
            lease_analysis = self._calculate_lease_scenario(
                vehicle_price, down_payment, trade_in_value, lease_term,
                money_factor, residual_percent, mileage,
                3, country, defaults  # 3-year analysis
            )
            
            loan_analysis = self._calculate_loan_scenario(
                vehicle_price, down_payment, trade_in_value, loan_rate, loan_term,
                3, country, defaults
            )
            
            if lease_analysis['net_cost'] >= loan_analysis['net_cost']:
                mileage_break_even = mileage
                break
        
        return {
            'time_break_even_months': break_even_months,
            'time_break_even_years': break_even_months / 12 if break_even_months else None,
            'mileage_break_even': mileage_break_even
        }
    
    def _generate_scenario_variations(self, vehicle_price: Decimal, down_payment: Decimal,
                                    trade_in_value: Decimal, loan_rate: Decimal, loan_term: int,
                                    lease_term: int, money_factor: Decimal, residual_percent: Decimal,
                                    annual_mileage: int, analysis_years: int, country: str,
                                    defaults: Dict) -> List[Dict]:
        """Generate scenario variations."""
        
        scenarios = []
        
        # Scenario 1: Higher down payment
        higher_down = down_payment + Decimal('5000')
        loan_scenario = self._calculate_loan_scenario(
            vehicle_price, higher_down, trade_in_value, loan_rate, loan_term,
            analysis_years, country, defaults
        )
        lease_scenario = self._calculate_lease_scenario(
            vehicle_price, higher_down, trade_in_value, lease_term,
            money_factor, residual_percent, annual_mileage,
            analysis_years, country, defaults
        )
        comparison = self._compare_scenarios(loan_scenario, lease_scenario, analysis_years)
        
        scenarios.append({
            'name': 'Higher Down Payment (+$5,000)',
            'description': 'With additional $5,000 down payment',
            'loan_cost': loan_scenario['net_cost'],
            'lease_cost': lease_scenario['net_cost'],
            'better_option': comparison['better_option'],
            'savings': comparison['savings']
        })
        
        # Scenario 2: Lower mileage
        if annual_mileage > 10000:
            lower_mileage = max(10000, annual_mileage - 3000)
            lease_scenario = self._calculate_lease_scenario(
                vehicle_price, down_payment, trade_in_value, lease_term,
                money_factor, residual_percent, lower_mileage,
                analysis_years, country, defaults
            )
            comparison = self._compare_scenarios(loan_scenario, lease_scenario, analysis_years)
            
            scenarios.append({
                'name': f'Lower Mileage ({lower_mileage:,}/year)',
                'description': f'With {lower_mileage:,} miles per year',
                'loan_cost': loan_scenario['net_cost'],
                'lease_cost': lease_scenario['net_cost'],
                'better_option': comparison['better_option'],
                'savings': comparison['savings']
            })
        
        # Scenario 3: Extended loan term
        if loan_term < 72:
            extended_term = min(84, loan_term + 12)
            loan_scenario = self._calculate_loan_scenario(
                vehicle_price, down_payment, trade_in_value, loan_rate, extended_term,
                analysis_years, country, defaults
            )
            comparison = self._compare_scenarios(loan_scenario, lease_scenario, analysis_years)
            
            scenarios.append({
                'name': f'Extended Loan ({extended_term} months)',
                'description': f'With {extended_term}-month financing',
                'loan_cost': loan_scenario['net_cost'],
                'lease_cost': lease_scenario['net_cost'],
                'better_option': comparison['better_option'],
                'savings': comparison['savings']
            })
        
        return scenarios[:3]  # Return top 3 scenarios
    
    def _estimate_residual_value(self, lease_term: int, vehicle_price: Decimal) -> Decimal:
        """Estimate residual value percentage based on lease term."""
        # Industry standard residual values
        if lease_term <= 24:
            return Decimal('65')  # 65%
        elif lease_term <= 36:
            return Decimal('55')  # 55%
        elif lease_term <= 48:
            return Decimal('45')  # 45%
        else:
            return Decimal('35')  # 35%
    
    def _calculate_vehicle_depreciation(self, initial_value: Decimal, years: int) -> Decimal:
        """Calculate vehicle value after depreciation."""
        # Standard depreciation curve
        depreciation_rates = [0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02]
        
        current_value = initial_value
        for year in range(min(years, len(depreciation_rates))):
            current_value = current_value * (1 - Decimal(str(depreciation_rates[year])))
        
        # After 10 years, depreciate at 2% annually
        if years > 10:
            remaining_years = years - 10
            current_value = current_value * ((1 - Decimal('0.02')) ** remaining_years)
        
        # Minimum value is 5% of original
        min_value = initial_value * Decimal('0.05')
        return max(current_value, min_value)
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Format main result
        if 'vehicle_price' in results:
            formatted['vehicle_price'] = currency_service.format_currency(results['vehicle_price'], currency)
        
        # Format loan analysis
        if 'loan_analysis' in results:
            formatted['loan_analysis'] = {}
            for key, value in results['loan_analysis'].items():
                if isinstance(value, Decimal):
                    formatted['loan_analysis'][key] = currency_service.format_currency(value, currency)
        
        # Format lease analysis
        if 'lease_analysis' in results:
            formatted['lease_analysis'] = {}
            for key, value in results['lease_analysis'].items():
                if isinstance(value, Decimal):
                    formatted['lease_analysis'][key] = currency_service.format_currency(value, currency)
        
        # Format comparison
        if 'comparison' in results:
            formatted['comparison'] = {}
            for key, value in results['comparison'].items():
                if isinstance(value, Decimal) and key != 'better_option':
                    formatted['comparison'][key] = currency_service.format_currency(value, currency)
        
        # Format scenarios
        if 'scenarios' in results:
            formatted['scenarios'] = []
            for scenario in results['scenarios']:
                formatted_scenario = scenario.copy()
                for key in ['loan_cost', 'lease_cost', 'savings']:
                    if key in scenario:
                        formatted_scenario[f'{key}_formatted'] = currency_service.format_currency(scenario[key], currency)
                formatted['scenarios'].append(formatted_scenario)
        
        return formatted
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate calculator inputs."""
        self.clear_errors()
        
        # Validate vehicle price
        vehicle_price = self.validate_number(
            inputs.get('vehicle_price', 0),
            'Vehicle price',
            min_val=10000,
            max_val=500000
        )
        if vehicle_price is None:
            return False
        
        # Validate down payment
        down_payment = self.validate_number(
            inputs.get('down_payment', 0),
            'Down payment',
            min_val=0,
            max_val=100000
        )
        if down_payment is None:
            return False
        
        # Validate trade-in value
        trade_in_value = self.validate_number(
            inputs.get('trade_in_value', 0),
            'Trade-in value',
            min_val=0,
            max_val=100000
        )
        if trade_in_value is None:
            return False
        
        # Validate loan rate
        loan_rate = self.validate_number(
            inputs.get('loan_rate', 7.5),
            'Loan rate',
            min_val=0,
            max_val=25
        )
        if loan_rate is None:
            return False
        
        # Validate loan term
        loan_term = self.validate_number(
            inputs.get('loan_term', 60),
            'Loan term',
            min_val=12,
            max_val=84
        )
        if loan_term is None:
            return False
        
        # Validate lease term
        lease_term = self.validate_number(
            inputs.get('lease_term', 36),
            'Lease term',
            min_val=12,
            max_val=60
        )
        if lease_term is None:
            return False
        
        # Validate annual mileage
        annual_mileage = self.validate_number(
            inputs.get('annual_mileage', 12000),
            'Annual mileage',
            min_val=5000,
            max_val=50000
        )
        if annual_mileage is None:
            return False
        
        # Validate analysis years
        analysis_years = self.validate_number(
            inputs.get('analysis_years', 6),
            'Analysis years',
            min_val=2,
            max_val=15
        )
        if analysis_years is None:
            return False
        
        # Validate residual percent if provided
        residual_percent = inputs.get('residual_percent')
        if residual_percent is not None:
            residual = self.validate_number(
                residual_percent,
                'Residual percentage',
                min_val=20,
                max_val=80
            )
            if residual is None:
                return False
        
        # Validate money factor if provided
        money_factor = inputs.get('money_factor')
        if money_factor is not None:
            factor = self.validate_number(
                money_factor,
                'Money factor',
                min_val=0.0001,
                max_val=0.01
            )
            if factor is None:
                return False
        
        # Validate country
        country = inputs.get('country', 'US')
        if country not in self.REGIONAL_DEFAULTS:
            self.add_error(f"Unsupported country: {country}")
        
        # Validate down payment doesn't exceed vehicle price
        if vehicle_price and down_payment and down_payment > vehicle_price:
            self.add_error("Down payment cannot exceed vehicle price")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Auto Loan vs Lease Calculator 2024 - Should You Buy or Lease a Car?',
            'description': 'Free auto loan vs lease calculator. Compare financing vs leasing costs, monthly payments, equity, and total cost of ownership. Get personalized recommendations.',
            'keywords': 'auto loan vs lease calculator, car lease vs buy calculator, lease or buy car calculator, auto financing calculator, car payment calculator, lease calculator',
            'canonical': '/calculators/autoloanvslease/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Auto Loan vs Lease Calculator",
            "description": "Compare auto loan vs lease options with comprehensive cost analysis and recommendations",
            "url": "https://yourcalcsite.com/calculators/autoloanvslease/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Comprehensive loan vs lease comparison",
                "Multi-country support (US, UK, Canada, Australia)",
                "Total cost of ownership analysis",
                "Monthly payment comparison",
                "Equity building analysis",
                "Break-even analysis",
                "Scenario variations",
                "Personalized recommendations",
                "Mileage penalty calculations",
                "Wear and tear cost estimates"
            ]
        }