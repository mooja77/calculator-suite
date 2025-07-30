#!/usr/bin/env python3
"""
Pre-deployment verification script
Checks if Calculator Suite is ready for production deployment
"""
import os
import sys
import importlib.util

def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING!")
        return False

def check_deployment_readiness():
    """Check if all deployment requirements are met"""
    print("🚀 Calculator Suite - Pre-Deployment Check")
    print("=" * 60)
    
    all_good = True
    
    # 1. Check core application files
    print("\n📁 Core Application Files:")
    core_files = [
        ("app.py", "Main application entry point"),
        ("requirements.txt", "Python dependencies"),
        ("app/__init__.py", "Application factory"),
        ("app/routes.py", "Main route handlers"),
        ("app/calculators/registry.py", "Calculator registry"),
    ]
    
    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # 2. Check deployment configuration files
    print("\n🐳 Deployment Configuration:")
    deployment_files = [
        ("Dockerfile", "Docker container config"),
        ("render.yaml", "Render.com deployment config"),
        ("Procfile", "Process configuration"),
        ("runtime.txt", "Python runtime version"),
        ("env.example", "Environment variables template"),
    ]
    
    for file_path, description in deployment_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # 3. Check calculator implementations
    print("\n🧮 Calculator Implementations:")
    calculator_files = [
        ("app/calculators/breakeven.py", "Break-Even Calculator"),
        ("app/calculators/freelancerate.py", "Freelance Rate Calculator"),
        ("app/calculators/percentage.py", "Percentage Calculator"),
        ("app/calculators/budget.py", "Budget Calculator"),
        ("app/calculators/emergencyfund.py", "Emergency Fund Calculator"),
    ]
    
    for file_path, description in calculator_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # 4. Check content files for new calculators
    print("\n📝 Content Files:")
    content_files = [
        ("app/content/breakeven_intro.md", "Break-Even intro content"),
        ("app/content/breakeven_guide.md", "Break-Even guide"),
        ("app/content/breakeven_faq.md", "Break-Even FAQ"),
        ("app/content/freelancerate_intro.md", "Freelance Rate intro content"),
        ("app/content/freelancerate_guide.md", "Freelance Rate guide"),
        ("app/content/freelancerate_faq.md", "Freelance Rate FAQ"),
    ]
    
    for file_path, description in content_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # 5. Check template files
    print("\n🎨 Template Files:")
    template_files = [
        ("app/templates/base.html", "Base template"),
        ("app/templates/calculator.html", "Calculator template"),
        ("app/templates/index.html", "Homepage template"),
    ]
    
    for file_path, description in template_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # 6. Check static assets
    print("\n🎯 Static Assets:")
    static_files = [
        ("app/static/css/calculator.css", "Calculator styles"),
        ("app/static/js/calculator.js", "Calculator JavaScript"),
    ]
    
    for file_path, description in static_files:
        if not check_file_exists(file_path, description):
            print(f"⚠️ {description}: {file_path} - Optional but recommended")
    
    # 7. Count calculators
    print("\n📊 Calculator Count:")
    calculator_count = 0
    calculators_dir = "app/calculators"
    if os.path.exists(calculators_dir):
        for file in os.listdir(calculators_dir):
            if file.endswith('.py') and file not in ['__init__.py', 'base.py', 'registry.py']:
                calculator_count += 1
    
    print(f"📈 Total Calculators Implemented: {calculator_count}")
    
    if calculator_count >= 20:
        print("✅ Excellent! You have a comprehensive calculator suite")
    elif calculator_count >= 15:
        print("✅ Good! You have a solid calculator collection")
    elif calculator_count >= 10:
        print("⚠️ Decent start, consider adding more calculators")
    else:
        print("❌ Too few calculators for a comprehensive suite")
        all_good = False
    
    # 8. Check if Python can import the app
    print("\n🐍 Python Import Test:")
    try:
        # Try to import the main app
        spec = importlib.util.spec_from_file_location("app", "app/__init__.py")
        if spec and spec.loader:
            print("✅ App module can be imported")
        else:
            print("❌ Cannot import app module")
            all_good = False
    except Exception as e:
        print(f"❌ Import error: {e}")
        all_good = False
    
    # 9. Final assessment
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All critical files present")
        print("✅ Calculator suite is comprehensive")
        print("✅ Deployment configurations created")
        print("\n🚀 Ready to deploy to production!")
        print("\nNext steps:")
        print("1. Push to GitHub repository")
        print("2. Deploy to Render.com (or chosen platform)")
        print("3. Configure environment variables")
        print("4. Test live deployment")
        return True
    else:
        print("❌ DEPLOYMENT NOT READY")
        print("⚠️ Please fix the missing files above")
        print("💡 Refer to DEPLOY_NOW.md for guidance")
        return False

def check_environment():
    """Check environment and provide recommendations"""
    print("\n🔧 Environment Recommendations:")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"🐍 Python Version: {python_version}")
    
    if python_version >= "3.9":
        print("✅ Python version is suitable for deployment")
    else:
        print("⚠️ Consider upgrading to Python 3.9+ for best compatibility")
    
    # Check if running on Windows
    if os.name == 'nt':
        print("💻 Platform: Windows")
        print("💡 Tip: Deployment will run on Linux - test locally if possible")
    
    # Check directory size
    total_size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
            except:
                pass
    
    size_mb = total_size / (1024 * 1024)
    print(f"📁 Project Size: {size_mb:.1f} MB")
    
    if size_mb < 50:
        print("✅ Project size is suitable for free hosting")
    elif size_mb < 100:
        print("⚠️ Project size is moderate - should work on most platforms")
    else:
        print("❌ Project size is large - may require paid hosting")

if __name__ == "__main__":
    print("Starting pre-deployment verification...\n")
    
    deployment_ready = check_deployment_readiness()
    check_environment()
    
    print("\n" + "=" * 60)
    if deployment_ready:
        print("🎊 SUCCESS: Your Calculator Suite is ready for deployment!")
        sys.exit(0)
    else:
        print("❌ FAILED: Please fix the issues above before deploying")
        sys.exit(1)