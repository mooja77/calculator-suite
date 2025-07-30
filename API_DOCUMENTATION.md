# Calculator Suite API Documentation

Complete API reference for the Calculator Suite REST API endpoints.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently no authentication required. All endpoints are publicly accessible.

## Response Format
All API responses are in JSON format with the following structure:

### Success Response
```json
{
  "result": "calculation_result",
  "inputs": {...},
  "additional_fields": "..."
}
```

### Error Response
```json
{
  "error": "Error message"
}
```

### Validation Error Response
```json
{
  "errors": ["Error message 1", "Error message 2"]
}
```

---

## 📊 Percentage Calculator
**Endpoint:** `POST /api/calculate/percentage`

### Operations
- `basic` - What % is X of Y?
- `find_value` - What is X% of Y?
- `increase` - Increase by %
- `decrease` - Decrease by %
- `difference` - % Difference
- `change` - % Change

### Request Examples

#### Basic Percentage
```json
{
  "operation": "basic",
  "x": "25",
  "y": "100"
}
```

#### Percentage Increase
```json
{
  "operation": "increase",
  "original": "100",
  "percent": "15"
}
```

### Response
```json
{
  "result": 25.0,
  "operation": "basic",
  "inputs": {...},
  "formula": "(X ÷ Y) × 100",
  "explanation": "25 is 25% of 100"
}
```

---

## 🏠 Loan Calculator
**Endpoint:** `POST /api/calculate/loan`

### Required Fields
- `loan_amount` - Principal loan amount
- `annual_rate` - Annual interest rate (percentage)
- `loan_term_years` - Loan term in years

### Optional Fields
- `loan_type` - Type of loan (mortgage, auto, personal)

### Request Example
```json
{
  "loan_amount": "250000",
  "annual_rate": "6.5",
  "loan_term_years": "30",
  "loan_type": "mortgage"
}
```

### Response
```json
{
  "loan_amount": 250000.0,
  "annual_rate": 6.5,
  "loan_term_years": 30.0,
  "monthly_payment": 1580.17,
  "total_paid": 568861.20,
  "total_interest": 318861.20,
  "loan_type": "mortgage",
  "loan_info": {...},
  "amortization_sample": [...]
}
```

---

## 📏 BMI Calculator
**Endpoint:** `POST /api/calculate/bmi`

### Metric System
```json
{
  "height": "175",
  "weight": "70",
  "unit_system": "metric",
  "age": "30",
  "gender": "male"
}
```

### Imperial System
```json
{
  "height_feet": "5",
  "height_inches": "9",
  "weight": "154",
  "unit_system": "imperial",
  "age": "25",
  "gender": "female"
}
```

### Response
```json
{
  "bmi": 22.86,
  "category": "Normal weight",
  "height_cm": 175.0,
  "weight_kg": 70.0,
  "health_info": {...}
}
```

---

## 🍽️ Tip Calculator
**Endpoint:** `POST /api/calculate/tip`

### Request Example
```json
{
  "bill_amount": "85.50",
  "tip_percentage": "18",
  "number_of_people": "4",
  "tax_amount": "7.25"
}
```

### Response
```json
{
  "bill_amount": 85.50,
  "tip_percentage": 18.0,
  "tip_amount": 15.39,
  "tax_amount": 7.25,
  "total_amount": 108.14,
  "number_of_people": 4,
  "amount_per_person": 27.04,
  "tip_per_person": 3.85
}
```

---

## 🏡 Mortgage Calculator
**Endpoint:** `POST /api/calculate/mortgage`

### Request Example
```json
{
  "home_price": "450000",
  "down_payment_percent": "20",
  "annual_rate": "7.0",
  "loan_term_years": "30",
  "property_tax_annual": "6000",
  "home_insurance_annual": "1200",
  "hoa_monthly": "150"
}
```

### Response
```json
{
  "home_price": 450000.0,
  "down_payment": 90000.0,
  "loan_amount": 360000.0,
  "monthly_principal_interest": 2395.10,
  "property_tax_monthly": 500.0,
  "insurance_monthly": 100.0,
  "pmi_monthly": 0.0,
  "hoa_monthly": 150.0,
  "total_monthly_payment": 3145.10,
  "loan_to_value": 80.0
}
```

---

## 💰 Tax Calculators

### Income Tax Calculator
**Endpoint:** `POST /api/calculate/income-tax`

```json
{
  "annual_income": "75000",
  "filing_status": "single",
  "state": "california",
  "tax_year": "2024",
  "deductions": "standard"
}
```

### Sales Tax Calculator
**Endpoint:** `POST /api/calculate/sales-tax`

```json
{
  "purchase_amount": "1500",
  "state": "texas",
  "city": "austin"
}
```

### Property Tax Calculator
**Endpoint:** `POST /api/calculate/property-tax`

```json
{
  "home_value": "400000",
  "location": "texas",
  "homestead_exemption": "40000"
}
```

### Tax Refund Calculator
**Endpoint:** `POST /api/calculate/tax-refund`

```json
{
  "annual_income": "65000",
  "federal_withholding": "9000",
  "state_withholding": "2500",
  "filing_status": "married_jointly",
  "dependents_under_17": "2",
  "dependents_other": "0"
}
```

---

## 💼 Salary Calculators

### Gross to Net Calculator
**Endpoint:** `POST /api/calculate/gross-to-net`

