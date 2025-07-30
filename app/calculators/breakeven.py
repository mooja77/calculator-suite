from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any
from app.calculators.base import BaseCalculator
from app.calculators.registry import register_calculator

@register_calculator
class BreakevenCalculator(BaseCalculator):
    """
    Break-Even Calculator for Business Viability Analysis
    
    Helps entrepreneurs determine how many units they need to sell
    to cover all costs and start making profit.
    """
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate break-even point and related business metrics"""
        if not self.validate_inputs(inputs):
            return {"errors": self.errors}
        
        try:
            # Convert inputs to Decimal for precise calculations
            fixed_costs = Decimal(str(inputs['fixed_costs']))
            price_per_unit = Decimal(str(inputs['price_per_unit']))
            variable_cost_per_unit = Decimal(str(inputs['variable_cost_per_unit']))
            
            # Optional target profit
            target_profit = Decimal(str(inputs.get('target_profit', 0)))
            
            # Calculate contribution margin per unit
            contribution_margin = price_per_unit - variable_cost_per_unit
            
            # Calculate break-even point in units
            breakeven_units = (fixed_costs + target_profit) / contribution_margin
            
            # Calculate break-even point in revenue
            breakeven_revenue = breakeven_units * price_per_unit
            
            # Calculate contribution margin ratio
            contribution_margin_ratio = (contribution_margin / price_per_unit) * 100
            
            # Safety margin calculations
            current_sales = Decimal(str(inputs.get('current_sales', 0)))
            safety_margin_units = max(0, current_sales - breakeven_units)
            safety_margin_percentage = 0
            if current_sales > 0:
                safety_margin_percentage = (safety_margin_units / current_sales) * 100
            
            # Profit at current sales level
            current_profit = (current_sales * contribution_margin) - fixed_costs
            
            # Calculate what happens with different sales scenarios
            scenarios = {}
            for multiplier, label in [(0.5, "50% of break-even"), (0.75, "75% of break-even"), 
                                    (1.25, "25% above break-even"), (1.5, "50% above break-even"), 
                                    (2.0, "Double break-even")]:
                scenario_units = breakeven_units * Decimal(str(multiplier))
                scenario_revenue = scenario_units * price_per_unit
                scenario_profit = (scenario_units * contribution_margin) - fixed_costs
                scenarios[label] = {
                    'units': float(scenario_units.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'revenue': float(scenario_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'profit': float(scenario_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                }
            
            # Business health indicators
            health_indicators = []
            if contribution_margin_ratio >= 40:
                health_indicators.append("✅ Strong contribution margin (≥40%)")
            elif contribution_margin_ratio >= 20:
                health_indicators.append("⚠️ Moderate contribution margin (20-39%)")
            else:
                health_indicators.append("🚨 Low contribution margin (<20%) - Consider pricing strategy")
            
            if safety_margin_percentage >= 20:
                health_indicators.append("✅ Healthy safety margin (≥20%)")
            elif safety_margin_percentage >= 10:
                health_indicators.append("⚠️ Moderate safety margin (10-19%)")
            elif current_sales > 0:
                health_indicators.append("🚨 Low safety margin (<10%) - High business risk")
            
            # Recommendations
            recommendations = []
            if contribution_margin_ratio < 30:
                recommendations.append("Consider increasing prices or reducing variable costs")
            if breakeven_units > 10000:
                recommendations.append("High break-even point - verify market size and demand")
            if current_sales > 0 and current_sales < breakeven_units:
                units_needed = breakeven_units - current_sales
                recommendations.append(f"Need to sell {float(units_needed.quantize(Decimal('0.01')))} more units to break even")
            
            return {
                "breakeven_units": float(breakeven_units.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "breakeven_revenue": float(breakeven_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "contribution_margin": float(contribution_margin.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "contribution_margin_ratio": float(contribution_margin_ratio.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "safety_margin_units": float(safety_margin_units.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "safety_margin_percentage": float(safety_margin_percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "current_profit": float(current_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                "scenarios": scenarios,
                "health_indicators": health_indicators,
                "recommendations": recommendations,
                "currency": inputs.get('currency', 'USD')
            }
            
        except Exception as e:
            self.add_error(f"Calculation error: {str(e)}")
            return {"errors": self.errors}
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate break-even calculator inputs"""
        self.clear_errors()
        
        # Required fields
        required_fields = ['fixed_costs', 'price_per_unit', 'variable_cost_per_unit']
        for field in required_fields:
            if field not in inputs or inputs[field] == '':
                self.add_error(f"{field.replace('_', ' ').title()} is required")
        
        if self.errors:
            return False
        
        # Validate numeric inputs
        fixed_costs = self.validate_number(inputs['fixed_costs'], 'Fixed costs', min_val=0)
        price_per_unit = self.validate_number(inputs['price_per_unit'], 'Price per unit', min_val=0.01)
        variable_cost_per_unit = self.validate_number(inputs['variable_cost_per_unit'], 'Variable cost per unit', min_val=0)
        
        # Optional fields
        if 'current_sales' in inputs and inputs['current_sales'] != '':
            self.validate_number(inputs['current_sales'], 'Current sales', min_val=0)
        
        if 'target_profit' in inputs and inputs['target_profit'] != '':
            self.validate_number(inputs['target_profit'], 'Target profit', min_val=0)
        
        # Business logic validation
        if price_per_unit is not None and variable_cost_per_unit is not None:
            if variable_cost_per_unit >= price_per_unit:
                self.add_error("Variable cost per unit must be less than price per unit")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        """SEO meta data for break-even calculator"""
        return {
            "title": "Break-Even Calculator - Business Viability Analysis | Calculator Suite",
            "description": "Calculate your business break-even point. Determine how many units to sell to cover costs and start making profit. Free break-even analysis tool.",
            "keywords": "break-even calculator, business calculator, break even analysis, contribution margin, fixed costs, variable costs, business planning, startup calculator",
            "canonical_url": "/calculators/breakeven"
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        """Schema.org markup for break-even calculator"""
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Break-Even Calculator",
            "description": "Calculate your business break-even point and analyze profitability scenarios",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Any",
            "permissions": "browser",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            }
        }