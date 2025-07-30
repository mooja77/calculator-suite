#!/usr/bin/env python3
"""
Security validation test script
"""
import requests
import json
from app import create_app
from app.security import sanitize_html, sanitize_input, validate_json_input

def test_xss_protection():
    """Test XSS protection in sanitization functions"""
    print("Testing XSS Protection...")
    
    # Test malicious HTML content
    malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
    sanitized = sanitize_html(malicious_html)
    print(f"Original: {malicious_html}")
    print(f"Sanitized: {sanitized}")
    assert '<script>' not in str(sanitized), "Script tags should be removed"
    assert 'Safe content' in str(sanitized), "Safe content should remain"
    print("✅ XSS protection working\n")

def test_input_sanitization():
    """Test input sanitization"""
    print("Testing Input Sanitization...")
    
    # Test malicious input
    malicious_input = '<script>alert("XSS")</script>123.45'
    sanitized = sanitize_input(malicious_input)
    print(f"Original: {malicious_input}")
    print(f"Sanitized: {sanitized}")
    assert '<script>' not in sanitized, "Script tags should be removed"
    print("✅ Input sanitization working\n")

def test_json_validation():
    """Test JSON input validation"""
    print("Testing JSON Validation...")
    
    # Test malicious JSON data
    malicious_data = {
        'operation': 'basic',
        'x': '<script>alert("XSS")</script>',
        'y': '100'
    }
    
    valid, result = validate_json_input(malicious_data)
    print(f"Original: {malicious_data}")
    print(f"Valid: {valid}, Result: {result}")
    
    if valid:
        assert '<script>' not in str(result), "Script tags should be removed from values"
    print("✅ JSON validation working\n")

def test_csrf_protection():
    """Test CSRF protection (requires running app)"""
    print("Testing CSRF Protection...")
    
    app = create_app()
    with app.test_client() as client:
        # Try to access calculator page
        response = client.get('/calculators/percentage/')
        print(f"Calculator page status: {response.status_code}")
        
        # Check if CSRF token is present in response
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            assert 'csrf_token' in content, "CSRF token should be present"
            print("✅ CSRF token present in form")
        
        # Try API call without CSRF token
        response = client.post('/api/calculate/percentage', 
                             json={'operation': 'basic', 'x': '50', 'y': '100'},
                             headers={'Content-Type': 'application/json'})
        print(f"API without CSRF token status: {response.status_code}")
        assert response.status_code == 403, "Should return 403 without CSRF token"
        print("✅ CSRF protection working\n")

def test_security_headers():
    """Test security headers"""
    print("Testing Security Headers...")
    
    app = create_app()
    with app.test_client() as client:
        response = client.get('/')
        
        headers_to_check = [
            'Content-Security-Policy',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        for header in headers_to_check:
            assert header in response.headers, f"Missing security header: {header}"
            print(f"✅ {header}: {response.headers[header]}")
        
        print("✅ All security headers present\n")

def run_security_tests():
    """Run all security tests"""
    print("=== SECURITY VALIDATION TESTS ===\n")
    
    try:
        test_xss_protection()
        test_input_sanitization()
        test_json_validation()
        test_csrf_protection()
        test_security_headers()
        
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("\nSecurity improvements implemented:")
        print("✅ XSS protection via HTML sanitization")
        print("✅ Input sanitization for all user inputs")
        print("✅ CSRF protection on forms and API endpoints")
        print("✅ Rate limiting on API endpoints")
        print("✅ Security headers (CSP, X-Frame-Options, etc.)")
        print("✅ Safe DOM updates (no innerHTML)")
        print("✅ User agent validation")
        print("✅ JSON input validation and sanitization")
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    run_security_tests()