```json
{
  "gross_salary": "85000",
  "pay_frequency": "bi-weekly",
  "filing_status": "single",
  "state": "california",
  "retirement_contribution_percent": "6",
  "health_insurance_monthly": "250"
}
```

### Hourly to Salary Calculator
**Endpoint:** `POST /api/calculate/hourly-to-salary`

#### Hourly to Salary
```json
{
  "calculation_type": "hourly_to_salary",
  "hourly_rate": "32.50",
  "hours_per_week": "40",
  "weeks_per_year": "52",
  "overtime_hours_week": "5",
  "overtime_multiplier": "1.5"
}
```

#### Salary to Hourly
```json
{
  "calculation_type": "salary_to_hourly",
  "annual_salary": "75000",
  "hours_per_week": "40",
  "weeks_per_year": "50"
}
```

### Salary Raise Calculator
**Endpoint:** `POST /api/calculate/salary-raise`

#### Calculate by Percentage
```json
{
  "calculation_type": "raise_percentage",
  "current_salary": "68000",
  "raise_percentage": "7.5"
}
```

#### Calculate by Amount
```json
{
  "calculation_type": "raise_amount",
  "current_salary": "68000",
  "raise_amount": "5000"
}
```

#### Calculate Target Salary
```json
{
  "calculation_type": "target_salary",
  "current_salary": "68000",
  "target_salary": "75000"
}
```

### Cost of Living Calculator
**Endpoint:** `POST /api/calculate/cost-of-living`

```json
{
  "current_salary": "80000",
  "current_city": "Austin, TX",
  "target_city": "San Francisco, CA",
  "current_city_key": "austin",
  "target_city_key": "san_francisco"
}
```

---

## 📈 Investment Calculators

### Compound Interest Calculator
**Endpoint:** `POST /api/calculate/compound-interest`

```json
{
  "principal": "15000",
  "annual_rate": "8",
  "years": "20",
  "compound_frequency": "12",
  "monthly_contribution": "500"
}
```

### Retirement Calculator
**Endpoint:** `POST /api/calculate/retirement`

```json
{
  "current_age": "32",
  "retirement_age": "65",
  "current_savings": "75000",
  "monthly_contribution": "1200",
  "annual_return": "7.5",
  "retirement_income_goal": "80000",
  "inflation_rate": "2.5"
}
```

### Investment Return Calculator
**Endpoint:** `POST /api/calculate/investment-return`

#### Future Value Calculation
```json
{
  "calculation_type": "future_value",
  "initial_investment": "25000",
  "annual_return": "9",
  "years": "15",
  "additional_contributions": "800",
  "contribution_frequency": "monthly"
}
```

#### Required Return Calculation
```json
{
  "calculation_type": "required_return",
  "initial_investment": "10000",
  "target_value": "75000",
  "years": "12"
}
```

#### Time Needed Calculation
```json
{
  "calculation_type": "time_needed",
  "initial_investment": "20000",
  "target_value": "100000",
  "annual_return": "8"
}
```

#### Portfolio Analysis
```json
{
  "calculation_type": "portfolio_analysis",
  "investment_1_name": "S&P 500 Index",
  "investment_1_initial": "15000",
  "investment_1_current": "18500",
  "investment_2_name": "Bond Index",
  "investment_2_initial": "8000",
  "investment_2_current": "8400",
  "investment_3_name": "Real Estate",
  "investment_3_initial": "12000",
  "investment_3_current": "13800"
}
```

---

## Common Response Fields

### Validation Errors
All calculators validate inputs and return errors in this format:
```json
{
  "errors": [
    "Loan amount must be a valid number",
    "Annual rate must be between 0 and 50"
  ]
}
```

### Meta Data
All calculators include SEO metadata:
```json
{
  "meta": {
    "title": "Calculator Title - SEO Optimized",
    "description": "Calculator description under 160 chars",
    "keywords": "relevant, calculator, keywords",
    "canonical": "/calculators/calculator-slug/"
  }
}
```

### Input Validation Rules

#### Numeric Fields
- Must be valid numbers (integer or decimal)
- Respect min/max value constraints
- Cannot be empty for required fields

#### Percentage Fields
- Typically 0-100 range
- Some allow negative values (market returns)
- Some allow >100% (large raises, high returns)

#### Text Fields
- State codes: lowercase, full names, or abbreviations
- Filing status: specific enumerated values
- Calculation types: specific enumerated values

---

## Rate Limits
Currently no rate limiting implemented. 

## Error Codes
- `200` - Success
- `400` - Validation error (malformed input)
- `500` - Server error (calculation failure)

## CORS
CORS headers are enabled for cross-origin requests from web applications.

## SDK Examples

### JavaScript/Node.js
```javascript
const response = await fetch('/api/calculate/loan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    loan_amount: '250000',
    annual_rate: '6.5',
    loan_term_years: '30'
  })
});
const result = await response.json();
```

### Python
```python
import requests

response = requests.post('/api/calculate/retirement', json={
    'current_age': '35',
    'retirement_age': '65',
    'current_savings': '50000',
    'monthly_contribution': '1000',
    'annual_return': '7'
})
result = response.json()
```

### cURL
```bash
curl -X POST http://localhost:5000/api/calculate/percentage \
  -H "Content-Type: application/json" \
  -d '{"operation":"basic","x":"25","y":"100"}'
```

---

## Changelog
- **v1.0** - Initial API release with 18 calculators
- All endpoints stable and production-ready
- Comprehensive input validation
- Detailed error messages and help text