# Calculator Suite Developer Guide

Complete guide for developers integrating with or extending the Calculator Suite.

## Quick Start

### 1. Setup Development Environment
```bash
# Clone and setup
git clone <repository>
cd calculator-app

# Install dependencies
pip install -r requirements.txt

# Run development server
python app_simple_fixed.py
```

### 2. API Integration
```python
# Basic API usage
import requests

response = requests.post('http://localhost:5000/api/calculate/loan', json={
    'loan_amount': '250000',
    'annual_rate': '6.5', 
    'loan_term_years': '30'
})
result = response.json()
print(f"Monthly payment: ${result['monthly_payment']}")
```

### 3. Using the Python SDK
```python
from api_examples import CalculatorAPI

api = CalculatorAPI()
result = api.calculate_loan(250000, 6.5, 30)
print(f"Monthly payment: ${result['monthly_payment']:,.2f}")
```

---

## Architecture Overview

### Application Structure
```
calculator-app/
├── app_simple_fixed.py     # Main application (single file)
├── app/                    # Modular version (future)
├── tests/                  # Comprehensive test suite
├── API_DOCUMENTATION.md    # Complete API reference
└── docs/                   # Project documentation
```

### Core Components

#### 1. Calculator Classes
All calculators inherit from `BaseCalculator`:
```python
class BaseCalculator:
    def calculate(self, inputs):     # Main calculation logic
    def validate_inputs(self, inputs): # Input validation 
    def get_meta_data(self):         # SEO metadata
```

#### 2. Calculator Registry
Automatic registration system:
```python
@register_calculator
class MyCalculator(BaseCalculator):
    # Implementation
```

#### 3. API Endpoints
RESTful endpoints following pattern:
- Route: `/api/calculate/{calculator-slug}`
- Method: `POST`
- Content-Type: `application/json`

#### 4. Web Interface
Server-side rendered HTML with:
- Responsive design
- Real-time validation
- AJAX form submission
- SEO optimization

---

## Adding New Calculators

### Step 1: Create Calculator Class
```python
@register_calculator
class MyNewCalculator(BaseCalculator):
    def calculate(self, inputs):
        # Validate required inputs
        value1 = float(inputs['value1'])
        value2 = float(inputs['value2'])
        
        # Perform calculation
        result = value1 * value2
        
        # Return structured result
        return {
            'result': result,
            'value1': value1,
            'value2': value2,
            'inputs': inputs
        }
    
    def validate_inputs(self, inputs):
        self.clear_errors()
        
        # Validate required fields
        if 'value1' not in inputs:
            self.add_error("Value 1 is required")
        if 'value2' not in inputs:
            self.add_error("Value 2 is required")
        
        # Validate number formats
        self.validate_number(inputs.get('value1', ''), 'Value 1', min_val=0)
        self.validate_number(inputs.get('value2', ''), 'Value 2', min_val=0)
        
        return len(self.errors) == 0
    
    def get_meta_data(self):
        return {
            'title': 'My New Calculator - Free Online Tool',
            'description': 'Calculate something useful with our free online calculator.',
            'keywords': 'calculator, my, new, calculation',
            'canonical': '/calculators/mynew/'
        }
```

### Step 2: Add Web Route
```python
@app.route('/calculators/mynew/')
def mynew_calculator():
    return render_calculator_template('mynew', {
        'title': 'My New Calculator',
        'description': 'Calculate something useful',
        'fields': [
            {'name': 'value1', 'label': 'First Value', 'type': 'number'},
            {'name': 'value2', 'label': 'Second Value', 'type': 'number'}
        ]
    })
```

### Step 3: Add API Endpoint
```python
@app.route('/api/calculate/mynew', methods=['POST'])
def calculate_mynew():
    try:
        calc = MyNewCalculator()
        inputs = request.get_json()
        
        if not calc.validate_inputs(inputs):
            return jsonify({'errors': calc.errors}), 400
        
        result = calc.calculate(inputs)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Step 4: Update Homepage
Add link to homepage calculator list:
```html
<a href="/calculators/mynew/" class="calc-item">
    <h3>🔢 My New Calculator</h3>
    <p>Calculate something useful with precision.</p>
</a>
```

---

## Testing Your Calculator

### Unit Tests
```python
def test_mynew_calculator():
    calc = MyNewCalculator()
    inputs = {'value1': '10', 'value2': '5'}
    
    assert calc.validate_inputs(inputs) == True
    result = calc.calculate(inputs)
    assert result['result'] == 50
```

### API Tests
```python
def test_mynew_api(client):
    response = client.post('/api/calculate/mynew', 
                          json={'value1': '10', 'value2': '5'})
    assert response.status_code == 200
    data = response.json()
    assert data['result'] == 50
```

### Edge Case Tests
```python
def test_mynew_edge_cases():
    calc = MyNewCalculator()
    
    # Test zero values
    inputs = {'value1': '0', 'value2': '5'}
    result = calc.calculate(inputs)
    assert result['result'] == 0
    
    # Test validation errors
    inputs = {'value1': 'invalid'}
    assert calc.validate_inputs(inputs) == False
    assert len(calc.errors) > 0
