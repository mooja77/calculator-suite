"""
Localization service for multi-regional support.
"""
import geoip2.database
import geoip2.errors
from typing import Dict, Optional, Tuple, List
import logging
import os
from datetime import datetime
import pytz
import pycountry
from babel import Locale, dates, numbers
from babel.core import UnknownLocaleError

from app import db, redis_client
from app.models import Country, UserPreference
from app.services.i18n import i18n_service

logger = logging.getLogger(__name__)

class LocalizationService:
    """Service for handling localization and regional preferences."""
    
    # Default regional configurations
    DEFAULT_REGIONS = {
        'US': {
            'currency_code': 'USD',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'date_format': 'MM/DD/YYYY',
            'time_format': 'HH:mm',
            'timezone': 'America/New_York',
            'language_code': 'en'
        },
        'GB': {
            'currency_code': 'GBP',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'date_format': 'DD/MM/YYYY',
            'time_format': 'HH:mm',
            'timezone': 'Europe/London',
            'language_code': 'en'
        },
        'DE': {
            'currency_code': 'EUR',
            'decimal_separator': ',',
            'thousands_separator': '.',
            'date_format': 'DD.MM.YYYY',
            'time_format': 'HH:mm',
            'timezone': 'Europe/Berlin',
            'language_code': 'de'
        },
        'FR': {
            'currency_code': 'EUR',
            'decimal_separator': ',',
            'thousands_separator': ' ',
            'date_format': 'DD/MM/YYYY',
            'time_format': 'HH:mm',
            'timezone': 'Europe/Paris',
            'language_code': 'fr'
        },
        'CA': {
            'currency_code': 'CAD',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'date_format': 'DD/MM/YYYY',
            'time_format': 'HH:mm',
            'timezone': 'America/Toronto',
            'language_code': 'en'
        },
        'AU': {
            'currency_code': 'AUD',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'date_format': 'DD/MM/YYYY',
            'time_format': 'HH:mm',
            'timezone': 'Australia/Sydney',
            'language_code': 'en'
        },
        'JP': {
            'currency_code': 'JPY',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'date_format': 'YYYY/MM/DD',
            'time_format': 'HH:mm',
            'timezone': 'Asia/Tokyo',
            'language_code': 'ja'
        }
    }
    
    def __init__(self):
        self.redis_key_prefix = 'locale:'
        self.geoip_db_path = os.getenv('GEOIP_DB_PATH', 'data/GeoLite2-Country.mmdb')
        self.cache_duration = 86400  # 24 hours
    
    def detect_country_from_ip(self, ip_address: str) -> Optional[str]:
        """
        Detect country from IP address using GeoIP database.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            ISO country code or None if detection failed
        """
        # Skip private/local IPs
        if self._is_private_ip(ip_address):
            return None
        
        # Check cache first
        cached_country = self._get_cached_country(ip_address)
        if cached_country:
            return cached_country
        
        try:
            if os.path.exists(self.geoip_db_path):
                with geoip2.database.Reader(self.geoip_db_path) as reader:
                    response = reader.country(ip_address)
                    country_code = response.country.iso_code
                    
                    if country_code:
                        self._cache_country(ip_address, country_code)
                        return country_code
        except (geoip2.errors.AddressNotFoundError, geoip2.errors.GeoIP2Error) as e:
            logger.debug(f"GeoIP lookup failed for {ip_address}: {e}")
        except Exception as e:
            logger.error(f"Error detecting country for {ip_address}: {e}")
        
        return None
    
    def get_regional_config(self, country_code: str = None) -> Dict:
        """
        Get regional configuration for a country.
        
        Args:
            country_code: ISO country code
            
        Returns:
            Regional configuration dictionary
        """
        if not country_code:
            country_code = 'US'  # Default to US
        
        # Try database first
        try:
            country = Country.query.filter_by(code=country_code, is_active=True).first()
            if country:
                return country.to_dict()
        except Exception as e:
            logger.error(f"Error fetching country config from DB: {e}")
        
        # Fallback to default configurations
        if country_code in self.DEFAULT_REGIONS:
            return self.DEFAULT_REGIONS[country_code].copy()
        
        # Ultimate fallback
        return self.DEFAULT_REGIONS['US'].copy()
    
    def get_user_preferences(self, session_id: str) -> Dict:
        """
        Get user preferences for a session.
        
        Args:
            session_id: User session ID
            
        Returns:
            User preferences dictionary
        """
        try:
            prefs = UserPreference.query.filter_by(session_id=session_id).first()
            if prefs:
                return prefs.to_dict()
        except Exception as e:
            logger.error(f"Error fetching user preferences: {e}")
        
        return {}
    
    def save_user_preferences(self, session_id: str, preferences: Dict) -> bool:
        """
        Save user preferences for a session.
        
        Args:
            session_id: User session ID
            preferences: Preferences dictionary
            
        Returns:
            True if saved successfully
        """
        try:
            prefs = UserPreference.query.filter_by(session_id=session_id).first()
            
            if prefs:
                # Update existing preferences
                for key, value in preferences.items():
                    if hasattr(prefs, key):
                        setattr(prefs, key, value)
                prefs.updated_at = datetime.utcnow()
            else:
                # Create new preferences
                prefs = UserPreference(session_id=session_id, **preferences)
                db.session.add(prefs)
            
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
            db.session.rollback()
            return False
    
    def format_number(self, number: float, locale_config: Dict = None) -> str:
        """
        Format number according to locale preferences.
        
        Args:
            number: Number to format
            locale_config: Locale configuration
            
        Returns:
            Formatted number string
        """
        try:
            if not locale_config:
                locale_config = self.get_regional_config()
            
            decimal_sep = locale_config.get('decimal_separator', '.')
            thousands_sep = locale_config.get('thousands_separator', ',')
            
            # Format with default separators first
            formatted = f"{number:,.2f}"
            
            # Replace with locale-specific separators
            if decimal_sep != '.' or thousands_sep != ',':
                parts = formatted.split('.')
                integer_part = parts[0].replace(',', thousands_sep)
                if len(parts) > 1:
                    formatted = f"{integer_part}{decimal_sep}{parts[1]}"
                else:
                    formatted = integer_part
            
            return formatted
        except Exception as e:
            logger.error(f"Error formatting number: {e}")
            return str(number)
    
    def format_date(self, date_obj: datetime, locale_config: Dict = None, 
                   include_time: bool = False) -> str:
        """
        Format date according to locale preferences.
        
        Args:
            date_obj: Date object to format
            locale_config: Locale configuration
            include_time: Whether to include time
            
        Returns:
            Formatted date string
        """
        try:
            if not locale_config:
                locale_config = self.get_regional_config()
            
            date_format = locale_config.get('date_format', 'MM/DD/YYYY')
            time_format = locale_config.get('time_format', 'HH:mm')
            
            # Convert format patterns
            format_mapping = {
                'YYYY': '%Y',
                'YY': '%y',
                'MM': '%m',
                'DD': '%d',
                'HH': '%H',
                'mm': '%M'
            }
            
            python_format = date_format
            for pattern, replacement in format_mapping.items():
                python_format = python_format.replace(pattern, replacement)
            
            if include_time:
                time_python_format = time_format
                for pattern, replacement in format_mapping.items():
                    time_python_format = time_python_format.replace(pattern, replacement)
                python_format += f" {time_python_format}"
            
            return date_obj.strftime(python_format)
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            return date_obj.isoformat()
    
    def get_timezone_info(self, country_code: str = None) -> Dict:
        """
        Get timezone information for a country.
        
        Args:
            country_code: ISO country code
            
        Returns:
            Timezone information dictionary
        """
        try:
            config = self.get_regional_config(country_code)
            timezone_name = config.get('timezone', 'UTC')
            
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
            
            return {
                'timezone': timezone_name,
                'offset': now.strftime('%z'),
                'offset_hours': now.utcoffset().total_seconds() / 3600,
                'is_dst': now.dst() is not None and now.dst().total_seconds() > 0
            }
        except Exception as e:
            logger.error(f"Error getting timezone info: {e}")
            return {
                'timezone': 'UTC',
                'offset': '+0000',
                'offset_hours': 0,
                'is_dst': False
            }
    
    def get_supported_locales(self) -> List[Dict]:
        """Get list of supported locales with enhanced language support."""
        # Get enhanced language list from i18n service
        try:
            enhanced_languages = i18n_service.get_available_languages()
            if enhanced_languages:
                return enhanced_languages
        except Exception as e:
            logger.error(f"Error getting enhanced languages: {e}")
        
        # Fallback to original implementation
        """Get list of supported locales."""
        try:
            countries = Country.query.filter_by(is_active=True).all()
            locales = []
            
            for country in countries:
                try:
                    # Get country name from pycountry
                    country_info = pycountry.countries.get(alpha_2=country.code)
                    country_name = country_info.name if country_info else country.name
                    
                    locales.append({
                        'code': country.code,
                        'name': country_name,
                        'currency': country.currency_code,
                        'language': country.language_code,
                        'timezone': country.timezone
                    })
                except Exception as e:
                    logger.error(f"Error processing country {country.code}: {e}")
            
            return locales
        except Exception as e:
            logger.error(f"Error getting supported locales: {e}")
            return []
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP address is private/local."""
        private_ranges = [
            '127.',      # Loopback
            '10.',       # Class A private
            '172.16.',   # Class B private (simplified check)
            '192.168.',  # Class C private
            '::1',       # IPv6 loopback
            'fc00:',     # IPv6 unique local
            'fe80:'      # IPv6 link local
        ]
        
        return any(ip_address.startswith(prefix) for prefix in private_ranges)
    
    def _get_cached_country(self, ip_address: str) -> Optional[str]:
        """Get cached country detection result."""
        if not redis_client:
            return None
        
        try:
            key = f"{self.redis_key_prefix}ip:{ip_address}"
            cached_value = redis_client.get(key)
            if cached_value:
                return cached_value.decode()
        except Exception as e:
            logger.error(f"Error getting cached country: {e}")
        
        return None
    
    def _cache_country(self, ip_address: str, country_code: str):
        """Cache country detection result."""
        if not redis_client:
            return
        
        try:
            key = f"{self.redis_key_prefix}ip:{ip_address}"
            redis_client.setex(key, self.cache_duration, country_code)
        except Exception as e:
            logger.error(f"Error caching country: {e}")

# Global instance
localization_service = LocalizationService()