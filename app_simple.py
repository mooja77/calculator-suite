#!/usr/bin/env python3
"""
Simplified Calculator Suite without database dependencies
Perfect for getting started and testing the core functionality
"""

from flask import Flask, render_template, request, jsonify, Response
import os
import json
import time
from datetime import datetime

# Simple in-memory storage for this demo
calculation_logs = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# Calculator Registry
calculators = {}

def register_calculator(calc_class):
    """Register a calculator"""
    instance = calc_class()
    calculators[instance.slug] = calc_class
    return calc_class

# Base Calculator Class
class BaseCalculator:
    def __init__(self):
        self.slug = self.__class__.__name__.lower().replace('calculator', '')
        self.errors = []
    
    def clear_errors(self):
        self.errors = []
    
    def add_error(self, message):
        self.errors.append(message)
    
    def validate_number(self, value, field_name, min_val=None, max_val=None):
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                self.add_error(f"{field_name} must be at least {min_val}")
                return None
            if max_val is not None and num > max_val:
                self.add_error(f"{field_name} must be at most {max_val}")
                return None
            return num
        except (ValueError, TypeError):
            self.add_error(f"{field_name} must be a valid number")
            return None

# Percentage Calculator
@register_calculator
class PercentageCalculator(BaseCalculator):
    def calculate(self, inputs):
        operation = inputs.get('operation', 'basic')
        
        if operation == 'basic':
            x = float(inputs['x'])
            y = float(inputs['y'])
            if y == 0:
                raise ValueError("Cannot divide by zero")
            result = (x / y) * 100
            
        elif operation == 'find_value':
            percent = float(inputs['percent'])
            total = float(inputs['total'])
            result = (percent / 100) * total
            
        elif operation == 'increase':
            original = float(inputs['original'])
            percent = float(inputs['percent'])
            result = original * (1 + percent / 100)
            
        elif operation == 'decrease':
            original = float(inputs['original'])
            percent = float(inputs['percent'])
            result = original * (1 - percent / 100)
            
        elif operation == 'difference':
            x = float(inputs['x'])
            y = float(inputs['y'])
            if x == 0 and y == 0:
                result = 0
            else:
                result = abs(x - y) / ((x + y) / 2) * 100
                
        elif operation == 'change':
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
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        operation = inputs.get('operation', 'basic')
        required = self._get_required_fields(operation)
        
        for field in required:
            if field not in inputs or inputs[field] == '':
                self.add_error(f"Missing required field: {field}")
                continue
            
            value = self.validate_number(inputs[field], field)
            if value is None:
                continue
            
            if operation in ['basic', 'difference'] and field == 'y' and value == 0:
                self.add_error("Division by zero: Y cannot be zero")
            elif operation == 'change' and field == 'original' and value == 0:
                self.add_error("Original value cannot be zero for percentage change")
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'Percentage Calculator - Calculate Percentages Online Free',
            'description': 'Free online percentage calculator. Calculate percentages, percentage increase/decrease, percentage difference and more. Simple, fast, and accurate.',
            'keywords': 'percentage calculator, percent calculator, calculate percentage, percentage increase, percentage decrease, percentage difference, percentage change',
            'canonical': '/calculators/percentage/'
        }
    
    def _get_required_fields(self, operation):
        fields_map = {
            'basic': ['x', 'y'],
            'find_value': ['percent', 'total'],
            'increase': ['original', 'percent'],
            'decrease': ['original', 'percent'],
            'difference': ['x', 'y'],
            'change': ['original', 'new_value']
        }
        return fields_map.get(operation, [])
    
    def _get_formula(self, operation):
        formulas = {
            'basic': '(X ÷ Y) × 100',
            'find_value': '(Percent ÷ 100) × Total',
            'increase': 'Original × (1 + Percent ÷ 100)',
            'decrease': 'Original × (1 - Percent ÷ 100)',
            'difference': '|X - Y| ÷ ((X + Y) ÷ 2) × 100',
            'change': '((New Value - Original) ÷ Original) × 100'
        }
        return formulas.get(operation, '')
    
    def _get_explanation(self, operation, inputs, result):
        explanations = {
            'basic': f"{inputs['x']} is {result}% of {inputs['y']}",
            'find_value': f"{inputs['percent']}% of {inputs['total']} is {result}",
            'increase': f"{inputs['original']} increased by {inputs['percent']}% is {result}",
            'decrease': f"{inputs['original']} decreased by {inputs['percent']}% is {result}",
            'difference': f"The percentage difference between {inputs['x']} and {inputs['y']} is {result}%",
            'change': f"The percentage change from {inputs['original']} to {inputs['new_value']} is {result}%"
        }
        return explanations.get(operation, '')

