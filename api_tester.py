#!/usr/bin/env python3
"""
Calculator Suite API Tester
Interactive testing tool for all calculator endpoints
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional


class APITester:
    """Interactive API testing utility"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CalculatorSuite-API-Tester/1.0'
        })
        
        # Test data templates
        self.test_data = {
            'percentage': [
                {'operation': 'basic', 'x': '25', 'y': '100'},
                {'operation': 'increase', 'original': '100', 'percent': '15'},
                {'operation': 'change', 'original': '50', 'new_value': '75'}
            ],
            'loan': [
                {'loan_amount': '250000', 'annual_rate': '6.5', 'loan_term_years': '30'},
                {'loan_amount': '50000', 'annual_rate': '4.2', 'loan_term_years': '5', 'loan_type': 'auto'},
                {'loan_amount': '1000000', 'annual_rate': '3.5', 'loan_term_years': '15'}
            ],
            'bmi': [
                {'height': '175', 'weight': '70', 'unit_system': 'metric', 'age': '30', 'gender': 'male'},
                {'height_feet': '5', 'height_inches': '9', 'weight': '154', 'unit_system': 'imperial', 'age': '25', 'gender': 'female'},
                {'height': '180', 'weight': '85', 'unit_system': 'metric'}
            ],
            'tip': [
                {'bill_amount': '85.50', 'tip_percentage': '18', 'number_of_people': '4'},
                {'bill_amount': '120.00', 'tip_percentage': '20', 'number_of_people': '2', 'tax_amount': '10.80'},
                {'bill_amount': '45.75', 'tip_percentage': '15', 'number_of_people': '1'}
            ],
            'mortgage': [
                {'home_price': '450000', 'down_payment_percent': '20', 'annual_rate': '7.0', 'loan_term_years': '30'},
                {'home_price': '300000', 'down_payment_percent': '10', 'annual_rate': '6.5', 'loan_term_years': '30'},
                {'home_price': '750000', 'down_payment_percent': '25', 'annual_rate': '5.8', 'loan_term_years': '15'}
            ],
            'income-tax': [
                {'annual_income': '75000', 'filing_status': 'single', 'state': 'california', 'tax_year': '2024'},
                {'annual_income': '120000', 'filing_status': 'married_jointly', 'state': 'texas', 'tax_year': '2024'},
                {'annual_income': '55000', 'filing_status': 'head_of_household', 'state': 'new_york', 'tax_year': '2024'}
            ],
            'retirement': [
                {'current_age': '32', 'retirement_age': '65', 'current_savings': '75000', 'monthly_contribution': '1200', 'annual_return': '7.5'},
                {'current_age': '45', 'retirement_age': '67', 'current_savings': '150000', 'monthly_contribution': '2000', 'annual_return': '6.5'},
                {'current_age': '25', 'retirement_age': '60', 'current_savings': '15000', 'monthly_contribution': '800', 'annual_return': '8.0'}
            ],
            'compound-interest': [
                {'principal': '15000', 'annual_rate': '8', 'years': '20', 'compound_frequency': '12', 'monthly_contribution': '500'},
                {'principal': '50000', 'annual_rate': '6.5', 'years': '10', 'compound_frequency': '4'},
                {'principal': '5000', 'annual_rate': '10', 'years': '30', 'compound_frequency': '365', 'monthly_contribution': '200'}
            ],
            'investment-return': [
                {'calculation_type': 'future_value', 'initial_investment': '25000', 'annual_return': '9', 'years': '15', 'additional_contributions': '800', 'contribution_frequency': 'monthly'},
                {'calculation_type': 'required_return', 'initial_investment': '10000', 'target_value': '75000', 'years': '12'},
                {'calculation_type': 'portfolio_analysis', 'investment_1_name': 'S&P 500', 'investment_1_initial': '15000', 'investment_1_current': '18500', 'investment_2_name': 'Bonds', 'investment_2_initial': '8000', 'investment_2_current': '8400'}
            ],
            'salary-raise': [
                {'calculation_type': 'raise_percentage', 'current_salary': '68000', 'raise_percentage': '7.5'},
                {'calculation_type': 'raise_amount', 'current_salary': '75000', 'raise_amount': '5000'},
                {'calculation_type': 'target_salary', 'current_salary': '65000', 'target_salary': '75000'}
            ],
            'gross-to-net': [
                {'gross_salary': '85000', 'pay_frequency': 'bi-weekly', 'filing_status': 'single', 'state': 'california'},
                {'gross_salary': '120000', 'pay_frequency': 'monthly', 'filing_status': 'married_jointly', 'state': 'texas'},
                {'gross_salary': '65000', 'pay_frequency': 'weekly', 'filing_status': 'head_of_household', 'state': 'new_york'}
            ],
            'hourly-to-salary': [
                {'calculation_type': 'hourly_to_salary', 'hourly_rate': '32.50', 'hours_per_week': '40', 'weeks_per_year': '52'},
                {'calculation_type': 'salary_to_hourly', 'annual_salary': '75000', 'hours_per_week': '40', 'weeks_per_year': '50'},
                {'calculation_type': 'hourly_to_salary', 'hourly_rate': '28.00', 'hours_per_week': '37.5', 'weeks_per_year': '50'}
            ]
        }
    
    def test_endpoint(self, calculator: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single endpoint with data"""
        url = f"{self.base_url}/api/calculate/{calculator}"
        
        try:
            start_time = time.time()
            response = self.session.post(url, json=data, timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                'calculator': calculator,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': response.status_code == 200,
                'data': data
            }
            
            try:
                result['response'] = response.json()
            except json.JSONDecodeError:
                result['response'] = {'error': 'Invalid JSON response'}
                result['success'] = False
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'calculator': calculator,
                'status_code': 0,
                'response_time_ms': 0,
                'success': False,
                'error': str(e),
                'data': data
            }
    
    def test_all_endpoints(self) -> List[Dict[str, Any]]:
        """Test all endpoints with sample data"""
        results = []
        
        print("🧪 Testing all Calculator Suite endpoints...")
        print("=" * 60)
        
        for calculator, test_cases in self.test_data.items():
            print(f"\n📊 Testing {calculator} calculator...")
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"  Test case {i}: ", end="")
                result = self.test_endpoint(calculator, test_case)
                
                if result['success']:
                    print(f"✅ {result['response_time_ms']}ms")
                else:
                    print(f"❌ {result.get('error', 'Failed')}")
                
                results.append(result)
        
        return results
    
    def test_specific_calculator(self, calculator: str) -> List[Dict[str, Any]]:
        """Test a specific calculator with all test cases"""
        if calculator not in self.test_data:
            print(f"❌ Unknown calculator: {calculator}")
            print(f"Available calculators: {', '.join(self.test_data.keys())}")
            return []
        
        results = []
        test_cases = self.test_data[calculator]
        
        print(f"🧪 Testing {calculator} calculator...")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest case {i}:")
            print(f"Input: {json.dumps(test_case, indent=2)}")
            
            result = self.test_endpoint(calculator, test_case)
            
            if result['success']:
                print(f"✅ Success ({result['response_time_ms']}ms)")
                print(f"Output: {json.dumps(result['response'], indent=2)}")
            else:
                print(f"❌ Failed")
                if 'error' in result:
                    print(f"Error: {result['error']}")
                if 'response' in result and 'errors' in result['response']:
                    print(f"Validation errors: {result['response']['errors']}")
            
            results.append(result)
        
        return results
    
    def performance_test(self, calculator: str, iterations: int = 100) -> Dict[str, Any]:
        """Performance test for a specific calculator"""
        if calculator not in self.test_data:
            print(f"❌ Unknown calculator: {calculator}")
            return {}
        
        test_case = self.test_data[calculator][0]  # Use first test case
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        print(f"⚡ Performance testing {calculator} ({iterations} requests)...")
        print("=" * 60)
        
        start_time = time.time()
        
        for i in range(iterations):
            if i % 10 == 0:
                print(f"Progress: {i}/{iterations}", end="\r")
            
            result = self.test_endpoint(calculator, test_case)
            
            if result['success']:
                successful_requests += 1
                response_times.append(result['response_time_ms'])
            else:
                failed_requests += 1
        
        total_time = time.time() - start_time
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p50 = p95 = p99 = 0
        
        results = {
            'calculator': calculator,
            'iterations': iterations,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'total_time_seconds': round(total_time, 2),
            'requests_per_second': round(iterations / total_time, 2),
            'avg_response_time_ms': round(avg_response_time, 2),
            'min_response_time_ms': round(min_response_time, 2),
            'max_response_time_ms': round(max_response_time, 2),
            'p50_response_time_ms': round(p50, 2),
            'p95_response_time_ms': round(p95, 2),
            'p99_response_time_ms': round(p99, 2)
        }
        
        print(f"\n📊 Performance Results:")
        print(f"Total time: {results['total_time_seconds']}s")
        print(f"Requests/second: {results['requests_per_second']}")
        print(f"Success rate: {successful_requests}/{iterations} ({successful_requests/iterations*100:.1f}%)")
        print(f"Average response time: {results['avg_response_time_ms']}ms")
        print(f"Response time range: {results['min_response_time_ms']}-{results['max_response_time_ms']}ms")
        print(f"Percentiles: P50={results['p50_response_time_ms']}ms, P95={results['p95_response_time_ms']}ms, P99={results['p99_response_time_ms']}ms")
        
        return results
    
    def stress_test(self, concurrent_requests: int = 20, duration_seconds: int = 30) -> Dict[str, Any]:
        """Stress test with concurrent requests"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        stop_event = threading.Event()
        
        def worker():
            calculator = 'percentage'  # Use simple calculator for stress test
            test_case = self.test_data[calculator][0]
            
            while not stop_event.is_set():
                try:
                    result = self.test_endpoint(calculator, test_case)
                    results_queue.put(result)
                except Exception as e:
                    results_queue.put({'success': False, 'error': str(e)})
        
        print(f"💪 Stress testing with {concurrent_requests} concurrent requests for {duration_seconds}s...")
        print("=" * 60)
        
        # Start worker threads
        threads = []
        for i in range(concurrent_requests):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Run for specified duration
        time.sleep(duration_seconds)
        
        # Stop all threads
        stop_event.set()
        for thread in threads:
            thread.join(timeout=5)
        
        # Collect results
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        while not results_queue.empty():
            result = results_queue.get()
            total_requests += 1
            
            if result.get('success', False):
                successful_requests += 1
                if 'response_time_ms' in result:
                    response_times.append(result['response_time_ms'])
            else:
                failed_requests += 1
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        else:
            avg_response_time = 0
        
        results = {
            'concurrent_requests': concurrent_requests,
            'duration_seconds': duration_seconds,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'requests_per_second': round(total_requests / duration_seconds, 2),
            'success_rate': round(successful_requests / total_requests * 100, 1) if total_requests > 0 else 0,
            'avg_response_time_ms': round(avg_response_time, 2)
        }
        
        print(f"\n📊 Stress Test Results:")
        print(f"Total requests: {results['total_requests']}")
        print(f"Requests/second: {results['requests_per_second']}")
        print(f"Success rate: {results['success_rate']}%")
        print(f"Average response time: {results['avg_response_time_ms']}ms")
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a summary report"""
        if not results:
            return "No test results to report."
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        if successful_tests > 0:
            avg_response_time = sum(r.get('response_time_ms', 0) for r in results if r.get('success', False)) / successful_tests
        else:
            avg_response_time = 0
        
        report = f"""
📋 Test Summary Report
{'=' * 50}
Total tests: {total_tests}
Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)
Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
Average response time: {avg_response_time:.2f}ms

