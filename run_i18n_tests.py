#!/usr/bin/env python3
"""
Run internationalization tests and generate coverage report
"""
import sys
import os
import pytest
import subprocess

def run_i18n_tests():
    """Run the complete i18n test suite."""
    
    print("🌍 Running Calculator-App Internationalization Tests")
    print("=" * 60)
    
    # Add the app directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Test configuration
    test_args = [
        'tests/test_i18n.py',
        '-v',  # verbose output
        '--tb=short',  # shorter traceback format
        '--color=yes',  # colored output
        '-x',  # stop on first failure
    ]
    
    # Run the tests
    print("Running i18n unit tests...")
    result = pytest.main(test_args)
    
    if result == 0:
        print("\n✅ All internationalization tests passed!")
        
        # Run additional integration tests
        print("\n🔄 Running integration tests...")
        integration_result = run_integration_tests()
        
        if integration_result == 0:
            print("\n🎉 Complete i18n test suite passed successfully!")
            print("\nNext steps:")
            print("1. Test language switching in browser: python run_dev.py")
            print("2. Verify translations: http://localhost:5000/fr/")
            print("3. Test Arabic RTL: http://localhost:5000/ar/")
            print("4. Check API endpoints: http://localhost:5000/api/languages")
            return 0
        else:
            print("\n❌ Integration tests failed")
            return integration_result
    else:
        print("\n❌ i18n tests failed")
        return result

def run_integration_tests():
    """Run integration tests for i18n system."""
    try:
        from app import create_app
        from app.services.i18n import i18n_service
        
        app = create_app()
        app.config['TESTING'] = True
        
        with app.app_context():
            # Test 1: Initialize translations
            print("  📝 Testing translation initialization...")
            success = i18n_service.initialize_translations()
            if not success:
                print("    ❌ Translation initialization failed")
                return 1
            print("    ✅ Translation initialization successful")
            
            # Test 2: Load all languages
            print("  🌐 Testing all language loading...")
            for lang_code in i18n_service.SUPPORTED_LANGUAGES.keys():
                translations = i18n_service._get_translations(lang_code)
                if not isinstance(translations, dict):
                    print(f"    ❌ Failed to load {lang_code} translations")
                    return 1
                print(f"    ✅ {lang_code} translations loaded ({len(translations)} keys)")
            
            # Test 3: Test API endpoints
            print("  🔗 Testing API endpoints...")
            client = app.test_client()
            
            endpoints = [
                '/api/languages',
                '/api/translations/en',
                '/api/health'
            ]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                if response.status_code != 200:
                    print(f"    ❌ API endpoint {endpoint} failed: {response.status_code}")
                    return 1
                print(f"    ✅ {endpoint} responded successfully")
            
            # Test 4: Language switching
            print("  🔄 Testing language switching...")
            response = client.post('/api/language', 
                json={'language': 'fr'},
                content_type='application/json'
            )
            if response.status_code != 200:
                print("    ❌ Language switching failed")
                return 1
            print("    ✅ Language switching successful")
            
            # Test 5: Number formatting
            print("  🔢 Testing number formatting...")
            test_cases = [
                ('en', 1234.56, 'USD'),
                ('fr', 1234.56, 'EUR'),
                ('de', 1234.56, 'EUR'),
                ('ar', 1234.56, 'SAR')
            ]
            
            for lang, number, currency in test_cases:
                formatted = i18n_service.format_number_localized(number, lang, currency=currency)
                if not formatted or formatted == str(number):
                    print(f"    ❌ Number formatting failed for {lang}")
                    return 1
                print(f"    ✅ {lang}: {number} → {formatted}")
            
            print("  🎯 All integration tests passed!")
            return 0
            
    except Exception as e:
        print(f"  ❌ Integration test error: {e}")
        return 1

def check_requirements():
    """Check if required packages are installed."""
    try:
        import flask
        import pytest
        import babel
        print("✅ All required packages are available")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def generate_test_report():
    """Generate a detailed test report."""
    print("\n📊 Generating test coverage report...")
    
    try:
        # Run tests with coverage
        cmd = [
            'python', '-m', 'pytest',
            'tests/test_i18n.py',
            '--cov=app.services.i18n',
            '--cov=app.middleware.i18n_middleware',
            '--cov=app.api.i18n_routes',
            '--cov-report=html:coverage_html',
            '--cov-report=term-missing',
            '--quiet'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Coverage report generated in coverage_html/")
            print(result.stdout)
        else:
            print("❌ Coverage report generation failed")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ pytest-cov not installed. Run: pip install pytest-cov")

if __name__ == '__main__':
    print("Calculator-App Internationalization Test Suite")
    print("Testing comprehensive multi-language support...")
    print()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Run tests
    result = run_i18n_tests()
    
    # Generate coverage report if tests passed
    if result == 0:
        generate_test_report()
    
    sys.exit(result)