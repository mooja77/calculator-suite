#!/usr/bin/env python3
"""
Calculator Suite API Examples
Demonstrates how to use the Calculator Suite API programmatically
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class CalculatorAPI:
    """Python SDK for Calculator Suite API"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CalculatorSuite-Python-SDK/1.0'
        })
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}/calculate/{endpoint}"
        
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    # Financial Calculators
    def calculate_loan(self, loan_amount: float, annual_rate: float, 
                      loan_term_years: float, loan_type: str = "personal") -> Dict[str, Any]:
        """Calculate loan payments and totals"""
        return self._make_request("loan", {
            "loan_amount": str(loan_amount),
            "annual_rate": str(annual_rate),
            "loan_term_years": str(loan_term_years),
            "loan_type": loan_type
        })
    
    def calculate_mortgage(self, home_price: float, down_payment_percent: float,
                          annual_rate: float, loan_term_years: float,
                          property_tax_annual: Optional[float] = None,
                          home_insurance_annual: Optional[float] = None) -> Dict[str, Any]:
        """Calculate mortgage payments with taxes and insurance"""
        data = {
            "home_price": str(home_price),
            "down_payment_percent": str(down_payment_percent),
            "annual_rate": str(annual_rate),
            "loan_term_years": str(loan_term_years)
        }
        
        if property_tax_annual:
            data["property_tax_annual"] = str(property_tax_annual)
        if home_insurance_annual:
            data["home_insurance_annual"] = str(home_insurance_annual)
        
        return self._make_request("mortgage", data)
    
    def calculate_retirement(self, current_age: int, retirement_age: int,
                           current_savings: float, monthly_contribution: float,
                           annual_return: float, retirement_income_goal: Optional[float] = None) -> Dict[str, Any]:
        """Calculate retirement savings projections"""
        data = {
            "current_age": str(current_age),
            "retirement_age": str(retirement_age),
            "current_savings": str(current_savings),
            "monthly_contribution": str(monthly_contribution),
            "annual_return": str(annual_return)
        }
        
        if retirement_income_goal:
            data["retirement_income_goal"] = str(retirement_income_goal)
        
        return self._make_request("retirement", data)
    
    def calculate_compound_interest(self, principal: float, annual_rate: float,
                                  years: int, compound_frequency: int = 12,
                                  monthly_contribution: Optional[float] = None) -> Dict[str, Any]:
        """Calculate compound interest growth"""
        data = {
            "principal": str(principal),
            "annual_rate": str(annual_rate),
            "years": str(years),
            "compound_frequency": str(compound_frequency)
        }
        
        if monthly_contribution:
            data["monthly_contribution"] = str(monthly_contribution)
        
        return self._make_request("compound-interest", data)
    
    # Salary and Tax Calculators
    def calculate_gross_to_net(self, gross_salary: float, pay_frequency: str = "monthly",
                              filing_status: str = "single", state: str = "federal_only") -> Dict[str, Any]:
        """Calculate net pay from gross salary"""
        return self._make_request("gross-to-net", {
            "gross_salary": str(gross_salary),
            "pay_frequency": pay_frequency,
            "filing_status": filing_status,
            "state": state
        })
    
    def calculate_hourly_to_salary(self, hourly_rate: float, hours_per_week: float = 40,
                                  weeks_per_year: float = 52) -> Dict[str, Any]:
        """Convert hourly rate to annual salary"""
        return self._make_request("hourly-to-salary", {
            "calculation_type": "hourly_to_salary",
            "hourly_rate": str(hourly_rate),
            "hours_per_week": str(hours_per_week),
            "weeks_per_year": str(weeks_per_year)
        })
    
    def calculate_salary_raise(self, current_salary: float, raise_percentage: float) -> Dict[str, Any]:
        """Calculate salary after percentage raise"""
        return self._make_request("salary-raise", {
            "calculation_type": "raise_percentage",
            "current_salary": str(current_salary),
            "raise_percentage": str(raise_percentage)
        })
    
    # Utility Calculators
    def calculate_percentage(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Calculate various percentage operations"""
        data = {"operation": operation}
        data.update({k: str(v) for k, v in kwargs.items()})
        return self._make_request("percentage", data)
    
    def calculate_bmi(self, height: float, weight: float, unit_system: str = "metric",
                     age: Optional[int] = None, gender: Optional[str] = None) -> Dict[str, Any]:
        """Calculate BMI and health category"""
        data = {
            "height": str(height),
            "weight": str(weight),
            "unit_system": unit_system
        }
        
        if age:
            data["age"] = str(age)
        if gender:
            data["gender"] = gender
        
        return self._make_request("bmi", data)
    
    def calculate_tip(self, bill_amount: float, tip_percentage: float,
                     number_of_people: int = 1, tax_amount: Optional[float] = None) -> Dict[str, Any]:
        """Calculate tip and split bill"""
        data = {
            "bill_amount": str(bill_amount),
            "tip_percentage": str(tip_percentage),
            "number_of_people": str(number_of_people)
        }
        
        if tax_amount:
            data["tax_amount"] = str(tax_amount)
        
        return self._make_request("tip", data)


def run_examples():
    """Run example calculations"""
    api = CalculatorAPI()
    
    print("🧮 Calculator Suite API Examples")
    print("=" * 50)
    
    try:
        # Loan calculation example
        print("\n💰 Loan Calculator Example:")
        loan_result = api.calculate_loan(
            loan_amount=250000,
            annual_rate=6.5,
            loan_term_years=30,
            loan_type="mortgage"
        )
        print(f"Monthly Payment: ${loan_result['monthly_payment']:,.2f}")
        print(f"Total Interest: ${loan_result['total_interest']:,.2f}")
        
        # Retirement planning example
        print("\n🏖️ Retirement Calculator Example:")
        retirement_result = api.calculate_retirement(
            current_age=30,
            retirement_age=65,
            current_savings=25000,
            monthly_contribution=1000,
            annual_return=7.5,
            retirement_income_goal=80000
        )
        print(f"Retirement Savings: ${retirement_result['total_retirement_savings']:,.2f}")
        print(f"Readiness Score: {retirement_result['readiness_score']:.1f}%")
        
        # Salary calculation example
        print("\n💼 Salary Calculator Example:")
        salary_result = api.calculate_hourly_to_salary(
            hourly_rate=35,
            hours_per_week=40,
            weeks_per_year=52
        )
        print(f"Annual Salary: ${salary_result['annual_salary']:,.2f}")
        print(f"Monthly Salary: ${salary_result['monthly_salary']:,.2f}")
        
        # BMI calculation example
        print("\n📏 BMI Calculator Example:")
        bmi_result = api.calculate_bmi(
            height=175,
            weight=70,
            unit_system="metric",
            age=30,
            gender="male"
        )
        print(f"BMI: {bmi_result['bmi']:.1f}")
        print(f"Category: {bmi_result['category']}")
        
        # Percentage calculation example
        print("\n📊 Percentage Calculator Example:")
        percentage_result = api.calculate_percentage(
            operation="increase",
            original=1000,
            percent=15
        )
        print(f"Result: {percentage_result['result']}")
        print(f"Explanation: {percentage_result['explanation']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the Calculator Suite server is running on localhost:5000")


def benchmark_api_performance():
    """Benchmark API response times"""
    api = CalculatorAPI()
    
    print("\n⚡ API Performance Benchmark")
    print("=" * 50)
    
    tests = [
        ("Percentage Calculator", lambda: api.calculate_percentage(operation="basic", x=25, y=100)),
        ("Loan Calculator", lambda: api.calculate_loan(100000, 5.5, 30)),
        ("BMI Calculator", lambda: api.calculate_bmi(175, 70)),
        ("Retirement Calculator", lambda: api.calculate_retirement(35, 65, 50000, 1000, 7)),
        ("Tip Calculator", lambda: api.calculate_tip(85.50, 18, 4))
    ]
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"{test_name:20} {response_time:6.1f}ms")
            
        except Exception as e:
            print(f"{test_name:20} ERROR: {e}")


def test_concurrent_requests():
    """Test concurrent API requests"""
    import threading
    import queue
    
    api = CalculatorAPI()
    results_queue = queue.Queue()
    
    def make_request():
        try:
            start_time = time.time()
            result = api.calculate_percentage(operation="basic", x=50, y=200)
            end_time = time.time()
            results_queue.put((True, end_time - start_time))
        except Exception as e:
            results_queue.put((False, str(e)))
    
    print("\n🔄 Concurrent Request Test (10 requests)")
    print("=" * 50)
    
    threads = []
    start_time = time.time()
    
    # Start 10 concurrent requests
    for i in range(10):
        thread = threading.Thread(target=make_request)
        thread.start()
        threads.append(thread)
    
    # Wait for all requests to complete
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = 0
    failed = 0
    response_times = []
    
    while not results_queue.empty():
        success, result = results_queue.get()
        if success:
            successful += 1
            response_times.append(result * 1000)  # Convert to ms
        else:
            failed += 1
            print(f"Failed request: {result}")
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        print(f"Successful requests: {successful}")
        print(f"Failed requests: {failed}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average response time: {avg_response_time:.1f}ms")
        print(f"Max response time: {max(response_times):.1f}ms")
        print(f"Min response time: {min(response_times):.1f}ms")


if __name__ == "__main__":
    # Run examples
    run_examples()
    
    # Performance benchmarks
    benchmark_api_performance()
    
    # Concurrent request test
    test_concurrent_requests()
    
    print("\n✅ API examples completed!")
    print("See API_DOCUMENTATION.md for complete API reference.")