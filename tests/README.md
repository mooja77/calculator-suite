# Calculator Suite Test Suite

Comprehensive test suite for the Calculator Suite application.

## Test Files

### Core Test Files
- **`test_calculators.py`** - Unit tests for all 18 calculator classes
- **`test_edge_cases.py`** - Edge cases and boundary condition tests  
- **`test_performance.py`** - Performance, load, and concurrency tests
- **`conftest.py`** - Pytest configuration and shared fixtures

### Test Runner
- **`run_tests.py`** - Complete test runner with coverage analysis

## Running Tests

### Quick Start
```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
python -m pytest tests/test_calculators.py -v

# Run with coverage
python -m pytest tests/ --cov=app_simple_fixed --cov-report=term-missing
```

### Individual Test Categories

```bash
# Unit tests only
python -m pytest tests/test_calculators.py -v

# Edge cases only  
python -m pytest tests/test_edge_cases.py -v

# Performance tests only
python -m pytest tests/test_performance.py -v
```

## Test Coverage

The test suite covers:

### Calculator Classes (18 total)
- PercentageCalculator
- LoanCalculator  
- BMICalculator
- TipCalculator
- MortgageCalculator
- IncomeTaxCalculator
- SalesTaxCalculator
- PropertyTaxCalculator
- TaxRefundCalculator
- GrossToNetCalculator
- HourlyToSalaryCalculator
- SalaryRaiseCalculator
- CostOfLivingCalculator
- CompoundInterestCalculator
- RetirementCalculator
- InvestmentReturnCalculator

### Test Categories
- **Unit Tests** (380+ tests) - Basic functionality, validation, calculations
- **Edge Cases** (500+ tests) - Boundary conditions, extreme values, error scenarios
- **Performance Tests** (50+ tests) - Response times, concurrency, resource usage
- **Integration Tests** - Flask app, API endpoints, web pages

### Key Features Tested
- Input validation and error handling
- Mathematical accuracy and precision
- SEO metadata generation
- API endpoint functionality
- Web page rendering
- Concurrent request handling
- Memory usage and performance
- Extreme value calculations
- Error recovery and logging

## Requirements

```bash
pip install pytest
pip install pytest-cov  # For coverage analysis
pip install psutil      # For memory usage tests
```

## Test Results

Expected results:
- **Unit Tests**: 380+ tests covering all calculator functionality
- **Edge Cases**: 500+ tests for boundary conditions and error scenarios  
- **Performance**: 50+ tests ensuring response times under acceptable limits
- **Coverage**: 95%+ code coverage of calculator logic

## Performance Benchmarks

Target performance metrics:
- Individual calculations: < 100ms
- Complex calculations (retirement, investment): < 500ms  
- API endpoints: < 300ms response time
- Web pages: < 800ms load time
- Concurrent requests: Handle 15+ simultaneous requests in < 2s