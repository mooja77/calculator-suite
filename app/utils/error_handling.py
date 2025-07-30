"""
Enhanced error handling for global infrastructure.
"""
import logging
import traceback
from functools import wraps
from typing import Dict, Any, Optional
from flask import g, request, current_app

logger = logging.getLogger(__name__)

class GlobalInfrastructureError(Exception):
    """Base exception for global infrastructure errors."""
    pass

class CurrencyServiceError(GlobalInfrastructureError):
    """Currency service related errors."""
    pass

class LocalizationServiceError(GlobalInfrastructureError):
    """Localization service related errors."""
    pass

class ExchangeRateError(CurrencyServiceError):
    """Exchange rate fetching/conversion errors."""
    pass

class CountryDetectionError(LocalizationServiceError):
    """Country detection related errors."""
    pass

def handle_service_error(func):
    """Decorator to handle service errors gracefully."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GlobalInfrastructureError as e:
            logger.error(f"Global infrastructure error in {func.__name__}: {e}")
            # Return a safe fallback response
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            return None
    return wrapper

def log_request_context(error_msg: str, additional_data: Dict[str, Any] = None):
    """Log error with request context for debugging."""
    context = {
        'endpoint': request.endpoint if request else None,
        'method': request.method if request else None,
        'url': request.url if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None,
        'session_id': getattr(g, 'session_id', None),
        'country_code': getattr(g, 'country_code', None),
        'currency_code': getattr(g, 'currency_code', None),
    }
    
    if additional_data:
        context.update(additional_data)
    
    logger.error(f"{error_msg} | Context: {context}")

def safe_currency_conversion(amount, from_currency, to_currency, fallback_rate=1.0):
    """Safely convert currency with fallback handling."""
    try:
        from app.services.currency import currency_service
        result = currency_service.convert_currency(amount, from_currency, to_currency)
        if result is not None:
            return result
    except Exception as e:
        log_request_context(
            f"Currency conversion failed: {from_currency} to {to_currency}",
            {'amount': amount, 'error': str(e)}
        )
    
    # Fallback to original amount or simple rate
    if from_currency == to_currency:
        return amount
    return amount * fallback_rate

def safe_number_formatting(number, locale_config=None, fallback_format="{:.2f}"):
    """Safely format number with fallback handling."""
    try:
        from app.services.localization import localization_service
        if locale_config is None:
            locale_config = getattr(g, 'locale_config', {})
        
        result = localization_service.format_number(number, locale_config)
        if result:
            return result
    except Exception as e:
        log_request_context(
            "Number formatting failed",
            {'number': number, 'locale_config': locale_config, 'error': str(e)}
        )
    
    # Fallback to simple formatting
    try:
        return fallback_format.format(number)
    except:
        return str(number)

def safe_country_detection(ip_address, fallback_country='US'):
    """Safely detect country with fallback handling."""
    try:
        from app.services.localization import localization_service
        result = localization_service.detect_country_from_ip(ip_address)
        if result:
            return result
    except Exception as e:
        log_request_context(
            "Country detection failed",
            {'ip_address': ip_address, 'error': str(e)}
        )
    
    return fallback_country

def validate_currency_code(currency_code: str) -> bool:
    """Validate currency code format and existence."""
    if not currency_code or len(currency_code) != 3:
        return False
    
    try:
        from app.services.currency import currency_service
        currencies = currency_service.get_supported_currencies()
        return any(c['code'] == currency_code.upper() for c in currencies)
    except Exception:
        # If we can't validate, allow common currencies
        common_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        return currency_code.upper() in common_currencies

def validate_country_code(country_code: str) -> bool:
    """Validate country code format and existence."""
    if not country_code or len(country_code) != 2:
        return False
    
    try:
        from app.services.localization import localization_service
        locales = localization_service.get_supported_locales()
        return any(l['code'] == country_code.upper() for l in locales)
    except Exception:
        # If we can't validate, allow common countries
        common_countries = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'IT', 'ES', 'JP']
        return country_code.upper() in common_countries

def create_error_response(error_type: str, error_message: str, 
                         status_code: int = 500, details: Dict = None) -> Dict:
    """Create standardized error response."""
    response = {
        'success': False,
        'error_type': error_type,
        'error_message': error_message,
        'timestamp': g.get('request_timestamp') if hasattr(g, 'request_timestamp') else None
    }
    
    if details:
        response['details'] = details
    
    # Add debug information in development mode
    if current_app.debug:
        response['debug_info'] = {
            'endpoint': request.endpoint if request else None,
            'method': request.method if request else None,
            'session_id': getattr(g, 'session_id', None)
        }
    
    return response

class ServiceHealthChecker:
    """Health checker for global infrastructure services."""
    
    @staticmethod
    def check_currency_service() -> Dict[str, Any]:
        """Check currency service health."""
        try:
            from app.services.currency import currency_service
            
            # Test basic operations
            currencies = currency_service.get_supported_currencies()
            if not currencies:
                return {'healthy': False, 'error': 'No currencies available'}
            
            # Test exchange rate fetch (USD to EUR as common pair)
            test_rate = currency_service.get_exchange_rate('USD', 'EUR')
            
            return {
                'healthy': True,
                'currencies_count': len(currencies),
                'test_rate_available': test_rate is not None,
                'last_check': logger.handlers[0].formatter.formatTime(
                    logging.LogRecord('', '', '', '', '', '', '', '')
                ) if logger.handlers else 'unknown'
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @staticmethod
    def check_localization_service() -> Dict[str, Any]:
        """Check localization service health."""
        try:
            from app.services.localization import localization_service
            
            # Test basic operations
            locales = localization_service.get_supported_locales()
            if not locales:
                return {'healthy': False, 'error': 'No locales available'}
            
            # Test regional config
            us_config = localization_service.get_regional_config('US')
            if not us_config:
                return {'healthy': False, 'error': 'Default config unavailable'}
            
            return {
                'healthy': True,
                'locales_count': len(locales),
                'default_config_available': bool(us_config),
                'geoip_available': hasattr(localization_service, 'geoip_db_path')
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    @staticmethod
    def check_database_health() -> Dict[str, Any]:
        """Check database connectivity and table existence."""
        try:
            from app import db
            from app.models import Currency, Country, ExchangeRate
            
            # Test database connection
            db.session.execute('SELECT 1')
            
            # Check table existence by counting records
            currency_count = Currency.query.count()
            country_count = Country.query.count()
            exchange_rate_count = ExchangeRate.query.count()
            
            return {
                'healthy': True,
                'currencies_seeded': currency_count > 0,
                'countries_seeded': country_count > 0,
                'exchange_rates_available': exchange_rate_count > 0,
                'tables_accessible': True
            }
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

# Global health checker instance
health_checker = ServiceHealthChecker()