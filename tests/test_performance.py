#!/usr/bin/env python3
"""
Performance tests for Calculator Suite
Tests response times, load handling, and resource usage
"""

import pytest
import time
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch
import json

# Add the parent directory to sys.path to import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_simple_fixed import (
    PercentageCalculator, LoanCalculator, BMICalculator, MortgageCalculator,
    IncomeTaxCalculator, RetirementCalculator, CompoundInterestCalculator,
    InvestmentReturnCalculator, app, calculation_logs
)


class TestCalculationPerformance:
    """Test individual calculator performance"""
    
    def test_percentage_calculator_speed(self):
        """Test percentage calculator completes within acceptable time"""
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
        
        start_time = time.time()
        result = calc.calculate(inputs)
        execution_time = time.time() - start_time
        
        assert execution_time < 0.1  # Should complete in less than 100ms
        assert result['result'] == 25.0
    
    def test_loan_calculator_speed(self):
        """Test loan calculator with amortization completes quickly"""
        calc = LoanCalculator()
        inputs = {
            'loan_amount': '500000',
            'annual_rate': '6.5',
            'loan_term_years': '30'
        }
        
        start_time = time.time()
        result = calc.calculate(inputs)
        execution_time = time.time() - start_time
        
        assert execution_time < 0.2  # Should complete in less than 200ms
        assert result['monthly_payment'] > 0
    
    def test_retirement_calculator_speed(self):
        """Test retirement calculator with complex calculations"""
        calc = RetirementCalculator()
        inputs = {
            'current_age': '25',
            'retirement_age': '65',
            'current_savings': '10000',
            'monthly_contribution': '1500',
            'annual_return': '8'
        }
        
        start_time = time.time()
        result = calc.calculate(inputs)
        execution_time = time.time() - start_time
        
        assert execution_time < 0.3  # Should complete in less than 300ms
        assert result['total_retirement_savings'] > 0
    
    def test_investment_calculator_iterative_solver_speed(self):
        """Test investment calculator's iterative solver performance"""
        calc = InvestmentReturnCalculator()
        inputs = {
            'calculation_type': 'required_return',
            'initial_investment': '10000',
            'target_value': '100000',
            'years': '15'
        }
        
        start_time = time.time()
        result = calc.calculate(inputs)
        execution_time = time.time() - start_time
        
        assert execution_time < 0.5  # Iterative solver should complete in less than 500ms
        assert result['required_return'] > 0
    
    def test_compound_interest_yearly_breakdown_speed(self):
        """Test compound interest calculator with yearly breakdown"""
        calc = CompoundInterestCalculator()
        inputs = {
            'principal': '50000',
            'annual_rate': '7',
            'years': '30',  # Long term calculation
            'compound_frequency': '12',
            'monthly_contribution': '1000'
        }
        
        start_time = time.time()
        result = calc.calculate(inputs)
        execution_time = time.time() - start_time
        
        assert execution_time < 0.4  # Should complete in less than 400ms
        assert len(result['yearly_breakdown']) == 30
        assert result['total_value'] > result['principal']


