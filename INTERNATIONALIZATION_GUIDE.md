# Calculator-App Internationalization (i18n) Guide

## Overview

The Calculator-App now features comprehensive internationalization support with 5 core languages, RTL support, and specialized Islamic finance terminology. This system provides seamless language switching, cultural localization, and accessibility compliance.

## Supported Languages

### Core Languages (Phase 1)
- **English** (en) - US/UK/AU/CA variants
- **French** (fr) - France/Canada variants  
- **German** (de) - Germany/Austria/Switzerland variants
- **Spanish** (es) - Spain/Mexico variants
- **Arabic** (ar) - Saudi Arabia/UAE/Egypt variants with RTL support

### Language Features
- Native script support
- Cultural number/date formatting
- Currency localization
- Direction-aware layouts (LTR/RTL)
- Regional variant support

## Architecture

### Core Components

#### 1. I18nService (`app/services/i18n.py`)
- Translation loading and caching
- Language detection from multiple sources
- Number/currency formatting
- Islamic finance terminology

#### 2. I18nMiddleware (`app/middleware/i18n_middleware.py`)
- Request-level language context
- URL-based language routing
- Browser language detection
- Session persistence

#### 3. Translation Files (`app/translations/`)
```
translations/
├── en.json     # English translations
├── fr.json     # French translations
├── de.json     # German translations
├── es.json     # Spanish translations
└── ar.json     # Arabic translations
```

#### 4. Language Switcher (`app/static/js/language-switcher.js`)
- Dynamic language switching UI
- No-reload language changes
- Accessibility compliant
- RTL direction support

#### 5. RTL Support (`app/static/css/i18n.css`)
- Right-to-left layout support
- Arabic typography optimization
- Direction-aware components
- Cultural design adaptations

## Implementation Details

### Translation Structure

```json
{
  \"common\": {
    \"calculate\": \"Calculate\",
    \"result\": \"Result\",
    \"currency\": \"Currency\"
  },
  \"calculators\": {
    \"percentage\": {
      \"title\": \"Percentage Calculator\",
      \"description\": \"Calculate percentages and percentage changes\"
    }
  },
  \"islamic_finance\": {
    \"terms\": {
      \"murabaha\": {
        \"arabic\": \"مرابحة\",
        \"transliteration\": \"Murabaha\",
        \"definition\": \"Cost-plus sale contract\"
      }
    }
  }
}
```

### API Endpoints

#### Language Management
- `GET /api/languages` - Get available languages
- `GET /api/language` - Get current language
- `POST /api/language` - Set language preference
- `GET /api/translations/{language}` - Get translations

#### Formatting Services
- `GET /api/format/number` - Format numbers by locale
- `GET /api/islamic-finance/terms` - Get Islamic terms

#### Utilities
- `GET /api/detect-language` - Auto-detect language
- `GET /api/health` - I18n system health check

### URL Structure

#### SEO-Friendly Language URLs
```
/                    # English (default)
/fr/                 # French homepage
/de/calculators/     # German calculators
/ar/islamic-finance/ # Arabic Islamic finance
```

#### Language Detection Priority
1. URL language prefix (`/fr/`)
2. Session preference
3. Browser Accept-Language header
4. IP-based country detection
5. Default fallback (English)

### RTL Support Features

#### Arabic Language Optimizations
- Right-to-left text direction
- Mirrored layout components
- Arabic typography enhancements
- Cultural color adaptations
- Number formatting (keep LTR for calculations)

#### CSS Classes
```css
.rtl { direction: rtl; }
[dir=\"rtl\"] .component { /* RTL-specific styles */ }
[lang=\"ar\"] { font-family: Arabic-optimized-fonts; }
```

## Usage Guide

### Template Integration

#### Basic Translation
```html
<h1 data-translate=\"calculators.title\">{{ 'calculators.title' | translate }}</h1>
<button data-translate=\"common.calculate\">{{ get_translation('common.calculate') }}</button>
```

#### Number Formatting
```html
<span>{{ amount | format_currency('USD') }}</span>
<span>{{ percentage | format_percentage }}</span>
```

#### Language Switching
```html
<!-- Language switcher is automatically injected -->
<div class=\"language-switcher\">
  <!-- Auto-generated language dropdown -->
</div>
```

### JavaScript Integration

#### Language Change Handling
```javascript
// Listen for language changes
window.addEventListener('languageChanged', (event) => {
  console.log('Language changed to:', event.detail.language);
  // Update dynamic content
});

// Manual language switching
window.languageSwitcher.switchLanguage('fr');
```

#### RTL Detection
```javascript
// Check if current language is RTL
if (document.documentElement.dir === 'rtl') {
  // Apply RTL-specific logic
}
```

