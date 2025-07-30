from .base import BaseCalculator
from .registry import register_calculator
from typing import Dict, Any, List
from app.cache import cache_calculation

@register_calculator
class PercentageCalculator(BaseCalculator):
    """Calculate various percentage operations"""
    
    @cache_calculation(timeout=3600)
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        operation = inputs.get('operation', 'basic')
        
        if operation == 'basic':
            # X is what % of Y?
            x = float(inputs['x'])
            y = float(inputs['y'])
            if y == 0:
                raise ValueError("Cannot divide by zero")
            result = (x / y) * 100
            
        elif operation == 'find_value':
            # What is X% of Y?
            percent = float(inputs['percent'])
            total = float(inputs['total'])
            result = (percent / 100) * total
            
        elif operation == 'increase':
            # X increased by Y%
            original = float(inputs['original'])
            percent = float(inputs['percent'])
            result = original * (1 + percent / 100)
            
        elif operation == 'decrease':
            # X decreased by Y%
            original = float(inputs['original'])
            percent = float(inputs['percent'])
            result = original * (1 - percent / 100)
            
        elif operation == 'difference':
            # Percentage difference between X and Y
            x = float(inputs['x'])
            y = float(inputs['y'])
            if x == 0 and y == 0:
                result = 0
            else:
                result = abs(x - y) / ((x + y) / 2) * 100
                
        elif operation == 'change':
            # Percentage change from X to Y
            original = float(inputs['original'])
            new_value = float(inputs['new_value'])
            if original == 0:
                raise ValueError("Cannot calculate percentage change from zero")
            result = ((new_value - original) / original) * 100
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {
            'result': round(result, 2),
            'operation': operation,
            'inputs': inputs,
            'formula': self._get_formula(operation),
            'explanation': self._get_explanation(operation, inputs, result)
        }
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        self.clear_errors()
        
        operation = inputs.get('operation', 'basic')
        required = self._get_required_fields(operation)
        
        for field in required:
            if field not in inputs or inputs[field] == '':
                self.add_error(f"Missing required field: {field}")
                continue
            
            # Validate as number
            value = self.validate_number(inputs[field], field)
            if value is None:
                continue
            
            # Operation-specific validations
            if operation in ['basic', 'difference'] and field == 'y' and value == 0:
                self.add_error("Division by zero: Y cannot be zero")
            elif operation == 'change' and field == 'original' and value == 0:
                self.add_error("Original value cannot be zero for percentage change")
        
        return len(self.errors) == 0
    
    def get_meta_data(self) -> Dict[str, str]:
        return {
            'title': 'Percentage Calculator - Calculate Percentages Online Free',
            'description': 'Free online percentage calculator. Calculate percentages, percentage increase/decrease, percentage difference and more. Simple, fast, and accurate.',
            'keywords': 'percentage calculator, percent calculator, calculate percentage, percentage increase, percentage decrease, percentage difference, percentage change',
            'canonical': '/calculators/percentage/'
        }
    
    def get_schema_markup(self) -> Dict[str, Any]:
        return {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": "Percentage Calculator",
            "description": "Calculate percentages, percentage increase, decrease, and differences online",
            "url": "https://yourcalcsite.com/calculators/percentage/",
            "applicationCategory": "UtilityApplication",
            "operatingSystem": "Any",
            "browserRequirements": "Requires JavaScript",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "featureList": [
                "Basic percentage calculation",
                "Percentage increase and decrease",
                "Percentage difference",
                "Percentage change",
                "Find percentage value"
            ]
        }
    
    def _get_required_fields(self, operation: str) -> List[str]:
        fields_map = {
            'basic': ['x', 'y'],
            'find_value': ['percent', 'total'],
            'increase': ['original', 'percent'],
            'decrease': ['original', 'percent'],
            'difference': ['x', 'y'],
            'change': ['original', 'new_value']
        }
        return fields_map.get(operation, [])
    
    def _get_formula(self, operation: str) -> str:
        formulas = {
            'basic': '(X ÷ Y) × 100',
            'find_value': '(Percent ÷ 100) × Total',
            'increase': 'Original × (1 + Percent ÷ 100)',
            'decrease': 'Original × (1 - Percent ÷ 100)',
            'difference': '|X - Y| ÷ ((X + Y) ÷ 2) × 100',
            'change': '((New Value - Original) ÷ Original) × 100'
        }
        return formulas.get(operation, '')
    
    def _get_explanation(self, operation: str, inputs: Dict[str, Any], result: float) -> str:
        explanations = {
            'basic': f"{inputs['x']} is {result}% of {inputs['y']}",
            'find_value': f"{inputs['percent']}% of {inputs['total']} is {result}",
            'increase': f"{inputs['original']} increased by {inputs['percent']}% is {result}",
            'decrease': f"{inputs['original']} decreased by {inputs['percent']}% is {result}",
            'difference': f"The percentage difference between {inputs['x']} and {inputs['y']} is {result}%",
            'change': f"The percentage change from {inputs['original']} to {inputs['new_value']} is {result}%"
        }
        return explanations.get(operation, '')