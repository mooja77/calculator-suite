"""
Currency conversion and exchange rate management service.
"""
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, List, Tuple
import logging

from app import db, redis_client
from app.models import Currency, ExchangeRate

logger = logging.getLogger(__name__)

class CurrencyService:
    """Service for currency conversion and exchange rate management."""
    
    # Free API endpoints for exchange rates
    EXCHANGE_APIS = {
        'exchangerate_api': {
            'url': 'https://api.exchangerate-api.com/v4/latest/{base}',
            'free_limit': 1500,  # requests per month
            'cache_duration': 3600  # 1 hour
        },
        'fixer_io': {
            'url': 'http://data.fixer.io/api/latest?access_key={api_key}&base={base}',
            'free_limit': 1000,  # requests per month
            'cache_duration': 3600
        }
    }
    
    # Fallback rates for when APIs are unavailable
    FALLBACK_RATES = {
        'USD': {'EUR': 0.85, 'GBP': 0.73, 'CAD': 1.25, 'AUD': 1.35, 'JPY': 110.0},
        'EUR': {'USD': 1.18, 'GBP': 0.86, 'CAD': 1.47, 'AUD': 1.59, 'JPY': 129.5}
    }
    
    def __init__(self):
        self.redis_key_prefix = 'currency:'
        self.default_cache_duration = 3600  # 1 hour
    
    def get_supported_currencies(self) -> List[Dict]:
        """Get list of supported currencies."""
        try:
            currencies = Currency.query.filter_by(is_active=True).all()
            return [currency.to_dict() for currency in currencies]
        except Exception as e:
            logger.error(f"Error fetching supported currencies: {e}")
            return []
    
    def get_exchange_rate(self, base_currency: str, target_currency: str, 
                         force_refresh: bool = False) -> Optional[Decimal]:
        """
        Get exchange rate between two currencies.
        
        Args:
            base_currency: Source currency code (e.g., 'USD')
            target_currency: Target currency code (e.g., 'EUR')
            force_refresh: Force refresh from API
            
        Returns:
            Exchange rate as Decimal or None if unavailable
        """
        # Same currency
        if base_currency == target_currency:
            return Decimal('1.0')
        
        # Check cache first
        if not force_refresh:
            cached_rate = self._get_cached_rate(base_currency, target_currency)
            if cached_rate:
                return cached_rate
        
        # Try to get from database
        db_rate = self._get_db_rate(base_currency, target_currency)
        if db_rate and not db_rate.is_expired:
            self._cache_rate(base_currency, target_currency, db_rate.rate)
            return db_rate.rate
        
        # Fetch from API
        try:
            rate = self._fetch_from_api(base_currency, target_currency)
            if rate:
                self._store_rate(base_currency, target_currency, rate)
                self._cache_rate(base_currency, target_currency, rate)
                return rate
        except Exception as e:
            logger.error(f"Error fetching exchange rate {base_currency}/{target_currency}: {e}")
        
        # Try inverse rate
        try:
            inverse_rate = self._get_inverse_rate(base_currency, target_currency)
            if inverse_rate:
                return inverse_rate
        except Exception as e:
            logger.error(f"Error calculating inverse rate: {e}")
        
        # Fallback to hardcoded rates
        return self._get_fallback_rate(base_currency, target_currency)
    
    def convert_currency(self, amount: Decimal, base_currency: str, 
                        target_currency: str) -> Optional[Decimal]:
        """
        Convert amount from base currency to target currency.
        
        Args:
            amount: Amount to convert
            base_currency: Source currency code
            target_currency: Target currency code
            
        Returns:
            Converted amount or None if conversion failed
        """
        try:
            rate = self.get_exchange_rate(base_currency, target_currency)
            if rate is None:
                return None
            
            converted = amount * rate
            return converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception as e:
            logger.error(f"Error converting {amount} {base_currency} to {target_currency}: {e}")
            return None
    
    def format_currency(self, amount: Decimal, currency_code: str, 
                       locale_format: Dict = None) -> str:
        """
        Format currency amount according to locale preferences.
        
        Args:
            amount: Amount to format
            currency_code: Currency code
            locale_format: Locale formatting preferences
            
        Returns:
            Formatted currency string
        """
        try:
            currency = Currency.query.filter_by(code=currency_code).first()
            if not currency:
                return f"{amount} {currency_code}"
            
            # Apply locale formatting
            if locale_format:
                decimal_sep = locale_format.get('decimal_separator', '.')
                thousands_sep = locale_format.get('thousands_separator', ',')
            else:
                decimal_sep = '.'
                thousands_sep = ','
            
            # Round to currency precision
            precision = currency.decimal_places
            rounded_amount = amount.quantize(
                Decimal('0.1') ** precision, 
                rounding=ROUND_HALF_UP
            )
            
            # Format with thousands separator
            amount_str = f"{rounded_amount:,.{precision}f}"
            
            # Apply locale separators
            if decimal_sep != '.' or thousands_sep != ',':
                parts = amount_str.split('.')
                integer_part = parts[0].replace(',', thousands_sep)
                if len(parts) > 1:
                    amount_str = f"{integer_part}{decimal_sep}{parts[1]}"
                else:
                    amount_str = integer_part
            
            return f"{currency.symbol}{amount_str}"
        except Exception as e:
            logger.error(f"Error formatting currency {amount} {currency_code}: {e}")
            return f"{amount} {currency_code}"
    
    def _get_cached_rate(self, base: str, target: str) -> Optional[Decimal]:
        """Get exchange rate from Redis cache."""
        if not redis_client:
            return None
        
        try:
            key = f"{self.redis_key_prefix}rate:{base}:{target}"
            cached_value = redis_client.get(key)
            if cached_value:
                return Decimal(cached_value.decode())
        except Exception as e:
            logger.error(f"Error getting cached rate: {e}")
        
        return None
    
    def _cache_rate(self, base: str, target: str, rate: Decimal):
        """Store exchange rate in Redis cache."""
        if not redis_client:
            return
        
        try:
            key = f"{self.redis_key_prefix}rate:{base}:{target}"
            redis_client.setex(key, self.default_cache_duration, str(rate))
        except Exception as e:
            logger.error(f"Error caching rate: {e}")
    
    def _get_db_rate(self, base: str, target: str) -> Optional[ExchangeRate]:
        """Get exchange rate from database."""
        try:
            return ExchangeRate.query.filter_by(
                base_currency=base,
                target_currency=target
            ).first()
        except Exception as e:
            logger.error(f"Error getting DB rate: {e}")
            return None
    
    def _store_rate(self, base: str, target: str, rate: Decimal):
        """Store exchange rate in database."""
        try:
            # Update or create rate
            db_rate = ExchangeRate.query.filter_by(
                base_currency=base,
                target_currency=target
            ).first()
            
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            if db_rate:
                db_rate.rate = rate
                db_rate.timestamp = datetime.utcnow()
                db_rate.expires_at = expires_at
                db_rate.source = 'api'
            else:
                db_rate = ExchangeRate(
                    base_currency=base,
                    target_currency=target,
                    rate=rate,
                    source='api',
                    expires_at=expires_at
                )
                db.session.add(db_rate)
            
            db.session.commit()
        except Exception as e:
            logger.error(f"Error storing rate: {e}")
            db.session.rollback()
    
    def _fetch_from_api(self, base: str, target: str) -> Optional[Decimal]:
        """Fetch exchange rate from external API."""
        # Try exchangerate-api.com (free tier)
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            if target in rates:
                return Decimal(str(rates[target]))
        except Exception as e:
            logger.error(f"Error fetching from exchangerate-api: {e}")
        
        return None
    
    def _get_inverse_rate(self, base: str, target: str) -> Optional[Decimal]:
        """Try to get inverse rate (target/base) and calculate base/target."""
        try:
            inverse_rate = self.get_exchange_rate(target, base)
            if inverse_rate and inverse_rate > 0:
                return Decimal('1') / inverse_rate
        except Exception as e:
            logger.error(f"Error calculating inverse rate: {e}")
        
        return None
    
    def _get_fallback_rate(self, base: str, target: str) -> Optional[Decimal]:
        """Get fallback exchange rate from hardcoded values."""
        try:
            if base in self.FALLBACK_RATES:
                rates = self.FALLBACK_RATES[base]
                if target in rates:
                    return Decimal(str(rates[target]))
            
            # Try inverse fallback
            if target in self.FALLBACK_RATES:
                rates = self.FALLBACK_RATES[target]
                if base in rates:
                    return Decimal('1') / Decimal(str(rates[base]))
        except Exception as e:
            logger.error(f"Error getting fallback rate: {e}")
        
        return None
    
    def refresh_all_rates(self, base_currencies: List[str] = None) -> Dict[str, int]:
        """
        Refresh exchange rates for all supported currencies.
        
        Args:
            base_currencies: List of base currencies to refresh (default: USD, EUR)
            
        Returns:
            Dictionary with refresh statistics
        """
        if not base_currencies:
            base_currencies = ['USD', 'EUR']
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        currencies = self.get_supported_currencies()
        currency_codes = [c['code'] for c in currencies]
        
        for base in base_currencies:
            if base not in currency_codes:
                continue
                
            for target in currency_codes:
                if base == target:
                    stats['skipped'] += 1
                    continue
                
                try:
                    rate = self._fetch_from_api(base, target)
                    if rate:
                        self._store_rate(base, target, rate)
                        self._cache_rate(base, target, rate)
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                except Exception as e:
                    logger.error(f"Error refreshing rate {base}/{target}: {e}")
                    stats['failed'] += 1
        
        return stats

# Global instance
currency_service = CurrencyService()