# Routes
@app.route('/')
def index():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Calculator Suite</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #007bff; text-align: center; }}
            .calc-list {{ display: grid; gap: 1rem; margin-top: 2rem; }}
            .calc-item {{ padding: 1rem; border: 1px solid #ddd; border-radius: 4px; text-decoration: none; color: inherit; }}
            .calc-item:hover {{ background: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧮 Calculator Suite</h1>
            <p>Free online calculators for all your math needs.</p>
            
            <div class="calc-list">
                <a href="/calculators/percentage/" class="calc-item">
                    <h3>📊 Percentage Calculator</h3>
                    <p>Calculate percentages, increases, decreases, and more.</p>
                </a>
            </div>
            
            <div style="margin-top: 2rem; text-align: center; color: #666;">
                <p>More calculators coming soon! Built with Flask and ❤️</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/calculators/percentage/')
def percentage_calculator():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Percentage Calculator - Free Online Tool</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free online percentage calculator. Calculate percentages, percentage increase/decrease, and more.">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2rem; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #007bff; text-align: center; }
            .form-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
            input, select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
            button:hover { background: #0056b3; }
            .result { background: #e8f5e8; border: 1px solid #d4edda; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 4px; margin-top: 1rem; }
            .operation-fields { margin-top: 1rem; }
            .formula { background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-top: 1rem; font-family: monospace; }
            .back-link { display: inline-block; margin-bottom: 1rem; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Calculator Suite</a>
            
            <h1>🧮 Percentage Calculator</h1>
            <p>Calculate percentages, increases, decreases, and differences with ease.</p>
            
            <form id="calculator-form">
                <div class="form-group">
                    <label for="operation">Calculation Type:</label>
                    <select id="operation" name="operation" required>
                        <option value="basic">What % is X of Y?</option>
                        <option value="find_value">What is X% of Y?</option>
                        <option value="increase">Increase by %</option>
                        <option value="decrease">Decrease by %</option>
                        <option value="difference">% Difference</option>
                        <option value="change">% Change</option>
                    </select>
                </div>
                
                <div id="basic-fields" class="operation-fields">
                    <div class="form-group">
                        <label for="x">First Number (X):</label>
                        <input type="number" id="x" name="x" step="any" required>
                    </div>
                    <div class="form-group">
                        <label for="y">Second Number (Y):</label>
                        <input type="number" id="y" name="y" step="any" required>
                    </div>
                </div>
                
                <div id="find_value-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="percent">Percentage (%):</label>
                        <input type="number" id="percent" name="percent" step="any">
                    </div>
                    <div class="form-group">
                        <label for="total">Total Amount:</label>
                        <input type="number" id="total" name="total" step="any">
                    </div>
                </div>
                
                <div id="increase-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="original">Original Value:</label>
                        <input type="number" id="original" name="original" step="any">
                    </div>
                    <div class="form-group">
                        <label for="percent_inc">Percentage Increase (%):</label>
                        <input type="number" id="percent_inc" name="percent" step="any">
                    </div>
                </div>
                
                <div id="decrease-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="original_dec">Original Value:</label>
                        <input type="number" id="original_dec" name="original" step="any">
                    </div>
                    <div class="form-group">
                        <label for="percent_dec">Percentage Decrease (%):</label>
                        <input type="number" id="percent_dec" name="percent" step="any">
                    </div>
                </div>
                
                <div id="difference-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="x_diff">First Value:</label>
                        <input type="number" id="x_diff" name="x" step="any">
                    </div>
                    <div class="form-group">
                        <label for="y_diff">Second Value:</label>
                        <input type="number" id="y_diff" name="y" step="any">
                    </div>
                </div>
                
                <div id="change-fields" class="operation-fields" style="display: none;">
                    <div class="form-group">
                        <label for="original_change">Original Value:</label>
                        <input type="number" id="original_change" name="original" step="any">
                    </div>
                    <div class="form-group">
                        <label for="new_value">New Value:</label>
                        <input type="number" id="new_value" name="new_value" step="any">
                    </div>
                </div>
                
                <button type="submit">Calculate</button>
            </form>
            
            <div id="result-container" style="display: none;"></div>
            <div id="error-container" style="display: none;"></div>
        </div>
        
        <script>
            const operationSelect = document.getElementById('operation');
            const form = document.getElementById('calculator-form');
            
            operationSelect.addEventListener('change', function() {
                document.querySelectorAll('.operation-fields').forEach(field => {
                    field.style.display = 'none';
                    field.querySelectorAll('input').forEach(input => input.removeAttribute('required'));
                });
                
                const selectedFields = document.getElementById(this.value + '-fields');
                if (selectedFields) {
                    selectedFields.style.display = 'block';
                    selectedFields.querySelectorAll('input').forEach(input => input.setAttribute('required', 'required'));
                }
            });
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(form);
                const data = {};
                
                for (let [key, value] of formData.entries()) {
                    if (value !== '') data[key] = value;
                }
                
                fetch('/api/calculate/percentage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    const resultContainer = document.getElementById('result-container');
                    const errorContainer = document.getElementById('error-container');
                    
                    if (result.error || result.errors) {
                        const errors = result.errors || [result.error];
                        errorContainer.innerHTML = '<div class="error">' + errors.join('<br>') + '</div>';
                        errorContainer.style.display = 'block';
                        resultContainer.style.display = 'none';
                    } else {
                        let resultHtml = '<div class="result">';
                        resultHtml += '<h3>Result: ' + result.result + '</h3>';
                        resultHtml += '<p>' + result.explanation + '</p>';
                        if (result.formula) {
                            resultHtml += '<div class="formula"><strong>Formula:</strong> ' + result.formula + '</div>';
                        }
                        resultHtml += '</div>';
                        
                        resultContainer.innerHTML = resultHtml;
                        resultContainer.style.display = 'block';
                        errorContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('error-container');
                    errorContainer.innerHTML = '<div class="error">An error occurred. Please try again.</div>';
                    errorContainer.style.display = 'block';
                    document.getElementById('result-container').style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/calculate/percentage', methods=['POST'])
def calculate_percentage():
    try:
        calc = PercentageCalculator()
        inputs = request.get_json()
        
        if not calc.validate_inputs(inputs):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(inputs)
        
        # Log calculation (in-memory for demo)
        calculation_logs.append({
            'calculator': 'percentage',
            'inputs': inputs,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Calculator Suite...")
    print("📊 Available at: http://localhost:5000")
    print("🧮 Percentage Calculator: http://localhost:5000/calculators/percentage/")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=True)