```

---

## Best Practices

### Input Validation
```python
# Always validate all inputs
def validate_inputs(self, inputs):
    self.clear_errors()
    
    # Check required fields
    required_fields = ['field1', 'field2']
    for field in required_fields:
        if field not in inputs or inputs[field] == '':
            self.add_error(f"{field} is required")
    
    # Validate numeric fields with constraints
    self.validate_number(inputs.get('amount'), 'Amount', min_val=0, max_val=1000000)
    self.validate_number(inputs.get('rate'), 'Rate', min_val=0, max_val=100)
    
    return len(self.errors) == 0
```

### Error Handling
```python
def calculate(self, inputs):
    try:
        # Perform calculations with error handling
        result = complex_calculation(inputs)
        return {'result': result, 'inputs': inputs}
    
    except ZeroDivisionError:
        raise ValueError("Division by zero not allowed")
    except ValueError as e:
        raise ValueError(f"Invalid input: {e}")
    except Exception as e:
        raise ValueError(f"Calculation error: {e}")
```

### Performance Optimization
```python
# Cache expensive calculations
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_calculation(value1, value2):
    # Complex calculation
    return result

# Use appropriate data types
def calculate(self, inputs):
    # Use Decimal for financial calculations
    from decimal import Decimal
    amount = Decimal(inputs['amount'])
    rate = Decimal(inputs['rate'])
    result = amount * rate
    return {'result': float(result)}
```

### SEO Optimization
```python
def get_meta_data(self):
    return {
        'title': 'Specific Calculator Name - Free Online Tool',
        'description': 'Under 160 characters describing calculator benefits.',
        'keywords': 'primary,keyword,calculator,specific,terms',
        'canonical': '/calculators/calculator-slug/',
        'schema_type': 'WebApplication',  # Schema.org markup
        'category': 'Financial'  # Calculator category
    }
```

---

## API Integration Patterns

### Basic Request/Response
```python
import requests

def call_calculator_api(calculator, data):
    url = f"http://localhost:5000/api/calculate/{calculator}"
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        errors = response.json().get('errors', [])
        raise ValueError(f"Validation errors: {errors}")
    else:
        raise Exception(f"API error: {response.status_code}")
```

### Batch Processing
```python
def process_multiple_calculations(calculations):
    results = []
    for calc_type, data in calculations:
        try:
            result = call_calculator_api(calc_type, data)
            results.append({'success': True, 'data': result})
        except Exception as e:
            results.append({'success': False, 'error': str(e)})
    return results
```

### Async Processing
```python
import asyncio
import aiohttp

async def async_calculate(session, calculator, data):
    url = f"http://localhost:5000/api/calculate/{calculator}"
    async with session.post(url, json=data) as response:
        return await response.json()

async def batch_calculate(calculations):
    async with aiohttp.ClientSession() as session:
        tasks = [async_calculate(session, calc, data) 
                for calc, data in calculations]
        return await asyncio.gather(*tasks)
```

---

## Deployment Guide

### Production Checklist
- [ ] Set `debug=False` in Flask app
- [ ] Configure proper secret key
- [ ] Set up proper logging
- [ ] Add rate limiting
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Database for calculation logs (optional)

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://...  # If using database
export REDIS_URL=redis://...          # If using Redis cache
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app_simple_fixed:app", "--bind", "0.0.0.0:5000"]
```

---

## Monitoring and Analytics

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log performance metrics
        print(f"{func.__name__} executed in {execution_time:.3f}s")
        return result
    return wrapper

@monitor_performance
def calculate(self, inputs):
    # Calculator logic
    pass
```

### Usage Analytics
```python
def log_calculation(calculator_type, inputs, result):
    # Log to database, file, or analytics service
    log_entry = {
        'timestamp': datetime.now(),
        'calculator': calculator_type,
        'inputs': inputs,
        'result': result,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    }
    # Store log_entry
```

---

## Troubleshooting

### Common Issues

#### Validation Errors
```python
# Issue: Numbers not validating
# Solution: Ensure string conversion
value = str(inputs.get('field', ''))
validated = self.validate_number(value, 'Field Name')
```

#### JSON Serialization
```python
# Issue: Decimal/complex types in JSON
# Solution: Convert to basic types
result = {
    'amount': float(decimal_amount),
    'date': date_obj.isoformat(),
    'values': [float(x) for x in decimal_list]
}
```

#### Performance Issues
```python
# Issue: Slow calculations
# Solutions:
1. Add caching for repeated calculations
2. Optimize algorithms
3. Use appropriate data structures
4. Consider background processing for complex calculations
```

### Debug Mode
```python
# Enable detailed error messages
app.config['DEBUG'] = True

# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints where helpful
- Add docstrings for all public methods
- Keep functions focused and small

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

### Testing Requirements
- All new calculators must have unit tests
- Edge cases must be tested
- API endpoints must be tested
- Performance tests for complex calculations

---

## Resources

- **API Documentation**: `API_DOCUMENTATION.md`
- **Test Suite**: `tests/` directory
- **Example Code**: `api_examples.py`
- **Performance Tests**: `tests/test_performance.py`

## Support

For development questions:
1. Check this developer guide
2. Review existing calculator implementations
3. Run the test suite to understand expected behavior
4. Use the API examples for integration patterns