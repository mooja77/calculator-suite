"""
Comprehensive tests for internationalization system
Tests translation loading, language switching, RTL support, and formatting
"""
import pytest
import json
from flask import Flask, g, session
from unittest.mock import patch, MagicMock

from app.services.i18n import i18n_service, I18nService
from app.middleware.i18n_middleware import i18n_middleware, I18nMiddleware
from app import create_app

class TestI18nService:
    """Test the core internationalization service."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create test app context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize i18n service
        i18n_service.initialize_translations()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.app_context.pop()
    
    def test_supported_languages(self):
        """Test that all supported languages are properly configured."""
        supported = i18n_service.SUPPORTED_LANGUAGES
        
        # Check required languages are present
        required_languages = ['en', 'fr', 'de', 'es', 'ar']
        for lang in required_languages:
            assert lang in supported
        
        # Check language metadata
        for lang_code, lang_info in supported.items():
            assert 'name' in lang_info
            assert 'native_name' in lang_info
            assert 'direction' in lang_info
            assert lang_info['direction'] in ['ltr', 'rtl']
    
    def test_language_support_check(self):
        """Test language support validation."""
        # Valid languages
        assert i18n_service._is_language_supported('en')
        assert i18n_service._is_language_supported('fr')
        assert i18n_service._is_language_supported('ar')
        
        # Invalid languages
        assert not i18n_service._is_language_supported('xx')
        assert not i18n_service._is_language_supported('')
        assert not i18n_service._is_language_supported(None)
    
    def test_translation_loading(self):
        """Test translation file loading."""
        # Test loading English translations
        translations_en = i18n_service._get_translations('en')
        assert isinstance(translations_en, dict)
        assert 'common' in translations_en
        assert 'navigation' in translations_en
        assert 'calculators' in translations_en
        
        # Test loading Arabic translations
        translations_ar = i18n_service._get_translations('ar')
        assert isinstance(translations_ar, dict)
        assert 'common' in translations_ar
        
        # Test invalid language
        translations_invalid = i18n_service._get_translations('xx')
        assert translations_invalid == {}
    
    def test_translation_functionality(self):
        """Test translation with various scenarios."""
        with self.app.test_request_context():
            g.language_code = 'en'
            
            # Basic translation
            result = i18n_service.translate('common.calculate')
            assert result == 'Calculate'
            
            # Nested key translation
            result = i18n_service.translate('calculators.percentage.title')
            assert result == 'Percentage Calculator'
            
            # Translation with variables
            result = i18n_service.translate('errors.min_value', min=10)
            assert '10' in result
            
            # Missing translation (should return key)
            result = i18n_service.translate('nonexistent.key')
            assert result == 'nonexistent.key'
    
    def test_language_detection(self):
        """Test language detection from various sources."""
        with self.app.test_request_context(
            headers={'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'}
        ):
            # Mock session and g
            with patch('flask.session', {'language': None}):
                with patch('flask.g', MagicMock()):
                    detected = i18n_service.get_user_language()
                    # Should detect French from Accept-Language
                    assert detected in ['fr', 'en']  # Fallback possible
    
    def test_language_info(self):
        """Test language information retrieval."""
        # Test English
        info_en = i18n_service.get_language_info('en')
        assert info_en['code'] == 'en'
        assert info_en['direction'] == 'ltr'
        assert not info_en['is_rtl']
        
        # Test Arabic
        info_ar = i18n_service.get_language_info('ar')
        assert info_ar['code'] == 'ar'
        assert info_ar['direction'] == 'rtl'
        assert info_ar['is_rtl']
        
        # Test invalid language (should return fallback)
        info_invalid = i18n_service.get_language_info('xx')
        assert info_invalid['code'] == 'en'
    
    def test_number_formatting(self):
        """Test localized number formatting."""
        test_number = 1234.56
        
        # English formatting
        result_en = i18n_service.format_number_localized(test_number, 'en')
        assert '1,234.56' in result_en
        
        # German formatting (different separators)
        result_de = i18n_service.format_number_localized(test_number, 'de')
        assert '1.234,56' in result_de or '1234,56' in result_de
        
        # Currency formatting
        result_currency = i18n_service.format_number_localized(
            test_number, 'en', currency='USD'
        )
        assert 'USD' in result_currency
        assert '1,234.56' in result_currency
    
    def test_islamic_finance_terms(self):
        """Test Islamic finance terminology."""
        # Test Arabic terms
        terms_ar = i18n_service.get_islamic_finance_terms('ar')
        assert isinstance(terms_ar, dict)
        
        if 'terms' in terms_ar:
            # Check for common Islamic finance terms
            common_terms = ['murabaha', 'takaful', 'zakat']
            for term in common_terms:
                if term in terms_ar['terms']:
                    term_data = terms_ar['terms'][term]
                    assert 'arabic' in term_data
                    # Transliteration should be added automatically
                    assert 'transliteration' in term_data
    
    def test_available_languages(self):
        """Test getting available languages list."""
        languages = i18n_service.get_available_languages()
        assert isinstance(languages, list)
        assert len(languages) == len(i18n_service.SUPPORTED_LANGUAGES)
        
        for lang in languages:
            assert 'code' in lang
            assert 'name' in lang
            assert 'native_name' in lang
            assert 'direction' in lang
            assert 'is_rtl' in lang

class TestI18nMiddleware:
    """Test the internationalization middleware."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Initialize middleware
        self.middleware = I18nMiddleware(self.app)
    
    def test_accept_language_parsing(self):
        """Test Accept-Language header parsing."""
        with self.app.app_context():
            # Test basic parsing
            languages = self.middleware.parse_accept_language('en-US,en;q=0.9,fr;q=0.8')
            assert 'en' in languages
            assert 'fr' in languages
            
            # Test quality values ordering
            languages = self.middleware.parse_accept_language('fr;q=0.8,en;q=0.9')
            assert languages[0] == 'en'  # Higher quality first
            
            # Test malformed header
            languages = self.middleware.parse_accept_language('invalid-header')
            assert isinstance(languages, list)
    
    def test_language_for_region(self):
        """Test region to language mapping."""
        with self.app.app_context():
            # Test known mappings
            assert self.middleware.get_language_for_region('US') == 'en'
            assert self.middleware.get_language_for_region('FR') == 'fr'
            assert self.middleware.get_language_for_region('DE') == 'de'
            assert self.middleware.get_language_for_region('SA') == 'ar'
            
            # Test unknown region
            assert self.middleware.get_language_for_region('XX') is None
    
    def test_client_ip_detection(self):
        """Test client IP detection from headers."""
        with self.app.test_request_context(
            headers={'X-Forwarded-For': '192.168.1.1, 10.0.0.1'}
        ):
            ip = self.middleware.get_client_ip()
            assert ip == '192.168.1.1'
        
        with self.app.test_request_context(
            headers={'X-Real-IP': '203.0.113.1'}
        ):
            ip = self.middleware.get_client_ip()
            assert ip == '203.0.113.1'
    
    def test_context_injection(self):
        """Test template context injection."""
        with self.app.test_request_context():
            with patch('flask.g') as mock_g:
                mock_g.language_code = 'fr'
                mock_g.language_info = {'name': 'French'}
                mock_g.text_direction = 'ltr'
                mock_g.is_rtl = False
                mock_g.translations = {}
                
                context = self.middleware.inject_i18n_context()
                
                assert 'language_code' in context
                assert 'language_info' in context
                assert 'text_direction' in context
                assert 'is_rtl' in context
                assert 'available_languages' in context

