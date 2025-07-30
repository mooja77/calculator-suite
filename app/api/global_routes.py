"""
API routes for global infrastructure (currency, localization).
"""
from flask import Blueprint, jsonify, request, g, session
from decimal import Decimal, InvalidOperation
import logging

from app.services.currency import currency_service
from app.services.localization import localization_service

logger = logging.getLogger(__name__)

global_api = Blueprint('global_api', __name__, url_prefix='/api/v1/global')

@global_api.route('/currencies', methods=['GET'])
def get_currencies():
    """Get list of supported currencies."""
    try:
        currencies = currency_service.get_supported_currencies()
        return jsonify({
            'success': True,
            'data': currencies,
            'count': len(currencies)
        })
    except Exception as e:
        logger.error(f"Error fetching currencies: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch currencies'
        }), 500

@global_api.route('/exchange-rate/<base>/<target>', methods=['GET'])
def get_exchange_rate(base, target):
    """Get exchange rate between two currencies."""
    try:
        # Validate currency codes
        if len(base) != 3 or len(target) != 3:
            return jsonify({
                'success': False,
                'error': 'Invalid currency codes'
            }), 400
        
        base = base.upper()
        target = target.upper()
        
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        rate = currency_service.get_exchange_rate(base, target, force_refresh)
        
        if rate is None:
            return jsonify({
                'success': False,
                'error': f'Exchange rate not available for {base}/{target}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'base_currency': base,
                'target_currency': target,
                'rate': float(rate),
                'formatted_rate': f"1 {base} = {rate} {target}"
            }
        })
    except Exception as e:
        logger.error(f"Error fetching exchange rate {base}/{target}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch exchange rate'
        }), 500

@global_api.route('/convert', methods=['POST'])
def convert_currency():
    """Convert amount between currencies."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON data required'
            }), 400
        
        # Validate required fields
        required_fields = ['amount', 'from_currency', 'to_currency']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        try:
            amount = Decimal(str(data['amount']))
        except (InvalidOperation, ValueError):
            return jsonify({
                'success': False,
                'error': 'Invalid amount format'
            }), 400
        
        from_currency = data['from_currency'].upper()
        to_currency = data['to_currency'].upper()
        
        # Convert currency
        converted_amount = currency_service.convert_currency(amount, from_currency, to_currency)
        
        if converted_amount is None:
            return jsonify({
                'success': False,
                'error': f'Currency conversion failed for {from_currency} to {to_currency}'
            }), 400
        
        # Format the result
        locale_format = getattr(g, 'locale_config', {})
        formatted_result = currency_service.format_currency(converted_amount, to_currency, locale_format)
        
        return jsonify({
            'success': True,
            'data': {
                'original_amount': float(amount),
                'original_currency': from_currency,
                'converted_amount': float(converted_amount),
                'converted_currency': to_currency,
                'formatted_result': formatted_result,
                'exchange_rate': float(converted_amount / amount) if amount > 0 else 0
            }
        })
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        return jsonify({
            'success': False,
            'error': 'Currency conversion failed'
        }), 500

@global_api.route('/countries', methods=['GET'])
def get_countries():
    """Get list of supported countries/regions."""
    try:
        locales = localization_service.get_supported_locales()
        return jsonify({
            'success': True,
            'data': locales,
            'count': len(locales)
        })
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch countries'
        }), 500

@global_api.route('/locale-config/<country_code>', methods=['GET'])
def get_locale_config(country_code):
    """Get regional configuration for a country."""
    try:
        if len(country_code) != 2:
            return jsonify({
                'success': False,
                'error': 'Invalid country code'
            }), 400
        
        country_code = country_code.upper()
        config = localization_service.get_regional_config(country_code)
        
        return jsonify({
            'success': True,
            'data': config
        })
    except Exception as e:
        logger.error(f"Error fetching locale config for {country_code}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch locale configuration'
        }), 500

@global_api.route('/user-preferences', methods=['GET'])
def get_user_preferences():
    """Get current user's preferences."""
    try:
        session_id = getattr(g, 'session_id', None)
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session available'
            }), 400
        
        preferences = localization_service.get_user_preferences(session_id)
        locale_config = getattr(g, 'locale_config', {})
        
        return jsonify({
            'success': True,
            'data': {
                'preferences': preferences,
                'active_config': locale_config,
                'detected_country': getattr(g, 'detected_country', None)
            }
        })
    except Exception as e:
        logger.error(f"Error fetching user preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user preferences'
        }), 500

@global_api.route('/user-preferences', methods=['POST'])
def save_user_preferences():
    """Save user preferences."""
    try:
        session_id = getattr(g, 'session_id', None)
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session available'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON data required'
            }), 400
        
        # Save preferences
        success = localization_service.save_user_preferences(session_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Preferences saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save preferences'
            }), 500
    except Exception as e:
        logger.error(f"Error saving user preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to save preferences'
        }), 500

@global_api.route('/detect-location', methods=['POST'])
def detect_location():
    """Detect user location from IP (admin only)."""
    try:
        data = request.get_json()
        if not data or 'ip_address' not in data:
            return jsonify({
                'success': False,
                'error': 'IP address required'
            }), 400
        
        ip_address = data['ip_address']
        country_code = localization_service.detect_country_from_ip(ip_address)
        
        if country_code:
            config = localization_service.get_regional_config(country_code)
            return jsonify({
                'success': True,
                'data': {
                    'country_code': country_code,
                    'config': config
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not detect location'
            }), 404
    except Exception as e:
        logger.error(f"Error detecting location: {e}")
        return jsonify({
            'success': False,
            'error': 'Location detection failed'
        }), 500

@global_api.route('/format-number', methods=['POST'])
def format_number():
    """Format number according to locale preferences."""
    try:
        data = request.get_json()
        if not data or 'number' not in data:
            return jsonify({
                'success': False,
                'error': 'Number required'
            }), 400
        
        try:
            number = float(data['number'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid number format'
            }), 400
        
        # Use provided locale config or current user's config
        locale_config = data.get('locale_config', getattr(g, 'locale_config', {}))
        formatted = localization_service.format_number(number, locale_config)
        
        return jsonify({
            'success': True,
            'data': {
                'original': number,
                'formatted': formatted,
                'locale_config': locale_config
            }
        })
    except Exception as e:
        logger.error(f"Error formatting number: {e}")
        return jsonify({
            'success': False,
            'error': 'Number formatting failed'
        }), 500

# Error handlers for this blueprint
@global_api.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@global_api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500