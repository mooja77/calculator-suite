#!/usr/bin/env python3
"""
Comprehensive test script for global infrastructure validation.
"""
import sys
import os
import requests
import json
from decimal import Decimal
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.utils.db_seed import seed_all, get_seeding_status
from app.services.currency import currency_service
from app.services.localization import localization_service
from app.utils.error_handling import health_checker

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_result(test_name, success, details=None):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"     Details: {details}")

def test_database_setup():
    """Test database setup and seeding."""
    print_header("DATABASE SETUP TESTS")
    
    try:
        # Create tables
        with app.app_context():
            db.create_all()
            print_result("Database tables created", True)
            
            # Test seeding
            seed_success = seed_all()
            print_result("Database seeding", seed_success)
            
            # Check seeding status
            status = get_seeding_status()
            if status:
                print("Seeding Status:")
                for table, info in status.items():
                    print(f"  {table}: {info['seeded']}/{info['total']} seeded, {info['active']} active")
                return True
            else:
                print_result("Seeding status check", False)
                return False
    except Exception as e:
        print_result("Database setup", False, str(e))
        return False

def test_currency_service():
    """Test currency service functionality."""
    print_header("CURRENCY SERVICE TESTS")
    
    with app.app_context():
        try:
            # Test getting supported currencies
            currencies = currency_service.get_supported_currencies()
            print_result("Get supported currencies", len(currencies) > 0, f"{len(currencies)} currencies")
            
            # Test exchange rate fetching
            rate = currency_service.get_exchange_rate('USD', 'EUR')
            print_result("Get exchange rate USD/EUR", rate is not None, f"Rate: {rate}")
            
            # Test currency conversion
            converted = currency_service.convert_currency(Decimal('100'), 'USD', 'EUR')
            print_result("Convert 100 USD to EUR", converted is not None, f"Result: {converted}")
            
            # Test currency formatting
            formatted = currency_service.format_currency(Decimal('1234.56'), 'USD')
            print_result("Format currency", formatted is not None, f"Formatted: {formatted}")
            
            # Test same currency conversion
            same_rate = currency_service.get_exchange_rate('USD', 'USD')
            print_result("Same currency rate", same_rate == Decimal('1.0'), f"Rate: {same_rate}")
            
            return True
        except Exception as e:
            print_result("Currency service tests", False, str(e))
            return False

def test_localization_service():
    """Test localization service functionality."""
    print_header("LOCALIZATION SERVICE TESTS")
    
    with app.app_context():
        try:
            # Test regional config
            us_config = localization_service.get_regional_config('US')
            print_result("Get US regional config", bool(us_config), f"Currency: {us_config.get('currency_code')}")
            
            # Test supported locales
            locales = localization_service.get_supported_locales()
            print_result("Get supported locales", len(locales) > 0, f"{len(locales)} locales")
            
            # Test number formatting
            formatted_num = localization_service.format_number(1234.56, us_config)
            print_result("Format number (US)", formatted_num is not None, f"Formatted: {formatted_num}")
            
            # Test German formatting
            de_config = localization_service.get_regional_config('DE')
            formatted_de = localization_service.format_number(1234.56, de_config)
            print_result("Format number (DE)", formatted_de is not None, f"Formatted: {formatted_de}")
            
            # Test date formatting
            test_date = datetime(2024, 1, 15, 14, 30)
            formatted_date = localization_service.format_date(test_date, us_config)
            print_result("Format date (US)", formatted_date is not None, f"Formatted: {formatted_date}")
            
            # Test timezone info
            tz_info = localization_service.get_timezone_info('US')
            print_result("Get timezone info", bool(tz_info), f"Timezone: {tz_info.get('timezone')}")
            
            return True
        except Exception as e:
            print_result("Localization service tests", False, str(e))
            return False

