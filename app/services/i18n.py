"""
Enhanced Internationalization Service for Calculator-App
Comprehensive language localization system with RTL support
"""
import json
import os
from typing import Dict, List, Optional, Any
from flask import current_app, request, session, g
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class I18nService:
    """Enhanced internationalization service for multi-language support."""
    
    # Supported languages with comprehensive metadata
    SUPPORTED_LANGUAGES = {
        'en': {
            'name': 'English',
            'native_name': 'English',
            'variants': {
                'en-US': {'name': 'English (US)', 'region': 'US'},
                'en-GB': {'name': 'English (UK)', 'region': 'GB'},
                'en-CA': {'name': 'English (Canada)', 'region': 'CA'},
                'en-AU': {'name': 'English (Australia)', 'region': 'AU'}
            },
            'direction': 'ltr',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'currency_position': 'before'
        },
        'fr': {
            'name': 'French',
            'native_name': 'Français',
            'variants': {
                'fr-FR': {'name': 'Français (France)', 'region': 'FR'},
                'fr-CA': {'name': 'Français (Canada)', 'region': 'CA'}
            },
            'direction': 'ltr',
            'decimal_separator': ',',
            'thousands_separator': ' ',
            'currency_position': 'after'
        },
        'de': {
            'name': 'German',
            'native_name': 'Deutsch',
            'variants': {
                'de-DE': {'name': 'Deutsch (Deutschland)', 'region': 'DE'},
                'de-AT': {'name': 'Deutsch (Österreich)', 'region': 'AT'},
                'de-CH': {'name': 'Deutsch (Schweiz)', 'region': 'CH'}
            },
            'direction': 'ltr',
            'decimal_separator': ',',
            'thousands_separator': '.',
            'currency_position': 'after'
        },
        'es': {
            'name': 'Spanish',
            'native_name': 'Español',
            'variants': {
                'es-ES': {'name': 'Español (España)', 'region': 'ES'},
                'es-MX': {'name': 'Español (México)', 'region': 'MX'}
            },
            'direction': 'ltr',
            'decimal_separator': ',',
            'thousands_separator': '.',
            'currency_position': 'after'
        },
        'ar': {
            'name': 'Arabic',
            'native_name': 'العربية',
            'variants': {
                'ar-SA': {'name': 'العربية (السعودية)', 'region': 'SA'},
                'ar-AE': {'name': 'العربية (الإمارات)', 'region': 'AE'},
                'ar-EG': {'name': 'العربية (مصر)', 'region': 'EG'}
            },
            'direction': 'rtl',
            'decimal_separator': '.',
            'thousands_separator': ',',
            'currency_position': 'after'
        }
    }
    
    def __init__(self):
        self.translations_cache = {}
        self.translations_dir = None  # Will be set in initialize_translations
        self.fallback_language = 'en'
        
    def initialize_translations(self):
        """Initialize translation system and load all language files."""
        try:
            # Set translations directory
            from flask import current_app
            self.translations_dir = Path(current_app.root_path) / 'translations'
            
            # Ensure translations directory exists
            self.translations_dir.mkdir(exist_ok=True)
            
            # Load all translation files into cache
            for lang_code in self.SUPPORTED_LANGUAGES.keys():
                self._load_translations(lang_code)
                
            logger.info(f"Initialized translations for {len(self.SUPPORTED_LANGUAGES)} languages")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize translations: {e}")
            return False
    
    def get_user_language(self) -> str:
        """
        Determine user's preferred language from multiple sources.
        Priority: session > user preference > browser > region > default
        """
        # 1. Check session preference
        if hasattr(g, 'session_id') and session.get('language'):
            lang = session.get('language')
            if self._is_language_supported(lang):
                return lang
        
        # 2. Check browser Accept-Language header
        if request and request.headers.get('Accept-Language'):
            browser_langs = self._parse_accept_language(request.headers.get('Accept-Language'))
            for lang in browser_langs:
                if self._is_language_supported(lang):
                    return lang
        
        # 3. Check regional detection
        if hasattr(g, 'country_code') and g.country_code:
            region_lang = self._get_language_for_region(g.country_code)
            if region_lang:
                return region_lang
        
        # 4. Default fallback
        return self.fallback_language
    
    def set_user_language(self, language_code: str) -> bool:
        """Set user's language preference and persist in session."""
        try:
            if not self._is_language_supported(language_code):
                logger.warning(f"Unsupported language: {language_code}")
                return False
            
            # Store in session
            session['language'] = language_code
            session.permanent = True
            
            # Update g context for current request
            g.language_code = language_code
            g.text_direction = self.SUPPORTED_LANGUAGES[language_code]['direction']
            
            logger.info(f"Set user language to: {language_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    def translate(self, key: str, language: str = None, **kwargs) -> str:
        """
        Translate a text key to the specified language.
        
        Args:
            key: Translation key (e.g., 'calculator.title')
            language: Target language code (defaults to current user language)
            **kwargs: Variables for string interpolation
            
        Returns:
            Translated text or original key if translation not found
        """
        try:
            if not language:
                language = self.get_user_language()
            
            # Get translation from cache
            translations = self._get_translations(language)
            
            # Navigate nested keys (e.g., 'calculator.title')
            text = self._get_nested_value(translations, key)
            
            if text is None:
                # Fallback to default language
                if language != self.fallback_language:
                    fallback_translations = self._get_translations(self.fallback_language)
                    text = self._get_nested_value(fallback_translations, key)
                
                if text is None:
                    logger.warning(f"Translation not found: {key} [{language}]")
                    return key
            
            # Handle string interpolation
            if kwargs and isinstance(text, str):
                try:
                    text = text.format(**kwargs)
                except (ValueError, KeyError) as e:
                    logger.warning(f"String interpolation failed for {key}: {e}")
            
            return text
            
        except Exception as e:
            logger.error(f"Translation error for {key}: {e}")
            return key
    
    def get_language_info(self, language_code: str = None) -> Dict:
        """Get comprehensive information about a language."""
        if not language_code:
            language_code = self.get_user_language()
        
        if language_code not in self.SUPPORTED_LANGUAGES:
            language_code = self.fallback_language
        
        lang_info = self.SUPPORTED_LANGUAGES[language_code].copy()
        lang_info['code'] = language_code
        lang_info['is_rtl'] = lang_info['direction'] == 'rtl'
        
        return lang_info
    
    def get_available_languages(self) -> List[Dict]:
        """Get list of all available languages with metadata."""
        languages = []
        
        for code, info in self.SUPPORTED_LANGUAGES.items():
            lang_data = {
                'code': code,
                'name': info['name'],
                'native_name': info['native_name'],
                'direction': info['direction'],
                'is_rtl': info['direction'] == 'rtl',
                'variants': info.get('variants', {})
            }
            languages.append(lang_data)
        
        return languages
    
    def format_number_localized(self, number: float, language: str = None, 
                               currency: str = None) -> str:
        """Format number according to language-specific conventions."""
        try:
            if not language:
                language = self.get_user_language()
            
            lang_info = self.get_language_info(language)
            
            # Format the number
            if currency:
                # Currency formatting
                formatted = f"{number:,.2f}"
                
                # Apply locale-specific separators
                if lang_info['decimal_separator'] != '.':
                    formatted = formatted.replace('.', '|DECIMAL|')
                if lang_info['thousands_separator'] != ',':
                    formatted = formatted.replace(',', lang_info['thousands_separator'])
                formatted = formatted.replace('|DECIMAL|', lang_info['decimal_separator'])
                
                # Add currency symbol
                if lang_info['currency_position'] == 'before':
                    return f"{currency} {formatted}"
                else:
                    return f"{formatted} {currency}"
            else:
                # Regular number formatting
                formatted = f"{number:,.2f}" if isinstance(number, float) else f"{number:,}"
                
                # Apply locale-specific separators
                if lang_info['decimal_separator'] != '.':
                    formatted = formatted.replace('.', '|DECIMAL|')
                if lang_info['thousands_separator'] != ',':
                    formatted = formatted.replace(',', lang_info['thousands_separator'])
                formatted = formatted.replace('|DECIMAL|', lang_info['decimal_separator'])
                
                return formatted
                
        except Exception as e:
            logger.error(f"Number formatting error: {e}")
            return str(number)
    
    def get_islamic_finance_terms(self, language: str = 'ar') -> Dict:
        """Get Islamic finance terminology with translations and explanations."""
        try:
            translations = self._get_translations(language)
            islamic_terms = translations.get('islamic_finance', {})
            
            # Add English transliterations for Arabic terms
            if language == 'ar' and 'terms' in islamic_terms:
                for term_key, term_data in islamic_terms['terms'].items():
                    if isinstance(term_data, dict) and 'transliteration' not in term_data:
                        # Add common transliterations
                        transliterations = {
                            'murabaha': 'Murabaha',
                            'takaful': 'Takaful',
                            'zakat': 'Zakat',
                            'riba': 'Riba',
                            'halal': 'Halal',
                            'haram': 'Haram',
                            'sukuk': 'Sukuk',
                            'musharaka': 'Musharaka'
                        }
                        if term_key in transliterations:
                            term_data['transliteration'] = transliterations[term_key]
            
            return islamic_terms
            
        except Exception as e:
            logger.error(f"Error getting Islamic finance terms: {e}")
            return {}
    
    def _load_translations(self, language_code: str) -> Dict:
        """Load translations for a specific language from JSON file."""
        try:
            file_path = self.translations_dir / f"{language_code}.json"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    self.translations_cache[language_code] = translations
                    return translations
            else:
                logger.warning(f"Translation file not found: {file_path}")
                self.translations_cache[language_code] = {}
                return {}
                
        except Exception as e:
            logger.error(f"Error loading translations for {language_code}: {e}")
            self.translations_cache[language_code] = {}
            return {}
    
    def _get_translations(self, language_code: str) -> Dict:
        """Get translations from cache or load if not cached."""
        if language_code not in self.translations_cache:
            return self._load_translations(language_code)
        return self.translations_cache[language_code]
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def _is_language_supported(self, language_code: str) -> bool:
        """Check if language code is supported."""
        # Check base language
        base_lang = language_code.split('-')[0]
        return base_lang in self.SUPPORTED_LANGUAGES
    
    def _parse_accept_language(self, accept_language: str) -> List[str]:
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
                
                languages.append((lang.strip(), q))
            
            # Sort by priority (q value)
            languages.sort(key=lambda x: x[1], reverse=True)
            return [lang for lang, _ in languages]
            
        except Exception as e:
            logger.error(f"Error parsing Accept-Language header: {e}")
            return []
    
    def _get_language_for_region(self, country_code: str) -> Optional[str]:
        """Get default language for a country/region."""
        region_language_map = {
            'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en',
            'FR': 'fr', 'DE': 'de', 'AT': 'de', 'CH': 'de',
            'ES': 'es', 'MX': 'es',
            'SA': 'ar', 'AE': 'ar', 'EG': 'ar'
        }
        return region_language_map.get(country_code)

# Global instance
i18n_service = I18nService()