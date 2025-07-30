"""
Internationalization API Routes
Provides translation data and language switching endpoints
"""
from flask import Blueprint, jsonify, request, session, g
from app.services.i18n import i18n_service
from app.services.localization import localization_service
import logging

logger = logging.getLogger(__name__)

i18n_bp = Blueprint('i18n', __name__, url_prefix='/api')

@i18n_bp.route('/translations/<language_code>')
def get_translations(language_code):
    """Get translation data for a specific language."""
    try:
        # Validate language code
        if not i18n_service._is_language_supported(language_code):
            return jsonify({
                'error': 'Unsupported language',
                'supported_languages': list(i18n_service.SUPPORTED_LANGUAGES.keys())
            }), 400
        
        # Load translations
        translations = i18n_service._get_translations(language_code)
        
        if not translations:
            return jsonify({
                'error': 'Translations not found',
                'language': language_code
            }), 404
        
        return jsonify({
            'language': language_code,
            'translations': translations,
            'language_info': i18n_service.get_language_info(language_code)
        })
        
    except Exception as e:
        logger.error(f"Error getting translations for {language_code}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/languages')
def get_supported_languages():
    """Get list of all supported languages."""
    try:
        languages = i18n_service.get_available_languages()
        
        return jsonify({
            'languages': languages,
            'current_language': i18n_service.get_user_language(),
            'total_count': len(languages)
        })
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/language', methods=['POST'])
def set_language():
    """Set user's preferred language."""
    try:
        data = request.get_json()
        
        if not data or 'language' not in data:
            return jsonify({
                'error': 'Language code required',
                'example': {'language': 'en'}
            }), 400
        
        language_code = data['language']
        
        # Set language preference
        success = i18n_service.set_user_language(language_code)
        
        if not success:
            return jsonify({
                'error': 'Failed to set language',
                'language': language_code,
                'supported_languages': list(i18n_service.SUPPORTED_LANGUAGES.keys())
            }), 400
        
        # Update localization service as well
        if hasattr(g, 'session_id'):
            localization_service.save_user_preferences(g.session_id, {
                'language_code': language_code
            })
        
        return jsonify({
            'success': True,
            'language': language_code,
            'language_info': i18n_service.get_language_info(language_code),
            'message': 'Language preference updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error setting language: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/language')
def get_current_language():
    """Get current user's language preference."""
    try:
        current_language = i18n_service.get_user_language()
        language_info = i18n_service.get_language_info(current_language)
        
        return jsonify({
            'current_language': current_language,
            'language_info': language_info,
            'regional_config': getattr(g, 'locale_config', {})
        })
        
    except Exception as e:
        logger.error(f"Error getting current language: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/format/number')
def format_number():
    """Format a number according to current language settings."""
    try:
        number = request.args.get('number')
        currency = request.args.get('currency')
        language = request.args.get('language')
        
        if not number:
            return jsonify({
                'error': 'Number parameter required',
                'example': '?number=1234.56&currency=USD&language=en'
            }), 400
        
        try:
            number_value = float(number)
        except ValueError:
            return jsonify({
                'error': 'Invalid number format',
                'provided': number
            }), 400
        
        # Format the number
        formatted = i18n_service.format_number_localized(
            number_value, 
            language=language, 
            currency=currency
        )
        
        return jsonify({
            'original': number_value,
            'formatted': formatted,
            'language': language or i18n_service.get_user_language(),
            'currency': currency
        })
        
    except Exception as e:
        logger.error(f"Error formatting number: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/islamic-finance/terms')
def get_islamic_finance_terms():
    """Get Islamic finance terminology with translations."""
    try:
        language = request.args.get('language', 'ar')
        
        terms = i18n_service.get_islamic_finance_terms(language)
        
        return jsonify({
            'language': language,
            'terms': terms,
            'total_terms': len(terms.get('terms', {}))
        })
        
    except Exception as e:
        logger.error(f"Error getting Islamic finance terms: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/detect-language')
def detect_language():
    """Detect user's preferred language from various sources."""
    try:
        # Get browser language preferences
        browser_languages = []
        accept_language = request.headers.get('Accept-Language', '')
        
        if accept_language:
            for lang_item in accept_language.split(','):
                lang = lang_item.split(';')[0].strip()
                if lang:
                    browser_languages.append(lang)
        
        # Get IP-based country detection
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        detected_country = None
        
        if client_ip:
            detected_country = localization_service.detect_country_from_ip(client_ip)
        
        # Get session language
        session_language = session.get('language')
        
        # Determine best language
        detected_language = i18n_service.get_user_language()
        
        return jsonify({
            'detected_language': detected_language,
            'session_language': session_language,
            'browser_languages': browser_languages,
            'detected_country': detected_country,
            'client_ip': client_ip,
            'language_info': i18n_service.get_language_info(detected_language)
        })
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@i18n_bp.route('/health')
def i18n_health_check():
    """Health check for i18n service."""
    try:
        # Test translation loading
        test_translations = i18n_service._get_translations('en')
        
        return jsonify({
            'status': 'healthy',
            'supported_languages': len(i18n_service.SUPPORTED_LANGUAGES),
            'translations_loaded': len(i18n_service.translations_cache),
            'test_translation_keys': len(test_translations.keys()) if test_translations else 0,
            'version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"I18n health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500