"""
Car Affordability Calculator with total cost of ownership analysis.
Calculates maximum affordable car price based on income and comprehensive ownership costs.
"""
from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.cache import cache_calculation
from app.services.currency import currency_service

@register_calculator
class CaraffordabilityCalculator(BaseCalculator):
    """Calculate maximum affordable car price with total cost of ownership."""
    
    # Regional defaults for car costs and regulations
    REGIONAL_DEFAULTS = {
        'US': {
            'currency': 'USD',
            'transport_ratio': 15,  # % of income for transportation
            'max_transport_ratio': 20,  # Maximum recommended
            'sales_tax_rate': 8.5,  # Average US sales tax
            'registration_fee': 150,  # Annual registration
            'inspection_fee': 50,   # Annual inspection
            'insurance_rates': {    # Annual insurance by age group
                'young': 2400,      # Under 25
                'middle': 1800,     # 25-55
                'senior': 1500      # 55+
            },
            'fuel_price_per_gallon': 3.50,
            'maintenance_rates': {  # Annual maintenance by car age
                'new': 0.05,        # 5% of car value
                'used_3': 0.08,     # 8% for 3-5 years
                'used_7': 0.12,     # 12% for 6-10 years
                'old': 0.18         # 18% for 10+ years
            },
            'depreciation_rates': { # Annual depreciation
                'year_1': 0.20,     # 20% first year
                'year_2': 0.15,     # 15% second year
                'year_3': 0.12,     # 12% third year
                'annual': 0.10      # 10% thereafter
            },
            'avg_loan_rate': 7.5,   # % annual
            'avg_loan_term': 60,    # months
            'min_down_payment': 10, # % minimum
        },
        'UK': {
            'currency': 'GBP',
            'transport_ratio': 12,  # Lower due to public transport
            'max_transport_ratio': 18,
            'vat_rate': 20,         # VAT on new cars
            'road_tax_annual': 165, # Average road tax
            'mot_fee': 55,          # Annual MOT
            'insurance_rates': {
                'young': 2000,
                'middle': 800,
                'senior': 600
            },
            'fuel_price_per_litre': 1.45,
            'maintenance_rates': {
                'new': 0.04,
                'used_3': 0.07,
                'used_7': 0.11,
                'old': 0.16
            },
            'depreciation_rates': {
                'year_1': 0.18,
                'year_2': 0.14,
                'year_3': 0.11,
                'annual': 0.09
            },
            'avg_loan_rate': 6.5,
            'avg_loan_term': 48,
            'min_down_payment': 10,
        },
        'CA': {
            'currency': 'CAD',
            'transport_ratio': 14,
            'max_transport_ratio': 19,
            'sales_tax_rate': 12,   # HST average
            'registration_fee': 120,
            'inspection_fee': 40,
            'insurance_rates': {
                'young': 3000,      # Higher in Canada
                'middle': 1500,
                'senior': 1200
            },
            'fuel_price_per_litre': 1.50,
            'maintenance_rates': {
                'new': 0.05,
                'used_3': 0.08,
                'used_7': 0.12,
                'old': 0.17
            },
            'depreciation_rates': {
                'year_1': 0.19,
                'year_2': 0.14,
                'year_3': 0.11,
                'annual': 0.09
            },
            'avg_loan_rate': 6.9,
            'avg_loan_term': 60,
            'min_down_payment': 10,
        },
        'AU': {
            'currency': 'AUD',
            'transport_ratio': 13,
            'max_transport_ratio': 18,
            'gst_rate': 10,         # GST on cars
            'registration_fee': 250,# Higher in Australia
            'inspection_fee': 45,
            'insurance_rates': {
                'young': 2200,
                'middle': 1200,
                'senior': 900
            },
            'fuel_price_per_litre': 1.60,
            'maintenance_rates': {
                'new': 0.06,        # Higher due to service costs
                'used_3': 0.09,
                'used_7': 0.13,
                'old': 0.19
            },
            'depreciation_rates': {
                'year_1': 0.17,
                'year_2': 0.13,
                'year_3': 0.10,
                'annual': 0.08
            },
            'avg_loan_rate': 8.5,   # Higher rates
            'avg_loan_term': 60,
            'min_down_payment': 20, # Higher down payment typical
        }
    }
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate maximum affordable car price with total cost analysis."""
        # Extract inputs
        annual_income = Decimal(str(inputs.get('annual_income', 0)))
        monthly_debt = Decimal(str(inputs.get('monthly_debt', 0)))
        down_payment = Decimal(str(inputs.get('down_payment', 0)))
        loan_term = int(inputs.get('loan_term', 60))
        loan_rate = Decimal(str(inputs.get('loan_rate', 0))) / 100
        ownership_years = int(inputs.get('ownership_years', 5))
        annual_mileage = int(inputs.get('annual_mileage', 12000))
        car_age = inputs.get('car_age', 'new')  # new, used_3, used_7, old
        driver_age_group = inputs.get('driver_age_group', 'middle')  # young, middle, senior
        country = inputs.get('country', 'US')
        
        # Get regional defaults
        defaults = self.REGIONAL_DEFAULTS.get(country, self.REGIONAL_DEFAULTS['US'])
        currency = defaults['currency']
        
        # Calculate maximum monthly transportation budget
        monthly_income = annual_income / 12
        max_transport_budget = monthly_income * (Decimal(str(defaults['transport_ratio'])) / 100)
        
        # Calculate affordable car price
        affordability_analysis = self._calculate_car_affordability(
            max_transport_budget, down_payment, loan_rate, loan_term,
            annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        # Calculate total cost of ownership
        total_cost_analysis = self._calculate_total_cost_ownership(
            affordability_analysis['car_price'], down_payment, loan_rate, loan_term,
            ownership_years, annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        # Calculate monthly budget breakdown
        monthly_breakdown = self._calculate_monthly_breakdown(
            affordability_analysis['car_price'], down_payment, loan_rate, loan_term,
            annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            affordability_analysis, total_cost_analysis, monthly_breakdown,
            monthly_income, defaults
        )
        
        # Calculate alternative scenarios
        scenarios = self._generate_scenarios(
            annual_income, monthly_debt, down_payment, annual_mileage,
            car_age, driver_age_group, country, defaults
        )
        
        results = {
            'affordable_price': affordability_analysis['car_price'].quantize(Decimal('0.01')),
            'loan_amount': affordability_analysis['loan_amount'].quantize(Decimal('0.01')),
            'down_payment': down_payment.quantize(Decimal('0.01')),
            'monthly_payment': affordability_analysis['monthly_payment'].quantize(Decimal('0.01')),
            'max_transport_budget': max_transport_budget.quantize(Decimal('0.01')),
            'monthly_income': monthly_income.quantize(Decimal('0.01')),
            'transport_ratio': ((affordability_analysis['total_monthly_cost'] / monthly_income) * 100).quantize(Decimal('0.1')),
            'currency': currency,
            'monthly_breakdown': monthly_breakdown,
            'total_cost_analysis': total_cost_analysis,
            'recommendations': recommendations,
            'scenarios': scenarios,
            'inputs': {
                'annual_income': annual_income,
                'monthly_debt': monthly_debt,
                'loan_term': loan_term,
                'ownership_years': ownership_years,
                'annual_mileage': annual_mileage,
                'car_age': car_age,
                'driver_age_group': driver_age_group,
                'country': country
            }
        }
        
        # Add formatted values
        results['formatted'] = self._format_results(results, currency)
        
        return results
    
    def _calculate_car_affordability(self, max_budget: Decimal, down_payment: Decimal,
                                   loan_rate: Decimal, loan_term: int,
                                   annual_mileage: int, car_age: str,
                                   driver_age_group: str, country: str,
                                   defaults: Dict) -> Dict[str, Decimal]:
        """Calculate maximum affordable car price iteratively."""
        
        # Start with estimated car price and refine
        estimated_price = Decimal('30000')  # Starting estimate
        tolerance = Decimal('100')
        max_iterations = 20
        
        for iteration in range(max_iterations):
            # Calculate total monthly costs for this price
            monthly_costs = self._calculate_monthly_breakdown(
                estimated_price, down_payment, loan_rate, loan_term,
                annual_mileage, car_age, driver_age_group, country, defaults
            )
            
            total_monthly = monthly_costs['total_monthly_cost']
            
            # Check if within budget and tolerance
            if abs(total_monthly - max_budget) <= tolerance:
                break
            
            # Adjust price based on budget difference
            if total_monthly > max_budget:
                # Too expensive, reduce price
                adjustment_ratio = max_budget / total_monthly
                estimated_price = estimated_price * adjustment_ratio * Decimal('0.95')  # Conservative adjustment
            else:
                # Can afford more, increase price
                adjustment_ratio = max_budget / total_monthly
                estimated_price = estimated_price * adjustment_ratio * Decimal('1.02')  # Conservative increase
            
            # Prevent infinite loops with reasonable bounds
            if estimated_price < Decimal('5000'):
                estimated_price = Decimal('5000')
                break
            elif estimated_price > Decimal('200000'):
                estimated_price = Decimal('200000')
                break
        
        # Calculate final values
        loan_amount = max(Decimal('0'), estimated_price - down_payment)
        
        # Calculate monthly loan payment
        if loan_rate > 0 and loan_amount > 0:
            monthly_rate = loan_rate / 12
            num_payments = loan_term
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                            ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / loan_term if loan_term > 0 else Decimal('0')
        
        # Recalculate total monthly cost for final price
        final_costs = self._calculate_monthly_breakdown(
            estimated_price, down_payment, loan_rate, loan_term,
            annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        return {
            'car_price': estimated_price,
            'loan_amount': loan_amount,
            'monthly_payment': monthly_payment,
            'total_monthly_cost': final_costs['total_monthly_cost']
        }
    
    def _calculate_monthly_breakdown(self, car_price: Decimal, down_payment: Decimal,
                                   loan_rate: Decimal, loan_term: int,
                                   annual_mileage: int, car_age: str,
                                   driver_age_group: str, country: str,
                                   defaults: Dict) -> Dict[str, Decimal]:
        """Calculate detailed monthly cost breakdown."""
        
        # Loan payment
        loan_amount = max(Decimal('0'), car_price - down_payment)
        if loan_rate > 0 and loan_amount > 0:
            monthly_rate = loan_rate / 12
            num_payments = loan_term
            monthly_loan_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                                 ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_loan_payment = loan_amount / loan_term if loan_term > 0 else Decimal('0')
        
        # Insurance (monthly)
        annual_insurance = Decimal(str(defaults['insurance_rates'][driver_age_group]))
        monthly_insurance = annual_insurance / 12
        
        # Registration and fees (monthly equivalent)
        annual_fees = (
            Decimal(str(defaults['registration_fee'])) +
            Decimal(str(defaults.get('inspection_fee', defaults.get('mot_fee', 0))))
        )
        if country == 'UK':
            annual_fees += Decimal(str(defaults['road_tax_annual']))
        monthly_fees = annual_fees / 12
        
        # Fuel costs (monthly)
        if country == 'US':
            # US uses gallons
            mpg = Decimal('25')  # Average fuel economy
            monthly_gallons = Decimal(str(annual_mileage)) / 12 / mpg
            fuel_price = Decimal(str(defaults['fuel_price_per_gallon']))
            monthly_fuel = monthly_gallons * fuel_price
        else:
            # Other countries use litres
            litres_per_100km = Decimal('8')  # Average consumption
            km_per_mile = Decimal('1.60934')
            monthly_km = Decimal(str(annual_mileage)) * km_per_mile / 12
            monthly_litres = monthly_km * litres_per_100km / 100
            fuel_price = Decimal(str(defaults['fuel_price_per_litre']))
            monthly_fuel = monthly_litres * fuel_price
        
        # Maintenance (monthly)
        maintenance_rate = Decimal(str(defaults['maintenance_rates'][car_age]))
        annual_maintenance = car_price * maintenance_rate
        monthly_maintenance = annual_maintenance / 12
        
        # Depreciation (monthly) - only for new/newer cars
        monthly_depreciation = Decimal('0')
        if car_age in ['new', 'used_3']:
            if car_age == 'new':
                annual_depreciation = car_price * Decimal(str(defaults['depreciation_rates']['year_1']))
            else:
                annual_depreciation = car_price * Decimal(str(defaults['depreciation_rates']['annual']))
            monthly_depreciation = annual_depreciation / 12
        
        # Total monthly cost
        total_monthly = (monthly_loan_payment + monthly_insurance + monthly_fees +
                        monthly_fuel + monthly_maintenance + monthly_depreciation)
        
        return {
            'loan_payment': monthly_loan_payment.quantize(Decimal('0.01')),
            'insurance': monthly_insurance.quantize(Decimal('0.01')),
            'registration_fees': monthly_fees.quantize(Decimal('0.01')),
            'fuel': monthly_fuel.quantize(Decimal('0.01')),
            'maintenance': monthly_maintenance.quantize(Decimal('0.01')),
            'depreciation': monthly_depreciation.quantize(Decimal('0.01')),
            'total_monthly_cost': total_monthly.quantize(Decimal('0.01'))
        }
    
    def _calculate_total_cost_ownership(self, car_price: Decimal, down_payment: Decimal,
                                      loan_rate: Decimal, loan_term: int,
                                      ownership_years: int, annual_mileage: int,
                                      car_age: str, driver_age_group: str,
                                      country: str, defaults: Dict) -> Dict[str, Decimal]:
        """Calculate total cost of ownership over specified period."""
        
        # Initial costs
        purchase_price = car_price
        sales_tax_rate = Decimal(str(defaults.get('sales_tax_rate', defaults.get('vat_rate', defaults.get('gst_rate', 0)))))
        sales_tax = car_price * (sales_tax_rate / 100)
        initial_fees = Decimal('500')  # Documentation, dealer fees, etc.
        
        total_initial_cost = purchase_price + sales_tax + initial_fees
        
        # Financing costs
        loan_amount = max(Decimal('0'), car_price - down_payment)
        if loan_rate > 0 and loan_amount > 0:
            monthly_rate = loan_rate / 12
            num_payments = min(loan_term, ownership_years * 12)  # Don't exceed ownership period
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                            ((1 + monthly_rate) ** num_payments - 1)
            total_loan_payments = monthly_payment * num_payments
            total_interest = total_loan_payments - loan_amount
        else:
            total_loan_payments = loan_amount
            total_interest = Decimal('0')
        
        # Operating costs over ownership period
        monthly_costs = self._calculate_monthly_breakdown(
            car_price, down_payment, loan_rate, loan_term,
            annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        total_insurance = monthly_costs['insurance'] * 12 * ownership_years
        total_fuel = monthly_costs['fuel'] * 12 * ownership_years
        total_maintenance = monthly_costs['maintenance'] * 12 * ownership_years
        total_fees = monthly_costs['registration_fees'] * 12 * ownership_years
        
        # Calculate depreciation and resale value
        resale_value = self._calculate_resale_value(car_price, ownership_years, car_age, defaults)
        total_depreciation = car_price - resale_value
        
        # Total cost of ownership
        total_cost = (down_payment + total_loan_payments + total_interest +
                     total_insurance + total_fuel + total_maintenance + 
                     total_fees + sales_tax + initial_fees + total_depreciation)
        
        # Cost per mile/km
        total_miles = annual_mileage * ownership_years
        cost_per_mile = total_cost / Decimal(str(total_miles)) if total_miles > 0 else Decimal('0')
        
        return {
            'total_cost': total_cost.quantize(Decimal('0.01')),
            'initial_cost': total_initial_cost.quantize(Decimal('0.01')),
            'financing_cost': (total_loan_payments + total_interest).quantize(Decimal('0.01')),
            'operating_cost': (total_insurance + total_fuel + total_maintenance + total_fees).quantize(Decimal('0.01')),
            'depreciation': total_depreciation.quantize(Decimal('0.01')),
            'resale_value': resale_value.quantize(Decimal('0.01')),
            'cost_per_mile': cost_per_mile.quantize(Decimal('0.01')),
            'breakdown': {
                'purchase_price': purchase_price.quantize(Decimal('0.01')),
                'sales_tax': sales_tax.quantize(Decimal('0.01')),
                'financing': total_interest.quantize(Decimal('0.01')),
                'insurance': total_insurance.quantize(Decimal('0.01')),
                'fuel': total_fuel.quantize(Decimal('0.01')),
                'maintenance': total_maintenance.quantize(Decimal('0.01')),
                'fees': total_fees.quantize(Decimal('0.01'))
            }
        }
    
    def _calculate_resale_value(self, initial_price: Decimal, ownership_years: int,
                              car_age: str, defaults: Dict) -> Decimal:
        """Calculate estimated resale value after ownership period."""
        
        # Determine starting age factor
        if car_age == 'new':
            current_value = initial_price
            years_old = 0
        elif car_age == 'used_3':
            current_value = initial_price  # Already depreciated to current value
            years_old = 3
        elif car_age == 'used_7':
            current_value = initial_price
            years_old = 7
        else:  # old
            current_value = initial_price
            years_old = 10
        
        # Apply depreciation for ownership period
        depreciation_rates = defaults['depreciation_rates']
        value = current_value
        
        for year in range(ownership_years):
            current_age = years_old + year
            
            if current_age == 0:  # First year
                depreciation_rate = Decimal(str(depreciation_rates['year_1']))
            elif current_age == 1:  # Second year
                depreciation_rate = Decimal(str(depreciation_rates['year_2']))
            elif current_age == 2:  # Third year
                depreciation_rate = Decimal(str(depreciation_rates['year_3']))
            else:  # Fourth year and beyond
                depreciation_rate = Decimal(str(depreciation_rates['annual']))
            
            value = value * (1 - depreciation_rate)
        
        # Minimum resale value (scrap value)
        min_value = initial_price * Decimal('0.05')  # 5% minimum
        return max(value, min_value)
    
    def _generate_recommendations(self, affordability: Dict, total_cost: Dict,
                                monthly_breakdown: Dict, monthly_income: Decimal,
                                defaults: Dict) -> List[str]:
        """Generate personalized car buying recommendations."""
        recommendations = []
        
        # Transport ratio analysis
        transport_ratio = (monthly_breakdown['total_monthly_cost'] / monthly_income) * 100
        max_ratio = Decimal(str(defaults['max_transport_ratio']))
        
        if transport_ratio > max_ratio:
            recommendations.append(
                f"Your transportation costs are {transport_ratio:.1f}% of income. "
                f"Consider keeping it under {max_ratio}% for better financial health."
            )
        
        # Down payment recommendation
        if affordability['loan_amount'] > affordability['car_price'] * Decimal('0.8'):
            recommendations.append(
                "Consider a larger down payment to reduce monthly payments and interest costs."
            )
        
        # Cost per mile analysis
        if total_cost['cost_per_mile'] > Decimal('0.60'):
            recommendations.append(
                f"At ${total_cost['cost_per_mile']:.2f} per mile, consider a more fuel-efficient "
                f"or reliable vehicle to reduce operating costs."
            )
        
        # Insurance optimization
        if monthly_breakdown['insurance'] > monthly_breakdown['loan_payment']:
            recommendations.append(
                "Insurance costs are high. Shop around for better rates or consider a less expensive vehicle."
            )
        
        # Maintenance cost warning
        if monthly_breakdown['maintenance'] > monthly_breakdown['loan_payment'] * Decimal('0.5'):
            recommendations.append(
                "High maintenance costs expected. Consider a newer or more reliable vehicle."
            )
        
        # Depreciation warning
        if monthly_breakdown.get('depreciation', Decimal('0')) > monthly_breakdown['loan_payment'] * Decimal('0.3'):
            recommendations.append(
                "High depreciation costs. Consider a certified pre-owned vehicle to reduce depreciation."
            )
        
        return recommendations
    
    def _generate_scenarios(self, annual_income: Decimal, monthly_debt: Decimal,
                          down_payment: Decimal, annual_mileage: int,
                          car_age: str, driver_age_group: str,
                          country: str, defaults: Dict) -> List[Dict]:
        """Generate alternative car buying scenarios."""
        
        scenarios = []
        monthly_income = annual_income / 12
        base_budget = monthly_income * (Decimal(str(defaults['transport_ratio'])) / 100)
        
        # Scenario 1: Used car (if currently considering new)
        if car_age == 'new':
            scenario1 = self._calculate_scenario(
                base_budget, down_payment, 'used_3', annual_mileage,
                driver_age_group, country, defaults
            )
            scenario1['name'] = "3-Year Old Used Car"
            scenario1['description'] = "Consider a 3-year old vehicle"
            scenarios.append(scenario1)
        
        # Scenario 2: Higher down payment
        higher_down = down_payment + (monthly_income * 2)  # 2 months extra savings
        scenario2 = self._calculate_scenario(
            base_budget, higher_down, car_age, annual_mileage,
            driver_age_group, country, defaults
        )
        scenario2['name'] = "Higher Down Payment"
        scenario2['description'] = f"With {currency_service.format_currency(higher_down, defaults['currency'])} down payment"
        scenarios.append(scenario2)
        
        # Scenario 3: Lower mileage (if high mileage)
        if annual_mileage > 15000:
            scenario3 = self._calculate_scenario(
                base_budget, down_payment, car_age, 12000,
                driver_age_group, country, defaults
            )
            scenario3['name'] = "Lower Mileage (12k/year)"
            scenario3['description'] = "With reduced annual mileage"
            scenarios.append(scenario3)
        
        # Scenario 4: Certified Pre-Owned (if considering used)
        if car_age != 'new':
            scenario4 = self._calculate_scenario(
                base_budget, down_payment, 'used_3', annual_mileage,
                driver_age_group, country, defaults
            )
            scenario4['name'] = "Certified Pre-Owned"
            scenario4['description'] = "Certified pre-owned with warranty"
            scenarios.append(scenario4)
        
        return scenarios[:3]  # Return top 3 scenarios
    
    def _calculate_scenario(self, max_budget: Decimal, down_payment: Decimal,
                          car_age: str, annual_mileage: int,
                          driver_age_group: str, country: str,
                          defaults: Dict) -> Dict[str, Any]:
        """Calculate a specific car buying scenario."""
        
        # Use average loan terms for scenario
        loan_rate = Decimal(str(defaults['avg_loan_rate'])) / 100
        loan_term = defaults['avg_loan_term']
        
        # Calculate affordability for this scenario
        affordability = self._calculate_car_affordability(
            max_budget, down_payment, loan_rate, loan_term,
            annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        # Calculate total cost for 5-year ownership
        total_cost = self._calculate_total_cost_ownership(
            affordability['car_price'], down_payment, loan_rate, loan_term,
            5, annual_mileage, car_age, driver_age_group, country, defaults
        )
        
        return {
            'affordable_price': affordability['car_price'].quantize(Decimal('0.01')),
            'monthly_payment': affordability['monthly_payment'].quantize(Decimal('0.01')),
            'total_monthly_cost': affordability['total_monthly_cost'].quantize(Decimal('0.01')),
            'total_5year_cost': total_cost['total_cost'].quantize(Decimal('0.01')),
            'cost_per_mile': total_cost['cost_per_mile'].quantize(Decimal('0.01'))
        }
    
    def _format_results(self, results: Dict[str, Any], currency: str) -> Dict[str, str]:
        """Format monetary values with currency."""
        formatted = {}
        
        # Main results
        main_fields = [
            'affordable_price', 'loan_amount', 'down_payment', 
            'monthly_payment', 'max_transport_budget', 'monthly_income'
        ]
        for field in main_fields:
            if field in results and isinstance(results[field], Decimal):
                formatted[field] = currency_service.format_currency(results[field], currency)
        
        # Monthly breakdown
        if 'monthly_breakdown' in results:
            formatted['monthly_breakdown'] = {}
            for key, value in results['monthly_breakdown'].items():
                formatted['monthly_breakdown'][key] = currency_service.format_currency(value, currency)
        
        # Total cost analysis
        if 'total_cost_analysis' in results:
            formatted['total_cost_analysis'] = {}
            for key, value in results['total_cost_analysis'].items():
                if isinstance(value, Decimal):
                    formatted['total_cost_analysis'][key] = currency_service.format_currency(value, currency)
                elif isinstance(value, dict):  # breakdown sub-dict
                    formatted['total_cost_analysis'][key] = {}
                    for sub_key, sub_value in value.items():
                        formatted['total_cost_analysis'][key][sub_key] = currency_service.format_currency(sub_value, currency)
        
        # Scenarios
        if 'scenarios' in results:
            formatted['scenarios'] = []
            for scenario in results['scenarios']:
                formatted_scenario = scenario.copy()
                for key in ['affordable_price', 'monthly_payment', 'total_monthly_cost', 'total_5year_cost', 'cost_per_mile']:
                    if key in scenario:
                        formatted_scenario[f'{key}_formatted'] = currency_service.format_currency(scenario[key], currency)
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
        
        # Validate down payment
        down_payment = self.validate_number(
            inputs.get('down_payment', 0),
            'Down payment',
            min_val=0,
            max_val=100000
        )
        if down_payment is None:
            return False
        
        # Validate loan terms
        loan_term = self.validate_number(
            inputs.get('loan_term', 60),
            'Loan term',
            min_val=12,
            max_val=84
        )
        if loan_term is None:
            return False
        
        loan_rate = self.validate_number(
            inputs.get('loan_rate', 7.5),
            'Loan rate',
            min_val=0,
            max_val=25
        )
        if loan_rate is None:
            return False
        
        # Validate ownership years
        ownership_years = self.validate_number(
            inputs.get('ownership_years', 5),
            'Ownership years',
            min_val=1,
            max_val=15
        )
        if ownership_years is None:
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
        
        # Validate car age
        car_age = inputs.get('car_age', 'new')
        valid_ages = ['new', 'used_3', 'used_7', 'old']
        if car_age not in valid_ages:
            self.add_error(f"Car age must be one of: {', '.join(valid_ages)}")
        
        # Validate driver age group
        driver_age_group = inputs.get('driver_age_group', 'middle')
        valid_groups = ['young', 'middle', 'senior']
        if driver_age_group not in valid_groups:
            self.add_error(f"Driver age group must be one of: {', '.join(valid_groups)}")
        
        # Validate country
        country = inputs.get('country', 'US')
        if country not in self.REGIONAL_DEFAULTS:
            self.add_error(f"Unsupported country: {country}")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """Return SEO meta data."""
        return {
            'title': 'Car Affordability Calculator 2024 - How Much Car Can I Afford? | Total Cost of Ownership',
            'description': 'Free car affordability calculator with total cost of ownership analysis. Calculate maximum car price based on income including insurance, fuel, maintenance, and depreciation.',
            'keywords': 'car affordability calculator, auto affordability calculator, car payment calculator, total cost of ownership, car budget calculator, vehicle affordability',
            'canonical': '/calculators/caraffordability/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Return schema.org markup."""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Car Affordability Calculator",
            "description": "Calculate maximum affordable car price with comprehensive total cost of ownership analysis",
            "url": "https://yourcalcsite.com/calculators/caraffordability/",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Total cost of ownership analysis",
                "Multi-country support (US, UK, Canada, Australia)",
                "Insurance cost estimation by age group",
                "Fuel cost calculation",
                "Maintenance cost projection",
                "Depreciation analysis",
                "Monthly budget breakdown",
                "Alternative scenarios comparison",
                "Cost per mile calculation"
            ]
        }