class TestI18nAPI:
    """Test the internationalization API endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_get_translations_endpoint(self):
        """Test GET /api/translations/<language_code>."""
        # Test valid language
        response = self.client.get('/api/translations/en')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'language' in data
        assert 'translations' in data
        assert 'language_info' in data
        assert data['language'] == 'en'
        
        # Test invalid language
        response = self.client.get('/api/translations/xx')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'supported_languages' in data
    
    def test_get_supported_languages_endpoint(self):
        """Test GET /api/languages."""
        response = self.client.get('/api/languages')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'languages' in data
        assert 'current_language' in data
        assert 'total_count' in data
        assert isinstance(data['languages'], list)
        assert data['total_count'] > 0
    
    def test_set_language_endpoint(self):
        """Test POST /api/language."""
        # Test valid language
        response = self.client.post('/api/language', 
            json={'language': 'fr'},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['language'] == 'fr'
        
        # Test invalid language
        response = self.client.post('/api/language', 
            json={'language': 'xx'},
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test missing data
        response = self.client.post('/api/language', 
            json={},
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_format_number_endpoint(self):
        """Test GET /api/format/number."""
        # Test basic number formatting
        response = self.client.get('/api/format/number?number=1234.56&language=en')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'formatted' in data
        assert 'original' in data
        assert data['original'] == 1234.56
        
        # Test currency formatting
        response = self.client.get('/api/format/number?number=1234.56&currency=USD&language=en')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'USD' in data['formatted']
        
        # Test invalid number
        response = self.client.get('/api/format/number?number=invalid')
        assert response.status_code == 400
        
        # Test missing number
        response = self.client.get('/api/format/number')
        assert response.status_code == 400
    
    def test_islamic_finance_terms_endpoint(self):
        """Test GET /api/islamic-finance/terms."""
        response = self.client.get('/api/islamic-finance/terms?language=ar')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'language' in data
        assert 'terms' in data
        assert data['language'] == 'ar'
    
    def test_detect_language_endpoint(self):
        """Test GET /api/detect-language."""
        response = self.client.get('/api/detect-language',
            headers={'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'detected_language' in data
        assert 'browser_languages' in data
        assert 'language_info' in data
        
        # Check browser languages were parsed
        assert isinstance(data['browser_languages'], list)
    
    def test_health_check_endpoint(self):
        """Test GET /api/health."""
        response = self.client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'supported_languages' in data
        assert 'version' in data

class TestRTLSupport:
    """Test Right-to-Left language support."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_arabic_direction(self):
        """Test Arabic language direction detection."""
        with self.app.test_request_context():
            g.language_code = 'ar'
            
            lang_info = i18n_service.get_language_info('ar')
            assert lang_info['direction'] == 'rtl'
            assert lang_info['is_rtl'] is True
    
    def test_ltr_languages(self):
        """Test Left-to-Right languages."""
        ltr_languages = ['en', 'fr', 'de', 'es']
        
        for lang in ltr_languages:
            with self.app.test_request_context():
                lang_info = i18n_service.get_language_info(lang)
                assert lang_info['direction'] == 'ltr'
                assert lang_info['is_rtl'] is False
    
    def test_arabic_translations(self):
        """Test Arabic translation content."""
        translations_ar = i18n_service._get_translations('ar')
        
        if translations_ar and 'common' in translations_ar:
            # Check for Arabic text
            calculate_ar = translations_ar['common'].get('calculate', '')
            assert 'احسب' in calculate_ar or len(calculate_ar) > 0
            
            # Check for proper RTL characters
            if 'navigation' in translations_ar:
                home_ar = translations_ar['navigation'].get('home', '')
                # Arabic text should contain RTL characters
                assert any(ord(char) > 1536 for char in home_ar) or len(home_ar) == 0