Calculator Results:
"""
        
        # Group by calculator
        by_calculator = {}
        for result in results:
            calc = result.get('calculator', 'unknown')
            if calc not in by_calculator:
                by_calculator[calc] = {'total': 0, 'success': 0, 'times': []}
            
            by_calculator[calc]['total'] += 1
            if result.get('success', False):
                by_calculator[calc]['success'] += 1
                if 'response_time_ms' in result:
                    by_calculator[calc]['times'].append(result['response_time_ms'])
        
        for calc, stats in by_calculator.items():
            success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
            avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            report += f"{calc:20} {stats['success']}/{stats['total']} ({success_rate:.1f}%) - {avg_time:.1f}ms avg\n"
        
        return report


def main():
    """Interactive API tester"""
    tester = APITester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'all':
            results = tester.test_all_endpoints()
            print(tester.generate_report(results))
        
        elif command == 'performance':
            calculator = sys.argv[2] if len(sys.argv) > 2 else 'percentage'
            iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            tester.performance_test(calculator, iterations)
        
        elif command == 'stress':
            concurrent = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
            tester.stress_test(concurrent, duration)
        
        elif command in tester.test_data:
            results = tester.test_specific_calculator(command)
            print(tester.generate_report(results))
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: all, performance, stress, or any calculator name")
            print(f"Available calculators: {', '.join(tester.test_data.keys())}")
    
    else:
        print("🧪 Calculator Suite API Tester")
        print("Usage:")
        print("  python api_tester.py all                    # Test all endpoints")
        print("  python api_tester.py [calculator]           # Test specific calculator")
        print("  python api_tester.py performance [calc] [n] # Performance test")
        print("  python api_tester.py stress [conc] [dur]    # Stress test")
        print()
        print(f"Available calculators: {', '.join(tester.test_data.keys())}")


if __name__ == "__main__":
    main()