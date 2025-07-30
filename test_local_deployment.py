#!/usr/bin/env python3
"""
Local deployment test - Verify app starts correctly before cloud deployment
"""
import subprocess
import time
import requests
import sys
import os

def test_local_deployment():
    """Test if the application runs correctly locally"""
    print("🧪 Testing Local Deployment...")
    print("=" * 60)
    
    # Start the Flask app in a subprocess
    print("\n📦 Starting Flask application...")
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['SECRET_KEY'] = 'test-secret-key-for-local-testing'
    
    try:
        # Start the app
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start
        print("⏳ Waiting for app to start...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ App failed to start!")
            print(f"Error: {stderr}")
            return False
        
        print("✅ Flask app started successfully")
        
        # Test endpoints
        print("\n🔍 Testing endpoints...")
        
        tests = [
            ("Homepage", "http://localhost:5000/"),
            ("Break-Even Calculator", "http://localhost:5000/calculators/breakeven/"),
            ("Freelance Rate Calculator", "http://localhost:5000/calculators/freelancerate/"),
            ("Percentage Calculator", "http://localhost:5000/calculators/percentage/"),
        ]
        
        all_passed = True
        
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {test_name}: OK (Status: {response.status_code})")
                else:
                    print(f"❌ {test_name}: Failed (Status: {response.status_code})")
                    all_passed = False
            except requests.exceptions.ConnectionError:
                print(f"❌ {test_name}: Connection failed - app may not be running")
                all_passed = False
            except Exception as e:
                print(f"❌ {test_name}: Error - {e}")
                all_passed = False
        
        # Terminate the process
        process.terminate()
        process.wait()
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def check_requirements():
    """Check if all requirements are installed"""
    print("\n📋 Checking Python dependencies...")
    
    try:
        import flask
        print("✅ Flask installed")
    except ImportError:
        print("❌ Flask not installed - run: pip install -r requirements.txt")
        return False
    
    try:
        import gunicorn
        print("✅ Gunicorn installed (for production)")
    except ImportError:
        print("⚠️ Gunicorn not installed - needed for production deployment")
    
    return True

def main():
    print("🚀 Calculator Suite - Local Deployment Test")
    print("This test verifies your app is ready for cloud deployment")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing dependencies first")
        return False
    
    # Run local test
    if test_local_deployment():
        print("\n" + "=" * 60)
        print("✅ LOCAL TEST PASSED!")
        print("Your Calculator Suite is ready for deployment")
        print("\nNext steps:")
        print("1. Push to GitHub: setup_github.bat")
        print("2. Deploy to Render.com")
        print("3. Monitor your live application")
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ LOCAL TEST FAILED")
        print("Please fix the issues above before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)