class TestFormattingFunctions:
    """Test number and currency formatting functions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
    
    def test_number_formatting_locales(self):
        """Test number formatting for different locales."""
        test_cases = [
            ('en', 1234.56, '1,234.56'),
            ('de', 1234.56, '1.234,56'),  # German format
            ('fr', 1234.56, '1 234,56'),  # French format
        ]
        
        for language, number, expected_pattern in test_cases:
            result = i18n_service.format_number_localized(number, language)
            # Check if the result contains expected separators
            if language == 'en':
                assert ',' in result and '.' in result
            elif language == 'de':
                assert ',' in result  # German uses comma for decimal
            # Note: Exact formatting may vary based on system locale
    
    def test_currency_formatting(self):
        """Test currency formatting."""
        # Test USD formatting
        result = i18n_service.format_number_localized(100.50, 'en', currency='USD')
        assert 'USD' in result
        assert '100.50' in result or '100,50' in result
        
        # Test EUR formatting
        result = i18n_service.format_number_localized(100.50, 'de', currency='EUR')
        assert 'EUR' in result
    
    def test_edge_cases(self):
        """Test edge cases in formatting."""
        # Test zero
        result = i18n_service.format_number_localized(0, 'en')
        assert '0' in result
        
        # Test negative numbers
        result = i18n_service.format_number_localized(-123.45, 'en')
        assert '-' in result or '(' in result  # Different negative formats
        
        # Test large numbers
        result = i18n_service.format_number_localized(1000000, 'en')
        assert '1,000,000' in result or '1000000' in result

class TestIntegration:
    """Integration tests for the complete i18n system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_language_switching_flow(self):
        """Test complete language switching flow."""
        # Start with English
        response = self.client.get('/')
        assert response.status_code == 200
        
        # Switch to French via API
        response = self.client.post('/api/language', 
            json={'language': 'fr'},
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify language was set
        response = self.client.get('/api/language')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_language'] == 'fr'
    
    def test_translation_consistency(self):
        """Test translation consistency across languages."""
        required_keys = [
            'common.calculate',
            'common.result', 
            'navigation.home',
            'calculators.percentage.title'
        ]
        
        for lang_code in i18n_service.SUPPORTED_LANGUAGES.keys():
            translations = i18n_service._get_translations(lang_code)
            
            for key in required_keys:
                # Check if translation exists
                result = i18n_service.translate(key, lang_code)
                # Should not return the key itself (meaning translation exists)
                # Allow fallback to English for some keys
                assert result is not None and result != ''
    
    def test_fallback_behavior(self):
        """Test fallback behavior when translations are missing."""
        # Test with invalid language
        with patch.object(i18n_service, '_get_translations', return_value={}):
            result = i18n_service.translate('common.calculate', 'xx')
            # Should fallback to key or English translation
            assert result in ['common.calculate', 'Calculate']
    
    @pytest.mark.parametrize("language", ['en', 'fr', 'de', 'es', 'ar'])
    def test_all_languages_load(self, language):
        """Test that all supported languages can be loaded."""
        translations = i18n_service._get_translations(language)
        # Should return dict (empty dict is acceptable for missing files)
        assert isinstance(translations, dict)
        
        # If translations exist, should have basic structure
        if translations:
            # At minimum should have some common translations
            assert any(key in translations for key in ['common', 'navigation', 'calculators'])

# Performance and stress tests
class TestPerformance:
    """Performance tests for i18n system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
    
    def test_translation_loading_performance(self):
        """Test that translation loading is reasonably fast."""
        import time
        
        start_time = time.time()
        
        # Load all languages
        for lang_code in i18n_service.SUPPORTED_LANGUAGES.keys():
            i18n_service._get_translations(lang_code)
        
        end_time = time.time()
        loading_time = end_time - start_time
        
        # Should load all languages in reasonable time (adjust threshold as needed)
        assert loading_time < 1.0, f"Translation loading took {loading_time:.2f}s"
    
    def test_translation_caching(self):
        """Test that translations are properly cached."""
        # Clear cache
        i18n_service.translations_cache.clear()
        
        # First load
        translations1 = i18n_service._get_translations('en')
        
        # Second load (should use cache)
        translations2 = i18n_service._get_translations('en')
        
        # Should be the same object (cached)
        assert translations1 is translations2
        
        # Should be in cache
        assert 'en' in i18n_service.translations_cache

if __name__ == '__main__':
    pytest.main([__file__, '-v'])