### Backend Usage

#### Translation in Views
```python
from app.services.i18n import i18n_service

# Get translation
translated = i18n_service.translate('common.calculate', g.language_code)

# Format numbers
formatted = i18n_service.format_number_localized(1234.56, g.language_code, currency='USD')
```

#### Language Context
```python
@app.route('/calculator')
def calculator():
    return render_template('calculator.html',
        page_title=i18n_service.translate('calculators.title', g.language_code)
    )
```

## Islamic Finance Features

### Specialized Terminology
- Arabic terms with English transliterations
- Religious context explanations
- Regional variations (Gulf vs Levant)
- Sharia compliance indicators

### Supported Calculators
- **Zakat Calculator** (زكاة) - Islamic almsgiving
- **Takaful Calculator** (تكافل) - Islamic insurance
- **Murabaha Calculator** (مرابحة) - Islamic financing

### Cultural Adaptations
- Lunar calendar support for Zakat
- Regional Islamic finance conventions
- Arabic numerals with LTR calculation display
- Religious disclaimers and guidance

## Performance Features

### Optimization Strategies
- **Translation Caching** - Memory-cached translations
- **Lazy Loading** - Load translations on demand
- **Compression** - Minified translation files
- **CDN Support** - Static asset optimization

### Performance Metrics
- Translation loading: <100ms
- Language switching: <200ms
- RTL layout adaptation: <50ms
- Memory usage: <5MB per language

## Accessibility Compliance

### WCAG 2.1 AA Standards
- Screen reader compatibility
- Keyboard navigation support
- High contrast mode support
- Focus management during language switches

### Language-Specific Accessibility
- Arabic screen reader optimization
- RTL reading order compliance
- Cultural color contrast standards
- Localized accessibility labels

## Development Workflow

### Adding New Languages

1. **Create Translation File**
```bash
# Create new language file
cp app/translations/en.json app/translations/ja.json
# Translate content to Japanese
```

2. **Update Language Configuration**
```python
# Add to SUPPORTED_LANGUAGES in i18n.py
'ja': {
    'name': 'Japanese',
    'native_name': '日本語',
    'direction': 'ltr',
    'decimal_separator': '.',
    'thousands_separator': ',',
    'currency_position': 'after'
}
```

3. **Add Regional Mapping**
```python
# Update region_language_map
'JP': 'ja'
```

### Translation Workflow

1. **Extract translatable strings**
2. **Update translation files**
3. **Test language switching**
4. **Verify formatting functions**
5. **Test RTL support (if applicable)**

### Testing Checklist

- [ ] All languages load correctly
- [ ] Translation keys are consistent
- [ ] Number formatting works per locale
- [ ] Currency display is correct
- [ ] Date formatting is localized
- [ ] RTL layout functions properly
- [ ] Language switching is seamless
- [ ] SEO URLs work correctly
- [ ] API endpoints respond correctly
- [ ] Accessibility standards met

## Deployment Considerations

### Production Setup
- Ensure translation files are deployed
- Configure CDN for static assets
- Set up proper caching headers
- Monitor translation loading performance

### SEO Configuration
- Generate language-specific sitemaps
- Configure hreflang tags
- Set up Google Search Console for each language
- Implement structured data in multiple languages

### Monitoring
- Track language usage analytics
- Monitor translation loading errors
- Measure language switching performance
- Track user language preferences

## Troubleshooting

### Common Issues

#### Translation Not Loading
```bash
# Check translation file exists
ls app/translations/fr.json

# Verify JSON syntax
python -m json.tool app/translations/fr.json
```

#### RTL Layout Issues
```css
/* Check RTL class application */
html[dir=\"rtl\"] .component {
  /* Add RTL-specific styles */
}
```

#### Language Detection Problems
```python
# Debug language detection
print(f\"Detected language: {i18n_service.get_user_language()}\")
print(f\"Session language: {session.get('language')}\")
print(f\"Browser languages: {request.headers.get('Accept-Language')}\")
```

### Performance Issues
- Enable translation caching
- Optimize translation file sizes
- Use CDN for static assets
- Implement lazy loading

## Future Enhancements

### Planned Features
- Additional language support (Chinese, Japanese, Russian)
- Voice interface localization
- Offline translation support
- Advanced plural forms
- Context-aware translations

### Integration Opportunities
- Translation management systems
- Professional translation services
- Community translation platforms
- Automated translation tools

## Support

For technical support or questions about the internationalization system:

1. Check the test suite: `python -m pytest tests/test_i18n.py`
2. Review the API documentation
3. Test with the interactive language switcher
4. Validate translations with native speakers

The internationalization system is designed to be extensible, performant, and culturally appropriate for global users while maintaining the highest standards of accessibility and user experience.