class TestConcurrentCalculations:
    """Test performance under concurrent load"""
    
    def test_concurrent_percentage_calculations(self):
        """Test multiple percentage calculations running concurrently"""
        def run_calculation():
            calc = PercentageCalculator()
            inputs = {'operation': 'basic', 'x': '50', 'y': '200'}
            return calc.calculate(inputs)
        
        # Run 20 concurrent calculations
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(run_calculation) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
            total_time = time.time() - start_time
        
        assert len(results) == 20
        assert all(result['result'] == 25.0 for result in results)
        assert total_time < 2.0  # All 20 should complete in less than 2 seconds
    
    def test_concurrent_different_calculators(self):
        """Test different calculator types running concurrently"""
        def run_percentage_calc():
            calc = PercentageCalculator()
            return calc.calculate({'operation': 'basic', 'x': '25', 'y': '100'})
        
        def run_loan_calc():
            calc = LoanCalculator()
            return calc.calculate({
                'loan_amount': '100000',
                'annual_rate': '5',
                'loan_term_years': '30'
            })
        
        def run_bmi_calc():
            calc = BMICalculator()
            return calc.calculate({
                'height': '175',
                'weight': '70',
                'unit_system': 'metric'
            })
        
        calculations = [run_percentage_calc, run_loan_calc, run_bmi_calc] * 5
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            start_time = time.time()
            futures = [executor.submit(calc) for calc in calculations]
            results = [future.result() for future in as_completed(futures)]
            total_time = time.time() - start_time
        
        assert len(results) == 15
        assert total_time < 3.0  # Should complete in less than 3 seconds
    
    def test_memory_usage_under_load(self):
        """Test that memory usage doesn't grow excessively under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run many calculations
        calc = LoanCalculator()
        for i in range(100):
            inputs = {
                'loan_amount': str(100000 + i * 1000),
                'annual_rate': '5.5',
                'loan_term_years': '30'
            }
            result = calc.calculate(inputs)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for 100 calculations)
        assert memory_increase < 50


class TestWebAppPerformance:
    """Test Flask web application performance"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        return app.test_client()
    
    def test_homepage_response_time(self, client):
        """Test homepage loads quickly"""
        start_time = time.time()
        response = client.get('/')
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 0.5  # Should load in less than 500ms
    
    def test_calculator_page_response_time(self, client):
        """Test calculator pages load quickly"""
        calculator_paths = [
            '/calculators/percentage/',
            '/calculators/bmi/',
            '/calculators/loan/',
            '/calculators/mortgage/',
            '/calculators/retirement/'
        ]
        
        for path in calculator_paths:
            start_time = time.time()
            response = client.get(path)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 0.8  # Each page should load in less than 800ms
    
    def test_api_endpoint_response_time(self, client):
        """Test API endpoints respond quickly"""
        start_time = time.time()
        response = client.post('/api/calculate/percentage',
                             json={'operation': 'basic', 'x': '25', 'y': '100'},
                             content_type='application/json')
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 0.3  # API should respond in less than 300ms
        
        data = json.loads(response.data)
        assert data['result'] == 25.0
    
    def test_concurrent_web_requests(self, client):
        """Test web app handles concurrent requests well"""
        def make_request():
            return client.post('/api/calculate/percentage',
                             json={'operation': 'basic', 'x': '50', 'y': '200'},
                             content_type='application/json')
        
        # Make 15 concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(15)]
            responses = [future.result() for future in as_completed(futures)]
            total_time = time.time() - start_time
        
        assert len(responses) == 15
        assert all(resp.status_code == 200 for resp in responses)
        assert total_time < 2.0  # All requests should complete in less than 2 seconds
        
        # Verify all calculations are correct
        for response in responses:
            data = json.loads(response.data)
            assert data['result'] == 25.0
    
    def test_large_calculation_handling(self, client):
        """Test handling of calculations with large numbers"""
        start_time = time.time()
        response = client.post('/api/calculate/loan',
                             json={
                                 'loan_amount': '10000000',  # 10 million
                                 'annual_rate': '4.5',
                                 'loan_term_years': '30'
                             },
                             content_type='application/json')
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should handle large numbers quickly
        
        data = json.loads(response.data)
        assert data['loan_amount'] == 10000000.0
        assert data['monthly_payment'] > 0


class TestCalculationLogsPerformance:
    """Test performance of calculation logging system"""
    
    def test_logging_performance(self):
        """Test that logging doesn't significantly impact performance"""
        # Clear existing logs
        calculation_logs.clear()
        
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
        
        # Time calculation without logging
        start_time = time.time()
        for i in range(100):
            result = calc.calculate(inputs)
        time_without_logging = time.time() - start_time
        
        # Time with manual logging simulation
        start_time = time.time()
        for i in range(100):
            result = calc.calculate(inputs)
            calculation_logs.append({
                'calculator': 'percentage',
                'inputs': inputs,
                'result': result,
                'timestamp': time.time()
            })
        time_with_logging = time.time() - start_time
        
        # Logging shouldn't add more than 50% overhead
        assert time_with_logging < time_without_logging * 1.5
        assert len(calculation_logs) == 100
        
        # Clean up
        calculation_logs.clear()
    
    def test_large_log_storage_performance(self):
        """Test performance with large number of stored calculations"""
        # Fill logs with many entries
        for i in range(1000):
            calculation_logs.append({
                'calculator': 'test',
                'inputs': {'x': i},
                'result': {'result': i * 2},
                'timestamp': time.time()
            })
        
        # Verify performance doesn't degrade with large log
        calc = PercentageCalculator()
        inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
        
        start_time = time.time()
        result = calc.calculate(inputs)
        execution_time = time.time() - start_time
        
        assert execution_time < 0.1  # Should still be fast
        assert result['result'] == 25.0
        
        # Clean up
        calculation_logs.clear()


