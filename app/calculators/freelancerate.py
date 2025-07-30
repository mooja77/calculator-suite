from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class FreelancerateCalculator(BaseCalculator):
    """
    Freelance Rate Calculator for Hourly Rate Determination
    
    Helps freelancers and contractors calculate what they should charge per hour
    to achieve their desired annual income after accounting for all business expenses.
    """
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal freelance hourly rate"""
        if not self.validate_inputs(inputs):
            return {"errors": self.errors}
        
        try:
            # Convert inputs to Decimal for precise calculations
            desired_salary = Decimal(str(inputs['desired_salary']))
            billable_hours_per_week = Decimal(str(inputs['billable_hours_per_week']))
            weeks_per_year = Decimal(str(inputs.get('weeks_per_year', 50)))  # Account for vacation/sick time
            
            # Business expenses
            business_expenses = Decimal(str(inputs.get('business_expenses', 0)))
            health_insurance = Decimal(str(inputs.get('health_insurance', 0)))
            retirement_contribution = Decimal(str(inputs.get('retirement_contribution', 0)))
            
            # Tax considerations
            tax_rate = Decimal(str(inputs.get('tax_rate', 30))) / 100  # Default 30% for self-employment
            
            # Calculate total annual billable hours
            total_billable_hours = billable_hours_per_week * weeks_per_year
            
            # Calculate total annual income needed (before taxes)
            total_expenses = business_expenses + health_insurance + retirement_contribution
            gross_income_needed = (desired_salary + total_expenses) / (1 - tax_rate)
            
            # Calculate base hourly rate
            base_hourly_rate = gross_income_needed / total_billable_hours
            
            # Add profit margin
            profit_margin = Decimal(str(inputs.get('profit_margin', 20))) / 100  # Default 20%
            recommended_rate = base_hourly_rate * (1 + profit_margin)
            
            # Calculate different rate scenarios
            rate_scenarios = {}
            for multiplier, label in [(0.8, "Conservative Rate (-20%)"), (1.0, "Calculated Rate"), 
                                    (1.2, "Premium Rate (+20%)"), (1.5, "High-End Rate (+50%)")]:
                scenario_rate = recommended_rate * Decimal(str(multiplier))
                annual_revenue = scenario_rate * total_billable_hours
                net_income = annual_revenue * (1 - tax_rate) - total_expenses
                
                rate_scenarios[label] = {
                    'hourly_rate': float(scenario_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'annual_revenue': float(annual_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'net_income': float(net_income.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'difference_from_target': float((net_income - desired_salary).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                }
            
            # Calculate effective employee equivalent
            # What salary would this be equivalent to as an employee?
            employee_equivalent = gross_income_needed * Decimal('0.75')  # Assuming employer covers benefits
            
            # Monthly and weekly revenue projections
            monthly_revenue = (recommended_rate * total_billable_hours) / 12
            weekly_revenue = recommended_rate * billable_hours_per_week
            
            # Break down the rate components
            rate_breakdown = {
                'base_salary_component': float((desired_salary / total_billable_hours).quantize(Decimal('0.01'))),
                'tax_component': float(((gross_income_needed - desired_salary - total_expenses) / total_billable_hours).quantize(Decimal('0.01'))),
                'expenses_component': float((total_expenses / total_billable_hours).quantize(Decimal('0.01'))),
                'profit_component': float((base_hourly_rate * profit_margin).quantize(Decimal('0.01')))
            }
            
            # Industry benchmarks and recommendations
            recommendations = []
            if recommended_rate < 25:
                recommendations.append("⚠️ Rate below industry minimum - consider raising your target")
            elif recommended_rate < 50:
                recommendations.append("💡 Entry-level freelance rate range")
            elif recommended_rate < 100:
                recommendations.append("✅ Mid-level professional rate range")
            elif recommended_rate < 200:
                recommendations.append("🎯 Senior professional/specialist rate range")
            else:
                recommendations.append("🌟 Expert/executive consultant rate range")
            
            if billable_hours_per_week > 35:
                recommendations.append("⚠️ High billable hours - ensure work-life balance")
            
            if tax_rate < Decimal('0.25'):
                recommendations.append("💡 Consider increasing tax reserve - freelancers typically pay 25-35%")
            
            # Payment structure suggestions
            payment_structures = {
                'hourly': {
                    'rate': float(recommended_rate.quantize(Decimal('0.01'))),
                    'description': 'Standard hourly billing'
                },
                'daily': {
                    'rate': float((recommended_rate * 8).quantize(Decimal('0.01'))),
                    'description': 'Day rate (8 hours)'
                },
                'weekly': {
                    'rate': float(weekly_revenue.quantize(Decimal('0.01'))),
                    'description': f'Weekly rate ({billable_hours_per_week} hours)'
                },
                'project_multiplier': {
                    'rate': float((recommended_rate * Decimal('1.15')).quantize(Decimal('0.01'))),
                    'description': 'Project rate (+15% for fixed scope risk)'
                }
            }
            
            return {
                "recommended_rate": float(recommended_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "base_hourly_rate": float(base_hourly_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "annual_revenue": float((recommended_rate * total_billable_hours).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "monthly_revenue": float(monthly_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "weekly_revenue": float(weekly_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "employee_equivalent": float(employee_equivalent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "total_billable_hours": float(total_billable_hours),
                "rate_breakdown": rate_breakdown,
                "rate_scenarios": rate_scenarios,
                "payment_structures": payment_structures,
                "recommendations": recommendations,
                "currency": inputs.get('currency', 'USD')
            }
            
        except Exception as e:
            self.add_error(f"Calculation error: {str(e)}")
            return {"errors": self.errors}
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate freelance rate calculator inputs"""
        self.clear_errors()
        
        # Required fields
        required_fields = ['desired_salary', 'billable_hours_per_week']
        for field in required_fields:
            if field not in inputs or inputs[field] == '':
                self.add_error(f"{field.replace('_', ' ').title()} is required")
        
        if self.errors:
            return False
        
        # Validate numeric inputs
        desired_salary = self.validate_number(inputs['desired_salary'], 'Desired salary', min_val=1000, max_val=1000000)
        billable_hours_per_week = self.validate_number(inputs['billable_hours_per_week'], 'Billable hours per week', min_val=1, max_val=60)
        
        # Optional fields with defaults
        if 'weeks_per_year' in inputs and inputs['weeks_per_year'] != '':
            self.validate_number(inputs['weeks_per_year'], 'Weeks per year', min_val=20, max_val=52)
        
        if 'business_expenses' in inputs and inputs['business_expenses'] != '':
            self.validate_number(inputs['business_expenses'], 'Business expenses', min_val=0, max_val=100000)
        
        if 'health_insurance' in inputs and inputs['health_insurance'] != '':
            self.validate_number(inputs['health_insurance'], 'Health insurance', min_val=0, max_val=50000)
        
        if 'retirement_contribution' in inputs and inputs['retirement_contribution'] != '':
            self.validate_number(inputs['retirement_contribution'], 'Retirement contribution', min_val=0, max_val=100000)
        
        if 'tax_rate' in inputs and inputs['tax_rate'] != '':
            self.validate_number(inputs['tax_rate'], 'Tax rate', min_val=0, max_val=50)
        
        if 'profit_margin' in inputs and inputs['profit_margin'] != '':
            self.validate_number(inputs['profit_margin'], 'Profit margin', min_val=0, max_val=100)
        
        # Business logic validation
        if billable_hours_per_week is not None and billable_hours_per_week > 40:
            self.add_error("⚠️ Warning: Over 40 billable hours per week may lead to burnout")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """SEO meta data for freelance rate calculator"""
        return {
            "title": "Freelance Rate Calculator - Hourly Rate Determination | Calculator Suite",
            "description": "Calculate your optimal freelance hourly rate. Factor in expenses, taxes, and desired income to set profitable freelance rates. Free rate calculator.",
            "keywords": "freelance rate calculator, hourly rate calculator, freelancer pricing, contractor rates, freelance income, business rate calculator, self-employed rate",
            "canonical_url": "/calculators/freelancerate"
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Schema.org markup for freelance rate calculator"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Freelance Rate Calculator",
            "description": "Calculate optimal hourly rates for freelancers and contractors",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Any",
            "permissions": "browser",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            }
        }