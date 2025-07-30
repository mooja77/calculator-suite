"""
Localization middleware for automatic region detection and context setup.
"""
from flask import request, g, session
import uuid
import logging

from app.services.localization import localization_service

logger = logging.getLogger(__name__)

class LocalizationMiddleware:
    """Middleware to handle automatic localization context setup."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app."""
        app.before_request(self.before_request)
        app.context_processor(self.inject_locale_context)
    
    def before_request(self):
        """Set up localization context before each request."""
        try:
            # Ensure session has an ID for preferences
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            # Get client IP for geo-detection
            client_ip = self.get_client_ip()
            
            # Detect country from IP if not already set
            detected_country = None
            if client_ip:
                detected_country = localization_service.detect_country_from_ip(client_ip)
            
            # Get user preferences or detect automatically
            user_prefs = localization_service.get_user_preferences(session['session_id'])
            
            # Determine active country (preference > detection > default)
            active_country = (
                user_prefs.get('country_code') or 
                detected_country or 
                'US'
            )
            
            # Get regional configuration
            regional_config = localization_service.get_regional_config(active_country)
            
            # Merge user preferences with regional defaults
            locale_config = regional_config.copy()
            locale_config.update({k: v for k, v in user_prefs.items() if v is not None})
            
            # Store in Flask's g object for request context
            g.locale_config = locale_config
            g.detected_country = detected_country
            g.user_preferences = user_prefs
            g.session_id = session['session_id']
            
            # Store commonly used values for easy access
            g.currency_code = locale_config.get('currency_code', 'USD')
            g.country_code = locale_config.get('country_code', 'US')
            g.language_code = locale_config.get('language_code', 'en')
            g.decimal_separator = locale_config.get('decimal_separator', '.')
            g.thousands_separator = locale_config.get('thousands_separator', ',')
            g.date_format = locale_config.get('date_format', 'MM/DD/YYYY')
            
        except Exception as e:
            logger.error(f"Error in localization middleware: {e}")
            # Set fallback values
            self.set_fallback_context()
    
    def inject_locale_context(self):
        """Inject localization context into templates."""
        return {
            'locale_config': getattr(g, 'locale_config', {}),
            'currency_code': getattr(g, 'currency_code', 'USD'),
            'country_code': getattr(g, 'country_code', 'US'),
            'language_code': getattr(g, 'language_code', 'en'),
            'decimal_separator': getattr(g, 'decimal_separator', '.'),
            'thousands_separator': getattr(g, 'thousands_separator', ','),
            'date_format': getattr(g, 'date_format', 'MM/DD/YYYY'),
            'detected_country': getattr(g, 'detected_country', None)
        }
    
    def get_client_ip(self):
        """Get client IP address from request headers."""
        # Check for forwarded headers (load balancers, proxies)
        if request.headers.get('X-Forwarded-For'):
            # Take the first IP in the chain
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
            ip = request.headers.get('CF-Connecting-IP')
        else:
            ip = request.remote_addr
        
        return ip
    
    def set_fallback_context(self):
        """Set fallback localization context."""
        fallback_config = localization_service.get_regional_config('US')
        
        g.locale_config = fallback_config
        g.detected_country = None
        g.user_preferences = {}
        g.session_id = session.get('session_id', str(uuid.uuid4()))
        g.currency_code = 'USD'
        g.country_code = 'US'
        g.language_code = 'en'
        g.decimal_separator = '.'
        g.thousands_separator = ','
        g.date_format = 'MM/DD/YYYY'

# Create global instance
localization_middleware = LocalizationMiddleware()