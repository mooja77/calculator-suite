"""
Template helpers for internationalization
Provides Jinja2 functions for translation and formatting
"""
from flask import g
from app.services.i18n import i18n_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def register_i18n_helpers(app):
    """Register i18n template helpers with Flask app."""
    
    @app.template_filter('translate')
    def translate_filter(key, **kwargs):
        """Translate a key using current language."""
        try:
            return i18n_service.translate(key, g.language_code, **kwargs)
        except Exception as e:
            logger.error(f"Translation error for key {key}: {e}")
            return key
    
    @app.template_filter('format_number')
    def format_number_filter(number, currency=None):
        """Format number according to current language settings."""
        try:
            return i18n_service.format_number_localized(
                number, 
                g.language_code, 
                currency=currency
            )
        except Exception as e:
            logger.error(f"Number formatting error: {e}")
            return str(number)
    
    @app.template_filter('format_currency')
    def format_currency_filter(amount, currency_code=None):
        """Format currency amount according to language settings."""
        try:
            if not currency_code:
                currency_code = getattr(g, 'currency_code', 'USD')
            
            return i18n_service.format_number_localized(
                amount, 
                g.language_code, 
                currency=currency_code
            )
        except Exception as e:
            logger.error(f"Currency formatting error: {e}")
            return f"{currency_code} {amount}"
    
    @app.template_filter('format_percentage')
    def format_percentage_filter(value, decimals=2):
        """Format percentage value."""
        try:
            formatted_number = i18n_service.format_number_localized(
                value, 
                g.language_code
            )
            return f"{formatted_number}%"
        except Exception as e:
            logger.error(f"Percentage formatting error: {e}")
            return f"{value}%"
    
    @app.template_global()
    def get_translation(key, language=None, **kwargs):
        """Get translation for a key."""
        try:
            if not language:
                language = getattr(g, 'language_code', 'en')
            return i18n_service.translate(key, language, **kwargs)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return key
    
    @app.template_global()
    def get_language_direction():
        """Get current language direction (ltr/rtl)."""
        return getattr(g, 'text_direction', 'ltr')
    
    @app.template_global()
    def is_rtl():
        """Check if current language is RTL."""
        return getattr(g, 'is_rtl', False)
    
    @app.template_global()
    def get_language_name(language_code=None):
        """Get native name of language."""
        try:
            if not language_code:
                language_code = getattr(g, 'language_code', 'en')
            
            lang_info = i18n_service.get_language_info(language_code)
            return lang_info.get('native_name', 'English')
        except Exception as e:
            logger.error(f"Error getting language name: {e}")
            return 'English'
    
    @app.template_global()
    def get_available_languages():
        """Get list of available languages for language switcher."""
        try:
            return i18n_service.get_available_languages()
        except Exception as e:
            logger.error(f"Error getting available languages: {e}")
            return []
    
    @app.template_global()
    def localize_url(endpoint, **values):
        """Generate localized URL."""
        from flask import url_for
        try:
            # Add current language code if not provided
            if 'language_code' not in values:
                values['language_code'] = getattr(g, 'language_code', 'en')
            
            return url_for(endpoint, **values)
        except Exception as e:
            logger.error(f"URL localization error: {e}")
            return '#'
    
    @app.template_global()
    def alternate_language_urls(endpoint, **values):
        """Generate alternate language URLs for SEO."""
        try:
            urls = {}
            for lang_code in i18n_service.SUPPORTED_LANGUAGES.keys():
                try:
                    values_copy = values.copy()
                    values_copy['language_code'] = lang_code
                    urls[lang_code] = url_for(endpoint, **values_copy)
                except Exception:
                    continue
            return urls
        except Exception as e:
            logger.error(f"Error generating alternate URLs: {e}")
            return {}
    
    @app.template_global()
    def get_islamic_terms(language='ar'):
        """Get Islamic finance terms for templates."""
        try:
            return i18n_service.get_islamic_finance_terms(language)
        except Exception as e:
            logger.error(f"Error getting Islamic terms: {e}")
            return {}
    
    @app.template_global()
    def format_input_value(value, input_type='text'):
        """Format input value according to current locale."""
        try:
            if input_type == 'number' and isinstance(value, (int, float)):
                # For number inputs, keep standard format for HTML
                return str(value)
            elif input_type == 'currency' and isinstance(value, (int, float)):
                return i18n_service.format_number_localized(value, g.language_code)
            else:
                return str(value) if value is not None else ''
        except Exception as e:
            logger.error(f"Input formatting error: {e}")
            return str(value) if value is not None else ''
    
    @app.template_global()
    def get_locale_config():
        """Get current locale configuration."""
        return getattr(g, 'locale_config', {})
    
    @app.template_global()
    def pluralize(count, singular, plural=None):
        """Simple pluralization helper."""
        try:
            if plural is None:
                plural = singular + 's'
            
            # Get pluralization rules for current language
            # This is simplified - real implementation would need full ICU rules
            language_code = getattr(g, 'language_code', 'en')
            
            if language_code == 'ar':
                # Arabic has complex plural rules
                if count == 0:
                    return get_translation('common.no') + ' ' + plural
                elif count == 1:
                    return singular
                elif count == 2:
                    return singular + 'ان'  # dual form
                elif count <= 10:
                    return plural
                else:
                    return singular
            else:
                # Simple English-style plurals
                return singular if count == 1 else plural
                
        except Exception as e:
            logger.error(f"Pluralization error: {e}")
            return plural if count != 1 else singular
    
    @app.template_global()
    def dir_class():
        """Get CSS class for text direction."""
        return 'rtl' if getattr(g, 'is_rtl', False) else 'ltr'
    
    @app.template_global()
    def lang_class():
        """Get CSS class for current language."""
        return f"lang-{getattr(g, 'language_code', 'en')}"
    
    @app.template_filter('safe_translate')
    def safe_translate_filter(key, fallback=''):
        """Safely translate a key with fallback."""
        try:
            translation = i18n_service.translate(key, g.language_code)
            return translation if translation != key else fallback
        except Exception as e:
            logger.error(f"Safe translation error for key {key}: {e}")
            return fallback
    
    @app.template_test('translated')
    def is_translated_test(key):
        """Test if a key has a translation."""
        try:
            translation = i18n_service.translate(key, g.language_code)
            return translation != key
        except Exception:
            return False