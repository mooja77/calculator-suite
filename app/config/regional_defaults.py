"""
Regional defaults and configuration data for global infrastructure.
"""
from typing import Dict, List

# Currency definitions with metadata
CURRENCIES = [
    # Major currencies
    {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'decimal_places': 2},
    {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'decimal_places': 2},
    {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'decimal_places': 2},
    {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'decimal_places': 0},
    {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'decimal_places': 2},
    {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'decimal_places': 2},
    {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF', 'decimal_places': 2},
    {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'decimal_places': 2},
    {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr', 'decimal_places': 2},
    {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr', 'decimal_places': 2},
    {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$', 'decimal_places': 2},
    {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$', 'decimal_places': 2},
    {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'decimal_places': 2},
    {'code': 'NZD', 'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'decimal_places': 2},
    {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩', 'decimal_places': 0},
    {'code': 'TRY', 'name': 'Turkish Lira', 'symbol': '₺', 'decimal_places': 2},
    {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽', 'decimal_places': 2},
    {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'decimal_places': 2},
    {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$', 'decimal_places': 2},
    {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'decimal_places': 2},
    
    # Islamic finance currencies
    {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'decimal_places': 2},
    {'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': 'ر.س', 'decimal_places': 2},
    {'code': 'MYR', 'name': 'Malaysian Ringgit', 'symbol': 'RM', 'decimal_places': 2},
    {'code': 'PKR', 'name': 'Pakistani Rupee', 'symbol': '₨', 'decimal_places': 2},
    {'code': 'BDT', 'name': 'Bangladeshi Taka', 'symbol': '৳', 'decimal_places': 2},
    {'code': 'IDR', 'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'decimal_places': 0},
    {'code': 'EGP', 'name': 'Egyptian Pound', 'symbol': 'ج.م', 'decimal_places': 2},
    {'code': 'QAR', 'name': 'Qatari Riyal', 'symbol': 'ر.ق', 'decimal_places': 2},
    {'code': 'KWD', 'name': 'Kuwaiti Dinar', 'symbol': 'د.ك', 'decimal_places': 3},
    {'code': 'BHD', 'name': 'Bahraini Dinar', 'symbol': '.د.ب', 'decimal_places': 3},
    {'code': 'OMR', 'name': 'Omani Rial', 'symbol': 'ر.ع.', 'decimal_places': 3},
]

# Country/region configurations
COUNTRIES = [
    # North America
    {
        'code': 'US', 'name': 'United States', 'currency_code': 'USD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'MM/DD/YYYY', 'time_format': 'HH:mm',
        'timezone': 'America/New_York', 'language_code': 'en'
    },
    {
        'code': 'CA', 'name': 'Canada', 'currency_code': 'CAD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'America/Toronto', 'language_code': 'en'
    },
    {
        'code': 'MX', 'name': 'Mexico', 'currency_code': 'MXN',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'America/Mexico_City', 'language_code': 'es'
    },
    
    # Europe
    {
        'code': 'GB', 'name': 'United Kingdom', 'currency_code': 'GBP',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/London', 'language_code': 'en'
    },
    {
        'code': 'DE', 'name': 'Germany', 'currency_code': 'EUR',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD.MM.YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Berlin', 'language_code': 'de'
    },
    {
        'code': 'FR', 'name': 'France', 'currency_code': 'EUR',
        'decimal_separator': ',', 'thousands_separator': ' ',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Paris', 'language_code': 'fr'
    },
    {
        'code': 'IT', 'name': 'Italy', 'currency_code': 'EUR',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Rome', 'language_code': 'it'
    },
    {
        'code': 'ES', 'name': 'Spain', 'currency_code': 'EUR',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Madrid', 'language_code': 'es'
    },
    {
        'code': 'NL', 'name': 'Netherlands', 'currency_code': 'EUR',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD-MM-YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Amsterdam', 'language_code': 'nl'
    },
    {
        'code': 'CH', 'name': 'Switzerland', 'currency_code': 'CHF',
        'decimal_separator': '.', 'thousands_separator': "'",
        'date_format': 'DD.MM.YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Zurich', 'language_code': 'de'
    },
    {
        'code': 'SE', 'name': 'Sweden', 'currency_code': 'SEK',
        'decimal_separator': ',', 'thousands_separator': ' ',
        'date_format': 'YYYY-MM-DD', 'time_format': 'HH:mm',
        'timezone': 'Europe/Stockholm', 'language_code': 'sv'
    },
    {
        'code': 'NO', 'name': 'Norway', 'currency_code': 'NOK',
        'decimal_separator': ',', 'thousands_separator': ' ',
        'date_format': 'DD.MM.YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Oslo', 'language_code': 'no'
    },
    
    # Asia-Pacific
    {
        'code': 'JP', 'name': 'Japan', 'currency_code': 'JPY',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'YYYY/MM/DD', 'time_format': 'HH:mm',
        'timezone': 'Asia/Tokyo', 'language_code': 'ja'
    },
    {
        'code': 'AU', 'name': 'Australia', 'currency_code': 'AUD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Australia/Sydney', 'language_code': 'en'
    },
    {
        'code': 'NZ', 'name': 'New Zealand', 'currency_code': 'NZD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Pacific/Auckland', 'language_code': 'en'
    },
    {
        'code': 'SG', 'name': 'Singapore', 'currency_code': 'SGD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Singapore', 'language_code': 'en'
    },
    {
        'code': 'HK', 'name': 'Hong Kong', 'currency_code': 'HKD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Hong_Kong', 'language_code': 'en'
    },
    {
        'code': 'KR', 'name': 'South Korea', 'currency_code': 'KRW',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'YYYY.MM.DD', 'time_format': 'HH:mm',
        'timezone': 'Asia/Seoul', 'language_code': 'ko'
    },
    {
        'code': 'CN', 'name': 'China', 'currency_code': 'CNY',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'YYYY/MM/DD', 'time_format': 'HH:mm',
        'timezone': 'Asia/Shanghai', 'language_code': 'zh'
    },
    {
        'code': 'IN', 'name': 'India', 'currency_code': 'INR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Kolkata', 'language_code': 'en'
    },
    
    # Other regions
    {
        'code': 'BR', 'name': 'Brazil', 'currency_code': 'BRL',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'America/Sao_Paulo', 'language_code': 'pt'
    },
    {
        'code': 'ZA', 'name': 'South Africa', 'currency_code': 'ZAR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Africa/Johannesburg', 'language_code': 'en'
    },
    {
        'code': 'TR', 'name': 'Turkey', 'currency_code': 'TRY',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD.MM.YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Istanbul', 'language_code': 'tr'
    },
    {
        'code': 'RU', 'name': 'Russia', 'currency_code': 'RUB',
        'decimal_separator': ',', 'thousands_separator': ' ',
        'date_format': 'DD.MM.YYYY', 'time_format': 'HH:mm',
        'timezone': 'Europe/Moscow', 'language_code': 'ru'
    },
    
    # Middle East & Islamic Countries
    {
        'code': 'AE', 'name': 'United Arab Emirates', 'currency_code': 'AED',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Dubai', 'language_code': 'ar'
    },
    {
        'code': 'SA', 'name': 'Saudi Arabia', 'currency_code': 'SAR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Riyadh', 'language_code': 'ar'
    },
    {
        'code': 'MY', 'name': 'Malaysia', 'currency_code': 'MYR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Kuala_Lumpur', 'language_code': 'ms'
    },
    {
        'code': 'PK', 'name': 'Pakistan', 'currency_code': 'PKR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Karachi', 'language_code': 'ur'
    },
    {
        'code': 'BD', 'name': 'Bangladesh', 'currency_code': 'BDT',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Dhaka', 'language_code': 'bn'
    },
    {
        'code': 'ID', 'name': 'Indonesia', 'currency_code': 'IDR',
        'decimal_separator': ',', 'thousands_separator': '.',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Jakarta', 'language_code': 'id'
    },
    {
        'code': 'EG', 'name': 'Egypt', 'currency_code': 'EGP',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Africa/Cairo', 'language_code': 'ar'
    },
    {
        'code': 'QA', 'name': 'Qatar', 'currency_code': 'QAR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Qatar', 'language_code': 'ar'
    },
    {
        'code': 'KW', 'name': 'Kuwait', 'currency_code': 'KWD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Kuwait', 'language_code': 'ar'
    },
    {
        'code': 'BH', 'name': 'Bahrain', 'currency_code': 'BHD',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Bahrain', 'language_code': 'ar'
    },
    {
        'code': 'OM', 'name': 'Oman', 'currency_code': 'OMR',
        'decimal_separator': '.', 'thousands_separator': ',',
        'date_format': 'DD/MM/YYYY', 'time_format': 'HH:mm',
        'timezone': 'Asia/Muscat', 'language_code': 'ar'
    }
]

# Common tax rates by region
TAX_RULES = [
    # US States (simplified - major states only)
    {'country_code': 'US', 'region_code': 'CA', 'tax_type': 'sales', 'rate': 0.0725, 'description': 'California Sales Tax'},
    {'country_code': 'US', 'region_code': 'NY', 'tax_type': 'sales', 'rate': 0.08, 'description': 'New York Sales Tax'},
    {'country_code': 'US', 'region_code': 'TX', 'tax_type': 'sales', 'rate': 0.0625, 'description': 'Texas Sales Tax'},
    {'country_code': 'US', 'region_code': 'FL', 'tax_type': 'sales', 'rate': 0.06, 'description': 'Florida Sales Tax'},
    
    # European VAT rates
    {'country_code': 'GB', 'tax_type': 'vat', 'rate': 0.20, 'description': 'UK VAT'},
    {'country_code': 'DE', 'tax_type': 'vat', 'rate': 0.19, 'description': 'German VAT'},
    {'country_code': 'FR', 'tax_type': 'vat', 'rate': 0.20, 'description': 'French VAT'},
    {'country_code': 'IT', 'tax_type': 'vat', 'rate': 0.22, 'description': 'Italian VAT'},
    {'country_code': 'ES', 'tax_type': 'vat', 'rate': 0.21, 'description': 'Spanish VAT'},
    {'country_code': 'NL', 'tax_type': 'vat', 'rate': 0.21, 'description': 'Dutch VAT'},
    {'country_code': 'CH', 'tax_type': 'vat', 'rate': 0.077, 'description': 'Swiss VAT'},
    {'country_code': 'SE', 'tax_type': 'vat', 'rate': 0.25, 'description': 'Swedish VAT'},
    {'country_code': 'NO', 'tax_type': 'vat', 'rate': 0.25, 'description': 'Norwegian VAT'},
    
    # Other regions
    {'country_code': 'CA', 'tax_type': 'gst', 'rate': 0.05, 'description': 'Canadian GST'},
    {'country_code': 'AU', 'tax_type': 'gst', 'rate': 0.10, 'description': 'Australian GST'},
    {'country_code': 'NZ', 'tax_type': 'gst', 'rate': 0.15, 'description': 'New Zealand GST'},
    {'country_code': 'SG', 'tax_type': 'gst', 'rate': 0.07, 'description': 'Singapore GST'},
    {'country_code': 'JP', 'tax_type': 'consumption', 'rate': 0.10, 'description': 'Japan Consumption Tax'},
    {'country_code': 'KR', 'tax_type': 'vat', 'rate': 0.10, 'description': 'South Korea VAT'},
    {'country_code': 'IN', 'tax_type': 'gst', 'rate': 0.18, 'description': 'India GST (standard)'},
    {'country_code': 'BR', 'tax_type': 'icms', 'rate': 0.18, 'description': 'Brazil ICMS (average)'},
    {'country_code': 'ZA', 'tax_type': 'vat', 'rate': 0.15, 'description': 'South Africa VAT'},
]

def get_currency_by_code(code: str) -> Dict:
    """Get currency information by code."""
    for currency in CURRENCIES:
        if currency['code'] == code:
            return currency.copy()
    return None

def get_country_by_code(code: str) -> Dict:
    """Get country information by code."""
    for country in COUNTRIES:
        if country['code'] == code:
            return country.copy()
    return None

def get_tax_rules_by_country(country_code: str, region_code: str = None) -> List[Dict]:
    """Get tax rules for a country/region."""
    rules = []
    for rule in TAX_RULES:
        if rule['country_code'] == country_code:
            if region_code is None or rule.get('region_code') == region_code:
                rules.append(rule.copy())
    return rules