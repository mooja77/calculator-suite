"""
Enhanced Internationalization Middleware
Integrates with existing localization middleware for comprehensive i18n support
"""
from flask import request, g, session, redirect, url_for
import uuid
import logging
from urllib.parse import urlparse

from app.services.i18n import i18n_service
from app.services.localization import localization_service

logger = logging.getLogger(__name__)

class I18nMiddleware:
    """Enhanced middleware for internationalization with URL routing support."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app."""
        app.before_request(self.before_request)
        app.context_processor(self.inject_i18n_context)
        app.url_defaults(self.add_language_code)
        app.url_value_preprocessor(self.pull_lang_code)
    
    def before_request(self):
        """Enhanced before_request that integrates with existing localization."""
        try:
            # Ensure session has an ID
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            # Extract language from URL or detect
            url_language = getattr(g, 'language_code', None)
            detected_language = self.detect_language()
            
            # Determine active language
            active_language = url_language or detected_language
            
            # Validate and set language
            if not i18n_service._is_language_supported(active_language):
                active_language = i18n_service.fallback_language
            
            # Store language in session and context
            session['language'] = active_language
            g.language_code = active_language
            g.language_info = i18n_service.get_language_info(active_language)
            g.text_direction = g.language_info['direction']
            g.is_rtl = g.language_info['is_rtl']
            
            # Load translations
            g.translations = i18n_service._get_translations(active_language)
            
            # Integrate with existing localization
            self.integrate_with_localization()
            
            # Handle URL redirects for SEO
            self.handle_url_redirects()
            
        except Exception as e:
            logger.error(f"Error in i18n middleware: {e}")
            self.set_fallback_context()
    
    def detect_language(self):
        """Detect user's preferred language from multiple sources."""
        # 1. URL parameter (handled by URL routing)
        url_lang = getattr(g, 'language_code', None)
        if url_lang and i18n_service._is_language_supported(url_lang):
            return url_lang
        
        # 2. Session preference
        session_lang = session.get('language')
        if session_lang and i18n_service._is_language_supported(session_lang):
            return session_lang
        
        # 3. Browser Accept-Language header
        if request and request.headers.get('Accept-Language'):
            browser_langs = self.parse_accept_language(request.headers.get('Accept-Language'))
            for lang in browser_langs:
                if i18n_service._is_language_supported(lang):
                    return lang
        
        # 4. Regional detection (from existing localization service)
        if hasattr(g, 'country_code') and g.country_code:
            region_lang = self.get_language_for_region(g.country_code)
            if region_lang and i18n_service._is_language_supported(region_lang):
                return region_lang
        
        # 5. Default fallback
        return i18n_service.fallback_language
    
    def parse_accept_language(self, accept_language):
        """Parse Accept-Language header and return ordered list of languages."""
        try:
            languages = []
            for item in accept_language.split(','):
                if ';' in item:
                    lang, priority = item.split(';', 1)
                    try:
                        q = float(priority.split('=')[1])
                    except (IndexError, ValueError):
                        q = 1.0
                else:
                    lang, q = item, 1.0
                
                # Extract base language code
                lang_code = lang.strip().split('-')[0].lower()
                languages.append((lang_code, q))
            
            # Sort by priority (q value)
            languages.sort(key=lambda x: x[1], reverse=True)
            return [lang for lang, _ in languages]
            
        except Exception as e:
            logger.error(f"Error parsing Accept-Language header: {e}")
            return []
    
    def get_language_for_region(self, country_code):
        """Get default language for a country/region."""
        region_language_map = {
            'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en',
            'FR': 'fr', 'DE': 'de', 'AT': 'de', 'CH': 'de',
            'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es',
            'SA': 'ar', 'AE': 'ar', 'EG': 'ar', 'MA': 'ar'
        }
        return region_language_map.get(country_code.upper())
    
    def integrate_with_localization(self):
        """Integrate with existing localization service."""
        try:
            # Get client IP and detect country (from existing middleware)
            client_ip = self.get_client_ip()
            detected_country = None
            
            if client_ip:
                detected_country = localization_service.detect_country_from_ip(client_ip)
            
            # Get user preferences
            user_prefs = localization_service.get_user_preferences(session['session_id'])
            
            # Determine active country (preference > detection > default)
            active_country = (
                user_prefs.get('country_code') or 
                detected_country or 
                'US'
            )
            
            # Get regional configuration
            regional_config = localization_service.get_regional_config(active_country)
            
            # Update regional config to match selected language
            language_regional_map = {
                'fr': {'country_code': 'FR', 'currency_code': 'EUR'},
                'de': {'country_code': 'DE', 'currency_code': 'EUR'},
                'es': {'country_code': 'ES', 'currency_code': 'EUR'},
                'ar': {'country_code': 'SA', 'currency_code': 'SAR'}
            }
            
            if g.language_code in language_regional_map:
                regional_config.update(language_regional_map[g.language_code])
            
            # Merge with user preferences
            locale_config = regional_config.copy()
            locale_config.update({k: v for k, v in user_prefs.items() if v is not None})
            locale_config['language_code'] = g.language_code
            
            # Store in g for template access
            g.locale_config = locale_config
            g.detected_country = detected_country
            g.user_preferences = user_prefs
            g.session_id = session['session_id']
            
            # Store commonly used values
            g.currency_code = locale_config.get('currency_code', 'USD')
            g.country_code = locale_config.get('country_code', 'US')
            g.decimal_separator = locale_config.get('decimal_separator', '.')
            g.thousands_separator = locale_config.get('thousands_separator', ',')
            g.date_format = locale_config.get('date_format', 'MM/DD/YYYY')
            
        except Exception as e:
            logger.error(f"Error integrating with localization: {e}")
    
    def handle_url_redirects(self):
        """Handle URL redirects for SEO-friendly language URLs."""
        # Skip for API endpoints and static files
        if (request.path.startswith('/api/') or 
            request.path.startswith('/static/') or
            request.method != 'GET'):
            return
        
        # Check if URL already has language prefix
        path_parts = request.path.strip('/').split('/')
        
        if not path_parts or path_parts[0] == '':
            # Root path - redirect to language-specific URL
            language = g.language_code
            if language != 'en':  # Only redirect non-English
                return redirect(f'/{language}' + request.path, code=302)
        
        elif path_parts[0] in i18n_service.SUPPORTED_LANGUAGES:
            # URL already has language prefix
            url_lang = path_parts[0]
            if url_lang != g.language_code and request.args.get('lang') != url_lang:
                # Language mismatch - update session but don't redirect
                session['language'] = url_lang
                g.language_code = url_lang
    
    def get_client_ip(self):
        """Get client IP address from request headers."""
        # Check for forwarded headers (load balancers, proxies)
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        elif request.headers.get('CF-Connecting-IP'):  # Cloudflare
            ip = request.headers.get('CF-Connecting-IP')
        else:
            ip = request.remote_addr
        
        return ip
    
    def inject_i18n_context(self):
        """Inject i18n context into templates."""
        return {
            'language_code': getattr(g, 'language_code', 'en'),
            'language_info': getattr(g, 'language_info', {}),
            'text_direction': getattr(g, 'text_direction', 'ltr'),
            'is_rtl': getattr(g, 'is_rtl', False),
            'translations': getattr(g, 'translations', {}),
            'available_languages': i18n_service.get_available_languages(),
            'current_language_name': getattr(g, 'language_info', {}).get('name', 'English')
        }
    
    def add_language_code(self, endpoint, values):
        """Add language code to URL generation."""
        if 'language_code' not in values and hasattr(g, 'language_code'):
            if g.language_code != 'en':  # Don't add 'en' to URLs
                values['language_code'] = g.language_code
    
    def pull_lang_code(self, endpoint, values):
        """Extract language code from URL."""
        if values is not None:
            g.language_code = values.pop('language_code', 'en')
    
    def set_fallback_context(self):
        """Set fallback i18n context."""
        g.language_code = 'en'
        g.language_info = i18n_service.get_language_info('en')
        g.text_direction = 'ltr'
        g.is_rtl = False
        g.translations = i18n_service._get_translations('en')

# Global instance
i18n_middleware = I18nMiddleware()