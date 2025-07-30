#!/usr/bin/env python3
"""Quick test to verify security implementation"""

print("Testing security implementation...")

# Test 1: Can we import the security module?
try:
    from app.security import sanitize_html
    print("✅ Security module imported successfully")
except Exception as e:
    print(f"❌ Failed to import security module: {e}")
    exit(1)

# Test 2: Does sanitization work?
try:
    malicious = '<script>alert("xss")</script><p>Safe content</p>'
    clean = sanitize_html(malicious)
    if '<script>' not in str(clean):
        print("✅ XSS sanitization working")
    else:
        print("❌ XSS sanitization failed")
except Exception as e:
    print(f"❌ Sanitization test failed: {e}")

# Test 3: Can we create the Flask app?
try:
    from app import create_app
    app = create_app()
    print("✅ Flask app created with security features")
except Exception as e:
    print(f"❌ Flask app creation failed: {e}")

print("Security test complete!")