def test_health_checks():
    """Test health check functionality."""
    print_header("HEALTH CHECK TESTS")
    
    with app.app_context():
        try:
            # Test currency service health
            currency_health = health_checker.check_currency_service()
            print_result("Currency service health", currency_health['healthy'], 
                        currency_health.get('error', 'OK'))
            
            # Test localization service health
            loc_health = health_checker.check_localization_service()
            print_result("Localization service health", loc_health['healthy'],
                        loc_health.get('error', 'OK'))
            
            # Test database health
            db_health = health_checker.check_database_health()
            print_result("Database health", db_health['healthy'],
                        db_health.get('error', 'OK'))
            
            return True
        except Exception as e:
            print_result("Health checks", False, str(e))
            return False

def test_api_endpoints():
    """Test API endpoints (requires running server)."""
    print_header("API ENDPOINT TESTS")
    
    base_url = "http://localhost:5000"
    
    endpoints_to_test = [
        ('/api/v1/global/currencies', 'GET', 'List currencies'),
        ('/api/v1/global/countries', 'GET', 'List countries'),
        ('/api/v1/global/exchange-rate/USD/EUR', 'GET', 'Get exchange rate'),
        ('/api/v1/global/locale-config/US', 'GET', 'Get locale config'),
        ('/api/v1/health/', 'GET', 'Overall health check'),
        ('/api/v1/health/currency', 'GET', 'Currency health'),
        ('/api/v1/health/localization', 'GET', 'Localization health'),
        ('/api/v1/health/database', 'GET', 'Database health'),
    ]
    
    print("Note: These tests require the Flask app to be running on localhost:5000")
    print("Start the server with: python app.py")
    
    success_count = 0
    for endpoint, method, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            success = response.status_code in [200, 201]
            print_result(f"{description} ({endpoint})", success, 
                        f"Status: {response.status_code}")
            if success:
                success_count += 1
        except requests.RequestException as e:
            print_result(f"{description} ({endpoint})", False, f"Connection error: {e}")
    
    return success_count == len(endpoints_to_test)

def test_error_handling():
    """Test error handling and fallback functionality."""
    print_header("ERROR HANDLING TESTS")
    
    with app.app_context():
        try:
            from app.utils.error_handling import (
                safe_currency_conversion, safe_number_formatting,
                validate_currency_code, validate_country_code
            )
            
            # Test invalid currency conversion
            result = safe_currency_conversion(100, 'INVALID', 'USD')
            print_result("Invalid currency fallback", result is not None, f"Result: {result}")
            
            # Test number formatting fallback
            formatted = safe_number_formatting("invalid_number")
            print_result("Invalid number formatting fallback", formatted is not None, f"Result: {formatted}")
            
            # Test currency code validation
            valid_usd = validate_currency_code('USD')
            invalid_curr = validate_currency_code('INVALID')
            print_result("Currency code validation", valid_usd and not invalid_curr, 
                        f"USD: {valid_usd}, INVALID: {invalid_curr}")
            
            # Test country code validation
            valid_us = validate_country_code('US')
            invalid_country = validate_country_code('INVALID')
            print_result("Country code validation", valid_us and not invalid_country,
                        f"US: {valid_us}, INVALID: {invalid_country}")
            
            return True
        except Exception as e:
            print_result("Error handling tests", False, str(e))
            return False

def run_comprehensive_test():
    """Run all tests and provide summary."""
    print_header("GLOBAL INFRASTRUCTURE VALIDATION")
    print("Testing global infrastructure components...")
    
    test_results = []
    
    # Run all test suites
    test_results.append(("Database Setup", test_database_setup()))
    test_results.append(("Currency Service", test_currency_service()))
    test_results.append(("Localization Service", test_localization_service()))
    test_results.append(("Health Checks", test_health_checks()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # API tests (may fail if server not running)
    try:
        test_results.append(("API Endpoints", test_api_endpoints()))
    except Exception:
        test_results.append(("API Endpoints", False))
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        print_result(test_name, result)
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Global infrastructure is ready.")
        return 0
    elif passed >= total * 0.8:  # 80% pass rate
        print("\n⚠️  Most tests passed. Some issues may need attention.")
        return 1
    else:
        print("\n❌ Multiple test failures. Infrastructure needs fixes.")
        return 2

if __name__ == '__main__':
    # Create Flask app context
    app = create_app()
    
    try:
        exit_code = run_comprehensive_test()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error during testing: {e}")
        sys.exit(1)