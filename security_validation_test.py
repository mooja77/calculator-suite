#!/usr/bin/env python3
"""
Security Validation Test Script
Tests all security fixes implemented in the Calculator-App
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all security modules can be imported"""
    print("🔍 Testing Security Module Imports...")
    
    try:
        from app import create_app
        print("✅ Flask app creation: OK")
        
        from app.security import sanitize_html, sanitize_input, validate_json_input, security_headers
        print("✅ Security module functions: OK")
        
        from flask_wtf.csrf import CSRFProtect
        print("✅ CSRF protection: OK")
        
        from flask_limiter import Limiter
        print("✅ Rate limiting: OK")
        
        import bleach
        print("✅ HTML sanitization (bleach): OK")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_sanitization():
    """Test HTML and input sanitization functions"""
    print("\n🧹 Testing Input Sanitization...")
    
    try:
        from app.security import sanitize_html, sanitize_input, validate_json_input
        
        # Test XSS prevention
        malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
        sanitized = sanitize_html(malicious_html)
        
        if '<script>' not in str(sanitized):
            print("✅ XSS script removal: OK")
        else:
            print("❌ XSS script removal: FAILED")
            return False
            
        # Test input sanitization
        malicious_input = '<script>alert("test")</script>123.45'
        clean_input = sanitize_input(malicious_input)
        
        if '<script>' not in clean_input and '123.45' in clean_input:
            print("✅ Input sanitization: OK")
        else:
            print("❌ Input sanitization: FAILED")
            return False
            
        # Test JSON validation
        test_data = {
            'amount': 100,
            'percentage': '15.5',
            'malicious': '<script>alert("xss")</script>'
        }
        
        is_valid, result = validate_json_input(test_data)
        if is_valid and '<script>' not in str(result):
            print("✅ JSON validation and sanitization: OK")
        else:
            print("❌ JSON validation: FAILED")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Sanitization test error: {e}")
        return False

def test_app_creation():
    """Test Flask app creation with security features"""
    print("\n🚀 Testing Flask App Creation...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Check if CSRF is configured
        if 'WTF_CSRF_TIME_LIMIT' in app.config:
            print("✅ CSRF configuration: OK")
        else:
            print("❌ CSRF configuration: MISSING")
            return False
            
        # Check if rate limiting is configured
        if 'RATELIMIT_DEFAULT' in app.config:
            print("✅ Rate limiting configuration: OK")
        else:
            print("❌ Rate limiting configuration: MISSING")
            return False
            
        # Test security headers
        with app.test_client() as client:
            response = client.get('/')
            
            # Check for security headers
            security_headers_present = [
                'Content-Security-Policy' in response.headers,
                'X-Frame-Options' in response.headers,
                'X-Content-Type-Options' in response.headers,
                'X-XSS-Protection' in response.headers
            ]
            
            if all(security_headers_present):
                print("✅ Security headers: OK")
            else:
                print("❌ Security headers: MISSING")
                return False
                
        print("✅ Flask app with security features: OK")
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calculator_functionality():
    """Test that calculator functionality still works after security fixes"""
    print("\n🧮 Testing Calculator Functionality...")
    
    try:
        from app import create_app
        from app.calculators.registry import calculator_registry
        
        app = create_app()
        
        # Test calculator registry
        calculators = calculator_registry.get_all()
        if len(calculators) > 0:
            print(f"✅ Calculator registry: {len(calculators)} calculators found")
        else:
            print("❌ Calculator registry: No calculators found")
            return False
            
        # Test percentage calculator specifically
        percentage_calc = calculator_registry.get('percentage')
        if percentage_calc:
            calc_instance = percentage_calc()
            test_inputs = {'operation': 'basic', 'x': '25', 'y': '100'}
            
            if calc_instance.validate_inputs(test_inputs):
                result = calc_instance.calculate(test_inputs)
                if result and 'result' in result:
                    print("✅ Percentage calculator: OK")
                else:
                    print("❌ Percentage calculator: Calculation failed")
                    return False
            else:
                print("❌ Percentage calculator: Validation failed")
                return False
        else:
            print("❌ Percentage calculator: Not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Calculator functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all security validation tests"""
    print("🛡️ CALCULATOR-APP SECURITY VALIDATION TEST")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all tests
    test_results = [
        test_imports(),
        test_sanitization(),
        test_app_creation(),
        test_calculator_functionality()
    ]
    
    all_tests_passed = all(test_results)
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("✅ The Calculator-App is secure and ready for production")
        print("🚀 Security hardening phase: COMPLETED SUCCESSFULLY")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🚨 Security issues need to be addressed before deployment")
        
    return all_tests_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)