class TestEdgeCasePerformance:
    """Test performance with edge cases and extreme values"""
    
    def test_extreme_loan_calculations(self):
        """Test performance with extreme loan values"""
        calc = LoanCalculator()
        
        # Very large loan
        start_time = time.time()
        result = calc.calculate({
            'loan_amount': '100000000',  # 100 million
            'annual_rate': '3.5',
            'loan_term_years': '30'
        })
        execution_time = time.time() - start_time
        
        assert execution_time < 0.3
        assert result['monthly_payment'] > 0
        
        # Very long term
        start_time = time.time()
        result = calc.calculate({
            'loan_amount': '500000',
            'annual_rate': '4.0',
            'loan_term_years': '50'  # 50 year loan
        })
        execution_time = time.time() - start_time
        
        assert execution_time < 0.3
        assert result['monthly_payment'] > 0
    
    def test_complex_investment_scenarios(self):
        """Test performance with complex investment calculations"""
        calc = InvestmentReturnCalculator()
        
        # Portfolio analysis with extreme values
        start_time = time.time()
        result = calc.calculate({
            'calculation_type': 'portfolio_analysis',
            'investment_1_name': 'Large Cap',
            'investment_1_initial': '1000000',
            'investment_1_current': '1500000',
            'investment_2_name': 'Small Cap',
            'investment_2_initial': '500000',
            'investment_2_current': '400000'
        })
        execution_time = time.time() - start_time
        
        assert execution_time < 0.4
        assert result['total_initial'] == 1500000.0
        assert result['total_current'] == 1900000.0
    
    def test_high_precision_calculations(self):
        """Test performance with high precision decimal calculations"""
        calc = PercentageCalculator()
        
        start_time = time.time()
        result = calc.calculate({
            'operation': 'basic',
            'x': '1.23456789012345',
            'y': '9.87654321098765'
        })
        execution_time = time.time() - start_time
        
        assert execution_time < 0.1
        assert isinstance(result['result'], float)


class TestResourceUtilization:
    """Test resource utilization and cleanup"""
    
    def test_calculator_instance_cleanup(self):
        """Test that calculator instances don't accumulate memory"""
        import gc
        
        # Create many calculator instances
        calculators = []
        for i in range(1000):
            calc = PercentageCalculator()
            calc.calculate({'operation': 'basic', 'x': str(i), 'y': '100'})
            calculators.append(calc)
        
        # Clear references
        calculators.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Create new calculator and verify it still works efficiently
        calc = PercentageCalculator()
        start_time = time.time()
        result = calc.calculate({'operation': 'basic', 'x': '25', 'y': '100'})
        execution_time = time.time() - start_time
        
        assert execution_time < 0.1
        assert result['result'] == 25.0
    
    def test_error_handling_performance(self):
        """Test that error handling doesn't significantly impact performance"""
        calc = PercentageCalculator()
        
        # Time successful calculations
        start_time = time.time()
        for i in range(100):
            calc.calculate({'operation': 'basic', 'x': '25', 'y': '100'})
        success_time = time.time() - start_time
        
        # Time error cases
        start_time = time.time()
        for i in range(100):
            try:
                calc.calculate({'operation': 'basic', 'x': '25', 'y': '0'})  # Division by zero
            except ValueError:
                pass
        error_time = time.time() - start_time
        
        # Error handling shouldn't be more than 3x slower
        assert error_time < success_time * 3


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])