"""
Security utilities for sanitization and validation
"""
import bleach
import re
from markupsafe import Markup
from flask import request
from functools import wraps

# Allowed HTML tags and attributes for content sanitization
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'div', 'span'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'div': ['class', 'id'],
    'span': ['class', 'id'],
    'code': ['class'],
    'pre': ['class']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def sanitize_html(content):
    """
    Sanitize HTML content to prevent XSS attacks
    """
    if not content:
        return ""
    
    # Clean the HTML with bleach
    cleaned = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    
    return Markup(cleaned)

def sanitize_input(value):
    """
    Sanitize general input values
    """
    if not value:
        return ""
    
    # Convert to string and strip whitespace
    cleaned = str(value).strip()
    
    # Remove any HTML tags completely for input fields
    cleaned = bleach.clean(cleaned, tags=[], attributes={}, strip=True)
    
    # Additional validation for numeric inputs
    if is_numeric_input(cleaned):
        return cleaned
    
    # For text inputs, limit length and remove potentially dangerous characters
    cleaned = re.sub(r'[<>"\']', '', cleaned)
    return cleaned[:1000]  # Limit length

def is_numeric_input(value):
    """
    Check if input is numeric (int or float)
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def validate_json_input(data):
    """
    Validate and sanitize JSON input data
    """
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    sanitized_data = {}
    errors = []
    
    for key, value in data.items():
        # Sanitize key
        clean_key = sanitize_input(key)
        if not clean_key or len(clean_key) > 50:
            errors.append(f"Invalid field name: {key}")
            continue
            
        # Sanitize value
        if isinstance(value, (int, float)):
            sanitized_data[clean_key] = value
        elif isinstance(value, str):
            clean_value = sanitize_input(value)
            if clean_value:
                sanitized_data[clean_key] = clean_value
        else:
            errors.append(f"Invalid value type for field: {key}")
    
    if errors:
        return False, errors
    
    return True, sanitized_data

def validate_ip_address(ip):
    """
    Basic IP address validation
    """
    if not ip:
        return False
    
    # Basic IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    return False

def rate_limit_key():
    """
    Generate rate limiting key based on IP and user agent
    """
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    
    # Fallback if no IP available
    if not ip or not validate_ip_address(ip):
        ip = 'unknown'
    
    return f"rate_limit:{ip}"

def validate_user_agent(user_agent_string):
    """
    Basic user agent validation to prevent obviously malicious requests
    """
    if not user_agent_string or len(user_agent_string) > 500:
        return False
    
    # Check for common bot patterns that might be malicious
    malicious_patterns = [
        r'<script',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'eval\(',
        r'document\.cookie'
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, user_agent_string, re.IGNORECASE):
            return False
    
    return True

def security_headers(response):
    """
    Add security headers to response
    """
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://www.google-analytics.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # Additional security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

def require_csrf(f):
    """
    Decorator to require CSRF token for API endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_wtf.csrf import validate_csrf
        from flask import request, jsonify
        
        try:
            validate_csrf(request.headers.get('X-CSRFToken', ''))
        except Exception:
            return jsonify({'error': 'CSRF token missing or invalid'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function